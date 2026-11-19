"""Tests verifying repository governance registers and compliance hygiene."""

from __future__ import annotations

from pathlib import Path
import re

import pytest

pytestmark = pytest.mark.governance

HOST_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    re.compile(r"[A-Za-z]:/Users/", re.IGNORECASE),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
)

SECRET_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9\-_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)

FRENCH_PROSE_PATTERN = re.compile(
    r"\b(?:Objectif|Contexte|Résultat|Terminé|Problème|Étapes?|Journal|Registre|"
    r"Amélioration|Décision|Démarrage|Chargement|Données|Entreprise)\b",
    re.IGNORECASE,
)

FRENCH_DIACRITIC_PATTERN = re.compile(r"[éèêëàâùûüîïôçÉÈÊËÀÂÙÛÜÎÏÔÇ]")


def _governance_files(repo_root: Path) -> dict[str, Path]:
    return {
        "action_logbook": repo_root / "docs" / "ACTION_LOGBOOK.md",
        "rca_register": repo_root / "docs" / "RCA_REGISTER.md",
        "governance_rules": repo_root / ".agents" / "rules" / "project-governance.md",
        "project_context": repo_root / "PROJECT-CONTEXT.md",
    }


def test_governance_files_exist(repo_root: Path) -> None:
    """Ensure all required governance documents exist at repository root."""
    files = _governance_files(repo_root)
    missing = [str(path) for path in files.values() if not path.is_file()]
    assert not missing, f"Missing governance files: {missing}"


def test_action_logbook_required_sections(repo_root: Path) -> None:
    """Verify docs/ACTION_LOGBOOK.md contains required lifecycle sections."""
    content = _governance_files(repo_root)["action_logbook"].read_text(encoding="utf-8")
    for heading in ("Strategic Roadmap", "Ongoing Actions", "Completed Actions"):
        assert heading in content, f"Missing required section '{heading}' in ACTION_LOGBOOK.md"


def test_rca_register_required_prefixes(repo_root: Path) -> None:
    """Verify docs/RCA_REGISTER.md tracks RCA, IMP, APP, and IDEA entries."""
    content = _governance_files(repo_root)["rca_register"].read_text(encoding="utf-8")
    for prefix in ("RCA-", "IMP-", "APP-", "IDEA-"):
        assert prefix in content, f"Missing required register prefix '{prefix}' in RCA_REGISTER.md"


def test_project_context_is_bounded(repo_root: Path) -> None:
    """Verify PROJECT-CONTEXT.md stays concise and bounded."""
    content = _governance_files(repo_root)["project_context"].read_text(encoding="utf-8")
    words = content.split()
    assert 10 <= len(words) <= 180, f"PROJECT-CONTEXT.md word count out of bounds: {len(words)}"


def test_governance_files_are_strictly_english(repo_root: Path) -> None:
    """Ensure governance registers contain English prose without French leaks."""
    for name, path in _governance_files(repo_root).items():
        content = path.read_text(encoding="utf-8")
        assert not FRENCH_PROSE_PATTERN.search(
            content
        ), f"French prose detected in {name} ({path.name})"
        assert not FRENCH_DIACRITIC_PATTERN.search(
            content
        ), f"French diacritics detected in {name} ({path.name})"


def test_governance_files_have_no_host_paths_or_secrets(repo_root: Path) -> None:
    """Ensure zero local host paths or non-ephemeral secrets appear in governance docs."""
    for name, path in _governance_files(repo_root).items():
        content = path.read_text(encoding="utf-8")
        for pattern in HOST_PATH_PATTERNS:
            assert not pattern.search(
                content
            ), f"Local host path pattern {pattern.pattern!r} found in {name}"
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(
                content
            ), f"Potential secret pattern {pattern.pattern!r} found in {name}"
