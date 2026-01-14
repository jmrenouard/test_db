# Performance Benchmarking with Sysbench

The project includes automated performance tests for high-concurrency simulation and stress testing using `sysbench`.

## Benchmark Overview

The benchmarking suite leverages a custom Lua script (`scripts/employees_sysbench.lua`) to execute real SQL queries from your dataset.

### Available Targets

- **Standard Bench**: `make bench`  
  Executes the query set sequentially, repeating the entire set 10 times to measure average throughput.
- **Threaded Scaling**: `make perf-threads`  
  Runs a scalability test across 1, 2, 4, 8, 16, 32, and 64 threads for 60 seconds each.

## Metrics Captured

- **QPS (Queries Per Second)**: Measures the raw throughput of the database.
- **Latency**: Average response time in milliseconds.
- **Thread Scaling**: Helps identify the saturation point where adding more threads no longer improves performance.

## Report Output

Results are saved in:

- `reports/perf_threads/results_{N}_threads.txt`
- Summarized output in the terminal console.
