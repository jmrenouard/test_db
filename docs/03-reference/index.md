# Reference: Schemas, Configuration, CLI, SQL Catalogs, and Error Matrix

Technical reference specifications for **test_db** (`v1.11.0`): MariaDB `11.8` / MySQL / Percona (`employees`,
`sakila`), PostgreSQL `12+` (`employees`), and PostgreSQL `18` (`sirene` 3NF ETL and multi-master qualification).

## Core Reference Specifications

| Document | Scope | Primary Source Artifacts |
| :--- | :--- | :--- |
| [Datasets & Schemas Matrix](architecture-specs/datasets-and-schemas-matrix.md) | `employees` (6 base tables, 2 views), `sakila` (16 tables, 7 views, triggers, spatial/fulltext), `sirene` (13 tables, 7 sentinels, 4 `STORED` columns, 25 indexes including 3 `pg_trgm` GIN indexes), synthetic `15k` UL / `30k` SIRET counts, and SHA-256 baselines. | `employees/employees.sql`, `sakila/sakila-mv-schema.sql`, `sirene/sql/01_schema_3nf.sql`, `sirene/sql/02_indexes.sql`, `sirene/test_sirene_sha2.sql` |
| [Environment Variables & Makefile Targets](configuration/environment-variables-and-makefile-targets.md) | Complete `Makefile` target inventory (MariaDB, Sysbench, Sirene PG 18, and MkDocs targets), `.env` overrides, PostgreSQL 18 container parameters, and CI/publishing variables. | `Makefile`, `.env_local`, `.env_mariadb118`, `sirene/.env.example`, `sirene/src/sirene_etl/config.py`, `sirene/docker-compose.yml` |
| [CLI Scripts & SQL Catalog](cli-and-scripts/cli-scripts-and-sql-catalog.md) | Flags, arguments, and exit codes for Python and Bash automation scripts plus exhaustive catalogs of `employees/req_employees.sql` (60 queries) and `sirene/sql/03_sample_queries.sql` (15 queries). | `sirene/*.py`, `sirene/scripts/generate_synthetic_dataset.py`, `scripts/*`, `interactive_runner.py`, `employees/req_employees.sql`, `sirene/sql/03_sample_queries.sql` |
| [Error & Alert Matrix](troubleshooting-codes/error-and-alert-matrix.md) | Failure codes, RCA taxonomy (`RCA-001`..`RCA-007`), InnoDB deadlock/gap-lock errors, SHA-256 failures, `mm_probe.py` probe outcomes, and direct remediation runbook links. | `docs/RCA_REGISTER.md`, `sirene/src/sirene_etl/*.py`, `scripts/verify_data.sh`, `scripts/db_simulator.py` |

## Bilingual Guides and Legacy References

| Document | Language | Focus |
| :--- | :--- | :--- |
| [Technical Guides Portal (EN)](../../documentation/en/index.md) | English | Legacy guide index for SQL analyzer, MariaDB management, benchmarking, and Sirene |
| [Technical Guides Portal (FR)](../../documentation/fr/index.md) | French | Bilingual technical guides index for MariaDB, Sysbench, and Sirene |
| [Sirene PostgreSQL 3NF Platform (EN)](../../documentation/en/sirene_platform.md) | English | Full 13-table data dictionary, CLI guide, and full SQL text for all 15 Sirene queries |
| [Sirene PostgreSQL 3NF Platform (FR)](../../documentation/fr/sirene_platform.md) | French | French 3NF data dictionary, CLI reference, and 15 analytical Sirene queries |
| [Employees Schema Documentation (EN)](../../doc_employees/employees.md) | English | Historical Employees schema overview and entity-relationship diagram |
| [Employees Schema Documentation (FR)](../../doc_employees/employees_fr.md) | French | French Employees data model overview and entity-relationship diagrams |
| [Sirene Module Quickstart](../../sirene/README.md) | English | Concise module layout, Compose targets, and `mm_probe.py` quickstart |

## Engineering Traceability & Release Records

| Record | Scope | Location |
| :--- | :--- | :--- |
| **Changelog** | Semantic version release history through `1.11.0` | [`Changelog`](../../Changelog) |
| **Action Logbook** | Chronological roadmap milestones (`M1`–`M8`) and verified actions (`ACT-000`–`ACT-004`) | [`docs/ACTION_LOGBOOK.md`](../ACTION_LOGBOOK.md) |
| **RCA Register** | Root cause analyses (`RCA-001`–`RCA-007`), improvements (`IMP-*`), approved standards (`APP-*`), and ideas (`IDEA-*`) | [`docs/RCA_REGISTER.md`](../RCA_REGISTER.md) |

## Related Documentation Quadrants

| Quadrant | Purpose | Entrypoint |
| :--- | :--- | :--- |
| **Portal Home** | Main documentation hub and 4-quadrant overview | [Documentation Portal](../index.md) |
| **Tutorials** | Isolated sandbox labs for Employees, Sirene PG 18, and Sysbench concurrency | [Tutorials Index](../01-tutorials/index.md) |
| **How-To Guides** | Goal-oriented operational procedures, deployment SOPs, and incident runbooks | [How-To Guides Index](../02-how-to-guides/index.md) |
| **Explanation** | Platform architecture, ADRs, and locking/replication trade-offs | [Explanation Index](../04-explanation/index.md) |
