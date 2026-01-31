# Feature: Database Health Check Script

## Context
The current `make status` command only lists the running Docker containers. It does not verify if the MariaDB service is actually ready to accept connections or if the `employees` database has been successfully initialized. This can lead to false positives where tests fail because the database wasn't ready.

## Objective
Create a robust `health_check.sh` script and integrate it into the `Makefile` as `make health`. This script should perform deep checks on the database status.

## Execution Prompt
You are a Site Reliability Engineer. Your task is to implement a health check mechanism for the database container.

### Instructions:

1.  **Create Script**:
    - Create `scripts/health_check.sh`.
    - Make it executable (`chmod +x`).

2.  **Script Logic**:
    - **Check 1 (Container)**: Verify the Docker container is running.
    - **Check 2 (Port)**: Verify that the MariaDB port (3306) inside the container is listening (or accessible).
    - **Check 3 (Connection)**: Attempt to connect to MariaDB using the `mysql` (or `mariadb`) client command inside the container.
    - **Check 4 (Data)**: verify that the `employees` database exists.

3.  **Integration**:
    - Update `Makefile` to add a `health` target that runs this script.
    - Update `Makefile`'s `start` or `inject` targets to optionally use this health check (or at least suggest it in the help).

4.  **Requirements**:
    - Use pure Bash (no external dependencies like `python` or `node` for this script if possible, or use the tools already present in the container).
    - Provide clear, colored output (Green for OK, Red for Fail).
    - **Rules**: Strictly follow the rules in `.agent/rules/*.md`.
    - **Memory Update**: Update the project memory/changelog.

5.  **Output**:
    - The content of `scripts/health_check.sh`.
    - The modified `Makefile`.
    - Updated `Changelog`.
