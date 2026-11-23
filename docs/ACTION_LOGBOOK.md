# Engineering Action Logbook

Living operational register tracking roadmap milestones, active engineering tasks, and verified deliverables for `test_db` and the `sirene/` PostgreSQL 3NF ETL platform.

## Strategic Roadmap

| Milestone | Scope | Target Version | Status |
| :--- | :--- | :--- | :--- |
| M1 | PostgreSQL 17 3NF schema, B-Tree & `pg_trgm` GIN indexes, analytical SQL queries | `1.9.0` | `COMPLETED` |
| M2 | Streaming downloader, SHA-256 integrity verification, and INSEE COG/NAF/CJ referentials | `1.9.0` | `COMPLETED` |
| M3 | High-throughput `COPY FROM STDIN` full importer and monotonic incremental upsert loader | `1.9.0` | `COMPLETED` |
| M4 | Autonomous `data.gouv.fr` watcher daemon and Docker Compose production-ready stack | `1.9.0` | `COMPLETED` |
| M5 | Automated unit, live PostgreSQL 17 integration, query, and governance `pytest` verification | `1.9.0` | `COMPLETED` |
| M6 | Interactive HTML and bilingual Markdown documentation with 15-query PostgreSQL 17 catalog | `1.9.1` | `COMPLETED` |
| M7 | PostgreSQL 18 upgrade (`/var/lib/postgresql` layout) and `mm_probe.py` multi-master qualification lab | `1.10.0` | `COMPLETED` |
| M8 | Deterministic synthetic SQL dumps (`15k` UL / `30k` SIRET), SHA-256 suite, and offline Parquet/delta samples | `1.11.0` | `COMPLETED` |
| M9 | Diataxis 4-quadrant documentation, versioned MkDocs Material site (`master` + `v1.9.0+`), and IONOS SFTP CI/CD | `1.12.0` | `COMPLETED` |

## Ongoing Actions

*None*

## Completed Actions

| ID | Issue / PR | Completed | Summary & Verification Evidence |
| :--- | :--- | :--- | :--- |
| `ACT-005` | `#12` / `docs/issue-12-mkdocs-material-diataxis-publish` | `2026-11-23` | `COMPLETED` — Delivered 4-quadrant Diataxis documentation (`docs/01-tutorials/`, ASD-STE100 Issue 9 `docs/02-how-to-guides/`, `docs/03-reference/`, `docs/04-explanation/` with `adr-001` and `adr-002`, and `docs/index.md`), MkDocs Material configuration (`mkdocs.yml`, `docs/stylesheets/extra.css`, `docs/javascripts/katex.js`, SVG branding), `scripts/mkdocs_hooks.py` (virtual mounting of bilingual guides and `sirene_documentation.html`, historical tag fallbacks), `scripts/build_versioned_docs.py` (sparse `git archive` excluding `employees/`, `master` + `v1.9.0+` releases, `versions.json`, `.htaccess`), SHA-pinned CI/CD workflows deploying via SFTP to `test-db.lightpath.fr`, GitHub repository secrets, `README.md`/`README_fr.md`/`Makefile` updates, and `tests/test_diataxis_documentation.py` + `tests/test_mkdocs_publishing.py` (`1.12.0`). Verified cleanly: `diataxis_check.py docs --strict --check-ste --lang en` (`0 error(s), 0 warning(s)` across 24 files), `pytest` docs/publishing/governance/page suites (**34 passed in 13.04s**), Dockerized PostgreSQL 18 Sirene suite (**61 passed, 1 skipped in 3.93s**), `mkdocs build --strict` (exit `0`), and `build_versioned_docs.py` across `master` and `v1.9.0..v1.11.0` (exit `0`). |
| `ACT-004` | `#10` / `feat/sirene-sql-data-dumps` | `2026-11-20` | `COMPLETED` — Delivered deterministic zero-PII synthetic SQL dumps (`sirene/load_sirene.sql`, `sirene/load_sirene_db.sh`, `sirene/data/sql/01..04_*.sql`), SHA-256 verifier (`sirene/test_sirene_sha2.sql`), offline ZSTD Parquet/delta samples, Compose/Makefile/doc wiring, and `test_direct_sql_and_sample_data.py` (`1.11.0`). Verified inside Docker PostgreSQL 18: `load_sirene.sql` + `bash load_sirene_db.sh` + `test_sirene_sha2.sql` `12/12` `CRC | OK` / `count | OK`, `full_import.py` (`15,000` UL / `30,000` SIRET / `0` orphan SIRENs), `incremental_import.py` (`250` UL / `500` SIRET / `150` state transitions), and `pytest -v` **61 passed, 1 skipped in 3.08s**. |
| `ACT-003` | `#8` / `feat/sirene-pg18-mm-probe` | `2026-11-20` | `COMPLETED` — Upgraded Docker runtime to `postgres:18-bookworm` (`/var/lib/postgresql` volume layout), implemented `mm_probe.py` and `sirene/docker-compose.pg18-birep.yml`, added `test_mm_probe.py`, and updated documentation & governance (`1.10.0`). Verified across both PG `18.7` stacks: standalone PG `18.7` (`58 passed, 1 skipped in 2.14s`, `03_sample_queries.sql` 15/15 exited `0`), live 2-node PG `18.7` bidirectional lab (`pytest -v tests/test_mm_probe.py`: `6 passed in 3.44s`), and empirical `pg18-native-birep` scorecard (`INCOMPATIBLE_WITH_SIRENE_3NF` due to `P3_CONCURRENT_SIRET_UPSERT` split-brain divergence). |
| `ACT-002` | `#6` / `docs/sirene-model-scripts-queries` | `2026-11-19` | `COMPLETED` — Delivered self-contained `documentation/sirene_documentation.html`, bilingual `documentation/{en,fr}/sirene_platform.md`, 15-query `sirene/sql/03_sample_queries.sql`, `Makefile` `sirene-docs`, `sirene/tests/test_documentation_page.py`, and root/README links (`1.9.1`). Verified inside Docker (`sirene-postgres` + `sirene-etl`): `pytest -v` **52 passed in 3.33s** (5 documentation, 6 governance, 2 live PostgreSQL 17 integration, 39 unit), `03_sample_queries.sql` 15/15 queries exited 0 via `psql -v ON_ERROR_STOP=1`, and clean `down -v`. |
| `ACT-001` | `#4` / `feat/sirene-postgresql-etl` | `2026-11-19` | `COMPLETED` — Implemented PostgreSQL 3NF schema (`sirene/sql/`), `sirene_etl` package (`full_import`, `incremental_import`, `watcher`), Docker stack, and governance registers. Verified end-to-end inside Docker (`sirene-postgres` + `sirene-etl`): `pytest -v` **47 passed** (39 unit, 2 live PostgreSQL 17 integration, 6 governance), `03_sample_queries.sql` 6/6 queries exited 0 via `psql -v ON_ERROR_STOP=1`, and clean `docker compose -f sirene/docker-compose.yml down -v`. |
| `ACT-000` | `1.8.1` baseline | `2026-08-01` | Established synthetic employee data injection (`scripts/inject_fake_employees.py`) and SHA-256 test verification baseline prior to Sirene 3NF ETL integration. |
