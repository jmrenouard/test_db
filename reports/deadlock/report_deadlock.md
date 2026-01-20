# 📊 DB Simulation: DEADLOCK
**Generated:** 2026-01-20 16:13:22

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `4`
- **Duration:** `10s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 3.32 |
| **QPS** | 29.59 |
| **Avg Latency** | 1171.38 ms |
| **95th Latency** | 2009.23 ms |
| **Total Events** | 36 |

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
The simulation triggered 47 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 19322, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570117 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19322 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b76; asc     Kv;;
 2: len 7; hex 720000002d0110; asc r   -  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19318 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b76; asc     Kv;;
 2: len 7; hex 720000002d0110; asc r   -  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19318, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570116 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19318 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7a; asc     Kz;;
 2: len 7; hex 740000002d0110; asc t   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19322 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7a; asc     Kz;;
 2: len 7; hex 740000002d0110; asc t   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 19325, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570126 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19325 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19319, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570125 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7d; asc     K};;
 2: len 7; hex 750000003501ca; asc u   5  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19325 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7d; asc     K};;
 2: len 7; hex 750000003501ca; asc u   5  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 19326, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570130 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19326 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19319, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570125 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7e; asc     K~;;
 2: len 7; hex 76000000310110; asc v   1  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19326 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7e; asc     K~;;
 2: len 7; hex 76000000310110; asc v   1  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
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
2026-01-20 15:13:24 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19322, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570117 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19322 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b76; asc     Kv;;
 2: len 7; hex 720000002d0110; asc r   -  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19318 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b76; asc     Kv;;
 2: len 7; hex 720000002d0110; asc r   -  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19318, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570116 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19318 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7a; asc     Kz;;
 2: len 7; hex 740000002d0110; asc t   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19322 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7a; asc     Kz;;
 2: len 7; hex 740000002d0110; asc t   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:24 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19325, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570126 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19325 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19319, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570125 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7d; asc     K};;
 2: len 7; hex 750000003501ca; asc u   5  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19325 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7d; asc     K};;
 2: len 7; hex 750000003501ca; asc u   5  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:24 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:24 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19326, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570130 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19326 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b77; asc     Kw;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19319, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570125 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19319 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7e; asc     K~;;
 2: len 7; hex 76000000310110; asc v   1  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19326 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b7e; asc     K~;;
 2: len 7; hex 76000000310110; asc v   1  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:24 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:24 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19328, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570138 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19328 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b78; asc     Kx;;
 2: len 7; hex 730000003701ca; asc s   7  ;;
 3: len 4; hex 8000000e; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19320 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b78; asc     Kx;;
 2: len 7; hex 730000003701ca; asc s   7  ;;
 3: len 4; hex 8000000e; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19320, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570139 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19320 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b80; asc     K ;;
 2: len 7; hex 77000000330110; asc w   3  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19328 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b80; asc     K ;;
 2: len 7; hex 77000000330110; asc w   3  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:24 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19334, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570148 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19334 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b83; asc     K ;;
 2: len 7; hex 780000003601ca; asc x   6  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19331 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b83; asc     K ;;
 2: len 7; hex 780000003601ca; asc x   6  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19331, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570147 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:24 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19331 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b86; asc     K ;;
 2: len 7; hex 7a000000360110; asc z   6  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19334 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b86; asc     K ;;
 2: len 7; hex 7a000000360110; asc z   6  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 15:13:24 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:25 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:25 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19336, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570152 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:25 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19336 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b83; asc     K ;;
 2: len 7; hex 780000003601ca; asc x   6  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19331 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b83; asc     K ;;
 2: len 7; hex 780000003601ca; asc x   6  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19331, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570147 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:25 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19331 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b88; asc     K ;;
 2: len 7; hex 7b000000300110; asc {   0  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19336 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b88; asc     K ;;
 2: len 7; hex 7b000000300110; asc {   0  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:25 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:25 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19332, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570161 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:25 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19332 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19338, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570160 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:25 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b84; asc     K ;;
 2: len 7; hex 790000003301ca; asc y   3  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19332 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b84; asc     K ;;
 2: len 7; hex 790000003301ca; asc y   3  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:25 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:25 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19341, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570165 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:25 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19341 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19338, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570160 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:25 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b8d; asc     K ;;
 2: len 7; hex 7d0000002e0110; asc }   .  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19341 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b8d; asc     K ;;
 2: len 7; hex 7d0000002e0110; asc }   .  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:25 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:25 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19342, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570169 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:25 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19342 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b8a; asc     K ;;
 2: len 7; hex 7c0000003b01ca; asc |   ;  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:25 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19338, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570160 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:25 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19338 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b8e; asc     K ;;
 2: len 7; hex 7e0000002d0110; asc ~   -  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19342 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b8e; asc     K ;;
 2: len 7; hex 7e0000002d0110; asc ~   -  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 15:13:25 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:25 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:25 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19344, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570178 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:25 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19344 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b92; asc     K ;;
 2: len 7; hex 010000003201ca; asc     2  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19346 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b92; asc     K ;;
 2: len 7; hex 010000003201ca; asc     2  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19346, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570177 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:25 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19346 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b90; asc     K ;;
 2: len 7; hex 7f000000370110; asc     7  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19344 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b90; asc     K ;;
 2: len 7; hex 7f000000370110; asc     7  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 15:13:25 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:26 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:26 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19350, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570182 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:26 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19350 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b92; asc     K ;;
 2: len 7; hex 010000003201ca; asc     2  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19346 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b92; asc     K ;;
 2: len 7; hex 010000003201ca; asc     2  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19346, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570177 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:26 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19346 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b96; asc     K ;;
 2: len 7; hex 02000000390110; asc     9  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19350 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b96; asc     K ;;
 2: len 7; hex 02000000390110; asc     9  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:26 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:26 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19349, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570191 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:26 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19349 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b98; asc     K ;;
 2: len 7; hex 03000000310110; asc     1  ;;
 3: len 4; hex 80000012; asc     ;;

2026-01-20 15:13:26 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19352 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b98; asc     K ;;
 2: len 7; hex 03000000310110; asc     1  ;;
 3: len 4; hex 80000012; asc     ;;

2026-01-20 15:13:26 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19352, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570190 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:26 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19352 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b95; asc     K ;;
 2: len 7; hex 010000003202c8; asc     2  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:26 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19349 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004b95; asc     K ;;
 2: len 7; hex 010000003202c8; asc     2  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:26 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:26 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:26 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19362, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570205 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:26 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19362 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b9c; asc     K ;;
 2: len 7; hex 050000003001ca; asc     0  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19356 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b9c; asc     K ;;
 2: len 7; hex 050000003001ca; asc     0  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19356, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570204 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:26 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19356 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba2; asc     K ;;
 2: len 7; hex 080000003c0110; asc     <  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19362 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba2; asc     K ;;
 2: len 7; hex 080000003c0110; asc     <  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 15:13:26 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:26 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:26 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19366, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570214 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:26 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19366 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b9f; asc     K ;;
 2: len 7; hex 060000010101ca; asc        ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 15:13:26 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19359 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004b9f; asc     K ;;
 2: len 7; hex 060000010101ca; asc        ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 15:13:26 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19359, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570213 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:26 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19359 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba6; asc     K ;;
 2: len 7; hex 0a000000380110; asc     8  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 15:13:26 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19366 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba6; asc     K ;;
 2: len 7; hex 0a000000380110; asc     8  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 15:13:26 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:27 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:27 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19369, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570223 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:27 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19369 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004ba0; asc     K ;;
 2: len 7; hex 070000003c01ca; asc     <  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19360 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004ba0; asc     K ;;
 2: len 7; hex 070000003c01ca; asc     <  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19360, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570222 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:27 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19360 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba9; asc     K ;;
 2: len 7; hex 0b0000003801ca; asc     8  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19369 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004ba9; asc     K ;;
 2: len 7; hex 0b0000003801ca; asc     8  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:27 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:27 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19374, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570232 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:27 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19374 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004ba5; asc     K ;;
 2: len 7; hex 09000000320110; asc     2  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:27 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19365 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004ba5; asc     K ;;
 2: len 7; hex 09000000320110; asc     2  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 15:13:27 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19365, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570231 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:27 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19365 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bae; asc     K ;;
 2: len 7; hex 0e0000003d0110; asc     =  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 15:13:27 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19374 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bae; asc     K ;;
 2: len 7; hex 0e0000003d0110; asc     =  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 15:13:27 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:27 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:27 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19378, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570241 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:27 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19378 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004baa; asc     K ;;
 2: len 7; hex 0c0000003301ca; asc     3  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 15:13:27 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19370 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004baa; asc     K ;;
 2: len 7; hex 0c0000003301ca; asc     3  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 15:13:27 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19370, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570240 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:27 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19370 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bb2; asc     K ;;
 2: len 7; hex 10000000c301ca; asc        ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 15:13:27 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19378 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bb2; asc     K ;;
 2: len 7; hex 10000000c301ca; asc        ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 15:13:27 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:27 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:27 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19384, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570255 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:27 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19384 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb1; asc     K ;;
 2: len 7; hex 0f000000310110; asc     1  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19377 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb1; asc     K ;;
 2: len 7; hex 0f000000310110; asc     1  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 15:13:27 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19377, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570254 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:27 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19377 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bb8; asc     K ;;
 2: len 7; hex 13000000c401ca; asc        ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19384 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bb8; asc     K ;;
 2: len 7; hex 13000000c401ca; asc        ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 15:13:27 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:28 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:28 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19381, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570264 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:28 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19381 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19387, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570263 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:28 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb5; asc     K ;;
 2: len 7; hex 11000000300110; asc     0  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19381 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb5; asc     K ;;
 2: len 7; hex 11000000300110; asc     0  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:28 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:28 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19382, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570268 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:28 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19382 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19387, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570263 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:28 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb6; asc     K ;;
 2: len 7; hex 120000003e01ca; asc     >  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19382 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bb6; asc     K ;;
 2: len 7; hex 120000003e01ca; asc     >  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:28 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:28 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19388, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570272 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:28 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19388 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbb; asc     K ;;
 2: len 7; hex 140000003e0110; asc     >  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:28 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19387, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570263 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:28 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19387 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bbc; asc     K ;;
 2: len 7; hex 150000003901ca; asc     9  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19388 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bbc; asc     K ;;
 2: len 7; hex 150000003901ca; asc     9  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 15:13:28 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:28 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:28 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19390, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570281 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:28 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19390 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:28 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19395, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570280 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:28 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbe; asc     K ;;
 2: len 7; hex 16000000c001ca; asc        ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19390 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bbe; asc     K ;;
 2: len 7; hex 16000000c001ca; asc        ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:28 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:28 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:28 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19392, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570285 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:28 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19392 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:28 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19395, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570280 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:28 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc0; asc     K ;;
 2: len 7; hex 170000003f0110; asc     ?  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19392 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc0; asc     K ;;
 2: len 7; hex 170000003f0110; asc     ?  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:28 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:29 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:29 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19396, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570289 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:29 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19396 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bc3; asc     K ;;
 2: len 7; hex 18000000310110; asc     1  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 15:13:29 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19395, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570280 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:29 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19395 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc4; asc     K ;;
 2: len 7; hex 190000002f01ca; asc     /  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19396 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc4; asc     K ;;
 2: len 7; hex 190000002f01ca; asc     /  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:29 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:29 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19404, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570298 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:29 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19404 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc6; asc     K ;;
 2: len 7; hex 1a0000003401ca; asc     4  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19398 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc6; asc     K ;;
 2: len 7; hex 1a0000003401ca; asc     4  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:29 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19398, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570297 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:29 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19398 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bcc; asc     K ;;
 2: len 7; hex 1d0000002f01ca; asc     /  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19404 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bcc; asc     K ;;
 2: len 7; hex 1d0000002f01ca; asc     /  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:29 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:29 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19407, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570307 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:29 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19407 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc8; asc     K ;;
 2: len 7; hex 1b0000003a01ca; asc     :  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19400 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bc8; asc     K ;;
 2: len 7; hex 1b0000003a01ca; asc     :  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:29 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19400, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570306 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:29 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19400 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bcf; asc     K ;;
 2: len 7; hex 1e000000310110; asc     1  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19407 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bcf; asc     K ;;
 2: len 7; hex 1e000000310110; asc     1  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 15:13:29 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:29 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:29 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19412, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570316 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:29 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19412 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bcb; asc     K ;;
 2: len 7; hex 1c0000003001ca; asc     0  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:29 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19403 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bcb; asc     K ;;
 2: len 7; hex 1c0000003001ca; asc     0  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:29 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19403, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570315 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:29 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19403 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bd4; asc     K ;;
 2: len 7; hex 210000003801ca; asc !   8  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 15:13:29 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19412 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bd4; asc     K ;;
 2: len 7; hex 210000003801ca; asc !   8  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 15:13:29 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:29 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:29 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19416, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570325 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:29 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19416 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bd0; asc     K ;;
 2: len 7; hex 1f0000002e01ca; asc     .  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19408 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bd0; asc     K ;;
 2: len 7; hex 1f0000002e01ca; asc     .  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:29 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19408, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570324 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:29 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19408 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bd8; asc     K ;;
 2: len 7; hex 230000003a01ca; asc #   :  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19416 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bd8; asc     K ;;
 2: len 7; hex 230000003a01ca; asc #   :  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 15:13:29 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:30 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:30 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19422, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570339 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:30 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19422 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bd7; asc     K ;;
 2: len 7; hex 220000003601ca; asc "   6  ;;
 3: len 4; hex 8000002c; asc    ,;;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19415 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bd7; asc     K ;;
 2: len 7; hex 220000003601ca; asc "   6  ;;
 3: len 4; hex 8000002c; asc    ,;;

2026-01-20 15:13:30 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19415, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570338 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:30 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19415 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bde; asc     K ;;
 2: len 7; hex 26000000800110; asc &      ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19422 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bde; asc     K ;;
 2: len 7; hex 26000000800110; asc &      ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:30 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:30 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19428, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570353 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:30 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19428 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bdc; asc     K ;;
 2: len 7; hex 250000002e0110; asc %   .  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 15:13:30 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19420 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bdc; asc     K ;;
 2: len 7; hex 250000002e0110; asc %   .  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 15:13:30 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19420, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570352 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:30 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19420 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be4; asc     K ;;
 2: len 7; hex 29000000340110; asc )   4  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 15:13:30 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19428 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be4; asc     K ;;
 2: len 7; hex 29000000340110; asc )   4  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 15:13:30 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:30 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:30 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19425, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570362 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:30 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19425 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be7; asc     K ;;
 2: len 7; hex 2a000000360110; asc *   6  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19431 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be7; asc     K ;;
 2: len 7; hex 2a000000360110; asc *   6  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:30 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19431, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570361 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:30 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19431 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004be1; asc     K ;;
 2: len 7; hex 27000000330110; asc '   3  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19425 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004be1; asc     K ;;
 2: len 7; hex 27000000330110; asc '   3  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 15:13:30 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:31 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:31 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19426, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570366 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:31 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19426 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be7; asc     K ;;
 2: len 7; hex 2a000000360110; asc *   6  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:31 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19431 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be7; asc     K ;;
 2: len 7; hex 2a000000360110; asc *   6  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 15:13:31 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19431, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570361 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:31 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19431 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004be2; asc     K ;;
 2: len 7; hex 28000000300110; asc (   0  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 15:13:31 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19426 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004be2; asc     K ;;
 2: len 7; hex 28000000300110; asc (   0  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 15:13:31 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:31 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:31 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19432, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570375 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:31 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19432 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bed; asc     K ;;
 2: len 7; hex 2d000000370110; asc -   7  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19437 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bed; asc     K ;;
 2: len 7; hex 2d000000370110; asc -   7  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 15:13:31 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19437, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570374 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:31 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19437 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be8; asc     K ;;
 2: len 7; hex 2b000000320110; asc +   2  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19432 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004be8; asc     K ;;
 2: len 7; hex 2b000000320110; asc +   2  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:31 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:31 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19434, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570379 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:31 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19434 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bed; asc     K ;;
 2: len 7; hex 2d000000370110; asc -   7  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 15:13:31 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19437 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bed; asc     K ;;
 2: len 7; hex 2d000000370110; asc -   7  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 15:13:31 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19437, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570374 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:31 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19437 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bea; asc     K ;;
 2: len 7; hex 2c0000003e0110; asc ,   >  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:31 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19434 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bea; asc     K ;;
 2: len 7; hex 2c0000003e0110; asc ,   >  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 15:13:31 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:31 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:31 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19438, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570388 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:31 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19438 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf3; asc     K ;;
 2: len 7; hex 30000000320110; asc 0   2  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:31 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19443 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf3; asc     K ;;
 2: len 7; hex 30000000320110; asc 0   2  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:31 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19443, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570387 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:31 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19443 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bee; asc     K ;;
 2: len 7; hex 2e0000002e0110; asc .   .  ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 15:13:31 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19438 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bee; asc     K ;;
 2: len 7; hex 2e0000002e0110; asc .   .  ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 15:13:31 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:31 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:31 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19440, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570392 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:31 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19440 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf3; asc     K ;;
 2: len 7; hex 30000000320110; asc 0   2  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19443 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf3; asc     K ;;
 2: len 7; hex 30000000320110; asc 0   2  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 15:13:31 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19443, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570387 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:31 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19443 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf0; asc     K ;;
 2: len 7; hex 2f000000810110; asc /      ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19440 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf0; asc     K ;;
 2: len 7; hex 2f000000810110; asc /      ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 15:13:31 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:32 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:32 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19444, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570401 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:32 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19444 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf6; asc     K ;;
 2: len 7; hex 32000000830110; asc 2      ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 15:13:32 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19446 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf6; asc     K ;;
 2: len 7; hex 32000000830110; asc 2      ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 15:13:32 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19446, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570400 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:32 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19446 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf4; asc     K ;;
 2: len 7; hex 31000000360110; asc 1   6  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:32 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19444 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf4; asc     K ;;
 2: len 7; hex 31000000360110; asc 1   6  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:32 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:32 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:32 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19449, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570405 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:32 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19449 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf6; asc     K ;;
 2: len 7; hex 32000000830110; asc 2      ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 15:13:32 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19446 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bf6; asc     K ;;
 2: len 7; hex 32000000830110; asc 2      ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 15:13:32 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19446, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570400 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:32 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19446 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf9; asc     K ;;
 2: len 7; hex 330000003f01ca; asc 3   ?  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:32 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19449 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bf9; asc     K ;;
 2: len 7; hex 330000003f01ca; asc 3   ?  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 15:13:32 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:32 2381 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:32 2381 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19450, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570414 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:32 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19450 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bfc; asc     K ;;
 2: len 7; hex 350000003501ca; asc 5   5  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:32 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19452 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bfc; asc     K ;;
 2: len 7; hex 350000003501ca; asc 5   5  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:32 2381 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19452, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570413 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:32 2381 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19452 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bfa; asc     K ;;
 2: len 7; hex 340000003901ca; asc 4   9  ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 15:13:32 2381 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19450 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004bfa; asc     K ;;
 2: len 7; hex 340000003901ca; asc 4   9  ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 15:13:32 2381 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:32 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:32 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19456, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570418 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:32 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19456 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bfc; asc     K ;;
 2: len 7; hex 350000003501ca; asc 5   5  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:32 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19452 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bfc; asc     K ;;
 2: len 7; hex 350000003501ca; asc 5   5  ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 15:13:32 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19452, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570413 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:32 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19452 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c00; asc     L ;;
 2: len 7; hex 370000003a0110; asc 7   :  ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 15:13:32 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19456 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c00; asc     L ;;
 2: len 7; hex 370000003a0110; asc 7   :  ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 15:13:32 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:33 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:33 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19455, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570427 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:33 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19455 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19458, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570426 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:33 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bff; asc     K ;;
 2: len 7; hex 36000000360110; asc 6   6  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19455 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004bff; asc     K ;;
 2: len 7; hex 36000000360110; asc 6   6  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:33 2383 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:33 2383 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19461, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570431 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:33 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19461 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2383 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19458, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570426 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:33 2383 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c05; asc     L ;;
 2: len 7; hex 39000000370110; asc 9   7  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2383 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19461 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c05; asc     L ;;
 2: len 7; hex 39000000370110; asc 9   7  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2383 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:33 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:33 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19462, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570435 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:33 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19462 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c02; asc     L ;;
 2: len 7; hex 380000008201ca; asc 8      ;;
 3: len 4; hex 80000034; asc    4;;

2026-01-20 15:13:33 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19458, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570426 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:33 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19458 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c06; asc     L ;;
 2: len 7; hex 3a0000003f01ca; asc :   ?  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19462 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c06; asc     L ;;
 2: len 7; hex 3a0000003f01ca; asc :   ?  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:33 2384 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:33 2384 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19464, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570444 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:33 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19464 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0a; asc     L ;;
 2: len 7; hex 3c000000320110; asc <   2  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19466 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0a; asc     L ;;
 2: len 7; hex 3c000000320110; asc <   2  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 15:13:33 2384 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19466, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570443 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:33 2384 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19466 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c08; asc     L ;;
 2: len 7; hex 3b000000350110; asc ;   5  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19464 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c08; asc     L ;;
 2: len 7; hex 3b000000350110; asc ;   5  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 15:13:33 2384 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:33 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:33 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19469, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570448 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:33 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19469 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0a; asc     L ;;
 2: len 7; hex 3c000000320110; asc <   2  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19466 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0a; asc     L ;;
 2: len 7; hex 3c000000320110; asc <   2  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 15:13:33 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19466, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2383, OS thread handle 137749198591680, query id 1570443 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:33 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19466 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c0d; asc     L ;;
 2: len 7; hex 3d0000003b0110; asc =   ;  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19469 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c0d; asc     L ;;
 2: len 7; hex 3d0000003b0110; asc =   ;  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 15:13:33 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:34 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:34 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19475, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570456 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:34 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19475 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0e; asc     L ;;
 2: len 7; hex 3e0000008401ca; asc >      ;;
 3: len 4; hex 80000036; asc    6;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19470 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c0e; asc     L ;;
 2: len 7; hex 3e0000008401ca; asc >      ;;
 3: len 4; hex 80000036; asc    6;;

2026-01-20 15:13:34 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19470, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2381, OS thread handle 137748422940352, query id 1570455 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:34 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19470 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c13; asc     L ;;
 2: len 7; hex 400000003c0110; asc @   <  ;;
 3: len 4; hex 8000002c; asc    ,;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19475 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c13; asc     L ;;
 2: len 7; hex 400000003c0110; asc @   <  ;;
 3: len 4; hex 8000002c; asc    ,;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 15:13:34 2382 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 15:13:34 2382 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 19478, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2382, OS thread handle 137748795619008, query id 1570464 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 15:13:34 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19478 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c10; asc     L ;;
 2: len 7; hex 3f0000003401ca; asc ?   4  ;;
 3: len 4; hex 80000037; asc    7;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19472 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000004c10; asc     L ;;
 2: len 7; hex 3f0000003401ca; asc ?   4  ;;
 3: len 4; hex 80000037; asc    7;;

2026-01-20 15:13:34 2382 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 19472, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2384, OS thread handle 137749199206080, query id 1570463 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 15:13:34 2382 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19472 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c16; asc     L ;;
 2: len 7; hex 41000000830110; asc A      ;;
 3: len 4; hex 8000002d; asc    -;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 303 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 19478 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000004c16; asc     L ;;
 2: len 7; hex 41000000830110; asc A      ;;
 3: len 4; hex 8000002d; asc    -;;

2026-01-20 15:13:34 2382 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)


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
DROP TABLE IF EXISTS deadlock_test;

```
#### trans_cycle_2.sql
```sql
-- Transaction 2: Update 2 then 1
BEGIN;
UPDATE deadlock_test SET val = val + 1 WHERE id = 2;
SELECT SLEEP(0.2);
UPDATE deadlock_test SET val = val + 1 WHERE id = 1;
COMMIT;

```
#### trans_cycle_1.sql
```sql
-- Transaction 1: Update 1 then 2
BEGIN;
UPDATE deadlock_test SET val = val + 1 WHERE id = 1;
SELECT SLEEP(0.2);
UPDATE deadlock_test SET val = val + 1 WHERE id = 2;
COMMIT;

```
#### setup.sql
```sql
-- Setup for deadlock simulation
DROP TABLE IF EXISTS deadlock_test;
CREATE TABLE deadlock_test (
    id INT PRIMARY KEY,
    val INT
) ENGINE=InnoDB;

INSERT INTO deadlock_test (id, val) VALUES (1, 10), (2, 20);

```