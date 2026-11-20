"""CLI wrapper for Sirene 3NF multi-master PostgreSQL qualification probes."""

from __future__ import annotations

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirene_etl.mm_probe import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
