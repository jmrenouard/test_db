# CLI Scripts, Exit Codes, and SQL Query Catalogs

Exact CLI syntax, flag specifications, process exit codes, and SQL catalogs grounded in `sirene/*.py`,
`sirene/scripts/generate_synthetic_dataset.py`, `scripts/*.py`, `scripts/*.sh`, `interactive_runner.py`,
`employees/req_employees.sql`, and `sirene/sql/03_sample_queries.sql`.

## 1. Python & Bash Scripts Reference

### 1.1 `sirene/full_import.py` (`sirene_etl.full_import:main`)

Idempotent full-stock Sirene importer with secondary index drop/rebuild, `COPY FROM STDIN`, sole-proprietor
projection, and `ANALYZE`.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (fetches via `data.gouv.fr` API) | Local `StockUniteLegale` path (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (fetches via `data.gouv.fr` API) | Local `StockEtablissement` path (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--ref-dir` | `Path` | `None` | Local directory containing INSEE COG 2026 CSVs and `nafr2.parquet` |
| `--offline-refs` | flag | `False` | Seeds built-in offline referentials without HTTP calls |
| `--limit-rows` | `int` | `None` | Maximum records read per entity file |
| `--force` | flag | `False` | Re-imports even when matching SHA-256 checksum exists with `SUCCESS` in `etl_logs` |

- **Exit Codes**: `0` on completion (including checksum `SKIPPED` no-op); non-zero (`1` uncaught exception such as
  missing file, advisory lock `84729101` contention, checksum mismatch, or SQL failure; `2` `argparse` error).

### 1.2 `sirene/incremental_import.py` (`sirene_etl.incremental_import:main`)

Single-transaction delta synchronization with `ON COMMIT DROP` temp tables, monotonic `date_dernier_traitement`
guard, and `'A' <-> 'F'` transition logging in `etablissements_historique_etat`.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (API) | Local delta `StockUniteLegale` path (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (API) | Local delta `StockEtablissement` path (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--force` | flag | `False` | Re-applies delta files even if checksums already succeeded in `etl_logs` |

- **Exit Codes**: `0` on commit or checksum skip; non-zero on missing file, advisory lock contention, or SQL error (`2`
  on invalid CLI flags).

### 1.3 `sirene/watcher.py` (`sirene_etl.watcher:main`)

Autonomous `data.gouv.fr` metadata poller dispatching `run_full_import` (when `unites_legales` is empty) or
`run_incremental_import` (when populated), logging each cycle as `WATCHER_CHECK` in `etl_logs`.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--once` | flag | `False` | Executes one poll-and-sync cycle and exits |
| `--interval` | `int` | `WATCHER_INTERVAL_SECONDS` (`3600`) | Daemon poll interval in seconds (must be `> 0`) |
| `--force` | flag | `False` | Forces download and ETL execution regardless of unchanged metadata |
| `--offline-refs` | flag | `False` | Passes `--offline-refs` when triggering an initial full import |

- **Exit Codes**: `0` on `--once` success or graceful `SIGINT`/`SIGTERM` shutdown; non-zero if `--once` fails or
  `--interval <= 0` (`ValueError`), `2` on invalid CLI flags. In daemon loop mode, failed iterations log an error and
  retry after `poll_interval`.

### 1.4 `sirene/mm_probe.py` (`sirene_etl.mm_probe:main`)

Executes the 5-probe multi-master qualification harness (`P1_DDL_COMPAT`, `P2_SEQUENCE_SPLIT_BRAIN`,
`P3_CONCURRENT_SIRET_UPSERT`, `P4_CROSS_NODE_FK_CAUSALITY`, `P5_BULK_COPY_REPLICATION_LAG`) in order
`P1 -> P2 -> P4 -> P5 -> P3`.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--dsn-a` | `str` | `MM_DSN_A` or `DATABASE_URL` | Target DSN for Node A |
| `--dsn-b` | `str` | `MM_DSN_B` or `DATABASE_URL` | Target DSN for Node B |
| `--internal-dsn-a` | `str` | `MM_INTERNAL_DSN_A` or `--dsn-a` | Inter-container DSN used by Node B (`sub_from_a`) |
| `--internal-dsn-b` | `str` | `MM_INTERNAL_DSN_B` or `--dsn-b` | Inter-container DSN used by Node A (`sub_from_b`) |
| `--candidate-name` | `str` | `pg18-candidate` | Architecture label printed in Markdown/JSON scorecards |
| `--setup-native-birep` | flag | `False` | Creates `sirene_mm_pub`, staggers sequences, and creates `origin=none` subscriptions |
| `--no-stagger-sequences` | flag | `False` | Disables `INCREMENT BY 2` sequence staggering during native setup |
| `--batch-rows` | `int` | `200` | Establishments streamed in `P5` (`1..99999`) |
| `--timeout-sec` | `float` | `15.0` | Replication convergence timeout per probe (seconds) |
| `--output-md` | `Path` | `None` | Writes rendered Markdown scorecard to file |
| `--output-json` | `Path` | `None` | Writes structured JSON scorecard to file |

- **Exit Codes**: `0` once scorecard prints (verdict `PRODUCTION_MULTI_MASTER_READY`,
  `CONDITIONAL_PARTITIONED_WRITES_ONLY`, or `INCOMPATIBLE_WITH_SIRENE_3NF` appears in stdout/report); non-zero on
  connection failure, invalid `--batch-rows`, subscription wait timeout, or invalid CLI flags (`2`).

### 1.5 `sirene/scripts/generate_synthetic_dataset.py`

Deterministic synthetic dataset generator (`SEED = 20261120`, zero PII, SIRENs `900000001`–`900015050`).

| CLI Flag | Default | Behavior |
| :--- | :--- | :--- |
| None (`main()` takes zero flags) | — | Regenerates `sirene/data/sql/01..04_*.sql` (LF endings), `sirene/data/parquet/*.parquet` (ZSTD), and `sirene/data/delta/*` |

- **Exit Codes**: `0` on completion; non-zero on write/import error.

### 1.6 `scripts/db_simulator.py`

Sysbench workload orchestrator and deadlock-extracting Markdown/HTML report generator.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--sql-dir` | `str` | mutually exclusive (required with `--script`) | Directory of transaction `.sql` files (runs `setup.sql` / `teardown.sql` if present) |
| `--script` | `str` | mutually exclusive | Direct `sysbench` Lua script path (e.g., `/usr/share/sysbench/oltp_read_only.lua`) |
| `--host` | `str` | `127.0.0.1` | MariaDB host |
| `--user` | `str` | `root` | MariaDB user |
| `--password` | `str` | `""` | MariaDB password |
| `--db` | `str` | `employees` | Target database |
| `--threads` | `int` | `4` | Concurrent `sysbench` threads |
| `--time` | `int` | `60` | Simulation duration in seconds |
| `--container` | `str` | `None` (cleared if `USE_CONTAINER=0`) | Target Docker container for `docker exec` and deadlock `docker logs` capture |
| `--name` | `str` | `Generic Test` | Report title slug |
| `--output-dir` | `str` | `reports` | Destination directory (`report_<slug>.md` and `.html`) |
| `--tables` | `int` | `None` | Passed as `--tables` to `sysbench` |
| `--table-size` | `int` | `None` | Passed as `--table-size` to `sysbench` |

- **Exit Codes**: `0` when simulation and report generation succeed; `1` when `run_simulation()` returns `False`;
  `2` on missing mutually exclusive argument.

### 1.7 `scripts/sql_analyzer.py`

Batch or single-query MariaDB `EXPLAIN` analyzer, heuristic rater, and missing-index DDL recommender.

| Flag | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `--query-file` | `str` | `employees/req_employees.sql` | Semicolon-delimited SQL file to analyze |
| `--query` | `str` | `None` | Single SQL query string (overrides `--query-file`) |
| `--container` | `str` | `None` (cleared if `USE_CONTAINER=0`) | MariaDB Docker container name |
| `--host` | `str` | `127.0.0.1` | MariaDB host |
| `--port` | `int` | `3306` | MariaDB TCP port |
| `--user` | `str` | `root` | MariaDB user |
| `--password` | `str` | `root` | MariaDB password |
| `--db` | `str` | `employees` | Target database schema |
| `--report-dir` | `str` | `reports/explain_reports` | Per-query `.txt` output directory |
| `--report-file` | `str` | `reports/performance_report.md` | Markdown summary file |
| `--html-file` | `str` | `reports/performance_report.html` | Interactive HTML report file |
| `--stdout` | flag | `False` | Prints per-query analysis to stdout |

- **Exit Codes**: `0` on completion; `1` if `--query-file` does not exist; `2` on invalid flags.

### 1.8 `interactive_runner.py`

Sequential and interactive MariaDB workflow runner producing live updates in `reports/run_report.html`.

| Flag | Behavior |
| :--- | :--- |
| `-a`, `--auto` | Runs all configured steps (`start`, `status`, `inject`, `verify`, `analyze`, `bench`, `perf-threads`) without prompts |
| `--run-all` | Runs all steps automatically without prompts |
| `-i`, `--interactive` | Prompts `(Y/n)` before each step and `(y/N)` on failure |

- **Exit Codes**: `0` on completion or `KeyboardInterrupt`; non-zero on unhandled exception (`2` on invalid flags).

### 1.9 `scripts/test_runner.sh` & Supporting Scripts

| Script | Subcommands / Flags | Exit Codes |
| :--- | :--- | :--- |
| `scripts/test_runner.sh` | `inject`, `verify`, `analyze`, `bench`, `perf-threads`, `std-oltp <type> [prepare\|run\|cleanup]`, `data-tests [subdir]`, `all`, `help` | `0` on success; `1` on missing SQL/data dir or missing `oltp` type; propagates sub-tool non-zero codes |
| `scripts/verify_data.sh` | Positional args: `[container] [user] [password] [db]` | `0` when `TOTAL_ERRORS == 0`; `1` on row-count or `CHECKSUM TABLE` mismatch |
| `scripts/run_dir_bench.sh` | `--sql-dir`, `--script`, `--threads`, `--time`, `--host`, `--container`, `--user`, `--password`, `--db`, `-h/--help` | `0` on `sysbench` completion; `1` on missing `--sql-dir`/`--script` or invalid dir |
| `scripts/inject_fake_employees.py` | `--count` (`10`), `--start-emp-no`, `--db-name` (`employees`), `--container`, `--use-container`, `--dry-run`, `--output-sql`, `--seed` | `0` on completion; `1` on `mariadb` execution failure |
| `scripts/perf_threads_reporter.py` | `--dir` (`reports/perf_threads`), `--md`, `--html` | `0` on completion; `1` if no `results_*_threads.txt` files exist |
| `sirene/load_sirene_db.sh` | Forwards all CLI args (`"$@"`) to `psql -v ON_ERROR_STOP=1 -f sirene/load_sirene.sql` | Propagates `psql` exit code (`0` success, `1`–`3` `psql` error) |
| `postgresql/load_employees_db.sh` | Zero CLI args; streams `postgresql/employees.sql` and `.dump` files via `sed` to `$PSQL` | Propagates `psql` exit code (`set -euo pipefail`) |

---

## 2. SQL Catalog: `employees/req_employees.sql` (`60` Queries)

| ID | Category | Primary Tables / Constructs | Query Description |
| :---: | :--- | :--- | :--- |
| `1` | OLTP Lookup | `employees` | Simple OLTP lookup by `emp_no = 10001` |
| `2` | Range Filter | `employees` | Filter employees hired after `'1995-01-01'` (`LIMIT 10`) |
| `3` | Prefix Search | `employees` | Filter by `last_name LIKE 'Fac%'` (`LIMIT 5`) |
| `4` | Scalar Aggregate | `employees` | Total employee count (`COUNT(*)`) |
| `5` | Composite Filter | `employees` | Female employees born in `1960` (`BETWEEN`) |
| `6` | OLTP Write | `employees` | Update `first_name` for `emp_no = 10002` |
| `7` | Point Lookup | `salaries` | Current salary for `emp_no = 10001` (`ORDER BY to_date DESC LIMIT 1`) |
| `8` | Catalog Scan | `departments` | List all departments ordered by `dept_name` |
| `9` | Active Filter | `dept_manager` | Current managers (`to_date = '9999-01-01'`) |
| `10` | Grouped Count | `employees` | Employee count grouped by `gender` |
| `11` | Multi-Table Join | `employees`, `dept_emp`, `departments` | Active employee names with current department name (`LIMIT 10`) |
| `12` | Multi-Table Join | `employees`, `dept_manager`, `departments` | Historical and current managers with department name |
| `13` | Scalar Aggregate | `salaries` | Company-wide mean salary (`AVG(salary)`) |
| `14` | History Join | `employees`, `titles` | Title history for `emp_no = 10005` |
| `15` | Top-N Sort | `salaries` | Top 5 highest historical salaries (`ORDER BY salary DESC LIMIT 5`) |
| `16` | Triple Join | `employees`, `dept_emp`, `departments`, `titles` | Active employees with current department and title (`LIMIT 10`) |
| `17` | Scalar Subquery | `salaries` | Current earners above company average (`LIMIT 10`) |
| `18` | Join Aggregate | `departments`, `dept_emp` | Total assignments per department |
| `19` | Join Aggregate | `departments`, `dept_emp`, `salaries` | Maximum salary per department |
| `20` | Having Filter | `dept_manager` | Departments with `> 10` historical managers |
| `21` | CTE Aggregate | `employees`, `salaries` | Average salary per gender via `GenderAvg` CTE |
| `22` | Window Function | `employees`, `dept_emp`, `salaries` | `RANK()` by current salary partitioned by `dept_no` (`LIMIT 20`) |
| `23` | Window Function | `salaries` | Running sum of current salaries (`SUM(salary) OVER (ORDER BY emp_no)`) |
| `24` | CTE Join | `titles`, `employees` | Employees holding multiple distinct titles (`MultiTitle` CTE) |
| `25` | Window Function | `salaries` | Previous salary per employee via `LAG(salary)` (`LIMIT 20`) |
| `26` | Window Function | `salaries` | `PERCENT_RANK()` across active salaries (`LIMIT 20`) |
| `27` | Join Aggregate | `departments`, `dept_emp`, `employees` | Departments ordered ascending by average employee age |
| `28` | CTE Aggregate | `titles`, `salaries` | Maximum active salary per active title (`TitleMax` CTE) |
| `29` | Window Function | `salaries` | `ROW_NUMBER()` per employee ordered by `from_date DESC` (`LIMIT 20`) |
| `30` | Window + CTE | `salaries` | Salary growth (`LAST_VALUE - FIRST_VALUE`) per employee (`LIMIT 10`) |
| `31` | OLTP Write | `departments` | Insert temporary department `('d999', 'Temporary Service')` via `INSERT IGNORE` |
| `32` | Anti-Join | `employees`, `dept_manager` | Employees never assigned as manager (`LEFT JOIN ... IS NULL`) |
| `33` | Temporal Grouping | `employees` | Hiring count grouped by `YEAR(hire_date)` |
| `34` | Window Function | `salaries` | Next salary record via `LEAD(salary)` (`LIMIT 10`) |
| `35` | CTE Classification | `employees` | Seniority brackets (`Veteran`, `Senior`, `Junior`) via `Seniority` CTE |
| `36` | Self-Join | `employees`, `dept_emp`, `departments`, `dept_manager` | Active employees paired with their current department manager |
| `37` | Statistical Agg | `departments`, `dept_emp`, `salaries` | Salary standard deviation (`STDDEV`) per department |
| `38` | Window Function | `employees` | `DENSE_RANK()` ordered by `hire_date` (`LIMIT 20`) |
| `39` | `IN` Subquery | `departments`, `dept_emp`, `salaries` | Departments having at least one salary `> 140000` |
| `40` | Temporal Aggregate | `employees` | Peak hiring month (`MONTH(hire_date)`) historically |
| `41` | Multi-CTE | `salaries` | Employees with `> 50%` salary growth (`InitialSal` + `CurrentSal` CTEs) |
| `42` | Window Function | `salaries` | Salary quartiles (`NTILE(4)`) for active salaries |
| `43` | Join Having | `employees`, `dept_emp` | Employees assigned to multiple departments (`HAVING COUNT > 1`) |
| `44` | Ratio Aggregate | `departments`, `dept_emp`, `salaries` | Department average salary divided by global average |
| `45` | Window Function | `employees` | `CUME_DIST()` of `hire_date` (`LIMIT 20`) |
| `46` | OLTP Write | `departments` | Delete temporary department `dept_no = 'd999'` |
| `47` | Subquery Percentile | `salaries` | Median-like active salary via `ROW_NUMBER()` and `COUNT(*) OVER ()` |
| `48` | Self-Join Comparison | `employees`, `dept_emp`, `dept_manager` | Employees older than their current department manager |
| `49` | Gap Detection CTE | `employees` | Hiring gap years via `Years` CTE and `NOT EXISTS` |
| `50` | CTE + Window Filter | `salaries`, `dept_emp` | Top `1%` active earners per department (`PERCENT_RANK() <= 0.01`) |
| `51` | Moving Window | `salaries` | 3-record moving average (`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`) |
| `52` | Temporal Equality Join | `employees`, `titles`, `salaries` | First title and first salary matching `hire_date` (`LIMIT 10`) |
| `53` | Temporal Aggregate | `salaries` | Total salary sum grouped by `YEAR(from_date)` |
| `54` | Mobility Having | `dept_emp` | Employees having worked in `> 2` distinct departments |
| `55` | CTE Aggregate | `employees` | Mean daily hiring count (`DailyHires` CTE) |
| `56` | Window Comparison | `salaries` | Flags whether current salary equals all-time personal maximum |
| `57` | Date-Part Join | `employees` | Employees hired in the same calendar month as `birth_date` (`LIMIT 10`) |
| `58` | Mode Aggregate | `employees` | Single most frequent `last_name` |
| `59` | Derived Window Table | `employees`, `dept_emp` | Most recent hire per department (`last_hired = 1`) |
| `60` | Conditional Aggregate | `departments`, `dept_emp`, `employees`, `salaries` | Active male vs. female average salary per department |

---

## 3. SQL Catalog: `sirene/sql/03_sample_queries.sql` (`15` Queries)

All `15` queries are read-only PostgreSQL `18` statements compatible with `ON_ERROR_STOP=1` against empty or populated
3NF databases.

| ID | Analytical / Search Domain | Primary Tables Joined | Primary Indexed Paths |
| :---: | :--- | :--- | :--- |
| `1` | Exact SIREN / SIRET lookup | `etablissements`, `unites_legales`, `ref_categories_juridiques`, `ref_naf`, `ref_tranches_effectifs`, `ref_communes`, `ref_departements`, `ref_regions`, `ref_pays` | `unites_legales_pkey`, `etablissements_pkey`, `idx_etab_siren` |
| `2` | Active NAF division + officers/proprietors | `etablissements`, `unites_legales`, `ref_naf`, `ref_categories_juridiques`, `ref_communes`, `ref_departements`, `ref_regions`, `roles_entreprises`, `personnes` | `idx_etab_etat_administratif`, `idx_etab_code_naf`, `idx_ul_etat_administratif`, `idx_roles_siren` |
| `3` | Unified `pg_trgm` fuzzy search across 3 dimensions | `unites_legales`, `etablissements`, `personnes`, `roles_entreprises` | `idx_ul_nom_trgm`, `idx_etab_enseigne_trgm`, `idx_personnes_nom_trgm`, `idx_roles_personne_id` |
| `4` | Officer / shareholder corporate portfolio | `roles_entreprises`, `personnes`, `unites_legales` (`ul` + `pm`), `ref_categories_juridiques`, `ref_naf`, `etablissements` | `idx_roles_personne_id`, `idx_roles_siren`, `idx_personnes_siren_pm`, `idx_etab_siren` |
| `5` | Active sole proprietors (`ENTREPRENEUR_INDIVIDUEL`) | `roles_entreprises`, `personnes`, `unites_legales`, `ref_naf`, `etablissements`, `ref_communes`, `ref_departements` | `idx_ul_etat_administratif`, `idx_roles_siren`, `idx_etab_siren`, `idx_etab_code_commune` |
| `6` | WGS84 bounding-box + Haversine & Lambert-93 radius | `etablissements`, `unites_legales` | `idx_etab_etat_administratif`, `unites_legales_pkey` |
| `7` | NAF Rev. 2 5-level `GROUP BY ROLLUP` hierarchy | `etablissements`, `ref_naf` | `idx_etab_code_naf`, `ref_naf_pkey` |
| `8` | Regional & departmental density + headcount floor | `ref_regions`, `ref_departements`, `ref_communes`, `etablissements`, `ref_tranches_effectifs` | `idx_ref_departements_code_region`, `idx_ref_communes_code_departement`, `idx_etab_code_commune` |
| `9` | Enterprise category (`PME`/`ETI`/`GE`), ESS & mission units | `unites_legales`, `ref_categories_juridiques`, `etablissements` | `idx_ul_categorie_entreprise`, `idx_ul_code_cj`, `idx_etab_siren` |
| `10` | Multi-establishment corporate networks (`COUNT >= 2`) | `unites_legales`, `etablissements`, `ref_categories_juridiques`, `ref_naf`, `ref_communes` | `idx_etab_siren`, `idx_etab_code_commune` |
| `11` | Closure / reopening churn (`etablissements_historique_etat`) | `etablissements_historique_etat`, `etablissements`, `unites_legales`, `ref_naf`, `ref_communes`, `etl_logs` | `idx_etab_hist_siret`, `etablissements_pkey`, `etl_logs_pkey` |
| `12` | Company creation cohorts & longevity by decade/year | `unites_legales`, `ref_tranches_effectifs` | `idx_ul_etat_administratif`, `idx_ul_code_tranche_effectifs` |
| `13` | Foreign-located establishments (`<> '99100'`) | `etablissements`, `ref_pays` | `idx_etab_code_pays_etranger`, `ref_pays_pkey` |
| `14` | Quality audit (`[ND]` `'P'`, `UNK00`, `HIST`, orphan `'C'`) | `unites_legales`, `etablissements`, `ref_communes`, `ref_naf` | `idx_etab_code_commune`, `idx_etab_code_naf`, `idx_ul_code_cj`, `idx_ul_code_tranche_effectifs` |
| `15` | `etl_logs` run health & `pg_stat_user_tables` storage | `etl_logs`, `pg_stat_user_tables` | `idx_etl_logs_entity_status_finished`, PostgreSQL catalog stats |

## Related Reference & Procedures

- Operational Sysbench and SQL Analyzer procedures:
  [Run Sysbench and SQL Analysis](../../02-how-to-guides/operations/run-sysbench-and-sql-analysis.md)
- Operational Sirene full and incremental ETL procedures:
  [Run Sirene Full and Incremental ETL](../../02-how-to-guides/operations/run-sirene-full-and-incremental-etl.md)
- Dataset schemas, indexes, and SHA-256 baseline checksums:
  [Datasets & Schemas Matrix](../architecture-specs/datasets-and-schemas-matrix.md)
