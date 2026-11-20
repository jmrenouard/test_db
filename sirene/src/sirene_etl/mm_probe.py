"""Multi-master PostgreSQL qualification probe suite for the Sirene 3NF workload."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import contextlib
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import threading
import time
from typing import TYPE_CHECKING, Any
import uuid

from sirene_etl.config import load_settings
from sirene_etl.db import apply_sql_file
from sirene_etl.logging_utils import get_logger

if TYPE_CHECKING:
    import psycopg

logger = get_logger(__name__)

_PROBE_ADVISORY_LOCK_ID = 84729199
_REPLICATED_TABLES: tuple[str, ...] = (
    "ref_regions",
    "ref_departements",
    "ref_communes",
    "ref_pays",
    "ref_naf",
    "ref_categories_juridiques",
    "ref_tranches_effectifs",
    "unites_legales",
    "etablissements",
    "etablissements_historique_etat",
    "personnes",
    "roles_entreprises",
)
_STAGGERED_SEQUENCES: tuple[tuple[str, str], ...] = (
    ("personnes_id_seq", "personnes"),
    ("roles_entreprises_id_seq", "roles_entreprises"),
    ("etablissements_historique_etat_id_seq", "etablissements_historique_etat"),
)
_VALID_PROBE_STATUSES = frozenset({"PASS", "WARN", "FAIL"})
_VERDICT_READY = "PRODUCTION_MULTI_MASTER_READY"
_VERDICT_CONDITIONAL = "CONDITIONAL_PARTITIONED_WRITES_ONLY"
_VERDICT_INCOMPATIBLE = "INCOMPATIBLE_WITH_SIRENE_3NF"


@dataclass(frozen=True)
class ProbeResult:
    """Outcome of a single multi-master qualification probe."""

    probe_id: str
    name: str
    status: str
    latency_ms: float
    detail: str
    metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in _VALID_PROBE_STATUSES:
            raise ValueError(
                f"Invalid probe status {self.status!r}; "
                f"expected one of {sorted(_VALID_PROBE_STATUSES)}."
            )


@dataclass(frozen=True)
class Scorecard:
    """Aggregated multi-master qualification scorecard across two candidate nodes."""

    candidate: str
    pg_version_a: str
    pg_version_b: str
    verdict: str
    probes: list[ProbeResult] = field(default_factory=list)


def classify_verdict(probes: Sequence[ProbeResult]) -> str:
    """Compute final deployment verdict from probe statuses."""
    if not probes or any(probe.status == "FAIL" for probe in probes):
        return _VERDICT_INCOMPATIBLE
    if any(probe.status == "WARN" for probe in probes):
        return _VERDICT_CONDITIONAL
    return _VERDICT_READY


def scorecard_to_dict(scorecard: Scorecard) -> dict[str, Any]:
    """Serialize a Scorecard dataclass to a JSON-compatible dictionary."""
    return asdict(scorecard)


def format_scorecard_markdown(scorecard: Scorecard) -> str:
    """Render a Scorecard as a concise GitHub-flavored Markdown report."""
    lines = [
        f"# Multi-Master Qualification Scorecard: `{scorecard.candidate}`",
        "",
        f"- **Verdict:** `{scorecard.verdict}`",
        f"- **Node A Version:** `{scorecard.pg_version_a}`",
        f"- **Node B Version:** `{scorecard.pg_version_b}`",
        "",
        "| Probe ID | Check | Status | Latency (ms) | Detail |",
        "| :--- | :--- | :--- | ---: | :--- |",
    ]
    for probe in scorecard.probes:
        detail_escaped = probe.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{probe.probe_id}` | {probe.name} | **{probe.status}** "
            f"| {probe.latency_ms:.2f} | {detail_escaped} |"
        )
    lines.append("")
    return "\n".join(lines)


def _connect(dsn: str, *, autocommit: bool = True) -> psycopg.Connection:
    """Open a psycopg v3 connection with explicit autocommit setting."""
    import psycopg

    return psycopg.connect(dsn, autocommit=autocommit)


def _ensure_schema_on_node(conn: psycopg.Connection, sql_dir: Path) -> None:
    """Apply 3NF DDL and indexes on a node when core tables are absent."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.unites_legales') IS NOT NULL")
        row = cur.fetchone()
    if row and row[0]:
        return
    apply_sql_file(conn, sql_dir / "01_schema_3nf.sql")
    apply_sql_file(conn, sql_dir / "02_indexes.sql")


def _next_staggered_start(max_id: int, parity: int) -> int:
    """Compute the next odd (parity=1) or even (parity=0) sequence start >= 10001."""
    base = 10001 if parity == 1 else 10002
    if max_id < base:
        return base
    nxt = max_id + 1
    return nxt if (nxt % 2 == parity) else nxt + 1


def _wait_for_subscriptions(
    conn_a: psycopg.Connection,
    conn_b: psycopg.Connection,
    timeout_sec: float = 20.0,
) -> None:
    """Poll pg_stat_subscription until both bidirectional apply workers are active."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        ready = True
        for conn, sub_name in ((conn_a, "sub_from_b"), (conn_b, "sub_from_a")):
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pid IS NOT NULL FROM pg_stat_subscription "
                    "WHERE subname = %s",
                    (sub_name,),
                )
                row = cur.fetchone()
                if not row or not row[0]:
                    ready = False
                    break
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM pg_subscription_rel sr
                    JOIN pg_subscription s ON s.oid = sr.srsubid
                    WHERE s.subname = %s AND sr.srsubstate <> 'r'
                    """,
                    (sub_name,),
                )
                pending = cur.fetchone()
                if pending and int(pending[0]) > 0:
                    ready = False
                    break
        if ready:
            return
        time.sleep(0.1)
    raise TimeoutError("Timed out waiting for bidirectional apply workers.")


def setup_native_birep(
    dsn_a: str,
    dsn_b: str,
    internal_dsn_a: str,
    internal_dsn_b: str,
    stagger_sequences: bool = True,
) -> None:
    """Configure idempotent native PG 18 bidirectional replication (origin=none)."""
    from psycopg import sql

    sql_dir = load_settings().sql_dir
    tables_sql = sql.SQL(", ").join(sql.Identifier(tbl) for tbl in _REPLICATED_TABLES)

    with (
        _connect(dsn_a, autocommit=True) as conn_a,
        _connect(dsn_b, autocommit=True) as conn_b,
    ):
        for node_idx, conn in enumerate((conn_a, conn_b)):
            _ensure_schema_on_node(conn, sql_dir)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_publication WHERE pubname = 'sirene_mm_pub'"
                )
                if cur.fetchone() is None:
                    cur.execute(
                        sql.SQL("CREATE PUBLICATION sirene_mm_pub FOR TABLE {}").format(
                            tables_sql
                        )
                    )
                if stagger_sequences:
                    parity = 1 if node_idx == 0 else 0
                    for seq_name, table_name in _STAGGERED_SEQUENCES:
                        cur.execute(
                            sql.SQL("SELECT COALESCE(MAX(id), 0) FROM {}").format(
                                sql.Identifier(table_name)
                            )
                        )
                        max_row = cur.fetchone()
                        max_id = int(max_row[0]) if max_row else 0
                        start_val = _next_staggered_start(max_id, parity)
                        cur.execute(
                            sql.SQL(
                                "ALTER SEQUENCE {} INCREMENT BY 2 RESTART WITH {}"
                            ).format(sql.Identifier(seq_name), sql.Literal(start_val))
                        )

        sub_specs = (
            (conn_a, "sub_from_b", internal_dsn_b),
            (conn_b, "sub_from_a", internal_dsn_a),
        )
        for conn, sub_name, peer_dsn in sub_specs:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_subscription WHERE subname = %s",
                    (sub_name,),
                )
                if cur.fetchone() is None:
                    cur.execute(
                        sql.SQL(
                            "CREATE SUBSCRIPTION {} CONNECTION {} "
                            "PUBLICATION sirene_mm_pub "
                            "WITH (copy_data = false, origin = none)"
                        ).format(sql.Identifier(sub_name), sql.Literal(peer_dsn))
                    )

        _wait_for_subscriptions(conn_a, conn_b)
        logger.info(
            "Configured native bidirectional replication between node A and node B.",
            extra={
                "event": "mm_native_birep_ready",
                "stagger_sequences": stagger_sequences,
            },
        )


def _check_single_node_ddl(conn: psycopg.Connection) -> dict[str, Any]:
    """Verify pg_trgm, GENERATED STORED columns, UNIQUE NULLS NOT DISTINCT, and COPY."""
    with conn.cursor() as cur:
        cur.execute("SELECT 'ACME TECHNOLOGIE' % 'ACME TECHNOLOGIES'")
        trgm_row = cur.fetchone()
        trgm_ok = bool(trgm_row and trgm_row[0])

        cur.execute(
            """
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND indexname IN (
                  'idx_ul_nom_trgm',
                  'idx_etab_enseigne_trgm',
                  'idx_personnes_nom_trgm'
              )
              AND indexdef ILIKE '%gin%'
            """
        )
        gin_count = int((cur.fetchone() or (0,))[0])

        cur.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND is_generated = 'ALWAYS'
              AND (table_name, column_name) IN (
                  ('unites_legales', 'nom_recherche'),
                  ('etablissements', 'adresse_complete'),
                  ('etablissements', 'enseigne_recherche'),
                  ('personnes', 'nom_complet_recherche')
              )
            """
        )
        generated_count = int((cur.fetchone() or (0,))[0])

        try:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_index i
                    WHERE i.indrelid = 'roles_entreprises'::regclass
                      AND i.indisunique
                      AND i.indnullsnotdistinct
                )
                """
            )
            nulls_nd_ok = bool((cur.fetchone() or (False,))[0])
        except Exception:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                      AND tablename = 'roles_entreprises'
                      AND indexdef ILIKE '%NULLS NOT DISTINCT%'
                )
                """
            )
            nulls_nd_ok = bool((cur.fetchone() or (False,))[0])

    copy_ok = False
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE tmp_p1_compat (siren VARCHAR(9)) ON COMMIT DROP"
        )
        with cur.copy("COPY tmp_p1_compat (siren) FROM STDIN") as copy:
            copy.write_row(("998000001",))
        cur.execute("SELECT COUNT(*) FROM tmp_p1_compat")
        copy_ok = (cur.fetchone() or (0,))[0] == 1

    return {
        "trgm_ok": trgm_ok,
        "gin_index_count": gin_count,
        "generated_columns": generated_count,
        "nulls_not_distinct_ok": nulls_nd_ok,
        "temp_copy_ok": copy_ok,
    }


def _probe_ddl_compat(
    conn_a: psycopg.Connection,
    conn_b: psycopg.Connection,
) -> ProbeResult:
    """P1: Verify 3NF DDL features, pg_trgm, COPY FROM STDIN, and lock scope."""
    t0 = time.perf_counter()
    try:
        checks_a = _check_single_node_ddl(conn_a)
        checks_b = _check_single_node_ddl(conn_b)

        with conn_a.cursor() as cur_a, conn_b.cursor() as cur_b:
            cur_a.execute(
                "SELECT pg_try_advisory_lock(%s)", (_PROBE_ADVISORY_LOCK_ID,)
            )
            a_locked = bool((cur_a.fetchone() or (False,))[0])
            cur_b.execute(
                "SELECT pg_try_advisory_lock(%s)", (_PROBE_ADVISORY_LOCK_ID,)
            )
            b_locked = bool((cur_b.fetchone() or (False,))[0])
            if a_locked:
                cur_a.execute(
                    "SELECT pg_advisory_unlock(%s)", (_PROBE_ADVISORY_LOCK_ID,)
                )
            if b_locked:
                cur_b.execute(
                    "SELECT pg_advisory_unlock(%s)", (_PROBE_ADVISORY_LOCK_ID,)
                )

        ddl_ok = all(
            c["trgm_ok"]
            and c["gin_index_count"] == 3
            and c["generated_columns"] == 4
            and c["nulls_not_distinct_ok"]
            and c["temp_copy_ok"]
            for c in (checks_a, checks_b)
        )
        advisory_node_local = a_locked and b_locked
        if not ddl_ok:
            status = "FAIL"
            detail = "One or more Sirene 3NF DDL/pg_trgm/COPY checks failed."
        elif advisory_node_local:
            status = "WARN"
            detail = (
                "All 3NF DDL, pg_trgm, and COPY checks passed; "
                "pg_try_advisory_lock is node-local and not cluster-wide."
            )
        else:
            status = "PASS"
            detail = "All 3NF DDL, pg_trgm, COPY, and cluster lock checks passed."

        return ProbeResult(
            probe_id="P1_DDL_COMPAT",
            name="Sirene 3NF DDL, pg_trgm, COPY & Advisory Lock Scope",
            status=status,
            latency_ms=(time.perf_counter() - t0) * 1000.0,
            detail=detail,
            metrics={
                "node_a": checks_a,
                "node_b": checks_b,
                "advisory_lock_node_local": advisory_node_local,
            },
        )
    except Exception as exc:
        return ProbeResult(
            probe_id="P1_DDL_COMPAT",
            name="Sirene 3NF DDL, pg_trgm, COPY & Advisory Lock Scope",
            status="FAIL",
            latency_ms=(time.perf_counter() - t0) * 1000.0,
            detail=f"DDL compatibility probe failed: {exc}",
            metrics={},
        )


def _probe_sequence_split_brain(
    dsn_a: str,
    dsn_b: str,
    run_tag: str,
    timeout_sec: float,
) -> ProbeResult:
    """P2: Verify simultaneous BIGSERIAL inserts across nodes do not collide."""
    t0 = time.perf_counter()
    key_a = f"mm_probe_p2_a_{run_tag}"
    key_b = f"mm_probe_p2_b_{run_tag}"
    results: dict[str, int | None] = {"a": None, "b": None}
    errors: dict[str, str] = {}
    barrier = threading.Barrier(2)

    def _insert_person(label: str, dsn: str, nom: str, dedup: str) -> None:
        try:
            with _connect(dsn, autocommit=True) as conn:
                barrier.wait(timeout=5.0)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO personnes (
                            type_personne, nom, prenoms, cle_deduplication
                        )
                        VALUES ('PHYSIQUE', %s, 'PROBE', %s)
                        RETURNING id
                        """,
                        (nom, dedup),
                    )
                    row = cur.fetchone()
                    results[label] = int(row[0]) if row else None
        except Exception as exc:
            errors[label] = str(exc)

    thread_a = threading.Thread(
        target=_insert_person, args=("a", dsn_a, "PROBE_P2_A", key_a)
    )
    thread_b = threading.Thread(
        target=_insert_person, args=("b", dsn_b, "PROBE_P2_B", key_b)
    )
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    try:
        if errors or results["a"] is None or results["b"] is None:
            return ProbeResult(
                probe_id="P2_SEQUENCE_SPLIT_BRAIN",
                name="Simultaneous BIGSERIAL Sequence Allocation",
                status="FAIL",
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"Insert failure during concurrent sequence test: {errors}",
                metrics={"id_a": results["a"], "id_b": results["b"]},
            )

        if results["a"] == results["b"]:
            return ProbeResult(
                probe_id="P2_SEQUENCE_SPLIT_BRAIN",
                name="Simultaneous BIGSERIAL Sequence Allocation",
                status="FAIL",
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"Sequence collision: both nodes allocated id={results['a']}.",
                metrics={
                    "id_a": results["a"],
                    "id_b": results["b"],
                    "converged": False,
                },
            )

        converged = False
        with (
            _connect(dsn_a, autocommit=True) as conn_a,
            _connect(dsn_b, autocommit=True) as conn_b,
        ):
            deadline = time.monotonic() + timeout_sec
            while time.monotonic() < deadline:
                with conn_a.cursor() as cur_a, conn_b.cursor() as cur_b:
                    cur_a.execute(
                        "SELECT cle_deduplication, id FROM personnes "
                        "WHERE cle_deduplication IN (%s, %s)",
                        (key_a, key_b),
                    )
                    rows_a = dict(cur_a.fetchall())
                    cur_b.execute(
                        "SELECT cle_deduplication, id FROM personnes "
                        "WHERE cle_deduplication IN (%s, %s)",
                        (key_a, key_b),
                    )
                    rows_b = dict(cur_b.fetchall())
                if len(rows_a) == 2 and rows_a == rows_b:
                    converged = True
                    break
                time.sleep(0.05)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        status = "PASS" if converged else "FAIL"
        detail = (
            f"Allocated distinct IDs ({results['a']}, {results['b']}) and converged."
            if converged
            else "Sequence inserts did not converge across both nodes before timeout."
        )
        return ProbeResult(
            probe_id="P2_SEQUENCE_SPLIT_BRAIN",
            name="Simultaneous BIGSERIAL Sequence Allocation",
            status=status,
            latency_ms=elapsed_ms,
            detail=detail,
            metrics={
                "id_a": results["a"],
                "id_b": results["b"],
                "staggered_parity_ok": results["a"] != results["b"],
                "converged": converged,
            },
        )
    finally:
        for dsn in (dsn_a, dsn_b):
            with (
                contextlib.suppress(Exception),
                _connect(dsn, autocommit=True) as conn,
            ):
                conn.execute(
                    "DELETE FROM personnes WHERE cle_deduplication IN (%s, %s)",
                    (key_a, key_b),
                )


def _probe_cross_node_fk_causality(
    conn_a: psycopg.Connection,
    conn_b: psycopg.Connection,
    run_num: int,
    timeout_sec: float,
) -> ProbeResult:
    """P4: Insert parent UL on A and immediately insert child ETAB on B."""
    import psycopg

    siren = f"998{run_num:04d}40"
    siret = f"{siren}00014"
    t0 = time.perf_counter()
    immediate_fk_error_23503 = False
    attempts = 0
    child_inserted = False
    converged = False

    try:
        with conn_a.cursor() as cur_a:
            cur_a.execute(
                """
                INSERT INTO unites_legales (
                    siren, etat_administratif, denomination
                )
                VALUES (%s, 'A', 'MM PROBE P4 PARENT')
                ON CONFLICT (siren) DO NOTHING
                """,
                (siren,),
            )

        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            attempts += 1
            try:
                with conn_b.cursor() as cur_b:
                    cur_b.execute(
                        """
                        INSERT INTO etablissements (
                            siret, siren, nic, etat_administratif, enseigne_1
                        )
                        VALUES (%s, %s, '00014', 'A', 'MM PROBE P4 CHILD')
                        ON CONFLICT (siret) DO NOTHING
                        """,
                        (siret, siren),
                    )
                child_inserted = True
                break
            except psycopg.errors.ForeignKeyViolation:
                immediate_fk_error_23503 = True
                time.sleep(0.025)

        if child_inserted:
            while time.monotonic() < deadline:
                with conn_a.cursor() as cur_a:
                    cur_a.execute(
                        "SELECT 1 FROM etablissements WHERE siret = %s",
                        (siret,),
                    )
                    if cur_a.fetchone() is not None:
                        converged = True
                        break
                time.sleep(0.05)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if not child_inserted or not converged:
            status = "FAIL"
            detail = "Cross-node parent/child FK replication did not converge."
        elif immediate_fk_error_23503:
            status = "WARN"
            detail = (
                "Observed transient 23503 ForeignKeyViolation under async replication "
                "before cross-node convergence."
            )
        else:
            status = "PASS"
            detail = "Child insert and round-trip FK convergence succeeded immediately."

        return ProbeResult(
            probe_id="P4_CROSS_NODE_FK_CAUSALITY",
            name="Cross-Node Parent/Child FK Causality",
            status=status,
            latency_ms=elapsed_ms,
            detail=detail,
            metrics={
                "immediate_fk_error_23503": immediate_fk_error_23503,
                "retry_attempts": attempts,
                "convergence_ms": round(elapsed_ms, 2),
            },
        )
    finally:
        with contextlib.suppress(Exception):
            conn_a.execute("DELETE FROM unites_legales WHERE siren = %s", (siren,))
        with contextlib.suppress(Exception):
            conn_b.execute("DELETE FROM unites_legales WHERE siren = %s", (siren,))


def _probe_bulk_copy_lag(
    conn_a: psycopg.Connection,
    conn_b: psycopg.Connection,
    run_num: int,
    run_tag: str,
    batch_rows: int,
    timeout_sec: float,
) -> ProbeResult:
    """P5: Measure COPY FROM STDIN replication lag and pg_trgm visibility on Node B."""
    siren = f"998{run_num:04d}50"
    sign = f"MMBULK_{run_tag}"
    t0 = time.perf_counter()

    try:
        with conn_a.transaction(), conn_a.cursor() as cur_a:
            cur_a.execute(
                """
                INSERT INTO unites_legales (
                    siren, etat_administratif, denomination
                )
                VALUES (%s, 'A', %s)
                """,
                (siren, f"MM PROBE P5 {run_tag}"),
            )
            cur_a.execute(
                """
                CREATE TEMP TABLE tmp_mm_p5 (
                    siret VARCHAR(14),
                    siren VARCHAR(9),
                    nic VARCHAR(5),
                    etat_administratif CHAR(1),
                    enseigne_1 VARCHAR(150)
                ) ON COMMIT DROP
                """
            )
            copy_sql = (
                "COPY tmp_mm_p5 "
                "(siret, siren, nic, etat_administratif, enseigne_1) FROM STDIN"
            )
            with cur_a.copy(copy_sql) as copy:
                for idx in range(batch_rows):
                    nic = f"{idx:05d}"
                    copy.write_row((f"{siren}{nic}", siren, nic, "A", sign))
            cur_a.execute(
                """
                INSERT INTO etablissements (
                    siret, siren, nic, etat_administratif, enseigne_1
                )
                SELECT siret, siren, nic, etat_administratif, enseigne_1
                FROM tmp_mm_p5
                """
            )

        commit_ts = time.perf_counter()
        synced_count = 0
        trgm_count = 0
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            with conn_b.cursor() as cur_b:
                cur_b.execute(
                    """
                    SELECT
                        COUNT(*),
                        COUNT(*) FILTER (WHERE enseigne_recherche %% %s)
                    FROM etablissements
                    WHERE siren = %s
                    """,
                    (sign, siren),
                )
                row = cur_b.fetchone()
                if row:
                    synced_count, trgm_count = int(row[0]), int(row[1])
                if synced_count >= batch_rows and trgm_count >= batch_rows:
                    break
            time.sleep(0.05)

        lag_ms = (time.perf_counter() - commit_ts) * 1000.0
        total_ms = (time.perf_counter() - t0) * 1000.0
        rows_per_sec = round(batch_rows / max(lag_ms / 1000.0, 1e-6), 2)
        ok = synced_count >= batch_rows and trgm_count >= batch_rows
        return ProbeResult(
            probe_id="P5_BULK_COPY_REPLICATION_LAG",
            name="Bulk COPY FROM STDIN Replication Lag & pg_trgm Visibility",
            status="PASS" if ok else "FAIL",
            latency_ms=total_ms,
            detail=(
                f"Replicated {synced_count}/{batch_rows} rows (pg_trgm visible: "
                f"{trgm_count}) in {lag_ms:.2f} ms ({rows_per_sec} rows/s)."
            ),
            metrics={
                "batch_rows": batch_rows,
                "synced_rows": synced_count,
                "trgm_visible_rows": trgm_count,
                "lag_ms": round(lag_ms, 2),
                "rows_per_sec": rows_per_sec,
            },
        )
    finally:
        with contextlib.suppress(Exception):
            conn_a.execute("DELETE FROM unites_legales WHERE siren = %s", (siren,))
        with contextlib.suppress(Exception):
            conn_b.execute("DELETE FROM unites_legales WHERE siren = %s", (siren,))


def _subscription_error_count(conn: psycopg.Connection) -> int:
    """Read apply/sync error counts from pg_stat_subscription_stats when supported."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(SUM(apply_error_count + sync_error_count), 0)
                FROM pg_stat_subscription_stats
                """
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0
    except Exception:
        return 0


def _probe_concurrent_siret_upsert(
    dsn_a: str,
    dsn_b: str,
    run_num: int,
    timeout_sec: float,
) -> ProbeResult:
    """P3: Execute concurrent conflicting updates on the same SIRET across A and B."""
    siren = f"998{run_num:04d}30"
    siret = f"{siren}00013"
    t0 = time.perf_counter()

    try:
        with (
            _connect(dsn_a, autocommit=True) as conn_a,
            _connect(dsn_b, autocommit=True) as conn_b,
        ):
            err_before_a = _subscription_error_count(conn_a)
            err_before_b = _subscription_error_count(conn_b)

            with conn_a.cursor() as cur_a:
                cur_a.execute(
                    """
                    INSERT INTO unites_legales (
                        siren, etat_administratif, denomination
                    )
                    VALUES (%s, 'A', 'MM PROBE P3 UNIT')
                    ON CONFLICT (siren) DO NOTHING
                    """,
                    (siren,),
                )
                cur_a.execute(
                    """
                    INSERT INTO etablissements (
                        siret, siren, nic, etat_administratif, enseigne_1,
                        date_dernier_traitement
                    )
                    VALUES (
                        %s, %s, '00013', 'A', 'MM_INITIAL',
                        '2025-01-01T00:00:00+00:00'::timestamptz
                    )
                    ON CONFLICT (siret) DO NOTHING
                    """,
                    (siret, siren),
                )

            deadline = time.monotonic() + timeout_sec
            while time.monotonic() < deadline:
                with conn_b.cursor() as cur_b:
                    cur_b.execute(
                        "SELECT 1 FROM etablissements WHERE siret = %s",
                        (siret,),
                    )
                    if cur_b.fetchone() is not None:
                        break
                time.sleep(0.05)

        barrier = threading.Barrier(2)
        tx_errors: dict[str, tuple[str | None, str]] = {}

        def _update_node(label: str, dsn: str, sql_stmt: str) -> None:
            try:
                with _connect(dsn, autocommit=False) as conn:
                    barrier.wait(timeout=5.0)
                    with conn.cursor() as cur:
                        cur.execute(sql_stmt, (siret,))
                    conn.commit()
            except Exception as exc:
                tx_errors[label] = (getattr(exc, "sqlstate", None), str(exc))

        stmt_a = """
            UPDATE etablissements
            SET etat_administratif = 'F',
                date_dernier_traitement = '2025-02-01T12:00:00+00:00'::timestamptz,
                updated_at = NOW()
            WHERE siret = %s
        """
        stmt_b = """
            UPDATE etablissements
            SET enseigne_1 = 'MM_NODE_B',
                date_dernier_traitement = '2025-01-15T12:00:00+00:00'::timestamptz,
                updated_at = NOW()
            WHERE siret = %s
        """
        thread_a = threading.Thread(target=_update_node, args=("a", dsn_a, stmt_a))
        thread_b = threading.Thread(target=_update_node, args=("b", dsn_b, stmt_b))
        thread_a.start()
        thread_b.start()
        thread_a.join()
        thread_b.join()

        if any(code == "40001" for code, _ in tx_errors.values()):
            return ProbeResult(
                probe_id="P3_CONCURRENT_SIRET_UPSERT",
                name="Concurrent Conflicting SIRET Update Resolution",
                status="WARN",
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail="Concurrent update aborted with SQLSTATE 40001 error.",
                metrics={
                    "classification": "SERIALIZATION_ABORT_40001",
                    "errors": tx_errors,
                },
            )

        row_a: tuple[Any, ...] | None = None
        row_b: tuple[Any, ...] | None = None
        err_delta_a = 0
        err_delta_b = 0
        select_p3 = (
            "SELECT etat_administratif, enseigne_1, date_dernier_traitement "
            "FROM etablissements WHERE siret = %s"
        )
        with (
            _connect(dsn_a, autocommit=True) as conn_a,
            _connect(dsn_b, autocommit=True) as conn_b,
        ):
            settle_deadline = time.monotonic() + min(timeout_sec, 3.0)
            while time.monotonic() < settle_deadline:
                with conn_a.cursor() as cur_a, conn_b.cursor() as cur_b:
                    cur_a.execute(select_p3, (siret,))
                    row_a = cur_a.fetchone()
                    cur_b.execute(select_p3, (siret,))
                    row_b = cur_b.fetchone()
                err_delta_a = max(0, _subscription_error_count(conn_a) - err_before_a)
                err_delta_b = max(0, _subscription_error_count(conn_b) - err_before_b)
                if err_delta_a > 0 or err_delta_b > 0:
                    break
                time.sleep(0.15)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if row_a is not None and row_a == row_b:
            if row_a[0] == "F":
                classification = "CONVERGED_DETERMINISTIC"
                status = "PASS"
                detail = "Nodes converged deterministically to newer timestamp state."
            else:
                classification = "CONVERGED_NON_MONOTONIC"
                status = "WARN"
                detail = (
                    "Nodes converged, but newer timestamp state did not win: "
                    f"{row_a}."
                )
        elif err_delta_a > 0 or err_delta_b > 0:
            classification = "SUBSCRIPTION_STALLED"
            status = "WARN"
            detail = (
                "Subscription apply error stalled conflict resolution "
                f"(errors A={err_delta_a}, B={err_delta_b})."
            )
        else:
            classification = "DIVERGED_SPLIT_BRAIN"
            status = "FAIL"
            detail = (
                "Nodes diverged on concurrent SIRET update without conflict resolution "
                f"(A={row_a}, B={row_b})."
            )

        return ProbeResult(
            probe_id="P3_CONCURRENT_SIRET_UPSERT",
            name="Concurrent Conflicting SIRET Update Resolution",
            status=status,
            latency_ms=elapsed_ms,
            detail=detail,
            metrics={
                "classification": classification,
                "state_a": list(row_a) if row_a else None,
                "state_b": list(row_b) if row_b else None,
                "subscription_errors_delta": err_delta_a + err_delta_b,
            },
        )
    finally:
        for dsn in (dsn_a, dsn_b):
            with (
                contextlib.suppress(Exception),
                _connect(dsn, autocommit=True) as conn,
            ):
                conn.execute("DELETE FROM unites_legales WHERE siren LIKE '998%'")
                conn.execute(
                    "DELETE FROM personnes WHERE cle_deduplication LIKE 'mm_probe_%'"
                )


def run_mm_qualification(
    dsn_a: str,
    dsn_b: str,
    *,
    candidate_name: str = "pg18-candidate",
    batch_rows: int = 200,
    timeout_sec: float = 15.0,
) -> Scorecard:
    """Run all 5 Sirene 3NF multi-master qualification probes and return Scorecard."""
    # shortcut: probes 2 nodes only (A/B); extend to mesh if >2 writers added.
    if not (1 <= batch_rows <= 99_999):
        raise ValueError("batch_rows must be between 1 and 99999")

    run_num = (int(time.time() * 1000) % 9000) + 1000
    run_tag = uuid.uuid4().hex[:8]

    with (
        _connect(dsn_a, autocommit=True) as conn_a,
        _connect(dsn_b, autocommit=True) as conn_b,
    ):
        row_a = conn_a.execute("SELECT current_setting('server_version')").fetchone()
        row_b = conn_b.execute("SELECT current_setting('server_version')").fetchone()
        ver_a = str((row_a or ("unknown",))[0])
        ver_b = str((row_b or ("unknown",))[0])

        # Execute P3 last so any replication conflict stall never blocks P4 or P5.
        p1 = _probe_ddl_compat(conn_a, conn_b)
        p2 = _probe_sequence_split_brain(dsn_a, dsn_b, run_tag, timeout_sec)
        p4 = _probe_cross_node_fk_causality(conn_a, conn_b, run_num, timeout_sec)
        p5 = _probe_bulk_copy_lag(
            conn_a, conn_b, run_num, run_tag, batch_rows, timeout_sec
        )

    p3 = _probe_concurrent_siret_upsert(dsn_a, dsn_b, run_num, timeout_sec)
    probes = sorted([p1, p2, p3, p4, p5], key=lambda item: item.probe_id)
    verdict = classify_verdict(probes)

    logger.info(
        "Completed multi-master qualification suite.",
        extra={
            "event": "mm_qualification_completed",
            "candidate": candidate_name,
            "verdict": verdict,
        },
    )
    return Scorecard(
        candidate=candidate_name,
        pg_version_a=ver_a,
        pg_version_b=ver_b,
        verdict=verdict,
        probes=probes,
    )


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI parser for multi-master qualification."""
    parser = argparse.ArgumentParser(
        description="Run Sirene 3NF multi-master PostgreSQL qualification probes."
    )
    parser.add_argument(
        "--dsn-a",
        default=os.getenv("MM_DSN_A"),
        help="PostgreSQL DSN for Node A (default: $MM_DSN_A or DATABASE_URL).",
    )
    parser.add_argument(
        "--dsn-b",
        default=os.getenv("MM_DSN_B"),
        help="PostgreSQL DSN for Node B (default: $MM_DSN_B or DATABASE_URL).",
    )
    parser.add_argument(
        "--internal-dsn-a",
        default=os.getenv("MM_INTERNAL_DSN_A"),
        help="Inter-container DSN to reach Node A from Node B (defaults to --dsn-a).",
    )
    parser.add_argument(
        "--internal-dsn-b",
        default=os.getenv("MM_INTERNAL_DSN_B"),
        help="Inter-container DSN to reach Node B from Node A (defaults to --dsn-b).",
    )
    parser.add_argument(
        "--candidate-name",
        default="pg18-candidate",
        help="Logical name of the multi-master architecture candidate.",
    )
    parser.add_argument(
        "--setup-native-birep",
        action="store_true",
        help="Configure native PG 18 bidirectional replication before running probes.",
    )
    parser.add_argument(
        "--no-stagger-sequences",
        action="store_true",
        help="Disable INCREMENT BY 2 sequence staggering during native setup.",
    )
    parser.add_argument(
        "--batch-rows",
        type=int,
        default=200,
        help="Number of establishments to stream in P5 COPY replication lag probe.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=15.0,
        help="Per-probe replication convergence timeout in seconds.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help="Optional path to write Markdown qualification scorecard.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Optional path to write JSON qualification scorecard.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for multi-master qualification probes."""
    args = _build_parser().parse_args(argv)
    default_dsn = load_settings().database_url
    dsn_a = args.dsn_a or default_dsn
    dsn_b = args.dsn_b or default_dsn
    internal_dsn_a = args.internal_dsn_a or dsn_a
    internal_dsn_b = args.internal_dsn_b or dsn_b

    if args.setup_native_birep:
        setup_native_birep(
            dsn_a,
            dsn_b,
            internal_dsn_a,
            internal_dsn_b,
            stagger_sequences=not args.no_stagger_sequences,
        )

    scorecard = run_mm_qualification(
        dsn_a,
        dsn_b,
        candidate_name=args.candidate_name,
        batch_rows=args.batch_rows,
        timeout_sec=args.timeout_sec,
    )
    markdown = format_scorecard_markdown(scorecard)
    print(markdown)

    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown, encoding="utf-8")
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(scorecard_to_dict(scorecard), indent=2),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
