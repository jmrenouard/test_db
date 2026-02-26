[🏠 Home](index.md) | [⬅️ Previous](tools_guide.md) | [➡️ Next](benchmarking.md)
***

# Interactive Reporting & HTML Dashboards

The test environment provides an Interactive Runner and an automated reporting engine (powered by Python and Tailwind CSS) to present complex benchmark data in an accessible format.

## The Interactive Runner (`make interactive`)

To execute tests and generate reports without memorizing Makefile arguments, run:

```bash
make interactive
```

This launches a terminal-based UI (`interactive_runner.py`) that steps through:

1. Environment detection (Docker vs Local).
2. Selection of the test type to run:
   - **Verification**: Data counts and structural integrity.
   - **Standard Bench**: Basic `sysbench` OLTP testing.
   - **Performance Scaling**: QPS/Latency graphs from 1 to 64 threads.
   - **Data Tests**: Deadlocks, Gap Locks, Isolation tests, etc.
   - **SQL Analysis**: Automated `EXPLAIN` and missing index detection.
3. Test execution with live progress output.
4. Automatic generation of enhanced HTML reports upon completion.

---

## The DB Simulator (`db_simulator.py`)

For advanced control and custom SQL workload simulation with premium HTML output, the `db_simulator.py` script replaces standard `sysbench` terminal output with actionable dashboards.

### Key Capabilities

1. **Deadlock Visualization**: Highlights exactly which transactions clashed.
2. **Interactive Charts**: Plots latency percentiles and throughput vs. threads.
3. **Environment Capture**: Snapshots OS, RAM, and Database versions for verifiable reproducibility.
4. **Tailwind Styling**: The HTML reports are self-contained and beautifully styled with Tailwind CSS via CDN.

### Execution Example

To manually run a workload simulation from a directory:

```bash
python3 scripts/db_simulator.py \
  --sql-dir tests/data/deadlock/ \
  --container mariadb-11-8 \
  --threads 16 \
  --time 30
```

### Report Output

Depending on the tool used, the final reports are placed in the `reports/` directory.

- `reports/performance_report.html` (Overall execution dashboard)
- `reports/perf_threads/scaling_report.html` (Scalability and thread comparisons)
- `reports/simulator_report.html` (Simulator specific outputs and deadlock highlights)

These files can be opened directly in any modern web browser.

***
[🏠 Home](index.md) | [⬅️ Previous](tools_guide.md) | [➡️ Next](benchmarking.md)
