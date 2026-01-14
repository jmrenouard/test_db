# Makefile for managing MariaDB container for test_db

CONTAINER_NAME = mariadb-11-8

.PHONY: start stop status inject report sysbench

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
	@cd employees && docker exec -i $(CONTAINER_NAME) mariadb -u root -proot employees < employees.sql

report:
	@echo "📊 Running generate_reports.py..."
	@ln -sf employees/req_employees.sql .
	@python3 scripts/generate_reports.py
	@rm req_employees.sql

sysbench:
	@echo "⚡ Running sysbench test with employees_sysbench.lua..."
	@if [ -f scripts/employees_sysbench.lua ]; then \
		sysbench --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password=root --mysql-db=employees scripts/employees_sysbench.lua run; \
	else \
		echo "❌ Error: scripts/employees_sysbench.lua not found."; \
		exit 1; \
	fi
