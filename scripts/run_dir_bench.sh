#!/bin/bash
# scripts/run_dir_bench.sh
# ============================================================================
# Sysbench Directory Transaction Runner
# ============================================================================
# Purpose:
#   Orchestrates the execution of directory-based SQL transactions.
#   It synchronizes local SQL files and the Lua driver with a Docker container
#   before launching the stress test.
#
# Logic:
#   1. Parse CLI arguments (threads, time, host, etc.).
#   2. Detect if the target MariaDB container is running.
#   3. If Docker:
#      - Synchronize scripts/dir_transactions_sysbench.lua to /tmp.
#      - Synchronize provided --sql-dir to /tmp/bench_dir/sql/ inside container.
#      - Execute sysbench inside the container.
#   4. If Local:
#      - Execute sysbench directly using local paths.
# ============================================================================

set -euo pipefail

# Configuration with defaults from environment or hardcoded values
CONTAINER_NAME="${CONTAINER_NAME:-mariadb-11-8}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-employees}"
THREADS="${THREADS:-4}"
TIME="${TIME:-60}"
SQL_DIR=""

show_usage() {
    echo "Usage: $0 --sql-dir <directory> [options]"
    echo ""
    echo "Options:"
    echo "  --sql-dir PATH      Directory containing .sql files (mandatory)"
    echo "  --threads N         Number of threads (default: $THREADS)"
    echo "  --time N            Duration in seconds (default: $TIME)"
    echo "  --host IP/NAME      Database host (default: $DB_HOST)"
    echo "  --container NAME    Docker container name (default: $CONTAINER_NAME)"
    echo "  --user USER         Database user (default: $DB_USER)"
    echo "  --password PASS     Database password (default: $DB_PASS)"
    echo "  --db DB             Database name (default: $DB_NAME)"
    echo ""
}

# Parse Command Line Arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sql-dir) SQL_DIR="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        --time) TIME="$2"; shift 2 ;;
        --host) DB_HOST="$2"; shift 2 ;;
        --container) CONTAINER_NAME="$2"; shift 2 ;;
        --user) DB_USER="$2"; shift 2 ;;
        --password) DB_PASS="$2"; shift 2 ;;
        --db) DB_NAME="$2"; shift 2 ;;
        --help|-h) show_usage; exit 0 ;;
        *) echo "Unknown option: $1"; show_usage; exit 1 ;;
    esac
done

# Mandatory Parameter Check
if [[ -z "$SQL_DIR" ]]; then
    echo "Error: --sql-dir is mandatory."
    show_usage
    exit 1
fi

if [[ ! -d "$SQL_DIR" ]]; then
    echo "Error: Directory $SQL_DIR does not exist."
    exit 1
fi

# Locate the Lua driver script relative to this script
SCRIPTS_DIR="$(dirname "$0")"
LUA_SCRIPT="$SCRIPTS_DIR/dir_transactions_sysbench.lua"

if [[ ! -f "$LUA_SCRIPT" ]]; then
    echo "Error: $LUA_SCRIPT not found."
    exit 1
fi

echo "🚀 Preparing simulation..."
echo "📂 SQL Directory: $SQL_DIR"
echo "🧵 Threads: $THREADS"
echo "⏱️ Time: ${TIME}s"

# STRATEGY: Check if container exists to decide between Docker or Local execution
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🐳 Running inside Docker container: $CONTAINER_NAME"
    
    # 1. Prepare container environment
    docker exec -i "$CONTAINER_NAME" mkdir -p /tmp/bench_dir
    docker cp "$LUA_SCRIPT" "$CONTAINER_NAME:/tmp/dir_transactions_sysbench.lua"
    
    # 2. Synchronize SQL transactions
    # We clear the remote directory first to avoid mixing different test scenarios.
    docker exec -i "$CONTAINER_NAME" rm -rf /tmp/bench_dir/sql
    docker exec -i "$CONTAINER_NAME" mkdir -p /tmp/bench_dir/sql
    docker cp "$SQL_DIR/." "$CONTAINER_NAME:/tmp/bench_dir/sql/"

    # 3. Execute sysbench inside the container scope
    docker exec -i "$CONTAINER_NAME" sysbench \
        --mysql-host="$DB_HOST" \
        --mysql-user="$DB_USER" \
        --mysql-password="$DB_PASS" \
        --mysql-db="$DB_NAME" \
        --sql-dir="/tmp/bench_dir/sql/" \
        --threads="$THREADS" \
        --time="$TIME" \
        --events=0 \
        /tmp/dir_transactions_sysbench.lua run
else
    # FALLBACK: Local execution (useful for standalone DBs or non-docker labs)
    echo "💻 Running locally (sysbench must be installed)"
    sysbench \
        --mysql-host="$DB_HOST" \
        --mysql-user="$DB_USER" \
        --mysql-password="$DB_PASS" \
        --mysql-db="$DB_NAME" \
        --sql-dir="$SQL_DIR" \
        --threads="$THREADS" \
        --time="$TIME" \
        --events=0 \
        "$LUA_SCRIPT" run
fi
