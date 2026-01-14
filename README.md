# 📊 test_db (Employees Database)

A sample database with an integrated test suite, used to test your applications and database servers. This repository provides a large dataset (300,000 employees, 2.8M salaries) for performance testing and complex query practice.

---

## 🚀 Quick Start (Modern Workflow)

This project is optimized for a **MariaDB 11.8+** Docker environment. A `Makefile` is provided to streamline common operations.

### Prerequisites

- Docker & Docker Compose
- Make
- Python 3 (for reporting)

### Commands

| Command | Description |
| :--- | :--- |
| `make start` | Start the MariaDB container (`mariadb-11-8`). |
| `make stop` | Stop the MariaDB container. |
| `make status` | Check the container status. |
| `make inject` | Inject the `employees.sql` dataset. |
| `make verify` | Run data integrity checks (counts/checksums). |
| `make bench` | Run Sysbench performance tests. |
| `make analyze` | Generate SQL EXPLAIN and performance reports. |
| `make test-all` | Run all tests (Verify + Analyze + Bench). |
| `make interactive` | Launch the Antigravity HTML test runner. |
| `make clean` | Clean up generated reports. |

### 🤖 Agentic Workflows

This project includes specialized agent workflows in `.agent/workflows/` for easier management:

- `/run-tests`: Runs full test suite and syncs documentation.
- `/git-sync`: Manages `pull`, `commit` (conventional), and optional `release`.
- `/release`: Automates versioning, changelog updates, and tagging.
- `/maintain`: Performs environment health checks and cleanup.
- `/audit`: Structural audit of the codebase and parameters.
- `/ideate`: Suggests project improvements and new features.

---

## 📂 Project Structure

- `employees/`: Core dataset and SQL scripts.
- `sakila/`: Sakila sample database (Alternative).
- `scripts/`: Utility scripts for automation and reporting.
- `reports/`: Generated performance analysis and EXPLAIN plans.
- `doc_employees/`: Extended documentation with 60+ sample queries and ER diagrams.

---

## 🛠 Manual Installation

If you're not using Docker, you can install it manually on any MySQL-compatible server:

1. **Prerequisites**: Ensure your user has the necessary privileges (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `RELOAD`, `REFERENCES`, `INDEX`, `ALTER`, `SHOW DATABASES`, `CREATE TEMPORARY TABLES`, `LOCK TABLES`, `EXECUTE`, `CREATE VIEW`).
2. **Import**:

   ```bash
   mysql < employees.sql
   ```

   *For partitioned tables:*

   ```bash
   mysql < employees_partitioned.sql
   ```

3. **Verify**:

   ```bash
   mysql -t < test_employees_md5.sql
   ```

---

## 📊 Reporting & Analysis

The project includes a sophisticated reporting system:

- **Performance Reports**: Located in `reports/`, generated via `make report`.
- **EXPLAIN Plans**: Detailed query execution plans are stored in `reports/explain_reports/`.

---

## 📜 Credits & License

### Origin

- Data created by Fusheng Wang and Carlo Zaniolo at Siemens Corporate Research.
- Relational schema by Giuseppe Maxia.
- Data export by Patrick Crews.

### License

This work is licensed under the **Creative Commons Attribution-Share Alike 3.0 Unported License**. To view a copy of this license, visit [Creative Commons](http://creativecommons.org/licenses/by-sa/3.0/).

---
*Note: This data is fabricated and does not correspond to real people. Any similarity is purely coincidental.*
