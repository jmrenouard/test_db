import subprocess
import time
import os
import argparse
import sys

def run_command(cmd_list):
    """Runs a shell command and returns stdout and stderr."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=False)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def execute_query(query, container, user, password, db):
    """Executes a query and measures time."""
    cmd = ["docker", "exec", container, "mariadb", "-u", user, f"-p{password}", db, "-e", query]
    start = time.time()
    stdout, stderr = run_command(cmd)
    end = time.time()
    return end - start, stdout, stderr

def get_explain_plan(query, container, user, password, db):
    """Gets the EXPLAIN plan for a query."""
    explain_query = f"EXPLAIN {query}"
    cmd = ["docker", "exec", container, "mariadb", "-u", user, f"-p{password}", db, "-e", explain_query]
    stdout, stderr = run_command(cmd)
    return stdout, stderr

def analyze_explain(explain_output):
    """Analyzes EXPLAIN output for potential issues."""
    issues = []
    if not explain_output:
        return ["Could not get EXPLAIN plan."]
    
    # Simple keyword based analysis
    if "ALL" in explain_output:
        issues.append("Full Table Scan (ALL) detected.")
    if "Using temporary" in explain_output:
        issues.append("Temporary table used.")
    if "Using filesort" in explain_output:
        issues.append("Filesort used (performance impact).")
    
    lines = explain_output.split('\n')
    if len(lines) > 3:
        for line in lines[3:]: # Skip header
            if "|" in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 5:
                    key = parts[5] 
                    if key == "NULL" or not key:
                        issues.append(f"No index used for table {parts[3] if len(parts)>3 else 'unknown'}")

    return list(set(issues))

def main():
    parser = argparse.ArgumentParser(description="Generate SQL performance and EXPLAIN reports.")
    parser.add_argument("--container", default="mariadb-11-8", help="Name of the MariaDB container")
    parser.add_argument("--user", default="root", help="Database user")
    parser.add_argument("--password", default="root", help="Database password")
    parser.add_argument("--db", default="employees", help="Database name")
    parser.add_argument("--query-file", default="employees/req_employees.sql", help="Path to SQL file with queries")
    parser.add_argument("--report-dir", default="reports/explain_reports", help="Directory to save reports")
    parser.add_argument("--summary", default="reports/performance_report.md", help="Path to summary markdown file")

    args = parser.parse_args()

    if not os.path.exists(args.query_file):
        print(f"Error: Query file not found at {args.query_file}")
        sys.exit(1)

    if not os.path.exists(args.report_dir):
        os.makedirs(args.report_dir)

    # Ensure the parent directory for summary exists
    summary_dir = os.path.dirname(args.summary)
    if summary_dir and not os.path.exists(summary_dir):
        os.makedirs(summary_dir)

    with open(args.query_file, 'r') as f:
        content = f.read()
    
    queries = [q.strip() for q in content.split(';') if q.strip()]
    
    summary_report = []
    summary_report.append(f"# Query Performance and Quality Report - Database: {args.db}\n")
    summary_report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    summary_report.append("| ID | Execution Time (s) | Issues | Query Snippet |")
    summary_report.append("|---|---|---|---|")

    print(f"🚀 Starting analysis of {len(queries)} queries from {args.query_file}...")

    for i, query in enumerate(queries, 1):
        # 1. Get EXPLAIN plan
        explain_plan, explain_err = get_explain_plan(query, args.container, args.user, args.password, args.db)
        issues = analyze_explain(explain_plan)
        
        # Save detailed EXPLAIN plan
        report_file = os.path.join(args.report_dir, f"query_{i:02d}.txt")
        with open(report_file, 'w') as rf:
            rf.write(f"QUERY:\n{query}\n\n")
            rf.write(f"EXPLAIN PLAN:\n{explain_plan}\n")
            if explain_err:
                rf.write(f"ERRORS:\n{explain_err}\n")
            if issues:
                rf.write(f"ANALYSIS ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues) + "\n")

        # 2. Measure execution time
        exec_time, _, exec_err = execute_query(query, args.container, args.user, args.password, args.db)
        
        issue_summary = ", ".join(issues) if issues else "None"
        query_snippet = query[:50].replace('\n', ' ') + "..." if len(query) > 50 else query.replace('\n', ' ')
        summary_report.append(f"| {i} | {exec_time:.4f} | {issue_summary} | `{query_snippet}` |")
        
        print(f"  [{i}/{len(queries)}] Time: {exec_time:.4f}s | Issues: {len(issues)}")

    # Write summary report
    with open(args.summary, "w") as f:
        f.write("\n".join(summary_report))
    
    print("\n✅ Analysis complete. Reports generated:")
    print(f"  📂 Detailed plans: {args.report_dir}/")
    print(f"  📄 Summary report: {args.summary}")

if __name__ == "__main__":
    main()
