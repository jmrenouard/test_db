# 📊 DB Simulation: GAP_LOCKING_5
**Generated:** 2026-01-20 16:52:13

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `10`
- **Duration:** `20s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 24.00 |
| **QPS** | 103.67 |
| **Avg Latency** | 407.63 ms |
| **95th Latency** | 1013.60 ms |
| **Total Events** | 502 |

## 🏗️ Infrastructure
- **OS:** `Linux 6.6.87.2-microsoft-standard-WSL2`
- **CPU Cores:** `20`
- **Hostname:** `Ligthpath-Main`
- **Container:** `mariadb-11-8`
- **DB Version:** `11.8.5-MariaDB-ubu2404`
- **Concurrency:** `10 Threads`
- **Experiment Time:** `20 Seconds`
- **Target Storage:** `employees`
- **Host Node:** `127.0.0.1`
- **Total RAM:** `15631 MB`


## ⚠️ Deadlocks Detected
The simulation triggered 10 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 21036, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766363 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21036 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21031 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2468 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21031, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2463, OS thread handle 137749199206080, query id 1766334 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21031 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2468 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21027, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766325 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (3)
```

```text
*** (1) TRANSACTION:

TRANSACTION 21036, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 5 lock struct(s), heap size 1120, 4 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766363 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21027, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766325 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)
```

```text
*** (1) TRANSACTION:

TRANSACTION 21042, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2463, OS thread handle 137749199206080, query id 1766367 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21042 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21037 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21042 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```


## 🛠️ Reproducibility
### Execution Command
```bash
docker exec -i mariadb-11-8 sysbench --mysql-host=127.0.0.1 --mysql-user=root --mysql-password= --mysql-db=employees --sql-dir=/tmp/bench_dir/sql/ --threads=10 --time=20 --events=0 /tmp/dir_transactions_sysbench.lua run
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
2026-01-20 15:52:15 2468 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2468 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21036, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766363 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21036 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21031 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2468 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21031, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2463, OS thread handle 137749199206080, query id 1766334 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21031 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2468 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21027, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766325 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2468 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (3)

2026-01-20 15:52:15 2466 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21036, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 5 lock struct(s), heap size 1120, 4 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766363 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21027, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766325 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21027 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21036 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:15 2464 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21042, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2463, OS thread handle 137749199206080, query id 1766367 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21042 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21037 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21042 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:52:15 2461 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2461 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2461 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2461 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2461 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2461 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21037 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2461 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21045 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2461 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21045, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2461, OS thread handle 137749198898880, query id 1766375 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2461 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21045 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2461 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2461 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:15 2467 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2467 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2467 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2467 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2467 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2467 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21037 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2467 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21049 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2467 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21049, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2467, OS thread handle 137749198284480, query id 1766386 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2467 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21049 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2467 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2467 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:15 2466 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21037 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21051 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:15 2466 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21051, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766390 127.0.0.1 root Updating
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21051 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2466 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:15 2464 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21037, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 5 lock struct(s), heap size 1120, 4 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766392 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:15 2464 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21050, ACTIVE 0 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766388 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:15 2464 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21050 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21037 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:15 2464 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:16 2468 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:16 2468 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21046, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2460, OS thread handle 137748795619008, query id 1766423 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:16 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21046 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:16 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21058 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:16 2468 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21058, ACTIVE 1 sec starting index read
mysql tables in use 2, locked 2
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2464, OS thread handle 137748796540608, query id 1766412 127.0.0.1 root Updating
DELETE FROM products WHERE sku = 'SKU200'
2026-01-20 15:52:16 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21058 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2468 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21065, ACTIVE 1 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766434 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:16 2468 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2468 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21046 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2468 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (3)

2026-01-20 15:52:16 2466 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:16 2466 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21065, ACTIVE 1 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766434 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:16 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21046 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2466 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21046, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2460, OS thread handle 137748795619008, query id 1766423 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:16 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21046 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:16 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 4 n bits 320 index sku of table `employees`.`products` trx id 21062 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 2; compact format; info bits 0
 0: len 6; hex 534b55323030; asc SKU200;;
 1: len 4; hex 800000c8; asc     ;;

2026-01-20 15:52:16 2466 [Note] InnoDB: 
*** (3) TRANSACTION:

TRANSACTION 21062, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s)
MariaDB thread id 2466, OS thread handle 137749198591680, query id 1766422 127.0.0.1 root Updating
UPDATE products SET category = 'Promo' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:16 2466 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21062 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2466 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2466 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)

2026-01-20 15:52:16 2460 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:52:16 2460 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 21046, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 5 lock struct(s), heap size 1120, 4 row lock(s)
MariaDB thread id 2460, OS thread handle 137748795619008, query id 1766423 127.0.0.1 root Updating
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200'
2026-01-20 15:52:16 2460 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21046 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2460 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 800000c8; asc     ;;
 1: len 6; hex 000000005222; asc     R";;
 2: len 7; hex 380000002d0132; asc 8   - 2;;
 3: len 6; hex 534b55323030; asc SKU200;;
 4: len 9; hex 557064617465642d36; asc Updated-6;;

2026-01-20 15:52:16 2460 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 21065, ACTIVE 1 sec fetching rows
mysql tables in use 1, locked 1
LOCK WAIT 4 lock struct(s), heap size 1120, 3 row lock(s)
MariaDB thread id 2468, OS thread handle 137748422940352, query id 1766434 127.0.0.1 root Updating
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool'
2026-01-20 15:52:16 2460 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21065 lock_mode X waiting
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2460 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 326 page no 3 n bits 320 index PRIMARY of table `employees`.`products` trx id 21046 lock_mode X locks rec but not gap
Record lock, heap no 4 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 4; hex 8000012c; asc    ,;;
 1: len 6; hex 000000005217; asc     R ;;
 2: len 7; hex b100000031012a; asc     1 *;;
 3: len 6; hex 534b55333030; asc SKU300;;
 4: len 9; hex 4675726e6974757265; asc Furniture;;

2026-01-20 15:52:16 2460 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (1)


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
-- Teardown for Gap Locking 5
DROP TABLE IF EXISTS audit_trail;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;

```
#### trans_03.sql
```sql
-- trans_03: Range UPDATE (Exclusive Gap Locks)
BEGIN;
UPDATE products SET category = 'Promo' WHERE sku > 'SKU100' AND sku < 'SKU200';
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_09.sql
```sql
-- trans_09: Complex Cascading Delete
BEGIN;
DELETE FROM products WHERE sku = 'SKU200';
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_04.sql
```sql
-- trans_04: Range DELETE
BEGIN;
DELETE FROM products WHERE sku > 'SKU400' AND sku < 'SKU501';
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_10.sql
```sql
-- trans_10: Maintenance Category Shift
BEGIN;
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool';
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_08.sql
```sql
-- trans_08: SELECT FOR UPDATE on Empty Range (Pure Gap Lock)
BEGIN;
SELECT * FROM products WHERE sku > 'SKU600' AND sku < 'SKU700' FOR UPDATE;
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_02.sql
```sql
-- trans_02: Deadlock Driver B
BEGIN;
UPDATE products SET category = 'B' WHERE sku > 'SKU200' AND sku < 'SKU300';
SELECT SLEEP(0.1);
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200';
COMMIT;

```
#### trans_07.sql
```sql
-- trans_07: Rapid Audit Point Inserts
BEGIN;
INSERT INTO audit_trail (event_type, ref_sku) VALUES ('MANUAL', 'SKU999');
SELECT SLEEP(0.1);
COMMIT;

```
#### setup.sql
```sql
-- Setup for Gap Locking 5 (The Extreme Scenario)
DROP TABLE IF EXISTS audit_trail;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;

-- Table 1: Master Catalog
CREATE TABLE products (
    id INT PRIMARY KEY,
    sku VARCHAR(10) UNIQUE,
    category VARCHAR(20)
) ENGINE=InnoDB;

-- Table 2: Stocks referencing SKUs
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    qty INT DEFAULT 0,
    FOREIGN KEY (sku_code) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 3: Static Reference
CREATE TABLE warehouses (
    id INT PRIMARY KEY,
    location VARCHAR(50),
    capacity INT
) ENGINE=InnoDB;

-- Table 4: Logging table for Shared Lock demonstration
CREATE TABLE audit_trail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(20),
    ref_sku VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Initial Sparse Data
INSERT INTO warehouses (id, location, capacity) VALUES (1, 'North-1', 5000), (2, 'South-2', 8000);

INSERT INTO products (id, sku, category) VALUES 
(100, 'SKU100', 'Electronic'),
(200, 'SKU200', 'Electronic'),
(300, 'SKU300', 'Furniture'),
(400, 'SKU400', 'Furniture'),
(500, 'SKU500', 'Tool');

INSERT INTO inventory (sku_code, qty) VALUES 
('SKU100', 10), ('SKU200', 50), ('SKU300', 5), ('SKU400', 12);

```
#### trans_01.sql
```sql
-- trans_01: Deadlock Driver A
BEGIN;
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200';
SELECT SLEEP(0.1);
UPDATE products SET category = 'A' WHERE sku > 'SKU200' AND sku < 'SKU300';
COMMIT;

```
#### trans_06.sql
```sql
-- trans_06: Relational Cross-Update
BEGIN;
UPDATE inventory SET qty = qty + 1 WHERE sku_code = 'SKU100';
UPDATE products SET category = 'Updated-6' WHERE sku = 'SKU200';
SELECT SLEEP(0.1);
COMMIT;

```
#### trans_05.sql
```sql
-- trans_05: SELECT / INSERT (Shared Gap Lock)
BEGIN;
-- This SELECT part sets SHARED gap locks
INSERT INTO audit_trail (event_type, ref_sku)
SELECT 'LOG', sku FROM products WHERE sku > 'SKU200' AND sku < 'SKU300';
SELECT SLEEP(0.1);
COMMIT;

```