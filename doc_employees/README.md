# 🗄️ Employees Database SQL Documentation

This document explains the SQL scripts provided in the `employees` directory, used for database initialization, object creation, and performance testing.

## 🏗️ Core Schema & Data Loading

| File | Description |
| :--- | :--- |
| `employees.sql` | **Main bootstrap script.** Creates the `employees` database and the 6 core tables (`employees`, `departments`, `dept_emp`, `dept_manager`, `titles`, `salaries`). It also handles data ingestion from `.dump` files. |
| `objects.sql` | **Programmable objects.** Defines auxiliary functions (e.g., `emp_name`, `emp_dept_name`), views (e.g., `v_full_employees`), and procedures (e.g., `show_departments`) for easier data access. |
| `employees_partitioned.sql` | **Alternative Schema.** Implementation of the database using **table partitioning** on `salaries` and `dept_emp` to optimize large-scale range queries. |

## 🔍 Analytical & Test Queries

The file `req_employees.sql` contains **60 categorized SQL requests** used for benchmarking and functional validation:

### 1. Simple OLTP Lookups

- Primary key lookups (e.g., `SELECT * FROM employees WHERE emp_no = 10001`).
- Filtering by date, gender, or name prefixes.
- Basic updates to simulate transactional load.

### 2. Relational Joins

- Joining employees with departments and managers.
- Retrieving salary history and title transitions.
- Triple joins to reconstruct full employee career paths.

### 3. Aggregations & Analytics

- Employee counts per department/gender.
- Average, Min, Max salary calculations.
- Using `HAVING` to filter groups (e.g., departments with many managers).

### 4. Advanced SQL Features (MariaDB 11.x)

- **CTEs (Common Table Expressions):** Calculating complex sub-metrics like average salary per gender or salary growth.
- **Window Functions:** Ranking employees by salary (`RANK()`), calculating running totals (`SUM() OVER`), and analyzing historical trends (`LAG`, `LEAD`, `FIRST_VALUE`).
- **Statistical Analytics:** Calculating standard deviation of salaries and percentile ranks (`PERCENT_RANK`).

## ⚡ Performance Benchmarking Tools

The project includes specific tools to measure database performance under various loads:

- **`make bench`**: Runs a single-threaded benchmark using all queries in `req_employees.sql`.
- **`make perf-threads`**: Executes a scaling test by running the benchmark with **1, 2, 4, 8, 16, 32, and 64 threads**.
  - Individual reports are saved in `reports/perf_threads/results_X_threads.txt`.
  - Provides real-time feedback on QPS (Queries Per Second) and average latency.
- **`scripts/employees_sysbench.lua`**: Custom Lua script that enables `sysbench` to execute the full SQL suite from `req_employees.sql`.

---

### 🚀 Technical Evolution Paths

1. **Query indexing optimization:** Analyze `EXPLAIN` plans for the 60 queries in `req_employees.sql` to propose optimized composite indexes.
2. **Automated Benchmark Suite:** Integrate `req_employees.sql` into a `sysbench` custom Lua script to measure TPS/QPS under high concurrency.
3. **JSON Export Implementation:** Add a script to export analytical query results to JSON/HTML for dynamic reporting integration.

```json
{
  "version": "1.0",
  "updates": [
    {
      "file": "doc_employees/README.md",
      "description": "Creation of the SQL documentation for the employees database."
    }
  ]
}
```
