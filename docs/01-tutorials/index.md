# Tutorials

> [!NOTE]
> **Learning-Oriented Quadrant (`01-tutorials/`):** Follow these guided, self-contained Docker labs to learn
> `test_db` safely on isolated local containers and synthetic datasets before running custom workloads.

Each tutorial starts from a clean container state, provides exact `make` and `docker` commands with expected terminal
outputs, and stops or cleans temporary artifacts at the end.

---

## Guided Learning Path

| Lesson | What You Will Practice | Key Commands &amp; Subsystems |
| :--- | :--- | :--- |
| [1. MariaDB 11.8 Employees Sandbox](01-mariadb-employees-sandbox.md) | Start `mariadb-11-8`, inject the 6-table `employees` dataset, verify CRC32 and SHA-256 checksums, and stop cleanly | `make start`, `make inject`, `make verify`, `test_employees_sha2.sql`, `make stop` |
| [2. Sirene PostgreSQL 18 3NF Offline Lab](02-sirene-postgresql18-offline-lab.md) | Boot PostgreSQL 18 on `127.0.0.1:15432`, load `15,000` legal units / `30,000` establishments via SQL and Parquet, and inspect deltas | `make sirene-up`, `make sirene-inject`, `make sirene-verify`, `make sirene-import-sample`, `make sirene-incremental-sample` |
| [3. Concurrency and Benchmarking Lab](03-concurrency-and-benchmarking-lab.md) | Run Sysbench query benchmarks, simulate InnoDB deadlocks and gap locks, run `EXPLAIN` analysis, and clean reports | `make bench`, `make test-data TEST=deadlock`, `make test-data TEST=gap_locking`, `make analyze`, `make clean` |

---

## Technical Guides

For component-level technical manuals in English:

- [Technical Guides Index (EN)](../../documentation/en/index.md)

---

## Next Steps

- Execute production deployment, ETL, multi-master probing, incident remediation, and checksum SOPs:
  [How-To Guides](../02-how-to-guides/index.md)
- Look up exhaustive schemas, `Makefile` targets, environment variables, CLI flags, and error codes:
  [Reference](../03-reference/index.md)
- Study platform topology, locking internals, and Architecture Decision Records:
  [Explanation](../04-explanation/index.md)
