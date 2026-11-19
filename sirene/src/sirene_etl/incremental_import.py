"""Incremental INSEE Sirene synchronization with monotonic guard and state audit."""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sirene_etl.config import Settings, load_settings
from sirene_etl.db import (
    acquire_etl_lock,
    finish_etl_log,
    get_connection,
    is_checksum_already_imported,
    release_etl_lock,
    start_etl_log,
)
from sirene_etl.downloader import (
    compute_file_checksum,
    fetch_datagouv_sirene_resources,
)
from sirene_etl.full_import import (
    _ensure_orphan_sirens,
    _stage_remote_resource,
    _sync_sole_proprietors,
)
from sirene_etl.logging_utils import get_logger
from sirene_etl.referentials import ensure_missing_referential_codes
from sirene_etl.transforms import (
    ETABLISSEMENT_COLUMNS,
    UNITE_LEGALE_COLUMNS,
    iter_records_from_file,
    transform_etablissement_row,
    transform_unite_legale_row,
)

if TYPE_CHECKING:
    import psycopg

logger = get_logger(__name__)

_UL_IDX_CODE_CJ = UNITE_LEGALE_COLUMNS.index("code_cj")
_UL_IDX_CODE_NAF = UNITE_LEGALE_COLUMNS.index("code_naf")
_ETAB_IDX_CODE_NAF = ETABLISSEMENT_COLUMNS.index("code_naf")
_ETAB_IDX_CODE_COMMUNE = ETABLISSEMENT_COLUMNS.index("code_commune")
_ETAB_IDX_CODE_PAYS = ETABLISSEMENT_COLUMNS.index("code_pays_etranger")


def _extract_entity_meta(
    resource_meta: dict[str, Any] | None,
    entity_type: str,
) -> dict[str, Any]:
    """Extract normalized per-entity metadata dictionary."""
    if not resource_meta:
        return {}
    nested = resource_meta.get(entity_type)
    if isinstance(nested, dict):
        return dict(nested)
    if "url" in resource_meta or "checksum_value" in resource_meta:
        return dict(resource_meta)
    return {}


def _resolve_incremental_targets(
    settings: Settings,
    *,
    ul_file: Path | None,
    etab_file: Path | None,
    resource_meta: dict[str, Any] | None,
) -> tuple[dict[str, Path], dict[str, dict[str, Any]]]:
    """Resolve local or remote target files and metadata for incremental sync."""
    targets: dict[str, Path] = {}
    meta_map: dict[str, dict[str, Any]] = {}

    if ul_file is None and etab_file is None:
        discovered = fetch_datagouv_sirene_resources(
            settings.datagouv_dataset_api,
            preferred_format=settings.preferred_format,
        )
        for entity_type in ("UNITE_LEGALE", "ETABLISSEMENT"):
            resource = (
                _extract_entity_meta(resource_meta, entity_type)
                or discovered.get(entity_type, {})
            )
            if not resource or not resource.get("url"):
                continue
            dest_path, entry = _stage_remote_resource(settings, entity_type, resource)
            targets[entity_type] = dest_path
            meta_map[entity_type] = entry
        if not targets:
            raise ValueError("No incremental Sirene files provided or resolved.")
        return targets, meta_map

    provided = {"UNITE_LEGALE": ul_file, "ETABLISSEMENT": etab_file}
    for entity_type, path_opt in provided.items():
        if path_opt is None:
            continue
        path = Path(path_opt)
        if not path.is_file():
            raise FileNotFoundError(
                f"Incremental file for {entity_type} not found: {path}"
            )
        entry = _extract_entity_meta(resource_meta, entity_type)
        if not entry.get("checksum_value"):
            entry["checksum_type"] = "sha256"
            entry["checksum_value"] = compute_file_checksum(path, "sha256")
        entry.setdefault("file_name", path.name)
        targets[entity_type] = path
        meta_map[entity_type] = entry

    return targets, meta_map


def _build_inc_ul_merge_sql(temp_table: str) -> str:
    """Build monotonic timestamp-guarded UPSERT SQL for unites_legales."""
    cols_csv = ", ".join(UNITE_LEGALE_COLUMNS)
    non_pk = [c for c in UNITE_LEGALE_COLUMNS if c != "siren"]
    select_cols = ", ".join(
        "COALESCE(te.code_tranche, 'NN') AS code_tranche_effectifs"
        if col == "code_tranche_effectifs"
        else f"d.{col}"
        for col in UNITE_LEGALE_COLUMNS
    )
    set_clauses = ", ".join(
        f"{col} = COALESCE(EXCLUDED.{col}, target.{col})"
        if col == "date_creation"
        else f"{col} = EXCLUDED.{col}"
        for col in non_pk
    )
    target_tuple = ", ".join(f"target.{col}" for col in non_pk)
    excluded_tuple = ", ".join(
        f"COALESCE(EXCLUDED.{col}, target.{col})"
        if col == "date_creation"
        else f"EXCLUDED.{col}"
        for col in non_pk
    )

    return f"""
        WITH dedup AS (
            SELECT DISTINCT ON (siren) *
            FROM {temp_table}
            ORDER BY siren, date_dernier_traitement DESC NULLS LAST
        ),
        upserted AS (
            INSERT INTO unites_legales AS target ({cols_csv})
            SELECT {select_cols}
            FROM dedup d
            LEFT JOIN ref_tranches_effectifs te
                ON te.code_tranche = d.code_tranche_effectifs
            ON CONFLICT (siren) DO UPDATE SET
                {set_clauses},
                updated_at = NOW()
            WHERE COALESCE(EXCLUDED.date_dernier_traitement, 'infinity'::timestamptz)
                  >= COALESCE(target.date_dernier_traitement, '-infinity'::timestamptz)
              AND ({target_tuple}) IS DISTINCT FROM ({excluded_tuple})
            RETURNING (xmax = 0) AS is_insert
        )
        SELECT
            COALESCE(SUM(CASE WHEN is_insert THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN NOT is_insert THEN 1 ELSE 0 END), 0)
        FROM upserted
    """


def _build_inc_etab_merge_sql(temp_table: str) -> str:
    """Build monotonic timestamp-guarded UPSERT SQL for etablissements."""
    cols_csv = ", ".join(ETABLISSEMENT_COLUMNS)
    non_pk = [c for c in ETABLISSEMENT_COLUMNS if c != "siret"]
    select_cols = ", ".join(
        "COALESCE(te.code_tranche, 'NN') AS code_tranche_effectifs"
        if col == "code_tranche_effectifs"
        else f"d.{col}"
        for col in ETABLISSEMENT_COLUMNS
    )
    set_clauses = ", ".join(
        f"{col} = COALESCE(EXCLUDED.{col}, target.{col})"
        if col == "date_creation"
        else f"{col} = EXCLUDED.{col}"
        for col in non_pk
    )
    target_tuple = ", ".join(f"target.{col}" for col in non_pk)
    excluded_tuple = ", ".join(
        f"COALESCE(EXCLUDED.{col}, target.{col})"
        if col == "date_creation"
        else f"EXCLUDED.{col}"
        for col in non_pk
    )

    return f"""
        WITH dedup AS (
            SELECT DISTINCT ON (siret) *
            FROM {temp_table}
            ORDER BY siret, date_dernier_traitement DESC NULLS LAST
        ),
        upserted AS (
            INSERT INTO etablissements AS target ({cols_csv})
            SELECT {select_cols}
            FROM dedup d
            LEFT JOIN ref_tranches_effectifs te
                ON te.code_tranche = d.code_tranche_effectifs
            ON CONFLICT (siret) DO UPDATE SET
                {set_clauses},
                updated_at = NOW()
            WHERE COALESCE(EXCLUDED.date_dernier_traitement, 'infinity'::timestamptz)
                  >= COALESCE(target.date_dernier_traitement, '-infinity'::timestamptz)
              AND ({target_tuple}) IS DISTINCT FROM ({excluded_tuple})
            RETURNING (xmax = 0) AS is_insert
        )
        SELECT
            COALESCE(SUM(CASE WHEN is_insert THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN NOT is_insert THEN 1 ELSE 0 END), 0)
        FROM upserted
    """


def _record_state_transitions(
    conn: psycopg.Connection,
    temp_table: str,
    etl_log_id: int,
) -> int:
    """Audit administrative state changes before updating etablissements."""
    query = f"""
        WITH dedup AS (
            SELECT DISTINCT ON (siret) *
            FROM {temp_table}
            ORDER BY siret, date_dernier_traitement DESC NULLS LAST
        ),
        inserted_hist AS (
            INSERT INTO etablissements_historique_etat (
                siret, ancien_etat, nouvel_etat, date_effet, etl_log_id
            )
            SELECT
                d.siret,
                target.etat_administratif,
                d.etat_administratif,
                COALESCE(d.date_debut_periode, d.date_dernier_traitement::date),
                %s
            FROM dedup d
            JOIN etablissements target ON target.siret = d.siret
            WHERE COALESCE(d.date_dernier_traitement, 'infinity'::timestamptz)
                  >= COALESCE(target.date_dernier_traitement, '-infinity'::timestamptz)
              AND target.etat_administratif IS DISTINCT FROM d.etat_administratif
            RETURNING id
        )
        SELECT COUNT(*) FROM inserted_hist
    """
    with conn.cursor() as cur:
        cur.execute(query, (etl_log_id,))
        row = cur.fetchone()
    return int(row[0]) if row else 0


def _process_inc_ul(
    conn: psycopg.Connection,
    *,
    file_path: Path,
    meta: dict[str, Any],
    batch_size: int,
) -> tuple[int, int, int, int]:
    """Stream, deduplicate, and merge incremental UniteLegale rows in active tx."""
    cols_csv = ", ".join(UNITE_LEGALE_COLUMNS)
    log_id = start_etl_log(
        conn,
        run_type="INCREMENTAL_IMPORT",
        entity_type="UNITE_LEGALE",
        resource_id=meta.get("resource_id") or None,
        source_url=meta.get("url") or None,
        file_name=file_path.name,
        file_version=str(meta.get("last_modified") or "") or None,
        checksum_type=meta.get("checksum_type"),
        checksum_value=meta.get("checksum_value"),
        commit=False,
    )

    with conn.cursor() as cur:
        cur.execute(
            f"CREATE TEMP TABLE tmp_inc_ul ON COMMIT DROP "
            f"AS SELECT {cols_csv} FROM unites_legales WITH NO DATA"
        )

    processed = 0
    naf_codes: set[str] = set()
    cj_codes: set[str] = set()
    copy_sql = f"COPY tmp_inc_ul ({cols_csv}) FROM STDIN"

    for raw_batch in iter_records_from_file(file_path, batch_size=batch_size):
        transformed: list[tuple[Any, ...]] = []
        for raw_row in raw_batch:
            parsed = transform_unite_legale_row(raw_row)
            if parsed is None:
                continue
            transformed.append(parsed)
            cj_codes.add(parsed[_UL_IDX_CODE_CJ])
            naf_codes.add(parsed[_UL_IDX_CODE_NAF])

        if not transformed:
            continue

        processed += len(transformed)
        with conn.cursor() as cur, cur.copy(copy_sql) as copy:
            for item in transformed:
                copy.write_row(item)

    inserted = 0
    updated = 0
    roles_synced = 0
    if processed > 0:
        ensure_missing_referential_codes(
            conn,
            naf_codes=naf_codes,
            cj_codes=cj_codes,
            commune_codes=set(),
            pays_codes=set(),
        )
        with conn.cursor() as cur:
            cur.execute(_build_inc_ul_merge_sql("tmp_inc_ul"))
            counts = cur.fetchone()
            if counts:
                inserted = int(counts[0])
                updated = int(counts[1])
        roles_synced = _sync_sole_proprietors(conn, "tmp_inc_ul")

    finish_etl_log(
        conn,
        log_id,
        status="SUCCESS",
        rows_processed=processed,
        rows_inserted=inserted,
        rows_updated=updated,
        metadata={"roles_synced": roles_synced},
        commit=False,
    )
    return processed, inserted, updated, roles_synced


def _process_inc_etab(
    conn: psycopg.Connection,
    *,
    file_path: Path,
    meta: dict[str, Any],
    batch_size: int,
) -> tuple[int, int, int, int, int]:
    """Stream, deduplicate, audit transitions, and merge incremental Etablissements."""
    cols_csv = ", ".join(ETABLISSEMENT_COLUMNS)
    log_id = start_etl_log(
        conn,
        run_type="INCREMENTAL_IMPORT",
        entity_type="ETABLISSEMENT",
        resource_id=meta.get("resource_id") or None,
        source_url=meta.get("url") or None,
        file_name=file_path.name,
        file_version=str(meta.get("last_modified") or "") or None,
        checksum_type=meta.get("checksum_type"),
        checksum_value=meta.get("checksum_value"),
        commit=False,
    )

    with conn.cursor() as cur:
        cur.execute(
            f"CREATE TEMP TABLE tmp_inc_etab ON COMMIT DROP "
            f"AS SELECT {cols_csv} FROM etablissements WITH NO DATA"
        )

    processed = 0
    naf_codes: set[str] = set()
    commune_codes: set[str] = set()
    pays_codes: set[str] = set()
    copy_sql = f"COPY tmp_inc_etab ({cols_csv}) FROM STDIN"

    for raw_batch in iter_records_from_file(file_path, batch_size=batch_size):
        transformed: list[tuple[Any, ...]] = []
        for raw_row in raw_batch:
            parsed = transform_etablissement_row(raw_row)
            if parsed is None:
                continue
            transformed.append(parsed)
            naf_codes.add(parsed[_ETAB_IDX_CODE_NAF])
            commune_codes.add(parsed[_ETAB_IDX_CODE_COMMUNE])
            pays_val = parsed[_ETAB_IDX_CODE_PAYS]
            if pays_val:
                pays_codes.add(pays_val)

        if not transformed:
            continue

        processed += len(transformed)
        with conn.cursor() as cur, cur.copy(copy_sql) as copy:
            for item in transformed:
                copy.write_row(item)

    inserted = 0
    updated = 0
    transitions = 0
    orphans = 0
    if processed > 0:
        ensure_missing_referential_codes(
            conn,
            naf_codes=naf_codes,
            cj_codes=set(),
            commune_codes=commune_codes,
            pays_codes=pays_codes,
        )
        orphans = _ensure_orphan_sirens(conn, "tmp_inc_etab")
        transitions = _record_state_transitions(conn, "tmp_inc_etab", log_id)
        with conn.cursor() as cur:
            cur.execute(_build_inc_etab_merge_sql("tmp_inc_etab"))
            counts = cur.fetchone()
            if counts:
                inserted = int(counts[0])
                updated = int(counts[1])

    finish_etl_log(
        conn,
        log_id,
        status="SUCCESS",
        rows_processed=processed,
        rows_inserted=inserted,
        rows_updated=updated,
        metadata={
            "state_transitions": transitions,
            "orphan_sirens_created": orphans,
        },
        commit=False,
    )
    return processed, inserted, updated, transitions, orphans


def run_incremental_import(
    settings: Settings,
    *,
    ul_file: Path | None = None,
    etab_file: Path | None = None,
    force: bool = False,
    resource_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute transactional incremental Sirene synchronization with audit history."""
    targets, meta_map = _resolve_incremental_targets(
        settings,
        ul_file=ul_file,
        etab_file=etab_file,
        resource_meta=resource_meta,
    )

    stats: dict[str, Any] = {
        "ul_processed": 0,
        "ul_inserted": 0,
        "ul_updated": 0,
        "etab_processed": 0,
        "etab_inserted": 0,
        "etab_updated": 0,
        "roles_synced": 0,
        "state_transitions": 0,
        "orphan_sirens_created": 0,
        "skipped": False,
    }

    with get_connection(settings.database_url) as conn:
        acquire_etl_lock(conn)
        try:
            ul_path = targets.get("UNITE_LEGALE")
            etab_path = targets.get("ETABLISSEMENT")
            ul_meta = meta_map.get("UNITE_LEGALE", {})
            etab_meta = meta_map.get("ETABLISSEMENT", {})

            ul_skip = ul_path is None or (
                (not force)
                and is_checksum_already_imported(
                    conn,
                    "UNITE_LEGALE",
                    str(ul_meta.get("checksum_value") or ""),
                )
            )
            etab_skip = etab_path is None or (
                (not force)
                and is_checksum_already_imported(
                    conn,
                    "ETABLISSEMENT",
                    str(etab_meta.get("checksum_value") or ""),
                )
            )
            # End read-only implicit tx so conn.transaction() opens a real BEGIN/COMMIT.
            conn.commit()

            try:
                with conn.transaction():
                    if ul_path is not None and ul_skip:
                        ul_ver = str(ul_meta.get("last_modified") or "") or None
                        skip_id = start_etl_log(
                            conn,
                            run_type="INCREMENTAL_IMPORT",
                            entity_type="UNITE_LEGALE",
                            resource_id=ul_meta.get("resource_id") or None,
                            source_url=ul_meta.get("url") or None,
                            file_name=ul_path.name,
                            file_version=ul_ver,
                            checksum_type=ul_meta.get("checksum_type"),
                            checksum_value=ul_meta.get("checksum_value"),
                            metadata={"reason": "checksum_already_imported"},
                            commit=False,
                        )
                        finish_etl_log(conn, skip_id, status="SKIPPED", commit=False)
                    elif ul_path is not None:
                        ul_proc, ul_ins, ul_upd, roles = _process_inc_ul(
                            conn,
                            file_path=ul_path,
                            meta=ul_meta,
                            batch_size=settings.batch_size,
                        )
                        stats["ul_processed"] = ul_proc
                        stats["ul_inserted"] = ul_ins
                        stats["ul_updated"] = ul_upd
                        stats["roles_synced"] = roles

                    if etab_path is not None and etab_skip:
                        etab_ver = str(etab_meta.get("last_modified") or "") or None
                        skip_id = start_etl_log(
                            conn,
                            run_type="INCREMENTAL_IMPORT",
                            entity_type="ETABLISSEMENT",
                            resource_id=etab_meta.get("resource_id") or None,
                            source_url=etab_meta.get("url") or None,
                            file_name=etab_path.name,
                            file_version=etab_ver,
                            checksum_type=etab_meta.get("checksum_type"),
                            checksum_value=etab_meta.get("checksum_value"),
                            metadata={"reason": "checksum_already_imported"},
                            commit=False,
                        )
                        finish_etl_log(conn, skip_id, status="SKIPPED", commit=False)
                    elif etab_path is not None:
                        etab_proc, etab_ins, etab_upd, transitions, orphans = (
                            _process_inc_etab(
                                conn,
                                file_path=etab_path,
                                meta=etab_meta,
                                batch_size=settings.batch_size,
                            )
                        )
                        stats["etab_processed"] = etab_proc
                        stats["etab_inserted"] = etab_ins
                        stats["etab_updated"] = etab_upd
                        stats["state_transitions"] = transitions
                        stats["orphan_sirens_created"] = orphans

                    if ul_skip and etab_skip:
                        stats["skipped"] = True
            except Exception as exc:
                with contextlib.suppress(Exception):
                    conn.rollback()
                failed_id = start_etl_log(
                    conn,
                    run_type="INCREMENTAL_IMPORT",
                    entity_type="ALL",
                    metadata={"targets": sorted(targets)},
                    commit=True,
                )
                finish_etl_log(
                    conn,
                    failed_id,
                    status="FAILED",
                    error_message=str(exc),
                    commit=True,
                )
                raise

            logger.info(
                "Completed Sirene incremental import.",
                extra={"event": "incremental_import_completed", "stats": stats},
            )
            return stats
        finally:
            with contextlib.suppress(Exception):
                conn.rollback()
                release_etl_lock(conn)
                conn.rollback()


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for incremental_import."""
    parser = argparse.ArgumentParser(
        description="Run transactional incremental Sirene delta sync into PostgreSQL."
    )
    parser.add_argument(
        "--ul-file",
        type=Path,
        default=None,
        help="Path to delta StockUniteLegale (.parquet, .csv, .csv.gz, .zip).",
    )
    parser.add_argument(
        "--etab-file",
        type=Path,
        default=None,
        help="Path to delta StockEtablissement (.parquet, .csv, .csv.gz, .zip).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-import even if file checksums already succeeded in etl_logs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for incremental Sirene delta synchronization."""
    args = _build_parser().parse_args(argv)
    settings = load_settings()
    run_incremental_import(
        settings,
        ul_file=args.ul_file,
        etab_file=args.etab_file,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
