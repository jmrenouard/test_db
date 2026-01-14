# SQL Analyzer Script

The `sql_analyzer.py` script is a powerful tool for analyzing SQL query performance and quality.

## Features

- **Automated EXPLAIN Analysis**: Automatically runs `EXPLAIN` on provided queries.
- **Performance Rating**: Assigns a 1-5 star rating based on query efficiency.
- **Optimization Suggestions**: Provides targeted advice for improving slow queries.
- **Index Recommendations**: Detects missing indexes and generates the corresponding `CREATE INDEX` DDL.
- **Schema Context**: Shows the involved tables' structure and existing indexes.
- **Stunning HTML Reports**: Generates a modern, Tailwind CSS-based analytics dashboard.

## Usage

### Analyzing a File

```bash
python3 scripts/sql_analyzer.py --container mariadb-11-8 --query-file employees/req_employees.sql
```

### Analyzing a Single Query

```bash
python3 scripts/sql_analyzer.py --container mariadb-11-8 --query "SELECT * FROM employees WHERE emp_no = 10001" --stdout
```

## Parameters

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `--container` | None | Name of the MariaDB Docker container. |
| `--query-file` | `employees/req_employees.sql` | Path to the SQL file containing queries. |
| `--query` | None | A single SQL query string to analyze. |
| `--db` | `employees` | The target database name. |
| `--stdout` | False | Print results directly to the terminal. |
| `--html-file` | `reports/performance_report.html` | Path for the generated HTML dashboard. |
| `[Other DB params]` | - | `--host`, `--port`, `--user`, `--password` for non-Docker connections. |
