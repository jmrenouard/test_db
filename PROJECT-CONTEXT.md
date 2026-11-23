# Project Context

**Project:** `test_db` — Sirene PostgreSQL 3NF ETL Platform (`sirene/`) alongside legacy MariaDB/PostgreSQL employee test suites.

**Purpose:** Ingest, normalize (3NF), deduplicate, continuously synchronize, and multi-master-qualify the French INSEE Sirene registry on PostgreSQL 18, including ready-to-inject synthetic SQL/Parquet datasets.

**Tech Stack:** Python 3.12, `psycopg` v3 (`COPY FROM STDIN`), PyArrow, `httpx`, `tenacity`, `python-dotenv`, PostgreSQL 18 (`pg_trgm`), Docker Compose, `pytest`.

**Current Phase:** Version `1.12.0` (Issue `#12`) — Diataxis 4-quadrant documentation (`docs/`), versioned MkDocs Material publishing (`master` + `v1.9.0+` releases), sparse Git archive builder (`scripts/build_versioned_docs.py`), and IONOS SFTP CI/CD (`https://test-db.lightpath.fr/`).

**Hard Constraints:** Strictly English across governance, code, and GitHub artifacts; ASD-STE100 Issue 9 compliance on `docs/02-how-to-guides/`; zero local host paths; zero real credentials or PII; idempotent ingestion.

**Definition of Done:** Full `diataxis_check.py --strict --check-ste`, `pytest` (Diataxis, MkDocs publishing, governance, documentation, and Dockerized Sirene suite), `mkdocs build --strict`, `build_versioned_docs.py`, and live HTTPS verification on `https://test-db.lightpath.fr/`.
