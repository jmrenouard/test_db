# Deploy MariaDB and PostgreSQL Stacks

Refer to
[Environment Variables and Makefile Targets](../../03-reference/configuration/environment-variables-and-makefile-targets.md)
before you edit `.env` files or port bindings.

## Prerequisites

1. Install Docker Engine, Docker Compose v2, GNU `make`, and `bash` on the target host.
2. Confirm that container `mariadb-11-8` exists on your Docker host.
3. Confirm that TCP ports `3306` and `15432` are free on `127.0.0.1`.

## Safety Instructions

**CAUTION:** Copy `.env` files only to local hosts and exclude them from Git commits.
Committed environment files expose local passwords and connection strings.

**CAUTION:** Mount the PostgreSQL 18 data volume at `/var/lib/postgresql` rather than `/var/lib/postgresql/data`.
Legacy mount paths cause `postgres:18-bookworm` container startup failures.

## Procedure

1. Copy the template environment file for the Sirene PostgreSQL 18 stack:

   ```bash
   cp sirene/.env.example sirene/.env
   ```

2. Edit `sirene/.env` if you must customize `POSTGRES_PASSWORD`, `POSTGRES_HOST_PORT`, or `BATCH_SIZE`.

3. Start the MariaDB 11.8 container and check container health:

   ```bash
   make start
   make status
   ```

4. Inject the canonical `employees` dataset into `mariadb-11-8`:

   ```bash
   make inject
   ```

5. Start the Sirene PostgreSQL 18 service on `127.0.0.1:15432`:

   ```bash
   make sirene-up
   ```

6. Build the `sirene-etl` container image and run the Dockerized `pytest` suite:

   ```bash
   make sirene-test
   ```

7. Load the offline synthetic Sirene dataset directly via `psql`:

   ```bash
   make sirene-inject
   ```

8. If you require autonomous daemon updates, start the `sirene-watcher` service under profile `daemon`:

   ```bash
   make sirene-watch
   ```

**NOTE:** `sirene/docker-compose.yml` isolates `sirene-watcher` inside profile `daemon`.
Default `make sirene-up` runs never start background network polls.

## Verification

1. Confirm that both database containers show healthy status:

   ```bash
   make status
   docker compose -f sirene/docker-compose.yml ps
   ```

2. Run `make verify` and confirm exit code `0` for all six `employees` tables.
3. Run `make sirene-verify` and confirm `CRC | OK` and `count | OK` across all twelve Sirene tables.

## Rollback

If a container deployment fails or corrupts local test data, do these steps:

1. Stop the Sirene stack and remove anonymous container state:

   ```bash
   make sirene-down
   ```

2. If you must reset the `sirene_pgdata` volume completely, run `docker compose down -v`:

   ```bash
   docker compose -f sirene/docker-compose.yml --profile daemon down -v
   ```

3. Stop the MariaDB container:

   ```bash
   make stop
   ```

4. Run `make start` and `make inject` to restore a clean `employees` schema.

## Related Documentation

- Reference: [Environment Variables and Makefile Targets](../../03-reference/configuration/environment-variables-and-makefile-targets.md)
- Reference: [Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
- Explanation: [Platform and ETL Architecture](../../04-explanation/architecture-overview/platform-and-etl-architecture.md)
- Explanation:
  [ADR-001: PostgreSQL 18 3NF Sirene ETL and MM Qualification](../../04-explanation/design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md)
