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
            return True
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False

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
        with open(self.output_md, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Markdown report: {self.output_md}")

    def _generate_html(self):
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
