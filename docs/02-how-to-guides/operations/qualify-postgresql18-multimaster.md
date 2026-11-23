# Qualify PostgreSQL 18 Multi-Master

Refer to
[CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
and
[Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
before you execute active-active probes.

## Prerequisites

1. Install Docker Engine and Docker Compose v2 on the test workstation.
2. Confirm that localhost ports `15441` and `15442` are free on `127.0.0.1`.
3. Stop other Sirene containers on low-memory hosts.

## Safety Instructions

**CAUTION:** Run `make sirene-mm-probe` only against dedicated qualification containers or isolated test clusters.
The probe suite creates publications, subscriptions, and temporary test rows with `998%` SIREN prefixes.

**CAUTION:** Do not deploy native PostgreSQL 18 `origin=none` bidirectional replication for active-active Sirene writes.
Probe `P3_CONCURRENT_SIRET_UPSERT` detects silent split-brain divergence on concurrent updates.

## Procedure

1. Start the two-node PostgreSQL 18 logical replication lab on ports `15441` and `15442`:

   ```bash
   make sirene-mm-up
   ```

2. Run the native bidirectional qualification probe across probes `P1` through `P5`:

   ```bash
   make sirene-mm-probe
   ```

3. Review the Markdown scorecard on standard output for each probe status (`PASS`, `WARN`, or `FAIL`).

4. To evaluate an external multi-master candidate, run `mm_probe.py` with explicit DSN arguments:

   ```bash
   python3 sirene/mm_probe.py \
     --dsn-a "$MM_DSN_A" \
     --dsn-b "$MM_DSN_B" \
     --candidate-name custom-mm \
     --output-md /tmp/mm-scorecard.md \
     --output-json /tmp/mm-scorecard.json
   ```

5. Check the final verdict field against deployment acceptance criteria:
   - `PRODUCTION_MULTI_MASTER_READY`: All five probes pass with `PASS`.
   - `CONDITIONAL_PARTITIONED_WRITES_ONLY`: Zero failures exist, with one or more `WARN` results.
   - `INCOMPATIBLE_WITH_SIRENE_3NF`: One or more probes report `FAIL`.

6. Tear down both multi-master containers and persistent volumes after evaluation:

   ```bash
   make sirene-mm-down
   ```

**NOTE:** `mm_probe.py` runs `P3_CONCURRENT_SIRET_UPSERT` last in the probe sequence.
Replication conflict stalls on `P3` cannot block `P4` or `P5`.

## Verification

1. Confirm that the scorecard lists all five probes (`P1` through `P5`) with numeric latencies.
2. If you wrote output files, confirm `/tmp/mm-scorecard.json` contains a non-empty `verdict` string.
3. Confirm zero remaining containers via `docker compose -f sirene/docker-compose.pg18-birep.yml ps`.

## Rollback

If a multi-master test stalls or corrupts replication slots, do these steps:

1. Stop the two-node lab and delete both volumes immediately:

   ```bash
   make sirene-mm-down
   ```

2. For external clusters, drop test publications and subscriptions created during the probe run.
3. Delete any leftover test rows where `siren LIKE '998%'` or `cle_deduplication LIKE 'mm_probe_%'`.
4. Revert production write routing to a single primary PostgreSQL 18 instance.

## Related Documentation

- Reference: [CLI Scripts and SQL Catalog](../../03-reference/cli-and-scripts/cli-scripts-and-sql-catalog.md)
- Reference: [Error and Alert Matrix](../../03-reference/troubleshooting-codes/error-and-alert-matrix.md)
- Explanation:
  [ADR-001: PostgreSQL 18 3NF Sirene ETL and MM Qualification](../../04-explanation/design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md)
- Explanation:
  [Concurrency, Lock Mechanics, and Replication Trade-offs](../../04-explanation/deep-dives/concurrency-locking-and-replication-tradeoffs.md)
