# Sirene PostgreSQL 3NF ETL Platform (`sirene/`)

Production-grade Python 3.12 and PostgreSQL 17 pipeline to ingest, normalize (3NF), enrich, and continuously synchronize the French INSEE Sirene business registry from `data.gouv.fr` Parquet and zipped CSV resources.

## Architecture

```mermaid
flowchart LR
    DG["data.gouv.fr Dataset API"] -->|"HTTPS / Tenacity Retries"| DL["downloader.py (.part + SHA-256)"]
    INSEE["INSEE COG & NAF Referentials"] -->|"2026 CSV / Parquet"| REF["referentials.py (3NF Lookup + Sentinels)"]
    DL -->|"Parquet / .csv.zip"| TR["transforms.py ([ND] Scrub + EPSG:2154 -> WGS84)"]
    TR -->|"COPY FROM STDIN"| PG["PostgreSQL 17 (3NF + pg_trgm GIN)"]
    REF --> PG
    WATCH["watcher.py (Daemon / --once)"] -->|"Polls & Dispatches"| FULL["full_import.py"]
    WATCH -->|"Polls & Dispatches"| INC["incremental_import.py"]
    FULL --> PG
    INC -->|"Monotonic Guard + A->F History"| PG
```

## Directory Layout

- `sirene/sql/01_schema_3nf.sql`: Idempotent PostgreSQL 17 DDL (`pg_trgm` extension, 7 referential tables with sentinels, `unites_legales`, `etablissements`, `etablissements_historique_etat`, `personnes`, `roles_entreprises`, and `etl_logs`).
- `sirene/sql/02_indexes.sql`: B-Tree indexes on foreign keys and selective filters, partial composite active-establishment index, and three `pg_trgm` GIN indexes (`fastupdate = on`).
- `sirene/sql/03_sample_queries.sql`: Six read-only analytical, fuzzy-search, regional density, closure-audit, and ETL freshness queries.
- `sirene/src/sirene_etl/`: Core ETL library (`config`, `logging_utils`, `db`, `downloader`, `referentials`, `transforms`, `full_import`, `incremental_import`, `watcher`).
- `sirene/full_import.py`, `sirene/incremental_import.py`, `sirene/watcher.py`: CLI entrypoints.
- `sirene/tests/`: Unit, live PostgreSQL 17 integration, SQL validation, and governance compliance `pytest` suite.

## Quickstart (Docker Compose & Makefile)

Copy `sirene/.env.example` to `sirene/.env` if you need to override defaults (uses ephemeral lab credential `pg_sirene_ephemeral` and loopback host port `15432` by default to avoid local port `5432` collisions):

```bash
cp sirene/.env.example sirene/.env
```

From the repository root:

```bash
# 1. Start PostgreSQL 17 (tuned for bulk ingestion; initializes sirene/sql/ automatically)
make sirene-up

# 2. Build and run the full pytest suite (unit + live PostgreSQL 17 + governance)
make sirene-test

# 3. Run an initial bulk import (or pass custom ARGS="--offline-refs --limit-rows 10000")
make sirene-import ARGS="--limit-rows 10000"

# 4. Run an incremental delta synchronization
make sirene-incremental

# 5. Start the autonomous watcher daemon (Compose profile: daemon)
make sirene-watch

# 6. Stop containers
make sirene-down
```

Direct `docker compose` equivalents from `sirene/`:

```bash
docker compose -f sirene/docker-compose.yml up -d sirene-postgres
docker compose -f sirene/docker-compose.yml build sirene-etl
docker compose -f sirene/docker-compose.yml run --rm sirene-etl python watcher.py --once
docker compose -f sirene/docker-compose.yml --profile daemon up -d sirene-watcher
```

## Configuration Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `POSTGRES_USER` | `sirene` | PostgreSQL role name |
| `POSTGRES_PASSWORD` | `pg_sirene_ephemeral` | Ephemeral local PoC password |
| `POSTGRES_DB` | `sirene` | Target database name |
| `POSTGRES_HOST_PORT` | `15432` | Host loopback port mapped to container `5432` |
| `DATABASE_URL` | `postgresql://sirene:pg_sirene_ephemeral@localhost:15432/sirene` | SQL DSN used by Python ETL modules |
| `STAGING_DIR` | `./staging` | Local download staging directory |
| `BATCH_SIZE` | `50000` | Rows per `COPY FROM STDIN` batch |
| `WATCHER_INTERVAL_SECONDS` | `3600` | Poll interval in daemon mode |
| `PREFERRED_FORMAT` | `parquet` | Preferred `data.gouv.fr` resource format |
| `LOG_LEVEL` | `INFO` | Structured JSON logger verbosity |

## Sample Analytical Queries

Execute all six reference queries in `sirene/sql/03_sample_queries.sql` against the running container:

```bash
docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
  psql -U sirene -d sirene < sirene/sql/03_sample_queries.sql
```

Included queries cover:
1. Active establishments by NAF division in target regions joined with corporate officers and sole proprietors.
2. Fuzzy `pg_trgm` (`%` and `similarity()`) search across `unites_legales`, `etablissements`, and `personnes`.
3. Regional and departmental active/closed establishment density with minimum headcount aggregation.
4. Establishment administrative closure audit (`etablissements_historique_etat` `'A' -> 'F'` transitions).
5. Enterprise size category (`PME`, `ETI`, `GE`), legal category, ESS, and mission-driven company breakdown.
6. ETL run freshness, SHA-256 checksum audit, and throughput summary from `etl_logs`.
