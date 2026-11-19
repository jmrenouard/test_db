# Project Context

**Project:** `test_db` — Sirene PostgreSQL 3NF ETL Platform (`sirene/`) alongside legacy MariaDB/PostgreSQL employee test suites.

**Purpose:** Ingest, normalize (3NF), deduplicate, and continuously synchronize the French INSEE Sirene business registry from `data.gouv.fr` Parquet/CSV datasets into PostgreSQL 17.

**Tech Stack:** Python 3.12, `psycopg` v3 (`COPY FROM STDIN`), PyArrow, `httpx`, `tenacity`, `python-dotenv`, PostgreSQL 17 (`pg_trgm`), Docker Compose, `pytest`.

**Current Phase:** Version `1.9.0` (Issue `#4`) — Implementing the 3NF schema, initial bulk and incremental loaders, autonomous dataset watcher, and engineering governance registers.

**Hard Constraints:** Strictly English across code, docs, and governance; zero local host paths; zero real credentials or PII; idempotent, monotonically guarded ingestion.

**Definition of Done:** Full Dockerized `pytest` pass covering unit transforms, live PostgreSQL 17 integration, analytical SQL queries, and governance checks.
