# Verify Checksums and Privacy Boundaries

Refer to
[Datasets and Schemas Matrix](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)
and
[Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
before you audit datasets or publication builds.

## Prerequisites

1. Confirm that `mariadb-11-8` or `sirene-postgres` is active with loaded test datasets.
2. Confirm Python 3 and `git` are available in the repository root.
3. Confirm access to `sirene/test_sirene_sha2.sql` and `test_employees_sha2.sql`.

## Safety Instructions

**WARNING:** Never ingest unmasked production INSEE or employee personal data into public lab repositories.
Real personal records violate privacy boundaries and expose personal identifiers.

**CAUTION:** Keep `.env`, `sirene/.env`, `*.kdbx`, `*.keyx`, `*.pid`, and `*.log` out of Git and MkDocs builds.
Private files in tracked trees expose credentials or runtime artifacts on public documentation portals.

## Procedure

1. Verify row counts and CRC32 checksums on the `employees` database:

   ```bash
   make verify
   ```

2. Run cross-engine `SHA2(..., 256)` verification on MariaDB or MySQL:

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -t < test_employees_sha2.sql
   ```

3. For PostgreSQL `employees` databases, run the equivalent SHA-256 verification script:

   ```bash
   psql -d employees -v ON_ERROR_STOP=1 -f postgresql/test_employees_sha2.sql
   ```

4. Verify row counts and SHA-256 checksums across all twelve Sirene PostgreSQL 18 tables:

   ```bash
   make sirene-verify
   ```

5. Run the Sirene synthetic dataset and documentation governance tests inside Docker:

   ```bash
   make sirene-test
   ```

6. Scan Markdown files under `docs/` and `documentation/` to verify zero local workstation paths exist:

   ```bash
   git grep -nE '(/Users/|/home/|[A-Za-z]:[/\\]Users[/\\])' docs/ documentation/ || true
   ```

7. Inspect `.gitignore`, `mkdocs.yml` `exclude_docs`, and `git status` before every documentation build.

**NOTE:** Embedded synthetic Sirene records use `9xxxxxxxx` SIREN identifiers generated with `seed = 20261120`.
All names and addresses in `sirene/data/` are zero-PII fabricated strings.

## Verification

1. Confirm `make verify` exits with code `0` and prints `Data integrity verification passed`.
2. Confirm `make sirene-verify` prints `CRC | OK` and `count | OK` with zero exceptions.
3. Confirm `git grep` returns zero local workstation path matches and `git status` shows zero `.env` files.

## Rollback

If a checksum mismatch or privacy leak occurs, do these steps:

1. Stop public documentation publication or container export immediately.
2. Drop or truncate affected tables, then reload baseline dumps via `make inject` or `make sirene-inject`.
3. Remove any tracked `.env` or secret file from Git index and rotate affected lab credentials.
4. Re-run `make verify`, `make sirene-verify`, and `make sirene-test` until all checks pass.

## Related Documentation

- Reference: [Datasets and Schemas Matrix](../../03-reference/architecture-specs/datasets-and-schemas-matrix.md)
- Reference: [Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
- Explanation:
  [ADR-002: Diataxis Versioned MkDocs Documentation](../../04-explanation/design-decisions/adr-002-diataxis-versioned-mkdocs-publishing.md)
- Explanation: [Platform and ETL Architecture](../../04-explanation/architecture-overview/platform-and-etl-architecture.md)
