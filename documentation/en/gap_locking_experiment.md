# Gap Locking Experiment in MariaDB

This experiment demonstrates why creating range locks (Gap Locking) in InnoDB can cause performance degradation and insertion stalls, especially when foreign keys are involved.

## Experiment Configuration

- **Tables**: `gap_parent` (sparse PKs: 10, 20, 30) and `gap_child` (FK to parent).
- **Contention**:
    1. **Locking Transaction**: `SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE`. This creates a Gap Lock on the space between ID 10 and 20.
    2. **Conflicting Transaction**: `INSERT INTO gap_parent (id, name) VALUES (15, 'Intruder')`. This attempt to insert into the gap will WAIT for the first transaction to commit/rollback.

## Technical Assets

### 1. MariaDB Configuration

Configuration used within the standard MariaDB 11.8 container (default settings). Note that Gap Locking is enabled by default in `REPEATABLE READ` isolation level (MariaDB's default).

### 2. Sysbench Execution

Command orchestrated by `db_simulator.py`:

```bash
sysbench scripts/dir_transactions_sysbench.lua \
  --mysql-host=127.0.0.1 \
  --mysql-user=root \
  --mysql-password= \
  --mysql-db=employees \
  --sql-dir=/tmp/bench_dir/sql/ \
  --threads=4 \
  --time=20 \
  run
```

### 3. Transaction Logic (SQL)

- **Selection/Locking**: `SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE;`
- **Insertion (Gap)**: `INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'Intruder');`
- **Insertion (Child)**: `INSERT IGNORE INTO gap_child (id, parent_id, description) VALUES (100, 20, 'Child');`

### 4. Lua script

The [dir_transactions_sysbench.lua](file:///home/jmren/GIT_REPOS/test_db/scripts/dir_transactions_sysbench.lua) script is used to load and execute these SQL statements in parallel, exposing index gaps contention.

## Observed Results

...

Using `db_simulator.py` with 4 concurrent threads:

| Metric | Results |
| :--- | :--- |
| **TPS** | ~60 |
| **Avg Latency** | ~64 ms |
| **95th Latency** | ~180 ms |

**Conclusion**: The significant gap between average and 95th percentile latency confirms that transactions were frequently waiting for lock releases. The gap lock successfully prevented insertions between existing keys, ensuring absolute range stability for the duration of the `FOR UPDATE` transaction.

## How to Reproduce

1. Inject environment:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root employees < tests/data/gap_locking/setup.sql
   ```

2. Run simulation:

   ```bash
   python3 scripts/db_simulator.py --sql-dir tests/data/gap_locking/ --container mariadb-11-8 --threads 4 --time 20
   ```
