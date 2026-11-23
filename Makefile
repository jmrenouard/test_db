# Makefile for managing MariaDB container for test_db

CONTAINER_NAME = mariadb-11-8

-include .env

.PHONY: help start stop status inject inject-fake verify bench perf-threads analyze test-all clean sirene-up sirene-down sirene-test sirene-import sirene-incremental sirene-watch sirene-docs sirene-mm-up sirene-mm-probe sirene-mm-down sirene-inject sirene-verify sirene-import-sample sirene-incremental-sample docs-check docs-build docs-build-versioned docs-serve

COUNT ?= 10
PYTHON ?= python3

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
	@echo ""
	@echo "Sirene PostgreSQL 18 3NF ETL Commands:"
	@echo "  make sirene-up          - Start PostgreSQL 18 container for Sirene"
	@echo "  make sirene-down        - Stop Sirene Docker Compose stack"
	@echo "  make sirene-test        - Build and run full Sirene pytest suite in Docker"
	@echo "  make sirene-import      - Run initial full Sirene bulk import"
	@echo "  make sirene-incremental - Run incremental Sirene delta synchronization"
	@echo "  make sirene-watch       - Start autonomous Sirene data.gouv.fr watcher daemon"
	@echo "  make sirene-docs        - Show Sirene interactive HTML and EN/FR documentation paths"
	@echo "  make sirene-mm-up       - Start 2-node PostgreSQL 18 bidirectional replication lab"
	@echo "  make sirene-mm-probe    - Run multi-master qualification probe against the 2-node PG 18 lab"
	@echo "  make sirene-mm-down     - Stop and remove 2-node PG 18 multi-master lab containers and volumes"
	@echo "  make sirene-inject      - Inject synthetic 15k UL / 30k SIRET SQL dumps directly via psql"
	@echo "  make sirene-verify      - Verify injected Sirene row counts and SHA-256 checksums"
	@echo "  make sirene-import-sample      - Run full_import.py on embedded offline synthetic Parquet files"
	@echo "  make sirene-incremental-sample - Run incremental_import.py on embedded synthetic delta Parquet files"
	@echo ""
	@echo "Documentation (MkDocs Material):"
	@echo "  make docs-check           - Run Diataxis and MkDocs publishing pytest suites"
	@echo "  make docs-build           - Build strict MkDocs Material site in site/"
	@echo "  make docs-build-versioned - Build multi-version IONOS site bundle in site_dist/"
	@echo "  make docs-serve           - Serve MkDocs Material documentation locally"

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

sirene-up:
	@echo "🐘 Starting Sirene PostgreSQL 18 container..."
	@docker compose -f sirene/docker-compose.yml up -d sirene-postgres

sirene-down:
	@echo "🛑 Stopping Sirene Docker Compose stack..."
	@docker compose -f sirene/docker-compose.yml --profile daemon down

sirene-test:
	@echo "🧪 Building and running Sirene ETL test suite in Docker..."
	@docker compose -f sirene/docker-compose.yml up -d --wait sirene-postgres
	@docker compose -f sirene/docker-compose.yml build sirene-etl
	@docker compose -f sirene/docker-compose.yml run --rm sirene-etl pytest -v

sirene-import:
	@echo "📥 Running Sirene initial bulk import..."
	@docker compose -f sirene/docker-compose.yml run --rm sirene-etl python full_import.py $(ARGS)

sirene-incremental:
	@echo "🔄 Running Sirene incremental synchronization..."
	@docker compose -f sirene/docker-compose.yml run --rm sirene-etl python incremental_import.py $(ARGS)

sirene-watch:
	@echo "👁️ Starting Sirene data.gouv.fr watcher daemon..."
	@docker compose -f sirene/docker-compose.yml --profile daemon up -d sirene-watcher

sirene-docs:
	@echo "📚 Sirene PostgreSQL 18 3NF ETL Documentation:"
	@echo "  - Interactive HTML Reference : documentation/sirene_documentation.html"
	@echo "  - Technical Guide (EN)       : documentation/en/sirene_platform.md"
	@echo "  - Technical Guide (FR)       : documentation/fr/sirene_platform.md"
	@echo "  - Module Quickstart          : sirene/README.md"

sirene-mm-up:
	@echo "🐘 Starting 2-node PostgreSQL 18 bidirectional replication lab..."
	@docker compose -f sirene/docker-compose.pg18-birep.yml up -d --wait sirene-mm-node-a sirene-mm-node-b

sirene-mm-probe:
	@echo "🔬 Building and running Sirene multi-master qualification probe..."
	@docker compose -f sirene/docker-compose.pg18-birep.yml up -d --wait sirene-mm-node-a sirene-mm-node-b
	@docker compose -f sirene/docker-compose.pg18-birep.yml build sirene-mm-probe
	@docker compose -f sirene/docker-compose.pg18-birep.yml run --rm sirene-mm-probe sh -c 'python mm_probe.py --dsn-a "$$MM_DSN_A" --dsn-b "$$MM_DSN_B" --setup-native-birep --candidate-name pg18-native-birep $(ARGS)'

sirene-mm-down:
	@echo "🛑 Stopping 2-node PostgreSQL 18 multi-master lab..."
	@docker compose -f sirene/docker-compose.pg18-birep.yml down -v

sirene-inject:
	@echo "💉 Injecting synthetic Sirene SQL dumps into sirene-postgres..."
	@docker compose -f sirene/docker-compose.yml exec -T -w /sirene sirene-postgres psql -U $${POSTGRES_USER:-sirene} -d $${POSTGRES_DB:-sirene} -v ON_ERROR_STOP=1 -f load_sirene.sql

sirene-verify:
	@echo "🔍 Verifying Sirene row counts and SHA-256 checksums..."
	@docker compose -f sirene/docker-compose.yml exec -T -w /sirene sirene-postgres psql -U $${POSTGRES_USER:-sirene} -d $${POSTGRES_DB:-sirene} -v ON_ERROR_STOP=1 -f test_sirene_sha2.sql

sirene-import-sample:
	@echo "📥 Running full_import.py against embedded offline synthetic Parquet files..."
	@docker compose -f sirene/docker-compose.yml run --rm sirene-etl python full_import.py --ul-file /app/data/parquet/StockUniteLegale_synthetic.parquet --etab-file /app/data/parquet/StockEtablissement_synthetic.parquet --offline-refs --force

sirene-incremental-sample:
	@echo "🔄 Running incremental_import.py against embedded synthetic delta Parquet files..."
	@docker compose -f sirene/docker-compose.yml run --rm sirene-etl python incremental_import.py --ul-file /app/data/delta/DeltaUniteLegale_synthetic.parquet --etab-file /app/data/delta/DeltaEtablissement_synthetic.parquet --force

docs-check:
	@echo "📚 Running Diataxis, tutorial, and MkDocs publishing checks..."
	@$(PYTHON) -m pytest tests/test_diataxis_documentation.py tests/test_mkdocs_publishing.py tests/test_tutorials_and_howtos.py -v

docs-build:
	@echo "🏗️ Building strict EN and FR MkDocs Material sites in site/ and site/fr/..."
	@$(PYTHON) -m mkdocs build --strict -d site
	@$(PYTHON) -m mkdocs build -f mkdocs.fr.yml --strict -d site/fr

docs-build-versioned:
	@echo "📦 Building multi-version IONOS site bundle in site_dist/..."
	@$(PYTHON) scripts/build_versioned_docs.py --output site_dist --base-url https://test-db.lightpath.fr --main-ref WORKTREE

docs-serve:
	@echo "🌐 Serving MkDocs Material documentation locally (English)..."
	@$(PYTHON) -m mkdocs serve

docs-serve-fr:
	@echo "🌐 Serving MkDocs Material documentation locally (French)..."
	@$(PYTHON) -m mkdocs serve -f mkdocs.fr.yml -a 127.0.0.1:8001
