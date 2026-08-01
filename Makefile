# Makefile for managing MariaDB container for test_db

CONTAINER_NAME = mariadb-11-8

-include .env

.PHONY: help start stop status inject inject-fake verify bench perf-threads analyze test-all clean

COUNT ?= 10

help:
	@echo "🛠️ test_db Management"
	@echo ""
	@echo "Core Commands:"
	@echo "  make start      - Start MariaDB container"
	@echo "  make stop       - Stop MariaDB container"
	@echo "  make status     - Show container status"
	@echo "  make inject     - Inject employees dataset"
	@echo "  make inject-fake - Inject synthetic employees using Faker (default COUNT=10)"
	@echo ""

	@echo "Test Commands:"
	@echo "  make verify     - Verify data integrity (counts/checksums)"
	@echo "  make bench      - Run sysbench performance tests"
	@echo "  make perf-threads - Run sysbench scaling test (1 to 64 threads)"
	@echo "  make analyze    - Run SQL explain and performance analysis"
	@echo "  make oltp TYPE=.. ACTION=.. - Run standard OLTP tests"
	@echo "                    (Types: read_only, read_write, update_index, ...)"
	@echo "                    (Actions: prepare, run, cleanup)"
	@echo "  make test-data  - Run all tests from tests/data/ subdirectories"
	@echo "  make test-all   - Run all tests sequentially"
	@echo "  make interactive - Run tests interactively with HTML report"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Remove generated reports"

start:
	@echo "🚀 Starting MariaDB container ($(CONTAINER_NAME))..."
	@docker start $(CONTAINER_NAME)

stop:
	@echo "🛑 Stopping MariaDB container ($(CONTAINER_NAME))..."
	@docker stop $(CONTAINER_NAME)

status:
	@echo "📊 Status of MariaDB container ($(CONTAINER_NAME)):"
	@docker ps -f name=$(CONTAINER_NAME)

inject:
	@echo "💉 Injecting employees.sql into $(CONTAINER_NAME)..."
	@docker exec -i $(CONTAINER_NAME) mkdir -p /tmp/employees_data
	@docker cp employees/. $(CONTAINER_NAME):/tmp/employees_data/
	@docker exec -i $(CONTAINER_NAME) bash -c "cd /tmp/employees_data && mariadb -u root < employees.sql"

inject-fake:
	@echo "🎲 Generating and injecting $(COUNT) synthetic employees..."
	@python3 scripts/inject_fake_employees.py --count $(COUNT) --container $(CONTAINER_NAME)

verify:
	@bash scripts/test_runner.sh verify

bench:
	@bash scripts/test_runner.sh bench

perf-threads:
	@bash scripts/test_runner.sh perf-threads

analyze:
	@bash scripts/test_runner.sh analyze

oltp:
	@THREADS=$(THREADS) TABLES=$(TABLES) SIZE=$(SIZE) TIME=$(TIME) bash scripts/test_runner.sh std-oltp $(TYPE) $(ACTION)

test-data:
	@bash scripts/test_runner.sh data-tests $(TEST)

test-all:
	@bash scripts/test_runner.sh all

interactive:
	@python3 interactive_runner.py

clean:
	@echo "🧹 Cleaning up reports..."
	@rm -rf reports/performance_report.md reports/explain_reports/*.txt reports/perf_threads/*.txt reports/perf_threads/*.html reports/perf_threads/*.md reports/deadlock reports/gap_locking reports/transactions reports/infrastructure.json
