"""PostgreSQL connection, locking, DDL, index, and audit-log helpers."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import psycopg

try:
    import psycopg
    from psycopg import pq, sql
except ImportError:  # pragma: no cover - allows pure-Python unit tests without psycopg
    psycopg = None  # type: ignore[assignment]
    pq = None  # type: ignore[assignment]
    sql = None  # type: ignore[assignment]

DEFAULT_ADVISORY_LOCK_ID = 84729101
MANAGED_DATA_TABLES = (
    "unites_legales",
    "etablissements",
    "personnes",
    "roles_entreprises",
)


def _require_psycopg() -> None:
    if psycopg is None or sql is None:
        raise RuntimeError(
            "psycopg v3 is required for PostgreSQL operations. "
            "Install 'psycopg[binary]>=3.2'."
        )


def _safe_commit(conn: Any) -> None:
    """Commit the connection unless autocommit or an explicit transaction is active."""
    if getattr(conn, "autocommit", False):
        return
    try:
        conn.commit()
    except Exception as exc:
        if psycopg is not None and isinstance(exc, psycopg.ProgrammingError):
            return
        raise


def _rollback_if_inerror(conn: Any) -> None:
    """Reset aborted transaction state before recording a failure audit entry."""
    if pq is None:
        return
    info = getattr(conn, "info", None)
    status = getattr(info, "transaction_status", None)
    if status == pq.TransactionStatus.INERROR:
        conn.rollback()


@contextmanager
def get_connection(dsn: str) -> Iterator[psycopg.Connection]:
    """Open a psycopg v3 connection context manager."""
    _require_psycopg()
    with psycopg.connect(dsn) as conn:
        yield conn


def acquire_etl_lock(
    conn: psycopg.Connection,
    lock_id: int = DEFAULT_ADVISORY_LOCK_ID,
) -> None:
    """Acquire a session-level PostgreSQL advisory lock or raise RuntimeError."""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s)", (lock_id,))
        row = cur.fetchone()
    if not row or not bool(row[0]):
        raise RuntimeError(
            f"Unable to acquire PostgreSQL advisory lock {lock_id}; "
            "another ETL instance is already running."
        )


def release_etl_lock(
    conn: psycopg.Connection,
    lock_id: int = DEFAULT_ADVISORY_LOCK_ID,
) -> bool:
    """Release a previously acquired session-level PostgreSQL advisory lock."""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
        row = cur.fetchone()
    return bool(row and row[0])


def apply_sql_file(conn: psycopg.Connection, sql_path: Path) -> None:
    """Read a UTF-8 SQL script and execute its statements on the connection."""
    path = Path(sql_path)
    if not path.is_file():
        raise FileNotFoundError(f"SQL file not found: {path}")

    script = path.read_text(encoding="utf-8")
    if not script.strip():
        return

    with conn.cursor() as cur:
        cur.execute(script)


def drop_secondary_indexes(conn: psycopg.Connection) -> list[str]:
    """Drop non-constraint secondary indexes on core tables before bulk loads."""
    _require_psycopg()
    query = """
        SELECT pi.schemaname, pi.indexname
        FROM pg_indexes pi
        JOIN pg_namespace n ON n.nspname = pi.schemaname
        JOIN pg_class c
          ON c.relname = pi.indexname
         AND c.relnamespace = n.oid
         AND c.relkind IN ('i', 'I')
        JOIN pg_index i ON i.indexrelid = c.oid
        WHERE pi.schemaname = ANY(current_schemas(false))
          AND pi.tablename = ANY(%s)
          AND NOT i.indisprimary
          AND NOT EXISTS (
              SELECT 1
              FROM pg_constraint con
              WHERE con.conindid = i.indexrelid
          )
        ORDER BY pi.tablename, pi.indexname
    """
    dropped: list[str] = []
    with conn.cursor() as cur:
        cur.execute(query, (list(MANAGED_DATA_TABLES),))
        targets = cur.fetchall()
        for schema_name, index_name in targets:
            stmt = sql.SQL("DROP INDEX IF EXISTS {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(index_name),
            )
            cur.execute(stmt)
            dropped.append(str(index_name))
    return dropped


def rebuild_indexes_and_analyze(
    conn: psycopg.Connection,
    sql_dir: Path,
) -> None:
    """Recreate secondary indexes from 02_indexes.sql and run ANALYZE."""
    apply_sql_file(conn, Path(sql_dir) / "02_indexes.sql")
    with conn.cursor() as cur:
        cur.execute(
            "ANALYZE unites_legales, etablissements, personnes, roles_entreprises"
        )


def start_etl_log(
    conn: psycopg.Connection,
    *,
    run_type: str,
    entity_type: str,
    resource_id: str | None = None,
    source_url: str | None = None,
    file_name: str | None = None,
    file_version: str | None = None,
    checksum_type: str | None = None,
    checksum_value: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> int:
    """Insert a RUNNING audit record into etl_logs and return its primary key."""
    payload_json = json.dumps(metadata or {}, default=str, ensure_ascii=False)
    query = """
        INSERT INTO etl_logs (
            run_type,
            entity_type,
            resource_id,
            source_url,
            file_name,
            file_version,
            checksum_type,
            checksum_value,
            status,
            metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'RUNNING', %s::jsonb)
        RETURNING id
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                run_type,
                entity_type,
                resource_id,
                source_url,
                file_name,
                file_version,
                checksum_type,
                checksum_value,
                payload_json,
            ),
        )
        row = cur.fetchone()
    if not row:
        raise RuntimeError("Failed to insert RUNNING row into etl_logs.")

    if commit:
        _safe_commit(conn)
    return int(row[0])


def finish_etl_log(
    conn: psycopg.Connection,
    log_id: int,
    *,
    status: str,
    rows_processed: int = 0,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> None:
    """Finalize an etl_logs row with completion status, counts, and metadata."""
    if status == "FAILED":
        _rollback_if_inerror(conn)

    metadata_json = (
        json.dumps(metadata, default=str, ensure_ascii=False)
        if metadata is not None
        else None
    )
    query = """
        UPDATE etl_logs
        SET status = %s,
            rows_processed = %s,
            rows_inserted = %s,
            rows_updated = %s,
            finished_at = NOW(),
            error_message = %s,
            metadata = CASE
                WHEN %s::jsonb IS NULL THEN metadata
                ELSE COALESCE(metadata, '{}'::jsonb) || %s::jsonb
            END
        WHERE id = %s
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                status,
                rows_processed,
                rows_inserted,
                rows_updated,
                error_message,
                metadata_json,
                metadata_json,
                log_id,
            ),
        )

    if commit:
        _safe_commit(conn)


def is_checksum_already_imported(
    conn: psycopg.Connection,
    entity_type: str,
    checksum_value: str,
) -> bool:
    """Return True if a SUCCESS import already exists for this entity and checksum."""
    normalized = (checksum_value or "").strip()
    if not normalized:
        return False

    query = """
        SELECT EXISTS (
            SELECT 1
            FROM etl_logs
            WHERE entity_type = %s
              AND status = 'SUCCESS'
              AND checksum_value IS NOT NULL
              AND checksum_value <> ''
              AND LOWER(checksum_value) = LOWER(%s)
        )
    """
    with conn.cursor() as cur:
        cur.execute(query, (entity_type, normalized))
        row = cur.fetchone()
    return bool(row and row[0])


def get_last_successful_import(
    conn: psycopg.Connection,
    entity_type: str,
) -> dict[str, Any] | None:
    """Return metadata of the latest SUCCESS import for the given entity_type."""
    query = """
        SELECT id,
               resource_id,
               file_name,
               file_version,
               checksum_type,
               checksum_value,
               finished_at,
               metadata
        FROM etl_logs
        WHERE entity_type = %s
          AND status = 'SUCCESS'
        ORDER BY finished_at DESC NULLS LAST, id DESC
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(query, (entity_type,))
        row = cur.fetchone()
    if not row:
        return None

    raw_meta = row[7]
    if isinstance(raw_meta, str):
        meta_dict: dict[str, Any] = json.loads(raw_meta) if raw_meta else {}
    elif isinstance(raw_meta, dict):
        meta_dict = raw_meta
    else:
        meta_dict = {}

    return {
        "id": row[0],
        "resource_id": row[1],
        "file_name": row[2],
        "file_version": row[3],
        "checksum_type": row[4],
        "checksum_value": row[5],
        "finished_at": row[6],
        "metadata": meta_dict,
    }
