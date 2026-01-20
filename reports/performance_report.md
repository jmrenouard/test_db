# SQL Performance Report - employees

Generated: 2026-01-15 22:48:07

| ID | Time (s) | Rating | Issues | Suggestions |
|---|---|---|---|---|
| 1 | 0.9994 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 2 | 0.3568 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: hire_date |
| 3 | 0.2267 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: last_name |
| 4 | 0.4107 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Query seems well-optimized. |
| 5 | 0.2161 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: birth_date, gender |
| 6 | 0.2623 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 7 | 0.2711 | ⭐⭐⭐⭐ | Filesort used (performance impact). | Add an index on columns used in ORDER BY. |
| 8 | 0.2759 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 9 | 0.2625 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: to_date |
| 10 | 0.6453 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 11 | 0.2918 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: to_date |
| 12 | 0.3813 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 13 | 4.3184 | ⭐⭐ | Full Table Scan (ALL) detected. | Query is slow, consider partitioning or pre-aggregating data. |
| 14 | 0.3717 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 15 | 0.7702 | ⭐⭐ | Full Table Scan (ALL) detected., Filesort used (performance impact). | Add an index on columns used in ORDER BY. |
| 16 | 0.2308 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: to_date |
| 17 | 0.5582 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: salary, to_date |
| 18 | 1.0564 | ⭐⭐⭐⭐ | None | Query is slow, consider partitioning or pre-aggregating data. |
| 19 | 2.4383 | ⭐⭐ | Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 20 | 0.2560 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 21 | 1.6933 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 22 | 1.8149 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 23 | 0.6816 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 24 | 0.6595 | ⭐⭐ | Full Table Scan (ALL) detected., Filesort used (performance impact). | Add an index on columns used in ORDER BY. |
| 25 | 3.9289 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 26 | -1.4080 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 27 | 1.0935 | ⭐⭐ | Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 28 | 1.7961 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 29 | 3.6211 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 30 | 6.4337 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 31 | 0.3117 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Query seems well-optimized. |
| 32 | 0.2578 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Query seems well-optimized. |
| 33 | 0.4824 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 34 | 3.7624 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 35 | 0.3616 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 36 | 3.0984 | ⭐⭐⭐⭐ | None | Query is slow, consider partitioning or pre-aggregating data. |
| 37 | 5.8588 | ⭐⭐ | Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 38 | 0.5470 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 39 | 0.6703 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 40 | 0.2866 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 41 | 2.4292 | ⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: from_date, FROM, emp_no, JO, M, curr_sal, to_date, Query is slow, consider partitioning or pre-aggregating data. |
| 42 | 0.6971 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 43 | 0.2579 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 44 | 3.1052 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 45 | 0.3892 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 46 | 0.2506 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 47 | 0.8328 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: row_id, to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 48 | 2.0853 | ⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: birth_date, to_date, Query is slow, consider partitioning or pre-aggregating data. |
| 49 | 0.4199 | ⭐⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: DIST, y, Optimize GROUP BY or DISTINCT to avoid temporary tables. |
| 50 | 1.7795 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: p_rank, to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 51 | 5.0355 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 52 | 0.2889 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Consider indexing: from_date |
| 53 | 1.1422 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY., Query is slow, consider partitioning or pre-aggregating data. |
| 54 | 0.5290 | ⭐⭐⭐⭐⭐ | None | Query seems well-optimized. |
| 55 | 0.6871 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 56 | 1.2668 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 57 | 0.2031 | ⭐⭐⭐ | Full Table Scan (ALL) detected. | Query seems well-optimized. |
| 58 | 0.4185 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |
| 59 | 1.1336 | ⭐ | Full Table Scan (ALL) detected., Temporary table used. | Consider indexing: last_hired, Optimize GROUP BY or DISTINCT to avoid temporary tables., Query is slow, consider partitioning or pre-aggregating data. |
| 60 | 2.1571 | ⭐ | Full Table Scan (ALL) detected., Temporary table used., Filesort used (performance impact). | Consider indexing: to_date, Optimize GROUP BY or DISTINCT to avoid temporary tables., Add an index on columns used in ORDER BY. |