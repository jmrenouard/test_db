# 📊 DB Simulation: GAP_LOCKING
**Generated:** 2026-01-20 15:15:34

## Connection Info
- **Host:** `127.0.0.1`
- **Database:** `employees`
- **Threads:** `4`
- **Duration:** `10s`

## Key Metrics
| Metric | Value |
|---|---|
| **TPS** | 59.28 |
| **QPS** | 197.04 |
| **Avg Latency** | 67.36 ms |
| **95th Latency** | 155.80 ms |
| **Total Events** | 599 |

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
The simulation triggered 67 deadlock(s).

```text
*** (1) TRANSACTION:

TRANSACTION 6466, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2227, OS thread handle 137748795619008, query id 578485 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:14:59 2227 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6466 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001940; asc      @;;
 2: len 7; hex 6e0000003a01ca; asc n   :  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:14:59 2227 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6464 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001940; asc      @;;
 2: len 7; hex 6e0000003a01ca; asc n   :  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:14:59 2227 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6464, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2224, OS thread handle 137748422940352, query id 578484 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:14:59 2227 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6464 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001942; asc      B;;
 2: len 7; hex 6f0000002f0110; asc o   /  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:14:59 2227 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6466 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001942; asc      B;;
 2: len 7; hex 6f0000002f0110; asc o   /  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:14:59 2227 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 6467, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2225, OS thread handle 137749199206080, query id 578489 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:14:59 2225 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6467 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001940; asc      @;;
 2: len 7; hex 6e0000003a01ca; asc n   :  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:14:59 2225 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6464 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001940; asc      @;;
 2: len 7; hex 6e0000003a01ca; asc n   :  ;;
 3: len 4; hex 80000015; asc     ;;

2026-01-20 14:14:59 2225 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6464, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2224, OS thread handle 137748422940352, query id 578484 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:14:59 2225 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6464 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001943; asc      C;;
 2: len 7; hex 700000002e0110; asc p   .  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:14:59 2225 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6467 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001943; asc      C;;
 2: len 7; hex 700000002e0110; asc p   .  ;;
 3: len 4; hex 8000000b; asc     ;;

2026-01-20 14:14:59 2225 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
```

```text
*** (1) TRANSACTION:

TRANSACTION 6465, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2226, OS thread handle 137749198591680, query id 578498 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:14:59 2226 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6465 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001945; asc      E;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:14:59 2226 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6469 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001945; asc      E;;
 2: len 7; hex 710000002e0110; asc q   .  ;;
 3: len 4; hex 8000000c; asc     ;;

2026-01-20 14:14:59 2226 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6469, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2227, OS thread handle 137748795619008, query id 578497 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:14:59 2226 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6469 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001941; asc      A;;
 2: len 7; hex 6d0000003d0110; asc m   =  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:14:59 2226 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 270 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6465 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001941; asc      A;;
 2: len 7; hex 6d0000003d0110; asc m   =  ;;
 3: len 4; hex 80000016; asc     ;;

2026-01-20 14:14:59 2226 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)
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
2026-01-20 14:15:31 2231 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:31 2231 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6737, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579088 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:31 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6737 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4b; asc      K;;
 2: len 7; hex 740000003001ca; asc t   0  ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 14:15:31 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6731 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4b; asc      K;;
 2: len 7; hex 740000003001ca; asc t   0  ;;
 3: len 4; hex 80000031; asc    1;;

2026-01-20 14:15:31 2231 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6731, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2233, OS thread handle 137749199206080, query id 579087 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:31 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6731 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a51; asc      Q;;
 2: len 7; hex 77000000350110; asc w   5  ;;
 3: len 4; hex 8000003b; asc    ;;;

2026-01-20 14:15:31 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6737 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a51; asc      Q;;
 2: len 7; hex 77000000350110; asc w   5  ;;
 3: len 4; hex 8000003b; asc    ;;;

2026-01-20 14:15:31 2231 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:31 2233 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:31 2233 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6741, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2233, OS thread handle 137749199206080, query id 579097 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:31 2233 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6741 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4d; asc      M;;
 2: len 7; hex 750000003801ca; asc u   8  ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6733 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4d; asc      M;;
 2: len 7; hex 750000003801ca; asc u   8  ;;
 3: len 4; hex 80000032; asc    2;;

2026-01-20 14:15:31 2233 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6733, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2230, OS thread handle 137748795619008, query id 579096 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:31 2233 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6733 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a55; asc      U;;
 2: len 7; hex 79000000c401ca; asc y      ;;
 3: len 4; hex 8000003c; asc    <;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6741 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a55; asc      U;;
 2: len 7; hex 79000000c401ca; asc y      ;;
 3: len 4; hex 8000003c; asc    <;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:31 2233 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:31 2233 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6744, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2233, OS thread handle 137749199206080, query id 579106 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:31 2233 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6744 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4f; asc      O;;
 2: len 7; hex 76000000c301ca; asc v      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6735 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4f; asc      O;;
 2: len 7; hex 76000000c301ca; asc v      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:15:31 2233 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6735, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2232, OS thread handle 137749198591680, query id 579105 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:31 2233 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6735 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a58; asc      X;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 8000003d; asc    =;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6744 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a58; asc      X;;
 2: len 7; hex 7a0000003301ca; asc z   3  ;;
 3: len 4; hex 8000003d; asc    =;;

2026-01-20 14:15:31 2233 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:32 2230 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:32 2230 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6745, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2230, OS thread handle 137748795619008, query id 579110 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:32 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6745 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4f; asc      O;;
 2: len 7; hex 76000000c301ca; asc v      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:15:32 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6735 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a4f; asc      O;;
 2: len 7; hex 76000000c301ca; asc v      ;;
 3: len 4; hex 80000033; asc    3;;

2026-01-20 14:15:32 2230 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6735, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2232, OS thread handle 137749198591680, query id 579105 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:32 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6735 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a59; asc      Y;;
 2: len 7; hex 7b0000003901ca; asc {   9  ;;
 3: len 4; hex 8000003d; asc    =;;

2026-01-20 14:15:32 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6745 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a59; asc      Y;;
 2: len 7; hex 7b0000003901ca; asc {   9  ;;
 3: len 4; hex 8000003d; asc    =;;

2026-01-20 14:15:32 2230 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:32 2231 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:32 2231 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6753, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579124 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:32 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6753 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a5b; asc      [;;
 2: len 7; hex 7c0000002e0110; asc |   .  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 14:15:32 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6747 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a5b; asc      [;;
 2: len 7; hex 7c0000002e0110; asc |   .  ;;
 3: len 4; hex 80000035; asc    5;;

2026-01-20 14:15:32 2231 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6747, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2233, OS thread handle 137749199206080, query id 579123 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:32 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6747 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a61; asc      a;;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 8000003f; asc    ?;;

2026-01-20 14:15:32 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6753 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a61; asc      a;;
 2: len 7; hex 7f000000c701ca; asc        ;;
 3: len 4; hex 8000003f; asc    ?;;

2026-01-20 14:15:32 2231 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:33 2232 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:33 2232 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6761, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2232, OS thread handle 137749198591680, query id 579143 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:33 2232 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6761 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a64; asc      d;;
 2: len 7; hex 01000000310110; asc     1  ;;
 3: len 4; hex 80000038; asc    8;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6756 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a64; asc      d;;
 2: len 7; hex 01000000310110; asc     1  ;;
 3: len 4; hex 80000038; asc    8;;

2026-01-20 14:15:33 2232 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6756, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579142 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:33 2232 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6756 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a69; asc      i;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000042; asc    B;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6761 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a69; asc      i;;
 2: len 7; hex 030000003b01ca; asc     ;  ;;
 3: len 4; hex 80000042; asc    B;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:33 2231 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:33 2231 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6765, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579152 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:33 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6765 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a65; asc      e;;
 2: len 7; hex 0100000031020e; asc     1  ;;
 3: len 4; hex 80000039; asc    9;;

2026-01-20 14:15:33 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6757 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a65; asc      e;;
 2: len 7; hex 0100000031020e; asc     1  ;;
 3: len 4; hex 80000039; asc    9;;

2026-01-20 14:15:33 2231 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6757, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2233, OS thread handle 137749199206080, query id 579151 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:33 2231 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6757 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a6d; asc      m;;
 2: len 7; hex 050000003c01ca; asc     <  ;;
 3: len 4; hex 80000043; asc    C;;

2026-01-20 14:15:33 2231 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6765 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a6d; asc      m;;
 2: len 7; hex 050000003c01ca; asc     <  ;;
 3: len 4; hex 80000043; asc    C;;

2026-01-20 14:15:33 2231 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:33 2230 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:33 2230 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6759, ACTIVE 1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2230, OS thread handle 137748795619008, query id 579160 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:33 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6759 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a70; asc      p;;
 2: len 7; hex 060000002f0110; asc     /  ;;
 3: len 4; hex 80000044; asc    D;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6768 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a70; asc      p;;
 2: len 7; hex 060000002f0110; asc     /  ;;
 3: len 4; hex 80000044; asc    D;;

2026-01-20 14:15:33 2230 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6768, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579159 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:33 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6768 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a67; asc      g;;
 2: len 7; hex 02000000300110; asc     0  ;;
 3: len 4; hex 8000003a; asc    :;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6759 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a67; asc      g;;
 2: len 7; hex 02000000300110; asc     0  ;;
 3: len 4; hex 8000003a; asc    :;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:33 2232 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:33 2232 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6764, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2232, OS thread handle 137749198591680, query id 579164 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:33 2232 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6764 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a70; asc      p;;
 2: len 7; hex 060000002f0110; asc     /  ;;
 3: len 4; hex 80000044; asc    D;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6768 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a70; asc      p;;
 2: len 7; hex 060000002f0110; asc     /  ;;
 3: len 4; hex 80000044; asc    D;;

2026-01-20 14:15:33 2232 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6768, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2231, OS thread handle 137748422940352, query id 579159 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:33 2232 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6768 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a6c; asc      l;;
 2: len 7; hex 04000000c801ca; asc        ;;
 3: len 4; hex 8000003a; asc    :;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6764 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a6c; asc      l;;
 2: len 7; hex 04000000c801ca; asc        ;;
 3: len 4; hex 8000003a; asc    :;;

2026-01-20 14:15:33 2232 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)

2026-01-20 14:15:33 2230 [Note] InnoDB: Transactions deadlock detected, dumping detailed information.
2026-01-20 14:15:33 2230 [Note] InnoDB: 
*** (1) TRANSACTION:

TRANSACTION 6770, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2230, OS thread handle 137748795619008, query id 579172 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 2
2026-01-20 14:15:33 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6770 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a75; asc      u;;
 2: len 7; hex 080000003b01ca; asc     ;  ;;
 3: len 4; hex 80000045; asc    E;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6773 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     ;;
 1: len 6; hex 000000001a75; asc      u;;
 2: len 7; hex 080000003b01ca; asc     ;  ;;
 3: len 4; hex 80000045; asc    E;;

2026-01-20 14:15:33 2230 [Note] InnoDB: 
*** (2) TRANSACTION:

TRANSACTION 6773, ACTIVE 0 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1120, 2 row lock(s), undo log entries 1
MariaDB thread id 2232, OS thread handle 137749198591680, query id 579171 127.0.0.1 root Updating
UPDATE deadlock_test SET val = val + 1 WHERE id = 1
2026-01-20 14:15:33 2230 [Note] InnoDB: *** WAITING FOR THIS LOCK TO BE GRANTED:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6773 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a72; asc      r;;
 2: len 7; hex 070000002e0110; asc     .  ;;
 3: len 4; hex 8000003b; asc    ;;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** CONFLICTING WITH:

RECORD LOCKS space id 271 page no 3 n bits 320 index PRIMARY of table `employees`.`deadlock_test` trx id 6770 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000001a72; asc      r;;
 2: len 7; hex 070000002e0110; asc     .  ;;
 3: len 4; hex 8000003b; asc    ;;;

2026-01-20 14:15:33 2230 [Note] InnoDB: *** WE ROLL BACK TRANSACTION (2)


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
#### trans_insert_gap.sql
```sql
-- Transaction attempting to insert into a locked gap
BEGIN;
-- Use IGNORE to prevent crash on duplicate, but it will still WAIT if there is a gap lock
INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'Intruder');
COMMIT;

```
#### trans_lock_range.sql
```sql
-- Transaction locking a range (gap)
BEGIN;
-- This will lock the gap between 10 and 20 (and the record 20)
SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE;
-- Simulate processing time to allow conflict
SELECT SLEEP(0.05);
COMMIT;

```
#### trans_insert_child.sql
```sql
-- Transaction inserting into child (fk check should also be affected by gap lock)
BEGIN;
INSERT IGNORE INTO gap_child (id, parent_id, description) VALUES (100, 20, 'Child of locked Node');
COMMIT;

```
#### setup.sql
```sql
-- Setup tables for gap locking demonstration
DROP TABLE IF EXISTS gap_child;
DROP TABLE IF EXISTS gap_parent;

CREATE TABLE gap_parent (
    id INT PRIMARY KEY,
    name VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE gap_child (
    id INT PRIMARY KEY,
    parent_id INT,
    description VARCHAR(100),
    FOREIGN KEY (parent_id) REFERENCES gap_parent(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insert sparse data to create gaps
INSERT INTO gap_parent (id, name) VALUES (10, 'Node 10'), (20, 'Node 20'), (30, 'Node 30');
INSERT INTO gap_child (id, parent_id, description) VALUES (1, 10, 'Child 1'), (2, 20, 'Child 2');

```