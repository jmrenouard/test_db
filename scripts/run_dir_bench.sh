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

# Load environment variables from .env if it exists
if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

# Configuration with defaults from environment or hardcoded values
CONTAINER_NAME="${CONTAINER_NAME:-mariadb-11-8}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-employees}"
THREADS="${THREADS:-4}"
TIME="${TIME:-60}"
SQL_DIR=""
SCRIPT_PATH=""

show_usage() {
    echo "Usage: $0 --sql-dir <directory> [options]"
    echo ""
    echo "Options:"
    echo "  --sql-dir PATH      Directory containing .sql files"
    echo "  --script PATH       Direct Lua script path (e.g. /usr/share/sysbench/oltp_read_only.lua)"
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
        --script) SCRIPT_PATH="$2"; shift 2 ;;
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
if [[ -z "$SQL_DIR" ]] && [[ -z "$SCRIPT_PATH" ]]; then
    echo "Error: Either --sql-dir or --script must be provided."
    show_usage
    exit 1
fi

if [[ -n "$SQL_DIR" ]] && [[ ! -d "$SQL_DIR" ]]; then
    echo "Error: Directory $SQL_DIR does not exist."
    exit 1
fi

# Locate the Lua driver script relative to this script
SCRIPTS_DIR="$(dirname "$0")"
LUA_SCRIPT="$SCRIPTS_DIR/dir_transactions_sysbench.lua"

if [[ -n "$SQL_DIR" ]] && [[ ! -f "$LUA_SCRIPT" ]]; then
    echo "Error: $LUA_SCRIPT not found."
    exit 1
fi

if [[ -n "$SCRIPT_PATH" ]]; then
    LUA_SCRIPT="$SCRIPT_PATH"
fi

echo "🚀 Preparing simulation..."
if [[ -n "$SQL_DIR" ]]; then
    echo "📂 SQL Directory: $SQL_DIR"
else
    echo "📜 Script Path: $SCRIPT_PATH"
fi
echo "🧵 Threads: $THREADS"
echo "⏱️ Time: ${TIME}s"

# Selection of Execution Mode
if [[ "${USE_CONTAINER:-true}" =~ ^(false|0|no|off|disable)$ ]]; then
    USE_CONTAINER=false
    echo -e "${YELLOW}ℹ️ USE_CONTAINER disabled by environment. Using local execution.${NC}"
else
    if [ -n "$CONTAINER_NAME" ] && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        USE_CONTAINER=true
        echo "🐳 Running inside Docker container: $CONTAINER_NAME"
    else
        USE_CONTAINER=false
        echo "⚠️ Container '$CONTAINER_NAME' not found or stopped. Falling back to local execution."
    fi
fi

if [ "$USE_CONTAINER" = true ]; then
    
    # 1. Prepare container environment
    docker exec -i "$CONTAINER_NAME" mkdir -p /tmp/bench_dir
    
    if [[ -n "$SQL_DIR" ]]; then
        docker cp "$LUA_SCRIPT" "$CONTAINER_NAME:/tmp/dir_transactions_sysbench.lua"
        
        # 2. Synchronize SQL transactions
        # We clear the remote directory first to avoid mixing different test scenarios.
        docker exec -i "$CONTAINER_NAME" rm -rf /tmp/bench_dir/sql
        docker exec -i "$CONTAINER_NAME" mkdir -p /tmp/bench_dir/sql
        docker cp "$SQL_DIR/." "$CONTAINER_NAME:/tmp/bench_dir/sql/"
    fi

    # 3. Execute sysbench inside the container scope
    sb_container_cmd=(sysbench \
        --mysql-host="$DB_HOST" \
        --mysql-user="$DB_USER" \
        --mysql-password="$DB_PASS" \
        --mysql-db="$DB_NAME" \
        --threads="$THREADS" \
        --time="$TIME" \
        --events=0)
    
    if [[ -n "$SQL_DIR" ]]; then
        sb_container_cmd+=(--sql-dir="/tmp/bench_dir/sql/" "/tmp/dir_transactions_sysbench.lua")
    else
        sb_container_cmd+=("$SCRIPT_PATH")
    fi
    
    docker exec -i "$CONTAINER_NAME" "${sb_container_cmd[@]}" run
else
    # FALLBACK: Local execution (useful for standalone DBs or non-docker labs)
    echo "💻 Running locally (sysbench must be installed)"
    sb_local_cmd=(sysbench \
        --mysql-host="$DB_HOST" \
        --mysql-user="$DB_USER" \
        --mysql-password="$DB_PASS" \
        --mysql-db="$DB_NAME" \
        --threads="$THREADS" \
        --time="$TIME" \
        --events=0)

    if [[ -n "$SQL_DIR" ]]; then
        sb_local_cmd+=(--sql-dir="$SQL_DIR" "$LUA_SCRIPT")
    else
        sb_local_cmd+=("$SCRIPT_PATH")
    fi

    "${sb_local_cmd[@]}" run
fi
