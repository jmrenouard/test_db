# Architecture, Design Decisions, and Technical Explanations

This quadrant explains how **test_db** unifies multi-engine database validation (`MariaDB`, `MySQL`, `Percona`, and
`PostgreSQL`), why its PostgreSQL 18 INSEE Sirene 3NF ETL and Diataxis publishing architecture were designed as they
are, and how locking, isolation, and active-active replication behave under contention.

## Contents

| Document | Focus | Primary Topics |
| :--- | :--- | :--- |
| [Platform and ETL Architecture](architecture-overview/platform-and-etl-architecture.md) | System Topology | Multi-engine MariaDB/MySQL/Percona/PostgreSQL testbed, `Makefile` orchestration, and 5-stage Sirene 3NF ETL pipeline |
| [ADR-001: PostgreSQL 18 3NF Sirene ETL & Multi-Master Qualification](design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md) | Engine & Data Design Decision | 13-table 3NF schema, `COPY FROM STDIN` index-drop/rebuild, monotonic incremental upsert, and `P1`–`P5` disqualification of native PG 18 `origin=none` |
| [ADR-002: Diataxis & Versioned MkDocs Publishing](design-decisions/adr-002-diataxis-versioned-mkdocs-publishing.md) | Documentation Decision | 4-quadrant Diataxis architecture, sparse `git archive` (excluding 168 MB `employees/`), virtual doc hooks, `mike` `versions.json`, and IONOS SFTP publishing |
| [Concurrency, Locking, and Replication Trade-Offs](deep-dives/concurrency-locking-and-replication-tradeoffs.md) | Deep Dive | InnoDB wait-for graph deadlocks, `REPEATABLE READ` gap and next-key locks, PostgreSQL advisory locks, and active-active `P3` split-brain causality |

## Foundational Context & Governance

- **Bilingual Technical Guides**: See [Technical Documentation Index (EN)](../../documentation/en/index.md),
  [Sirene Platform Guide (EN)](../../documentation/en/sirene_platform.md), and
  [Sirene Quickstart](../../sirene/README.md).
- **Engineering Traceability**: See [Action Logbook](../ACTION_LOGBOOK.md), [RCA Register](../RCA_REGISTER.md), and
  [Changelog](../../Changelog) for milestone history (`M1`–`M8`) and root-cause records (`RCA-001`–`RCA-007`).

## Related Documentation Quadrants

- **Portal Home**: [Documentation Portal](../index.md)
- **Tutorials**: [Guided Sandbox Labs](../01-tutorials/index.md)
- **How-To Guides**: [Operational SOPs and Incident Runbooks](../02-how-to-guides/index.md)
- **Reference**: [Schemas, Configuration, CLI & Error Specifications](../03-reference/index.md)
