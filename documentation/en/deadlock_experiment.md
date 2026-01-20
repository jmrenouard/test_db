# Deadlock Experiment in MariaDB

This experiment demonstrates how `db_simulator.py` can detect and analyze deadlocks by monitoring the MariaDB error log.

## Experiment Configuration

- **Tables**: `deadlock_test` (2 rows).
- **Contention Pattern**:
  - **Thread 1**: Updates Row 1, sleeps, then attempts to update Row 2.
  - **Thread 2**: Updates Row 2, sleeps, then attempts to update Row 1.
  - This creates a circular dependency (Wait-for Graph cycle), triggering a deadlock.

## Implementation Details

1. **Detection**: The simulator enables `SET GLOBAL innodb_print_all_deadlocks = 1` and fetches Docker logs since the start of the run.
2. **Reporting**: Deadlock events are extracted using regex and displayed in a dedicated card in both the Markdown and HTML reports.

## Observed Results

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
