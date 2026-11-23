# Error, RCA, and Operational Alert Matrix

Consolidated failure taxonomy, root-cause identifiers (`RCA-001`–`RCA-007`), database error codes, probe
classifications, and direct remediation runbook links.

## 1. Recorded Root Cause & Infrastructure Failure Matrix (`docs/RCA_REGISTER.md`)

| Code / Failure | Component | Observable Symptom | Root Cause | Remediation Runbook |
| :--- | :--- | :--- | :--- | :--- |
| **`RCA-001`** Fork Remote Ambiguity | GitHub CLI (`gh`) | `gh issue`/`gh pr` commands target `datacharmer/test_db` instead of `jmrenouard/test_db`. | Multiple remotes (`origin` fork + `upstream` original) cause `gh` to default to `upstream` unless `-R jmrenouard/test_db` is passed or set as default. | [Verify Checksums & Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md) |
| **`RCA-002`** CSV Trailing Spaces & `[ND]` Masking | `sirene_etl.transforms` | Key lookup fails on `"coordonneeLambertAbscisseEtablissement "` or numeric/date cast raises on `[ND]`. | INSEE stock CSV headers occasionally contain trailing whitespace and literal `[ND]`/`[nd]` privacy sentinels across text, date, and numeric columns. | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| **`RCA-003`** Host PostgreSQL `5432` Collision | `sirene-postgres` | Binding container `5432` to host `5432` fails with port-in-use or connects to host system PostgreSQL. | Local workstations/CI runners bind system PostgreSQL to `127.0.0.1:5432`. Stack binds `127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432`. | [Deploy MariaDB & PostgreSQL Stacks](../../02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md) |
| **`RCA-004`** `psycopg` v3 `INTRANS` + `SAVEPOINT` Rollback | `sirene_etl.incremental_import` | `incremental_import.py` logs `etab_updated > 0` and `state_transitions > 0`, yet target rows remain unchanged. | Calling `acquire_etl_lock` / `is_checksum_already_imported` on `autocommit=False` left `conn` in `INTRANS`; `with conn.transaction():` opened a nested `SAVEPOINT` rolled back by `finally: conn.rollback()`. Fixed by explicit `conn.commit()` preamble. | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| **`RCA-005`** Parameterless `%%` & `AccessShareLock` | `psycopg` v3 / `sirene_etl.db` | Query raises `operator does not exist: text %% unknown` or `drop_secondary_indexes` stalls behind open reader. | `psycopg` v3 unescapes `%%` only when `params` is passed; unclosed non-autocommit sessions hold `AccessShareLock` blocking `DROP INDEX` (`AccessExclusiveLock`). | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| **`RCA-006`** PostgreSQL 18 Volume Mount Layout | Docker `postgres:18-bookworm` | Container fails init when volume targets `/var/lib/postgresql/data`. | Official `postgres:18` images changed `PGDATA` to `/var/lib/postgresql/18/docker` and require mounting persistent volumes at `/var/lib/postgresql`. | [Deploy MariaDB & PostgreSQL Stacks](../../02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md) |
| **`RCA-007`** Parameterized `pg_trgm` `%` & PG18 `P3` Split-Brain | `sirene_etl.mm_probe` | `psycopg.ProgrammingError: incomplete placeholder: '%'` (`mm_probe.py:702`), or Node A/B silent state divergence after concurrent SIRET updates. | Parameterized `psycopg` v3 queries require `%%` (`enseigne_recherche %% %s`); native PG 18 `origin=none` applies bidirectional updates independently without LWW/CRDT conflict resolution. | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |

---

## 2. Database Contention, Integrity & Runtime Failures

| Alert / Error Signature | Engine / Script | Probable Cause | Observable Exit / SQLSTATE | Remediation Runbook |
| :--- | :--- | :--- | :--- | :--- |
| `TRANSACTION DEADLOCK` / `ER_LOCK_DEADLOCK` | MariaDB `11.8` (`InnoDB`), `db_simulator.py` | Circular wait-for graph cycle between concurrent transactions (`tests/data/deadlock/`). | MySQL `1213` / SQLSTATE `40001` | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| `Lock wait timeout exceeded` (`ER_LOCK_WAIT_TIMEOUT`) | MariaDB `11.8` (`InnoDB`), `gap_locking*` | `REPEATABLE READ` gap lock or FK unique-index scan blocks concurrent `INSERT` beyond `innodb_lock_wait_timeout`. | MySQL `1205` / SQLSTATE `HY000` | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| `CRC \| FAIL` or `count \| FAIL` (`verify_data.sh`) | MariaDB `verify` (`test_employees_sha2.sql`) | Missing/partial dump injection, post-injection DML mutation (`inject-fake`, `oltp`), or aborted import. | Exit code `1` (`verify_data.sh`) | [Verify Checksums & Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md) |
| `RAISE EXCEPTION 'SIRENE SHA-256 verification failed'` | PostgreSQL `18` (`sirene/test_sirene_sha2.sql`) | Row count or deterministic `sha256` hash mismatch across any of the 12 domain/referential tables. | `psql` exit code `3` (`ON_ERROR_STOP=1`) | [Verify Checksums & Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md) |
| `ValueError` checksum mismatch on `.part` download | `sirene_etl.downloader` | Corrupted stream or upstream checksum change during download; `.part` deleted before atomic rename. | Non-zero Python exit | [Verify Checksums & Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md) |
| `Unable to acquire PostgreSQL advisory lock 84729101` | `sirene_etl.db` | Concurrent `full_import.py`, `incremental_import.py`, or `watcher.py` holds session lock on same PG node. | `RuntimeError` (non-zero exit) | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| `Private files detected` / `exclude_docs` breach | `build_versioned_docs.py`, `docs-publish.yml` | `.kdbx`, `.keyx`, `.pid`, `.log`, or `.env*` artifact staged inside site output bundle. | CI exit `1` | [Verify Checksums & Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md) |
| Container `mariadb-11-8` or `sirene-postgres` unreachable | `Makefile`, `test_runner.sh`, `config.py` | Container stopped, `USE_CONTAINER=0` without local DB, or host port `15432` mismatch. | `1` / `psycopg.OperationalError` | [Deploy MariaDB & PostgreSQL Stacks](../../02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md) |

---

## 3. Multi-Master Qualification Probe Outcomes (`sirene/mm_probe.py`)

| Probe ID | Outcome / Classification | Trigger Condition | Architecture Verdict Impact | Target Guide / Runbook |
| :--- | :--- | :--- | :--- | :--- |
| `P1_DDL_COMPAT` | `PASS` / `WARN` / `FAIL` | `WARN` when `pg_try_advisory_lock` succeeds independently on both nodes (node-local lock); `FAIL` if `pg_trgm`, `STORED` columns, `UNIQUE NULLS NOT DISTINCT`, or `COPY` fails. | `WARN` -> `CONDITIONAL_PARTITIONED_WRITES_ONLY` | [Qualify PostgreSQL 18 Multi-Master](../../02-how-to-guides/operations/qualify-postgresql18-multimaster.md) |
| `P2_SEQUENCE_SPLIT_BRAIN` | `PASS` / `FAIL` | `FAIL` on identical `BIGSERIAL` `id` (`23505`) or convergence timeout across Node A/B. | `FAIL` -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Qualify PostgreSQL 18 Multi-Master](../../02-how-to-guides/operations/qualify-postgresql18-multimaster.md) |
| `P3_CONCURRENT_SIRET_UPSERT` | `CONVERGED_DETERMINISTIC` (`PASS`), `CONVERGED_NON_MONOTONIC` (`WARN`), `SERIALIZATION_ABORT_40001` (`WARN`), `SUBSCRIPTION_STALLED` (`WARN`), `DIVERGED_SPLIT_BRAIN` (`FAIL`) | Concurrent updates on identical `siret` diverge silently (Node A `('A','MM_NODE_B')` vs Node B `('F','MM_INITIAL')` on native PG 18 `origin=none`). | `FAIL` -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Remediate Deadlocks, Gap Locks & ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) |
| `P4_CROSS_NODE_FK_CAUSALITY` | `PASS` / `WARN` / `FAIL` | `WARN` on transient `23503 ForeignKeyViolation` during async parent-to-child replication; `FAIL` on convergence timeout. | `WARN` -> `CONDITIONAL_PARTITIONED_WRITES_ONLY` | [Qualify PostgreSQL 18 Multi-Master](../../02-how-to-guides/operations/qualify-postgresql18-multimaster.md) |
| `P5_BULK_COPY_REPLICATION_LAG` | `PASS` / `FAIL` | `FAIL` if replicated `etablissements` count or `pg_trgm` `%%` visibility lags past `timeout_sec`. | `FAIL` -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Qualify PostgreSQL 18 Multi-Master](../../02-how-to-guides/operations/qualify-postgresql18-multimaster.md) |

## Related Explanation & Incident Guides

- Deep dive on InnoDB wait-for graphs, gap locks, advisory locks, and split-brain causality:
  [Concurrency, Locking, and Replication Trade-Offs](../../04-explanation/deep-dives/concurrency-locking-and-replication-tradeoffs.md)
- Incident remediation SOP:
  [Remediate Deadlocks, Gap Locks, and ETL Drift](../../02-how-to-guides/incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md)
- Checksum and privacy boundary audit SOP:
  [Verify Checksums and Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md)
