# Remediate Deadlocks, Gap Locks, and ETL Drift

Refer to the
[Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
before you execute this runbook.

## Prerequisites

1. Confirm terminal access to the Docker host for `mariadb-11-8` and `sirene-postgres`.
2. Collect the exact failed `make` target, container log snippet, or `etl_logs` error string.
3. Confirm `psql` or `mariadb` client access inside the affected container.

## Safety Instructions

**CAUTION:** Do not kill `sirene-postgres` with `SIGKILL` during an active bulk import or index build.
Abrupt container termination can leave partial temporary tables or unindexed relations.

**CAUTION:** Do not route concurrent writes for one SIRET across two `origin=none` PostgreSQL nodes.
Concurrent updates cause silent split-brain divergence on `etablissements`.

## Procedure

1. If MariaDB deadlocks spike, enable full deadlock output and read container logs:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -e "SET GLOBAL innodb_print_all_deadlocks = 1;"
   docker logs --tail 100 mariadb-11-8
   ```

2. If InnoDB transactions stall on gap locks under `REPEATABLE READ`, examine active waits:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -e "SHOW ENGINE INNODB STATUS\G"
   ```

3. Shorten lock duration in SQL workloads or execute `teardown.sql` for stuck simulation tables.
4. If PostgreSQL startup fails on host port `5432`, set `POSTGRES_HOST_PORT=15432` in `sirene/.env`.
5. If `postgres:18-bookworm` fails initialization, update Compose volume mounts to `/var/lib/postgresql`.
6. If another ETL process holds advisory lock `84729101`, inspect active backend sessions:

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT pid, state, query FROM pg_stat_activity WHERE datname = 'sirene';"
   ```

7. Wait for active ETL jobs to finish, or terminate only verified orphan ETL PIDs.
8. If `incremental_import.py` persists zero rows, confirm `conn.commit()` precedes `with conn.transaction():`.
9. If `drop_secondary_indexes` stalls on `AccessShareLock`, commit idle read sessions or set `autocommit=True`.
10. If `pg_trgm` parameterized queries raise `incomplete placeholder`, escape `%` as `%%` when parameters exist.
11. If INSEE CSV files fail on extra header spaces or `[ND]` cells, check `sirene_etl.transforms` normalization.
12. If `P3` probe fails with split-brain divergence, stop the second writer and switch to single-primary writes.

**NOTE:** `sirene/src/sirene_etl/db.py` holds advisory lock `84729101` per ETL session.
Lock release happens automatically when the PostgreSQL session closes.

## Verification

1. Run `make verify` and confirm exit code `0` on `mariadb-11-8`.
2. Inspect `etl_logs` in `sirene-postgres` and confirm recent runs report `status = 'SUCCESS'`:

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT id, run_type, status, error_message FROM etl_logs ORDER BY id DESC LIMIT 5;"
   ```

3. Confirm that `pg_locks` shows zero ungranted `AccessShareLock` or `AccessExclusiveLock` waits.

## Rollback

If remediation triggers fresh contention or failed ETL runs, do these steps:

1. Stop the `sirene-watcher` daemon with `make sirene-down`.
2. Stop active benchmark runs and execute `make clean` to remove stale reports.
3. Restart `sirene-postgres` alone via `make sirene-up` and rebuild indexes from `sirene/sql/02_indexes.sql`.
4. Reload baseline synthetic fixtures with `make sirene-inject` or `make inject` before new runs.

## Related Documentation

- Reference: [Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
- Reference: [CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
- Explanation:
  [Concurrency, Lock Mechanics, and Replication Trade-offs](../../04-explanation/deep-dives/concurrency-locking-and-replication-tradeoffs.md)
- Explanation: [Platform and ETL Architecture](../../04-explanation/architecture-overview/platform-and-etl-architecture.md)
