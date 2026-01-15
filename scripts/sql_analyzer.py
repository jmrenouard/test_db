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
    """Generates a standalone HTML report with Tailwind CSS, sorting, and filtering."""
    rows_html = ""
    for item in summary_data:
        rating_val = item['rating']
        rating_html = "⭐" * rating_val
        issues_list = "".join([f"<li class='text-red-600 mb-1 flex items-center'><span class='mr-2'>⚠️</span>{i}</li>" for i in item['issues']]) if item['issues'] else "<li class='text-green-600 flex items-center'><span class='mr-2'>✅</span>None</li>"
        sugg_list = "".join([f"<li class='mb-1 flex items-start'><span class='mr-2 font-bold text-indigo-500'>•</span>{s}</li>" for s in item['suggestions']])
        idx_list = "".join([f"<div class='flex items-center gap-2 mb-1'><code class='bg-black/5 p-1 rounded text-[10px] flex-1'>{sql}</code></div>" for sql in item['index_sql']])
        
        rows_html += f"""
        <tr class="border-b border-gray-100 hover:bg-indigo-50/30 transition-colors duration-150 group" data-rating="{rating_val}">
            <td class="p-4 text-center font-mono text-gray-500 text-sm">{item['id']}</td>
            <td class="p-4 font-mono text-sm font-semibold text-indigo-700" data-value="{item['time']}">{item['time']:.4f}s</td>
            <td class="p-4 text-amber-500" data-value="{rating_val}">{rating_html}</td>
            <td class="p-4 text-sm"><ul class="list-none p-0">{issues_list}</ul></td>
            <td class="p-4 text-sm">
                <ul class="list-none p-0 mb-3">{sugg_list}</ul>
                {f'<div class="mt-2 p-3 bg-indigo-50 rounded-lg border border-indigo-100 shadow-sm"><p class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-2">Suggested Indexes</p>{idx_list}</div>' if item['index_sql'] else ''}
            </td>
            <td class="p-4">
                <div class="relative group/code">
                    <code class="block font-mono text-[11px] text-gray-600 bg-gray-50 p-2 rounded border border-gray-200 truncate max-w-sm cursor-help transition-all group-hover/code:max-w-none group-hover/code:absolute group-hover/code:z-20 group-hover/code:shadow-xl group-hover/code:whitespace-normal group-hover/code:bg-white" title="{item['query']}">{item['query']}</code>
                </div>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL Analytics - {args.db}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; }}
            .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
            th.sortable {{ cursor: pointer; position: relative; transition: background 0.2s; }}
            th.sortable:hover {{ background-color: #f3f4f6; }}
            th.sortable::after {{ content: '↕'; position: absolute; right: 8px; opacity: 0.3; }}
            th.sort-asc::after {{ content: '↑'; opacity: 1; color: #4f46e5; }}
            th.sort-desc::after {{ content: '↓'; opacity: 1; color: #4f46e5; }}
            .glass {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }}
        </style>
    </head>
    <body class="bg-[#f8fafc] text-slate-900 min-h-screen pb-20">
        <div class="max-w-7xl mx-auto pt-10 px-6">
            <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
                            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        </div>
                        <h1 class="text-4xl font-extrabold tracking-tight text-slate-900 whitespace-nowrap">SQL Analytics Dashboard</h1>
                    </div>
                    <p class="text-slate-500 font-medium">Database: <span class="text-indigo-600 font-bold px-2 py-0.5 bg-indigo-50 rounded-md border border-indigo-100">{args.db}</span></p>
                </div>
                
                <div class="flex flex-col gap-2 w-full md:w-96">
                    <label class="text-[11px] font-bold text-slate-400 uppercase tracking-widest ml-1">Live Filter</label>
                    <div class="relative">
                        <input type="text" id="tableSearch" placeholder="Filter queries, issues or DDL..." 
                            class="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-2xl shadow-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none">
                        <div class="absolute left-4 top-3.5 text-slate-400">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        </div>
                    </div>
                </div>
            </header>

            <div class="bg-white rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse" id="perfTable">
                        <thead>
                            <tr class="bg-slate-50 border-b border-slate-100 text-slate-600 uppercase text-[11px] font-bold tracking-wider">
                                <th class="p-5 text-center sortable" data-sort="int">ID</th>
                                <th class="p-5 sortable" data-sort="float">Exec Time</th>
                                <th class="p-5 sortable" data-sort="int">Rating</th>
                                <th class="p-5">Analysis Issues</th>
                                <th class="p-5">Optimization Advice</th>
                                <th class="p-5">SQL Query</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-50">
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                
                <div id="noResults" class="hidden p-20 text-center">
                    <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 9.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <p class="text-slate-400 font-medium text-lg">No matching queries found</p>
                </div>
            </div>

            <footer class="mt-8 flex items-center justify-between text-slate-400 text-xs px-2">
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                    <span>Generated on {footer_info}</span>
                </div>
                <div class="flex items-center gap-4">
                    <span>Performance Matrix v2.0</span>
                    <a href="#" class="hover:text-indigo-600 transition-colors uppercase font-bold tracking-widest text-[10px]">Documentation</a>
                </div>
            </footer>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', () => {{
                const searchInput = document.getElementById('tableSearch');
                const table = document.getElementById('perfTable');
                const rows = table.querySelectorAll('tbody tr');
                const noResults = document.getElementById('noResults');

                // Filtering Logic
                searchInput.addEventListener('input', (e) => {{
                    const term = e.target.value.toLowerCase();
                    let visibleCount = 0;

                    rows.forEach(row => {{
                        const text = row.innerText.toLowerCase();
                        if (text.includes(term)) {{
                            row.style.display = '';
                            visibleCount++;
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }});

                    noResults.classList.toggle('hidden', visibleCount > 0);
                    table.classList.toggle('hidden', visibleCount === 0);
                }});

                // Sorting Logic
                const getCellValue = (tr, idx) => {{
                    const cell = tr.children[idx];
                    return cell.getAttribute('data-value') || cell.innerText || cell.textContent;
                }};

                const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
                    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
                )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

                document.querySelectorAll('th.sortable').forEach(th => th.addEventListener('click', (() => {{
                    const table = th.closest('table');
                    const tbody = table.querySelector('tbody');
                    const headerRow = th.parentElement;
                    
                    // Update classes
                    const isAsc = th.classList.contains('sort-asc');
                    headerRow.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                    th.classList.add(isAsc ? 'sort-desc' : 'sort-asc');

                    Array.from(tbody.querySelectorAll('tr'))
                        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), !isAsc))
                        .forEach(tr => tbody.appendChild(tr));
                }})));
            }});
        </script>
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
