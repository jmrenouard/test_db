#!/bin/bash
set -euo pipefail

# Configuration
CONTAINER_NAME="${1:-mariadb-11-8}"
DB_USER="${2:-root}"
DB_PASS="${3:-root}"
DB_NAME="${4:-employees}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Verifying data integrity for database: ${DB_NAME} in container: ${CONTAINER_NAME}${NC}"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}❌ Error: Container ${CONTAINER_NAME} is not running.${NC}"
    exit 1
fi

MYSQL_CMD="docker exec -i ${CONTAINER_NAME} mariadb -u ${DB_USER} -p${DB_PASS} -BN"

EXPECTED=(
    "departments:9:3407387832"
    "dept_emp:331603:3190576018"
    "dept_manager:24:3048905531"
    "employees:300024:610052939"
    "salaries:2844047:4273816835"
    "titles:443308:1842528371"
)

function get_expected {
    local table="$1"
    local field="$2"
    for E in "${EXPECTED[@]}"; do
        t=$(echo "$E" | cut -d':' -f1)
        count=$(echo "$E" | cut -d':' -f2)
        crc=$(echo "$E" | cut -d':' -f3)
        if [ "$t" == "$table" ]; then
            if [ "$field" == "count" ]; then
                echo "$count"
            else
                echo "$crc"
            fi 
            return
        fi
    done
}

printf "%-25s %-10s     %-15s %-10s\n" "Table" "Count" "Checksum" "Status"
echo '------------------------- ----------     --------------- ----------'

TOTAL_ERRORS=0

# Only check BASE TABLES, skip views
# We use -r to avoid issues with backslashes if any
TABLES=$($MYSQL_CMD -e "show full tables from ${DB_NAME} where table_type = 'BASE TABLE'" | cut -f1)

for T in $TABLES; do 
    # Use -BN to avoid borders, but be aware it might still include the table name
    CRC_TEXT=$($MYSQL_CMD -e "checksum table $T" "${DB_NAME}")
    COUNT=$($MYSQL_CMD -e "select count(*) from $T" "${DB_NAME}")
    
    # Checksum output with -BN is usually "dbname.tablename CRC"
    # We take the last field to get the CRC
    CRC=$(echo "$CRC_TEXT" | awk '{print $NF}')
    
    # Handle NULL or empty values
    if [ "$CRC" == "NULL" ] || [ -z "$CRC" ]; then
        CRC=0
    fi
    if [ -z "$COUNT" ]; then
        COUNT=0
    fi
    
    expected_crc=$(get_expected "$T" crc)
    expected_count=$(get_expected "$T" count)
    
    if [ -z "$expected_crc" ]; then
        STATUS="${YELLOW}UNKNOWN${NC}"
    elif [ "$expected_count" -eq "$COUNT" ] && [ "$expected_crc" == "$CRC" ]; then
        STATUS="${GREEN}OK${NC}"
    else
        STATUS="${RED}ERROR${NC}"
        ((TOTAL_ERRORS++))
    fi
    
    printf "%-25s %'10d     %'15s %b\n" "$T" "$COUNT" "$CRC" "$STATUS"
done


echo '----------------------------------------------------------'
if [ "$TOTAL_ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ Data integrity verification passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Data integrity verification failed with $TOTAL_ERRORS errors.${NC}"
    exit 1
fi
