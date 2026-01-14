import subprocess
import os
import json
import sys
from datetime import datetime

# Configuration
STEPS = [
    {
        "id": "start",
        "name": "Start Container",
        "description": "Starts the MariaDB container if it's not already running.",
        "command": "make start"
    },
    {
        "id": "status",
        "name": "Check Status",
        "description": "Shows the current status of the MariaDB container.",
        "command": "make status"
    },
    {
        "id": "inject",
        "name": "Inject Data",
        "description": "Injects the employees dataset into the database.",
        "command": "make inject"
    },
    {
        "id": "verify",
        "name": "Verify Integrity",
        "description": "Runs data integrity checks (counts and checksums).",
        "command": "make verify"
    },
    {
        "id": "analyze",
        "name": "Analyze Performance",
        "description": "Generates EXPLAIN reports and performance analysis.",
        "command": "make analyze"
    },
    {
        "id": "bench",
        "name": "Run Sysbench",
        "description": "Executes sysbench performance tests.",
        "command": "make bench"
    }
]

REPORT_FILE = "reports/run_report.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Runner Report - {timestamp}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --bg: #0b0e14;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at 0% 0%, #1e293b 0%, #0f172a 50%, #020617 100%);
            color: #f1f5f9;
            min-height: 100vh;
        }}
        .glass {{
            background: var(--glass);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        .status-success {{ color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }}
        .status-failure {{ color: #f43f5e; text-shadow: 0 0 10px rgba(244, 63, 94, 0.3); }}
        .status-skipped {{ color: #94a3b8; }}
        .code-block {{
            font-family: 'Fira Code', monospace;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.03);
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .step-card {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .step-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.05);
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.2); }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.2); }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-6xl mx-auto">
        <header class="mb-16 relative">
            <div class="absolute -top-24 -left-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl"></div>
            <div class="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl"></div>
            
            <div class="relative text-center">
                <h1 class="text-6xl font-black tracking-tight mb-6 gradient-text">
                    Interactive Test execution
                </h1>
                <p class="text-slate-400 text-xl font-light">
                    Real-time execution dashboard for <span class="text-slate-200 font-medium">test_db</span> suite
                </p>
                <div class="flex flex-wrap justify-center gap-6 mt-10">
                    <div class="glass px-8 py-4 flex flex-col items-center min-w-[140px]">
                        <span class="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold mb-1">Execution Date</span>
                        <span class="text-lg font-semibold text-slate-200">{timestamp}</span>
                    </div>
                    <div class="glass px-8 py-4 flex flex-col items-center min-w-[120px]">
                        <span class="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold mb-1">Steps</span>
                        <span class="text-3xl font-black text-white">{total_steps}</span>
                    </div>
                    <div class="glass px-8 py-4 border-emerald-500/20 flex flex-col items-center min-w-[120px]">
                        <span class="text-[10px] uppercase tracking-[0.2em] text-emerald-500/60 font-bold mb-1">Passed</span>
                        <span class="text-3xl font-black text-emerald-400">{passed_steps}</span>
                    </div>
                    <div class="glass px-8 py-4 border-rose-500/20 flex flex-col items-center min-w-[120px]">
                        <span class="text-[10px] uppercase tracking-[0.2em] text-rose-500/60 font-bold mb-1">Failed</span>
                        <span class="text-3xl font-black text-rose-400">{failed_steps}</span>
                    </div>
                </div>
            </div>
        </header>

        <main class="space-y-10 relative">
            <div class="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-blue-500/20 via-slate-500/10 to-transparent hidden lg:block"></div>
            {steps_content}
        </main>

        <footer class="mt-20 text-center text-slate-500 text-sm font-medium tracking-wide">
            Generated by Antigravity Runner &bull; {timestamp}
        </footer>
    </div>
</body>
</html>
"""

STEP_TEMPLATE = """
<section id="step-{id}" class="step-card glass p-6 md:p-8 relative overflow-hidden">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 relative z-10">
        <div>
            <div class="flex items-center gap-4 mb-2">
                <span class="text-[10px] font-black uppercase tracking-[0.2em] px-3 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700">Step {index}</span>
                <h2 class="text-3xl font-bold text-white tracking-tight">{name}</h2>
            </div>
            <p class="text-slate-400 text-lg font-light leading-relaxed max-w-2xl">{description}</p>
        </div>
        <div class="flex items-center gap-6 glass px-6 py-4 bg-white/[0.02]">
            <div class="text-right">
                <p class="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold mb-1">Current Status</p>
                <p class="text-xl font-black tracking-tight {status_class}">{status}</p>
            </div>
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center {status_bg} relative overflow-hidden">
                <div class="absolute inset-0 bg-current opacity-10 animate-pulse"></div>
                {status_icon}
            </div>
        </div>
    </div>

    <div class="space-y-6 relative z-10">
        <div>
            <div class="flex items-center gap-2 mb-3">
                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-500">Command Executed</h3>
            </div>
            <div class="code-block p-5 rounded-xl border border-white/5 text-blue-300 group transition-all duration-300 hover:border-blue-500/30">
                <code class="text-sm font-medium leading-relaxed">{command}</code>
            </div>
        </div>

        {output_section}
    </div>
</section>
"""

OUTPUT_TEMPLATE = """
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4">
            <div class="space-y-3">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-500">Standard Output</h3>
                </div>
                <div class="code-block p-5 rounded-xl border border-white/5 h-[32rem] overflow-y-auto text-emerald-300 text-sm scrollbar-thin">
                    <pre class="leading-relaxed">{stdout}</pre>
                </div>
            </div>
            <div class="space-y-3">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-rose-500"></div>
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-500">Error / Stderr</h3>
                </div>
                <div class="code-block p-5 rounded-xl border border-white/5 h-[32rem] overflow-y-auto text-rose-300 text-sm scrollbar-thin">
                    <pre class="leading-relaxed">{stderr}</pre>
                </div>
            </div>
        </div>
"""

def run_command(command):
    print(f"\n📦 Executing: {command}")
    print("-" * 40)
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    stdout_lines = []
    stderr_lines = []

    # Using a simple way to read both streams or at least show progress
    # For simplicity in a script like this, we'll read stdout then stderr 
    # or use a more advanced selector if needed. 
    # Let's try to read line by line from stdout first as it's the primary output.
    
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(line, end="")
            stdout_lines.append(line)
            
    # Capture remaining stderr
    stderr_content = process.stderr.read()
    if stderr_content:
        print(f"\n❌ STDERR:\n{stderr_content}")
        stderr_lines.append(stderr_content)

    print("-" * 40)
    return process.returncode, "".join(stdout_lines), "".join(stderr_lines)

def generate_report(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    steps_content = ""
    passed = 0
    failed = 0
    
    for i, res in enumerate(results):
        status_class = "status-success" if res['status'] == "SUCCESS" else "status-failure" if res['status'] == "FAILED" else "text-blue-400" if res['status'] == "RUNNING" else "text-amber-400" if res['status'] == "PENDING" else "status-skipped"
        status_bg = "bg-emerald-500/20" if res['status'] == "SUCCESS" else "bg-rose-500/20" if res['status'] == "FAILED" else "bg-blue-500/20" if res['status'] == "RUNNING" else "bg-amber-500/20" if res['status'] == "PENDING" else "bg-slate-500/20"
        
        status_icon = ""
        if res['status'] == "SUCCESS":
            passed += 1
            status_icon = '<svg class="w-7 h-7 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>'
        elif res['status'] == "FAILED":
            failed += 1
            status_icon = '<svg class="w-7 h-7 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>'
        elif res['status'] == "RUNNING":
            status_icon = '<svg class="w-7 h-7 text-blue-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>'
        elif res['status'] == "PENDING":
            status_icon = '<svg class="w-7 h-7 text-amber-500 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
        else:
            status_icon = '<svg class="w-7 h-7 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>'

        output_section = ""
        if res['status'] not in ["SKIPPED", "PENDING", "RUNNING"]:
            output_section = OUTPUT_TEMPLATE.format(
                stdout=res['stdout'] if res['stdout'] else "(no output)",
                stderr=res['stderr'] if res['stderr'] else "(no error output)"
            )

        steps_content += STEP_TEMPLATE.format(
            index=i+1,
            id=res['id'],
            name=res['name'],
            description=res['description'],
            command=res['command'],
            status=res['status'],
            status_class=status_class,
            status_bg=status_bg,
            status_icon=status_icon,
            output_section=output_section
        )

    html = HTML_TEMPLATE.format(
        timestamp=timestamp,
        total_steps=len(results),
        passed_steps=passed,
        failed_steps=failed,
        steps_content=steps_content
    )

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write(html)
    
    print(f"\n✨ Report updated: {REPORT_FILE}")

def main():
    print("\n🚀 Interactive Test Runner")
    print("==========================")
    
    mode_input = input("Run mode ([a]uto / [i]nteractive - default: i)? ").lower().strip()
    mode = 'a' if mode_input == 'a' else 'i'
    
    results = []
    
    # Initial report generation with all steps as PENDING
    initial_results = [
        {**step, "status": "PENDING", "stdout": "", "stderr": ""}
        for step in STEPS
    ]
    generate_report(initial_results)

    for i, step in enumerate(STEPS):
        print(f"\n[{i+1}/{len(STEPS)}] Step: {step['name']}")
        print(f"Description: {step['description']}")
        
        should_run = True
        if mode == 'i':
            confirm = input(f"   Run this step? (Y/n) ").lower().strip()
            if confirm == 'n':
                should_run = False
        
        if should_run:
            returncode, stdout, stderr = run_command(step['command'])
            status = "SUCCESS" if returncode == 0 else "FAILED"
            results.append({
                **step,
                "status": status,
                "stdout": stdout,
                "stderr": stderr
            })
            # Update report after finishing
            current_report = results + [
                {**s, "status": "PENDING", "stdout": "", "stderr": ""}
                for s in STEPS[len(results):]
            ]
            generate_report(current_report)

            if status == "FAILED":
                print(f"❌ Step failed with return code {returncode}")
                if mode == 'i':
                    cont = input("   Continue to next step? (y/N) ").lower().strip()
                    if cont != 'y':
                        break
        else:
            results.append({
                **step,
                "status": "SKIPPED",
                "stdout": "",
                "stderr": ""
            })
            current_report = results + [
                {**s, "status": "PENDING", "stdout": "", "stderr": ""}
                for s in STEPS[len(results):]
            ]
            generate_report(current_report)
    
    print(f"\n✅ All steps completed. Final report: {REPORT_FILE}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Runner interrupted by user.")
        sys.exit(0)
