# Run Sirene Full and Incremental ETL

Refer to
[Datasets and Schemas Matrix](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)
and
[CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
before you execute ETL runs.

## Prerequisites

1. Start PostgreSQL 18 cleanly with `make sirene-up`.
2. Confirm that `sirene-postgres` is healthy on `127.0.0.1:15432`.
3. For remote INSEE syncs, confirm outbound HTTPS access to `data.gouv.fr` and `insee.fr`.

## Safety Instructions

**CAUTION:** Do not start two concurrent `full_import.py` or `incremental_import.py` processes on one database.
PostgreSQL advisory lock `84729101` rejects the second writer immediately.

**CAUTION:** Pass `--force` only when you intentionally override `etl_logs` SHA-256 deduplication.
Default runs skip files whose SHA-256 checksum matches a previous `SUCCESS` row.

## Procedure

1. Run a bounded full-stock import from `data.gouv.fr` to verify connectivity and schema load:

   ```bash
   make sirene-import ARGS="--limit-rows 10000"
   ```

2. For offline environments, execute the embedded synthetic Parquet full import instead:

   ```bash
   make sirene-import-sample
   ```

3. Run a full-stock import from local Parquet or zipped CSV files with local referentials:

   ```bash
   docker compose -f sirene/docker-compose.yml run --rm sirene-etl \
     python full_import.py --ul-file /app/data/parquet/StockUniteLegale_synthetic.parquet \
     --etab-file /app/data/parquet/StockEtablissement_synthetic.parquet --offline-refs
   ```

4. Execute an incremental delta synchronization against `data.gouv.fr` or local delta files:

   ```bash
   make sirene-incremental
   ```

5. For offline delta validation, run the embedded synthetic delta Parquet pipeline:

   ```bash
   make sirene-incremental-sample
   ```

6. Run one bounded watcher check-and-sync cycle before you enable daemon mode:

   ```bash
   docker compose -f sirene/docker-compose.yml run --rm sirene-etl python watcher.py --once --offline-refs
   ```

7. Start the continuous watcher daemon with profile `daemon` when ready:

   ```bash
   make sirene-watch
   ```

**NOTE:** `incremental_import.py` commits its preamble before `with conn.transaction():`.
This sequence prevents implicit `INTRANS` savepoint rollbacks and preserves monotonic updates.

## Verification

1. Inspect recent `etl_logs` rows and confirm `status = 'SUCCESS'` for both entities:

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT id, run_type, entity_type, status, rows_processed FROM etl_logs ORDER BY id DESC LIMIT 10;"
   ```

2. Confirm `'A' -> 'F'` administrative closures appear in `etablissements_historique_etat`:

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT COUNT(*) FROM etablissements_historique_etat;"
   ```

3. Confirm all `pg_trgm` GIN and B-Tree indexes exist in `pg_indexes`.

## Rollback

If an ETL run imports invalid data or stalls mid-batch, do these steps:

1. Stop the `sirene-watcher` daemon if active:

   ```bash
   make sirene-down
   ```

2. Start PostgreSQL 18 alone with `make sirene-up`.
3. If `full_import.py` exited before index rebuild, apply `sirene/sql/02_indexes.sql` manually:

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -v ON_ERROR_STOP=1 -f /sirene/sql/02_indexes.sql
   ```

4. Reload the deterministic synthetic baseline with `make sirene-inject` or re-run `full_import.py --force`.

## Related Documentation

- Reference: [Datasets and Schemas Matrix](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)
- Reference: [CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
- Explanation: [Platform and ETL Architecture](../../04-explanation/architecture-overview/platform-and-etl-architecture.md)
- Explanation:
  [ADR-001: PostgreSQL 18 3NF Sirene ETL and MM Qualification](../../04-explanation/design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md)
