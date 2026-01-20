#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
import json
import html
import platform
import multiprocessing
import shutil
from datetime import datetime

class DBSimulator:
    def __init__(self, args):
        self.args = args
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_name = self.args.name.lower().replace(" ", "_")
        self.results = {}
        self.env_details = {
            'sysbench_cmd': "",
            'db_config': {},
            'lua_script': "",
            'sql_scripts': {},
            'error_log': "",
            'infra': {}
        }
        
        # Output directory handling
        self.output_dir = self.args.output_dir or "reports"
        
        # If output_dir is specified and not the default 'reports', 
        # we simplify the filename to avoid redundancy with the directory name
        if self.args.output_dir and self.args.output_dir != "reports":
            self.output_md = os.path.join(self.output_dir, f"report_{self.test_name}.md")
            self.output_html = os.path.join(self.output_dir, f"report_{self.test_name}.html")
        else:
            self.output_md = os.path.join(self.output_dir, f"report_{self.test_name}_{self.ts_slug}.md")
            self.output_html = os.path.join(self.output_dir, f"report_{self.test_name}_{self.ts_slug}.html")

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def run_simulation(self):
        """Runs the sysbench simulation via run_dir_bench.sh and captures output."""
        # Pre-simulation: Clear container logs to ensure transparency
        if self.args.container:
            self.clear_container_logs()
            
        # Capture start time to filter logs later
        self.start_time = datetime.now()
        print(f"🚀 Starting simulation on {self.args.host}...")
        
        cmd = [
            "bash", "scripts/run_dir_bench.sh",
            "--sql-dir", self.args.sql_dir,
            "--threads", str(self.args.threads),
            "--time", str(self.args.time),
            "--host", self.args.host,
            "--user", self.args.user,
            "--password", self.args.password,
            "--db", self.args.db
        ]
        
        if self.args.container:
            cmd.extend(["--container", self.args.container])

        # Pre-simulation: Run setup.sql if it exists
        setup_script = os.path.join(self.args.sql_dir, "setup.sql")
        if os.path.exists(setup_script):
            print(f"🔧 Running setup script: {setup_script}")
            setup_cmd = [
                "docker", "exec", "-i", self.args.container or "mariadb-11-8",
                "mariadb", "-u", self.args.user
            ]
            if self.args.password:
                setup_cmd.append(f"-p{self.args.password}")
            setup_cmd.append(self.args.db)
            try:
                with open(setup_script, 'r') as f:
                    subprocess.run(setup_cmd, stdin=f, check=True)
            except Exception as e:
                print(f"⚠️  Setup script failed: {e}")

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"❌ Simulation failed:\n{stderr}")
                return False
            
            self.raw_output = stdout
            
            # Reconstruct sysbench command for transparency in the report
            container_name = self.args.container or "mariadb-11-8"
            # We assume it's running in Docker based on the project environment
            sb_cmd = [
                "sysbench",
                f"--mysql-host={self.args.host}",
                f"--mysql-user={self.args.user}",
                f"--mysql-password={self.args.password}" if self.args.password else "--mysql-password=",
                f"--mysql-db={self.args.db}",
                "--sql-dir=/tmp/bench_dir/sql/",
                f"--threads={self.args.threads}",
                f"--time={self.args.time}",
                "--events=0",
                "/tmp/dir_transactions_sysbench.lua run"
            ]
            
            reconstructed_cmd = f"docker exec -i {container_name} " + " ".join(sb_cmd)
            self.env_details['sysbench_cmd'] = reconstructed_cmd
            
            self.parse_sysbench_output(stdout)
            
            # Fetch and parse deadlocks if container is specified
            if self.args.container:
                self.fetch_deadlocks()
            
            self.fetch_environment_details()
            
            return True
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False

    def clear_container_logs(self):
        """Attempts to clear (truncate) the docker container logs."""
        print(f"🧹 Clearing logs for container: {self.args.container}...")
        try:
            # Get the log path
            cmd_path = ["docker", "inspect", "--format", "{{.LogPath}}", self.args.container]
            path_res = subprocess.run(cmd_path, capture_output=True, text=True)
            if path_res.returncode == 0:
                log_path = path_res.stdout.strip()
                if log_path:
                    # Try to truncate via sudo if needed, but since we are usually in a dev env
                    # we try to run a command that truncates it.
                    # On many systems, we can use a docker-based trick to truncate:
                    truncate_cmd = ["sudo", "truncate", "-s", "0", log_path]
                    # We try without sudo first if we are in a container or have direct access
                    res = subprocess.run(["truncate", "-s", "0", log_path], capture_output=True)
                    if res.returncode != 0:
                        # If that fails, we can try via a temporary container that mounts the path
                        # but that might be overkill. Let's just log that we rely on --since.
                        print("⚠️  Could not truncate log file directly (permission denied). Using strict --since filtering instead.")
            else:
                print("⚠️  Could not find log path for container.")
        except Exception as e:
            print(f"⚠️  Failed to clear container logs: {e}")

    def fetch_deadlocks(self):
        """Fetches and parses deadlocks from the container's error log."""
        self.deadlocks = []
        try:
            # Use UTC for since_ts as Docker usually logs in UTC
            import datetime as dt
            since_ts = (self.start_time - dt.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S")
            cmd = ["docker", "logs", "--since", since_ts, self.args.container]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            log_content = process.stdout + process.stderr
            
            # Simplified regex: start at *** (1) TRANSACTION and end at WE ROLL BACK TRANSACTION
            pattern = re.compile(r'(\*\*\* \(1\) TRANSACTION:.*?\*\*\* WE ROLL BACK TRANSACTION.*?\n)', re.DOTALL)
            matches = pattern.findall(log_content)
            
            for match in matches:
                self.deadlocks.append(match.strip())
            
            if self.deadlocks:
                print(f"⚠️  Found {len(self.deadlocks)} deadlocks in error logs.")
            else:
                if "deadlock" in log_content.lower():
                    print("⚠️  Deadlocks mentioned in logs but regex failed to extract blocks.")
                    # Show a bigger sample
                    sample_idx = log_content.find("*** (1) TRANSACTION:")
                    if sample_idx != -1:
                        print(f"DEBUG: Log sample (1000 chars):\n{log_content[sample_idx:sample_idx+1000]}")
        except Exception as e:
            print(f"⚠️  Failed to fetch deadlocks: {e}")

    def fetch_environment_details(self):
        """Captures MariaDB config, Lua script, and SQL files for reproducibility."""
        print("🔍 Fetching environment details...")
        
        # 1. Database Configuration (if container)
        if self.args.container:
            try:
                cmd = [
                    "docker", "exec", self.args.container, 
                    "mariadb", "-u", self.args.user
                ]
                if self.args.password:
                    cmd.append(f"-p{self.args.password}")
                cmd.extend(["-e", "SHOW VARIABLES;"])
                process = subprocess.run(cmd, capture_output=True, text=True)
                if process.returncode == 0:
                    relevant_patterns = [
                        r'^innodb_', r'^query_cache_', r'^join_buffer_', 
                        r'^sort_buffer_', r'^read_buffer_', r'^tmp_table_', 
                        r'^max_heap_table_', r'^max_connections', r'^thread_pool',
                        r'^wait_timeout', r'^interactive_timeout', r'^log_bin',
                        r'^sync_binlog', r'^slow_query_log', r'^long_query_time',
                        r'^version', r'^datadir', r'^character_set_server', r'^collation_server'
                    ]
                    for line in process.stdout.splitlines():
                        parts = line.split('\t')
                        if len(parts) == 2:
                            name, val = parts[0], parts[1]
                            if any(re.match(p, name) for p in relevant_patterns):
                                self.env_details['db_config'][name] = val
            except Exception as e:
                print(f"⚠️  Could not fetch DB variables: {e}")

        # 2. MariaDB Error Log snippet (if container)
        if self.args.container:
            try:
                import datetime as dt
                since_ts = (self.start_time - dt.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S")
                cmd = ["docker", "logs", "--since", since_ts, self.args.container]
                process = subprocess.run(cmd, capture_output=True, text=True)
                self.env_details['error_log'] = process.stdout + process.stderr
            except Exception as e:
                print(f"⚠️  Could not fetch error logs: {e}")

        # 3. Lua Script
        lua_path = "scripts/dir_transactions_sysbench.lua"
        if os.path.exists(lua_path):
            with open(lua_path, 'r') as f:
                self.env_details['lua_script'] = f.read()

        # 3. SQL Scripts
        if os.path.exists(self.args.sql_dir):
            for filename in os.listdir(self.args.sql_dir):
                if filename.endswith(".sql"):
                    path = os.path.join(self.args.sql_dir, filename)
                    try:
                        with open(path, 'r') as f:
                            self.env_details['sql_scripts'][filename] = f.read()
                    except Exception as e:
                        print(f"⚠️  Could not read SQL file {filename}: {e}")

        # 4. Infrastructure Metadata
        self.env_details['infra'] = {
            'OS': f"{platform.system()} {platform.release()}",
            'CPU Cores': multiprocessing.cpu_count(),
            'Hostname': platform.node(),
            'Container': self.args.container or "None",
            'DB Version': self.env_details['db_config'].get('version', 'Unknown'),
            'Concurrency': f"{self.args.threads} Threads",
            'Experiment Time': f"{self.args.time} Seconds",
            'Target Storage': self.args.db,
            'Host Node': self.args.host
        }
        
        # Try to get RAM info if on Linux
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        self.env_details['infra']['Total RAM'] = f"{int(line.split()[1]) // 1024} MB"
                        break
        except:
            pass

        # Save infrastructure metadata for MT-reporter compatibility
        try:
            # We assume dumps_dir is the same as where the reports are going, 
            # or specifically in a 'Dumps' subfolder if it exists.
            # In MT-reporter logic, it's usually passed via --dumps.
            # For now, let's just save it in the results/dumps if we can find it.
            # Actually, db_simulator doesn't have a 'dumps' arg, it just runs.
            # But let's save it to 'reports/infrastructure.json' so it can be picked up.
            infra_json_path = os.path.join(self.output_dir, "infrastructure.json")
            with open(infra_json_path, 'w') as f:
                json.dump(self.env_details['infra'], f, indent=4)
            print(f"📊 Infrastructure metadata saved to {infra_json_path}")
        except Exception as e:
            print(f"⚠️  Could not save infrastructure.json: {e}")

    def parse_sysbench_output(self, output):
        """Parses metrics from sysbench output."""
        self.results = {
            'threads': self.args.threads,
            'time': self.args.time,
            'host': self.args.host,
            'db': self.args.db,
            'tps': self._extract(r'transactions:.*?\((\d+\.\d+) per sec\.\)', output),
            'qps': self._extract(r'queries:.*?\((\d+\.\d+) per sec\.\)', output),
            'avg_lat': self._extract(r'avg:\s+(\d+\.\d+)', output),
            'p95_lat': self._extract(r'95th percentile:\s+(\d+\.\d+)', output),
            'max_lat': self._extract(r'max:\s+(\d+\.\d+)', output),
            'total_events': self._extract(r'total number of events:\s+(\d+)', output),
            'read': self._extract(r'read:\s+(\d+)', output),
            'write': self._extract(r'write:\s+(\d+)', output),
            'other': self._extract(r'other:\s+(\d+)', output),
        }

    def _extract(self, pattern, content):
        match = re.search(pattern, content)
        if match:
            try:
                val = match.group(1)
                return float(val) if '.' in val else int(val)
            except ValueError:
                return 0
        return 0

    def generate_reports(self):
        """Generates Markdown and Premium HTML reports."""
        os.makedirs(self.output_dir, exist_ok=True)
        self._generate_markdown()
        self._generate_html()

    def _generate_markdown(self):
        lines = [
            f"# 📊 DB Simulation: {self.args.name.upper()}",
            f"**Generated:** {self.timestamp}\n",
            f"## Connection Info",
            f"- **Host:** `{self.results['host']}`",
            f"- **Database:** `{self.results['db']}`",
            f"- **Threads:** `{self.results['threads']}`",
            f"- **Duration:** `{self.results['time']}s`",
            f"\n## Key Metrics",
            f"| Metric | Value |",
            f"|---|---|",
            f"| **TPS** | {self.results['tps']:.2f} |",
            f"| **QPS** | {self.results['qps']:.2f} |",
            f"| **Avg Latency** | {self.results['avg_lat']:.2f} ms |",
            f"| **95th Latency** | {self.results['p95_lat']:.2f} ms |",
            f"| **Total Events** | {self.results['total_events']} |",
            f"\n## 🏗️ Infrastructure",
        ]
        
        for k, v in self.env_details['infra'].items():
            lines.append(f"- **{k}:** `{v}`")
        
        lines.append("")

        if hasattr(self, 'deadlocks') and self.deadlocks:
            lines.extend([
                f"\n## ⚠️ Deadlocks Detected",
                f"The simulation triggered {len(self.deadlocks)} deadlock(s).\n"
            ])
            for d in self.deadlocks[:3]: # Show first 3 in MD
                lines.append(f"```text\n{d}\n```\n")

        lines.extend([
            f"\n## 🛠️ Reproducibility",
            f"### Execution Command",
            f"```bash\n{self.env_details['sysbench_cmd']}\n```",
        ])

        if self.env_details['db_config']:
            lines.append(f"\n### Database Configuration (Sample)")
            lines.append(f"| Variable | Value |")
            lines.append(f"|---|---|")
            for k in sorted(self.env_details['db_config'].keys()):
                lines.append(f"| `{k}` | `{self.env_details['db_config'][k]}` |")

        if self.env_details['error_log']:
            lines.append(f"\n### MariaDB Error Log (Tail)")
            lines.append(f"```text\n{self.env_details['error_log']}\n```")

        if self.env_details['lua_script']:
            lines.append(f"\n### Lua Script")
            lines.append(f"```lua\n{self.env_details['lua_script']}\n```")

        if self.env_details['sql_scripts']:
            lines.append(f"\n### SQL Transaction Files")
            for name, content in self.env_details['sql_scripts'].items():
                lines.append(f"#### {name}")
                lines.append(f"```sql\n{content}\n```")

        with open(self.output_md, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Markdown report: {self.output_md}")

    def _generate_html(self):
        # 1. Prepare Infra Section
        infra_items = ""
        for k, v in self.env_details['infra'].items():
            infra_items += f"""
            <div class="glass rounded-2xl p-4 border border-white/5">
                <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">{k}</div>
                <div class="text-sm font-mono text-slate-200">{v}</div>
            </div>"""

        infra_html = f"""
        <section class="mb-12">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                Infrastructure Metadata
            </h2>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {infra_items}
            </div>
        </section>
        """

        # 2. Prepare Deadlock Section
        deadlock_html = ""
        if hasattr(self, 'deadlocks') and self.deadlocks:
            events = ""
            for d in self.deadlocks[:10]:
                events += f"""
                <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4">
                    <pre class="whitespace-pre-wrap text-[10px] text-red-300 font-mono">{html.escape(d)}</pre>
                </div>"""
            
            deadlock_html = f"""
            <section class="glass rounded-3xl p-8 mb-12 border-red-500/20">
                <h2 class="text-xl font-bold mb-6 flex items-center gap-3 text-red-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Deadlock Analysis ({len(self.deadlocks)} detected)
                </h2>
                <div class="max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
                    {events}
                </div>
            </section>
            """

        # 2. Prepare Config Section (Relevant variables)
        config_text = ""
        if self.env_details['db_config']:
            sorted_keys = sorted(self.env_details['db_config'].keys())
            max_key_len = max(len(k) for k in sorted_keys) if sorted_keys else 0
            for k in sorted_keys:
                config_text += f"{k.ljust(max_key_len)} = {self.env_details['db_config'][k]}\n"

        # 3. Prepare Scripts Section
        sql_blocks = ""
        for name, content in self.env_details['sql_scripts'].items():
            sql_blocks += f"""
            <div class="mb-6 last:mb-0">
                <div class="flex items-center gap-2 mb-2 text-slate-500">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <span class="text-[10px] font-bold uppercase tracking-wider">{name}</span>
                </div>
                <div class="bg-slate-950/50 border border-slate-800 rounded-xl p-4">
                    <pre class="text-[11px] text-emerald-400 font-mono overflow-x-auto whitespace-pre-wrap">{html.escape(content)}</pre>
                </div>
            </div>"""

        repro_html = f"""
        <section class="glass rounded-3xl p-8 mb-12">
            <h2 class="text-xl font-bold mb-8 flex items-center gap-3">
                <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                Reproducibility Lab
            </h2>

            <div class="space-y-8">
                <!-- Command -->
                <div>
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <span class="w-1 h-1 rounded-full bg-purple-500"></span>
                        Execution Command
                    </h3>
                    <div class="bg-slate-950 border border-purple-500/20 rounded-2xl p-6 font-mono text-xs text-purple-300 leading-relaxed break-all">
                        {html.escape(self.env_details['sysbench_cmd'])}
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Config -->
                    <div>
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <span class="w-1 h-1 rounded-full bg-blue-500"></span>
                            MariaDB Configuration
                        </h3>
                        <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 h-[332px] overflow-y-auto custom-scrollbar">
                            <pre class="text-[11px] text-blue-300 font-mono leading-relaxed">{html.escape(config_text)}</pre>
                        </div>
                    </div>

                    <!-- Lua Script -->
                    <div>
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <span class="w-1 h-1 rounded-full bg-emerald-500"></span>
                            Sysbench Lua Driver
                        </h3>
                        <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 h-[332px] overflow-y-auto custom-scrollbar">
                            <pre class="text-[11px] text-emerald-400 font-mono leading-relaxed">{html.escape(self.env_details['lua_script'])}</pre>
                        </div>
                    </div>

                    <!-- Error Log -->
                    <div class="lg:col-span-2">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <span class="w-1 h-1 rounded-full bg-red-500"></span>
                            MariaDB Error Log (Captured during test)
                        </h3>
                        <div class="bg-black/40 border border-red-500/10 rounded-2xl p-6 max-h-[400px] overflow-y-auto custom-scrollbar">
                            <pre class="text-[10px] text-red-300 font-mono leading-tight whitespace-pre-wrap">{html.escape(self.env_details['error_log'])}</pre>
                        </div>
                    </div>
                </div>

                <!-- SQL Scripts -->
                <div>
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <span class="w-1 h-1 rounded-full bg-amber-500"></span>
                        Transaction SQL Files
                    </h3>
                    <div class="glass rounded-2xl p-8">
                        {sql_blocks}
                    </div>
                </div>
            </div>
        </section>
        """

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB Simulation Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #070b14; color: #f8fafc; }}
        .glass {{ background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }}
        .gradient-text {{ background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: rgba(255, 255, 255, 0.02); }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.08); border-radius: 10px; }}
        pre {{ scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent; }}
    </style>
</head>
<body class="min-h-screen p-8 md:p-16">
    <div class="max-w-5xl mx-auto">
        <header class="mb-16">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
                <div>
                    <h1 class="text-6xl font-extrabold tracking-tight mb-4 gradient-text">{self.args.name.upper()}</h1>
                    <p class="text-slate-400 text-lg font-medium max-w-xl leading-relaxed">Performance audit for {self.results['host']} / {self.results['db']}</p>
                </div>
                <div class="text-right">
                    <div class="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-3 justify-end mb-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Audit Completed
                    </div>
                    <div class="text-slate-300 font-mono text-sm">{self.timestamp}</div>
                </div>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div class="glass rounded-3xl p-8 border-blue-500/20">
                <h3 class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-4">Throughput</h3>
                <div class="flex items-baseline gap-2 mb-1">
                    <span class="text-4xl font-black text-white">{self.results['tps']:.2f}</span>
                    <span class="text-blue-400 text-xs font-bold">TPS</span>
                </div>
                <div class="text-slate-500 text-sm font-medium">{self.results['qps']:.1f} queries/sec</div>
            </div>
            <div class="glass rounded-3xl p-8 border-amber-500/20">
                <h3 class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-4">Latency AVG</h3>
                <div class="flex items-baseline gap-2 mb-1">
                    <span class="text-4xl font-black text-amber-400">{self.results['avg_lat']:.2f}</span>
                    <span class="text-slate-500 text-xs font-bold">ms</span>
                </div>
                <div class="w-full bg-slate-800/50 rounded-full h-1 mt-2">
                    <div class="bg-amber-400 h-full rounded-full" style="width: 45%"></div>
                </div>
            </div>
            <div class="glass rounded-3xl p-8 border-orange-500/20">
                <h3 class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-4">Latency P95</h3>
                <div class="flex items-baseline gap-2 mb-1">
                    <span class="text-4xl font-black text-orange-500">{self.results['p95_lat']:.2f}</span>
                    <span class="text-slate-500 text-xs font-bold">ms</span>
                </div>
                <div class="w-full bg-slate-800/50 rounded-full h-1 mt-2">
                    <div class="bg-orange-500 h-full rounded-full" style="width: 65%"></div>
                </div>
            </div>
            <div class="glass rounded-3xl p-8 border-emerald-500/20">
                <h3 class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-4">Efficiency</h3>
                <div class="flex items-baseline gap-2 mb-1">
                    <span class="text-4xl font-black text-emerald-400">{self.results['total_events']}</span>
                </div>
                <div class="text-slate-500 text-sm font-medium">Total events processed</div>
            </div>
        </div>

        {infra_html}

        {deadlock_html}
        {repro_html}


        <footer class="flex items-center justify-between border-t border-slate-800 pt-12 text-slate-600 text-[10px] font-bold uppercase tracking-[0.3em]">
            <span>&copy; {datetime.now().year} MT-Reporter &bull; DB Simulation Suite</span>
            <span class="flex items-center gap-2">
                <span class="w-3 h-px bg-slate-800"></span>
                v1.1.0 Ready
            </span>
        </footer>
    </div>
</body>
</html>
        """
        with open(self.output_html, 'w') as f:
            f.write(html_template)
        print(f"✅ HTML report: {self.output_html}")

def main():
    parser = argparse.ArgumentParser(description="Generic DB Simulator and Reporter")
    parser.add_argument("--sql-dir", required=True, help="Directory containing .sql transaction files")
    parser.add_argument("--host", default="127.0.0.1", help="Database host")
    parser.add_argument("--user", default="root", help="Database user")
    parser.add_argument("--password", default="", help="Database password")
    parser.add_argument("--db", default="employees", help="Database name")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--time", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--container", help="Optional Docker container name")
    parser.add_argument("--name", default="Generic Test", help="Nature of the test (e.g. Deadlock, Gap Locking)")
    parser.add_argument("--output-dir", help="Directory where reports will be saved")
    
    args = parser.parse_args()
    
    sim = DBSimulator(args)
    if sim.run_simulation():
        sim.generate_reports()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
