# 📊 DB Simulation: GAP_LOCKING_4
**Generated:** 2026-01-20 16:36:36

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `4`
- **Duration:** `10s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 1.98 |
| **QPS** | 11.06 |
| **Avg Latency** | 1912.66 ms |
| **95th Latency** | 3982.86 ms |
| **Total Events** | 22 |

## 🏗️ Infrastructure
- **OS:** `Linux 6.6.87.2-microsoft-standard-WSL2`
- **CPU Cores:** `20`
- **Hostname:** `Ligthpath-Main`
- **Container:** `mariadb-11-8`
- **DB Version:** `11.8.5-MariaDB-ubu2404`
- **Concurrency:** `4 Threads`
- **Experiment Time:** `10 Seconds`
- **Target Storage:** `employees`
- **Host Node:** `127.0.0.1`
- **Total RAM:** `15631 MB`


## ⚠️ Deadlocks Detected
The simulation triggered 1 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 19679, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2428, OS thread handle 137748422940352, query id 1761327 127.0.0.1 root Updating
DELETE FROM parent_metadata WHERE code = 'C30'
2026-01-20 15:36:39 2428 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19679 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433330; asc C30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19676 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433330; asc C30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19676, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2426, OS thread handle 137748795619008, query id 1761326 127.0.0.1 root Update
INSERT IGNORE INTO parent_metadata (id, code, info) VALUES (15, 'C15', 'Conflict A')
2026-01-20 15:36:39 2428 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19676 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433230; asc C20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19679 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433230; asc C20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```


## 🛠️ Reproducibility
### Execution Command
```bash
docker exec -i mariadb-11-8 sysbench --mysql-host=127.0.0.1 --mysql-user=root --mysql-password= --mysql-db=employees --sql-dir=/tmp/bench_dir/sql/ --threads=4 --time=10 --events=0 /tmp/dir_transactions_sysbench.lua run
```

### Database Configuration (Sample)
| Variable | Value |
|---|---|
| `character_set_server` | `utf8mb4` |
| `collation_server` | `utf8mb4_uca1400_ai_ci` |
| `datadir` | `/var/lib/mysql/` |
| `innodb_adaptive_flushing` | `ON` |
| `innodb_adaptive_flushing_lwm` | `10.000000` |
| `innodb_adaptive_hash_index` | `OFF` |
| `innodb_adaptive_hash_index_cells` | `34679` |
| `innodb_adaptive_hash_index_parts` | `8` |
| `innodb_alter_copy_bulk` | `ON` |
| `innodb_autoextend_increment` | `64` |
| `innodb_autoinc_lock_mode` | `1` |
| `innodb_buf_dump_status_frequency` | `0` |
| `innodb_buffer_pool_chunk_size` | `0` |
| `innodb_buffer_pool_dump_at_shutdown` | `ON` |
| `innodb_buffer_pool_dump_now` | `OFF` |
| `innodb_buffer_pool_dump_pct` | `25` |
| `innodb_buffer_pool_filename` | `ib_buffer_pool` |
| `innodb_buffer_pool_load_abort` | `OFF` |
| `innodb_buffer_pool_load_at_startup` | `ON` |
| `innodb_buffer_pool_load_now` | `OFF` |
| `innodb_buffer_pool_size` | `134217728` |
| `innodb_buffer_pool_size_auto_min` | `134217728` |
| `innodb_buffer_pool_size_max` | `134217728` |
| `innodb_checksum_algorithm` | `full_crc32` |
| `innodb_cmp_per_index_enabled` | `OFF` |
| `innodb_compression_algorithm` | `zlib` |
| `innodb_compression_default` | `OFF` |
| `innodb_compression_failure_threshold_pct` | `5` |
| `innodb_compression_level` | `6` |
| `innodb_compression_pad_pct_max` | `50` |
| `innodb_data_file_buffering` | `OFF` |
| `innodb_data_file_path` | `ibdata1:12M:autoextend` |
| `innodb_data_file_write_through` | `OFF` |
| `innodb_data_home_dir` | `` |
| `innodb_deadlock_detect` | `ON` |
| `innodb_deadlock_report` | `full` |
| `innodb_default_encryption_key_id` | `1` |
| `innodb_default_row_format` | `dynamic` |
| `innodb_disable_sort_file_cache` | `OFF` |
| `innodb_doublewrite` | `ON` |
| `innodb_encrypt_log` | `OFF` |
| `innodb_encrypt_tables` | `OFF` |
| `innodb_encrypt_temporary_tables` | `OFF` |
| `innodb_encryption_rotate_key_age` | `1` |
| `innodb_encryption_rotation_iops` | `100` |
| `innodb_encryption_threads` | `0` |
| `innodb_fast_shutdown` | `1` |
| `innodb_fatal_semaphore_wait_threshold` | `600` |
| `innodb_file_per_table` | `ON` |
| `innodb_fill_factor` | `100` |
| `innodb_flush_log_at_timeout` | `1` |
| `innodb_flush_log_at_trx_commit` | `1` |
| `innodb_flush_method` | `O_DIRECT` |
| `innodb_flush_neighbors` | `1` |
| `innodb_flush_sync` | `ON` |
| `innodb_flushing_avg_loops` | `30` |
| `innodb_force_primary_key` | `OFF` |
| `innodb_force_recovery` | `0` |
| `innodb_ft_aux_table` | `` |
| `innodb_ft_cache_size` | `8000000` |
| `innodb_ft_enable_diag_print` | `OFF` |
| `innodb_ft_enable_stopword` | `ON` |
| `innodb_ft_max_token_size` | `84` |
| `innodb_ft_min_token_size` | `3` |
| `innodb_ft_num_word_optimize` | `2000` |
| `innodb_ft_result_cache_limit` | `2000000000` |
| `innodb_ft_server_stopword_table` | `` |
| `innodb_ft_sort_pll_degree` | `2` |
| `innodb_ft_total_cache_size` | `640000000` |
| `innodb_ft_user_stopword_table` | `` |
| `innodb_immediate_scrub_data_uncompressed` | `OFF` |
| `innodb_instant_alter_column_allowed` | `add_drop_reorder` |
| `innodb_io_capacity` | `200` |
| `innodb_io_capacity_max` | `2000` |
| `innodb_linux_aio` | `auto` |
| `innodb_lock_wait_timeout` | `50` |
| `innodb_log_buffer_size` | `16777216` |
| `innodb_log_checkpoint_now` | `OFF` |
| `innodb_log_file_buffering` | `OFF` |
| `innodb_log_file_mmap` | `OFF` |
| `innodb_log_file_size` | `100663296` |
| `innodb_log_file_write_through` | `OFF` |
| `innodb_log_group_home_dir` | `./` |
| `innodb_log_spin_wait_delay` | `0` |
| `innodb_log_write_ahead_size` | `4096` |
| `innodb_lru_flush_size` | `0` |
| `innodb_lru_scan_depth` | `1536` |
| `innodb_max_dirty_pages_pct` | `90.000000` |
| `innodb_max_dirty_pages_pct_lwm` | `0.000000` |
| `innodb_max_purge_lag` | `0` |
| `innodb_max_purge_lag_delay` | `0` |
| `innodb_max_purge_lag_wait` | `4294967295` |
| `innodb_max_undo_log_size` | `10485760` |
| `innodb_monitor_disable` | `` |
| `innodb_monitor_enable` | `` |
| `innodb_monitor_reset` | `` |
| `innodb_monitor_reset_all` | `` |
| `innodb_old_blocks_pct` | `37` |
| `innodb_old_blocks_time` | `1000` |
| `innodb_online_alter_log_max_size` | `134217728` |
| `innodb_open_files` | `2000` |
| `innodb_optimize_fulltext_only` | `OFF` |
| `innodb_page_size` | `16384` |
| `innodb_prefix_index_cluster_optimization` | `OFF` |
| `innodb_print_all_deadlocks` | `ON` |
| `innodb_purge_batch_size` | `127` |
| `innodb_purge_rseg_truncate_frequency` | `128` |
| `innodb_purge_threads` | `4` |
| `innodb_random_read_ahead` | `OFF` |
| `innodb_read_ahead_threshold` | `56` |
| `innodb_read_io_threads` | `4` |
| `innodb_read_only` | `OFF` |
| `innodb_read_only_compressed` | `OFF` |
| `innodb_rollback_on_timeout` | `OFF` |
| `innodb_snapshot_isolation` | `ON` |
| `innodb_sort_buffer_size` | `1048576` |
| `innodb_spin_wait_delay` | `4` |
| `innodb_stats_auto_recalc` | `ON` |
| `innodb_stats_include_delete_marked` | `OFF` |
| `innodb_stats_method` | `nulls_equal` |
| `innodb_stats_modified_counter` | `0` |
| `innodb_stats_on_metadata` | `OFF` |
| `innodb_stats_persistent` | `ON` |
| `innodb_stats_persistent_sample_pages` | `20` |
| `innodb_stats_traditional` | `ON` |
| `innodb_stats_transient_sample_pages` | `8` |
| `innodb_status_output` | `OFF` |
| `innodb_status_output_locks` | `OFF` |
| `innodb_strict_mode` | `ON` |
| `innodb_sync_spin_loops` | `30` |
| `innodb_table_locks` | `ON` |
| `innodb_temp_data_file_path` | `ibtmp1:12M:autoextend` |
| `innodb_tmpdir` | `` |
| `innodb_truncate_temporary_tablespace_now` | `OFF` |
| `innodb_undo_directory` | `./` |
| `innodb_undo_log_truncate` | `OFF` |
| `innodb_undo_tablespaces` | `3` |
| `innodb_use_atomic_writes` | `ON` |
| `innodb_use_native_aio` | `ON` |
| `innodb_write_io_threads` | `4` |
| `interactive_timeout` | `28800` |
| `join_buffer_size` | `262144` |
| `join_buffer_space_limit` | `2097152` |
| `log_bin` | `OFF` |
| `log_bin_basename` | `` |
| `log_bin_compress` | `OFF` |
| `log_bin_compress_min_len` | `256` |
| `log_bin_index` | `` |
| `log_bin_trust_function_creators` | `OFF` |
| `long_query_time` | `10.000000` |
| `max_connections` | `151` |
| `max_heap_table_size` | `16777216` |
| `query_cache_limit` | `1048576` |
| `query_cache_min_res_unit` | `4096` |
| `query_cache_size` | `1048576` |
| `query_cache_strip_comments` | `OFF` |
| `query_cache_type` | `OFF` |
| `query_cache_wlock_invalidate` | `OFF` |
| `read_buffer_size` | `131072` |
| `slow_query_log` | `OFF` |
| `slow_query_log_file` | `37f12bec3a99-slow.log` |
| `sort_buffer_size` | `2097152` |
| `sync_binlog` | `0` |
| `thread_pool_dedicated_listener` | `OFF` |
| `thread_pool_exact_stats` | `OFF` |
| `thread_pool_idle_timeout` | `60` |
| `thread_pool_max_threads` | `65536` |
| `thread_pool_oversubscribe` | `3` |
| `thread_pool_prio_kickup_timer` | `1000` |
| `thread_pool_priority` | `auto` |
| `thread_pool_size` | `20` |
| `thread_pool_stall_limit` | `500` |
| `tmp_table_size` | `16777216` |
| `version` | `11.8.5-MariaDB-ubu2404` |
| `version_comment` | `mariadb.org binary distribution` |
| `version_compile_machine` | `x86_64` |
| `version_compile_os` | `debian-linux-gnu` |
| `version_malloc_library` | `system` |
| `version_source_revision` | `a74edc42d080a73e20d5d94e1dd5beea400b507c` |
| `version_ssl_library` | `OpenSSL 3.0.13 30 Jan 2024` |
| `wait_timeout` | `28800` |

### MariaDB Error Log (Tail)
```text
2026-01-20 15:36:39 2428 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:36:39 2428 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19679, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2428, OS thread handle 137748422940352, query id 1761327 127.0.0.1 root Updating
DELETE FROM parent_metadata WHERE code = 'C30'
2026-01-20 15:36:39 2428 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19679 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433330; asc C30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19676 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433330; asc C30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19676, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2426, OS thread handle 137748795619008, query id 1761326 127.0.0.1 root Update
INSERT IGNORE INTO parent_metadata (id, code, info) VALUES (15, 'C15', 'Conflict A')
2026-01-20 15:36:39 2428 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19676 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433230; asc C20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 313 page no 4 n bits 320 index code of table `employees`.`parent_metadata` trx id 19679 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 433230; asc C20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:36:39 2428 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)


```

### Lua Script
```lua
-- scripts/dir_transactions_sysbench.lua
-- This script executes SQL transactions from all .sql files in a specified directory.
-- Usage: sysbench scripts/dir_transactions_sysbench.lua --sql-dir=/path/to/sql/dir [options] run

-- Define custom command line options
sysbench.cmdline.options = {
    ["sql-dir"] = {"Directory containing transaction SQL files", ""}
}

local transactions = {}
local transaction_count = 0

-- Function to load SQL files from a directory
function load_transactions()
    local sql_dir = sysbench.opt.sql_dir
    
    if not sql_dir or sql_dir == "" then
        error("You must specify the SQL directory using --sql-dir")
    end

    -- Ensure directory ends with /
    if string.sub(sql_dir, -1) ~= "/" then
        sql_dir = sql_dir .. "/"
    end

    -- Use find to get all .sql files in the directory
    local p = io.popen("find " .. sql_dir .. " -maxdepth 1 -name '*.sql'")
    if not p then
        error("Could not access directory: " .. sql_dir)
    end

    for file_path in p:lines() do
        -- Skip setup.sql if present in the directory
        if not string.match(file_path, "setup.sql$") and not string.match(file_path, "teardown.sql$") then
            local f = io.open(file_path, "r")
            if f then
            local content = f:read("*all")
            f:close()

            local statements = {}
            -- Split content by ; and trim whitespace
            for stmt in string.gmatch(content, "([^;]+);") do
                -- Remove comments and leading/trailing whitespace
                local lines = {}
                for line in string.gmatch(stmt, "([^\n]+)") do
                    if not string.match(line, "^%s*%-%-") then
                        table.insert(lines, line)
                    end
                end
                local clean_stmt = table.concat(lines, " ")
                clean_stmt = string.gsub(clean_stmt, "^%s*(.-)%s*$", "%1")
                
                if clean_stmt ~= "" then
                    table.insert(statements, clean_stmt)
                end
            end

            if #statements > 0 then
                table.insert(transactions, statements)
            end
            end
        end
    end
    p:close()

    transaction_count = #transactions
    if transaction_count == 0 then
        error("No .sql files found in " .. sql_dir)
    end
    
    print(string.format("Loaded %d transactions from %s", transaction_count, sql_dir))
end

-- sysbench entry point for each thread
function thread_init()
    load_transactions()
    -- Initialize random seed for each thread
    math.randomseed(os.time() + sysbench.tid)
end

-- sysbench event loop
function event()
    -- Pick a random transaction
    local idx = math.random(transaction_count)
    local statements = transactions[idx]

    for _, stmt in ipairs(statements) do
        db_query(stmt)
    end
end

```

### SQL Transaction Files
#### teardown.sql
```sql
-- Teardown for Gap Locking 4
DROP TABLE IF EXISTS child_details;
DROP TABLE IF EXISTS parent_metadata;

```
#### trans_A.sql
```sql
-- Transaction A: SELECT (via INSERT) and DELETE
BEGIN;

-- Part 1: Shared Gap Lock via range-based INSERT ... SELECT
-- This SELECT (without FOR UPDATE) still sets shared locks because it is part of an INSERT
INSERT INTO child_details (p_code)
SELECT code FROM parent_metadata WHERE code > 'C10' AND code < 'C20';

SELECT SLEEP(1);

-- Part 2: Exclusive lock on another record
DELETE FROM parent_metadata WHERE code = 'C30';

SELECT SLEEP(1);
COMMIT;

```
#### trans_B.sql
```sql
-- Transaction B: Range UPDATE and Intrusion INSERT
BEGIN;

-- Part 1: Range-based UPDATE (Locks gap (C20, C30) and record C30)
UPDATE parent_metadata SET info = 'Updated by B' WHERE code > 'C20' AND code < 'C40';

SELECT SLEEP(1);

-- Part 2: Intrusion into A's gap (C10, C20)
-- This will wait for Transaction A's shared gap lock
INSERT IGNORE INTO parent_metadata (id, code, info) VALUES (15, 'C15', 'Conflict A');

COMMIT;

```
#### setup.sql
```sql
-- Setup for Gap Locking 4 (Comprehensive Scenario)
DROP TABLE IF EXISTS child_details;
DROP TABLE IF EXISTS parent_metadata;

-- Parent table with UNIQUE index (non-PK)
CREATE TABLE parent_metadata (
    id INT PRIMARY KEY,
    code VARCHAR(10) UNIQUE,
    info VARCHAR(50)
) ENGINE=InnoDB;

-- Child table with Foreign Key on the non-PK column
CREATE TABLE child_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    p_code VARCHAR(10),
    FOREIGN KEY (p_code) REFERENCES parent_metadata(code)
) ENGINE=InnoDB;

-- Insert sparse data
INSERT INTO parent_metadata (id, code, info) VALUES 
(10, 'C10', 'P10'), 
(20, 'C20', 'P20'), 
(30, 'C30', 'P30');

```