[🏠 Home](index.md) | [⬅️ Previous](sql_analyzer.md) | [➡️ Next](gap_locking_experiment.md)
***

# Deadlock Experiment in MariaDB

This experiment demonstrates how `db_simulator.py` can detect and analyze deadlocks by monitoring the MariaDB error log.

## Experiment Configuration

- **Tables**: `deadlock_test` (2 rows).
- **Contention Pattern**:
  - **Thread 1**: Updates Row 1, sleeps, then attempts to update Row 2.
  - **Thread 2**: Updates Row 2, sleeps, then attempts to update Row 1.
  - This creates a circular dependency (Wait-for Graph cycle), triggering a deadlock.

## Automated Detection

The `db_simulator.py` tool automates the detection of these events by:

1. Parsing the Docker container logs for `TRANSACTION DEADLOCK` signatures.
2. Correlating the timestamp of the event with the simulation time.
3. Extracting the exact SQL statements involved from the MariaDB error log.

## Technical Assets

### 1. MariaDB Configuration

Enabled detailed deadlock logging:

```sql
SET GLOBAL innodb_print_all_deadlocks = 1;
```

### 2. Sysbench Execution

Command orchestrated by `db_simulator.py`:

```bash
sysbench scripts/dir_transactions_sysbench.lua \
  --mysql-host=127.0.0.1 \
  --mysql-user=root \
  --mysql-password= \
  --mysql-db=employees \
  --sql-dir=/tmp/bench_dir/sql/ \
  --threads=8 \
  --time=10 \
  run
```

### 3. Transaction Logic (SQL)

Designed to collide:

- **Transaction A**: `UPDATE id=1; SLEEP; UPDATE id=2;`
- **Transaction B**: `UPDATE id=2; SLEEP; UPDATE id=1;`

### 4. Lua Automation

The [dir_transactions_sysbench.lua](file:///home/jmren/GIT_REPOS/test_db/scripts/dir_transactions_sysbench.lua) script randomly selects these SQL files and executes them using `db_query()`, wrapped in `pcall` to ensure the simulation continues after a deadlock rollback.

## Observed Results

...

Running the simulation with 8 threads for 10 seconds:

- **Deadlocks Detected**: 30
- **Peak Latency**: Significantly increased due to rollback and re-execution.

The HTML report now visually highlights these events, providing the exact transaction queries involved in the conflict.

## How to Reproduce

1. Setup environment:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root employees < tests/data/deadlock/setup.sql
   ```

2. Run simulation:

   ```bash
   python3 scripts/db_simulator.py --sql-dir tests/data/deadlock/ --container mariadb-11-8 --threads 8 --time 10
   ```

***
[🏠 Home](index.md) | [⬅️ Previous](sql_analyzer.md) | [➡️ Next](gap_locking_experiment.md)
