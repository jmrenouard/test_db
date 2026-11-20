# Documentation Index

Welcome to the `test_db` technical documentation. This documentation covers the architecture, tooling, and benchmarking practices of the MariaDB testing environment.

Please follow the guides in order, or jump directly to a topic of interest:

## 1. Environment & Tools

1. [MariaDB Management](mariadb_management.md) - Container lifecycle, environment setup, and data injection.
2. [Tools Guide](tools_guide.md) - Overview of Sysbench, Python analyzers, and the general testing architecture.
3. [Interactive Reporting & Dashboards](interactive_reporting.md) - Using `make interactive` and viewing HTML/Tailwind CSS reports.

## 2. Performance & Analysis

1. [Benchmarking & Sysbench](benchmarking.md) - Deep dive into scalable benchmarking and metrics glossary.
2. [SQL Analyzer](sql_analyzer.md) - Using the AI-assisted SQL query analyzer and missing index generation.

## 3. Concurrency Experiments

1. [Deadlock Experiment](deadlock_experiment.md) - Simulating and tracking wait-for-graph deadlocks.
2. [Gap Locking Experiment](gap_locking_experiment.md) - Demonstrating InnoDB gap locks on non-unique indexes.

## 4. Sirene PostgreSQL 18 3NF Platform

1. [Sirene PostgreSQL 18 3NF Platform Guide](sirene_platform.md) - Architecture, 13-table 3NF schema, `pg_trgm` GIN indexes, Python ETL CLI/Docker operations, multi-master qualification (`mm_probe.py`), and 15 SQL queries.
2. [Interactive HTML Reference](../sirene_documentation.html) - Self-contained interactive PostgreSQL 18 schema explorer, SVG diagrams, multi-master probe reference, and searchable SQL query catalog with one-click copy.

---
*Back to [Main Repository README](../../README.md)*
