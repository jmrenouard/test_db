#!/bin/bash
set -euo pipefail

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
    echo "  perf-threads Run sysbench scaling test (1 to 64 threads)"
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
    local query_file="employees/req_employees.sql"
    
    # Check for the requested file or its variant
    if [ ! -f "$query_file" ]; then
        query_file="employees/rerq_employees.sql"
    fi

    if [ ! -f "$query_file" ]; then
        echo -e "${RED}❌ Error: Query file (req_employees.sql or rerq_employees.sql) not found in employees/.${NC}"
        return 1
    fi

    # Count number of queries (semicolon count)
    local query_count=$(grep -c ";" "$query_file")
    local total_events=$((query_count * 10))

    if [ -f "$SCRIPTS_DIR/employees_sysbench.lua" ]; then
        echo -e "${YELLOW}📦 Copying scripts and queries to container...${NC}"
        docker cp "$SCRIPTS_DIR/employees_sysbench.lua" "$CONTAINER_NAME:/tmp/employees_sysbench.lua"
        docker cp "$query_file" "$CONTAINER_NAME:/tmp/req_employees.sql"
        
        echo -e "${YELLOW}⚡ Running $query_count queries 10 times ($total_events events total)...${NC}"
        docker exec -i "$CONTAINER_NAME" sysbench \
            --mysql-host=127.0.0.1 \
            --mysql-user="$DB_USER" \
            --mysql-password="$DB_PASS" \
            --mysql-db="$DB_NAME" \
            --threads=1 \
            --events="$total_events" \
            --time=0 \
            /tmp/employees_sysbench.lua run
    else
        echo -e "${RED}❌ Error: scripts/employees_sysbench.lua not found.${NC}"
        return 1
    fi
}

function run_perf_threads {
    echo -e "${BLUE}=== Threaded Performance Test (Scale) ===${NC}"
    mkdir -p reports/perf_threads
    
    local query_file="employees/req_employees.sql"
    if [ ! -f "$query_file" ]; then
        query_file="employees/rerq_employees.sql"
    fi

    if [ ! -f "$query_file" ]; then
        echo -e "${RED}❌ Error: Query file not found.${NC}"
        return 1
    fi

    local query_count=$(grep -c ";" "$query_file")
    local total_events=$((query_count * 10))

    docker cp "$SCRIPTS_DIR/employees_sysbench.lua" "$CONTAINER_NAME:/tmp/employees_sysbench.lua"
    docker cp "$query_file" "$CONTAINER_NAME:/tmp/req_employees.sql"

    for t in 1 2 4 8 16 32 64; do
        echo -e "${YELLOW}⚡ Testing with $t threads...${NC}"
        docker exec -i "$CONTAINER_NAME" sysbench \
            --mysql-host=127.0.0.1 \
            --mysql-user="$DB_USER" \
            --mysql-password="$DB_PASS" \
            --mysql-db="$DB_NAME" \
            --threads="$t" \
            --events=0 \
            --time=60 \
            /tmp/employees_sysbench.lua run > "reports/perf_threads/results_${t}_threads.txt"
        
        local tps=$(grep "queries:" "reports/perf_threads/results_${t}_threads.txt" | awk '{print $3}' | tr -d '(')
        local lat=$(grep "avg:" "reports/perf_threads/results_${t}_threads.txt" | head -n 1 | awk '{print $2}')
        echo -e "${GREEN}✅ Finished $t threads: $tps QPS, $lat ms avg latency${NC}"
    done
}


case "${1:-help}" in
    verify)
        run_verify
        ;;
    analyze)
        run_analyze
        ;;
    bench)
        run_bench
        ;;
    perf-threads)
        run_perf_threads
        ;;
    all)
        run_verify
        run_analyze
        run_bench
        run_perf_threads
        ;;
    help|*)
        show_help
        ;;
esac
