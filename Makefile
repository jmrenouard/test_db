# Makefile for managing MariaDB container for test_db

CONTAINER_NAME = mariadb-11-8

.PHONY: help start stop status inject verify bench perf-threads analyze test-all clean

help:
	@echo "🛠️ test_db Management"
	@echo ""
	@echo "Core Commands:"
	@echo "  make start      - Start MariaDB container"
	@echo "  make stop       - Stop MariaDB container"
	@echo "  make status     - Show container status"
	@echo "  make inject     - Inject employees dataset"
	@echo ""
	@echo "Test Commands:"
	@echo "  make verify     - Verify data integrity (counts/checksums)"
	@echo "  make bench      - Run sysbench performance tests"
	@echo "  make perf-threads - Run sysbench scaling test (1 to 64 threads)"
	@echo "  make analyze    - Run SQL explain and performance analysis"
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
	@docker exec -i $(CONTAINER_NAME) bash -c "cd /tmp/employees_data && mariadb -u root -proot < employees.sql"

verify:
	@bash scripts/test_runner.sh verify

bench:
	@bash scripts/test_runner.sh bench

perf-threads:
	@bash scripts/test_runner.sh perf-threads

analyze:
	@bash scripts/test_runner.sh analyze

test-all:
	@bash scripts/test_runner.sh all

interactive:
	@python3 interactive_runner.py

clean:
	@echo "🧹 Cleaning up reports..."
	@rm -rf reports/performance_report.md reports/explain_reports/*.txt reports/perf_threads/*.txt
