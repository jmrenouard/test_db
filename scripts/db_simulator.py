#!/usr/bin/env python3
"""
scripts/db_simulator.py
================================================================================
Generic MariaDB Simulation & Premium Reporting Tool
================================================================================
Purpose:
  Orchestrates complex database simulations by running sysbench with directory-
  based transactions and generating high-quality HTML/Markdown reports.

Workflow:
  1. Environment Preparation: Truncates container logs and runs setup.sql.
  2. Simulation: Launches sysbench via run_dir_bench.sh wrapper.
  3. Analysis:
     - Parses sysbench metrics (TPS, QPS, Latency).
     - Fetches Docker logs and extracts deadlock blocks via regex.
     - Captures DB variables and infrastructure metadata.
  4. Cleanup: Runs teardown.sql.
  5. Reporting: Generates glassmorphism HTML and descriptive Markdown reports.

Usage:
  python3 scripts/db_simulator.py --sql-dir tests/data/deadlock/ \
    --container mariadb-11-8 --name "Deadlock Test"
================================================================================
"""
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

# Detect USE_CONTAINER mode
USE_CONTAINER_ENV = os.environ.get('USE_CONTAINER', 'true').lower()
USE_CONTAINER_GLOBAL = USE_CONTAINER_ENV not in ('false', '0', 'no', 'off', 'disable')

class DBSimulator:
    def __init__(self, args):
        """Initializes the simulator with CLI arguments and sets up reporting paths."""
        self.args = args
        # Standardize container usage based on global env if not explicitly disabled in args
        if not USE_CONTAINER_GLOBAL:
            self.args.container = None
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
        
        # Determine output filenames based on directory structure
        if self.args.output_dir and self.args.output_dir != "reports":
            self.output_md = os.path.join(self.output_dir, f"report_{self.test_name}.md")
            self.output_html = os.path.join(self.output_dir, f"report_{self.test_name}.html")
        else:
            self.output_md = os.path.join(self.output_dir, f"report_{self.test_name}_{self.ts_slug}.md")
            self.output_html = os.path.join(self.output_dir, f"report_{self.test_name}_{self.ts_slug}.html")

        # Ensure output directory exists before any writing
        os.makedirs(self.output_dir, exist_ok=True)

    def run_simulation(self):
        """
        Main execution flow:
        1. Cleanup logs
        2. Run setup.sql
        3. Execute performance test
        4. Capture metrics and analysis
        5. Run teardown.sql
        """
        # Pre-simulation: Clear container logs to ensure transparency
        if self.args.container:
            self.clear_container_logs()
            
        # Capture start time to filter logs later
        self.start_time = datetime.now()
        
        # Display Configuration Summary
        print(f"🚀 Starting simulation on {self.args.host}...")
        print(f"   ├─ Nature:   {self.args.name}")
        print(f"   ├─ Threads:  {self.args.threads}")
        print(f"   ├─ Duration: {self.args.time}s")
        if self.args.script:
            print(f"   ├─ Script:   {self.args.script}")
        if self.args.tables:
            print(f"   ├─ Tables:   {self.args.tables}")
        if self.args.table_size:
            print(f"   └─ Size:     {self.args.table_size}")
        else:
            print(f"   └─ Target:   {self.args.db}")
        print("")

        # Wrapper command that invokes our custom Lua script
        cmd = [
            "bash", "scripts/run_dir_bench.sh",
            "--threads", str(self.args.threads),
            "--time", str(self.args.time),
            "--host", self.args.host,
            "--user", self.args.user,
            "--password", self.args.password,
            "--db", self.args.db
        ]

        if self.args.script:
            cmd.extend(["--script", self.args.script])
        else:
            cmd.extend(["--sql-dir", self.args.sql_dir])

        if self.args.container:
            cmd.extend(["--container", self.args.container])

        # Pre-simulation: Run setup.sql if it exists (e.g. for creating state/tables)
        if self.args.sql_dir:
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
            # Execute simulation via subprocess
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"❌ Simulation failed:\n{stderr}")
                return False
            
            self.raw_output = stdout
            
            # Reconstruct sysbench command for transparency in the report
            # The actual execution happens inside run_dir_bench.sh, which handles the container logic.
            # We match the reconstruction to what was actually executed.
            sb_cmd = [
                "sysbench",
                f"--mysql-host={self.args.host}",
                f"--mysql-user={self.args.user}",
                f"--mysql-password={self.args.password}" if self.args.password else "--mysql-password=",
                f"--mysql-db={self.args.db}",
                f"--threads={self.args.threads}",
                f"--time={self.args.time}",
                "--events=0"
            ]

            if getattr(self.args, 'tables', None):
                sb_cmd.append(f"--tables={self.args.tables}")
            if getattr(self.args, 'table_size', None):
                sb_cmd.append(f"--table-size={self.args.table_size}")
            
            if self.args.sql_dir:
                sb_cmd.insert(5, "--sql-dir=/tmp/bench_dir/sql/")
                sb_cmd.append("/tmp/dir_transactions_sysbench.lua run")
            else:
                sb_cmd.append(f"{self.args.script} run")
            
            if self.args.container:
                reconstructed_cmd = f"docker exec -i {self.args.container} " + " ".join(sb_cmd)
            else:
                reconstructed_cmd = " ".join(sb_cmd)
                
            self.env_details['sysbench_cmd'] = reconstructed_cmd
            
            # Parse metrics from stdout
            self.parse_sysbench_output(stdout)
            
            # Fetch and parse deadlocks if container is specified
            if self.args.container:
                self.fetch_deadlocks()
            
            # Gather configuration and infrastructure data
            self.fetch_environment_details()
            
            # Post-simulation: Run teardown.sql if it exists
            self.run_cleanup()
            
            return True
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False

    def run_cleanup(self):
        """Runs teardown.sql if it exists in the test directory."""
        if not self.args.sql_dir:
            return
            
        teardown_script = os.path.join(self.args.sql_dir, "teardown.sql")
        if os.path.exists(teardown_script):
            print(f"🧹 Running teardown script: {teardown_script}")
            cleanup_cmd = [
                "docker", "exec", "-i", self.args.container or "mariadb-11-8",
                "mariadb", "-u", self.args.user
            ]
            if self.args.password:
                cleanup_cmd.append(f"-p{self.args.password}")
            cleanup_cmd.append(self.args.db)
            try:
                with open(teardown_script, 'r') as f:
                    subprocess.run(cleanup_cmd, stdin=f, check=True)
            except Exception as e:
                print(f"⚠️  Teardown script failed: {e}")

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
        """
        Retrieves deadlocks from the MariaDB container logs.
        Uses --since strategy with a 1-second overlap to capture events 
        that occurred during the simulation.
        """
        self.deadlocks = []
        try:
            # Docker logs are usually UTC; we use a 1-second buffer to be safe
            import datetime as dt
            since_ts = (self.start_time - dt.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S")
            cmd = ["docker", "logs", "--since", since_ts, self.args.container]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            log_content = process.stdout + process.stderr
            
            # REGEX LOGIC:
            # InnoDB deadlock reports start with '*** (1) TRANSACTION:'
            # and end with '*** WE ROLL BACK TRANSACTION'.
            pattern = re.compile(r'(\*\*\* \(1\) TRANSACTION:.*?\*\*\* WE ROLL BACK TRANSACTION.*?\n)', re.DOTALL)
            matches = pattern.findall(log_content)
            
            for match in matches:
                self.deadlocks.append(match.strip())
            
            if self.deadlocks:
                print(f"⚠️  Found {len(self.deadlocks)} deadlocks in error logs.")
            else:
                # Fallback if text is present but regex didn't match perfectly
                if "deadlock" in log_content.lower():
                    print("⚠️  Deadlocks mentioned in logs but regex failed to extract blocks.")
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
                cmd.extend(["-e", "SHOW GLOBAL VARIABLES;"])
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
        if self.args.sql_dir and os.path.exists(self.args.sql_dir):
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
            'min_lat': self._extract(r'min:\s+(\d+\.\d+)', output),
            'sum_lat': self._extract(r'sum:\s+(\d+\.\d+)', output),
            'events_avg': self._extract(r'events \(avg/stddev\):\s+(\d+\.\d+)', output),
            'events_stddev': self._extract(r'events \(avg/stddev\):.*?/(\d+\.\d+)', output),
            'execution_avg': self._extract(r'execution time \(avg/stddev\):\s+(\d+\.\d+)', output),
            'execution_stddev': self._extract(r'execution time \(avg/stddev\):.*?/(\d+\.\d+)', output),
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
        """
        Entry point for reporting. 
        Creates both Markdown (for quick review/logs) and HTML (for presentation).
        """
        os.makedirs(self.output_dir, exist_ok=True)
        self._generate_markdown()
        self._generate_html()
        self._save_raw_results()

    def _save_raw_results(self):
        """Save raw sysbench output to a text file."""
        if self.raw_output:
            raw_path = os.path.join(self.output_dir, "result_sysbench.txt")
            with open(raw_path, 'w') as f:
                f.write(self.raw_output)
            print(f"📄 Raw results saved to {raw_path}")

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
            f"| **TPS** | {self.results.get('tps', 0):.2f} |",
            f"| **QPS** | {self.results.get('qps', 0):.2f} |",
            f"| **Avg Latency** | {self.results.get('avg_lat', 0):.2f} ms |",
            f"| **95th Latency** | {self.results.get('p95_lat', 0):.2f} ms |",
            f"| **Total Events** | {self.results.get('total_events', 0)} |",
            f"\n## 📊 Detailed Metrics",
            f"### SQL Statistics",
            f"- **Read:** `{self.results.get('read', 0)}`",
            f"- **Write:** `{self.results.get('write', 0)}`",
            f"- **Other:** `{self.results.get('other', 0)}`",
            f"\n### Latency Details (ms)",
            f"- **Min:** `{self.results.get('min_lat', 0):.2f}`",
            f"- **Avg:** `{self.results.get('avg_lat', 0):.2f}`",
            f"- **Max:** `{self.results.get('max_lat', 0):.2f}`",
            f"- **95th:** `{self.results.get('p95_lat', 0):.2f}`",
            f"- **Sum:** `{self.results.get('sum_lat', 0):.2f}`",
            f"\n### Threads Fairness",
            f"- **Events (avg/stddev):** `{self.results.get('events_avg', 0)} / {self.results.get('events_stddev', 0)}`",
            f"- **Execution time (avg/stddev):** `{self.results.get('execution_avg', 0)} / {self.results.get('execution_stddev', 0)}`",
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

        if self.env_details['error_log'] and self.env_details['error_log'].strip():
            lines.append(f"\n### MariaDB Error Log (Tail)")
            lines.append(f"```text\n{self.env_details['error_log']}\n```")

        if self.env_details['lua_script'] and self.args.sql_dir:
            lines.append(f"\n### Lua Script")
            lines.append(f"```lua\n{self.env_details['lua_script']}\n```")

        if self.env_details['sql_scripts']:
            lines.append(f"\n### SQL Transaction Files")
            for name, content in self.env_details['sql_scripts'].items():
                lines.append(f"#### {name}")
                lines.append(f"```sql\n{content}\n```")

        if self.raw_output:
            lines.append(f"\n## 📄 Raw Sysbench Output")
            lines.append(f"```text\n{self.raw_output}\n```")

        with open(self.output_md, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Markdown report: {self.output_md}")

    def _generate_html(self):
        # 0. Define metrics for template
        qps = f"{self.results.get('qps', 0):.2f}"
        avg_lat = f"{self.results.get('avg_lat', 0):.2f}"
        lat_95 = f"{self.results.get('p95_lat', 0):.2f}"

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

        # 2. Prepare Detailed Metrics Section
        metrics_html = f"""
        <section class="mb-12">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                Detailed Performance Metrics
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass rounded-2xl p-6">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">SQL Operations</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Read</span><span class="font-mono text-emerald-400">{self.results.get('read', 0)}</span>
                        </div>
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Write</span><span class="font-mono text-amber-400">{self.results.get('write', 0)}</span>
                        </div>
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Other</span><span class="font-mono text-slate-400">{self.results.get('other', 0)}</span>
                        </div>
                    </div>
                </div>
                <div class="glass rounded-2xl p-6">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Latency Details (ms)</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Min</span><span class="font-mono">{self.results.get('min_lat', 0):.2f}</span>
                        </div>
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Max</span><span class="font-mono text-rose-400">{self.results.get('max_lat', 0):.2f}</span>
                        </div>
                        <div class="flex justify-between border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Sum</span><span class="font-mono">{self.results.get('sum_lat', 0):.2f}</span>
                        </div>
                    </div>
                </div>
                <div class="glass rounded-2xl p-6">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Thread Fairness</h3>
                    <div class="space-y-3">
                        <div class="flex flex-col border-b border-slate-800 pb-2">
                            <span class="text-[10px] text-slate-500 uppercase mb-1">Events (Avg/Std)</span>
                            <span class="font-mono text-indigo-400">{self.results.get('events_avg', 0)} / {self.results.get('events_stddev', 0)}</span>
                        </div>
                        <div class="flex flex-col border-b border-slate-800 pb-2">
                            <span class="text-[10px] text-slate-500 uppercase mb-1">Execution (Avg/Std)</span>
                            <span class="font-mono text-indigo-400">{self.results.get('execution_avg', 0)} / {self.results.get('execution_stddev', 0)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        """

        # 3. Prepare Deadlock Section
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

        # 4. Prepare Config Section
        config_text = ""
        if self.env_details['db_config']:
            sorted_keys = sorted(self.env_details['db_config'].keys())
            max_key_len = max(len(k) for k in sorted_keys) if sorted_keys else 0
            for k in sorted_keys:
                config_text += f"{k.ljust(max_key_len)} = {self.env_details['db_config'][k]}\n"

        # 5. Prepare Error Log Section (Conditional)
        error_log_html = ""
        if self.env_details['error_log'] and self.env_details['error_log'].strip():
            error_log_html = f"""
            <div class="lg:col-span-2">
                <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <span class="w-1 h-1 rounded-full bg-red-500"></span>
                    MariaDB Error Log (Captured during test)
                </h3>
                <div class="bg-black/40 border border-red-500/10 rounded-2xl p-6 max-h-[400px] overflow-y-auto custom-scrollbar">
                    <pre class="text-[10px] text-red-300 font-mono leading-tight whitespace-pre-wrap">{html.escape(self.env_details['error_log'])}</pre>
                </div>
            </div>"""

        # 6. Prepare Scripts Section (Conditional)
        sql_scripts_section = ""
        if self.env_details['sql_scripts']:
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
            
            sql_scripts_section = f"""
                <div>
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <span class="w-1 h-1 rounded-full bg-amber-500"></span>
                        Transaction SQL Files
                    </h3>
                    <div class="glass rounded-2xl p-8">
                        {sql_blocks}
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

                    {error_log_html}
                </div>

                <!-- SQL Scripts -->
                {sql_scripts_section}
            </div>
        </section>
        """

        # 7. Prepare Raw Output Section
        raw_html = ""
        if self.raw_output:
            raw_html = f"""
            <section class="mb-12">
                <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Raw Sysbench Output
                </h2>
                <div class="bg-black/40 border border-slate-700/30 rounded-2xl p-6 max-h-[500px] overflow-y-auto custom-scrollbar">
                    <pre class="text-[10px] text-slate-400 font-mono leading-tight whitespace-pre-wrap">{html.escape(self.raw_output)}</pre>
                </div>
            </section>
            """

        # Final Template assembly
        if self.args.script:
            script_display = os.path.basename(self.args.script)
        else:
            script_display = "SQL Files"

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB Simulation Report - {self.args.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --accent: #f43f5e;
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
        }}
        body {{ font-family: 'Outfit', sans-serif; background-color: var(--bg-dark); color: #f8fafc; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: transparent; }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 10px; }}
    </style>
</head>
<body class="p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
            <div>
                <span class="inline-block px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase tracking-wider mb-4 border border-indigo-500/20">
                    Simulation Analytics
                </span>
                <h1 class="text-5xl md:text-6xl font-bold tracking-tight mb-2">
                    {self.args.name}
                </h1>
                <p class="text-slate-400 max-w-2xl text-lg">
                    Comprehensive performance report generated on <span class="text-white font-semibold">{self.timestamp}</span>.
                </p>
            </div>
            <div class="flex gap-4">
                <div class="px-6 py-3 rounded-2xl bg-slate-800/50 border border-slate-700/50">
                    <p class="text-slate-500 text-[10px] font-bold uppercase tracking-wider mb-1">Target Engine</p>
                    <p class="text-white font-semibold">MariaDB</p>
                </div>
                <div class="px-6 py-3 rounded-2xl bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20">
                    {qps} QPS
                </div>
            </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-12">
            <div class="glass p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                <div class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Script</div>
                <div class="text-white text-lg font-bold mono truncate w-full" title="{self.args.script if self.args.script else 'SQL Directory'}">{script_display}</div>
            </div>
            <div class="glass p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                <div class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Threads</div>
                <div class="text-white text-3xl font-bold">{self.args.threads}</div>
            </div>
            <div class="glass p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                <div class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Duration</div>
                <div class="text-white text-3xl font-bold">{self.args.time}s</div>
            </div>
            <div class="glass p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                <div class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Avg Latency</div>
                <div class="text-amber-400 text-3xl font-bold">{avg_lat}ms</div>
            </div>
            <div class="glass p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                <div class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">95th Latency</div>
                <div class="text-rose-400 text-3xl font-bold">{lat_95}ms</div>
            </div>
        </div>

        {infra_html}
        {metrics_html}

        {deadlock_html}
        {repro_html}

        <!-- 4. Prepare Raw Output Section -->
        {raw_html}

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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sql-dir", help="Directory containing .sql transaction files")
    group.add_argument("--script", help="Path to a direct sysbench Lua script")
    
    parser.add_argument("--host", default="127.0.0.1", help="Database host")
    parser.add_argument("--user", default="root", help="Database user")
    parser.add_argument("--password", default="", help="Database password")
    parser.add_argument("--db", default="employees", help="Database name")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--time", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--container", help="Optional Docker container name")
    parser.add_argument("--name", default="Generic Test", help="Nature of the test (e.g. Deadlock, Gap Locking)")
    parser.add_argument("--output-dir", help="Directory where reports will be saved")
    parser.add_argument("--tables", type=int, help="Number of tables for sysbench")
    parser.add_argument("--table-size", type=int, help="Number of rows per table for sysbench")
    
    args = parser.parse_args()
    
    sim = DBSimulator(args)
    if sim.run_simulation():
        sim.generate_reports()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
