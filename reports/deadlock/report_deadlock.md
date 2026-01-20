# 📊 DB Simulation: DEADLOCK
**Generated:** 2026-01-20 15:19:00

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `4`
- **Duration:** `10s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 3.74 |
| **QPS** | 29.88 |
| **Avg Latency** | 1040.37 ms |
| **95th Latency** | 2045.74 ms |
| **Total Events** | 40 |

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
The simulation triggered 40 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 8944, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777712 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8944 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8942, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777711 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f0; asc     " ;;
 2: len 7; hex 63000000c301ca; asc c      ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8944 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f0; asc     " ;;
 2: len 7; hex 63000000c301ca; asc c      ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 8945, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777716 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8945 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8942, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777711 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f1; asc     " ;;
 2: len 7; hex 64000000330110; asc d   3  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8945 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f1; asc     " ;;
 2: len 7; hex 64000000330110; asc d   3  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 8951, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777725 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8951 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ef; asc     " ;;
 2: len 7; hex 620000002d0110; asc b   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8943 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ef; asc     " ;;
 2: len 7; hex 620000002d0110; asc b   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8943, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777724 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8943 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f7; asc     " ;;
 2: len 7; hex 670000003201ca; asc g   2  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8951 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f7; asc     " ;;
 2: len 7; hex 670000003201ca; asc g   2  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
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
2026-01-20 14:19:02 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:02 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8944, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777712 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8944 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8942, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777711 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f0; asc     " ;;
 2: len 7; hex 63000000c301ca; asc c      ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8944 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f0; asc     " ;;
 2: len 7; hex 63000000c301ca; asc c      ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:02 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:02 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8945, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777716 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8945 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ee; asc     " ;;
 2: len 7; hex 61000000310110; asc a   1  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8942, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777711 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8942 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f1; asc     " ;;
 2: len 7; hex 64000000330110; asc d   3  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8945 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f1; asc     " ;;
 2: len 7; hex 64000000330110; asc d   3  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:19:02 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:02 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:02 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8951, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777725 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8951 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ef; asc     " ;;
 2: len 7; hex 620000002d0110; asc b   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8943 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022ef; asc     " ;;
 2: len 7; hex 620000002d0110; asc b   -  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8943, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777724 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8943 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f7; asc     " ;;
 2: len 7; hex 670000003201ca; asc g   2  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8951 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022f7; asc     " ;;
 2: len 7; hex 670000003201ca; asc g   2  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:19:02 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:02 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:02 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8955, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777734 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8955 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022f3; asc     " ;;
 2: len 7; hex 650000002e0110; asc e   .  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:02 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8947 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022f3; asc     " ;;
 2: len 7; hex 650000002e0110; asc e   .  ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:02 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8947, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777733 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8947 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022fb; asc     " ;;
 2: len 7; hex 690000002e0110; asc i   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 14:19:02 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8955 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022fb; asc     " ;;
 2: len 7; hex 690000002e0110; asc i   .  ;;
 3: len 4; hex 8000000d; asc     ;;

2026-01-20 14:19:02 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:02 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:02 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8959, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777743 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8959 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022f5; asc     " ;;
 2: len 7; hex 66000000c401ca; asc f      ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8949 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022f5; asc     " ;;
 2: len 7; hex 66000000c401ca; asc f      ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8949, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777742 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:02 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8949 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022ff; asc     " ;;
 2: len 7; hex 6b0000002d0110; asc k   -  ;;
 3: len 4; hex 8000000e; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8959 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 0000000022ff; asc     " ;;
 2: len 7; hex 6b0000002d0110; asc k   -  ;;
 3: len 4; hex 8000000e; asc     ;;

2026-01-20 14:19:02 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:03 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:03 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8954, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777752 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:03 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8954 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8962, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777751 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:03 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022fa; asc     " ;;
 2: len 7; hex 68000000370110; asc h   7  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8954 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022fa; asc     " ;;
 2: len 7; hex 68000000370110; asc h   7  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:03 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:03 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8957, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777756 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:03 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8957 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8962, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777751 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:03 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022fd; asc     " ;;
 2: len 7; hex 6a000000310110; asc j   1  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8957 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 0000000022fd; asc     " ;;
 2: len 7; hex 6a000000310110; asc j   1  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:03 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:03 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8963, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777760 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:03 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8963 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002302; asc     # ;;
 2: len 7; hex 6c0000002f0110; asc l   /  ;;
 3: len 4; hex 8000000f; asc     ;;

2026-01-20 14:19:03 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8962, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777751 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:03 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8962 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002303; asc     # ;;
 2: len 7; hex 6d000000340110; asc m   4  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8963 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002303; asc     # ;;
 2: len 7; hex 6d000000340110; asc m   4  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:03 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:03 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:03 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8971, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777769 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:03 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8971 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002305; asc     # ;;
 2: len 7; hex 6e0000002e0110; asc n   .  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8965 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002305; asc     # ;;
 2: len 7; hex 6e0000002e0110; asc n   .  ;;
 3: len 4; hex 80000010; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8965, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777768 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:03 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8965 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000230b; asc     # ;;
 2: len 7; hex 71000000380110; asc q   8  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8971 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000230b; asc     # ;;
 2: len 7; hex 71000000380110; asc q   8  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:03 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:03 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8974, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777778 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:03 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8974 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002307; asc     # ;;
 2: len 7; hex 6f000000320110; asc o   2  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8967 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002307; asc     # ;;
 2: len 7; hex 6f000000320110; asc o   2  ;;
 3: len 4; hex 80000011; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8967, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777777 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:03 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8967 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000230e; asc     # ;;
 2: len 7; hex 72000000350110; asc r   5  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8974 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000230e; asc     # ;;
 2: len 7; hex 72000000350110; asc r   5  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 14:19:03 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:04 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:04 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8981, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777792 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:04 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8981 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000230f; asc     # ;;
 2: len 7; hex 730000003a0110; asc s   :  ;;
 3: len 4; hex 80000013; asc     ;;

2026-01-20 14:19:04 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8975 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000230f; asc     # ;;
 2: len 7; hex 730000003a0110; asc s   :  ;;
 3: len 4; hex 80000013; asc     ;;

2026-01-20 14:19:04 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8975, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777791 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:04 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8975 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002315; asc     # ;;
 2: len 7; hex 760000003d0110; asc v   =  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:04 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8981 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002315; asc     # ;;
 2: len 7; hex 760000003d0110; asc v   =  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:04 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:04 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:04 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8978, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777801 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:04 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8978 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002318; asc     # ;;
 2: len 7; hex 770000003501ca; asc w   5  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8984 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002318; asc     # ;;
 2: len 7; hex 770000003501ca; asc w   5  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8984, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777800 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:04 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8984 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002312; asc     # ;;
 2: len 7; hex 74000000390110; asc t   9  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8978 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002312; asc     # ;;
 2: len 7; hex 74000000390110; asc t   9  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:04 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:04 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8979, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777805 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:04 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8979 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002318; asc     # ;;
 2: len 7; hex 770000003501ca; asc w   5  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:04 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8984 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002318; asc     # ;;
 2: len 7; hex 770000003501ca; asc w   5  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:04 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8984, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777800 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:04 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8984 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002313; asc     # ;;
 2: len 7; hex 750000002f0110; asc u   /  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 14:19:04 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8979 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002313; asc     # ;;
 2: len 7; hex 750000002f0110; asc u   /  ;;
 3: len 4; hex 80000014; asc     ;;

2026-01-20 14:19:04 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:04 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:04 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8987, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777814 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:04 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8987 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002319; asc     # ;;
 2: len 7; hex 78000000320110; asc x   2  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8985 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002319; asc     # ;;
 2: len 7; hex 78000000320110; asc x   2  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8985, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777813 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:04 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8985 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000231b; asc     # ;;
 2: len 7; hex 79000000c401ca; asc y      ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8987 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000231b; asc     # ;;
 2: len 7; hex 79000000c401ca; asc y      ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:04 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:05 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:05 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8991, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777818 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:05 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8991 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002319; asc     # ;;
 2: len 7; hex 78000000320110; asc x   2  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8985 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002319; asc     # ;;
 2: len 7; hex 78000000320110; asc x   2  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8985, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777813 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:05 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8985 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000231f; asc     # ;;
 2: len 7; hex 7b0000003901ca; asc {   9  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8991 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000231f; asc     # ;;
 2: len 7; hex 7b0000003901ca; asc {   9  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:05 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:05 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8996, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777827 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:05 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8996 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000231d; asc     # ;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8989 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000231d; asc     # ;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8989, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777826 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:05 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8989 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002324; asc     #$;;
 2: len 7; hex 7d0000002e0110; asc }   .  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8996 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002324; asc     #$;;
 2: len 7; hex 7d0000002e0110; asc }   .  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:05 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:05 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:05 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8997, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777831 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:05 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8997 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000231d; asc     # ;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:05 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8989 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000231d; asc     # ;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:05 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8989, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777826 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:05 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8989 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002325; asc     #%;;
 2: len 7; hex 7e000000380110; asc ~   8  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:05 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8997 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002325; asc     #%;;
 2: len 7; hex 7e000000380110; asc ~   8  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:19:05 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:05 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:05 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 8993, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777840 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:05 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8993 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002327; asc     #';;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:05 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8999 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002327; asc     #';;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:05 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8999, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777839 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:05 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8999 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002321; asc     #!;;
 2: len 7; hex 7c000000390110; asc |   9  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:05 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8993 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002321; asc     #!;;
 2: len 7; hex 7c000000390110; asc |   9  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:05 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:05 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:05 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9003, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777844 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:05 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9003 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002327; asc     #';;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:05 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8999 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002327; asc     #';;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 80000017; asc     ;;

2026-01-20 14:19:05 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 8999, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777839 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:05 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 8999 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000232b; asc     #+;;
 2: len 7; hex 010000003a0110; asc     :  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:05 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9003 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000232b; asc     #+;;
 2: len 7; hex 010000003a0110; asc     :  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:05 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:06 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:06 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9002, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777852 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:06 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9002 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9008, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777853 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:06 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000232a; asc     #*;;
 2: len 7; hex 010000003a01ca; asc     :  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9002 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000232a; asc     #*;;
 2: len 7; hex 010000003a01ca; asc     :  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:06 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:06 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9005, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777857 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:06 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9005 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9008, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777853 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:06 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000232d; asc     #-;;
 2: len 7; hex 020000003001ca; asc     0  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9005 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000232d; asc     #-;;
 2: len 7; hex 020000003001ca; asc     0  ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:06 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:06 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9009, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777861 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:06 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9009 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002330; asc     #0;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000022; asc    ";;

2026-01-20 14:19:06 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9008, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777853 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:06 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9008 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002331; asc     #1;;
 2: len 7; hex 04000000c801ca; asc        ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9009 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002331; asc     #1;;
 2: len 7; hex 04000000c801ca; asc        ;;
 3: len 4; hex 80000018; asc     ;;

2026-01-20 14:19:06 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:06 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:06 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9011, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777870 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:06 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9011 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002338; asc     #8;;
 2: len 7; hex 070000002e01ca; asc     .  ;;
 3: len 4; hex 80000023; asc    #;;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9016 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002338; asc     #8;;
 2: len 7; hex 070000002e01ca; asc     .  ;;
 3: len 4; hex 80000023; asc    #;;

2026-01-20 14:19:06 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9016, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777869 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:06 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9016 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002333; asc     #3;;
 2: len 7; hex 050000003c01ca; asc     <  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9011 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002333; asc     #3;;
 2: len 7; hex 050000003c01ca; asc     <  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:06 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:06 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:06 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9013, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777874 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:06 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9013 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002338; asc     #8;;
 2: len 7; hex 070000002e01ca; asc     .  ;;
 3: len 4; hex 80000023; asc    #;;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9016 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002338; asc     #8;;
 2: len 7; hex 070000002e01ca; asc     .  ;;
 3: len 4; hex 80000023; asc    #;;

2026-01-20 14:19:06 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9016, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777869 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:06 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9016 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002335; asc     #5;;
 2: len 7; hex 06000000320110; asc     2  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9013 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002335; asc     #5;;
 2: len 7; hex 06000000320110; asc     2  ;;
 3: len 4; hex 80000019; asc     ;;

2026-01-20 14:19:06 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:07 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:07 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9023, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777883 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:07 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9023 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002339; asc     #9;;
 2: len 7; hex 08000000330110; asc     3  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9017 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002339; asc     #9;;
 2: len 7; hex 08000000330110; asc     3  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 14:19:07 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9017, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777882 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:07 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9017 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000233f; asc     #?;;
 2: len 7; hex 0b000000350110; asc     5  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9023 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000233f; asc     #?;;
 2: len 7; hex 0b000000350110; asc     5  ;;
 3: len 4; hex 8000001a; asc     ;;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:07 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:07 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9027, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777892 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:07 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9027 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000233b; asc     #;;;
 2: len 7; hex 090000003d0110; asc     =  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9019 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000233b; asc     #;;;
 2: len 7; hex 090000003d0110; asc     =  ;;
 3: len 4; hex 80000025; asc    %;;

2026-01-20 14:19:07 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9019, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777891 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:07 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9019 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002343; asc     #C;;
 2: len 7; hex 0d0000003e0110; asc     >  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9027 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002343; asc     #C;;
 2: len 7; hex 0d0000003e0110; asc     >  ;;
 3: len 4; hex 8000001b; asc     ;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:07 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:07 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9030, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777901 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:07 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9030 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000233e; asc     #>;;
 2: len 7; hex 0a000000c00110; asc        ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9022 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000233e; asc     #>;;
 2: len 7; hex 0a000000c00110; asc        ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 14:19:07 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9022, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777900 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:07 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9022 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002346; asc     #F;;
 2: len 7; hex 0e0000003a0110; asc     :  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9030 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002346; asc     #F;;
 2: len 7; hex 0e0000003a0110; asc     :  ;;
 3: len 4; hex 8000001c; asc     ;;

2026-01-20 14:19:07 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:07 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:07 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9026, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777909 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:07 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9026 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234a; asc     #J;;
 2: len 7; hex 100000002e0110; asc     .  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9034 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234a; asc     #J;;
 2: len 7; hex 100000002e0110; asc     .  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:07 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9034, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777910 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:07 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9034 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002342; asc     #B;;
 2: len 7; hex 0c0000003b0110; asc     ;  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9026 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002342; asc     #B;;
 2: len 7; hex 0c0000003b0110; asc     ;  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 14:19:07 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:07 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:07 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9031, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777914 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:07 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9031 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234a; asc     #J;;
 2: len 7; hex 100000002e0110; asc     .  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:07 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9034 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234a; asc     #J;;
 2: len 7; hex 100000002e0110; asc     .  ;;
 3: len 4; hex 8000001d; asc     ;;

2026-01-20 14:19:07 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9034, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777910 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:07 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9034 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002347; asc     #G;;
 2: len 7; hex 0f0000003d0110; asc     =  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 14:19:07 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9031 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002347; asc     #G;;
 2: len 7; hex 0f0000003d0110; asc     =  ;;
 3: len 4; hex 80000027; asc    ';;

2026-01-20 14:19:07 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:08 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9041, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777923 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9041 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234b; asc     #K;;
 2: len 7; hex 11000000330110; asc     3  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9035 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234b; asc     #K;;
 2: len 7; hex 11000000330110; asc     3  ;;
 3: len 4; hex 8000001e; asc     ;;

2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9035, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777922 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9035 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002351; asc     #Q;;
 2: len 7; hex 140000002f01ca; asc     /  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9041 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002351; asc     #Q;;
 2: len 7; hex 140000002f01ca; asc     /  ;;
 3: len 4; hex 80000028; asc    (;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:08 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:08 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9037, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777931 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:08 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9037 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002354; asc     #T;;
 2: len 7; hex 15000000c20110; asc        ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:08 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9044 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002354; asc     #T;;
 2: len 7; hex 15000000c20110; asc        ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:08 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9044, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777932 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:08 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9044 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234d; asc     #M;;
 2: len 7; hex 120000003e0110; asc     >  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:08 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9037 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000234d; asc     #M;;
 2: len 7; hex 120000003e0110; asc     >  ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:08 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:08 2255 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:08 2255 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9040, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777936 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:08 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9040 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002354; asc     #T;;
 2: len 7; hex 15000000c20110; asc        ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:08 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9044 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002354; asc     #T;;
 2: len 7; hex 15000000c20110; asc        ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:08 2255 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9044, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777932 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:08 2255 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9044 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002350; asc     #P;;
 2: len 7; hex 13000000c10110; asc        ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:08 2255 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9040 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002350; asc     #P;;
 2: len 7; hex 13000000c10110; asc        ;;
 3: len 4; hex 8000001f; asc     ;;

2026-01-20 14:19:08 2255 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:08 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9051, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777945 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9051 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002355; asc     #U;;
 2: len 7; hex 160000003b01ca; asc     ;  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9045 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002355; asc     #U;;
 2: len 7; hex 160000003b01ca; asc     ;  ;;
 3: len 4; hex 8000002a; asc    *;;

2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9045, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777944 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9045 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000235b; asc     #[;;
 2: len 7; hex 190000003601ca; asc     6  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9051 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000235b; asc     #[;;
 2: len 7; hex 190000003601ca; asc     6  ;;
 3: len 4; hex 80000020; asc     ;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:08 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9054, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777954 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9054 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002357; asc     #W;;
 2: len 7; hex 17000000330110; asc     3  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9047 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002357; asc     #W;;
 2: len 7; hex 17000000330110; asc     3  ;;
 3: len 4; hex 8000002b; asc    +;;

2026-01-20 14:19:08 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9047, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777953 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:08 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9047 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000235e; asc     #^;;
 2: len 7; hex 1a0000003401ca; asc     4  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9054 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000235e; asc     #^;;
 2: len 7; hex 1a0000003401ca; asc     4  ;;
 3: len 4; hex 80000021; asc    !;;

2026-01-20 14:19:08 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:09 2254 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:09 2254 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9063, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 777973 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:09 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9063 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002362; asc     #b;;
 2: len 7; hex 1c0000002e0110; asc     .  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 14:19:09 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9058 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002362; asc     #b;;
 2: len 7; hex 1c0000002e0110; asc     .  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 14:19:09 2254 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9058, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 777972 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:09 2254 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9058 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002367; asc     #g;;
 2: len 7; hex 1f0000003701ca; asc     7  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 14:19:09 2254 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9063 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002367; asc     #g;;
 2: len 7; hex 1f0000003701ca; asc     7  ;;
 3: len 4; hex 80000024; asc    $;;

2026-01-20 14:19:09 2254 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:10 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:10 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9069, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 777987 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:10 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9069 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002365; asc     #e;;
 2: len 7; hex 1e0000003a0110; asc     :  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 14:19:10 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9061 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002365; asc     #e;;
 2: len 7; hex 1e0000003a0110; asc     :  ;;
 3: len 4; hex 80000030; asc    0;;

2026-01-20 14:19:10 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9061, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 777986 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:10 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9061 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000236d; asc     #m;;
 2: len 7; hex 220000003b0110; asc "   ;  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 14:19:10 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9069 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000236d; asc     #m;;
 2: len 7; hex 220000003b0110; asc "   ;  ;;
 3: len 4; hex 80000026; asc    &;;

2026-01-20 14:19:10 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:10 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:10 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9077, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 778006 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:10 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9077 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002370; asc     #p;;
 2: len 7; hex 230000008001ca; asc #      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:19:10 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9072 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002370; asc     #p;;
 2: len 7; hex 230000008001ca; asc #      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:19:10 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9072, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 778005 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:10 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9072 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002375; asc     #u;;
 2: len 7; hex 260000008201ca; asc &      ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:10 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9077 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002375; asc     #u;;
 2: len 7; hex 260000008201ca; asc &      ;;
 3: len 4; hex 80000029; asc    );;

2026-01-20 14:19:10 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:11 2257 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:11 2257 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9087, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2257, OS thread handle 137749198591680, query id 778030 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:11 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9087 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002379; asc     #y;;
 2: len 7; hex 280000003801ca; asc (   8  ;;
 3: len 4; hex 80000037; asc    7;;

2026-01-20 14:19:11 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9081 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000002379; asc     #y;;
 2: len 7; hex 280000003801ca; asc (   8  ;;
 3: len 4; hex 80000037; asc    7;;

2026-01-20 14:19:11 2257 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9081, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 778029 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:11 2257 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9081 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000237f; asc     # ;;
 2: len 7; hex 2b0000002e0110; asc +   .  ;;
 3: len 4; hex 8000002d; asc    -;;

2026-01-20 14:19:11 2257 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9087 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 00000000237f; asc     # ;;
 2: len 7; hex 2b0000002e0110; asc +   .  ;;
 3: len 4; hex 8000002d; asc    -;;

2026-01-20 14:19:11 2257 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:11 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:11 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9091, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 778039 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:11 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9091 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000237b; asc     #{;;
 2: len 7; hex 29000000310110; asc )   1  ;;
 3: len 4; hex 80000038; asc    8;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9083 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000237b; asc     #{;;
 2: len 7; hex 29000000310110; asc )   1  ;;
 3: len 4; hex 80000038; asc    8;;

2026-01-20 14:19:11 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9083, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2255, OS thread handle 137749199206080, query id 778038 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:11 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9083 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002383; asc     # ;;
 2: len 7; hex 2d0000003c01ca; asc -   <  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9091 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002383; asc     # ;;
 2: len 7; hex 2d0000003c01ca; asc -   <  ;;
 3: len 4; hex 8000002e; asc    .;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:19:11 2256 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:19:11 2256 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 9094, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2256, OS thread handle 137748795619008, query id 778048 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:19:11 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9094 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000237d; asc     #};;
 2: len 7; hex 2a0000002d0110; asc *   -  ;;
 3: len 4; hex 80000039; asc    9;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9085 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 00000000237d; asc     #};;
 2: len 7; hex 2a0000002d0110; asc *   -  ;;
 3: len 4; hex 80000039; asc    9;;

2026-01-20 14:19:11 2256 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 9085, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2254, OS thread handle 137748422940352, query id 778047 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:19:11 2256 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9085 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002386; asc     # ;;
 2: len 7; hex 2e0000003001ca; asc .   0  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 276 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 9094 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000002386; asc     # ;;
 2: len 7; hex 2e0000003001ca; asc .   0  ;;
 3: len 4; hex 8000002f; asc    /;;

2026-01-20 14:19:11 2256 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)


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
        if not string.match(file_path, "setup.sql$") then
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