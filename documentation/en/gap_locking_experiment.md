# Gap Locking Experiment in MariaDB

This experiment demonstrates why creating range locks (Gap Locking) in InnoDB can cause performance degradation and insertion stalls, especially when foreign keys are involved.

## Experiment Configuration

- **Tables**: `gap_parent` (sparse PKs: 10, 20, 30) and `gap_child` (FK to parent).
- **Contention**:
    1. **Locking Transaction**: `SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE`. This creates a Gap Lock on the space between ID 10 and 20.
    2. **Conflicting Transaction**: `INSERT INTO gap_parent (id, name) VALUES (15, 'Intruder')`. This attempt to insert into the gap will WAIT for the first transaction to commit/rollback.

## Observed Results

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
