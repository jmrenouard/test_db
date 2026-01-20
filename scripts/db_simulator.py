#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
import json
from datetime import datetime

class DBSimulator:
    def __init__(self, args):
        self.args = args
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results = {}
        self.output_md = "reports/simulator_report.md"
        self.output_html = "reports/simulator_report.html"

    def run_simulation(self):
        """Runs the sysbench simulation via run_dir_bench.sh and captures output."""
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

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"❌ Simulation failed:\n{stderr}")
                return False
            
            self.raw_output = stdout
            self.parse_sysbench_output(stdout)
            
            # Fetch and parse deadlocks if container is specified
            if self.args.container:
                self.fetch_deadlocks()
            
            return True
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False

    def fetch_deadlocks(self):
        """Fetches and parses deadlocks from the container's error log."""
        self.deadlocks = []
        try:
            # Use UTC for since_ts as Docker usually logs in UTC
            import datetime as dt
            since_ts = (self.start_time - dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
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
        os.makedirs("reports", exist_ok=True)
        self._generate_markdown()
        self._generate_html()

    def _generate_markdown(self):
        lines = [
            f"# 📊 Database Simulation Report",
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
        ]

        if hasattr(self, 'deadlocks') and self.deadlocks:
            lines.extend([
                f"\n## ⚠️ Deadlocks Detected",
                f"The simulation triggered {len(self.deadlocks)} deadlock(s). See logs for details.\n"
            ])
            for d in self.deadlocks[:5]: # Show first 5
                lines.append(f"```text\n{d}\n```\n")

        with open(self.output_md, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Markdown report: {self.output_md}")

    def _generate_html(self):
        deadlock_html = ""
        if hasattr(self, 'deadlocks') and self.deadlocks:
            events = ""
            for d in self.deadlocks[:5]:
                events += f"""
                <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4">
                    <pre class="whitespace-pre-wrap text-[10px] text-red-300 font-mono">{d}</pre>
                </div>"""
            
            deadlock_html = f"""
            <section class="glass rounded-3xl p-8 mb-12 border-red-500/30">
                <h2 class="text-xl font-bold mb-6 flex items-center gap-3 text-red-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Deadlock Analysis ({len(self.deadlocks)} detected)
                </h2>
                <div class="max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
                    {events}
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
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #0f172a; color: #f8fafc; }}
        .glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .gradient-text {{ background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: rgba(255, 255, 255, 0.05); }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 10px; }}
    </style>
</head>
<body class="min-h-screen p-8 md:p-16">
    <div class="max-w-4xl mx-auto">
        <header class="mb-12">
            <h1 class="text-5xl font-extrabold tracking-tight mb-2 gradient-text">Simulation Results</h1>
            <p class="text-slate-400 font-medium">Performance audit for {self.results['host']}</p>
            <div class="mt-4 text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Generated at {self.timestamp}
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <div class="glass rounded-3xl p-8">
                <h3 class="text-slate-500 text-xs font-bold uppercase tracking-widest mb-4">Throughput</h3>
                <div class="flex items-baseline gap-2 mb-1">
                    <span class="text-4xl font-black text-white">{self.results['tps']:.2f}</span>
                    <span class="text-slate-400 text-sm font-bold uppercase">TPS</span>
                </div>
                <div class="flex items-baseline gap-2">
                    <span class="text-2xl font-bold text-blue-400">{self.results['qps']:.2f}</span>
                    <span class="text-slate-500 text-xs font-bold uppercase">QPS</span>
                </div>
            </div>
            <div class="glass rounded-3xl p-8">
                <h3 class="text-slate-500 text-xs font-bold uppercase tracking-widest mb-4">Latency (ms)</h3>
                <div class="flex items-baseline gap-4 mb-4">
                    <div>
                        <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">Average</span>
                        <span class="text-2xl font-black text-amber-400">{self.results['avg_lat']:.2f}</span>
                    </div>
                    <div>
                        <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">95th Percentile</span>
                        <span class="text-2xl font-black text-orange-500">{self.results['p95_lat']:.2f}</span>
                    </div>
                </div>
                <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full" style="width: 75%"></div>
                </div>
            </div>
        </div>

        {deadlock_html}

        <section class="glass rounded-3xl p-8 mb-12">
            <h2 class="text-xl font-bold mb-6 flex items-center gap-3">
                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Execution Metadata
            </h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
                <div>
                    <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">Threads</span>
                    <span class="text-lg font-bold">{self.results['threads']}</span>
                </div>
                <div>
                    <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">Duration</span>
                    <span class="text-lg font-bold">{self.results['time']}s</span>
                </div>
                <div>
                    <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">Database</span>
                    <span class="text-lg font-bold">{self.results['db']}</span>
                </div>
                <div>
                    <span class="block text-slate-500 text-[10px] font-bold uppercase mb-1">Total Events</span>
                    <span class="text-lg font-bold">{self.results['total_events']}</span>
                </div>
            </div>
        </section>

        <footer class="text-center text-slate-600 text-xs font-bold uppercase tracking-[0.2em]">
            &copy; {datetime.now().year} DB Simulator &bull; Premium Performance Suite
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
    parser.add_argument("--password", default="root", help="Database password")
    parser.add_argument("--db", default="employees", help="Database name")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--time", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--container", help="Optional Docker container name")
    
    args = parser.parse_args()
    
    sim = DBSimulator(args)
    if sim.run_simulation():
        sim.generate_reports()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
