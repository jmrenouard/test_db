# Environment Variables, Engine Parameters, and Makefile Targets

Complete parameter specification for `Makefile`, MariaDB/MySQL shell tools, Sirene PostgreSQL 18 ETL
(`sirene/src/sirene_etl/config.py`, `sirene/.env.example`), Docker Compose stacks, and MkDocs Material publishing.

## 1. Makefile Targets (`Makefile`)

Default variable in `Makefile`: `COUNT ?= 10`; `CONTAINER_NAME = mariadb-11-8`; optional `-include .env`.

### 1.1 MariaDB & Employees Targets

| Target | Underlying Command | Parameters / Overrides | Purpose |
| :--- | :--- | :--- | :--- |
| `help` | `@echo ...` | — | Prints grouped command summary |
| `start` | `docker start $(CONTAINER_NAME)` | `CONTAINER_NAME` | Starts MariaDB container |
| `stop` | `docker stop $(CONTAINER_NAME)` | `CONTAINER_NAME` | Stops MariaDB container |
| `status` | `docker ps -f name=$(CONTAINER_NAME)` | `CONTAINER_NAME` | Displays container runtime status |
| `inject` | `docker cp employees/. ... && mariadb -u root < employees.sql` | `CONTAINER_NAME` | Loads canonical `employees` schema and dumps |
| `inject-fake` | `python3 scripts/inject_fake_employees.py --count $(COUNT) --container $(CONTAINER_NAME)` | `COUNT` (`10`), `CONTAINER_NAME` | Injects synthetic employees via Faker or fallback |
| `verify` | `bash scripts/test_runner.sh verify` | `USE_CONTAINER`, `CONTAINER_NAME`, `DB_*` | Verifies row counts and `CHECKSUM TABLE` |
| `bench` | `bash scripts/test_runner.sh bench` | `USE_CONTAINER`, `CONTAINER_NAME`, `DB_*` | Runs single-thread sequential `sysbench` query pass |
| `perf-threads` | `bash scripts/test_runner.sh perf-threads` | `USE_CONTAINER`, `CONTAINER_NAME`, `DB_*` | Runs 1/2/4/8/16/32/64-thread scaling & HTML report |
| `analyze` | `bash scripts/test_runner.sh analyze` | `USE_CONTAINER`, `CONTAINER_NAME`, `DB_*` | Runs `EXPLAIN` & index recommendation HTML report |
| `oltp` | `THREADS=$(THREADS) ... bash scripts/test_runner.sh std-oltp $(TYPE) $(ACTION)` | `TYPE`, `ACTION`, `THREADS`, `TABLES`, `SIZE`, `TIME` | Runs standard `sysbench` OLTP workload |
| `test-data` | `bash scripts/test_runner.sh data-tests $(TEST)` | `TEST` (optional subdir under `tests/data/`) | Runs contention/deadlock/gap-locking SQL tests |
| `test-all` | `bash scripts/test_runner.sh all` | `USE_CONTAINER`, `CONTAINER_NAME`, `DB_*` | Runs `verify`, `analyze`, `bench`, `perf-threads`, `data-tests` |
| `interactive` | `python3 interactive_runner.py` | `USE_CONTAINER` | Launches interactive CLI and live HTML report |
| `clean` | `rm -rf reports/...` | — | Removes generated Markdown, text, JSON, and HTML reports |

### 1.2 Sirene PostgreSQL 18 3NF & Multi-Master Targets

| Target | Underlying Command | Parameters / Overrides | Purpose |
| :--- | :--- | :--- | :--- |
| `sirene-up` | `docker compose -f sirene/docker-compose.yml up -d sirene-postgres` | `POSTGRES_*` | Starts single-node PG 18 container (`sirene-postgres`) |
| `sirene-down` | `docker compose -f sirene/docker-compose.yml --profile daemon down` | — | Stops Sirene Compose services including `sirene-watcher` |
| `sirene-test` | `up -d --wait sirene-postgres`, `build sirene-etl`, `run --rm sirene-etl pytest -v` | — | Runs full `pytest` unit, live PG 18, and governance suite |
| `sirene-import` | `docker compose ... run --rm sirene-etl python full_import.py $(ARGS)` | `ARGS` | Runs initial full-stock Sirene ingestion |
| `sirene-incremental` | `docker compose ... run --rm sirene-etl python incremental_import.py $(ARGS)` | `ARGS` | Runs transactional incremental delta sync |
| `sirene-watch` | `docker compose ... --profile daemon up -d sirene-watcher` | `WATCHER_INTERVAL_SECONDS` | Starts autonomous `data.gouv.fr` watcher daemon |
| `sirene-docs` | Prints paths to HTML and EN/FR Markdown guides | — | Displays `sirene` documentation paths |
| `sirene-mm-up` | `docker compose -f sirene/docker-compose.pg18-birep.yml up -d --wait sirene-mm-node-a sirene-mm-node-b` | `MM_NODE_A_PORT`, `MM_NODE_B_PORT` | Starts 2-node PG 18 bidirectional replication lab |
| `sirene-mm-probe` | Builds and runs `mm_probe.py --dsn-a "$MM_DSN_A" --dsn-b "$MM_DSN_B" --setup-native-birep --candidate-name pg18-native-birep $(ARGS)` | `ARGS`, `MM_DSN_A`, `MM_DSN_B` | Provisions native `origin=none` birep and runs `P1`–`P5` |
| `sirene-mm-down` | `docker compose -f sirene/docker-compose.pg18-birep.yml down -v` | — | Stops and removes 2-node MM containers and volumes |
| `sirene-inject` | `docker compose ... exec -T -w /sirene sirene-postgres psql -U ... -v ON_ERROR_STOP=1 -f load_sirene.sql` | `POSTGRES_USER`, `POSTGRES_DB` | Loads synthetic `15k` UL / `30k` SIRET SQL dumps |
| `sirene-verify` | `docker compose ... exec -T -w /sirene sirene-postgres psql -U ... -v ON_ERROR_STOP=1 -f test_sirene_sha2.sql` | `POSTGRES_USER`, `POSTGRES_DB` | Verifies row counts and 12-table SHA-256 checksums |
| `sirene-import-sample` | `run --rm sirene-etl python full_import.py --ul-file /app/data/parquet/StockUniteLegale_synthetic.parquet --etab-file /app/data/parquet/StockEtablissement_synthetic.parquet --offline-refs --force` | — | Runs `full_import.py` against offline synthetic Parquet |
| `sirene-incremental-sample` | `run --rm sirene-etl python incremental_import.py --ul-file /app/data/delta/DeltaUniteLegale_synthetic.parquet --etab-file /app/data/delta/DeltaEtablissement_synthetic.parquet --force` | — | Runs `incremental_import.py` against offline synthetic delta |

### 1.3 Documentation & MkDocs Publishing Targets

| Target | Purpose | Validation / Output |
| :--- | :--- | :--- |
| `docs-check` | Runs Diataxis, STE, and MkDocs publishing checks (`diataxis_check.py`, `pytest`, `mkdocs build --strict`) | Fails non-zero on broken links, genre mixing, or STE errors |
| `docs-build` | Compiles single-version static site from current `docs/` tree via `mkdocs build --strict` | Generates `site/` bundle |
| `docs-build-versioned` | Runs `scripts/build_versioned_docs.py` across `master` (`WORKTREE`) and tags `>= v1.9.0` | Generates `site_dist/` (`versions.json`, `.htaccess`, per-version dirs) |
| `docs-serve` | Launches local MkDocs Material live-reload preview server (`mkdocs serve`) | Serves local preview on loopback HTTP port |

---

## 2. MariaDB & Shell Runner Environment Variables

Sourced from `.env`, `.env_local`, `.env_mariadb118`, `scripts/test_runner.sh`, `scripts/verify_data.sh`,
`scripts/run_dir_bench.sh`, and `scripts/inject_fake_employees.py`. All credentials are ephemeral local lab values.

| Variable | Default | Allowed / Type | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `CONTAINER_NAME` | `mariadb-11-8` | string (`""` in `.env_local`) | `Makefile`, `scripts/*.sh`, Python | Target Docker container name |
| `USE_CONTAINER` | `true` | `true` \| `false\|0\|no\|off\|disable` | `scripts/*.sh`, Python | Enables Docker execution when running container exists; `0`/`false` forces local client |
| `DB_USER` | `root` | string | `.env*`, `scripts/*.sh` | MariaDB/MySQL client username |
| `DB_PASS` | `""` (`root` fallback in `verify_data.sh`) | string (ephemeral placeholder) | `.env*`, `scripts/*.sh` | Ephemeral lab password; leave empty or set locally in untracked `.env` |
| `DB_NAME` | `employees` | string | `.env*`, `scripts/*.sh` | Target MariaDB database schema |
| `DB_HOST` | `127.0.0.1` | IP / hostname | `.env*`, `scripts/*.sh` | Target TCP host when running locally or inside container |
| `COUNT` | `10` | integer `>= 1` | `Makefile` (`inject-fake`) | Number of synthetic employees generated |
| `THREADS` | `4` | integer `>= 1` | `Makefile` (`oltp`), `run_dir_bench.sh` | Concurrent `sysbench` worker threads |
| `TIME` | `60` | integer (seconds) | `Makefile` (`oltp`), `run_dir_bench.sh` | `sysbench` benchmark execution duration |
| `TABLES` | unset (`sysbench` default) | integer `>= 1` | `Makefile` (`oltp`), `db_simulator.py` | Standard OLTP table count override |
| `SIZE` | unset (`sysbench` default) | integer `>= 1` | `Makefile` (`oltp`), `db_simulator.py` | Rows per OLTP table override (`--table-size`) |
| `TYPE` | unset (required for `oltp`) | `read_only`, `read_write`, `update_index`, `update_non_index`, `write_only` | `Makefile` (`oltp`) | Selects `/usr/share/sysbench/oltp_<TYPE>.lua` |
| `ACTION` | `run` | `prepare`, `run`, `cleanup` | `Makefile` (`oltp`) | Standard `sysbench` lifecycle phase |
| `TEST` | unset (all subdirs) | subdir name under `tests/data/` | `Makefile` (`test-data`) | Filters `tests/data/<TEST>` scenario |
| `PSQL` | `psql` | binary path/name | `postgresql/load_employees_db.sh`, `sirene/load_sirene_db.sh` | PostgreSQL CLI executable override |

---

## 3. Sirene PostgreSQL 18 ETL & Multi-Master Environment Variables

Loaded by `sirene/src/sirene_etl/config.py` (`load_settings()`) and Compose files (`sirene/docker-compose.yml`,
`sirene/docker-compose.pg18-birep.yml`). Placeholder credentials below are ephemeral local PoC values only.

| Variable | Default Value | Unit / Type | Source / Component | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `POSTGRES_IMAGE` | `postgres:18-bookworm` | Docker tag | Compose stacks | Base PostgreSQL 18 container image |
| `POSTGRES_USER` | `sirene` | string | Compose stacks | PostgreSQL superuser/role inside container |
| `POSTGRES_PASSWORD` | `<ephemeral-local-password>` (template `pg_sirene_ephemeral` in `sirene/.env.example`) | string | Compose stacks | Ephemeral lab-only password; override via untracked `sirene/.env` |
| `POSTGRES_DB` | `sirene` | string | Compose stacks | Target PostgreSQL database name |
| `POSTGRES_HOST_PORT` | `15432` | TCP port (`127.0.0.1`) | `docker-compose.yml` | Host loopback port mapped to container `5432` (avoids host `5432` conflict) |
| `MM_NODE_A_PORT` | `15441` | TCP port (`127.0.0.1`) | `docker-compose.pg18-birep.yml` | Host loopback port for `sirene-mm-node-a` |
| `MM_NODE_B_PORT` | `15442` | TCP port (`127.0.0.1`) | `docker-compose.pg18-birep.yml` | Host loopback port for `sirene-mm-node-b` |
| `DATABASE_URL` | `postgresql://sirene:<ephemeral-pass>@localhost:15432/sirene` | DSN URI | `config.py`, `sirene-etl` (`@sirene-postgres:5432`) | Connection string for `psycopg` v3 ETL modules |
| `MM_DSN_A` | `postgresql://sirene:<ephemeral-pass>@sirene-mm-node-a:5432/sirene` | DSN URI | `docker-compose.pg18-birep.yml`, `mm_probe.py` | Node A connection string for multi-master probes |
| `MM_DSN_B` | `postgresql://sirene:<ephemeral-pass>@sirene-mm-node-b:5432/sirene` | DSN URI | `docker-compose.pg18-birep.yml`, `mm_probe.py` | Node B connection string for multi-master probes |
| `MM_INTERNAL_DSN_A` | Falls back to `--dsn-a` | DSN URI | `mm_probe.py` | Inter-container DSN used by Node B (`sub_from_a`) |
| `MM_INTERNAL_DSN_B` | Falls back to `--dsn-b` | DSN URI | `mm_probe.py` | Inter-container DSN used by Node A (`sub_from_b`) |
| `STAGING_DIR` | `./staging` (`/app/staging` in Compose) | directory path | `config.py` | Staging directory for `.part` downloads and cached referentials |
| `SQL_DIR` | `<package_root>/sql` (`/app/sql` in Compose) | directory path | `config.py` | Location of `01_schema_3nf.sql` and `02_indexes.sql` |
| `BATCH_SIZE` | `50000` | rows (`int > 0`) | `config.py` | Rows streamed per `COPY FROM STDIN` batch |
| `WATCHER_INTERVAL_SECONDS` | `3600` | seconds (`int > 0`) | `config.py` | Polling interval in `watcher.py` daemon mode |
| `PREFERRED_FORMAT` | `parquet` | `parquet` \| `zip` \| `csv.gz` \| `csv` | `config.py` | Preferred `data.gouv.fr` resource format |
| `LOG_LEVEL` | `INFO` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `logging_utils.py`, Compose | Structured JSON logger verbosity |
| `DATAGOUV_DATASET_API` | `https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/` | HTTPS URL | `config.py` | `data.gouv.fr` Sirene dataset metadata endpoint |
| `COG_REGIONS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_region_2026.csv` | HTTPS URL | `config.py` | INSEE COG 2026 regions CSV |
| `COG_DEPARTEMENTS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv` | HTTPS URL | `config.py` | INSEE COG 2026 departments CSV |
| `COG_COMMUNES_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv` | HTTPS URL | `config.py` | INSEE COG 2026 municipalities CSV |
| `COG_COMMUNES_HIST_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv` | HTTPS URL | `config.py` | INSEE historical municipalities since 1943 CSV |
| `COG_COMER_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_comer_2026.csv` | HTTPS URL | `config.py` | INSEE overseas collectivities (`COMER`) CSV |
| `COG_PAYS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_pays_territoire_2026.csv` | HTTPS URL | `config.py` | INSEE countries and territories CSV |
| `NAF_PARQUET_URL` | `https://static.data.gouv.fr/resources/naf-1/20231123-121750/nafr2.parquet` | HTTPS URL | `config.py` | Official NAF Rev. 2 hierarchy Parquet file |

---

## 4. PostgreSQL 18 Container Engine Parameters

| Stack File | Service(s) | Volume Mount (`PGDATA`) | `shm_size` | `postgres` `-c` Runtime Flags |
| :--- | :--- | :--- | :--- | :--- |
| `sirene/docker-compose.yml` | `sirene-postgres` | `sirene_pgdata:/var/lib/postgresql` | `1gb` | `shared_buffers=1GB`, `work_mem=64MB`, `maintenance_work_mem=512MB`, `max_wal_size=4GB`, `checkpoint_timeout=15min`, `wal_level=minimal`, `max_wal_senders=0`, `effective_io_concurrency=200` |
| `sirene/docker-compose.pg18-birep.yml` | `sirene-mm-node-a`, `sirene-mm-node-b` | `sirene_mm_*_pgdata:/var/lib/postgresql` | `512mb` | `wal_level=logical`, `max_wal_senders=10`, `max_replication_slots=10`, `track_commit_timestamp=on` |

---

## 5. MkDocs Publishing Variables & CI Secrets

| Variable / Secret | Scope | Default / Format | Purpose |
| :--- | :--- | :--- | :--- |
| `TEST_DB_DOCS_REF` | Build hook (`scripts/mkdocs_hooks.py`) | `master` (normalizes `WORKTREE`, `HEAD`, `origin/master`) | Git ref used when rewriting repo-relative links to GitHub `blob`/`tree` URLs |
| `TEST_DB_DOCS_SITE_URL` | Build hook / versioned builder | `https://test-db.lightpath.fr` | Base portal URL for canonical links and redirect templates |
| `IONOS_FTP_SERVER` | GitHub Actions secret (`docs-publish.yml`) | Hostname (SFTP) | Remote IONOS hosting server endpoint |
| `IONOS_FTP_USERNAME` | GitHub Actions secret (`docs-publish.yml`) | Username string | SFTP authentication username |
| `IONOS_FTP_PASSWORD` | GitHub Actions secret (`docs-publish.yml`) | Ephemeral CI secret | SFTP authentication secret (never stored in repository) |
| `IONOS_FTP_PORT` | GitHub Actions secret (`docs-publish.yml`) | `22` | SFTP TCP port |
| `IONOS_REMOTE_PATH` | GitHub Actions secret (`docs-publish.yml`) | Remote path string | Target web root directory on IONOS hosting |

## Related Reference & Explanations

- Diataxis and sparse versioned MkDocs publishing architecture:
  [ADR-002: Diataxis & Versioned MkDocs Publishing](../../04-explanation/design-decisions/adr-002-diataxis-versioned-mkdocs-publishing.md)
- Deployment SOP for MariaDB and PostgreSQL stacks:
  [Deploy MariaDB and PostgreSQL Stacks](../../02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md)
- CLI options and SQL query catalogs:
  [CLI Scripts and SQL Catalog](../cli-and-scripts/cli-scripts-and-sql-catalog.md)
