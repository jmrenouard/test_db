# Scripts for test_db

This directory contains utility scripts for testing and reporting on the `employees` database and the MariaDB environment.

## Available Scripts

### 1. `generate_reports.py`

- **Language**: Python
- **Purpose**: Processes performance data and generates execution reports (HTML/Markdown).
- **Usage**: `python3 generate_reports.py`

### 2. `employees_sysbench.lua`

- **Language**: Lua
- **Purpose**: A Custom Sysbench script tailored for the `employees` database schema to perform load testing.
- **Usage**: `sysbench --script=employees_sysbench.lua ... run`

### 3. `test_mariadb.sh`

- **Language**: Bash
- **Purpose**: Automates basic connectivity and health checks for the MariaDB container.
- **Usage**: `./test_mariadb.sh`

### 4. `test_employees.sh`

- **Language**: Bash
- **Purpose**: Runs a suite of SQL tests against the `employees` database to verify data integrity and performance.
- **Usage**: `./test_employees.sh`

---
*Note: Ensure the MariaDB container is running (use `make start` in the parent directory) before executing these scripts.*
