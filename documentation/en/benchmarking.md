# Performance Benchmarking with Sysbench

The project includes automated performance tests for high-concurrency simulation and stress testing using `sysbench`.

## Benchmark Overview

The benchmarking suite leverages a custom Lua script (`scripts/employees_sysbench.lua`) to execute real SQL queries from your dataset.

### Available Targets

- **Standard Bench**: `make bench`  
  Executes the query set sequentially, repeating the entire set 10 times to measure average throughput.
- **Threaded Scaling**: `make perf-threads`  
  Runs a scalability test across 1, 2, 4, 8, 16, 32, and 64 threads for 60 seconds each.
- **Directory-Based Transactions**: `make test-data`  
  Executes all SQL files from each subdirectory in `tests/data/` in parallel.
  - Run all: `make test-data`
  - Run specific: `make test-data TEST=deadlock`
- **Manual Runner**: `scripts/run_dir_bench.sh`  
  Direct CLI runner for custom SQL directories.

## Execution Environment

The performance suite supports both Docker-based and local execution modes.

### 1. Mode Switching (`USE_CONTAINER`)

By default, the system detects if the MariaDB container is running and uses it. You can force the execution mode using the `USE_CONTAINER` environment variable:

- **Force Docker**: (Default if container exists)
- **Force Local**: `export USE_CONTAINER=0`
  - In this mode, scripts will attempt to connect to a local MariaDB instance and use local `sysbench` binaries.

### 2. Connection Parameters

All scripts respect standard environment variables for database connectivity:

- `DB_USER` (Default: root)
- `DB_PASS` (Default: empty)
- `DB_NAME` (Default: employees)
- `DB_HOST` (Default: 127.0.0.1)

## Standard Sysbench Scripts

In addition to directory-based SQL tests, you can now run standard sysbench scripts (e.g., from `/usr/share/sysbench/`):

### Using `db_simulator.py`

```bash
python3 scripts/db_simulator.py --script /usr/share/sysbench/oltp_read_only.lua --name "OLTP Test"
```

### Using `run_dir_bench.sh`

```bash
bash scripts/run_dir_bench.sh --script /usr/share/sysbench/oltp_read_only.lua --threads 8
```

### Advanced OLTP Parameters

You can control the scale of standard OLTP tests using `THREADS`, `TABLES`, `SIZE`, and `TIME` (duration in seconds):

```bash
make oltp TYPE=read_write ACTION=prepare TABLES=10 SIZE=100000
make oltp TYPE=read_write THREADS=16 TIME=120
```

### Precise Reporting

Standard OLTP tests automatically generate HTML reports in dedicated, timestamp-friendly directories:

- **Directory Format**: `reports/oltp_{TYPE}_{THREADS}t_{TIME}s/`
- **Metadata**: Reports include the exact script used, thread count, and duration.

## Metrics Captured

- **QPS (Queries Per Second)**: Measures the raw throughput of the database.
- **Latency**: Average response time in milliseconds (includes 95th percentile analysis).
- **Thread Scaling**: Helps identify the saturation point where adding more threads no longer improves performance.
- **Infrastructure Metadata**: Captures OS, CPU architecture, RAM, and Hostname for reproducibility.
- **Deadlock Detection**: Automatically identifies MariaDB deadlocks and highlights them in reports.

## Report Output

Results are saved in:

- `reports/perf_threads/results_{N}_threads.txt`
- `reports/simulator_report.md` / `reports/simulator_report.html` (when using `db_simulator.py`)
- **Interactive Dashboard**: Modern HTML reporting with CSS-based bar graphs and command transparency.
- Summarized output in the terminal console.
