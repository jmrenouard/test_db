"""Unit and integration tests for versioned MkDocs Material publishing and IONOS deployment."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "docs-publish.yml"
MKDOCS_CONFIG_PATH = REPO_ROOT / "mkdocs.yml"
HOOKS_SCRIPT_PATH = REPO_ROOT / "scripts" / "mkdocs_hooks.py"
BUILD_SCRIPT_PATH = REPO_ROOT / "scripts" / "build_versioned_docs.py"
REQUIREMENTS_DOCS_PATH = REPO_ROOT / "requirements-docs.txt"
REQUIREMENTS_ROOT_PATH = REPO_ROOT / "requirements.txt"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"
MAKEFILE_PATH = REPO_ROOT / "Makefile"

PORTAL_BASE_URL = "https://test-db.lightpath.fr"
SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
RELEASE_TAGS: tuple[str, ...] = ("v1.11.0", "v1.10.0", "v1.9.1", "v1.9.0")


class _MkDocsYamlLoader(yaml.SafeLoader):
    """Safe YAML loader supporting PyMdownx `!!python/name:` tag references as strings."""


def _python_name_multi_constructor(
    loader: yaml.Loader,
    tag_suffix: str,
    node: yaml.Node,
) -> str:
    del loader, node
    return f"python/name:{tag_suffix}"


_MkDocsYamlLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:",
    _python_name_multi_constructor,
)


class _AttrDict(dict[str, Any]):
    """Dictionary exposing keys as attributes to mimic MkDocsConfig in hook unit tests."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value


class _FakeFile:
    """Minimal MkDocs File stand-in for `on_page_markdown` tests."""

    def __init__(self, src_uri: str) -> None:
        self.src_uri = src_uri
        self.src_path = src_uri


class _FakeFiles:
    """Minimal MkDocs Files collection stand-in for `on_page_markdown` tests."""

    def __init__(self, present: set[str] | None = None) -> None:
        self._present = present or set()

    def get_file_from_path(self, path: str) -> _FakeFile | None:
        return _FakeFile(path) if path in self._present else None


class _FakePage:
    """Minimal MkDocs Page stand-in for `on_page_markdown` tests."""

    def __init__(self, src_uri: str, edit_url: str | None = None) -> None:
        self.file = _FakeFile(src_uri)
        self.edit_url = edit_url


def _load_mkdocs_config() -> dict[str, Any]:
    assert MKDOCS_CONFIG_PATH.is_file(), "mkdocs.yml must exist at repository root"
    loader = _MkDocsYamlLoader(MKDOCS_CONFIG_PATH.read_text(encoding="utf-8"))
    try:
        parsed = loader.get_single_data()
    finally:
        loader.dispose()
    assert isinstance(parsed, dict), "mkdocs.yml must parse into a YAML mapping"
    return parsed


def _load_script_module(module_name: str, script_path: Path) -> ModuleType:
    assert script_path.is_file(), f"Missing script module: {script_path}"
    scripts_dir = str(script_path.parent)
    added_sys_path = False
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        added_sys_path = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        assert spec is not None and spec.loader is not None, f"Cannot load spec for {script_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if added_sys_path and scripts_dir in sys.path:
            sys.path.remove(scripts_dir)


def _flatten_nav_paths(node: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(node, str):
        paths.append(node)
    elif isinstance(node, list):
        for item in node:
            paths.extend(_flatten_nav_paths(item))
    elif isinstance(node, dict):
        for val in node.values():
            paths.extend(_flatten_nav_paths(val))
    return paths


def _find_nav_section(nav: list[Any], section_name: str) -> Any:
    for item in nav:
        if isinstance(item, dict) and section_name in item:
            return item[section_name]
    return None


def _collect_workflow_steps(job_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    steps = job_cfg.get("steps", [])
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


# ==============================================================================
# 1. mkdocs.yml and Portal Assets Verification
# ==============================================================================


def test_mkdocs_yml_configuration_and_security_exclusions() -> None:
    """Verify mkdocs.yml Material config, Mermaid, KaTeX, mike switcher, hooks, and privacy exclusions."""
    config = _load_mkdocs_config()

    assert config.get("site_name") == "test_db Documentation"
    assert config.get("site_url") == f"{PORTAL_BASE_URL}/"
    assert config.get("repo_name") == "jmrenouard/test_db"
    assert config.get("repo_url") == "https://github.com/jmrenouard/test_db"
    assert config.get("edit_uri") == "edit/master/docs/"
    assert config.get("docs_dir") == "docs"
    assert "scripts/mkdocs_hooks.py" in config.get("hooks", [])

    theme = config.get("theme", {})
    assert isinstance(theme, dict)
    assert theme.get("name") == "material"
    assert theme.get("language") == "en"
    assert "navigation.tabs" in theme.get("features", [])
    assert "navigation.indexes" in theme.get("features", [])

    extra = config.get("extra", {})
    assert extra.get("version", {}).get("provider") == "mike"
    assert extra.get("version", {}).get("default") == "latest"
    social_links = [item.get("link") for item in extra.get("social", []) if isinstance(item, dict)]
    assert "https://github.com/jmrenouard/test_db" in social_links
    assert "https://www.lightpath.fr" in social_links

    extra_css = config.get("extra_css", [])
    assert any("katex" in item and item.endswith(".css") for item in extra_css)
    assert "stylesheets/extra.css" in extra_css

    extra_js = config.get("extra_javascript", [])
    assert "javascripts/katex.js" in extra_js
    assert any("katex.min.js" in item for item in extra_js)
    assert any("auto-render.min.js" in item for item in extra_js)

    extensions = config.get("markdown_extensions", [])
    ext_names: set[str] = set()
    superfences_cfg: dict[str, Any] = {}
    for ext in extensions:
        if isinstance(ext, str):
            ext_names.add(ext)
        elif isinstance(ext, dict):
            ext_names.update(ext.keys())
            if "pymdownx.superfences" in ext:
                superfences_cfg = ext["pymdownx.superfences"] or {}

    assert "admonition" in ext_names
    assert "pymdownx.arithmatex" in ext_names
    assert "pymdownx.superfences" in ext_names

    custom_fences = superfences_cfg.get("custom_fences", [])
    mermaid_fences = [
        fence for fence in custom_fences if isinstance(fence, dict) and fence.get("name") == "mermaid"
    ]
    assert len(mermaid_fences) == 1, "pymdownx.superfences must configure a mermaid custom fence"
    assert mermaid_fences[0].get("class") == "mermaid"
    assert "fence_code_format" in str(mermaid_fences[0].get("format", ""))

    raw_exclude = config.get("exclude_docs", "")
    exclude_text = "\n".join(raw_exclude) if isinstance(raw_exclude, list) else str(raw_exclude)
    for pattern in ("*.kdbx", "*.keyx", "*.pid", "*.log", ".env", ".env.*", ".env_*", "guides/fr/", "overview-fr.md", "01-tutoriels/", "02-guides-pratiques/"):
        assert pattern in exclude_text, f"exclude_docs must exclude '{pattern}'"

    assert config.get("theme", {}).get("language") == "en", "mkdocs.yml theme.language must be 'en'"
    alternates = config.get("extra", {}).get("alternate", [])
    alt_langs = {item.get("lang"): item.get("link") for item in alternates if isinstance(item, dict)}
    assert alt_langs == {"en": "/", "fr": "/fr/"}, f"Unexpected extra.alternate in mkdocs.yml: {alternates}"

    nav = config.get("nav", [])
    assert isinstance(nav, list) and len(nav) == 6
    tab_names = [next(iter(entry.keys())) for entry in nav if isinstance(entry, dict)]
    assert tab_names == [
        "Home",
        "Tutorials",
        "How-To Guides",
        "Reference",
        "Explanation",
        "Releases & Governance",
    ]

    assert (REPO_ROOT / "docs" / "index.md").is_file()
    assert (REPO_ROOT / "docs" / "stylesheets" / "extra.css").is_file()
    assert (REPO_ROOT / "docs" / "assets" / "logo.svg").is_file()
    assert (REPO_ROOT / "docs" / "assets" / "header-banner.svg").is_file()
    katex_js = REPO_ROOT / "docs" / "javascripts" / "katex.js"
    assert katex_js.is_file()
    katex_js_text = katex_js.read_text(encoding="utf-8")
    assert "document$.subscribe" in katex_js_text
    assert "renderMathInElement" in katex_js_text


def test_mkdocs_fr_yml_configuration_and_language_isolation() -> None:
    """Verify mkdocs.fr.yml configures strict French Material tabs, alternate switcher, and EN exclusions."""
    fr_cfg_path = REPO_ROOT / "mkdocs.fr.yml"
    assert fr_cfg_path.is_file(), "mkdocs.fr.yml must exist"

    class _IgnoreTagsLoader(yaml.SafeLoader):
        pass

    _IgnoreTagsLoader.add_multi_constructor("!", lambda loader, suffix, node: None)
    _IgnoreTagsLoader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)
    fr_cfg = yaml.load(fr_cfg_path.read_text(encoding="utf-8"), Loader=_IgnoreTagsLoader)
    assert isinstance(fr_cfg, dict)

    assert fr_cfg.get("docs_dir") == "docs/fr"
    assert fr_cfg.get("theme", {}).get("language") == "fr"
    alternates = fr_cfg.get("extra", {}).get("alternate", [])
    alt_langs = {item.get("lang"): item.get("link") for item in alternates if isinstance(item, dict)}
    assert alt_langs == {"en": "/", "fr": "/fr/"}

    fr_exclude = fr_cfg.get("exclude_docs", "")
    fr_exclude_text = "\n".join(fr_exclude) if isinstance(fr_exclude, list) else str(fr_exclude)
    for pattern in ("*.kdbx", "*.keyx", ".env", "guides/en/", "overview-en.md", "01-tutorials/", "02-how-to-guides/"):
        assert pattern in fr_exclude_text, f"mkdocs.fr.yml exclude_docs must exclude '{pattern}'"

    fr_nav = fr_cfg.get("nav", [])
    fr_tabs = [next(iter(entry.keys())) for entry in fr_nav if isinstance(entry, dict)]
    assert fr_tabs == [
        "Accueil",
        "Tutoriels",
        "Guides pratiques",
        "Référence",
        "Explications",
        "Versions et gouvernance",
    ]
    assert (REPO_ROOT / "docs" / "fr" / "index.md").is_file()


# ==============================================================================
# 2. scripts/mkdocs_hooks.py Unit Tests
# ==============================================================================


def test_mkdocs_hooks_convert_github_alerts_and_ignore_code_blocks() -> None:
    """Verify all 5 GitHub alerts convert to Material admonitions while fenced blocks stay untouched."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)

    sample = (
        "Intro paragraph.\n\n"
        "> [!NOTE]\n"
        "> Useful context line.\n\n"
        "> [!TIP]\n"
        "> Helpful optimization.\n\n"
        "> [!IMPORTANT]\n"
        "> Essential requirement.\n\n"
        "> [!WARNING]\n"
        "> Watch out for drift.\n\n"
        "> [!CAUTION]\n"
        "> High risk operation.\n\n"
        "```markdown\n"
        "> [!NOTE]\n"
        "> Literal example inside fenced code.\n"
        "```\n"
    )

    converted = hooks.convert_github_alerts(sample)

    assert "!!! note" in converted
    assert "!!! tip" in converted
    assert "!!! info" in converted
    assert "!!! warning" in converted
    assert "!!! danger" in converted
    assert "Useful context line." in converted
    assert "High risk operation." in converted

    outside_fenced, fenced_part = converted.split("```markdown", 1)
    assert "> [!NOTE]" in fenced_part
    for marker in (f"[!{tag}]" for tag in ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION")):
        assert marker not in outside_fenced


def test_mkdocs_hooks_gfm_slugify() -> None:
    """Verify gfm_slugify produces GitHub-compatible TOC anchors across EN and FR headings."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)

    assert hooks.gfm_slugify("Documentation & Governance Hub") == "documentation--governance-hub"
    assert hooks.gfm_slugify("13-Table PostgreSQL 18 3NF Schema") == "13-table-postgresql-18-3nf-schema"
    assert hooks.gfm_slugify("Why test_db?") == "why-test_db"
    assert (
        hooks.gfm_slugify("Matrice des schémas (13 tables)")
        == "matrice-des-schémas-13-tables"
    )
    assert hooks.gfm_slugify("cli_flags") == "cli_flags"
    assert hooks.gfm_slugify("Alpha Beta", separator="_") == "alpha_beta"


def test_mkdocs_hooks_rewrite_relative_links_virtual_html_and_exclusions() -> None:
    """Verify virtual doc links, legacy link cleanups, HTML <img> depth, GitHub blob URLs, and exclusions."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)

    overview_md = (
        '<img src="docs/assets/header-banner.svg" alt="Banner" />\n'
        '<img src="docs/assets/logo.svg" alt="Logo" />\n'
        "- [French](README_fr.md)\n"
        "- [English](README.md)\n"
        "- [Changelog](Changelog)\n"
        "- [Sirene Quickstart](sirene/README.md)\n"
        "- [Portal](docs/index.md)\n"
        "- [Sirene Guide](documentation/en/sirene_platform.md)\n"
        "- [Sirene FR](documentation/fr/sirene_platform.md)\n"
        "- [Sirene HTML](documentation/sirene_documentation.html)\n"
        "- [Employees SQL](doc_employees/employees.md)\n"
        "- [Employees SQL FR](doc_employees/employees_fr.md)\n"
        "- [Makefile](Makefile)\n"
        "- Runner: <www.lightpath.fr>\n"
        "- [Vault](secrets.kdbx)\n"
        "- [Key](vault.keyx)\n"
        "- [Pid](daemon.pid)\n"
        "- [Log](run.log)\n"
        "- [Env](.env)\n"
        "- [EnvLocal](.env_local)\n"
        "- [EnvMariaDB](.env_mariadb118)\n"
        "```markdown\n"
        "[Preserved](README_fr.md)\n"
        '<img src="docs/assets/logo.svg" />\n'
        "```\n"
    )

    rewritten_overview = hooks.rewrite_relative_links(
        overview_md,
        page_src_path="overview-en.md",
        ref="v1.11.0",
        use_directory_urls=True,
    )
    outside_fence, fenced_part = rewritten_overview.split("```markdown", 1)

    assert '<img src="../assets/header-banner.svg"' in outside_fence
    assert '<img src="../assets/logo.svg"' in outside_fence
    assert "](overview-fr.md)" in outside_fence
    assert "](overview-en.md)" in outside_fence
    assert "](CHANGELOG.md)" in outside_fence
    assert "](sirene-quickstart.md)" in outside_fence
    assert "](index.md)" in outside_fence
    assert "](guides/en/sirene_platform.md)" in outside_fence
    assert "](guides/fr/sirene_platform.md)" in outside_fence
    assert "](guides/sirene_documentation.html)" in outside_fence
    assert "](guides/employees-sql-en.md)" in outside_fence
    assert "](guides/employees-sql-fr.md)" in outside_fence
    assert "](https://github.com/jmrenouard/test_db/blob/v1.11.0/Makefile)" in outside_fence
    assert "[www.lightpath.fr](https://www.lightpath.fr)" in outside_fence

    for forbidden_target in (
        "secrets.kdbx",
        "vault.keyx",
        "daemon.pid",
        "run.log",
        "(.env)",
        ".env_local",
        ".env_mariadb118",
    ):
        assert forbidden_target not in outside_fence
    for kept_label in ("Vault", "Key", "Pid", "Log", "Env", "EnvLocal", "EnvMariaDB"):
        assert kept_label in outside_fence

    assert "[Preserved](README_fr.md)" in fenced_part
    assert '<img src="docs/assets/logo.svg" />' in fenced_part

    rewritten_flat = hooks.rewrite_relative_links(
        '<img src="docs/assets/header-banner.svg" alt="Banner" />\n',
        page_src_path="overview-en.md",
        ref="v1.11.0",
        use_directory_urls=False,
    )
    assert '<img src="assets/header-banner.svg"' in rewritten_flat

    # Nested guide links (`guides/en/*`) + `file:///test_db/...` rewriting
    guide_md = (
        "- [Index](index.md)\n"
        "- [HTML](../sirene_documentation.html)\n"
        "- [FR](../fr/sirene_platform.md)\n"
        "- [README](../../README.md)\n"
        "- [Lua](file:///test_db/scripts/dir_transactions_sysbench.lua)\n"
    )
    rewritten_guide = hooks.rewrite_relative_links(
        guide_md,
        page_src_path="guides/en/deadlock_experiment.md",
        ref="master",
        use_directory_urls=True,
    )
    assert "](../../guides/en/index.md)" in rewritten_guide
    assert "](../../guides/sirene_documentation.html)" in rewritten_guide
    assert "](../../guides/fr/sirene_platform.md)" in rewritten_guide
    assert "](../../overview-en.md)" in rewritten_guide
    assert (
        "](https://github.com/jmrenouard/test_db/blob/master/scripts/dir_transactions_sysbench.lua)"
        in rewritten_guide
    )

    # Legacy `?tab=t.0#heading=` and `#heading=` cleanup in employees SQL docs
    emp_en = hooks.rewrite_relative_links(
        "[Schema](employees.md#heading=)\n",
        page_src_path="guides/employees-sql-en.md",
        ref="master",
    )
    assert "employees.md#heading=" not in emp_en
    assert "Schema" in emp_en

    emp_fr = hooks.rewrite_relative_links(
        "[Schéma](?tab=t.0#heading=)\n",
        page_src_path="guides/employees-sql-fr.md",
        ref="master",
    )
    assert "?tab=t.0#heading=" not in emp_fr
    assert "Schéma" in emp_fr


def test_mkdocs_hooks_diataxis_depth_links_and_historical_fallbacks(tmp_path: Path) -> None:
    """Verify depth-1/depth-2 Diataxis rewriting and v1.9.0/v1.9.1+ historical fallbacks."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)

    depth1_md = (
        "- [Root](../../README.md)\n"
        "- [RootFR](../../README_fr.md)\n"
        "- [Changelog](../../Changelog)\n"
        "- [Sirene](../../sirene/README.md)\n"
        "- [Portal](../index.md)\n"
        "- [Script](../../scripts/test_runner.sh)\n"
        "- [Ref](../03-reference/configuration/environment-variables-and-makefile-targets.md)\n"
    )
    rewritten_d1 = hooks.rewrite_relative_links(
        depth1_md,
        page_src_path="01-tutorials/01-mariadb-employees-sandbox.md",
        ref="master",
    )
    assert "](../overview-en.md)" in rewritten_d1
    assert "](../overview-fr.md)" in rewritten_d1
    assert "](../CHANGELOG.md)" in rewritten_d1
    assert "](../sirene-quickstart.md)" in rewritten_d1
    assert "](../index.md)" in rewritten_d1
    assert "](https://github.com/jmrenouard/test_db/blob/master/scripts/test_runner.sh)" in rewritten_d1
    assert "](../03-reference/configuration/environment-variables-and-makefile-targets.md)" in rewritten_d1

    depth2_md = (
        "- [Root](../../../README.md)\n"
        "- [RootFR](../../../README_fr.md)\n"
        "- [Changelog](../../../Changelog)\n"
        "- [Portal](../../index.md)\n"
        "- [Compose](../../../sirene/docker-compose.yml)\n"
        "- [Ref](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)\n"
    )
    rewritten_d2 = hooks.rewrite_relative_links(
        depth2_md,
        page_src_path="02-how-to-guides/deployment/deploy-mariadb-and-postgresql-stacks.md",
        ref="master",
    )
    assert "](../../overview-en.md)" in rewritten_d2
    assert "](../../overview-fr.md)" in rewritten_d2
    assert "](../../CHANGELOG.md)" in rewritten_d2
    assert "](../../index.md)" in rewritten_d2
    assert "](https://github.com/jmrenouard/test_db/blob/master/sirene/docker-compose.yml)" in rewritten_d2
    assert "](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)" in rewritten_d2

    # Historical v1.9.0 snapshot: lacks quadrant dirs, sirene_platform.md, and sirene_documentation.html
    v190_root = tmp_path / "v190"
    v190_docs = v190_root / "docs"
    v190_docs.mkdir(parents=True)
    (v190_root / "README.md").write_text("# test_db\n", encoding="utf-8")
    (v190_root / "README_fr.md").write_text("# test_db FR\n", encoding="utf-8")
    (v190_root / "Changelog").write_text("1.9.0 2026-11-19\n", encoding="utf-8")
    (v190_root / "sirene").mkdir()
    (v190_root / "sirene" / "README.md").write_text("# Sirene\n", encoding="utf-8")
    (v190_root / "documentation" / "en").mkdir(parents=True)
    (v190_root / "documentation" / "fr").mkdir(parents=True)
    (v190_root / "documentation" / "en" / "index.md").write_text("# EN\n", encoding="utf-8")
    (v190_root / "documentation" / "fr" / "index.md").write_text("# FR\n", encoding="utf-8")
    (v190_root / "documentation" / "en" / "mariadb_management.md").write_text("# MariaDB\n", encoding="utf-8")
    (v190_root / "documentation" / "en" / "tools_guide.md").write_text("# Tools\n", encoding="utf-8")
    (v190_root / "documentation" / "en" / "benchmarking.md").write_text("# Bench\n", encoding="utf-8")

    portal_links = (
        "- [T](01-tutorials/index.md)\n"
        "- [H](02-how-to-guides/index.md)\n"
        "- [R](03-reference/index.md)\n"
        "- [E](04-explanation/index.md)\n"
        "- [SireneHTML](../documentation/sirene_documentation.html)\n"
    )
    rewritten_v190 = hooks.rewrite_relative_links(
        portal_links,
        page_src_path="index.md",
        ref="v1.9.0",
        docs_dir=v190_docs,
        available_root_docs=("overview-en.md", "overview-fr.md", "CHANGELOG.md", "sirene-quickstart.md"),
    )
    for missing_quadrant in ("01-tutorials/", "02-how-to-guides/", "03-reference/", "04-explanation/"):
        assert missing_quadrant not in rewritten_v190
    assert "- [SireneHTML](sirene-quickstart.md)" in rewritten_v190

    # Historical v1.9.1+ snapshot: adds sirene_documentation.html
    (v190_root / "documentation" / "sirene_documentation.html").write_text("<html></html>", encoding="utf-8")
    rewritten_v191 = hooks.rewrite_relative_links(
        "- [SireneHTML](../documentation/sirene_documentation.html)\n",
        page_src_path="index.md",
        ref="v1.9.1",
        docs_dir=v190_docs,
        available_root_docs=(
            "overview-en.md",
            "overview-fr.md",
            "CHANGELOG.md",
            "sirene-quickstart.md",
            "guides/sirene_documentation.html",
        ),
    )
    assert "- [SireneHTML](guides/sirene_documentation.html)" in rewritten_v191

    # Modern docs_dir preserves quadrant links and resolves directory links to index.md
    modern_docs = tmp_path / "modern_docs"
    for quadrant in ("01-tutorials", "02-how-to-guides", "03-reference", "04-explanation"):
        (modern_docs / quadrant).mkdir(parents=True)
        (modern_docs / quadrant / "index.md").write_text(f"# {quadrant}\n", encoding="utf-8")
    (modern_docs / "01-tutorials" / "01-mariadb-employees-sandbox.md").write_text("# Lab\n", encoding="utf-8")

    rewritten_modern = hooks.rewrite_relative_links(
        "- [T](01-tutorials/index.md)\n- [TDir](01-tutorials/)\n- [T1](01-tutorials/01-mariadb-employees-sandbox.md)\n",
        page_src_path="index.md",
        ref="master",
        docs_dir=modern_docs,
    )
    assert "- [T](01-tutorials/index.md)" in rewritten_modern
    assert "- [TDir](01-tutorials/index.md)" in rewritten_modern
    assert "- [T1](01-tutorials/01-mariadb-employees-sandbox.md)" in rewritten_modern


def test_mkdocs_hooks_prune_nav_and_prepend_changelog_heading(tmp_path: Path) -> None:
    """Verify nav pruning drops missing entries/virtual docs and CHANGELOG.md receives a top-level heading."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "index.md").write_text("# Home\n", encoding="utf-8")
    (docs_dir / "ACTION_LOGBOOK.md").write_text("# Logbook\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# English Overview\n", encoding="utf-8")
    (tmp_path / "Changelog").write_text("1.11.0 2026-11-20\n\n- feat: sample\n", encoding="utf-8")
    (tmp_path / "sirene").mkdir()
    (tmp_path / "sirene" / "README.md").write_text("# Sirene\n", encoding="utf-8")
    (tmp_path / "documentation" / "en").mkdir(parents=True)
    (tmp_path / "documentation" / "en" / "index.md").write_text("# Guides EN\n", encoding="utf-8")
    # Note: README_fr.md and documentation/en/sirene_platform.md intentionally omitted

    nav = [
        {"Home": "index.md"},
        {
            "How-To Guides": [
                {"Deployment": ["02-how-to-guides/deployment/missing.md"]},
                "MISSING_DOC.md",
            ]
        },
        {
            "Reference": [
                {
                    "Bilingual Guides (EN)": [
                        "guides/en/index.md",
                        "guides/en/sirene_platform.md",
                    ]
                }
            ]
        },
        {
            "Explanation": [
                {"Overview (English)": "overview-en.md"},
                {"Aperçu (Français)": "overview-fr.md"},
                {"Sirene Quickstart": "sirene-quickstart.md"},
            ]
        },
        {
            "Releases & Governance": [
                {"Changelog": "CHANGELOG.md"},
                {"Action Logbook": "ACTION_LOGBOOK.md"},
            ]
        },
    ]

    pruned = hooks.prune_nav_for_existing_files(nav, docs_dir, tmp_path)
    all_paths = _flatten_nav_paths(pruned)

    assert "index.md" in all_paths
    assert "overview-en.md" in all_paths
    assert "sirene-quickstart.md" in all_paths
    assert "guides/en/index.md" in all_paths
    assert "CHANGELOG.md" in all_paths
    assert "ACTION_LOGBOOK.md" in all_paths
    assert "overview-fr.md" not in all_paths
    assert "guides/en/sirene_platform.md" not in all_paths
    assert "MISSING_DOC.md" not in all_paths
    assert "02-how-to-guides/deployment/missing.md" not in all_paths
    assert _find_nav_section(pruned, "How-To Guides") is None

    # CHANGELOG.md lacking top-level `# ` heading gets `# Changelog\n\n` prepended
    cfg = _AttrDict({"docs_dir": str(docs_dir), "repo_url": "https://github.com/jmrenouard/test_db"})
    rendered_changelog = hooks.on_page_markdown(
        "1.11.0 2026-11-20\n\n- feat: initial\n",
        _FakePage("CHANGELOG.md"),
        cfg,
        _FakeFiles({"CHANGELOG.md"}),
    )
    assert rendered_changelog.startswith("# Changelog\n\n")


def test_mkdocs_hooks_on_config_edit_uri_and_virtual_edit_url(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify on_config sets edit_uri on master/WORKTREE, clears on tags, attaches gfm_slugify, and maps edit_url."""
    hooks = _load_script_module("mkdocs_hooks", HOOKS_SCRIPT_PATH)
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "index.md").write_text("# Home\n", encoding="utf-8")

    monkeypatch.setenv("TEST_DB_DOCS_REF", "WORKTREE")
    monkeypatch.setenv("TEST_DB_DOCS_SITE_URL", f"{PORTAL_BASE_URL}/master")
    cfg_master = _AttrDict(
        {
            "docs_dir": str(docs_dir),
            "site_url": "",
            "edit_uri": "",
            "repo_url": "https://github.com/jmrenouard/test_db",
            "mdx_configs": {"toc": {"permalink": True}},
            "nav": [{"Home": "index.md"}],
        }
    )
    hooks.on_config(cfg_master)
    assert cfg_master["edit_uri"] == "edit/master/docs/"
    assert cfg_master["site_url"] == f"{PORTAL_BASE_URL}/master/"
    assert cfg_master["mdx_configs"]["toc"]["slugify"] is hooks.gfm_slugify

    expected_edit_targets = {
        "overview-en.md": "README.md",
        "overview-fr.md": "README_fr.md",
        "CHANGELOG.md": "Changelog",
        "sirene-quickstart.md": "sirene/README.md",
        "guides/en/index.md": "documentation/en/index.md",
        "guides/employees-sql-en.md": "doc_employees/employees.md",
    }
    for virtual_uri, repo_file in expected_edit_targets.items():
        page = _FakePage(
            virtual_uri,
            f"https://github.com/jmrenouard/test_db/edit/master/docs/{virtual_uri}",
        )
        hooks.on_page_markdown("# Heading\n", page, cfg_master, _FakeFiles())
        assert page.edit_url == f"https://github.com/jmrenouard/test_db/edit/master/{repo_file}"

    monkeypatch.setenv("TEST_DB_DOCS_REF", "v1.11.0")
    monkeypatch.setenv("TEST_DB_DOCS_SITE_URL", f"{PORTAL_BASE_URL}/v1.11.0")
    cfg_tag = _AttrDict(
        {
            "docs_dir": str(docs_dir),
            "site_url": "",
            "edit_uri": "edit/master/docs/",
            "repo_url": "https://github.com/jmrenouard/test_db",
            "mdx_configs": {"toc": {}},
            "nav": [],
            "extra": {
                "alternate": [
                    {"name": "English", "link": "/", "lang": "en"},
                    {"name": "Français", "link": "/fr/", "lang": "fr"},
                ]
            },
        }
    )
    hooks.on_config(cfg_tag)
    assert cfg_tag["edit_uri"] == ""
    tag_alts = {item["lang"]: item["link"] for item in cfg_tag["extra"]["alternate"]}
    assert tag_alts == {"en": "/v1.11.0/", "fr": "/v1.11.0/fr/"}

    page_tag = _FakePage(
        "overview-en.md",
        "https://github.com/jmrenouard/test_db/edit/master/docs/overview-en.md",
    )
    hooks.on_page_markdown("# Overview\n", page_tag, cfg_tag, _FakeFiles())
    assert not page_tag.edit_url

    docs_fr_dir = docs_dir / "fr"
    docs_fr_dir.mkdir()
    (docs_fr_dir / "index.md").write_text("# Accueil\n", encoding="utf-8")
    monkeypatch.setenv("TEST_DB_DOCS_REF", "WORKTREE")
    monkeypatch.setenv("TEST_DB_DOCS_SITE_URL", f"{PORTAL_BASE_URL}/master/fr")
    cfg_fr_master = _AttrDict(
        {
            "docs_dir": str(docs_fr_dir),
            "site_url": "",
            "edit_uri": "",
            "repo_url": "https://github.com/jmrenouard/test_db",
            "theme": _AttrDict({"language": "fr"}),
            "mdx_configs": {"toc": {"permalink": True}},
            "nav": [{"Accueil": "index.md"}],
            "extra": {
                "alternate": [
                    {"name": "English", "link": "/", "lang": "en"},
                    {"name": "Français", "link": "/fr/", "lang": "fr"},
                ]
            },
        }
    )
    hooks.on_config(cfg_fr_master)
    assert cfg_fr_master["edit_uri"] == "edit/master/docs/fr/"
    fr_master_alts = {item["lang"]: item["link"] for item in cfg_fr_master["extra"]["alternate"]}
    assert fr_master_alts == {"en": "/master/", "fr": "/master/fr/"}


def test_mkdocs_hooks_importable_without_mkdocs_or_pathspec(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify scripts/mkdocs_hooks.py imports and runs helper/hook functions without mkdocs or pathspec installed."""
    for blocked in (
        "mkdocs",
        "mkdocs.structure",
        "mkdocs.structure.files",
        "pathspec",
        "pathspec.gitignore",
    ):
        monkeypatch.setitem(sys.modules, blocked, None)

    try:
        hooks = _load_script_module("mkdocs_hooks_no_deps", HOOKS_SCRIPT_PATH)
        assert "!!! note" in hooks.convert_github_alerts("> [!NOTE]\n> Works without mkdocs.")
        assert hooks.gfm_slugify("Sirene 3NF Schema") == "sirene-3nf-schema"
        assert "](../../overview-en.md)" in hooks.rewrite_relative_links(
            "[Root](../../README.md)",
            "guides/en/index.md",
        )
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Home\n", encoding="utf-8")
        cfg = _AttrDict(
            {
                "docs_dir": str(docs_dir),
                "site_url": "",
                "edit_uri": "",
                "mdx_configs": {"toc": {}},
                "nav": [{"Home": "index.md"}],
            }
        )
        hooks.on_config(cfg)
        assert cfg["edit_uri"] == "edit/master/docs/"
    finally:
        sys.modules.pop("mkdocs_hooks_no_deps", None)


# ==============================================================================
# 3. scripts/build_versioned_docs.py Unit & Integration Tests
# ==============================================================================


def test_build_versioned_docs_parse_semver_tag_min_tag_and_manifest_ordering() -> None:
    """Verify semver parsing, min_tag v1.9.0 filtering, descending sort, and master/dev alias manifest."""
    builder = _load_script_module("build_versioned_docs", BUILD_SCRIPT_PATH)

    assert builder.parse_semver_tag("v1.9.0") == (1, 9, 0)
    assert builder.parse_semver_tag("v1.9.1") == (1, 9, 1)
    assert builder.parse_semver_tag("v1.10.0") == (1, 10, 0)
    assert builder.parse_semver_tag("v1.11.0") == (1, 11, 0)
    assert builder.parse_semver_tag("master") is None
    assert builder.parse_semver_tag("latest") is None
    assert builder.parse_semver_tag("v1.9") is None

    if (REPO_ROOT / ".git").exists() and shutil.which("git") is not None:
        discovered = builder.discover_release_tags(REPO_ROOT)
        assert set(RELEASE_TAGS).issubset(set(discovered))
        for legacy_tag in ("v1.7.6", "v1.5.0", "v1.0.7"):
            assert legacy_tag not in discovered, f"Pre-min_tag release {legacy_tag} must be filtered out"
        assert discovered.index("v1.11.0") < discovered.index("v1.10.0")
        assert discovered.index("v1.10.0") < discovered.index("v1.9.1")
        assert discovered.index("v1.9.1") < discovered.index("v1.9.0")

    manifest = builder.build_versions_manifest(["v1.9.0", "v1.10.0", "v1.11.0", "v1.9.1"])
    versions = [entry["version"] for entry in manifest]

    assert versions.index("v1.11.0") < versions.index("v1.10.0")
    assert versions.index("v1.10.0") < versions.index("v1.9.1")
    assert versions.index("v1.9.1") < versions.index("v1.9.0")

    by_version = {entry["version"]: entry for entry in manifest}
    assert "latest" in by_version["v1.11.0"]["aliases"]
    assert "latest" not in by_version["v1.10.0"]["aliases"]
    assert "master" in by_version
    assert "dev" in by_version["master"]["aliases"]

    fallback_master = builder.build_versions_manifest([])
    assert len(fallback_master) == 1
    assert fallback_master[0]["version"] == "master"
    assert "latest" in fallback_master[0]["aliases"]
    assert "dev" in fallback_master[0]["aliases"]


def test_build_versioned_docs_sparse_git_archive_excludes_employees(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify build_versioned_docs.py defaults and sparse git archive exclusion of 168 MB employees/."""
    script_text = BUILD_SCRIPT_PATH.read_text(encoding="utf-8")
    assert PORTAL_BASE_URL in script_text
    assert "v1.9.0" in script_text
    assert "master" in script_text
    assert "ls-tree" in script_text

    if shutil.which("git") is None:
        pytest.skip("git executable required for sparse archive verification")

    builder = _load_script_module("build_versioned_docs", BUILD_SCRIPT_PATH)

    repo = tmp_path / "repo"
    (repo / "employees").mkdir(parents=True)
    (repo / "docs" / "stylesheets").mkdir(parents=True)
    (repo / "docs" / "javascripts").mkdir(parents=True)
    (repo / "documentation" / "en").mkdir(parents=True)
    (repo / "doc_employees").mkdir(parents=True)
    (repo / "sirene").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)

    (repo / "employees" / "load_salaries.dump").write_text("HEAVY_PAYLOAD\n", encoding="utf-8")
    (repo / "README.md").write_text("# test_db\n", encoding="utf-8")
    (repo / "README_fr.md").write_text("# test_db FR\n", encoding="utf-8")
    (repo / "Changelog").write_text("1.9.0 2026-11-19\n", encoding="utf-8")
    (repo / "sirene" / "README.md").write_text("# Sirene\n", encoding="utf-8")
    (repo / "documentation" / "en" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / "doc_employees" / "employees.md").write_text("# Emp\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Portal\n", encoding="utf-8")
    (repo / "docs" / "stylesheets" / "extra.css").write_text("body {}\n", encoding="utf-8")
    (repo / "docs" / "javascripts" / "katex.js").write_text("// katex\n", encoding="utf-8")
    (repo / "mkdocs.yml").write_text("site_name: test_db Documentation\n", encoding="utf-8")
    (repo / "scripts" / "mkdocs_hooks.py").write_text("# hooks\n", encoding="utf-8")

    subprocess.run(["git", "init", "-b", "master", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "ci@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "CI"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "tag", "v1.9.0"], check=True)

    archive_calls: list[list[str]] = []
    real_run = subprocess.run

    def _spied_run(cmd: Any, *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        cmd_list = [str(part) for part in cmd] if isinstance(cmd, (list, tuple)) else [str(cmd)]
        if len(cmd_list) >= 3 and "git" in Path(cmd_list[0]).name and "archive" in cmd_list:
            archive_calls.append(cmd_list)
        if "-m" in cmd_list and "mkdocs" in cmd_list and "build" in cmd_list:
            out_idx = cmd_list.index("-d") + 1
            site_dir = Path(cmd_list[out_idx])
            site_dir.mkdir(parents=True, exist_ok=True)
            (site_dir / "index.html").write_text("<html>ok</html>", encoding="utf-8")
            return subprocess.CompletedProcess(cmd_list, 0, stdout="", stderr="")
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(builder.subprocess, "run", _spied_run)

    out_dir = tmp_path / "site_out"
    builder.build_single_version(
        repo_root=repo,
        git_ref="v1.9.0",
        version_slug="v1.9.0",
        output_dir=out_dir,
        base_url=PORTAL_BASE_URL,
        strict=True,
    )

    assert len(archive_calls) == 1, "Expected exactly one sparse git archive call for tag v1.9.0"
    archive_cmd = archive_calls[0]
    joined_cmd = " ".join(archive_cmd)
    assert "employees/load_salaries.dump" not in joined_cmd
    assert "employees" not in [Path(part).parts[0] for part in archive_cmd if part != "--"]
    assert any("README.md" in part or "docs" in part for part in archive_cmd), (
        f"Expected sparse doc pathspecs in git archive call: {archive_cmd}"
    )


def test_build_versioned_site_rejects_protected_or_ancestor_output_dirs(tmp_path: Path) -> None:
    """Verify build_versioned_site refuses to overwrite repo root, ancestors, or protected subdirectories."""
    builder = _load_script_module("build_versioned_docs", BUILD_SCRIPT_PATH)
    repo_dir = tmp_path / "repo"
    docs_dir = repo_dir / "docs"
    scripts_dir = repo_dir / "scripts"
    tests_dir = repo_dir / "tests"
    git_dir = repo_dir / ".git"
    for directory in (docs_dir, scripts_dir, tests_dir, git_dir):
        directory.mkdir(parents=True)
    sentinel = docs_dir / "keep.md"
    sentinel.write_text("# Keep\n", encoding="utf-8")

    for forbidden_out in (
        repo_dir,
        tmp_path,
        git_dir,
        docs_dir,
        docs_dir / "nested",
        scripts_dir,
        tests_dir,
    ):
        with pytest.raises(ValueError, match="protected"):
            builder.build_versioned_site(repo_root=repo_dir, output_dir=forbidden_out, skip_tags=True)
        assert sentinel.is_file()


def test_build_versioned_docs_render_htaccess_and_redirect_html() -> None:
    """Verify .htaccess rules (HTTPS 301, /latest/, /dev/, /main/ -> /master/ 302) and redirect HTML."""
    builder = _load_script_module("build_versioned_docs", BUILD_SCRIPT_PATH)

    htaccess = builder.render_htaccess("v1.11.0", main_version="master")
    assert "Options -Indexes" in htaccess
    assert "DirectoryIndex index.html" in htaccess
    assert "RewriteEngine On" in htaccess
    assert "RewriteBase /" in htaccess
    assert "X-Content-Type-Options" in htaccess
    assert "R=301" in htaccess
    assert "^latest(?:/(.*))?$" in htaccess
    assert "/v1.11.0/$1" in htaccess
    assert "^dev(?:/(.*))?$" in htaccess
    assert "^main(?:/(.*))?$" in htaccess
    assert "/master/$1" in htaccess
    assert "R=302" in htaccess
    assert "ErrorDocument 404 /v1.11.0/404.html" in htaccess

    redirect_html = builder.render_redirect_html("/v1.11.0/", "test_db Documentation")
    assert "<!doctype html>" in redirect_html.lower()
    assert "test_db Documentation" in redirect_html
    assert 'http-equiv="refresh"' in redirect_html.lower()
    assert "/v1.11.0/" in redirect_html


def test_build_versioned_docs_end_to_end_worktree_and_release_tags(tmp_path: Path) -> None:
    """End-to-end build of WORKTREE + v1.11.0..v1.9.0 asserting manifest, redirects, assets, and zero leaks."""
    if importlib.util.find_spec("mkdocs") is None:
        pytest.skip("mkdocs optional extra not installed in current test environment")
    if not (REPO_ROOT / ".git").exists() or shutil.which("git") is None:
        pytest.skip("Git repository metadata required for multi-version tag build test")

    tag_probe = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "tag", "--list"],
        capture_output=True,
        text=True,
        check=False,
    )
    available_tags = set(tag_probe.stdout.splitlines())
    if tag_probe.returncode != 0 or not set(RELEASE_TAGS).issubset(available_tags):
        pytest.skip(f"Tags {RELEASE_TAGS} not all available in local Git clone")

    out_dir = tmp_path / "site_dist"
    proc = subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT_PATH),
            "--output",
            str(out_dir),
            "--base-url",
            PORTAL_BASE_URL,
            "--main-ref",
            "WORKTREE",
            "--tags",
            *RELEASE_TAGS,
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"build_versioned_docs.py failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    expected_files = [
        out_dir / "versions.json",
        out_dir / "index.html",
        out_dir / ".htaccess",
        out_dir / "latest" / "index.html",
        out_dir / "dev" / "index.html",
        out_dir / "master" / "index.html",
        out_dir / "master" / "fr" / "index.html",
        out_dir / "master" / "stylesheets" / "extra.css",
        out_dir / "master" / "javascripts" / "katex.js",
        out_dir / "master" / "guides" / "sirene_documentation.html",
        out_dir / "master" / "fr" / "guides" / "sirene_documentation.html",
        out_dir / "v1.11.0" / "index.html",
        out_dir / "v1.11.0" / "fr" / "index.html",
        out_dir / "v1.10.0" / "index.html",
        out_dir / "v1.9.1" / "index.html",
        out_dir / "v1.9.0" / "index.html",
    ]
    for path in expected_files:
        assert path.is_file(), f"Expected built artifact missing: {path}"

    assert 'lang="en"' in (out_dir / "master" / "index.html").read_text(encoding="utf-8")
    assert 'lang="fr"' in (out_dir / "master" / "fr" / "index.html").read_text(encoding="utf-8")
    assert not (out_dir / "master" / "guides" / "fr").exists(), "EN version build must exclude FR guides/"
    assert not (out_dir / "master" / "fr" / "guides" / "en").exists(), "FR version build must exclude EN guides/"

    manifest = json.loads((out_dir / "versions.json").read_text(encoding="utf-8"))
    assert isinstance(manifest, list)
    versions_order = [entry["version"] for entry in manifest]
    assert versions_order.index("v1.11.0") < versions_order.index("v1.10.0")
    assert versions_order.index("v1.10.0") < versions_order.index("v1.9.1")
    assert versions_order.index("v1.9.1") < versions_order.index("v1.9.0")

    by_version = {entry["version"]: entry for entry in manifest}
    for tag in RELEASE_TAGS:
        assert tag in by_version
    assert "latest" in by_version["v1.11.0"]["aliases"]
    for older in ("v1.10.0", "v1.9.1", "v1.9.0"):
        assert "latest" not in by_version[older]["aliases"]
    assert "master" in by_version
    assert "dev" in by_version["master"]["aliases"]

    htaccess_text = (out_dir / ".htaccess").read_text(encoding="utf-8")
    assert "/v1.11.0/$1" in htaccess_text
    assert "/master/$1" in htaccess_text
    assert "^main(?:/(.*))?$" in htaccess_text

    leaked_sensitive = [
        p.relative_to(out_dir).as_posix()
        for p in out_dir.rglob("*")
        if p.is_file()
        and (
            p.suffix.lower() in {".kdbx", ".keyx", ".pid", ".log"}
            or p.name.lower() == ".env"
            or p.name.lower().startswith((".env.", ".env_"))
        )
    ]
    assert not leaked_sensitive, f"Sensitive or temporary files leaked into built output: {leaked_sensitive}"


# ==============================================================================
# 4. .github/workflows/docs-publish.yml Security & Deployment Tests
# ==============================================================================


def test_docs_publish_workflow_triggers_permissions_build_and_sftp_deploy() -> None:
    """Verify docs-publish.yml triggers, SHA pinning, least-privilege permissions, artifact flags, and SFTP steps."""
    assert WORKFLOW_PATH.is_file(), ".github/workflows/docs-publish.yml must exist"
    raw_yaml = WORKFLOW_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw_yaml)
    assert isinstance(data, dict)

    assert data.get("permissions") == {"contents": "read"}

    triggers = data.get("on") if "on" in data else data.get(True)
    assert isinstance(triggers, dict)
    assert triggers["push"]["branches"] == ["master"]
    assert triggers["pull_request"]["branches"] == ["master"]
    assert triggers["push"]["paths"] == triggers["pull_request"]["paths"]
    assert any("v*" in str(tag) for tag in triggers["push"].get("tags", []))
    for required_path in (
        "docs/**",
        "mkdocs.yml",
        "mkdocs.fr.yml",
        "README.md",
        "README_fr.md",
        "Changelog",
        "requirements-docs.txt",
        ".vale.ini",
        ".markdownlint.json",
        "scripts/mkdocs_hooks.py",
        "scripts/build_versioned_docs.py",
        ".github/workflows/docs-ci.yml",
        ".github/workflows/docs-publish.yml",
        "tests/test_diataxis_documentation.py",
        "tests/test_mkdocs_publishing.py",
        "tests/test_tutorials_and_howtos.py",
    ):
        assert required_path in triggers["push"]["paths"]

    assert triggers["release"] == {"types": ["published"]}
    deploy_input = triggers["workflow_dispatch"]["inputs"]["deploy"]
    assert deploy_input["type"] == "boolean"
    assert deploy_input["default"] is True

    concurrency = data.get("concurrency", {})
    assert "docs-publish-" in str(concurrency.get("group", ""))
    assert "github.ref" in str(concurrency.get("group", ""))
    assert "pull_request" in str(concurrency.get("cancel-in-progress", ""))

    jobs = data.get("jobs", {})
    assert "verify-and-build" in jobs
    assert "deploy-ionos" in jobs

    # Global supply-chain & injection checks across every job and step
    for job_name, job_cfg in jobs.items():
        if isinstance(job_cfg.get("if"), str):
            assert "secrets." not in job_cfg["if"], f"{job_name}.if must not reference secrets."
        for idx, step in enumerate(_collect_workflow_steps(job_cfg)):
            uses_val = step.get("uses")
            if isinstance(uses_val, str):
                assert "@" in uses_val, f"{job_name} step #{idx} must pin action to SHA: {uses_val}"
                sha = uses_val.split("@", 1)[1]
                assert SHA40_RE.fullmatch(sha), (
                    f"{job_name} step #{idx} must use 40-char SHA, got '{uses_val}'"
                )
            if_val = step.get("if")
            if isinstance(if_val, str):
                assert "secrets." not in if_val, f"{job_name} step #{idx} must not use secrets. in if:"
            run_val = step.get("run")
            if isinstance(run_val, str):
                assert "${{" not in run_val, (
                    f"{job_name} step #{idx} must pass GitHub expressions via env:, never ${{ in run:"
                )

    # Job 1: verify-and-build
    build_job = jobs["verify-and-build"]
    assert build_job.get("runs-on") == "ubuntu-latest"
    assert isinstance(build_job.get("timeout-minutes"), int) and build_job["timeout-minutes"] <= 15

    build_steps = _collect_workflow_steps(build_job)
    checkout_steps = [s for s in build_steps if str(s.get("uses", "")).startswith("actions/checkout@")]
    assert len(checkout_steps) == 1
    assert checkout_steps[0].get("with", {}).get("fetch-depth") == 0

    python_steps = [s for s in build_steps if str(s.get("uses", "")).startswith("actions/setup-python@")]
    assert len(python_steps) == 1
    python_with = python_steps[0].get("with", {})
    assert python_with.get("python-version") == "3.12"
    assert python_with.get("cache") == "pip"
    assert python_with.get("cache-dependency-path") == "requirements-docs.txt"

    build_run_script = "\n".join(str(s.get("run", "")) for s in build_steps)
    for expected_token in (
        "requirements-docs.txt",
        "tests/test_diataxis_documentation.py",
        "tests/test_mkdocs_publishing.py",
        "tests/test_tutorials_and_howtos.py",
        "scripts/build_versioned_docs.py",
        PORTAL_BASE_URL,
        "origin/master",
        "WORKTREE",
        "site_dist/versions.json",
        "site_dist/.htaccess",
        "site_dist/master/index.html",
        "site_dist/master/fr/index.html",
    ):
        assert expected_token in build_run_script, f"verify-and-build missing '{expected_token}'"

    upload_steps = [s for s in build_steps if str(s.get("uses", "")).startswith("actions/upload-artifact@")]
    assert len(upload_steps) == 1
    upload_with = upload_steps[0].get("with", {})
    assert upload_with.get("name") == "mkdocs-site-dist"
    assert upload_with.get("path") == "site_dist/"
    assert upload_with.get("include-hidden-files") is True
    assert upload_with.get("retention-days") == 7

    # Job 2: deploy-ionos
    deploy_job = jobs["deploy-ionos"]
    assert deploy_job.get("needs") == "verify-and-build"
    assert deploy_job.get("runs-on") == "ubuntu-latest"
    assert isinstance(deploy_job.get("timeout-minutes"), int) and deploy_job["timeout-minutes"] <= 15

    deploy_if = str(deploy_job.get("if", ""))
    assert "github.event_name == 'release'" in deploy_if
    assert "refs/heads/master" in deploy_if
    assert "refs/tags/v" in deploy_if or "github.ref_type == 'tag'" in deploy_if
    assert "inputs.deploy == true" in deploy_if

    deploy_steps = _collect_workflow_steps(deploy_job)
    assert not any("actions/checkout" in str(s.get("uses", "")) for s in deploy_steps)

    download_steps = [s for s in deploy_steps if str(s.get("uses", "")).startswith("actions/download-artifact@")]
    assert len(download_steps) == 1
    assert download_steps[0].get("with", {}).get("name") == "mkdocs-site-dist"
    assert download_steps[0].get("with", {}).get("path") == "."

    sftp_steps = [s for s in deploy_steps if str(s.get("uses", "")).startswith("wlixcc/SFTP-Deploy-Action@")]
    assert len(sftp_steps) == 2, "Expected site upload step plus explicit .htaccess upload step"

    local_paths = [step.get("with", {}).get("local_path") for step in sftp_steps]
    assert "./" in local_paths
    assert ".htaccess" in local_paths

    for step in sftp_steps:
        step_with = step.get("with", {})
        assert step_with.get("sftp_only") is True
        assert step_with.get("server") == "${{ secrets.IONOS_FTP_SERVER }}"
        assert step_with.get("username") == "${{ secrets.IONOS_FTP_USERNAME }}"
        assert step_with.get("password") == "${{ secrets.IONOS_FTP_PASSWORD }}"
        assert step_with.get("port") == "${{ secrets.IONOS_FTP_PORT || '22' }}"
        assert step_with.get("remote_path") == "${{ secrets.IONOS_REMOTE_PATH }}/"

    deploy_run_script = "\n".join(str(s.get("run", "")) for s in deploy_steps)
    assert ".htaccess" in deploy_run_script
    assert "versions.json" in deploy_run_script
    assert f"{PORTAL_BASE_URL}/versions.json" in deploy_run_script
    assert f"{PORTAL_BASE_URL}/latest/" in deploy_run_script
    assert f"{PORTAL_BASE_URL}/master/" in deploy_run_script
    assert f"{PORTAL_BASE_URL}/master/fr/" in deploy_run_script

    for unsafe_pattern in (
        "chmod 777",
        "chmod -R 777",
        "chmod a+rwx",
        "sudo",
        "eval ",
        "curl -s | bash",
        "wget -O- | sh",
    ):
        assert unsafe_pattern not in raw_yaml, f"Unsafe shell pattern found in workflow: {unsafe_pattern}"


# ==============================================================================
# 5. Requirements, .gitignore, Makefile, and Portal Link Consistency
# ==============================================================================


def test_gitignore_requirements_makefile_and_portal_links() -> None:
    """Verify .gitignore, requirements*, Makefile docs targets, and README portal URLs."""
    gitignore_lines = {
        line.strip()
        for line in GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    for entry in ("site/", "site_dist/", ".venv-docs/", ".pytest_cache/", "__pycache__/", "*.pyc"):
        assert entry in gitignore_lines, f".gitignore must exclude '{entry}'"

    assert REQUIREMENTS_DOCS_PATH.is_file(), "requirements-docs.txt must exist"
    reqs_docs = REQUIREMENTS_DOCS_PATH.read_text(encoding="utf-8")
    for pkg in ("mkdocs>=", "mkdocs-material>=", "pymdown-extensions>="):
        assert pkg in reqs_docs, f"requirements-docs.txt must pin {pkg}"

    root_reqs = REQUIREMENTS_ROOT_PATH.read_text(encoding="utf-8")
    assert "psycopg[binary]>=3.2" in root_reqs
    assert "faker >= 18.0.0" in root_reqs
    assert (
        all(pkg in root_reqs for pkg in ("mkdocs>=", "mkdocs-material>=", "pymdown-extensions>="))
        or "requirements-docs.txt" in root_reqs
    ), "requirements.txt must include MkDocs Material publishing dependencies"

    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")
    for target in ("docs-check", "docs-build", "docs-build-versioned", "docs-serve"):
        assert re.search(rf"(?m)^{re.escape(target)}:", makefile_text), (
            f"Makefile missing target '{target}:'"
        )
        assert target in makefile_text

    for doc_path in (REPO_ROOT / "README.md", REPO_ROOT / "README_fr.md"):
        assert PORTAL_BASE_URL in doc_path.read_text(encoding="utf-8")
