[🏠 Home](index.md) | [⬅️ Previous](interactive_reporting.md) | [➡️ Next](sql_analyzer.md)
***

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

## Metrics Captured and Glossary

The simulation suite captures and parses various metrics from `sysbench`. Below is a glossary explaining each parameter and its unit.

### 1. Throughput Metrics

- **TPS (Transactions Per Second)**: The number of successful transactions executed per second. A transaction is a logical unit of work (e.g., an OLTP read/write script).
- **QPS (Queries Per Second)**: The total number of SQL queries (SELECT, INSERT, UPDATE, etc.) executed per second. This counts individual SQL operations.

### 2. Latency Metrics (Measured in Milliseconds, ms)

- **Min Latency**: The smallest execution time recorded for a single event/transaction.
- **Avg Latency**: The arithmetic mean of all event execution times.
- **Max Latency**: The longest execution time recorded for a single event/transaction.
- **95th Percentile**: A key benchmark metric indicating that 95% of all events were completed within this time or less. It represents the "worst-case" performance for the vast majority of users.
- **Sum Latency**: The cumulative execution time of all events across all threads.

### 3. Database Operations (Counts)

- **Read**: Total number of read queries (e.g., SELECT).
- **Write**: Total number of write queries (e.g., INSERT, UPDATE, DELETE).
- **Other**: Total number of administrative or non-data-mutating queries (e.g., COMMIT, BEGIN, etc.).
- **Total Events**: The total number of transactions or script iterations performed during the test.

### 4. Thread Fairness Statistics

Metrics used to determine if work was distributed evenly across all execution threads.

- **Events (Avg/Stddev)**:
  - **Avg**: Average number of events handled per thread.
  - **Stddev (Standard Deviation)**: Measures the variation from the average. A low value indicates even distribution; a high value suggests "noisy" threads or contention.
- **Execution Time (Avg/Stddev)**:
  - **Avg**: Average total time spent by each thread.
  - **Stddev**: The variation in total execution time across threads. High standard deviation indicates that some threads were stalled longer than others.

***

## Infrastructure Metadata

Captures the environment context for reproducibility:

- **OS**: Operating system version and kernel (e.g., Linux 6.5.0-26-generic).
- **CPU Cores**: Total number of logical processors detected.
- **Total RAM**: Amount of system memory (MB).
- **DB Version**: Full MariaDB version string (e.g., 11.8.1-MariaDB).
- **Concurrency/Threads**: The number of parallel workers used for the test.
- **Duration**: The total run time in seconds.

***

## Deadlock Detection

Automatically identifies MariaDB deadlocks and highlights them in reports.

## Report Output

Results are saved in:

- `reports/perf_threads/results_{N}_threads.txt`
- `reports/simulator_report.md` / `reports/simulator_report.html` (when using `db_simulator.py`)
- **Interactive Dashboard**: Modern HTML reporting with CSS-based bar graphs and command transparency.
- Summarized output in the terminal console.

***
[🏠 Home](index.md) | [⬅️ Previous](interactive_reporting.md) | [➡️ Next](sql_analyzer.md)
