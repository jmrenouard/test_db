# 📊 test_db (Employees Database)

A sample database with an integrated test suite, used to test your applications and database servers. This repository provides a large dataset (300,000 employees, 2.8M salaries) for performance testing and complex query practice.

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
| `make test-all` | **Recommended**: Run Verify + Analyze + Bench in one go. |
| `make interactive` | Launch the <www.lightpath.fr> HTML test runner. |
| `make stop` | Stop the MariaDB container. |
| `make clean` | Remove all generated reports and artifacts. |

---

## 📚 Technical Documentation

Deep-dive documentation for specific components is available in the `documentation/` directory:

| Topic | Documentation (EN) | Documentation (FR) |
| :--- | :--- | :--- |
| **SQL Analysis** | [sql_analyzer.md](documentation/en/sql_analyzer.md) | [sql_analyzer.md](documentation/fr/sql_analyzer.md) |
| **MariaDB/Docker** | [mariadb_management.md](documentation/en/mariadb_management.md) | [mariadb_management.md](documentation/fr/mariadb_management.md) |
| **Benchmarking** | [benchmarking.md](documentation/en/benchmarking.md) | [benchmarking.md](documentation/fr/benchmarking.md) |
| **Tools & Metrics** | [tools_guide.md](documentation/en/tools_guide.md) | [guide_outils.md](documentation/fr/guide_outils.md) |

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
   mysql -t < employees/test_employees_md5.sql
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
