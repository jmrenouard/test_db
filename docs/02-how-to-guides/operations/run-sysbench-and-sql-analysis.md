# Run Sysbench and SQL Analysis

Refer to
[CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
before you select custom `sysbench` flags or SQL files.

## Prerequisites

1. Start `mariadb-11-8` and load the `employees` dataset with `make start` and `make inject`.
2. Make sure that Python 3 is available on `PATH`.
3. Make sure that `sysbench` is available inside `mariadb-11-8` or on the local host.

## Safety Instructions

**CAUTION:** Run `sysbench` stress workloads and `make oltp` mutations only against disposable lab databases.
Standard OLTP `prepare` and `cleanup` commands create and drop `sbtest` tables inside `DB_NAME`.

**CAUTION:** Set `USE_CONTAINER=0` only when a local MariaDB server runs on `DB_HOST`.
Local mode connects directly to `127.0.0.1` instead of `mariadb-11-8`.

## Procedure

1. Execute the baseline single-thread query benchmark against `employees/req_employees.sql`:

   ```bash
   make bench
   ```

2. Run the multi-thread scale sweep across `1`, `2`, `4`, `8`, `16`, `32`, and `64` threads:

   ```bash
   make perf-threads
   ```

3. Prepare, execute, and clean up a standard Sysbench OLTP workload:

   ```bash
   make oltp TYPE=read_write ACTION=prepare TABLES=4 SIZE=10000
   make oltp TYPE=read_write ACTION=run THREADS=8 TIME=30 TABLES=4 SIZE=10000
   make oltp TYPE=read_write ACTION=cleanup TABLES=4
   ```

4. Run a directory-based concurrency simulation with `make test-data`:

   ```bash
   make test-data TEST=deadlock
   ```

5. Execute `make analyze` to inspect `EXPLAIN` plans and generate index DDL suggestions:

   ```bash
   make analyze
   ```

6. Analyze one custom SQL statement directly on standard output:

   ```bash
   python3 scripts/sql_analyzer.py --container mariadb-11-8 --query "SELECT * FROM employees WHERE emp_no = 10001" --stdout
   ```

7. Launch the guided terminal menu if you want interactive selection across all suites:

   ```bash
   make interactive
   ```

**NOTE:** Each `make perf-threads` iteration runs for `60s` per thread count.
A full 7-step sweep takes approximately seven minutes.

## Verification

1. Confirm that `reports/perf_threads/scaling_report.html` and `reports/perf_threads/scaling_report.md` exist.
2. Confirm that `reports/performance_report.html` and `reports/explain_reports/` contain per-query outputs.
3. Open `reports/deadlock/report_deadlock.md` and confirm valid TPS, QPS, and latency figures.

## Rollback

If a benchmark run leaves `sbtest` or contention tables behind, do these steps:

1. Run `make oltp ACTION=cleanup` for any active OLTP test type:

   ```bash
   make oltp TYPE=read_write ACTION=cleanup TABLES=4
   ```

2. Execute the directory teardown script manually if a simulation aborted early:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root employees < tests/data/deadlock/teardown.sql
   ```

3. Remove generated report artifacts from `reports/`:

   ```bash
   make clean
   ```

4. Run `make verify` to confirm that all six `employees` tables match baseline counts.

## Related Documentation

- Reference: [CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
- Reference: [Environment Variables and Makefile Targets](../../03-reference/configuration/environment-variables-and-makefile-targets.md)
- Explanation: [Platform and ETL Architecture](../../04-explanation/architecture-overview/platform-and-etl-architecture.md)
- Explanation:
  [Concurrency, Lock Mechanics, and Replication Trade-offs](../../04-explanation/deep-dives/concurrency-locking-and-replication-tradeoffs.md)
