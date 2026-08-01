# 📊 test_db (Employees Database)

A sample database with an integrated test suite, used to test your applications and database servers. This repository provides a large dataset (300,000 employees, 2.8M salaries) for performance testing and complex query practice.

[![CI MySQL](https://github.com/datacharmer/test_db/actions/workflows/ci-mysql.yml/badge.svg)](https://github.com/datacharmer/test_db/actions/workflows/ci-mysql.yml)
[![CI Percona](https://github.com/datacharmer/test_db/actions/workflows/ci-percona.yml/badge.svg)](https://github.com/datacharmer/test_db/actions/workflows/ci-percona.yml)
[![CI MariaDB](https://github.com/datacharmer/test_db/actions/workflows/ci-mariadb.yml/badge.svg)](https://github.com/datacharmer/test_db/actions/workflows/ci-mariadb.yml)
[![CI PostgreSQL](https://github.com/datacharmer/test_db/actions/workflows/ci-postgresql.yml/badge.svg)](https://github.com/datacharmer/test_db/actions/workflows/ci-postgresql.yml)

---

## Tested Versions

The database requires MySQL 5.0+ or PostgreSQL 12+. The following versions are tested in CI using [ProxySQL/dbdeployer](https://github.com/ProxySQL/dbdeployer) on a weekly schedule:

| Vendor | Versions |
|--------|----------|
| MySQL | 5.6, 5.7, 8.0, 8.4, 9.0, 9.2, 9.5, 9.6 |
| Percona Server | 8.0, 8.4 |
| MariaDB | 10.11, 11.4, 12.1 |
| PostgreSQL | 16, 17 |

### MySQL 9.x Notes

Starting with MySQL 9.5, the `SOURCE` command requires the `--commands` flag on the client:

    mysql --commands < employees.sql

Starting with MySQL 9.6, the `MD5()` and `SHA()` functions have been removed from the server.
The integrity test files `test_employees_md5.sql` and `test_employees_sha.sql` will not work on 9.6+.
Use `test_employees_sha2.sql` instead, which uses `SHA2(..., 256)` and is compatible with all versions:

    mysql -t < test_employees_sha2.sql

The SHA-256 checksums are identical across all supported MySQL, Percona, MariaDB, and PostgreSQL versions.

---

## 🚀 Setup & Usage (Modern Workflow)

This project is optimized for a **MariaDB 11.8+** Docker environment. A `Makefile` is provided to streamline common operations.

### 1. Prerequisites

- Docker & Docker Compose
- Make
- Python 3 (for premium reporting)

### 2. Core Commands

| Command | Action |
| :--- | :--- |
| `make start` | Start the MariaDB container (`mariadb-11-8`). |
| `make status` | Check if the database is up and healthy. |
| `make inject` | Inject the `employees.sql` dataset into the container. |
| `make test-data` | Run all tests from `tests/data/` (e.g. deadlocks, gap locking). |
| `make test-all` | **Recommended**: Run Verify + Analyze + Bench + Data in one go. |
| `make interactive` | Launch the <www.lightpath.fr> HTML test runner. |
| `make stop` | Stop the MariaDB container. |
| `make clean` | Remove all generated reports and artifacts. |

### Environment Overrides

| Variable | Effect |
| :--- | :--- |
| `USE_CONTAINER=0` | Force local execution (bypasses Docker checks). |
| `CONTAINER_NAME=xyz` | Target a specific container name. |

---

## 📚 Technical Documentation

Deep-dive documentation for specific components is available in the `documentation/` directory:

| Topic | Documentation (EN) | Documentation (FR) |
| :--- | :--- | :--- |
| **All Technical Documentation** | [index.md](documentation/en/index.md) | [index.md](documentation/fr/index.md) |
| **SQL Analysis** | [sql_analyzer.md](documentation/en/sql_analyzer.md) | [sql_analyzer.md](documentation/fr/sql_analyzer.md) |
| **MariaDB/Docker** | [mariadb_management.md](documentation/en/mariadb_management.md) | [mariadb_management.md](documentation/fr/mariadb_management.md) |
| **Benchmarking** | [benchmarking.md](documentation/en/benchmarking.md) | [benchmarking.md](documentation/fr/benchmarking.md) |
| **Tools Guide** | [tools_guide.md](documentation/en/tools_guide.md) | [guide_outils.md](documentation/fr/guide_outils.md) |
| **Interactive Reporting** | [interactive_reporting.md](documentation/en/interactive_reporting.md) | [interactive_reporting.md](documentation/fr/interactive_reporting.md) |

---

## 🤖 Automation & Workflows

For users working with AI agents or seeking automated maintenance, we provide specialized workflows in `.agent/workflows/`:

- `/run-tests`: Comprehensive battery of tests with documentation sync.
- `/git-sync`: Conventional commit automation and remote synchronization.
- `/release`: **Full release flow**: logic for versioning, changelog, and multi-line annotated tags.
- `/audit`: Structural and performance audit of the environment.

---

## 📂 Repository Map

- `employees/`: Core dataset, schema definitions, and 60+ sample queries.
- `postgresql/`: PostgreSQL dataset, schema definitions, loading script, and integrity tests.
- `scripts/`: Python/Bash automation (SQL analyzer, sysbench Lua, runners).
- `reports/`: Destination for EXPLAIN plans, QPS results, and HTML dashboards.
- `documentation/`: Bilingual technical guides.
- `doc_employees/`: Extended documentation including ER diagrams.

---

## 🛠 Manual Installation (Non-Docker)

1. **Privileges**: Ensure your user has `CREATE`, `DROP`, `RELOAD`, `INDEX`, `ALTER`, and `CREATE VIEW` rights.
2. **Import Data**:

   ```bash
   mysql < employees/employees.sql
   ```

3. **Run Verification**:

   ```bash
   mysql -t < test_employees_sha2.sql   # SHA-256 (recommended for MySQL 8.0 - 9.6+)
   mysql -t < test_employees_md5.sql    # MD5 (MySQL 8.0–9.5 only)
   ```

---

## 🐘 PostgreSQL Installation

The database is also available for PostgreSQL 12+. The schema and data are identical to the MySQL version. All files are in the `postgresql/` directory.

### Differences from the MySQL version

- **ENUM type**: MySQL `ENUM('M','F')` is replaced with `CHAR(1) CHECK (gender IN ('M','F'))`
- **Stored procedures**: MySQL's `delimiter //` syntax is replaced with PostgreSQL dollar-quoting (`$...$ LANGUAGE plpgsql`)
- **`show_departments()`**: Implemented as a function returning TABLE (use `SELECT * FROM show_departments();` instead of `CALL show_departments();`)
- **User variables**: MySQL's `@var := value` pattern is replaced with PL/pgSQL local variables
- **Integrity tests**: Use the same incremental hashing approach but via PL/pgSQL helper functions instead of MySQL user variables

### Data integrity across databases

The SHA-256 checksums are **identical** between MySQL and PostgreSQL. This is verified in CI: the same expected values in `test_employees_sha2.sql` and `postgresql/test_employees_sha2.sql` produce matching results on both databases.

### Installation

1. Download the repository
2. Install PostgreSQL (12+)
3. Run the loading script:

   ```bash
   cd postgresql
   bash load_employees_db.sh
   ```

### Testing the PostgreSQL installation

```bash
psql -d employees < postgresql/test_employees_sha2.sql   # SHA-256 (recommended)
```

---

## 📜 Credits & License

### Origin

- **Data Creation**: Fusheng Wang and Carlo Zaniolo (Siemens Corporate Research).
- **Relational Schema**: Giuseppe Maxia.
- **Data Export**: Patrick Crews.

### License

This work is licensed under the **Creative Commons Attribution-Share Alike 3.0 Unported License**. To view a copy, visit [Creative Commons](http://creativecommons.org/licenses/by-sa/3.0/).

---
*Note: This data is fabricated and does not correspond to real people. Any similarity is purely coincidental.*
