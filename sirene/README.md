# Sirene PostgreSQL 3NF ETL Platform (`sirene/`)

Production-grade Python 3.12 and PostgreSQL 18 pipeline to ingest, normalize (3NF), enrich, synchronize, and multi-master-qualify the French INSEE Sirene business registry from `data.gouv.fr` Parquet and zipped CSV resources.

## Documentation

- [Interactive HTML Reference](../documentation/sirene_documentation.html) — Visual ER diagram, 13-table 3NF schema & index explorer, ETL script/CLI guide, and filterable 15-query SQL catalog.
- [Technical Platform Guide (English)](../documentation/en/sirene_platform.md) — Architecture, Mermaid ER diagram, full data dictionary, CLI/Docker operations, and 15 SQL queries.
- [Technical Platform Guide (French)](../documentation/fr/sirene_platform.md) — French translation covering the 3NF data model, ETL scripts, Docker workflow, and 15 SQL queries.

## Architecture

```mermaid
flowchart LR
    DG["data.gouv.fr Dataset API"] -->|"HTTPS / Tenacity Retries"| DL["downloader.py (.part + SHA-256)"]
    INSEE["INSEE COG & NAF Referentials"] -->|"2026 CSV / Parquet"| REF["referentials.py (3NF Lookup + Sentinels)"]
    DL -->|"Parquet / .csv.zip"| TR["transforms.py ([ND] Scrub + EPSG:2154 -> WGS84)"]
    TR -->|"COPY FROM STDIN"| PG["PostgreSQL 18 (3NF + pg_trgm GIN)"]
    REF --> PG
    WATCH["watcher.py (Daemon / --once)"] -->|"Polls & Dispatches"| FULL["full_import.py"]
    WATCH -->|"Polls & Dispatches"| INC["incremental_import.py"]
    FULL --> PG
    INC -->|"Monotonic Guard + A->F History"| PG
```

## Directory Layout

- `sirene/sql/01_schema_3nf.sql`: Idempotent PostgreSQL 18 DDL (`pg_trgm` extension, 7 referential tables with sentinels, `unites_legales`, `etablissements`, `etablissements_historique_etat`, `personnes`, `roles_entreprises`, and `etl_logs`).
- `sirene/sql/02_indexes.sql`: B-Tree indexes on foreign keys and selective filters, partial composite active-establishment index, and three `pg_trgm` GIN indexes (`fastupdate = on`).
- `sirene/sql/03_sample_queries.sql`: Fifteen read-only analytical, spatial, governance, fuzzy-search, quality-audit, and ETL freshness queries.
- `sirene/src/sirene_etl/`: Core ETL library (`config`, `logging_utils`, `db`, `downloader`, `referentials`, `transforms`, `full_import`, `incremental_import`, `watcher`, `mm_probe`).
- `sirene/full_import.py`, `sirene/incremental_import.py`, `sirene/watcher.py`, `sirene/mm_probe.py`: CLI entrypoints.
- `sirene/docker-compose.yml` & `sirene/docker-compose.pg18-birep.yml`: Single-node PostgreSQL 18 bulk stack (`/var/lib/postgresql` mount) and 2-node logical bidirectional replication lab.
- `sirene/tests/`: Unit, live PostgreSQL 18 integration, multi-master probe, SQL validation, and governance compliance `pytest` suite.

## Quickstart (Docker Compose & Makefile)

Copy `sirene/.env.example` to `sirene/.env` if you need to override defaults (uses ephemeral lab credential `pg_sirene_ephemeral` and loopback host port `15432` by default to avoid local port `5432` collisions):

```bash
cp sirene/.env.example sirene/.env
```

From the repository root:

```bash
# 1. Start PostgreSQL 18 (mounts sirene_pgdata at /var/lib/postgresql; initializes sirene/sql/)
make sirene-up

# 2. Build and run the full pytest suite (unit + live PostgreSQL 18 + governance)
make sirene-test

# 3. Run an initial bulk import (or pass custom ARGS="--offline-refs --limit-rows 10000")
make sirene-import ARGS="--limit-rows 10000"

# 4. Run an incremental delta synchronization
make sirene-incremental

# 5. Start the autonomous watcher daemon (Compose profile: daemon)
make sirene-watch

# 6. Show documentation entrypoints (interactive HTML & EN/FR Markdown guides)
make sirene-docs

# 7. Stop containers
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
| `POSTGRES_IMAGE` | `postgres:18-bookworm` | PostgreSQL container image tag |
| `POSTGRES_HOST_PORT` | `15432` | Host loopback port mapped to container `5432` |
| `MM_NODE_A_PORT` | `15441` | Multi-master lab Node A host loopback port |
| `MM_NODE_B_PORT` | `15442` | Multi-master lab Node B host loopback port |
| `DATABASE_URL` | `postgresql://sirene:pg_sirene_ephemeral@localhost:15432/sirene` | SQL DSN used by Python ETL modules |
| `STAGING_DIR` | `./staging` | Local download staging directory |
| `BATCH_SIZE` | `50000` | Rows per `COPY FROM STDIN` batch |
| `WATCHER_INTERVAL_SECONDS` | `3600` | Poll interval in daemon mode |
| `PREFERRED_FORMAT` | `parquet` | Preferred `data.gouv.fr` resource format |
| `LOG_LEVEL` | `INFO` | Structured JSON logger verbosity |

## Multi-Master Qualification (`mm_probe.py`)

Qualify PostgreSQL 18 native bidirectional logical replication (`origin=none`) or external candidates (pgEdge Spock, Citus, YugabyteDB, CockroachDB) against the 3NF Sirene schema via 5 automated probes (`P1_DDL_COMPAT`, `P2_SEQUENCE_SPLIT_BRAIN`, `P3_CONCURRENT_SIRET_UPSERT`, `P4_CROSS_NODE_FK_CAUSALITY`, `P5_BULK_COPY_REPLICATION_LAG`):

```bash
# Start 2-node PostgreSQL 18 logical replication lab (ports 15441/15442)
make sirene-mm-up

# Configure native bidirectional replication & execute P1..P5 qualification scorecard
make sirene-mm-probe

# Point at any external multi-master candidate DSN pair directly
python sirene/mm_probe.py --dsn-a "$MM_DSN_A" --dsn-b "$MM_DSN_B" --candidate-name custom-mm

# Tear down lab containers and /var/lib/postgresql volumes
make sirene-mm-down
```

## Sample Analytical Queries

Execute all 15 reference queries in `sirene/sql/03_sample_queries.sql` against the running container:

```bash
docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
  psql -U sirene -d sirene < sirene/sql/03_sample_queries.sql
```

Included queries cover exact SIREN/SIRET lookup, active NAF division + officers, unified `pg_trgm` fuzzy search, officer/shareholder portfolios, sole proprietors directory, WGS84 radius/bounding-box geo search, NAF 5-level rollup, regional density & headcount, `PME`/`ETI`/`GE` + ESS/mission breakdown, multi-establishment networks, `'A' -> 'F'` closure churn audit, creation cohorts, foreign establishments, `[ND]` & `HIST` quality audit, and `etl_logs` / `pg_stat_user_tables` operational health. See [sirene_documentation.html](../documentation/sirene_documentation.html) for interactive filtering and copy-ready SQL cards.
