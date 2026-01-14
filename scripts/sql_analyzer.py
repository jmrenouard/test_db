import subprocess
import time
import os
import argparse
import sys
import re
import json

def run_command(cmd_list):
    """Runs a shell command and returns stdout and stderr."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=False)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def get_db_command(args, query):
    """Constructs the database command based on Docker or direct connection."""
    if args.container:
        return ["docker", "exec", args.container, "mariadb", "-h", args.host, "-P", str(args.port), "-u", args.user, f"-p{args.password}", args.db, "-e", query]
    else:
        return ["mariadb", "-h", args.host, "-P", str(args.port), "-u", args.user, f"-p{args.password}", args.db, "-e", query]

def execute_query(query, args):
    """Executes a query and measures time."""
    cmd = get_db_command(args, query)
    start = time.time()
    stdout, stderr = run_command(cmd)
    end = time.time()
    return end - start, stdout, stderr

def get_explain_plan(query, args):
    """Gets the EXPLAIN plan for a query."""
    explain_query = f"EXPLAIN {query}"
    cmd = get_db_command(args, explain_query)
    stdout, stderr = run_command(cmd)
    return stdout, stderr

def get_tables_from_explain(explain_output):
    """Parses table names from EXPLAIN output."""
    tables = []
    if not explain_output:
        return []
    lines = explain_output.split('\n')
    header_found = False
    table_idx = -1
    
    for line in lines:
        if not line.strip():
            continue
        parts = []
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if line.strip().startswith('|'):
                parts = [p for p in parts if p]
        else:
            parts = [p.strip() for p in line.split('\t')]
        
        if not parts:
            continue
            
        if "table" in [p.lower() for p in parts]:
            try:
                table_idx = [p.lower() for p in parts].index("table")
                header_found = True
                continue
            except ValueError:
                pass
        
        if header_found and table_idx != -1 and len(parts) > table_idx:
            table_name = parts[table_idx]
            if table_name and table_name != "NULL" and not table_name.startswith('<'):
                tables.append(table_name)
    
    return list(set(tables))

def get_table_schema_info(tables, args):
    """Gets a combined view of columns and their associated indexes."""
    info = ""
    for table in tables:
        query = f"""
        SELECT 
            c.COLUMN_NAME AS 'Field', 
            c.COLUMN_TYPE AS 'Type', 
            c.COLUMN_KEY AS 'Key',
            COALESCE(GROUP_CONCAT(DISTINCT s.INDEX_NAME SEPARATOR ', '), 'None') AS 'Indexes'
        FROM information_schema.COLUMNS c
        LEFT JOIN information_schema.STATISTICS s 
            ON c.TABLE_SCHEMA = s.TABLE_SCHEMA 
            AND c.TABLE_NAME = s.TABLE_NAME 
            AND c.COLUMN_NAME = s.COLUMN_NAME
        WHERE c.TABLE_SCHEMA = '{args.db}' 
            AND c.TABLE_NAME = '{table}'
        GROUP BY c.COLUMN_NAME, c.COLUMN_TYPE, c.COLUMN_KEY, c.ORDINAL_POSITION
        ORDER BY c.ORDINAL_POSITION;
        """
        cmd = get_db_command(args, query)
        info += f"\n--- TABLE: {table} ---\n"
        output, _ = run_command(cmd)
        info += f"{output}\n"
    return info

def extract_where_columns(query):
    """Roughly extracts columns from WHERE clause for index suggestions."""
    # This is a basic regex approach; won't handle all SQL edge cases but good for suggestions
    match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|;|$)', query, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    where_clause = match.group(1)
    # Find word-like identifiers followed by =, <, >, IN, etc.
    cols = re.findall(r'(\w+)\s*(?:=|!=|<>|<|>|<=|>=|IN|LIKE|BETWEEN)', where_clause, re.IGNORECASE)
    return list(set(cols))

def analyze_performance(query, explain_output, exec_time, args):
    """Analyzes EXPLAIN output and time to provide rating and suggestions."""
    issues = []
    suggestions = []
    index_sql = []
    score = 5

    if not explain_output:
        return 1, ["Could not analyze."], ["Ensure the query is valid and the database is accessible."], []

    tables = get_tables_from_explain(explain_output)

    if "ALL" in explain_output:
        issues.append("Full Table Scan (ALL) detected.")
        score -= 2
        potential_cols = extract_where_columns(query)
        if potential_cols and tables:
            suggestions.append(f"Consider indexing: {', '.join(potential_cols)}")
            for table in tables:
                for col in potential_cols:
                    idx_name = f"idx_{table}_{col}"
                    index_sql.append(f"CREATE INDEX {idx_name} ON {table}({col});")
    
    if "Using temporary" in explain_output:
        issues.append("Temporary table used.")
        score -= 1
        suggestions.append("Optimize GROUP BY or DISTINCT to avoid temporary tables.")
        
    if "Using filesort" in explain_output:
        issues.append("Filesort used (performance impact).")
        score -= 1
        suggestions.append("Add an index on columns used in ORDER BY.")

    if exec_time > 1.0:
        score -= 1
        suggestions.append("Query is slow, consider partitioning or pre-aggregating data.")
    elif exec_time > 5.0:
        score -= 2
        
    score = max(1, min(5, score))
    if not suggestions:
        suggestions.append("Query seems well-optimized.")
    
    return score, issues, suggestions[:3], index_sql

def generate_html_report(summary_data, footer_info, args):
    """Generates a standalone HTML report with Tailwind CSS."""
    rows_html = ""
    for item in summary_data:
        rating_html = "⭐" * item['rating']
        issues_list = "".join([f"<li class='text-red-600'>{i}</li>" for i in item['issues']]) if item['issues'] else "None"
        sugg_list = "".join([f"<li>{s}</li>" for s in item['suggestions']])
        idx_list = "".join([f"<code>{sql}</code><br>" for sql in item['index_sql']])
        
        rows_html += f"""
        <tr class="border-b hover:bg-gray-50">
            <td class="p-3 text-center font-mono">{item['id']}</td>
            <td class="p-3 font-mono text-sm">{item['time']:.4f}s</td>
            <td class="p-3">{rating_html}</td>
            <td class="p-3 text-sm"><ul>{issues_list}</ul></td>
            <td class="p-3 text-sm">
                <ul class="list-disc ml-4">{sugg_list}</ul>
                {f'<div class="mt-2 p-2 bg-blue-50 text-xs border border-blue-100 rounded">{idx_list}</div>' if item['index_sql'] else ''}
            </td>
            <td class="p-3 font-mono text-xs truncate max-w-xs" title="{item['query']}"><code>{item['query'][:100]}...</code></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL Performance Report</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-7xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="bg-indigo-600 p-6 text-white">
                <h1 class="text-3xl font-bold">SQL Analytics Dashboard</h1>
                <p class="mt-2 opacity-80">Report for Database: <span class="font-mono text-yellow-300">{args.db}</span></p>
                <p class="text-sm opacity-60">Generated at: {footer_info}</p>
            </div>
            
            <div class="p-6">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-200 text-gray-700 uppercase text-xs">
                            <th class="p-3">ID</th>
                            <th class="p-3">Exec Time</th>
                            <th class="p-3">Rating</th>
                            <th class="p-3">Issues</th>
                            <th class="p-3">Suggestions / DDL</th>
                            <th class="p-3">Query Snippet</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    parser = argparse.ArgumentParser(description="Generate SQL performance and EXPLAIN reports.")
    # Targets
    parser.add_argument("--query-file", default="employees/req_employees.sql", help="Path to SQL file")
    parser.add_argument("--query", help="Execute a single query string instead of a file")
    
    # Connection
    parser.add_argument("--container", help="Name of the MariaDB container (if using Docker)")
    parser.add_argument("--host", default="127.0.0.1", help="Database host")
    parser.add_argument("--port", type=int, default=3306, help="Database port")
    parser.add_argument("--user", default="root", help="Database user")
    parser.add_argument("--password", default="root", help="Database password")
    parser.add_argument("--db", default="employees", help="Database name")
    
    # Output
    parser.add_argument("--report-dir", default="reports/explain_reports", help="Directory for detailed reports")
    parser.add_argument("--report-file", default="reports/performance_report.md", help="Path to summary markdown")
    parser.add_argument("--html-file", default="reports/performance_report.html", help="Path to HTML report")
    parser.add_argument("--stdout", action="store_true", help="Print report to stdout (recommended for single query)")

    args = parser.parse_args()

    if args.query:
        queries = [args.query]
    else:
        if not os.path.exists(args.query_file):
            print(f"Error: Query file not found at {args.query_file}")
            sys.exit(1)
        with open(args.query_file, 'r') as f:
            content = f.read()
        queries = [q.strip() for q in content.split(';') if q.strip()]

    if not os.path.exists(args.report_dir):
        os.makedirs(args.report_dir, exist_ok=True)

    summary_data = []
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    for i, query in enumerate(queries, 1):
        exec_time, _, _ = execute_query(query, args)
        explain_plan, explain_err = get_explain_plan(query, args)
        rating, issues, suggestions, index_sql = analyze_performance(query, explain_plan, exec_time, args)
        tables = get_tables_from_explain(explain_plan)
        schema_info = get_table_schema_info(tables, args)
        
        item = {
            "id": i,
            "query": query,
            "time": exec_time,
            "rating": rating,
            "issues": issues,
            "suggestions": suggestions,
            "index_sql": index_sql,
            "schema_info": schema_info,
            "explain": explain_plan
        }
        summary_data.append(item)

        # File report
        report_file = os.path.join(args.report_dir, f"query_{i:02}d.txt")
        with open(report_file, 'w') as rf:
            rf.write(f"QUERY: {query}\n\nRATING: {'⭐' * rating}\n\nEXPLAIN:\n{explain_plan}\n\nSCHEMA:\n{schema_info}\n")
            if issues: rf.write(f"ISSUES: {', '.join(issues)}\n")
            if index_sql: rf.write(f"INDEX SUGGESTIONS:\n" + "\n".join(index_sql) + "\n")

        if args.stdout:
            print(f"--- QUERY {i} analysis ---")
            print(f"Time: {exec_time:.4f}s | Rating: {'*' * rating}")
            print(f"Issues: {', '.join(issues) if issues else 'None'}")
            print(f"Suggestions: {', '.join(suggestions)}")
            if index_sql: print("Suggested SQL:\n" + "\n".join(index_sql))

    # Save Markdown Summary
    md_report = [f"# SQL Performance Report - {args.db}\n", f"Generated: {timestamp}\n", "| ID | Time (s) | Rating | Issues | Suggestions |", "|---|---|---|---|---|"]
    for d in summary_data:
        md_report.append(f"| {d['id']} | {d['time']:.4f} | {'⭐'*d['rating']} | {', '.join(d['issues']) or 'None'} | {', '.join(d['suggestions'])} |")
    
    with open(args.report_file, "w") as f:
        f.write("\n".join(md_report))

    # Save HTML
    html_content = generate_html_report(summary_data, timestamp, args)
    with open(args.html_file, "w") as f:
        f.write(html_content)

    if not args.stdout:
        print(f"✅ Analysis complete. HTML report: {args.html_file}")

if __name__ == "__main__":
    main()
