#!/bin/bash

# Configuration
CONTAINER_NAME="mariadb-11-8"
DB_USER="root"
DB_PASS="root"
DB_NAME="employees"
SCRIPTS_DIR="$(dirname "$0")"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function show_help {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  verify    Verify data integrity (count and checksum)"
    echo "  analyze   Run performance analysis and EXPLAIN reports"
    echo "  bench     Run sysbench performance test"
    echo "  all       Run all tests"
    echo "  help      Show this help message"
}

function run_verify {
    echo -e "${BLUE}=== Data Integrity Verification ===${NC}"
    bash "$SCRIPTS_DIR/verify_data.sh" "$CONTAINER_NAME" "$DB_USER" "$DB_PASS" "$DB_NAME"
    return $?
}

function run_analyze {
    echo -e "${BLUE}=== SQL Performance Analysis ===${NC}"
    python3 "$SCRIPTS_DIR/generate_reports.py" \
        --container "$CONTAINER_NAME" \
        --user "$DB_USER" \
        --password "$DB_PASS" \
        --db "$DB_NAME" \
        --query-file "employees/req_employees.sql"
    return $?
}

function run_bench {
    echo -e "${BLUE}=== Sysbench Performance Test ===${NC}"
    if [ -f "$SCRIPTS_DIR/employees_sysbench.lua" ]; then
        echo -e "${YELLOW}📦 Copying script to container...${NC}"
        docker cp "$SCRIPTS_DIR/employees_sysbench.lua" "$CONTAINER_NAME:/tmp/employees_sysbench.lua"
        echo -e "${YELLOW}⚡ Running sysbench in container...${NC}"
        docker exec -i "$CONTAINER_NAME" sysbench \
            --mysql-host=127.0.0.1 \
            --mysql-user="$DB_USER" \
            --mysql-password="$DB_PASS" \
            --mysql-db="$DB_NAME" \
            /tmp/employees_sysbench.lua run
    else
        echo -e "${RED}❌ Error: scripts/employees_sysbench.lua not found.${NC}"
        return 1
    fi
}


case "$1" in
    verify)
        run_verify
        ;;
    analyze)
        run_analyze
        ;;
    bench)
        run_bench
        ;;
    all)
        run_verify && run_analyze && run_bench
        ;;
    help|*)
        show_help
        ;;
esac
