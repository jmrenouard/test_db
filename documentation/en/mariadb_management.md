# MariaDB 11.8 Management

This project uses MariaDB 11.8 in a Dockerized environment to ensure reproducibility and performance consistency.

## Lifecycle Commands

The `Makefile` simplifies the management of the MariaDB container:

- **Start**: `make start` - Boots up the `mariadb-11-8` container.
- **Stop**: `make stop` - Safely shuts down the container.
- **Status**: `make status` - Checks if the container is running and healthy.

## Environment Details

- **DBMS**: MariaDB 11.8
- **Default Container Name**: `mariadb-11-8`
- **Default Port**: `3306`
- **Default Credentials**: Root password is set to `root` (intended for lab usage).

## Data Management

Queries and data are injected using the `make inject` target, which:

1. Creates a temporary directory in the container.
2. Copies the dataset (e.g., `employees`) to `/tmp`.
3. Executes the SQL initialization script via `mariadb` standard input.
