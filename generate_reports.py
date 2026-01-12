import subprocess
import time
import os
import json
import re

# Database connection settings
DB_USER = "root"
DB_PASS = "root"
DB_NAME = "employees"
CONTAINER_NAME = "mariadb-test"
QUERY_FILE = "req_employees.sql"
REPORT_DIR = "explain_reports"

def run_command(cmd_list):
    """Runs a shell command and returns stdout and stderr."""
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result.stdout, result.stderr

def execute_query(query):
    """Executes a query and measures time."""
    cmd = ["docker", "exec", CONTAINER_NAME, "mariadb", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME, "-e", query]
    start = time.time()
    stdout, stderr = run_command(cmd)
    end = time.time()
    return end - start, stdout, stderr

def get_explain_plan(query):
    """Gets the EXPLAIN plan for a query."""
    # We use tabular format for readability in reports, and JSON for analysis if needed.
    explain_query = f"EXPLAIN {query}"
    cmd = ["docker", "exec", CONTAINER_NAME, "mariadb", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME, "-e", explain_query]
    stdout, stderr = run_command(cmd)
    return stdout, stderr

def analyze_explain(explain_output):
    """Analyzes EXPLAIN output for potential issues."""
    issues = []
    if not explain_output:
        return ["Could not get EXPLAIN plan."]
    
    # Simple keyword based analysis for tabular EXPLAIN
    if "ALL" in explain_output:
        issues.append("Full Table Scan (ALL) detected.")
    if "Using temporary" in explain_output:
        issues.append("Temporary table used.")
    if "Using filesort" in explain_output:
        issues.append("Filesort used (performance impact).")
    
    # Check for NULL in the 'key' column
    # Tabular output usually looks like: | id | select_type | table | type | possible_keys | key | ...
    # We look for '| NULL |' in the key column. This is a bit brittle with text parsing but works for common cases.
    lines = explain_output.split('\n')
    if len(lines) > 3:
        for line in lines[3:]: # Skip header
            if "|" in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 5:
                    key = parts[5] # Key is typically index 5
                    if key == "NULL" or not key:
                        issues.append(f"No index used for table {parts[3] if len(parts)>3 else 'unknown'}")

    return list(set(issues)) # Unique issues

def main():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    with open(QUERY_FILE, 'r') as f:
        content = f.read()
    
    # Split queries by semicolon, filtering out empty ones
    queries = [q.strip() for q in content.split(';') if q.strip()]
    
    summary_report = []
    summary_report.append("# Query Performance and Quality Report\n")
    summary_report.append("| ID | Execution Time (s) | Issues | Query Snippet |")
    summary_report.append("|---|---|---|---|")

    print(f"Starting analysis of {len(queries)} queries...")

    for i, query in enumerate(queries, 1):
        print(f"Processing query {i}/{len(queries)}...")
        
        # 1. Get EXPLAIN plan
        explain_plan, explain_err = get_explain_plan(query)
        issues = analyze_explain(explain_plan)
        
        # Save detailed EXPLAIN plan
        report_file = os.path.join(REPORT_DIR, f"query_{i:02d}.txt")
        with open(report_file, 'w') as rf:
            rf.write(f"QUERY:\n{query}\n\n")
            rf.write(f"EXPLAIN PLAN:\n{explain_plan}\n")
            if explain_err:
                rf.write(f"ERRORS:\n{explain_err}\n")
            if issues:
                rf.write(f"ANALYSIS ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues) + "\n")

        # 2. Measure execution time
        exec_time, _, exec_err = execute_query(query)
        
        issue_summary = ", ".join(issues) if issues else "None"
        query_snippet = query[:50] + "..." if len(query) > 50 else query
        summary_report.append(f"| {i} | {exec_time:.4f} | {issue_summary} | `{query_snippet}` |")

    # Write summary report
    with open("performance_report.md", "w") as f:
        f.write("\n".join(summary_report))
    
    print("\nAnalysis complete. Reports generated:")
    print(f"- Detailed plans in {REPORT_DIR}/")
    print("- Summary report in performance_report.md")

if __name__ == "__main__":
    main()
