# How-To Guides and Operational Runbooks

This section provides goal-oriented operational procedures and incident runbooks for **test_db** written in
**ASD-STE100 Issue 9** Simplified Technical English.

## Deployment

| Guide | Purpose |
| :--- | :--- |
| [Deploy MariaDB and PostgreSQL Stacks](deployment/deploy-mariadb-and-postgresql-stacks.md) | Configure `.env` files, start MariaDB 11.8 and PostgreSQL 18 containers, and load baseline datasets. |

## Operations

| Guide | Purpose |
| :--- | :--- |
| [Run Sysbench and SQL Analysis](operations/run-sysbench-and-sql-analysis.md) | Execute `sysbench` scaling sweeps, standard OLTP profiles, directory simulations, and `EXPLAIN` audits. |
| [Run Sirene Full and Incremental ETL](operations/run-sirene-full-and-incremental-etl.md) | Execute full-stock `COPY` imports, transactional delta syncs, offline Parquet samples, and watcher runs. |
| [Qualify PostgreSQL 18 Multi-Master](operations/qualify-postgresql18-multimaster.md) | Deploy the 2-node bidirectional replication lab, run probes `P1`..`P5`, and evaluate scorecards. |

## Incident Response

| Guide | Purpose |
| :--- | :--- |
| [Remediate Deadlocks, Gap Locks, and ETL Drift](incident-response/remediate-deadlocks-gap-locks-and-etl-drift.md) | Resolve InnoDB deadlocks, `REPEATABLE READ` gap-lock stalls, PostgreSQL `INTRANS` rollbacks, and `P3` divergence. |

## Security

| Guide | Purpose |
| :--- | :--- |
| [Verify Checksums and Privacy Boundaries](security/verify-checksums-and-privacy-boundaries.md) | Validate `employees` and Sirene SHA-256 digests, enforce zero-PII boundaries, and audit `.env` exclusions. |

## Bilingual Technical Guides

Legacy English and French technical guides cover tool usage and Sirene internals:

- [Technical Guides Index (EN)](../../documentation/en/index.md)
- [Technical Guides Index (FR)](../../documentation/fr/index.md)

## Other Documentation Quadrants

- [Documentation Portal](../index.md)
- [Tutorials](../01-tutorials/index.md)
- [Reference Specifications](../03-reference/index.md)
- [Architecture Explanation](../04-explanation/index.md)
