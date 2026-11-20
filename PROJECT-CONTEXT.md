# Project Context

**Project:** `test_db` — Sirene PostgreSQL 3NF ETL Platform (`sirene/`) alongside legacy MariaDB/PostgreSQL employee test suites.

**Purpose:** Ingest, normalize (3NF), deduplicate, continuously synchronize, and multi-master-qualify the French INSEE Sirene registry on PostgreSQL 18.

**Tech Stack:** Python 3.12, `psycopg` v3 (`COPY FROM STDIN`), PyArrow, `httpx`, `tenacity`, `python-dotenv`, PostgreSQL 18 (`pg_trgm`), Docker Compose, `pytest`.

**Current Phase:** Version `1.10.0` (Issue `#8`) — PostgreSQL 18 runtime upgrade (`/var/lib/postgresql` layout), `mm_probe.py` 5-probe multi-master qualification suite, and 2-node bidirectional logical replication lab.

**Hard Constraints:** Strictly English across code, docs, and governance; zero local host paths; zero real credentials or PII; idempotent, monotonically guarded ingestion.

**Definition of Done:** Full Dockerized `pytest` pass covering unit transforms, live PostgreSQL 18 integration, 15 SQL queries, multi-master probe tests, documentation, and governance checks.
