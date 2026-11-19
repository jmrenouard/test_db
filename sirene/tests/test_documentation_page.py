"""Tests verifying Sirene HTML and bilingual Markdown documentation deliverables."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re

import pytest

pytestmark = pytest.mark.governance

REQUIRED_TABLES: tuple[str, ...] = (
    "ref_regions",
    "ref_departements",
    "ref_communes",
    "ref_pays",
    "ref_naf",
    "ref_categories_juridiques",
    "ref_tranches_effectifs",
    "unites_legales",
    "etablissements",
    "etablissements_historique_etat",
    "personnes",
    "roles_entreprises",
    "etl_logs",
)

REQUIRED_GIN_INDEXES: tuple[str, ...] = (
    "idx_ul_nom_trgm",
    "idx_etab_enseigne_trgm",
    "idx_personnes_nom_trgm",
)

REQUIRED_ETL_MODULES: tuple[str, ...] = (
    "full_import.py",
    "incremental_import.py",
    "watcher.py",
    "config.py",
    "db.py",
    "downloader.py",
    "referentials.py",
    "transforms.py",
)

HOST_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    re.compile(r"[A-Za-z]:/Users/", re.IGNORECASE),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
)

MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class _BalancedSectionHTMLParser(HTMLParser):
    """HTML5 parser verifying balanced structural tags and capturing script/style/pre content."""

    TRACKED_TAGS = frozenset({"style", "script", "table", "section"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.tag_counts: dict[str, int] = {tag: 0 for tag in self.TRACKED_TAGS}
        self.unbalanced_errors: list[str] = []
        self.scripts: list[str] = []
        self.pre_blocks: list[str] = []
        self._in_script = False
        self._current_script: list[str] = []
        self._pre_depth = 0
        self._current_pre: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        if lower in self.TRACKED_TAGS:
            self.stack.append(lower)
            self.tag_counts[lower] += 1
        if lower == "script":
            self._in_script = True
            self._current_script = []
        elif lower == "pre":
            self._pre_depth += 1
            if self._pre_depth == 1:
                self._current_pre = []

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower == "script" and self._in_script:
            self.scripts.append("".join(self._current_script))
            self._in_script = False
            self._current_script = []
        elif lower == "pre" and self._pre_depth > 0:
            self._pre_depth -= 1
            if self._pre_depth == 0:
                self.pre_blocks.append("".join(self._current_pre))
                self._current_pre = []

        if lower in self.TRACKED_TAGS:
            if not self.stack:
                self.unbalanced_errors.append(
                    f"Unexpected closing </{lower}> with empty stack"
                )
            elif self.stack[-1] != lower:
                self.unbalanced_errors.append(
                    f"Mismatched closing </{lower}>; expected </{self.stack[-1]}>"
                )
                if lower in self.stack:
                    while self.stack and self.stack[-1] != lower:
                        self.stack.pop()
                    if self.stack:
                        self.stack.pop()
            else:
                self.stack.pop()

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._current_script.append(data)
        if self._pre_depth > 0:
            self._current_pre.append(data)


def _doc_files(repo_root: Path) -> dict[str, Path]:
    return {
        "html": repo_root / "documentation" / "sirene_documentation.html",
        "en_md": repo_root / "documentation" / "en" / "sirene_platform.md",
        "fr_md": repo_root / "documentation" / "fr" / "sirene_platform.md",
    }


def test_documentation_files_exist_and_non_empty(repo_root: Path) -> None:
    """Verify the HTML reference and bilingual Markdown guides exist and are non-empty."""
    for label, path in _doc_files(repo_root).items():
        assert path.is_file(), f"Missing documentation file ({label}): {path}"
        content = path.read_text(encoding="utf-8").strip()
        assert len(content) > 500, f"Documentation file ({label}) is unexpectedly short"


def test_all_tables_indexes_and_etl_modules_documented(repo_root: Path) -> None:
    """Ensure all 13 tables, 3 pg_trgm GIN indexes, and 8 ETL modules appear in every doc."""
    required_symbols = REQUIRED_TABLES + REQUIRED_GIN_INDEXES + REQUIRED_ETL_MODULES
    for label, path in _doc_files(repo_root).items():
        content = path.read_text(encoding="utf-8")
        missing = [symbol for symbol in required_symbols if symbol not in content]
        assert not missing, f"Missing documented symbols in {label} ({path.name}): {missing}"


def test_html_documentation_structure_copy_js_and_15_queries(repo_root: Path) -> None:
    """Verify HTML5 tag balance, inline self-containment, copy-SQL JS, and >= 15 SQL queries."""
    html_path = _doc_files(repo_root)["html"]
    content = html_path.read_text(encoding="utf-8")

    parser = _BalancedSectionHTMLParser()
    parser.feed(content)
    parser.close()

    assert not parser.unbalanced_errors, (
        f"HTML tag balance errors: {parser.unbalanced_errors}"
    )
    assert not parser.stack, f"Unclosed tracked HTML tags: {parser.stack}"
    assert parser.tag_counts["style"] >= 1, "Expected inline <style> block"
    assert parser.tag_counts["script"] >= 1, "Expected inline <script> block"
    assert parser.tag_counts["table"] >= 1, "Expected schema/reference <table> blocks"
    assert parser.tag_counts["section"] >= 1, "Expected <section> blocks"

    # Self-contained check: zero external CDN stylesheet/script dependencies
    assert not re.search(
        r"<(?:script|link)\b[^>]*(?:src|href)=[\"']https?://",
        content,
        re.IGNORECASE,
    ), "External CDN <script> or <link> dependency detected in sirene_documentation.html"

    # Copy-SQL JavaScript capability
    combined_scripts = "\n".join(parser.scripts)
    assert "clipboard" in combined_scripts or "execCommand" in combined_scripts, (
        "Copy-SQL JS implementation missing from sirene_documentation.html"
    )

    # At least 15 SQL query blocks (either rendered <pre> blocks or JS query definitions)
    sql_pre_blocks = [
        block
        for block in parser.pre_blocks
        if re.search(r"\bSELECT\b", block, re.IGNORECASE)
        and re.search(r"\bFROM\b", block, re.IGNORECASE)
    ]
    js_sql_blocks = re.findall(
        r"(?:`[^`]*\bSELECT\b[^`]*\bFROM\b[^`]*`|"
        r'"[^"]*\bSELECT\b[^"]*\bFROM\b[^"]*"|'
        r"'[^']*\bSELECT\b[^']*\bFROM\b[^']*')",
        combined_scripts,
        re.IGNORECASE | re.DOTALL,
    )
    total_sql_blocks = max(len(sql_pre_blocks), len(js_sql_blocks))
    assert total_sql_blocks >= 15, (
        f"Expected >= 15 SQL query blocks in HTML doc; found pre={len(sql_pre_blocks)}, js={len(js_sql_blocks)}"
    )


def test_documentation_files_have_zero_local_host_paths(repo_root: Path) -> None:
    """Verify none of the new documentation files leak local workstation paths."""
    for label, path in _doc_files(repo_root).items():
        content = path.read_text(encoding="utf-8")
        for pattern in HOST_PATH_PATTERNS:
            assert not pattern.search(
                content
            ), f"Local host path pattern {pattern.pattern!r} found in {label}"


def test_navigation_links_across_indexes_and_readmes(repo_root: Path) -> None:
    """Verify links to Sirene docs in indexes and READMEs point to valid existing files."""
    files_to_check = (
        repo_root / "documentation" / "en" / "index.md",
        repo_root / "documentation" / "fr" / "index.md",
        repo_root / "README.md",
        repo_root / "README_fr.md",
        repo_root / "sirene" / "README.md",
        repo_root / "documentation" / "en" / "sirene_platform.md",
        repo_root / "documentation" / "fr" / "sirene_platform.md",
    )

    for md_path in files_to_check:
        assert md_path.is_file(), f"Expected Markdown file missing: {md_path}"
        content = md_path.read_text(encoding="utf-8")
        targets = [
            match.group(1).strip()
            for match in MD_LINK_RE.finditer(content)
            if "sirene_platform.md" in match.group(1)
            or "sirene_documentation.html" in match.group(1)
            or (
                md_path.name == "sirene_platform.md"
                and not match.group(1).startswith(("http://", "https://", "#", "mailto:"))
            )
        ]

        if md_path.name in {"index.md", "README.md", "README_fr.md"}:
            assert any(
                "sirene_platform.md" in t or "sirene_documentation.html" in t
                for t in targets
            ), f"Missing Sirene documentation link in {md_path.relative_to(repo_root)}"

        for raw_target in targets:
            rel_target = raw_target.split("#", 1)[0].strip()
            if not rel_target:
                continue
            resolved = (md_path.parent / rel_target).resolve()
            assert resolved.exists(), (
                f"Broken documentation link {raw_target!r} in {md_path.relative_to(repo_root)}"
            )
