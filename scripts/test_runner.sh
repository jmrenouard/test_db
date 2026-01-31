#!/bin/bash
# scripts/test_runner.sh
# ============================================================================
# Main Test Orchestrator
# ============================================================================
# Purpose:
#   Provides a unified entry point for all database lab operations:
#   integrity verification, performance analysis, and stress testing.
#
# Commands:
#   - verify: Data checksums and counts.
#   - analyze: Query plans and optimization suggestions.
#   - bench: Single-threaded sysbench run.
#   - perf-threads: Multi-threaded scaling analysis.
#   - data-tests: Recursive testing of subdirectories in tests/data/.
# ============================================================================

set -euo pipefail

# Configuration (Environment Variable Overrides)
CONTAINER_NAME="${CONTAINER_NAME:-mariadb-11-8}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-employees}"
DB_HOST="${DB_HOST:-127.0.0.1}"
SCRIPTS_DIR="$(dirname "$0")"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Execution Mode Selection
USE_CONTAINER=false
if [ -n "$CONTAINER_NAME" ] && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    USE_CONTAINER=true
    echo -e "${GREEN}ℹ️ Using Docker container: $CONTAINER_NAME${NC}"
else
    echo -e "${YELLOW}⚠️ Container '$CONTAINER_NAME' not found or stopped. Falling back to local execution.${NC}"
fi

function show_help {
    echo "Usage: [VAR=value] $0 [command]"
    echo ""
    echo "Environment Variables (Overrides):"
    echo "  CONTAINER_NAME Default: mariadb-11-8"
    echo "  DB_USER       Default: root"
    echo "  DB_PASS       Default: \"\""
    echo "  DB_NAME       Default: employees"
    echo "  DB_HOST       Default: 127.0.0.1"
    echo ""
    echo "Commands:"
    echo "  verify    Verify data integrity (count and checksum)"
    echo "  analyze   Run performance analysis and EXPLAIN reports"
    echo "  bench     Run sysbench performance test"
    echo "  perf-threads Run sysbench scaling test (1 to 64 threads)"
    echo "  std-oltp [type] [action]  Run standard OLTP tests"
    echo "            Types: read_only, read_write, update_index,"
    echo "                   update_non_index, write_only"
    echo "            Actions: prepare, run, cleanup"
    echo "  data-tests   Run tests from tests/data subdirectories"
    echo "  all          Run all tests"
    echo "  help         Show this help message"
}

function run_std_oltp {
    local type="${1:-}"
    local action="${2:-run}"
    
    if [ -z "$type" ]; then
        echo -e "${RED}❌ Error: OLTP type required (read_only, read_write, etc.)${NC}"
        return 1
    fi

    local script_path="/usr/share/sysbench/oltp_${type}.lua"
    echo -e "${BLUE}=== Standard OLTP Test: $type ($action) ===${NC}"

    local sb_cmd=(sysbench \
        --mysql-host="$DB_HOST" \
        --mysql-user="$DB_USER" \
        --mysql-password="$DB_PASS" \
        --mysql-db="$DB_NAME" \
        "$script_path" "$action")

    if [ "$USE_CONTAINER" = true ]; then
        # When in container, we assume the path exists there too
        echo -e "${YELLOW}⚡ Executing in container: $CONTAINER_NAME${NC}"
        docker exec -i "$CONTAINER_NAME" "${sb_cmd[@]}"
    else
        echo -e "${YELLOW}⚡ Executing locally...${NC}"
        "${sb_cmd[@]}"
    fi
}

function run_verify {
    echo -e "${BLUE}=== Data Integrity Verification ===${NC}"
    # Pass container name as empty if not using container to trigger local detection in sub-scripts if needed
    local target_container="$CONTAINER_NAME"
    if [ "$USE_CONTAINER" = false ]; then target_container=""; fi
    
    bash "$SCRIPTS_DIR/verify_data.sh" "$target_container" "$DB_USER" "$DB_PASS" "$DB_NAME"
    return $?
}

function run_analyze {
    echo -e "${BLUE}=== SQL Performance Analysis ===${NC}"
    local cmd=(python3 "$SCRIPTS_DIR/sql_analyzer.py" \
        --user "$DB_USER" \
        --password "$DB_PASS" \
        --db "$DB_NAME" \
        --query-file "employees/req_employees.sql")
    
    if [ "$USE_CONTAINER" = true ]; then
        cmd+=(--container "$CONTAINER_NAME")
    else
        cmd+=(--host "$DB_HOST")
    fi

    "${cmd[@]}"
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
        if [ "$USE_CONTAINER" = true ]; then
            echo -e "${YELLOW}📦 Copying scripts and queries to container...${NC}"
            docker cp "$SCRIPTS_DIR/employees_sysbench.lua" "$CONTAINER_NAME:/tmp/employees_sysbench.lua"
            docker cp "$query_file" "$CONTAINER_NAME:/tmp/req_employees.sql"
            
            echo -e "${YELLOW}⚡ Running $query_count queries 10 times ($total_events events total) in container...${NC}"
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
            echo -e "${YELLOW}⚡ Running $query_count queries 10 times ($total_events events total) locally...${NC}"
            sysbench \
                --mysql-host="$DB_HOST" \
                --mysql-user="$DB_USER" \
                --mysql-password="$DB_PASS" \
                --mysql-db="$DB_NAME" \
                --threads=1 \
                --events="$total_events" \
                --time=0 \
                --report-interval=1 \
                "$SCRIPTS_DIR/employees_sysbench.lua" run
        fi
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

    if [ "$USE_CONTAINER" = true ]; then
        docker cp "$SCRIPTS_DIR/employees_sysbench.lua" "$CONTAINER_NAME:/tmp/employees_sysbench.lua"
        docker cp "$query_file" "$CONTAINER_NAME:/tmp/req_employees.sql"
    fi

    for t in 1 2 4 8 16 32 64; do
        echo -e "${YELLOW}⚡ Testing with $t threads...${NC}"
        if [ "$USE_CONTAINER" = true ]; then
            docker exec -i "$CONTAINER_NAME" sysbench \
                --mysql-host=127.0.0.1 \
                --mysql-user="$DB_USER" \
                --mysql-password="$DB_PASS" \
                --mysql-db="$DB_NAME" \
                --threads="$t" \
                --events=0 \
                --time=60 \
                /tmp/employees_sysbench.lua run > "reports/perf_threads/results_${t}_threads.txt"
        else
            sysbench \
                --mysql-host="$DB_HOST" \
                --mysql-user="$DB_USER" \
                --mysql-password="$DB_PASS" \
                --mysql-db="$DB_NAME" \
                --threads="$t" \
                --events=0 \
                --time=60 \
                "$SCRIPTS_DIR/employees_sysbench.lua" run > "reports/perf_threads/results_${t}_threads.txt"
        fi
        
        local tps=$(grep "queries:" "reports/perf_threads/results_${t}_threads.txt" | awk '{print $3}' | tr -d '(')
        local lat=$(grep "avg:" "reports/perf_threads/results_${t}_threads.txt" | head -n 1 | awk '{print $2}')
        echo -e "${GREEN}✅ Finished $t threads: $tps QPS, $lat ms avg latency${NC}"
    done

    echo -e "${YELLOW}📊 Generating reports...${NC}"
    python3 "$SCRIPTS_DIR/perf_threads_reporter.py" \
        --dir "reports/perf_threads" \
        --md "reports/perf_threads/scaling_report.md" \
        --html "reports/perf_threads/scaling_report.html"
    
    echo -e "${GREEN}✅ Scaling reports generated in reports/perf_threads/${NC}"
}
 
function run_data_tests {
    local target_test="${1:-}"
    echo -e "${BLUE}=== Subdirectory Data Tests ===${NC}"
    local data_dir="tests/data"
    
    if [ ! -d "$data_dir" ]; then
        echo -e "${RED}❌ Error: $data_dir not found.${NC}"
        return 1
    fi

    if [ -n "$target_test" ]; then
        if [ ! -d "$data_dir/$target_test" ]; then
            echo -e "${RED}❌ Error: Test directory $data_dir/$target_test not found.${NC}"
            return 1
        fi
        local test_paths=("$data_dir/$target_test")
    else
        local test_paths=("$data_dir"/*)
    fi

    for test_path in "${test_paths[@]}"; do
        if [ -d "$test_path" ]; then
            local test_name=$(basename "$test_path")
            echo -e "${YELLOW}📂 Running test: $test_name...${NC}"
            
            local cmd=(python3 scripts/db_simulator.py \
                --sql-dir "$test_path" \
                --name "$test_name" \
                --output-dir "reports/$test_name" \
                --threads 4 \
                --time 10 \
                --user "$DB_USER" \
                --password "$DB_PASS" \
                --db "$DB_NAME")
            
            if [ "$USE_CONTAINER" = true ]; then
                cmd+=(--container "$CONTAINER_NAME" --host "127.0.0.1")
            else
                cmd+=(--host "$DB_HOST")
            fi

            "${cmd[@]}"
                
            echo -e "${GREEN}✅ Finished $test_name. Reports in reports/$test_name/${NC}"
            
            echo -e "${YELLOW}⏳ Waiting 5 seconds before next test (log isolation)...${NC}"
            sleep 5
        fi
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
    std-oltp)
        run_std_oltp "${2:-}" "${3:-run}"
        ;;
    data-tests)
        run_data_tests "${2:-}"
        ;;
    all)
        run_verify
        run_analyze
        run_bench
        run_perf_threads
        run_data_tests
        ;;
    help|*)
        show_help
        ;;
esac
