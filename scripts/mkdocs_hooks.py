"""MkDocs Material build hooks for test_db documentation publishing."""

from __future__ import annotations

import os
from pathlib import Path
import posixpath
import re
from typing import TYPE_CHECKING, Any, Iterable
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from mkdocs.structure.files import Files

DEFAULT_REPO_URL = "https://github.com/jmrenouard/test_db"
DEFAULT_REF = "master"

# Virtual Markdown docs mapped from repository paths outside docs/ into MkDocs URIs.
# Format: virtual_uri -> (repo_source_path, repo_source_dir)
VIRTUAL_DOCS: dict[str, tuple[str, str]] = {
    "overview-en.md": ("README.md", ""),
    "overview-fr.md": ("README_fr.md", ""),
    "CHANGELOG.md": ("Changelog", ""),
    "sirene-quickstart.md": ("sirene/README.md", "sirene"),
    "guides/employees-sql-en.md": ("doc_employees/employees.md", "doc_employees"),
    "guides/employees-sql-fr.md": ("doc_employees/employees_fr.md", "doc_employees"),
    "guides/en/index.md": ("documentation/en/index.md", "documentation/en"),
    "guides/en/sirene_platform.md": ("documentation/en/sirene_platform.md", "documentation/en"),
    "guides/en/mariadb_management.md": ("documentation/en/mariadb_management.md", "documentation/en"),
    "guides/en/tools_guide.md": ("documentation/en/tools_guide.md", "documentation/en"),
    "guides/en/benchmarking.md": ("documentation/en/benchmarking.md", "documentation/en"),
    "guides/en/sql_analyzer.md": ("documentation/en/sql_analyzer.md", "documentation/en"),
    "guides/en/interactive_reporting.md": ("documentation/en/interactive_reporting.md", "documentation/en"),
    "guides/en/deadlock_experiment.md": ("documentation/en/deadlock_experiment.md", "documentation/en"),
    "guides/en/gap_locking_experiment.md": ("documentation/en/gap_locking_experiment.md", "documentation/en"),
    "guides/fr/index.md": ("documentation/fr/index.md", "documentation/fr"),
    "guides/fr/sirene_platform.md": ("documentation/fr/sirene_platform.md", "documentation/fr"),
    "guides/fr/mariadb_management.md": ("documentation/fr/mariadb_management.md", "documentation/fr"),
    "guides/fr/guide_outils.md": ("documentation/fr/guide_outils.md", "documentation/fr"),
    "guides/fr/benchmarking.md": ("documentation/fr/benchmarking.md", "documentation/fr"),
    "guides/fr/sql_analyzer.md": ("documentation/fr/sql_analyzer.md", "documentation/fr"),
    "guides/fr/interactive_reporting.md": ("documentation/fr/interactive_reporting.md", "documentation/fr"),
    "guides/fr/deadlock_experiment.md": ("documentation/fr/deadlock_experiment.md", "documentation/fr"),
    "guides/fr/gap_locking_experiment.md": ("documentation/fr/gap_locking_experiment.md", "documentation/fr"),
}

# Non-Markdown static assets outside docs/ injected via File.generated when present.
VIRTUAL_STATIC_ASSETS: dict[str, tuple[str, str]] = {
    "guides/sirene_documentation.html": ("documentation/sirene_documentation.html", "documentation"),
}

# Shared docs files mounted into French builds (docs_dir=docs/fr) without duplicating files on disk.
VIRTUAL_FR_ROOT_DOCS: dict[str, tuple[str, str]] = {
    "ACTION_LOGBOOK.md": ("docs/ACTION_LOGBOOK.md", "docs"),
    "RCA_REGISTER.md": ("docs/RCA_REGISTER.md", "docs"),
}

VIRTUAL_FR_STATIC_ASSETS: dict[str, str] = {
    "assets/logo.svg": "docs/assets/logo.svg",
    "assets/header-banner.svg": "docs/assets/header-banner.svg",
    "stylesheets/extra.css": "docs/stylesheets/extra.css",
    "javascripts/katex.js": "docs/javascripts/katex.js",
}

VIRTUAL_DOCS_SHARED: frozenset[str] = frozenset({"CHANGELOG.md", "sirene-quickstart.md"})
VIRTUAL_DOCS_EN: frozenset[str] = VIRTUAL_DOCS_SHARED | frozenset(
    uri for uri in VIRTUAL_DOCS if uri == "overview-en.md" or uri.startswith(("guides/en/", "guides/employees-sql-en"))
)
VIRTUAL_DOCS_FR: frozenset[str] = VIRTUAL_DOCS_SHARED | frozenset(
    uri for uri in VIRTUAL_DOCS if uri == "overview-fr.md" or uri.startswith(("guides/fr/", "guides/employees-sql-fr"))
)

_REPO_DOC_TO_VIRTUAL: dict[str, str] = {
    source_path: virtual_uri for virtual_uri, (source_path, _) in VIRTUAL_DOCS.items()
}
_REPO_ASSET_TO_VIRTUAL: dict[str, str] = {
    source_path: virtual_uri for virtual_uri, (source_path, _) in VIRTUAL_STATIC_ASSETS.items()
}

QUADRANT_HISTORICAL_FALLBACKS: dict[str, tuple[str, ...]] = {
    "01-tutorials": ("guides/en/mariadb_management.md", "guides/en/index.md", "overview-en.md"),
    "02-how-to-guides": ("guides/en/tools_guide.md", "guides/en/index.md", "overview-en.md"),
    "03-reference": ("guides/en/index.md", "overview-en.md"),
    "04-explanation": ("guides/en/benchmarking.md", "guides/en/index.md", "overview-en.md"),
}

QUADRANT_HISTORICAL_FALLBACKS_FR: dict[str, tuple[str, ...]] = {
    "01-tutoriels": ("guides/fr/mariadb_management.md", "guides/fr/index.md", "overview-fr.md"),
    "02-guides-pratiques": ("guides/fr/guide_outils.md", "guides/fr/index.md", "overview-fr.md"),
    "03-reference": ("guides/fr/index.md", "overview-fr.md"),
    "04-explications": ("guides/fr/benchmarking.md", "guides/fr/index.md", "overview-fr.md"),
}

ALERT_MAP: dict[str, str] = {
    "NOTE": "note",
    "TIP": "tip",
    "IMPORTANT": "info",
    "WARNING": "warning",
    "CAUTION": "danger",
}

_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})(.*)$")
_ALERT_RE = re.compile(
    r"(?m)^([ \t]*)>[ \t]*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*([^\r\n]*)\r?\n"
    r"((?:[ \t]*>.*(?:\r?\n|$))*)"
)
_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_EXCLUDED_TARGET_RE = re.compile(
    r"(?i)(?:(?:^|/)\.env[^/]*$|\.(?:kdbx|keyx|pid|log)$)"
)
_HTML_ATTR_RE = re.compile(
    r"""(<(?:img|a|source)\b[^>]*?\b(?:src|href)\s*=\s*)(["'])([^"']+)\2""",
    re.IGNORECASE,
)
_LIGHTPATH_AUTOLINK_RE = re.compile(r"<www\.lightpath\.fr>", re.IGNORECASE)
_GOOGLE_DOCS_TAB_RE = re.compile(r"\?tab=t\.\d+(?=#|$)")
_FILE_TEST_DB_PREFIX = "file:///test_db/"


def gfm_slugify(value: str, separator: str = "-") -> str:
    """Slugify headings using GitHub Flavored Markdown anchor rules."""
    return "".join(
        separator if ch == " " else ch
        for ch in value.strip().lower()
        if ch.isalnum() or ch in (" ", "-", "_")
    )


def _effective_repo_ref(raw_ref: str | None = None) -> str:
    """Resolve the effective Git ref used for GitHub repository links."""
    ref = (
        raw_ref if raw_ref is not None else os.environ.get("TEST_DB_DOCS_REF", DEFAULT_REF)
    ).strip()
    if not ref or ref in {"WORKTREE", "HEAD", "origin/master", "master"}:
        return DEFAULT_REF
    return ref


def _split_fences(markdown: str) -> list[tuple[bool, str]]:
    """Split Markdown into `(is_fence, text)` chunks while preserving newlines."""
    chunks: list[tuple[bool, str]] = []
    buf: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in markdown.splitlines(keepends=True):
        stripped_nl = line.rstrip("\r\n")
        if not in_fence:
            match = _FENCE_RE.match(stripped_nl)
            if match:
                if buf:
                    chunks.append((False, "".join(buf)))
                    buf.clear()
                in_fence = True
                fence_char = match.group(2)[0]
                fence_len = len(match.group(2))
        else:
            lead = stripped_nl.lstrip(" \t")
            if (
                lead.startswith(fence_char)
                and len(lead) - len(lead.lstrip(fence_char)) >= fence_len
                and not lead.lstrip(fence_char).strip()
            ):
                buf.append(line)
                chunks.append((True, "".join(buf)))
                buf.clear()
                in_fence = False
                fence_char = ""
                fence_len = 0
                continue
        buf.append(line)

    if buf:
        chunks.append((in_fence, "".join(buf)))
    return chunks


def _format_github_alert(match: re.Match[str]) -> str:
    """Convert a matched GitHub alert blockquote into a Material admonition block."""
    ws = match.group(1)
    kind = ALERT_MAP[match.group(2).upper()]
    title = match.group(3).strip()
    body = match.group(4)
    out = [f'{ws}!!! {kind} "{title}"\n' if title else f"{ws}!!! {kind}\n"]
    for raw_line in body.splitlines(keepends=True):
        stripped = raw_line.rstrip("\r\n")
        inner = re.sub(r"^[ \t]*>[ \t]?", "", stripped)
        nl = raw_line[len(stripped) :] or "\n"
        out.append(nl if not inner.strip() else f"{ws}    {inner}{nl}")
    return "".join(out)


def convert_github_alerts(markdown: str) -> str:
    """Convert GitHub-style blockquote alerts into Material admonitions outside code fences."""
    return "".join(
        chunk if is_fence else _ALERT_RE.sub(_format_github_alert, chunk)
        for is_fence, chunk in _split_fences(markdown)
    )


def _is_escaped(text: str, pos: int) -> bool:
    """Return True if the character at `pos` is preceded by an odd number of backslashes."""
    cursor = pos - 1
    while cursor >= 0 and text[cursor] == "\\":
        cursor -= 1
    return ((pos - 1 - cursor) & 1) == 1


def _match_delimiter(
    text: str,
    start: int,
    open_ch: str,
    close_ch: str,
    skip_inline_code: bool,
) -> int | None:
    """Find matching closing delimiter while respecting escapes and inline code spans."""
    depth = 1
    idx = start + 1
    n = len(text)
    while idx < n:
        ch = text[idx]
        if skip_inline_code and ch == "`":
            tick_len = 1
            while idx + tick_len < n and text[idx + tick_len] == "`":
                tick_len += 1
            end = text.find("`" * tick_len, idx + tick_len)
            if end == -1:
                return None
            idx = end + tick_len
            continue
        if not skip_inline_code and ch == "\n":
            return None
        if ch == open_ch and not _is_escaped(text, idx):
            depth += 1
        elif ch == close_ch and not _is_escaped(text, idx):
            depth -= 1
            if depth == 0:
                return idx
        elif skip_inline_code and ch == "\n" and idx + 1 < n and text[idx + 1] == "\n":
            return None
        idx += 1
    return None


def _split_destination(raw_dest: str) -> tuple[str, str, bool]:
    """Split a Markdown link destination into `(url, title_suffix, had_angle_brackets)`."""
    stripped = raw_dest.strip()
    if stripped.startswith("<") and (end := stripped.find(">")) != -1:
        return stripped[1:end].strip(), stripped[end + 1 :], True
    for idx, ch in enumerate(stripped):
        if ch.isspace():
            return stripped[:idx], stripped[idx:], False
    return stripped, "", False


def _repo_root_for_docs_dir(docs_dir: Path) -> Path:
    """Resolve repository root from either `docs/` or `docs/fr/`."""
    if docs_dir.name == "fr" and docs_dir.parent.name == "docs":
        return docs_dir.parent.parent
    return docs_dir.parent


def _get_build_language(config: Any, docs_dir: Path | None = None) -> str:
    """Resolve active MkDocs theme language (`en` or `fr`) from config or docs_dir."""
    theme = getattr(config, "theme", None)
    if theme is None and isinstance(config, dict):
        theme = config.get("theme")
    raw_lang: Any = None
    if isinstance(theme, dict):
        raw_lang = theme.get("language")
    elif theme is not None:
        raw_lang = getattr(theme, "language", None)
        if raw_lang is None:
            try:
                raw_lang = theme["language"]
            except (KeyError, TypeError):
                raw_lang = None
    if isinstance(raw_lang, str) and raw_lang.strip().lower() == "fr":
        return "fr"
    if docs_dir is not None and docs_dir.name == "fr" and docs_dir.parent.name == "docs":
        return "fr"
    return "en"


def virtual_docs_for_language(lang: str) -> frozenset[str]:
    """Return allowed virtual document URIs for a single-language MkDocs build."""
    if lang == "fr":
        return VIRTUAL_DOCS_FR
    return VIRTUAL_DOCS_EN


def _adjust_alternate_links(config: Any) -> None:
    """Adjust `extra.alternate` EN/FR switcher links to match the current version base path."""
    extra = getattr(config, "extra", None)
    if extra is None and isinstance(config, dict):
        extra = config.get("extra")
    if not isinstance(extra, dict):
        return
    alternate = extra.get("alternate")
    if not isinstance(alternate, list):
        return

    site_url = getattr(config, "site_url", None)
    if site_url is None and isinstance(config, dict):
        site_url = config.get("site_url", "")
    site_path = urlsplit(str(site_url or "")).path or "/"
    if not site_path.startswith("/"):
        site_path = "/" + site_path
    if not site_path.endswith("/"):
        site_path += "/"
    base_path = site_path[:-3] if site_path.endswith("/fr/") else site_path
    if not base_path:
        base_path = "/"
    fr_path = "/fr/" if base_path == "/" else f"{base_path.rstrip('/')}/fr/"

    for entry in alternate:
        if not isinstance(entry, dict):
            continue
        entry_lang = str(entry.get("lang", "")).strip().lower()
        if entry_lang == "en":
            entry["link"] = base_path
        elif entry_lang == "fr":
            entry["link"] = fr_path


def _virtual_doc_available(
    virtual_uri: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None,
) -> bool:
    """Return True when a virtual doc is active in the current build or snapshot."""
    if virtual_uri not in available_root_docs:
        return False
    if docs_dir is not None:
        repo_root = _repo_root_for_docs_dir(docs_dir)
        # When repo_root contains real repository layout markers, verify the source file exists on disk.
        if (
            (repo_root / "README.md").is_file()
            or (repo_root / "documentation").is_dir()
            or (repo_root / "sirene").is_dir()
        ):
            return (repo_root / VIRTUAL_DOCS[virtual_uri][0]).is_file()
    return True


def _static_asset_available(
    virtual_uri: str,
    available_static_assets: frozenset[str] | None,
    docs_dir: Path | None,
) -> bool:
    """Return True when a virtual static asset is present in the current snapshot."""
    if available_static_assets is not None:
        return virtual_uri in available_static_assets
    if docs_dir is not None:
        repo_root = _repo_root_for_docs_dir(docs_dir)
        if (
            (repo_root / "README.md").is_file()
            or (repo_root / "documentation").is_dir()
            or (repo_root / "sirene").is_dir()
        ):
            return (repo_root / VIRTUAL_STATIC_ASSETS[virtual_uri][0]).is_file()
    return True


def _historical_overview_target(
    prefix: str,
    clean_repo: str,
    ref: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None = None,
    virtual_doc: str = "overview-en.md",
) -> str:
    """Resolve fallback target for historical tags when a quadrant document is absent."""
    if _virtual_doc_available(virtual_doc, available_root_docs, docs_dir):
        return f"{prefix}{virtual_doc}"
    source_path = VIRTUAL_DOCS.get(virtual_doc, ("README.md", ""))[0]
    return f"{clean_repo}/blob/{ref}/{source_path}"


def _resolve_static_asset_target(
    virtual_uri: str,
    source_rel: str,
    anchor: str,
    prefix: str,
    clean_repo: str,
    ref: str,
    available_root_docs: frozenset[str],
    available_static_assets: frozenset[str] | None,
    docs_dir: Path | None,
) -> str:
    """Resolve a virtual static asset or fall back cleanly on v1.9.0 where HTML docs did not exist."""
    if _static_asset_available(virtual_uri, available_static_assets, docs_dir):
        return f"{prefix}{virtual_uri}{anchor}"
    if virtual_uri == "guides/sirene_documentation.html":
        if _virtual_doc_available("sirene-quickstart.md", available_root_docs, docs_dir):
            return f"{prefix}sirene-quickstart.md"
        return _historical_overview_target(prefix, clean_repo, ref, available_root_docs, docs_dir)
    return f"{clean_repo}/blob/{ref}/{source_rel}{anchor}"


def _resolve_target(
    raw_url: str,
    page_src_path: str,
    prefix: str,
    ref: str,
    repo_url: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None = None,
    available_static_assets: frozenset[str] | None = None,
    build_lang: str | None = None,
) -> tuple[str | None, bool]:
    """Resolve a target URL or return `(None, True)` when excluded/neutralized."""
    if not raw_url:
        return raw_url, False

    clean_repo = repo_url.rstrip("/")
    repo_root = _repo_root_for_docs_dir(docs_dir) if docs_dir is not None else None
    effective_lang = build_lang or (
        "fr"
        if (docs_dir is not None and docs_dir.name == "fr" and docs_dir.parent.name == "docs")
        else "en"
    )
    docs_repo_prefix = "docs/fr" if effective_lang == "fr" else "docs"

    # Rewrite legacy file:///test_db/<rel> links (deadlock/gap_locking guides) to GitHub blob/tree URLs.
    if raw_url.startswith(_FILE_TEST_DB_PREFIX):
        rel_with_frag = raw_url[len(_FILE_TEST_DB_PREFIX) :]
        rel_path, sep, frag = rel_with_frag.partition("#")
        anchor = f"{sep}{frag}" if sep else ""
        clean_rel = posixpath.normpath(rel_path).lstrip("/")
        if _EXCLUDED_TARGET_RE.search(clean_rel) or _EXCLUDED_TARGET_RE.search(rel_path):
            return None, True
        is_dir = rel_path.endswith("/") or (
            repo_root is not None and (repo_root / clean_rel).is_dir()
        )
        kind = "tree" if is_dir else "blob"
        trailing = "/" if rel_path.endswith("/") and clean_rel and not clean_rel.endswith("/") else ""
        return f"{clean_repo}/{kind}/{ref}/{clean_rel}{trailing}{anchor}", False

    # Clean legacy Google Docs TOC anchors (?tab=t.0#heading= or #heading=) in doc_employees docs.
    if raw_url in {"?tab=t.0#heading=", "#heading="} or raw_url.endswith(
        ("employees.md#heading=", "employees_fr.md#heading=")
    ):
        return "#", False
    cleaned_url = _GOOGLE_DOCS_TAB_RE.sub("", raw_url)
    if cleaned_url.endswith("#heading="):
        cleaned_url = cleaned_url[: -len("#heading=")] or "#"

    if not cleaned_url or cleaned_url.startswith(("#", "/", "\\")) or _SCHEME_RE.match(cleaned_url):
        return cleaned_url, False

    path_part, sep, frag = cleaned_url.partition("#")
    anchor = f"{sep}{frag}" if sep else ""
    if not path_part:
        return cleaned_url, False

    norm_src = page_src_path.replace("\\", "/").lstrip("/")
    if norm_src in VIRTUAL_DOCS:
        src_dir = VIRTUAL_DOCS[norm_src][1]
    elif norm_src in VIRTUAL_FR_ROOT_DOCS:
        src_dir = VIRTUAL_FR_ROOT_DOCS[norm_src][1]
    else:
        src_dir = posixpath.dirname(f"{docs_repo_prefix}/{norm_src}")
    had_trailing_slash = path_part.endswith("/")
    repo_rel = (
        posixpath.normpath(posixpath.join(src_dir, path_part))
        if src_dir
        else posixpath.normpath(path_part)
    )

    if _EXCLUDED_TARGET_RE.search(repo_rel) or _EXCLUDED_TARGET_RE.search(path_part):
        return None, True

    if repo_rel in _REPO_ASSET_TO_VIRTUAL:
        virtual_asset = _REPO_ASSET_TO_VIRTUAL[repo_rel]
        return (
            _resolve_static_asset_target(
                virtual_uri=virtual_asset,
                source_rel=repo_rel,
                anchor=anchor,
                prefix=prefix,
                clean_repo=clean_repo,
                ref=ref,
                available_root_docs=available_root_docs,
                available_static_assets=available_static_assets,
                docs_dir=docs_dir,
            ),
            False,
        )

    if repo_rel in _REPO_DOC_TO_VIRTUAL:
        virtual_uri = _REPO_DOC_TO_VIRTUAL[repo_rel]
        if _virtual_doc_available(virtual_uri, available_root_docs, docs_dir):
            return f"{prefix}{virtual_uri}{anchor}", False
        if (
            virtual_uri in {"guides/en/sirene_platform.md", "guides/fr/sirene_platform.md"}
            and _virtual_doc_available("sirene-quickstart.md", available_root_docs, docs_dir)
        ):
            return f"{prefix}sirene-quickstart.md", False
        return f"{clean_repo}/blob/{ref}/{repo_rel}{anchor}", False

    if repo_rel == "docs/index.md":
        if effective_lang == "en":
            return f"{prefix}index.md{anchor}", False
        return f"{clean_repo}/blob/{ref}/docs/index.md{anchor}", False

    if repo_rel == "docs/fr/index.md":
        if effective_lang == "fr":
            return f"{prefix}index.md{anchor}", False
        return f"{clean_repo}/blob/{ref}/docs/fr/index.md{anchor}", False

    if repo_rel in ("docs/ACTION_LOGBOOK.md", "docs/RCA_REGISTER.md"):
        return f"{prefix}{repo_rel[len('docs/'):]}{anchor}", False

    if repo_rel.startswith(("docs/assets/", "docs/stylesheets/", "docs/javascripts/")):
        return f"{prefix}{repo_rel[len('docs/'):]}{anchor}", False

    if repo_rel.startswith("docs/"):
        doc_subpath = repo_rel[len("docs/") :]
        if doc_subpath in VIRTUAL_STATIC_ASSETS:
            return (
                _resolve_static_asset_target(
                    virtual_uri=doc_subpath,
                    source_rel=VIRTUAL_STATIC_ASSETS[doc_subpath][0],
                    anchor=anchor,
                    prefix=prefix,
                    clean_repo=clean_repo,
                    ref=ref,
                    available_root_docs=available_root_docs,
                    available_static_assets=available_static_assets,
                    docs_dir=docs_dir,
                ),
                False,
            )

        if doc_subpath in VIRTUAL_DOCS and (
            docs_dir is None or not (docs_dir / doc_subpath).is_file()
        ):
            if _virtual_doc_available(doc_subpath, available_root_docs, docs_dir):
                return f"{prefix}{doc_subpath}{anchor}", False
            if (
                doc_subpath in {"guides/en/sirene_platform.md", "guides/fr/sirene_platform.md"}
                and _virtual_doc_available("sirene-quickstart.md", available_root_docs, docs_dir)
            ):
                return f"{prefix}sirene-quickstart.md", False
            return f"{clean_repo}/blob/{ref}/{VIRTUAL_DOCS[doc_subpath][0]}{anchor}", False

        if effective_lang == "en" and doc_subpath.startswith("fr/"):
            is_dir_target = had_trailing_slash or (repo_root is not None and (repo_root / repo_rel).is_dir())
            kind = "tree" if is_dir_target else "blob"
            trailing = "/" if had_trailing_slash and not repo_rel.endswith("/") else ""
            return f"{clean_repo}/{kind}/{ref}/{repo_rel}{trailing}{anchor}", False

        if effective_lang == "fr":
            if repo_rel.startswith("docs/fr/"):
                doc_subpath = repo_rel[len("docs/fr/") :]
            else:
                is_dir_target = had_trailing_slash or (repo_root is not None and (repo_root / repo_rel).is_dir())
                kind = "tree" if is_dir_target else "blob"
                trailing = "/" if had_trailing_slash and not repo_rel.endswith("/") else ""
                return f"{clean_repo}/{kind}/{ref}/{repo_rel}{trailing}{anchor}", False

        fallbacks = (
            QUADRANT_HISTORICAL_FALLBACKS_FR if effective_lang == "fr" else QUADRANT_HISTORICAL_FALLBACKS
        )
        primary_quadrant = "01-tutoriels" if effective_lang == "fr" else "01-tutorials"
        default_overview = "overview-fr.md" if effective_lang == "fr" else "overview-en.md"

        if docs_dir is not None:
            top_segment = doc_subpath.split("/", 1)[0]
            if top_segment in fallbacks and not (docs_dir / top_segment).is_dir():
                for candidate in fallbacks[top_segment]:
                    if (docs_dir / candidate).is_file() or (
                        candidate in VIRTUAL_DOCS
                        and _virtual_doc_available(candidate, available_root_docs, docs_dir)
                    ):
                        return f"{prefix}{candidate}", False
                return (
                    _historical_overview_target(
                        prefix, clean_repo, ref, available_root_docs, docs_dir, default_overview
                    ),
                    False,
                )

            if (
                norm_src == "index.md"
                and not (docs_dir / primary_quadrant).is_dir()
                and not (docs_dir / doc_subpath).exists()
                and doc_subpath not in available_root_docs
            ):
                if effective_lang == "fr" or doc_subpath.startswith(("guides/fr/", "fr/")):
                    if _virtual_doc_available("guides/fr/index.md", available_root_docs, docs_dir):
                        return f"{prefix}guides/fr/index.md", False
                    return (
                        _historical_overview_target(
                            prefix, clean_repo, ref, available_root_docs, docs_dir, "overview-fr.md"
                        ),
                        False,
                    )
                if _virtual_doc_available("guides/en/index.md", available_root_docs, docs_dir):
                    return f"{prefix}guides/en/index.md", False
                return (
                    _historical_overview_target(
                        prefix, clean_repo, ref, available_root_docs, docs_dir
                    ),
                    False,
                )

            candidate_path = docs_dir / doc_subpath
            if candidate_path.is_dir() and (candidate_path / "index.md").is_file():
                index_subpath = posixpath.join(doc_subpath.rstrip("/"), "index.md")
                return f"{prefix}{index_subpath}{anchor}", False

        trailing = "/" if had_trailing_slash and doc_subpath and not doc_subpath.endswith("/") else ""
        return f"{prefix}{doc_subpath}{trailing}{anchor}", False

    if repo_rel in (".", "..") or repo_rel.startswith("../"):
        return clean_repo, False

    is_dir_target = had_trailing_slash or (repo_root is not None and (repo_root / repo_rel).is_dir())
    kind = "tree" if is_dir_target else "blob"
    trailing = "/" if had_trailing_slash and not repo_rel.endswith("/") else ""
    return f"{clean_repo}/{kind}/{ref}/{repo_rel}{trailing}{anchor}", False


def _rewrite_html_attributes(
    segment: str,
    page_src_path: str,
    html_prefix: str,
    ref: str,
    repo_url: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None,
    available_static_assets: frozenset[str] | None,
    build_lang: str | None = None,
) -> str:
    """Rewrite relative HTML `src`/`href` attributes outside inline code."""

    def _replace_attr(match: re.Match[str]) -> str:
        resolved, neutralized = _resolve_target(
            match.group(3),
            page_src_path=page_src_path,
            prefix=html_prefix,
            ref=ref,
            repo_url=repo_url,
            available_root_docs=available_root_docs,
            docs_dir=docs_dir,
            available_static_assets=available_static_assets,
            build_lang=build_lang,
        )
        new_val = "#" if neutralized else str(resolved)
        return f"{match.group(1)}{match.group(2)}{new_val}{match.group(2)}"

    return _HTML_ATTR_RE.sub(_replace_attr, segment)


def _rewrite_plain_segment(
    segment: str,
    page_src_path: str,
    html_prefix: str,
    ref: str,
    repo_url: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None,
    available_static_assets: frozenset[str] | None,
    build_lang: str | None = None,
) -> str:
    """Convert `<www.lightpath.fr>` autolinks and rewrite HTML attributes outside inline code."""
    normalized = _LIGHTPATH_AUTOLINK_RE.sub(
        "[www.lightpath.fr](https://www.lightpath.fr)",
        segment,
    )
    return _rewrite_html_attributes(
        normalized,
        page_src_path=page_src_path,
        html_prefix=html_prefix,
        ref=ref,
        repo_url=repo_url,
        available_root_docs=available_root_docs,
        docs_dir=docs_dir,
        available_static_assets=available_static_assets,
        build_lang=build_lang,
    )


def _rewrite_prose_segment(
    text: str,
    page_src_path: str,
    md_prefix: str,
    html_prefix: str,
    ref: str,
    repo_url: str,
    available_root_docs: frozenset[str],
    docs_dir: Path | None = None,
    available_static_assets: frozenset[str] | None = None,
    build_lang: str | None = None,
) -> str:
    """Rewrite Markdown links, HTML `src`/`href`, and legacy autolinks outside inline code."""
    out: list[str] = []
    prose_start = 0
    idx = 0
    n = len(text)

    def _flush_plain(end_idx: int) -> None:
        if end_idx > prose_start:
            out.append(
                _rewrite_plain_segment(
                    text[prose_start:end_idx],
                    page_src_path=page_src_path,
                    html_prefix=html_prefix,
                    ref=ref,
                    repo_url=repo_url,
                    available_root_docs=available_root_docs,
                    docs_dir=docs_dir,
                    available_static_assets=available_static_assets,
                    build_lang=build_lang,
                )
            )

    while idx < n:
        ch = text[idx]
        if ch == "`":
            _flush_plain(idx)
            tick_len = 1
            while idx + tick_len < n and text[idx + tick_len] == "`":
                tick_len += 1
            close_pos = text.find("`" * tick_len, idx + tick_len)
            if close_pos == -1:
                out.append(text[idx:])
                prose_start = n
                break
            out.append(text[idx : close_pos + tick_len])
            idx = prose_start = close_pos + tick_len
            continue

        is_img = ch == "!" and idx + 1 < n and text[idx + 1] == "[" and not _is_escaped(text, idx)
        bracket_start = idx + 1 if is_img else (idx if ch == "[" and not _is_escaped(text, idx) else -1)
        if bracket_start != -1:
            bracket_end = _match_delimiter(text, bracket_start, "[", "]", skip_inline_code=True)
            if bracket_end is not None and bracket_end + 1 < n and text[bracket_end + 1] == "(":
                paren_end = _match_delimiter(text, bracket_end + 1, "(", ")", skip_inline_code=False)
                if paren_end is not None:
                    _flush_plain(idx)
                    label = _rewrite_prose_segment(
                        text[bracket_start + 1 : bracket_end],
                        page_src_path=page_src_path,
                        md_prefix=md_prefix,
                        html_prefix=html_prefix,
                        ref=ref,
                        repo_url=repo_url,
                        available_root_docs=available_root_docs,
                        docs_dir=docs_dir,
                        available_static_assets=available_static_assets,
                        build_lang=build_lang,
                    )
                    url_part, title_suffix, had_angles = _split_destination(
                        text[bracket_end + 2 : paren_end]
                    )
                    resolved, neutralized = _resolve_target(
                        url_part,
                        page_src_path=page_src_path,
                        prefix=md_prefix,
                        ref=ref,
                        repo_url=repo_url,
                        available_root_docs=available_root_docs,
                        docs_dir=docs_dir,
                        available_static_assets=available_static_assets,
                        build_lang=build_lang,
                    )
                    if neutralized:
                        out.append("" if is_img else label)
                    else:
                        formatted_url = f"<{resolved}>" if had_angles else str(resolved)
                        bang = "!" if is_img else ""
                        out.append(f"{bang}[{label}]({formatted_url}{title_suffix})")
                    idx = prose_start = paren_end + 1
                    continue

        idx += 1

    _flush_plain(n)
    return "".join(out)


def rewrite_relative_links(
    markdown: str,
    page_src_path: str,
    ref: str = DEFAULT_REF,
    repo_url: str = DEFAULT_REPO_URL,
    docs_dir: Path | None = None,
    use_directory_urls: bool = True,
    available_root_docs: Iterable[str] | None = None,
    available_static_assets: Iterable[str] | None = None,
    build_lang: str | None = None,
) -> str:
    """Rewrite repository-relative Markdown and HTML links outside fenced code blocks."""
    norm = page_src_path.replace("\\", "/").lstrip("/")
    md_depth = norm.count("/")
    html_depth = md_depth + (
        0 if (not use_directory_urls or norm == "index.md" or norm.endswith("/index.md")) else 1
    )
    resolved_ref = _effective_repo_ref(ref)
    resolved_docs = Path(docs_dir) if docs_dir is not None else None
    root_docs = (
        frozenset(VIRTUAL_DOCS) if available_root_docs is None else frozenset(available_root_docs)
    )
    static_assets = (
        None if available_static_assets is None else frozenset(available_static_assets)
    )
    return "".join(
        chunk
        if is_fence
        else _rewrite_prose_segment(
            chunk,
            page_src_path=norm,
            md_prefix="../" * md_depth,
            html_prefix="../" * html_depth,
            ref=resolved_ref,
            repo_url=repo_url,
            available_root_docs=root_docs,
            docs_dir=resolved_docs,
            available_static_assets=static_assets,
            build_lang=build_lang,
        )
        for is_fence, chunk in _split_fences(markdown)
    )


def _nav_doc_exists(
    rel_path: str,
    docs_dir: Path,
    repo_root: Path,
    allowed_virtual_docs: frozenset[str] | None = None,
) -> bool:
    """Return True if a navigation target exists in `docs_dir` or as an active virtual doc."""
    if (docs_dir / rel_path).is_file():
        return True
    if rel_path in VIRTUAL_DOCS:
        if allowed_virtual_docs is not None and rel_path not in allowed_virtual_docs:
            return False
        if (repo_root / VIRTUAL_DOCS[rel_path][0]).is_file():
            return True
    if rel_path in VIRTUAL_STATIC_ASSETS and (repo_root / VIRTUAL_STATIC_ASSETS[rel_path][0]).is_file():
        return True
    if (
        docs_dir.name == "fr"
        and rel_path in VIRTUAL_FR_ROOT_DOCS
        and (repo_root / VIRTUAL_FR_ROOT_DOCS[rel_path][0]).is_file()
    ):
        return True
    return False


def _prune_nav_list(
    items: list[Any],
    docs_dir: Path,
    repo_root: Path,
    allowed_virtual_docs: frozenset[str] | None = None,
) -> list[Any]:
    """Recursively prune missing pages and empty sections from a MkDocs navigation list."""
    pruned: list[Any] = []
    for entry in items:
        if isinstance(entry, str):
            if _nav_doc_exists(entry, docs_dir, repo_root, allowed_virtual_docs):
                pruned.append(entry)
            continue

        if isinstance(entry, dict):
            kept_dict: dict[str, Any] = {}
            for title, target in entry.items():
                if isinstance(target, str):
                    if _nav_doc_exists(target, docs_dir, repo_root, allowed_virtual_docs):
                        kept_dict[title] = target
                elif isinstance(target, list):
                    nested = _prune_nav_list(target, docs_dir, repo_root, allowed_virtual_docs)
                    if nested:
                        kept_dict[title] = nested
                elif isinstance(target, dict):
                    nested_dict = _prune_nav_list([target], docs_dir, repo_root, allowed_virtual_docs)
                    if nested_dict:
                        kept_dict[title] = nested_dict[0]
            if kept_dict:
                pruned.append(kept_dict)
    return pruned


def prune_nav_for_existing_files(
    nav: list[Any] | None,
    docs_dir: Path,
    repo_root: Path,
    allowed_virtual_docs: Iterable[str] | None = None,
) -> list[Any]:
    """Prune missing pages and empty sections from a MkDocs navigation list."""
    if not nav:
        return []
    allowed = None if allowed_virtual_docs is None else frozenset(allowed_virtual_docs)
    return _prune_nav_list(list(nav), Path(docs_dir), Path(repo_root), allowed)


def on_config(config: Any) -> Any:
    """Configure environment-driven `site_url`, `edit_uri`, switcher links, GFM slugifier, and pruned nav."""
    site_url = os.environ.get("TEST_DB_DOCS_SITE_URL", "").strip()
    if site_url:
        config.site_url = site_url.rstrip("/") + "/"

    docs_dir = Path(config.docs_dir)
    lang = _get_build_language(config, docs_dir=docs_dir)
    docs_prefix = "docs/fr" if (lang == "fr" and docs_dir.name == "fr") else "docs"
    config.edit_uri = f"edit/master/{docs_prefix}/" if _effective_repo_ref() == "master" else ""

    mdx = getattr(config, "mdx_configs", None)
    if isinstance(mdx, dict):
        toc_cfg = mdx.setdefault("toc", {})
        if isinstance(toc_cfg, dict) and not toc_cfg.get("slugify"):
            toc_cfg["slugify"] = gfm_slugify

    _adjust_alternate_links(config)

    repo_root = _repo_root_for_docs_dir(docs_dir)
    if getattr(config, "nav", None):
        config.nav = prune_nav_for_existing_files(
            config.nav,
            docs_dir=docs_dir,
            repo_root=repo_root,
            allowed_virtual_docs=virtual_docs_for_language(lang),
        )
    return config


def on_files(files: Files, config: Any) -> Files:
    """Exclude sensitive runtime files and inject language-isolated virtual docs and static assets."""
    from mkdocs.structure.files import File, Files as MkDocsFiles, InclusionLevel

    docs_dir = Path(config.docs_dir)
    lang = _get_build_language(config, docs_dir=docs_dir)
    allowed_virtual = virtual_docs_for_language(lang)

    kept: list[File] = []
    for file_obj in list(files):
        if _EXCLUDED_TARGET_RE.search(file_obj.src_uri):
            file_obj.inclusion = InclusionLevel.EXCLUDED
            continue
        kept.append(file_obj)

    if len(kept) != len(files):
        files = MkDocsFiles(kept)

    repo_root = _repo_root_for_docs_dir(docs_dir)
    for virtual_uri, (source_rel, _) in VIRTUAL_DOCS.items():
        if virtual_uri not in allowed_virtual:
            continue
        src_path = repo_root / source_rel
        if src_path.is_file() and files.get_file_from_path(virtual_uri) is None:
            files.append(File.generated(config, virtual_uri, abs_src_path=str(src_path)))

    for virtual_uri, (source_rel, _) in VIRTUAL_STATIC_ASSETS.items():
        src_path = repo_root / source_rel
        if src_path.is_file() and files.get_file_from_path(virtual_uri) is None:
            files.append(File.generated(config, virtual_uri, abs_src_path=str(src_path)))

    if lang == "fr" and docs_dir.name == "fr":
        for virtual_uri, (source_rel, _) in VIRTUAL_FR_ROOT_DOCS.items():
            src_path = repo_root / source_rel
            if src_path.is_file() and files.get_file_from_path(virtual_uri) is None:
                files.append(File.generated(config, virtual_uri, abs_src_path=str(src_path)))
        for virtual_uri, source_rel in VIRTUAL_FR_STATIC_ASSETS.items():
            src_path = repo_root / source_rel
            if src_path.is_file() and files.get_file_from_path(virtual_uri) is None:
                files.append(File.generated(config, virtual_uri, abs_src_path=str(src_path)))

    return files


def on_page_markdown(markdown: str, page: Any, config: Any, files: Files) -> str:
    """Convert GitHub alerts, normalize Changelog H1, rewrite links, and update virtual edit URLs."""
    src = getattr(page.file, "src_uri", None) or str(page.file.src_path).replace("\\", "/")
    ref = _effective_repo_ref()
    repo_url = (getattr(config, "repo_url", None) or DEFAULT_REPO_URL).rstrip("/")
    raw_docs = getattr(config, "docs_dir", None) or (
        config.get("docs_dir") if isinstance(config, dict) else None
    )
    docs_dir = Path(raw_docs) if raw_docs else None
    build_lang = _get_build_language(config, docs_dir=docs_dir)

    if src in VIRTUAL_DOCS:
        page.edit_url = f"{repo_url}/edit/master/{VIRTUAL_DOCS[src][0]}" if ref == "master" else None
    elif src in VIRTUAL_FR_ROOT_DOCS and build_lang == "fr":
        page.edit_url = (
            f"{repo_url}/edit/master/{VIRTUAL_FR_ROOT_DOCS[src][0]}" if ref == "master" else None
        )

    if src == "CHANGELOG.md" and not markdown.lstrip().startswith("# "):
        markdown = f"# Changelog\n\n{markdown}"

    available_root_docs: Iterable[str] | None = (
        [name for name in VIRTUAL_DOCS if files.get_file_from_path(name) is not None]
        if files is not None
        else None
    )
    available_static_assets: Iterable[str] | None = (
        [name for name in VIRTUAL_STATIC_ASSETS if files.get_file_from_path(name) is not None]
        if files is not None
        else None
    )
    return rewrite_relative_links(
        convert_github_alerts(markdown),
        page_src_path=src,
        ref=ref,
        repo_url=repo_url,
        docs_dir=docs_dir,
        use_directory_urls=bool(getattr(config, "use_directory_urls", True)),
        available_root_docs=available_root_docs,
        available_static_assets=available_static_assets,
        build_lang=build_lang,
    )
