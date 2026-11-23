# Root Cause Analysis & Improvement Register

Engineering register capturing technical root causes (`RCA-`), implemented improvements (`IMP-`), approved architectural standards (`APP-`), and future evolution ideas (`IDEA-`).

## Root Cause Analyses (RCA)

### RCA-001: Fork Remote Ambiguity and GitHub CLI Target Pitfall
- **Symptom:** Running `gh` commands without `-R` targeted `upstream` (`datacharmer/test_db`) rather than `origin` (`jmrenouard/test_db`), creating confusion around issue availability and issue numbers.
- **Root Cause:** Local Git config defines both `origin` (personal fork) and `upstream` (original template repository); `gh` defaults to the upstream tracking remote when multiple remotes exist.
- **Resolution:** Always pass `-R jmrenouard/test_db` (or set `gh repo set-default`) when inspecting, creating, or closing issues and PRs on the fork.

### RCA-002: Sirene v3.11 CSV Trailing Whitespace Headers and `[ND]` Sentinel Values
- **Symptom:** Naive CSV ingestion fails to map columns such as `"coordonneeLambertAbscisseEtablissement "` and raises numeric/date cast errors on `[ND]` (non-diffusible) cells.
- **Root Cause:** Official INSEE zipped CSV stock exports occasionally include trailing whitespace in header column names and literal `[ND]`/`[nd]` placeholder tokens across text, date, and numeric fields.
- **Resolution:** Strip whitespace from all parsed CSV column headers at read time and normalize `""`, `"null"`, `"[ND]"`, and `"[nd]"` to `None` prior to typed conversion.

### RCA-003: Host PostgreSQL Port 5432 Collision
- **Symptom:** Starting a Dockerized PostgreSQL container bound to host port `5432` fails or routes client traffic to a pre-existing local PostgreSQL service.
- **Root Cause:** Local development hosts and CI runners frequently run a system PostgreSQL daemon listening on `127.0.0.1:5432`.
- **Resolution:** Bind `sirene-postgres` exclusively to `127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432` on the host while keeping internal Docker service-to-service communication on `sirene-postgres:5432`.

### RCA-004: `psycopg` v3 Implicit `INTRANS` + `SAVEPOINT` Rollback Before `with conn.transaction():`
- **Symptom:** `run_incremental_import` reported `etab_updated=1` and `state_transitions=1`, yet PostgreSQL rows remained unchanged after the run completed.
- **Root Cause:** Running `acquire_etl_lock(conn)` and `is_checksum_already_imported(...)` on an `autocommit=False` connection left `conn` in `INTRANS`. In `psycopg` v3, entering `with conn.transaction():` on an already-open transaction creates a nested `SAVEPOINT` rather than a top-level `BEGIN`/`COMMIT`, so `finally: conn.rollback()` rolled back the entire import.
- **Resolution:** Commit the read-only lock and checksum-check preamble (`conn.commit()`) before entering `with conn.transaction():` in `sirene/src/sirene_etl/incremental_import.py` (and clear post-unlock state cleanly in `finally:`).

### RCA-005: `psycopg` v3 Parameterless `%%` Escaping and `AccessShareLock` Across `drop_secondary_indexes`
- **Symptom:** A `pg_trgm` fuzzy search query using `%%` without query parameters raised `operator does not exist: text %% unknown`, and open test transactions risked `AccessShareLock` contention during `drop_secondary_indexes`.
- **Root Cause:** `psycopg` v3 only unescapes `%%` when parameter binding is used, leaving raw `%%` intact when `params=None`; meanwhile, non-autocommit inspection connections hold `AccessShareLock` until committed or closed.
- **Resolution:** Parameterize `pg_trgm` `%` operator queries in `sirene/tests/test_integration_pipeline.py` and configure `autocommit=True` on the test fixture connection in `sirene/tests/conftest.py`.

### RCA-006: PostgreSQL 18 Docker Image `/var/lib/postgresql` Volume Layout Change
- **Symptom:** Starting `postgres:18-bookworm` with a legacy volume mounted at `/var/lib/postgresql/data` fails container initialization.
- **Root Cause:** Official Docker `postgres:18` images changed `PGDATA` to `/var/lib/postgresql/18/docker` and require the persistent volume mount point to target `/var/lib/postgresql` rather than `/var/lib/postgresql/data`.
- **Resolution:** Update `sirene/docker-compose.yml` and `sirene/docker-compose.pg18-birep.yml` persistent volume mounts to `/var/lib/postgresql` and document the layout change across EN/FR guides.

### RCA-007: Parameterized `pg_trgm` Escaping in `mm_probe.py` and Native PG 18 `origin=none` Split-Brain Divergence
- **Symptom:** Running `P5_BULK_COPY_REPLICATION_LAG` raised `psycopg.ProgrammingError: incomplete placeholder: '%'` at `sirene/src/sirene_etl/mm_probe.py:702`, and running `P3_CONCURRENT_SIRET_UPSERT` on `pg18-native-birep` (`PostgreSQL 18.7`) diverged silently (`Node A=('A','MM_NODE_B')` vs `Node B=('F','MM_INITIAL')`).
- **Root Cause:** (1) Parameterized `psycopg` v3 queries require `%%` to escape the `pg_trgm` `%` operator (`WHERE enseigne_recherche %% %s`). (2) Native PostgreSQL 18 logical replication with `origin=none` applies bidirectional streams independently without deterministic last-writer-wins (LWW) or column-level CRDT conflict resolution.
- **Resolution:** Fixed `mm_probe.py:702` to `WHERE enseigne_recherche %% %s` and empirically classified `pg18-native-birep` as `INCOMPATIBLE_WITH_SIRENE_3NF` on `P3`, validating `mm_probe.py`'s ability to disqualify unsafe active-active setups before production adoption.

## Implemented Improvements (IMP)

- **IMP-001:** Implemented unified Parquet (`pyarrow`) and `.csv.zip` / `.csv.gz` streaming transforms (`sirene_etl.transforms`) with header whitespace stripping, `[ND]` scrubbing, and pure-Python EPSG:2154 Lambert-93 to WGS84 conversion.
- **IMP-002:** Implemented secondary index drop/rebuild orchestration around `psycopg` v3 `COPY FROM STDIN` temporary staging tables (`sirene_etl.db`, `sirene_etl.full_import`) plus `pg_trgm` GIN indexes for fast fuzzy search.
- **IMP-003:** Implemented `tenacity`-backed exponential-backoff streaming downloads into `.part` files with on-the-fly SHA-256 verification and PostgreSQL advisory locking (`pg_try_advisory_lock`) to guarantee single-writer safety.
- **IMP-004:** Added self-contained interactive HTML5 reference (`documentation/sirene_documentation.html`, inline SVG architecture/ER diagrams, 13-table explorer, filterable 15-query copy-ready catalog) paired with bilingual Markdown guides (`documentation/en/sirene_platform.md`, `documentation/fr/sirene_platform.md`), 15-query `sirene/sql/03_sample_queries.sql`, and automated structural/link tests (`sirene/tests/test_documentation_page.py`).
- **IMP-005:** Added `sirene/mm_probe.py` (`sirene_etl.mm_probe`) and 2-node `sirene/docker-compose.pg18-birep.yml` lab delivering a 5-probe multi-master qualification scorecard (`P1_DDL_COMPAT`..`P5_BULK_COPY_REPLICATION_LAG`) with staggered sequences, `origin=none` loop protection, and P3-last ordering.
- **IMP-006:** Added deterministic zero-PII synthetic dataset generator (`sirene/scripts/generate_synthetic_dataset.py`, `seed=20261120`), direct `psql` SQL dumps (`sirene/load_sirene.sql`, `sirene/load_sirene_db.sh`, `sirene/data/sql/01..04_*.sql`), SHA-256 checksum suite (`sirene/test_sirene_sha2.sql`), offline ZSTD Parquet/delta fixtures (`sirene/data/parquet/`, `sirene/data/delta/`), and `.gitattributes` LF normalization.
- **IMP-007:** Added Diataxis 4-quadrant documentation (`docs/01-tutorials/`, ASD-STE100 Issue 9 `docs/02-how-to-guides/`, `docs/03-reference/`, `docs/04-explanation/`), `scripts/mkdocs_hooks.py` virtual doc/HTML mounting and legacy link rewriting, `scripts/build_versioned_docs.py` sparse `git archive` builder (avoiding 168 MB `employees/` dataset snapshots across releases `v1.9.0+` and `master`), and SHA-pinned GitHub Actions CI/CD workflows deploying to IONOS (`test-db.lightpath.fr`).

## Approved Next Enhancements (APP)

- **APP-001:** Enforce monotonic `date_dernier_traitement` upserts (`IS DISTINCT FROM` + timestamp guard) and record every establishment administrative closure (`'A' -> 'F'`) in `etablissements_historique_etat`.
- **APP-002:** Automatically register unseen historical INSEE COG commune codes, foreign country codes, juridical categories, and obsolete NAF codes (`ensure_missing_referential_codes`) before fact-table merges so 3NF foreign keys never fail.
- **APP-003:** Isolate the long-running `sirene-watcher` service under the Docker Compose `daemon` profile so offline builds and integration test runs never spawn background network polling.

## Future Evolution Ideas (IDEA)

- **IDEA-001:** Enrich `personnes` and `roles_entreprises` from the INPI/RNE corporate officers and beneficial owners API beyond Sirene sole proprietors.
- **IDEA-002:** Add optional PostGIS `GEOGRAPHY(POINT, 4326)` spatial indexing alongside WGS84 `longitude`/`latitude` columns for radius-based establishment analytics.
- **IDEA-003:** Ingest INSEE `StockEtablissementLiensSuccession` datasets to build an establishment transfer and predecessor/successor lineage graph.
- **IDEA-004:** Add an automated PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` benchmark exporter feeding empirical execution timings into `documentation/sirene_documentation.html` at full national Sirene scale.
