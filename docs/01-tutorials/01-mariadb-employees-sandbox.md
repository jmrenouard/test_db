# Tutorial 1: MariaDB 11.8 Employees Sandbox

> **Learning Goal:** Boot the isolated `mariadb-11-8` Docker container, inject the canonical `employees` dataset
> (`300,024` employees and `2,844,047` salaries), and verify both CRC32 (`make verify`) and SHA-256
> (`test_employees_sha2.sql`) integrity checksums.

> [!WARNING]
> **Isolated Local Lab Container Only:** The default MariaDB lab configuration uses `DB_USER="root"` with an empty
> password (`DB_PASS=""`). Never reuse these lab settings on shared or production database servers.

---

## Prerequisites

Make sure your workstation meets these requirements before starting:

- Docker Engine running with a provisioned container named `mariadb-11-8` (with `mariadb` client and `sysbench`
  installed)
- GNU `make`, `bash`, and standard Unix utilities on your `PATH`
- Cloned `test_db` repository at the root directory (`Makefile` and `employees/` present)

Verify that the `mariadb-11-8` container exists on your Docker host:

```bash
docker ps -a --filter name=mariadb-11-8 --format "table {{.Names}}\t{{.Status}}"
```

Expected output:

```text
NAMES          STATUS
mariadb-11-8   Exited (0) ...
```

---

## What You Will Build

```mermaid
flowchart LR
    S1["1. make start / status"] -->|"Boot mariadb-11-8"| S2["2. make inject"]
    S2 -->|"Load 6 tables + 2 views"| S3["3. make verify"]
    S3 -->|"CRC32 checksums OK"| S4["4. test_employees_sha2.sql"]
    S4 -->|"Cross-engine SHA-256 OK"| S5["5. make stop"]
```

By the end of this tutorial, you will have:

1. Started the `mariadb-11-8` container and verified container readiness with `make status`.
2. Loaded the 6-table `employees` schema, 2 views, and all `.dump` datasets into MariaDB 11.8 with `make inject`.
3. Validated row counts and table CRC32 checksums with `make verify`.
4. Executed cross-engine SHA-256 verification using `test_employees_sha2.sql`.
5. Stopped the sandbox container cleanly with `make stop`.

---

## Step 1: Start and Inspect the MariaDB Container

Start `mariadb-11-8` from the repository root and confirm it is running:

```bash
make start
make status
```

Expected output:

```text
🚀 Starting MariaDB container (mariadb-11-8)...
mariadb-11-8
📊 Status of MariaDB container (mariadb-11-8):
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                    NAMES
...            mariadb:11.8   "docker-entrypoint.s…"   ...             Up 2 seconds   0.0.0.0:3306->3306/tcp   mariadb-11-8
```

---

## Step 2: Inject the Canonical `employees` Dataset

Copy the SQL scripts and `.dump` files from `employees/` into `/tmp/employees_data/` inside the container and load
them with `make inject`:

```bash
make inject
```

Expected output:

```text
💉 Injecting employees.sql into mariadb-11-8...
INFO
CREATING DATABASE STRUCTURE
INFO
storage engine: InnoDB
INFO
LOADING departments
INFO
LOADING employees
INFO
LOADING dept_emp
INFO
LOADING dept_manager
INFO
LOADING titles
INFO
LOADING salaries
...
```

Notice that `employees/employees.sql` drops and recreates the `employees` database cleanly, so repeated runs start
from an identical baseline.

---

## Step 3: Verify Row Counts and CRC32 Checksums

Run `make verify` to compare live row counts and `CHECKSUM TABLE` outputs against the canonical baseline in
`scripts/verify_data.sh`:

```bash
make verify
```

Expected output:

```text
ℹ️ Using Docker container: mariadb-11-8
ℹ️ Verifying data in container: mariadb-11-8
Table                     Count          Checksum       Status
------------------------- ----------     --------------- ----------
departments                        9          3407387832 OK
dept_emp                      331603          3190576018 OK
dept_manager                      24          3048905531 OK
employees                     300024           610052939 OK
salaries                     2844047          4273816835 OK
titles                        443308          1842528371 OK
----------------------------------------------------------
✅ Data integrity verification passed!
```

---

## Step 4: Run Cross-Engine SHA-256 Verification

Run `test_employees_sha2.sql` inside the container to verify deterministic row-by-row `SHA2(..., 256)` checksums (the
same hashes validated across MySQL, Percona, MariaDB, and PostgreSQL):

```bash
docker exec -i mariadb-11-8 mariadb -u root -t < test_employees_sha2.sql
```

Expected output (summary tail):

```mysql
+--------------+---------------+------------------------------------------------------------------+
| table_name   | records_match | crc_match                                                        |
+--------------+---------------+------------------------------------------------------------------+
| departments  | OK            | ok                                                               |
| dept_emp     | OK            | ok                                                               |
| dept_manager | OK            | ok                                                               |
| employees    | OK            | ok                                                               |
| salaries     | OK            | ok                                                               |
| titles       | OK            | ok                                                               |
+--------------+---------------+------------------------------------------------------------------+
+---------+--------+
| summary | result |
+---------+--------+
| CRC     | OK     |
| count   | OK     |
+---------+--------+
```

---

## Step 5: Stop the Sandbox Container

Stop the MariaDB container cleanly when finished:

```bash
make stop
```

Expected output:

```text
🛑 Stopping MariaDB container (mariadb-11-8)...
mariadb-11-8
```

---

## Next Steps

- Continue to [Tutorial 2: Sirene PostgreSQL 18 Offline Lab](02-sirene-postgresql18-offline-lab.md)
- Execute production deployment and lifecycle procedures:
  [How-To Guides](../02-how-to-guides/index.md) and
  [Deploy MariaDB and PostgreSQL Stacks](../02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md)
- Inspect all `employees` tables, baseline counts, and SHA-256 digests:
  [Datasets and Schemas Matrix](../03-reference/architecture-specs/datasets-and-schemas-matrix.md) and
  [Reference](../03-reference/index.md)
- Explore the multi-engine architecture and locking semantics:
  [Platform and ETL Architecture](../04-explanation/architecture-overview/platform-and-etl-architecture.md) and
  [Explanation](../04-explanation/index.md)
