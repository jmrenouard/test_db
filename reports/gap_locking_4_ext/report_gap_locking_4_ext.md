# 📊 DB Simulation: GAP_LOCKING_4_EXT
**Generated:** 2026-01-20 16:45:41

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `4`
- **Duration:** `10s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 1.98 |
| **QPS** | 11.67 |
| **Avg Latency** | 2012.02 ms |
| **95th Latency** | 3911.79 ms |
| **Total Events** | 20 |

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
The simulation triggered 2 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 19736, ACTIVE 1 sec starting index read
mysql tables in use 3, locked 3
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2433, OS thread handle 137748422940352, query id 1761469 127.0.0.1 root Updating
DELETE FROM main_catalog WHERE sku = 'S30'
2026-01-20 15:45:44 2433 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19736 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19734, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2434, OS thread handle 137749199206080, query id 1761468 127.0.0.1 root Update
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item')
2026-01-20 15:45:44 2433 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19736 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 0 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 19737, ACTIVE 1 sec starting index read
mysql tables in use 3, locked 3
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2435, OS thread handle 137748795619008, query id 1761470 127.0.0.1 root Updating
DELETE FROM main_catalog WHERE sku = 'S30'
2026-01-20 15:45:44 2435 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19737 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19734, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2434, OS thread handle 137749199206080, query id 1761468 127.0.0.1 root Update
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item')
2026-01-20 15:45:44 2435 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19737 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
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
2026-01-20 15:45:44 2433 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:45:44 2433 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19736, ACTIVE 1 sec starting index read
mysql tables in use 3, locked 3
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2433, OS thread handle 137748422940352, query id 1761469 127.0.0.1 root Updating
DELETE FROM main_catalog WHERE sku = 'S30'
2026-01-20 15:45:44 2433 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19736 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19734, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2434, OS thread handle 137749199206080, query id 1761468 127.0.0.1 root Update
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item')
2026-01-20 15:45:44 2433 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19736 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 0 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2433 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:45:44 2435 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:45:44 2435 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19737, ACTIVE 1 sec starting index read
mysql tables in use 3, locked 3
LOCK WAIT 4 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2435, OS thread handle 137748795619008, query id 1761470 127.0.0.1 root Updating
DELETE FROM main_catalog WHERE sku = 'S30'
2026-01-20 15:45:44 2435 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19737 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X
Record lock, heap no 1 PHYSICAL RECORD: n_fields 1; compact format; info bits 0
 0: len 8; hex 73757072656d756d; asc supremum;;

Record lock, heap no 4 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533330; asc S30;;
 1: len 4; hex 8000001e; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19734, ACTIVE 1 sec inserting
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 4 row lock(s), undo log entries 2
MariaDB thread id 2434, OS thread handle 137749199206080, query id 1761468 127.0.0.1 root Update
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item')
2026-01-20 15:45:44 2435 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19734 lock_mode X locks gap before rec insert intention waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 315 page no 4 n bits 320 index sku of table `employees`.`main_catalog` trx id 19737 lock mode S
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 3; hex 533230; asc S20;;
 1: len 4; hex 80000014; asc     ;;

2026-01-20 15:45:44 2435 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)


```

### Lua Script
```lua
-- scripts/dir_transactions_sysbench.lua
-- ============================================================================
-- Sysbench Transaction Simulation Script
-- ============================================================================
-- Purpose:
--   Executes SQL transactions from all .sql files found in a specified directory.
--   Each .sql file represents a single transaction (atomic unit of work).
--   Multiple statements within a file must be separated by semicolons.
--
-- Usage:
--   sysbench scripts/dir_transactions_sysbench.lua \
--     --sql-dir=/path/to/sql/dir \
--     --db-driver=mysql --mysql-host=... [options] \
--     run
--
-- Parameters:
--   --sql-dir: Path to directory containing .sql transaction files.
--
-- Logic:
--   1. thread_init(): Calls load_transactions() to read SQL files into memory.
--   2. event(): Randomly picks one loaded transaction and executes its statements.
-- ============================================================================

-- Define custom command line options for sysbench
sysbench.cmdline.options = {
    ["sql-dir"] = {"Directory containing transaction SQL files", ""}
}

-- Global state to store loaded transactions across thread lifecycles
local transactions = {}
local transaction_count = 0

--- Loads SQL files from the directory specified by --sql-dir.
-- This function scans the directory, reads .sql files (excluding setup/teardown),
-- and parses them into a structure ready for execution.
function load_transactions()
    local sql_dir = sysbench.opt.sql_dir
    
    -- Validate mandatory parameter
    if not sql_dir or sql_dir == "" then
        error("You must specify the SQL directory using --sql-dir")
    end

    -- Normalize directory path (ensure trailing slash)
    if string.sub(sql_dir, -1) ~= "/" then
        sql_dir = sql_dir .. "/"
    end

    -- Use shell 'find' to retrieve all .sql files in the immediate directory.
    -- This allows the script to remain agnostic of file naming conventions.
    local p = io.popen("find " .. sql_dir .. " -maxdepth 1 -name '*.sql'")
    if not p then
        error("Could not access directory: " .. sql_dir)
    end

    -- Iterate through each found file path
    for file_path in p:lines() do
        -- EXCLUSION LOGIC:
        -- setup.sql and teardown.sql are reserved for environment prep/cleanup
        -- and should not be part of the performance simulation transactions.
        if not string.match(file_path, "setup.sql$") and not string.match(file_path, "teardown.sql$") then
            local f = io.open(file_path, "r")
            if f then
                local content = f:read("*all")
                f:close()

                local statements = {}
                -- PARSING LOGIC:
                -- Split the file content by semicolons (;) to handle multi-statement transactions.
                for stmt in string.gmatch(content, "([^;]+);") do
                    -- CLEANING LOGIC:
                    -- Remove SQL comments (-- comment) and trim whitespace for cleaner DB execution.
                    local lines = {}
                    for line in string.gmatch(stmt, "([^\n]+)") do
                        -- Ignore lines starting with --
                        if not string.match(line, "^%s*%-%-") then
                            table.insert(lines, line)
                        end
                    end
                    
                    -- Rebuild the statement into a single line string
                    local clean_stmt = table.concat(lines, " ")
                    clean_stmt = string.gsub(clean_stmt, "^%s*(.-)%s*$", "%1")
                    
                    -- Only add non-empty statements to the transaction block
                    if clean_stmt ~= "" then
                        table.insert(statements, clean_stmt)
                    end
                end

                -- A file is considered a valid transaction if it contains at least one SQL statement
                if #statements > 0 then
                    table.insert(transactions, statements)
                end
            end
        end
    end
    p:close()

    -- Final validation: ensure at least one transaction was loaded
    transaction_count = #transactions
    if transaction_count == 0 then
        error("No .sql files found in " .. sql_dir)
    end
    
    -- Print summary to stdout (visible in sysbench logs)
    print(string.format("Loaded %d transactions from %s", transaction_count, sql_dir))
end

--- sysbench entry point: initialization for each worker thread.
function thread_init()
    -- Each thread loads the directory contents into its own local memory space
    load_transactions()
    
    -- Initialize random seed using time and Thread ID to ensure different
    -- threads pick different transactions even if started simultaneously.
    math.randomseed(os.time() + sysbench.tid)
end

--- sysbench entry point: logic executed for each 'request' (iteration).
function event()
    -- 1. Randomly pick a transaction from the loaded list
    local idx = math.random(transaction_count)
    local statements = transactions[idx]

    -- 2. Execute all SQL statements in this transaction sequentially
    -- Note: Sysbench handles transaction wrap (BEGIN/COMMIT) automatically
    -- if configured, or they can be explicitly included in the .sql files.
    for _, stmt in ipairs(statements) do
        db_query(stmt)
    end
end

```

### SQL Transaction Files
#### teardown.sql
```sql
-- Teardown for Gap Locking 4 Extended
DROP TABLE IF EXISTS child_logs;
DROP TABLE IF EXISTS child_orders;
DROP TABLE IF EXISTS main_catalog;

```
#### trans_A.sql
```sql
-- Transaction A: Shared Gap Lock + Delete Cascade
BEGIN;

-- Part 1: Shared Gap Lock via range-based INSERT ... SELECT
-- SELECT (without FOR UPDATE) triggers shared locks on unique index gaps
INSERT INTO child_orders (sku_code)
SELECT sku FROM main_catalog WHERE sku > 'S10' AND sku < 'S20';

SELECT SLEEP(1);

-- Part 2: Delete which triggers cascading checks and locks on children
DELETE FROM main_catalog WHERE sku = 'S30';

SELECT SLEEP(1);
COMMIT;

```
#### trans_B.sql
```sql
-- Transaction B: Range UPDATE + Gap Intrusion
BEGIN;

-- Part 1: Range-based UPDATE triggers exclusive range locks (including gaps)
UPDATE main_catalog SET description = 'Updated by B' WHERE sku > 'S20' AND sku < 'S40';

SELECT SLEEP(1);

-- Part 2: Try to insert into the gap currently locked by Transaction A (Shared)
-- This creates a deadlock potential if B waits for A, and A later needs something B has
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item');

COMMIT;

```
#### setup.sql
```sql
-- Setup for Gap Locking 4 Extended (Cascading & Multi-Child)
DROP TABLE IF EXISTS child_logs;
DROP TABLE IF EXISTS child_orders;
DROP TABLE IF EXISTS main_catalog;

-- Main table with UNIQUE non-PK SKU
CREATE TABLE main_catalog (
    id INT PRIMARY KEY,
    sku VARCHAR(10) UNIQUE,
    description VARCHAR(50)
) ENGINE=InnoDB;

-- First child table with CASCADE
CREATE TABLE child_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    FOREIGN KEY (sku_code) REFERENCES main_catalog(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Second child table with CASCADE
CREATE TABLE child_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    FOREIGN KEY (sku_code) REFERENCES main_catalog(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insert sparse data
INSERT INTO main_catalog (id, sku, description) VALUES 
(10, 'S10', 'Item 10'), 
(20, 'S20', 'Item 20'), 
(30, 'S30', 'Item 30');

```