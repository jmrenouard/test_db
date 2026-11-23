# Tutorial 2: Sirene PostgreSQL 18 3NF Offline Lab

> **Learning Goal:** Boot an isolated PostgreSQL 18 container (`sirene-postgres`), inject the zero-PII synthetic
> INSEE Sirene dataset (`15,000` legal units and `30,000` establishments) via direct `psql`, verify 12-table SHA-256
> checksums, and execute offline full and incremental Parquet ETL pipelines.

> [!WARNING]
> **Isolated Local Docker Lab Only:** `sirene/docker-compose.yml` binds `127.0.0.1:15432` using the ephemeral lab
> credential `pg_sirene_ephemeral` and loads fabricated `9xxxxxxxx` SIREN records. Never expose ephemeral credentials on
> shared networks.

---

## Prerequisites

Make sure your environment meets these requirements:

- Docker Engine `24+` with Docker Compose v2 (`docker compose`)
- GNU `make` and cloned `test_db` repository (`sirene/` directory present)
- Localhost TCP port `15432` free on `127.0.0.1`

Confirm Docker Compose parses the Sirene stack cleanly:

```bash
docker compose -f sirene/docker-compose.yml config --services
```

Expected output:

```text
sirene-postgres
sirene-etl
```

---

## What You Will Build

By the end of this tutorial, you will have:

1. Started PostgreSQL 18 (`postgres:18-bookworm`) with `/var/lib/postgresql` persistent storage (`make sirene-up`).
2. Loaded the 13-table 3NF schema and synthetic SQL dumps with zero Python dependencies (`make sirene-inject`).
3. Verified all 12 populated tables against deterministic SHA-256 digests (`make sirene-verify`).
4. Executed the offline Python bulk Parquet importer (`make sirene-import-sample`) and incremental delta pipeline
   (`make sirene-incremental-sample`).
5. Inspected `etablissements_historique_etat` and `etl_logs`, then torn down the Compose stack (`make sirene-down`).

---

## Step 1: Start the Sirene PostgreSQL 18 Container

Start `sirene-postgres` in detached mode and verify health status:

```bash
make sirene-up
docker compose -f sirene/docker-compose.yml ps
```

Expected output:

```text
🐘 Starting Sirene PostgreSQL 18 container...
...
NAME                      IMAGE                  STATUS                   PORTS
sirene-sirene-postgres-1  postgres:18-bookworm   Up ... (healthy)         127.0.0.1:15432->5432/tcp
```

---

## Step 2: Inject the Synthetic 3NF SQL Dumps

Run `make sirene-inject` to execute `sirene/load_sirene.sql` inside `sirene-postgres` via `psql`:

```bash
make sirene-inject
```

Expected output:

```text
💉 Injecting synthetic Sirene SQL dumps into sirene-postgres...
              status
-----------------------------------
 CREATING SIRENE 3NF SCHEMA
...
 TRUNCATING TABLES FOR IDEMPOTENT LOAD
...
 DROPPING SECONDARY INDEXES BEFORE BULK COPY
...
 LOADING SYNTHETIC REFERENTIALS
...
 LOADING SYNTHETIC LEGAL UNITS (15,000)
...
 LOADING SYNTHETIC ESTABLISHMENTS (30,000)
...
 LOADING GOVERNANCE, HISTORY, AND ETL LOGS
...
 REBUILDING SECONDARY AND GIN INDEXES
...
 ANALYZING TABLES
...
 SIRENE DATABASE LOAD COMPLETE
```

---

## Step 3: Verify Row Counts and SHA-256 Checksums

Run `make sirene-verify` to execute `sirene/test_sirene_sha2.sql` across all 7 referential tables and 5 domain/audit
tables:

```bash
make sirene-verify
```

Expected output (summary tail):

```text
           table_name           | records_match | crc_match
--------------------------------+---------------+-----------
 etablissements                 | OK            | OK
 etablissements_historique_etat | OK            | OK
 personnes                      | OK            | OK
 ref_categories_juridiques      | OK            | OK
 ref_communes                   | OK            | OK
 ref_departements               | OK            | OK
 ref_naf                        | OK            | OK
 ref_pays                       | OK            | OK
 ref_regions                    | OK            | OK
 ref_tranches_effectifs         | OK            | OK
 roles_entreprises              | OK            | OK
 unites_legales                 | OK            | OK
(12 rows)

 summary | result
---------+--------
 CRC     | OK
 count   | OK
(2 rows)
```

---

## Step 4: Run the Offline Parquet Bulk Importer

Now test the Python 3.12 ETL pipeline (`sirene/full_import.py`) inside the `sirene-etl` container using the embedded
ZSTD-compressed Parquet files under `sirene/data/parquet/` (`--offline-refs --force`):

```bash
make sirene-import-sample
```

Expected output (key structured JSON log events):

```text
📥 Running full_import.py against embedded offline synthetic Parquet files...
... "event": "indexes_dropped" ...
... "event": "full_import_completed", "stats": {"ul_processed": 15000, ..., "etab_processed": 30000, ...} ...
```

Notice that `full_import.py` drops secondary indexes on managed tables, streams rows with `COPY FROM STDIN`, rebuilds
B-Tree and `pg_trgm` GIN indexes from `sirene/sql/02_indexes.sql`, and runs `ANALYZE`.

---

## Step 5: Apply the Offline Incremental Delta Pipeline

Run `make sirene-incremental-sample` to process `DeltaUniteLegale_synthetic.parquet` (`250` rows) and
`DeltaEtablissement_synthetic.parquet` (`500` rows):

```bash
make sirene-incremental-sample
```

Expected output (summary event):

```text
🔄 Running incremental_import.py against embedded synthetic delta Parquet files...
... "event": "incremental_import_completed", "stats": {"ul_processed": 250, ..., "etab_processed": 500, ..., "state_transitions": 150, ...} ...
```

Inspect the recorded `'A' -> 'F'` administrative state transitions and `etl_logs` audit entries:

```bash
docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
  psql -U sirene -d sirene -c "SELECT COUNT(*) AS history_rows FROM etablissements_historique_etat;"
docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
  psql -U sirene -d sirene -c "SELECT run_type, entity_type, status, rows_processed FROM etl_logs ORDER BY id;"
```

---

## Step 6: Stop the Sirene Docker Compose Stack

Stop the Sirene containers cleanly when finished:

```bash
make sirene-down
```

Expected output:

```text
🛑 Stopping Sirene Docker Compose stack...
```

---

## Next Steps

- Continue to [Tutorial 3: Concurrency and Benchmarking Lab](03-concurrency-and-benchmarking-lab.md)
- Execute production ETL and multi-master procedures:
  [How-To Guides](../02-how-to-guides/index.md) and
  [Run Sirene Full and Incremental ETL](../02-how-to-guides/operations/run-sirene-full-and-incremental-etl.md)
- Inspect the 13-table 3NF schema, GIN indexes, and SHA-256 baseline:
  [Datasets and Schemas Matrix](../03-reference/architecture-specs/datasets-and-schemas-matrix.md) and
  [Reference](../03-reference/index.md)
- Understand why PostgreSQL 18 `COPY` index drop/rebuild and monotonic upserts are designed this way:
  [ADR-001: PostgreSQL 18 3NF Sirene ETL &amp; MM Qualification](../04-explanation/design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md) and
  [Explanation](../04-explanation/index.md)
