#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# tests/test_inject_fake.sh
# Automated Test Suite for Synthetic Employee Data Injection
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Running Synthetic Data Injection Unit Tests..."

# Test 1: Dry-run SQL generation
echo "  [1/3] Testing --dry-run SQL generation..."
DRY_OUTPUT=$(python3 scripts/inject_fake_employees.py --count 5 --dry-run --seed 42)
if ! echo "$DRY_OUTPUT" | grep -q "INSERT INTO employees"; then
    echo "❌ Test 1 failed: 'INSERT INTO employees' not found in dry-run output."
    exit 1
fi
echo "  ✅ Test 1 passed."

# Test 2: Output SQL file creation
echo "  [2/3] Testing --output-sql file creation..."
TMP_SQL=$(mktemp /tmp/fake_test_XXXXXX.sql)
python3 scripts/inject_fake_employees.py --count 10 --output-sql "$TMP_SQL" --seed 42 > /dev/null
if [ ! -s "$TMP_SQL" ]; then
    echo "❌ Test 2 failed: Output SQL file is empty."
    rm -f "$TMP_SQL"
    exit 1
fi
LINE_COUNT=$(grep -c "INSERT INTO" "$TMP_SQL" || true)
if [ "$LINE_COUNT" -ne 4 ]; then
    echo "❌ Test 2 failed: Expected 4 INSERT statements, got $LINE_COUNT."
    rm -f "$TMP_SQL"
    exit 1
fi
rm -f "$TMP_SQL"
echo "  ✅ Test 2 passed."

# Test 3: Deterministic Seed Output
echo "  [3/3] Testing --seed reproducibility..."
OUT1=$(python3 scripts/inject_fake_employees.py --count 3 --dry-run --seed 123)
OUT2=$(python3 scripts/inject_fake_employees.py --count 3 --dry-run --seed 123)
if [ "$OUT1" != "$OUT2" ]; then
    echo "❌ Test 3 failed: Seed outputs do not match."
    exit 1
fi
echo "  ✅ Test 3 passed."

echo "🎉 All synthetic data injection tests passed successfully!"
