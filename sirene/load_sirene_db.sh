#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PSQL="${PSQL:-psql}"

echo "Loading synthetic SIRENE PostgreSQL 18 dataset..."
"$PSQL" -v ON_ERROR_STOP=1 -f "$SCRIPT_DIR/load_sirene.sql" "$@"
echo "Done loading SIRENE database."
