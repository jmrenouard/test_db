"""CLI wrapper for the Sirene autonomous data.gouv.fr watcher."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirene_etl.watcher import main  # noqa: E402, I001

if __name__ == "__main__":
    raise SystemExit(main())
