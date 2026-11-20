"""Shared pytest configuration and fixtures for the Sirene ETL test suite."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Iterator

import pytest


TESTS_DIR = Path(__file__).resolve().parent
SIRENE_DIR = TESTS_DIR.parent
SRC_DIR = SIRENE_DIR / "src"

if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _resolve_repo_root() -> Path:
    """Locate the repository root containing governance docs and sirene/."""
    for candidate in (TESTS_DIR, *TESTS_DIR.parents):
        if (candidate / "PROJECT-CONTEXT.md").exists() or (
            candidate / "docs" / "ACTION_LOGBOOK.md"
        ).exists():
            return candidate
    workspace = Path("/workspace")
    if (workspace / "PROJECT-CONTEXT.md").exists() or (
        workspace / "docs" / "ACTION_LOGBOOK.md"
    ).exists():
        return workspace
    for candidate in (TESTS_DIR, *TESTS_DIR.parents):
        if (candidate / ".git").exists():
            return candidate
    return SIRENE_DIR.parent


REPO_ROOT = _resolve_repo_root()


def pytest_configure(config: pytest.Config) -> None:
    """Register custom test markers to avoid unknown-mark warnings."""
    config.addinivalue_line("markers", "unit: Pure unit tests without external services.")
    config.addinivalue_line(
        "markers", "integration: End-to-end tests requiring PostgreSQL 18."
    )
    config.addinivalue_line(
        "markers", "governance: Repository documentation and hygiene checks."
    )


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the resolved repository root directory."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def sirene_dir() -> Path:
    """Return the sirene project directory."""
    return SIRENE_DIR


@pytest.fixture(scope="session")
def sql_dir() -> Path:
    """Return the sirene SQL scripts directory."""
    return SIRENE_DIR / "sql"


@pytest.fixture(scope="session")
def database_url() -> str:
    """Return the PostgreSQL DSN from environment or default settings."""
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url
    from sirene_etl.config import load_settings

    return load_settings().database_url


@pytest.fixture()
def db_conn(database_url: str) -> Iterator[object]:
    """Yield a live autocommit psycopg connection for setup and assertions."""
    import psycopg

    with psycopg.connect(database_url, autocommit=True) as conn:
        yield conn
