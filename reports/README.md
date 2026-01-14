# 📊 Reports Directory

This directory contains automatically generated reports and analysis from the test suite and performance benchmarks.

## 📂 Contents

### 1. `performance_report.md`

A Markdown summary of the latest SQL performance analysis, including execution times and identified query issues (like full table scans).

### 2. `explain_reports/`

Detailed `EXPLAIN` plans for each query analyzed. Each file (`query_XX.txt`) includes the original query, the tabular EXPLAIN plan, and an analysis of potential performance bottlenecks.

---

## 🚀 How to generate these reports

You can regenerate these reports at any time using the `Makefile` in the root directory:

```bash
make analyze
```

For a complete test run (including data verification and sysbench):

```bash
make test-all
```

## 🧹 Maintenance

To clear generated reports and start fresh:

```bash
make clean
```
