# Project Context

**Project:** `test_db` — Sirene PostgreSQL 3NF ETL Platform (`sirene/`) alongside legacy MariaDB/PostgreSQL employee test suites.

**Purpose:** Ingest, normalize (3NF), deduplicate, continuously synchronize, and multi-master-qualify the French INSEE Sirene registry on PostgreSQL 18, including ready-to-inject synthetic SQL/Parquet datasets.

**Tech Stack:** Python 3.12, `psycopg` v3 (`COPY FROM STDIN`), PyArrow, `httpx`, `tenacity`, `python-dotenv`, PostgreSQL 18 (`pg_trgm`), Docker Compose, `pytest`.

**Current Phase:** Version `1.11.0` (Issue `#10`) — Embedded deterministic synthetic SQL dumps (`15,000` legal units / `30,000` establishments, zero PII), SHA-256 verifier (`test_sirene_sha2.sql`), and offline Parquet/delta sample datasets.

**Hard Constraints:** Strictly English across code, docs, and governance; zero local host paths; zero real credentials or PII; idempotent, monotonically guarded ingestion.

**Definition of Done:** Full Dockerized `pytest` pass plus clean `load_sirene.sql` injection, `test_sirene_sha2.sql` SHA-256 checksum pass, and governance checks.
