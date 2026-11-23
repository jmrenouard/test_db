"""Executable validation tests for Diataxis EN/FR tutorials and how-to guides.

These tests verify:
- Every Makefile target and repository file path referenced in tutorials/how-tos exists.
- Documented CLI entrypoints parse safely and produce expected dry-run or help output.
- Shell scripts pass ``bash -n`` syntax validation cleanly (LF-normalized).
- SQL workloads and Docker Compose topologies match documented schemas and services.
- All tutorials contain column-0 Mermaid diagrams, zero ASCII box diagrams, and strict EN/FR isolation.
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DOCS_FR_DIR = DOCS_DIR / "fr"

TUTORIAL_AND_HOWTO_DIRS: tuple[Path, ...] = (
    DOCS_DIR / "01-tutorials",
    DOCS_DIR / "02-how-to-guides",
    DOCS_FR_DIR / "01-tutoriels",
    DOCS_FR_DIR / "02-guides-pratiques",
)

EN_TUTORIAL_FILES: tuple[Path, ...] = (
    DOCS_DIR / "01-tutorials" / "01-mariadb-employees-sandbox.md",
    DOCS_DIR / "01-tutorials" / "02-sirene-postgresql18-offline-lab.md",
    DOCS_DIR / "01-tutorials" / "03-concurrency-and-benchmarking-lab.md",
)

FR_TUTORIAL_FILES: tuple[Path, ...] = (
    DOCS_FR_DIR / "01-tutoriels" / "01-bac-a-sable-mariadb-employees.md",
    DOCS_FR_DIR / "01-tutoriels" / "02-lab-sirene-postgresql18-hors-ligne.md",
    DOCS_FR_DIR / "01-tutoriels" / "03-lab-concurrence-et-benchmarks.md",
)

MAKEFILE_TARGET_RE = re.compile(r"(?:^|\s|`)make\s+([A-Za-z0-9_-]+)")
REPO_PATH_REF_RE = re.compile(
    r"\b(?:scripts|sirene|employees|postgresql|tests)/[A-Za-z0-9_./-]+\.(?:py|sh|sql|lua|yml|yaml)\b"
)
MERMAID_COL0_RE = re.compile(r"^```mermaid\s*$", re.MULTILINE)
INDENTED_MERMAID_RE = re.compile(r"^[ \t]+```mermaid\b", re.MULTILINE)
ASCII_BOX_RE = re.compile(r"\+[=-]{3,}\+|[┌┐└┘╔╗╚╝][─━═]{2,}|[─━═]{2,}[┌┐└┘╔╗╚╝]")
FENCED_BLOCK_RE = re.compile(r"^[ \t]*```([A-Za-z0-9_-]*)\r?\n(.*?)^[ \t]*```", re.MULTILINE | re.DOTALL)


def _strip_sql_comments(sql_text: str) -> str:
    """Remove full-line ``--`` SQL comments before splitting statements."""
    return "\n".join(
        line for line in sql_text.splitlines() if not line.lstrip().startswith("--")
    )


def _check_balanced_parens(sql_text: str) -> bool:
    """Verify parentheses balance outside single-quoted SQL string literals."""
    depth = 0
    in_quote = False
    i = 0
    while i < len(sql_text):
        ch = sql_text[i]
        if ch == "'":
            if in_quote and i + 1 < len(sql_text) and sql_text[i + 1] == "'":
                i += 2
                continue
            in_quote = not in_quote
        elif not in_quote:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        i += 1
    return depth == 0 and not in_quote


def test_referenced_make_targets_and_repo_files_exist() -> None:
    """Ensure every make target and file path cited in EN/FR tutorials and how-tos exists."""
    makefile_text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    defined_targets = set(re.findall(r"^([A-Za-z0-9_.-]+):", makefile_text, re.MULTILINE))

    missing_targets: list[str] = []
    missing_files: list[str] = []

    for doc_dir in TUTORIAL_AND_HOWTO_DIRS:
        for md_file in sorted(doc_dir.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            rel_md = md_file.relative_to(REPO_ROOT).as_posix()
            for target in sorted(set(MAKEFILE_TARGET_RE.findall(text))):
                if target not in defined_targets:
                    missing_targets.append(f"{rel_md} -> make {target}")
            for ref in sorted(set(REPO_PATH_REF_RE.findall(text))):
                if not (REPO_ROOT / ref).exists():
                    missing_files.append(f"{rel_md} -> {ref}")

    assert not missing_targets, f"Unknown Makefile targets referenced in docs: {missing_targets}"
    assert not missing_files, f"Missing repository files referenced in docs: {missing_files}"


def test_python_cli_entrypoints_syntax_and_safe_execution() -> None:
    """Validate AST syntax and run safe non-mutating --help / --dry-run checks on documented scripts."""
    python_files = [
        REPO_ROOT / "interactive_runner.py",
        REPO_ROOT / "scripts" / "inject_fake_employees.py",
        REPO_ROOT / "scripts" / "db_simulator.py",
        REPO_ROOT / "scripts" / "sql_analyzer.py",
        REPO_ROOT / "scripts" / "perf_threads_reporter.py",
        REPO_ROOT / "scripts" / "mkdocs_hooks.py",
        REPO_ROOT / "scripts" / "build_versioned_docs.py",
        REPO_ROOT / "sirene" / "full_import.py",
        REPO_ROOT / "sirene" / "incremental_import.py",
        REPO_ROOT / "sirene" / "mm_probe.py",
        REPO_ROOT / "sirene" / "watcher.py",
        REPO_ROOT / "sirene" / "scripts" / "generate_synthetic_dataset.py",
    ]
    for py_file in python_files:
        assert py_file.exists(), f"Expected Python entrypoint missing: {py_file}"
        ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))

    dry_run = subprocess.run(
        [
            sys.executable,
            "scripts/inject_fake_employees.py",
            "--count",
            "5",
            "--dry-run",
            "--seed",
            "42",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry_run.returncode == 0, dry_run.stderr
    for token in ("INSERT INTO employees", "INSERT INTO dept_emp", "INSERT INTO titles", "INSERT INTO salaries", "COMMIT;"):
        assert token in dry_run.stdout, f"inject_fake_employees.py --dry-run missing {token}"

    help_expectations: dict[str, tuple[str, ...]] = {
        "scripts/db_simulator.py": ("--sql-dir", "--script", "--container", "--output-dir"),
        "scripts/sql_analyzer.py": ("--query-file", "--query", "--container"),
        "scripts/perf_threads_reporter.py": ("--dir", "--md", "--html"),
        "interactive_runner.py": ("-a", "--run-all"),
        "sirene/full_import.py": ("--offline-refs", "--limit-rows", "--force"),
        "sirene/incremental_import.py": ("--ul-file", "--etab-file", "--force"),
        "sirene/mm_probe.py": ("--dsn-a", "--dsn-b", "--setup-native-birep"),
    }
    for rel_script, expected_flags in help_expectations.items():
        proc = subprocess.run(
            [sys.executable, rel_script, "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, f"{rel_script} --help failed: {proc.stderr}"
        for flag in expected_flags:
            assert flag in proc.stdout, f"{rel_script} --help missing flag {flag}"


def test_documented_shell_scripts_pass_bash_syntax() -> None:
    """Validate all shell scripts referenced in tutorials and how-tos with bash -n."""
    bash_bin = shutil.which("bash")
    assert bash_bin is not None, "bash executable is required for shell script syntax checks"

    shell_scripts = [
        REPO_ROOT / "scripts" / "test_runner.sh",
        REPO_ROOT / "scripts" / "verify_data.sh",
        REPO_ROOT / "scripts" / "run_dir_bench.sh",
        REPO_ROOT / "postgresql" / "load_employees_db.sh",
        REPO_ROOT / "sirene" / "load_sirene_db.sh",
        REPO_ROOT / "tests" / "test_inject_fake.sh",
    ]
    for sh_file in shell_scripts:
        assert sh_file.exists(), f"Missing shell script: {sh_file}"
        # Pass LF-normalized bytes on stdin so Windows CRLF checkouts and WSL bash behave consistently.
        lf_bytes = sh_file.read_bytes().replace(b"\r\n", b"\n")
        res = subprocess.run([bash_bin, "-n"], input=lf_bytes, capture_output=True, check=False)
        assert res.returncode == 0, (
            f"bash -n failed for {sh_file.relative_to(REPO_ROOT).as_posix()}: "
            f"{res.stderr.decode('utf-8', 'replace')}"
        )


def test_documented_sql_workloads_and_schemas_valid() -> None:
    """Verify SQL query counts, DDL tables, and balanced syntax across tutorial SQL workloads."""
    req_sql = (REPO_ROOT / "employees" / "req_employees.sql").read_text(encoding="utf-8")
    req_stmts = [s.strip() for s in _strip_sql_comments(req_sql).split(";") if s.strip()]
    assert len(req_stmts) == 60, f"Expected 60 benchmark queries in employees/req_employees.sql, got {len(req_stmts)}"

    sirene_sample = (REPO_ROOT / "sirene" / "sql" / "03_sample_queries.sql").read_text(encoding="utf-8")
    query_headers = re.findall(r"--\s*Query\s+\d+:", sirene_sample)
    assert len(query_headers) == 15, f"Expected 15 query sections in 03_sample_queries.sql, got {len(query_headers)}"

    sql_files = [
        REPO_ROOT / "employees" / "employees.sql",
        REPO_ROOT / "employees" / "req_employees.sql",
        REPO_ROOT / "postgresql" / "employees.sql",
        REPO_ROOT / "sirene" / "sql" / "01_schema_3nf.sql",
        REPO_ROOT / "sirene" / "sql" / "02_indexes.sql",
        REPO_ROOT / "sirene" / "sql" / "03_sample_queries.sql",
        REPO_ROOT / "tests" / "data" / "deadlock" / "setup.sql",
        REPO_ROOT / "tests" / "data" / "deadlock" / "trans_cycle_1.sql",
        REPO_ROOT / "tests" / "data" / "deadlock" / "trans_cycle_2.sql",
        REPO_ROOT / "tests" / "data" / "deadlock" / "teardown.sql",
        REPO_ROOT / "tests" / "data" / "gap_locking" / "setup.sql",
        REPO_ROOT / "tests" / "data" / "gap_locking" / "trans_A.sql",
        REPO_ROOT / "tests" / "data" / "gap_locking" / "trans_B.sql",
        REPO_ROOT / "tests" / "data" / "gap_locking" / "teardown.sql",
    ]
    for sql_file in sql_files:
        assert sql_file.exists(), f"Missing documented SQL file: {sql_file}"
        raw = sql_file.read_text(encoding="utf-8")
        cleaned = _strip_sql_comments(raw).strip()
        assert cleaned, f"SQL file has no statements: {sql_file}"
        assert _check_balanced_parens(cleaned), f"Unbalanced parentheses or quotes in {sql_file}"


def test_sirene_compose_topologies_match_tutorials() -> None:
    """Validate Sirene Docker Compose services, localhost bindings, and PostgreSQL 18 mounts."""
    single_compose = yaml.safe_load((REPO_ROOT / "sirene" / "docker-compose.yml").read_text(encoding="utf-8"))
    single_services = single_compose["services"]
    for svc in ("sirene-postgres", "sirene-etl", "sirene-watcher"):
        assert svc in single_services, f"Missing service {svc} in sirene/docker-compose.yml"
    assert "daemon" in single_services["sirene-watcher"].get("profiles", [])
    pg_raw = (REPO_ROOT / "sirene" / "docker-compose.yml").read_text(encoding="utf-8")
    assert "127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432" in pg_raw
    assert "/var/lib/postgresql" in pg_raw

    mm_compose = yaml.safe_load((REPO_ROOT / "sirene" / "docker-compose.pg18-birep.yml").read_text(encoding="utf-8"))
    mm_services = mm_compose["services"]
    for svc in ("sirene-mm-node-a", "sirene-mm-node-b", "sirene-mm-probe"):
        assert svc in mm_services, f"Missing service {svc} in sirene/docker-compose.pg18-birep.yml"


def test_tutorials_have_col0_mermaid_and_zero_ascii_diagrams() -> None:
    """Require column-0 Mermaid diagrams in all EN/FR tutorials and forbid ASCII box diagrams."""
    for tutorial in (*EN_TUTORIAL_FILES, *FR_TUTORIAL_FILES):
        assert tutorial.exists(), f"Missing tutorial: {tutorial}"
        text = tutorial.read_text(encoding="utf-8")
        assert MERMAID_COL0_RE.search(text), f"Tutorial missing column-0 Mermaid block: {tutorial.name}"

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(REPO_ROOT).as_posix()
        assert not INDENTED_MERMAID_RE.search(text), f"Indented Mermaid fence found in {rel}"
        for match in FENCED_BLOCK_RE.finditer(text):
            lang = match.group(1).lower()
            body = match.group(2)
            if lang in {"mermaid", "psql", "sql", "mysql", "diff", "patch"}:
                continue
            assert not ASCII_BOX_RE.search(body), f"ASCII box diagram detected in {rel} (lang={lang or 'untagged'})"
