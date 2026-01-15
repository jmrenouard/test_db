#!/usr/bin/env python3
import os
import re
import sys
import argparse
from datetime import datetime

class PerfReporter:
    def __init__(self, results_dir, output_md, output_html):
        self.results_dir = results_dir
        self.output_md = output_md
        self.output_html = output_html
        self.data = []

    def parse_results(self):
        """Parses all results_N_threads.txt files in the results directory."""
        if not os.path.exists(self.results_dir):
            print(f"Directory {self.results_dir} not found.")
            return

        files = [f for f in os.listdir(self.results_dir) if f.startswith('results_') and f.endswith('_threads.txt')]
        # Sort by thread number
        files.sort(key=lambda x: int(re.search(r'results_(\d+)_threads\.txt', x).group(1)))

        for filename in files:
            threads = int(re.search(r'results_(\d+)_threads\.txt', filename).group(1))
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'r') as f:
                content = f.read()
                
            metrics = {
                'threads': threads,
                'read': self._extract(r'read:\s+(\d+)', content),
                'write': self._extract(r'write:\s+(\d+)', content),
                'other': self._extract(r'other:\s+(\d+)', content),
                'total': self._extract(r'total:\s+(\d+)', content),
                'transactions': self._extract(r'transactions:\s+(\d+)', content),
                'tps': self._extract(r'transactions:.*?\((\d+\.\d+) per sec\.\)', content),
                'queries_per_sec': self._extract(r'queries:.*?\((\d+\.\d+) per sec\.\)', content),
                'total_time': self._extract(r'total time:\s+(\d+\.\d+)s', content),
                'total_events': self._extract(r'total number of events:\s+(\d+)', content),
                'min_lat': self._extract(r'min:\s+(\d+\.\d+)', content),
                'avg_lat': self._extract(r'avg:\s+(\d+\.\d+)', content),
                'max_lat': self._extract(r'max:\s+(\d+\.\d+)', content),
                'p95_lat': self._extract(r'95th percentile:\s+(\d+\.\d+)', content),
            }
            self.data.append(metrics)

    def _extract(self, pattern, content):
        match = re.search(pattern, content)
        if match:
            try:
                val = match.group(1)
                return float(val) if '.' in val else int(val)
            except ValueError:
                return 0
        return 0

    def generate_markdown(self):
        """Generates a Markdown report."""
        lines = [
            "# 🚀 Performance Scaling Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## Summary Table",
            "| Threads | QPS | TPS | Avg Latency (ms) | 95th Latency (ms) | Total Events |",
            "|---|---|---|---|---|---|"
        ]
        
        for d in self.data:
            lines.append(f"| {d['threads']} | {d['queries_per_sec']:.2f} | {d['tps']:.2f} | {d['avg_lat']:.2f} | {d['p95_lat']:.2f} | {d['total_events']} |")
        
        with open(self.output_md, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Markdown report generated: {self.output_md}")

    def generate_html(self):
        """Generates an HTML report with Tailwind CSS and CSS bar graphs."""
        
        def get_max(key):
            return max([d[key] for d in self.data]) if self.data else 1

        metrics_to_graph = [
            ('queries_per_sec', 'Queries Per Second (QPS)', 'blue'),
            ('tps', 'Transactions Per Second (TPS)', 'indigo'),
            ('avg_lat', 'Average Latency (ms)', 'amber'),
            ('p95_lat', '95th Percentile Latency (ms)', 'orange'),
        ]

        sections_html = ""
        for key, label, color in metrics_to_graph:
            max_val = get_max(key)
            
            bars_html = ""
            table_rows = ""
            
            for d in self.data:
                val = d[key]
                percentage = (val / max_val * 100) if max_val > 0 else 0
                
                bars_html += f"""
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-16 text-right text-xs font-bold text-slate-500">{d['threads']} T</div>
                    <div class="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden group">
                        <div class="bg-{color}-500 h-full transition-all duration-1000 ease-out group-hover:brightness-110" style="width: {percentage}%"></div>
                    </div>
                    <div class="w-24 text-sm font-mono font-bold text-slate-700">{val:.2f}</div>
                </div>
                """
                
                table_rows += f"""
                <tr class="border-b border-slate-50 hover:bg-slate-50/50">
                    <td class="px-4 py-2 font-mono text-sm">{d['threads']}</td>
                    <td class="px-4 py-2 font-mono text-sm text-right">{val:.2f}</td>
                </tr>
                """

            sections_html += f"""
            <section class="bg-white rounded-3xl shadow-xl border border-slate-100 p-8 mb-10">
                <h2 class="text-2xl font-extrabold text-slate-800 mb-6 flex items-center gap-3">
                    <span class="w-2 h-8 bg-{color}-500 rounded-full"></span>
                    {label}
                </h2>
                
                <div class="mb-8">
                    {bars_html}
                </div>
                
                <div class="mt-6 pt-6 border-t border-slate-100">
                    <table class="w-full max-w-md mx-auto text-left">
                        <thead>
                            <tr class="text-[10px] font-bold text-slate-400 uppercase tracking-widest italic">
                                <th class="px-4 py-2">Threads</th>
                                <th class="px-4 py-2 text-right">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </section>
            """

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scaling Performance Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
        .bg-glass {{ background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); }}
    </style>
</head>
<body class="bg-[#F8FAFC] text-slate-900 min-h-screen pb-20">
    <div class="max-w-5xl mx-auto px-6 pt-12">
        <header class="mb-12 relative">
            <div class="absolute -top-6 -left-6 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl"></div>
            <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
            
            <div class="relative flex items-center gap-6 mb-4">
                <div class="w-16 h-16 bg-gradient-to-br from-indigo-600 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-indigo-200">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                </div>
                <div>
                    <h1 class="text-4xl font-extrabold tracking-tight text-slate-900">Scaling Performance</h1>
                    <p class="text-slate-500 font-medium">Detailed analysis of database performance across multiple thread counts</p>
                </div>
            </div>
            
            <div class="flex items-center gap-4 text-xs font-bold text-slate-400 uppercase tracking-widest mt-6">
                <span class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </span>
            </div>
        </header>

        {sections_html}

        <footer class="text-center text-slate-400 text-sm mt-20">
            <p>© {datetime.now().year} MariaDB Scaling Performance Suite</p>
            <div class="mt-4 flex items-center justify-center gap-6 font-bold uppercase tracking-widest text-[10px]">
                <a href="#" class="hover:text-indigo-600">Documentation</a>
                <a href="#" class="hover:text-indigo-600">System Info</a>
                <a href="#" class="hover:text-indigo-600">Raw Data</a>
            </div>
        </footer>
    </div>
</body>
</html>
        """
        with open(self.output_html, 'w') as f:
            f.write(html_content)
        print(f"✅ HTML report generated: {self.output_html}")

def main():
    parser = argparse.ArgumentParser(description="Generate scaling performance reports from sysbench results.")
    parser.add_argument("--dir", default="reports/perf_threads", help="Directory containing results_*_threads.txt files")
    parser.add_argument("--md", default="reports/perf_threads/scaling_report.md", help="Output Markdown file")
    parser.add_argument("--html", default="reports/perf_threads/scaling_report.html", help="Output HTML file")
    
    args = parser.parse_args()
    
    reporter = PerfReporter(args.dir, args.md, args.html)
    reporter.parse_results()
    if not reporter.data:
        print("No result files found. Run the performance tests first.")
        sys.exit(1)
        
    reporter.generate_markdown()
    reporter.generate_html()

if __name__ == "__main__":
    main()
