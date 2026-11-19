# Project Context

**Project:** `test_db` — Sirene PostgreSQL 3NF ETL Platform (`sirene/`) alongside legacy MariaDB/PostgreSQL employee test suites.

**Purpose:** Ingest, normalize (3NF), deduplicate, and continuously synchronize the French INSEE Sirene business registry from `data.gouv.fr` Parquet/CSV datasets into PostgreSQL 17.

**Tech Stack:** Python 3.12, `psycopg` v3 (`COPY FROM STDIN`), PyArrow, `httpx`, `tenacity`, `python-dotenv`, PostgreSQL 17 (`pg_trgm`), Docker Compose, `pytest`.

**Current Phase:** Version `1.9.1` (Issue `#6`) — Publishing interactive HTML and bilingual Markdown technical documentation for the 3NF model, ETL scripts, Docker operations, and 15-query PostgreSQL 17 catalog.

**Hard Constraints:** Strictly English across code, docs, and governance; zero local host paths; zero real credentials or PII; idempotent, monotonically guarded ingestion.

**Definition of Done:** Full Dockerized `pytest` pass covering unit transforms, live PostgreSQL 17 integration, 15 SQL queries, documentation validation, and governance checks.
