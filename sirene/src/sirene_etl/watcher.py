"""Autonomous data.gouv.fr watcher and ETL synchronization dispatcher."""

from __future__ import annotations

import argparse
import contextlib
import signal
import threading
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from sirene_etl.config import Settings, load_settings
from sirene_etl.db import (
    apply_sql_file,
    finish_etl_log,
    get_connection,
    get_last_successful_import,
    start_etl_log,
)
from sirene_etl.downloader import (
    compute_file_checksum,
    download_with_verification,
    extract_sirene_resources_from_payload,
    fetch_datagouv_sirene_resources,
)
from sirene_etl.full_import import run_full_import
from sirene_etl.incremental_import import run_incremental_import
from sirene_etl.logging_utils import get_logger

logger = get_logger(__name__)

ENTITY_ORDER = ("UNITE_LEGALE", "ETABLISSEMENT")


def _normalize_override_entry(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize an entity-keyed resource override dictionary."""
    checksum_obj = raw.get("checksum")
    if isinstance(checksum_obj, dict):
        ctype = checksum_obj.get("type") or raw.get("checksum_type")
        cval = checksum_obj.get("value") or raw.get("checksum_value")
    else:
        ctype = raw.get("checksum_type")
        cval = raw.get("checksum_value")

    return {
        "resource_id": str(raw.get("resource_id") or raw.get("id") or ""),
        "title": str(raw.get("title") or ""),
        "url": str(raw.get("url") or "").strip(),
        "format": str(raw.get("format") or "").strip().lower().lstrip("."),
        "last_modified": raw.get("last_modified") or raw.get("updated_at"),
        "checksum_type": str(ctype).strip().lower() if ctype else None,
        "checksum_value": str(cval).strip().lower() if cval else None,
        "filesize": raw.get("filesize"),
    }


def _resolve_resources(
    settings: Settings,
    api_payload_override: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Fetch remote resource metadata or extract test override payload entries."""
    if api_payload_override is None:
        return fetch_datagouv_sirene_resources(
            settings.datagouv_dataset_api,
            preferred_format=settings.preferred_format,
        )

    if isinstance(api_payload_override.get("resources"), list):
        return extract_sirene_resources_from_payload(
            api_payload_override,
            preferred_format=settings.preferred_format,
        )

    resolved: dict[str, dict[str, Any]] = {}
    for entity in ENTITY_ORDER:
        entry = api_payload_override.get(entity)
        if isinstance(entry, dict) and entry.get("url"):
            resolved[entity] = _normalize_override_entry(entry)
    return resolved


def _derive_staged_filename(entity_type: str, resource: dict[str, Any]) -> str:
    """Derive a deterministic local staging filename from resource URL or metadata."""
    url = str(resource.get("url") or "").strip()
    if url:
        name = Path(urlsplit(url).path).name
        if name:
            return name
    title = str(resource.get("title") or "").strip()
    if title:
        return Path(title).name
    fmt = str(resource.get("format") or "parquet").strip().lstrip(".")
    return f"{entity_type.lower()}.{fmt}"


def _is_resource_updated(
    entity_type: str,
    resource: dict[str, Any],
    last_import: dict[str, Any] | None,
    *,
    force: bool,
) -> tuple[bool, str]:
    """Compare remote resource metadata against the latest successful etl_logs entry."""
    if force:
        return (True, "forced")
    if last_import is None:
        return (True, "no_previous_import")

    remote_checksum = str(resource.get("checksum_value") or "").strip().lower()
    last_checksum = str(last_import.get("checksum_value") or "").strip().lower()
    if remote_checksum and last_checksum:
        if remote_checksum != last_checksum:
            return (True, "checksum_changed")
        return (False, "checksum_matched")

    last_meta = last_import.get("metadata") or {}
    remote_lm = str(resource.get("last_modified") or "").strip()
    last_lm = str(
        last_import.get("file_version") or last_meta.get("last_modified") or ""
    ).strip()
    if remote_lm and last_lm and remote_lm != last_lm:
        return (True, "last_modified_changed")

    remote_rid = str(resource.get("resource_id") or "").strip()
    last_rid = str(last_import.get("resource_id") or "").strip()
    if remote_rid and last_rid and remote_rid != last_rid:
        return (True, "resource_id_changed")

    remote_filename = _derive_staged_filename(entity_type, resource)
    last_filename = str(last_import.get("file_name") or "").strip()
    if remote_filename and last_filename and remote_filename != last_filename:
        return (True, "filename_changed")

    remote_title = str(resource.get("title") or "").strip()
    last_title = str(last_meta.get("title") or "").strip()
    if remote_title and last_title and remote_title != last_title:
        return (True, "title_changed")

    if not last_checksum and not last_lm and not last_rid:
        return (True, "incomplete_previous_metadata")
    return (False, "metadata_unchanged")


def _stage_resource(
    settings: Settings,
    entity_type: str,
    resource: dict[str, Any],
) -> tuple[Path, str, bool]:
    """Ensure a resource is present locally in staging_dir with verified checksum."""
    settings.staging_dir.mkdir(parents=True, exist_ok=True)
    dest_path = settings.staging_dir / _derive_staged_filename(entity_type, resource)
    checksum_type = str(resource.get("checksum_type") or "sha256").strip().lower()
    expected = str(resource.get("checksum_value") or "").strip().lower() or None

    if dest_path.is_file() and expected:
        local_digest = compute_file_checksum(dest_path, algorithm=checksum_type)
        if local_digest.lower() == expected:
            return (dest_path, local_digest, True)

    try:
        downloaded_path, actual_digest = download_with_verification(
            url=str(resource["url"]),
            dest_path=dest_path,
            expected_checksum=expected,
            checksum_type=checksum_type,
        )
    except ValueError as exc:
        if "checksum" in str(exc).lower() and "checksum" not in str(exc):
            raise ValueError(f"checksum verification failed: {exc}") from exc
        raise

    return (downloaded_path, actual_digest, False)


def _inspect_db_and_start_log(
    settings: Settings,
    resources: dict[str, dict[str, Any]],
    *,
    force: bool,
) -> tuple[bool, dict[str, dict[str, Any]], dict[str, str], int]:
    """Inspect database state, detect updated entities, and open a WATCHER_CHECK log."""
    with get_connection(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.unites_legales') IS NOT NULL")
            schema_ready = bool(cur.fetchone()[0])
        if not schema_ready:
            apply_sql_file(conn, settings.sql_dir / "01_schema_3nf.sql")
            conn.commit()

        watch_log_id = start_etl_log(
            conn,
            run_type="WATCHER_CHECK",
            entity_type="ALL",
            metadata={"resource_entities": sorted(resources)},
        )

        with conn.cursor() as cur:
            cur.execute("SELECT NOT EXISTS (SELECT 1 FROM unites_legales LIMIT 1)")
            is_empty = bool(cur.fetchone()[0])

        updated: dict[str, dict[str, Any]] = {}
        reasons: dict[str, str] = {}
        for entity in ENTITY_ORDER:
            resource = resources.get(entity)
            if resource is None:
                continue
            if is_empty:
                updated[entity] = resource
                reasons[entity] = "initial_empty_db"
                continue
            last_import = get_last_successful_import(conn, entity)
            changed, reason = _is_resource_updated(
                entity, resource, last_import, force=force
            )
            reasons[entity] = reason
            if changed:
                updated[entity] = resource

    return (is_empty, updated, reasons, watch_log_id)


def _finalize_watch_log(
    settings: Settings,
    watch_log_id: int,
    *,
    status: str,
    rows_processed: int = 0,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Update the WATCHER_CHECK record in etl_logs in a clean short-lived connection."""
    with get_connection(settings.database_url) as conn:
        finish_etl_log(
            conn,
            watch_log_id,
            status=status,
            rows_processed=rows_processed,
            rows_inserted=rows_inserted,
            rows_updated=rows_updated,
            error_message=error_message,
            metadata=metadata,
        )


def check_and_sync_once(
    settings: Settings,
    api_payload_override: dict[str, Any] | None = None,
    force: bool = False,
    *,
    offline_refs: bool = False,
) -> dict[str, Any]:
    """Poll dataset metadata, stage updated files, and run full or incremental ETL."""
    resources = _resolve_resources(settings, api_payload_override)
    if not resources:
        raise ValueError("No Sirene UNITE_LEGALE or ETABLISSEMENT resources resolved.")

    is_empty, updated_resources, reasons, watch_log_id = _inspect_db_and_start_log(
        settings, resources, force=force
    )
    logger.info(
        "Watcher evaluated remote Sirene resources.",
        extra={
            "event": "watcher_check_started",
            "watch_log_id": watch_log_id,
            "is_empty_db": is_empty,
            "reasons": reasons,
            "updated_entities": sorted(updated_resources),
        },
    )

    try:
        if not updated_resources:
            _finalize_watch_log(
                settings,
                watch_log_id,
                status="SKIPPED",
                metadata={"reasons": reasons, "mode": "NONE"},
            )
            logger.info(
                "Watcher skipped sync; all resources match latest successful imports.",
                extra={"event": "watcher_check_skipped", "watch_log_id": watch_log_id},
            )
            return {
                "status": "SKIPPED",
                "mode": "NONE",
                "updated_entities": [],
                "resources": resources,
                "import_stats": {},
            }

        staged_files: dict[str, Path] = {}
        download_reused: dict[str, bool] = {}
        for entity in ENTITY_ORDER:
            if entity not in updated_resources:
                continue
            path, digest, reused = _stage_resource(
                settings, entity, updated_resources[entity]
            )
            staged_files[entity] = path
            download_reused[entity] = reused
            logger.info(
                "Watcher staged resource file.",
                extra={
                    "event": "watcher_resource_staged",
                    "entity_type": entity,
                    "file_name": path.name,
                    "checksum_value": digest,
                    "reused_local_file": reused,
                },
            )

        effective_offline_refs = offline_refs or (api_payload_override is not None)
        if is_empty:
            mode = "FULL_IMPORT"
            import_stats = run_full_import(
                settings,
                ul_file=staged_files.get("UNITE_LEGALE"),
                etab_file=staged_files.get("ETABLISSEMENT"),
                offline_refs=effective_offline_refs,
                force=force,
                resource_meta=updated_resources,
            )
        else:
            mode = "INCREMENTAL_IMPORT"
            import_stats = run_incremental_import(
                settings,
                ul_file=staged_files.get("UNITE_LEGALE"),
                etab_file=staged_files.get("ETABLISSEMENT"),
                force=force,
                resource_meta=updated_resources,
            )

        rows_processed = int(import_stats.get("ul_processed", 0)) + int(
            import_stats.get("etab_processed", 0)
        )
        rows_inserted = int(import_stats.get("ul_inserted", 0)) + int(
            import_stats.get("etab_inserted", 0)
        )
        rows_updated = int(import_stats.get("ul_updated", 0)) + int(
            import_stats.get("etab_updated", 0)
        )

        _finalize_watch_log(
            settings,
            watch_log_id,
            status="SUCCESS",
            rows_processed=rows_processed,
            rows_inserted=rows_inserted,
            rows_updated=rows_updated,
            metadata={
                "mode": mode,
                "reasons": reasons,
                "updated_entities": sorted(updated_resources),
                "reused_local_files": download_reused,
                "import_stats": import_stats,
            },
        )
        logger.info(
            "Watcher completed Sirene synchronization.",
            extra={
                "event": "watcher_check_succeeded",
                "watch_log_id": watch_log_id,
                "mode": mode,
                "import_stats": import_stats,
            },
        )
        return {
            "status": "SUCCESS",
            "mode": mode,
            "updated_entities": sorted(updated_resources),
            "resources": resources,
            "import_stats": import_stats,
        }
    except Exception as exc:
        try:
            _finalize_watch_log(
                settings,
                watch_log_id,
                status="FAILED",
                error_message=str(exc),
                metadata={"reasons": reasons},
            )
        except Exception:
            logger.exception(
                "Failed to persist FAILED status on WATCHER_CHECK log.",
                extra={"watch_log_id": watch_log_id},
            )
        logger.error(
            "Watcher synchronization failed.",
            extra={
                "event": "watcher_check_failed",
                "watch_log_id": watch_log_id,
                "error": str(exc),
            },
        )
        raise


def run_daemon(
    settings: Settings,
    once: bool = False,
    interval_seconds: int | None = None,
    *,
    force: bool = False,
    offline_refs: bool = False,
) -> None:
    """Run check_and_sync_once either once or continuously on a configured interval."""
    poll_interval = (
        interval_seconds
        if interval_seconds is not None
        else settings.watcher_interval_seconds
    )
    if poll_interval <= 0:
        raise ValueError("Watcher interval_seconds must be a positive integer.")

    stop_event = threading.Event()

    def _handle_stop(signum: int, _frame: Any) -> None:
        logger.info(
            "Watcher received shutdown signal; stopping cleanly.",
            extra={"event": "watcher_shutdown_signal", "signal": signum},
        )
        stop_event.set()

    for sig in (signal.SIGINT, getattr(signal, "SIGTERM", None)):
        if sig is None:
            continue
        with contextlib.suppress(ValueError):
            signal.signal(sig, _handle_stop)

    if once:
        check_and_sync_once(settings, force=force, offline_refs=offline_refs)
        return

    logger.info(
        "Starting Sirene watcher daemon.",
        extra={
            "event": "watcher_daemon_started",
            "interval_seconds": poll_interval,
        },
    )
    while not stop_event.is_set():
        try:
            check_and_sync_once(settings, force=force, offline_refs=offline_refs)
        except Exception as exc:
            logger.error(
                "Watcher daemon iteration failed; will retry after interval.",
                extra={"event": "watcher_iteration_error", "error": str(exc)},
            )
        stop_event.wait(timeout=poll_interval)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Autonomous data.gouv.fr Sirene dataset watcher and ETL trigger."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single check-and-sync cycle and exit.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Polling interval in seconds when running in daemon mode.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download and ETL execution even if metadata matches.",
    )
    parser.add_argument(
        "--offline-refs",
        action="store_true",
        help="Seed built-in offline INSEE referentials on initial full import.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the Sirene dataset watcher."""
    args = _build_parser().parse_args(argv)
    settings = load_settings()
    run_daemon(
        settings,
        once=args.once,
        interval_seconds=args.interval,
        force=args.force,
        offline_refs=args.offline_refs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
