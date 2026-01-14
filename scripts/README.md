# 📜 Scripts for test_db

This directory contains utility scripts for testing, verifying, and reporting on the `employees` database and the MariaDB environment.

## 🚦 Primary Entry Point: `test_runner.sh`

This script provides a unified interface for all testing activities. It centralizes configuration and simplifies execution.

**Usage:**

```bash
./scripts/test_runner.sh [command]
```

**Commands:**

- `verify`: Checks data integrity by comparing table counts and checksums against expected values.
- `analyze`: Runs a series of SQL queries, measures performance, and generates EXPLAIN reports.
- `bench`: Runs sysbench performance tests using custom Lua scripts.
- `all`: Runs verify, analyze, and bench in sequence.

## 🛠 Utility Scripts

### 1. `generate_reports.py`

- **Language**: Python 3
- **Purpose**: Executes SQL queries, analyzes EXPLAIN plans for potential performance issues (like full table scans), and generates reports.
- **Output**: Saves detailed reports to `reports/explain_reports/` and a summary to `reports/performance_report.md`.

### 2. `verify_data.sh`

- **Language**: Bash
- **Purpose**: Compares current database state against known good checksums/counts.
- **Output**: Color-coded table showing status of each table.

### 3. `employees_sysbench.lua`

- **Language**: Lua
- **Purpose**: Custom Sysbench script tailored for the `employees` database schema.

---

## 🚀 Recommended Workflow

Use the root `Makefile` for the most convenient access:

- `make verify`: Verify data integrity.
- `make analyze`: Run performance and EXPLAIN analysis.
- `make bench`: Run sysbench tests.
- `make test-all`: Run the complete test suite.
- `make clean`: Clean up generated reports.
