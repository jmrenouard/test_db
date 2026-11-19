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

## Ongoing Actions

*None*

## Completed Actions

| ID | Issue / PR | Completed | Summary & Verification Evidence |
| :--- | :--- | :--- | :--- |
| `ACT-001` | `#4` / `feat/sirene-postgresql-etl` | `2026-11-19` | `COMPLETED` — Implemented PostgreSQL 3NF schema (`sirene/sql/`), `sirene_etl` package (`full_import`, `incremental_import`, `watcher`), Docker stack, and governance registers. Verified end-to-end inside Docker (`sirene-postgres` + `sirene-etl`): `pytest -v` **47 passed** (39 unit, 2 live PostgreSQL 17 integration, 6 governance), `03_sample_queries.sql` 6/6 queries exited 0 via `psql -v ON_ERROR_STOP=1`, and clean `docker compose -f sirene/docker-compose.yml down -v`. |
| `ACT-000` | `1.8.1` baseline | `2026-08-01` | Established synthetic employee data injection (`scripts/inject_fake_employees.py`) and SHA-256 test verification baseline prior to Sirene 3NF ETL integration. |
