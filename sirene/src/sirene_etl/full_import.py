"""Full-stock INSEE Sirene importer with bulk COPY and role projection."""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from sirene_etl.config import Settings, load_settings
from sirene_etl.db import (
    acquire_etl_lock,
    apply_sql_file,
    drop_secondary_indexes,
    finish_etl_log,
    get_connection,
    is_checksum_already_imported,
    rebuild_indexes_and_analyze,
    release_etl_lock,
    start_etl_log,
)
from sirene_etl.downloader import (
    compute_file_checksum,
    download_with_verification,
    fetch_datagouv_sirene_resources,
)
from sirene_etl.logging_utils import get_logger
from sirene_etl.referentials import (
    ensure_missing_referential_codes,
    seed_all_referentials,
)
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


def _derive_filename(entity_type: str, resource: dict[str, Any]) -> str:
    """Derive a clean staging filename from resource URL or metadata."""
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


def _stage_remote_resource(
    settings: Settings,
    entity_type: str,
    resource: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    """Download a remote resource into staging_dir unless checksum already matches."""
    settings.staging_dir.mkdir(parents=True, exist_ok=True)
    dest_path = settings.staging_dir / _derive_filename(entity_type, resource)
    expected_checksum = (
        str(resource.get("checksum_value") or "").strip().lower() or None
    )
    checksum_type = str(resource.get("checksum_type") or "sha256").strip().lower()

    if dest_path.is_file() and expected_checksum:
        local_digest = compute_file_checksum(dest_path, checksum_type)
        if local_digest.lower() == expected_checksum:
            actual_digest = local_digest
        else:
            dest_path, actual_digest = download_with_verification(
                url=str(resource["url"]),
                dest_path=dest_path,
                expected_checksum=expected_checksum,
                checksum_type=checksum_type,
            )
    else:
        dest_path, actual_digest = download_with_verification(
            url=str(resource["url"]),
            dest_path=dest_path,
            expected_checksum=expected_checksum,
            checksum_type=checksum_type,
        )

    entry = dict(resource)
    entry["checksum_type"] = checksum_type
    entry["checksum_value"] = expected_checksum or actual_digest
    entry.setdefault("file_name", dest_path.name)
    return dest_path, entry


def _resolve_input_files(
    settings: Settings,
    *,
    ul_file: Path | None,
    etab_file: Path | None,
    resource_meta: dict[str, Any] | None,
) -> tuple[Path, Path, dict[str, dict[str, Any]]]:
    """Resolve local or remote UNITE_LEGALE and ETABLISSEMENT files and metadata."""
    meta_map: dict[str, dict[str, Any]] = {}
    if resource_meta:
        for key in ("UNITE_LEGALE", "ETABLISSEMENT"):
            if isinstance(resource_meta.get(key), dict):
                meta_map[key] = dict(resource_meta[key])

    discovered: dict[str, dict[str, Any]] = {}
    if ul_file is None or etab_file is None:
        discovered = fetch_datagouv_sirene_resources(
            settings.datagouv_dataset_api,
            preferred_format=settings.preferred_format,
        )

    resolved_paths: dict[str, Path] = {}
    provided = {"UNITE_LEGALE": ul_file, "ETABLISSEMENT": etab_file}
    for entity_type, explicit_path in provided.items():
        if explicit_path is not None:
            path = Path(explicit_path)
            if not path.is_file():
                raise FileNotFoundError(
                    f"Input file for {entity_type} not found: {path}"
                )
            resolved_paths[entity_type] = path
            entry = dict(meta_map.get(entity_type) or {})
            if not entry.get("checksum_value"):
                entry["checksum_type"] = "sha256"
                entry["checksum_value"] = compute_file_checksum(path, "sha256")
            entry.setdefault("file_name", path.name)
            meta_map[entity_type] = entry
            continue

        resource = meta_map.get(entity_type) or discovered.get(entity_type)
        if not resource or not resource.get("url"):
            raise ValueError(
                f"Unable to resolve remote resource URL for {entity_type}."
            )

        dest_path, entry = _stage_remote_resource(settings, entity_type, resource)
        resolved_paths[entity_type] = dest_path
        meta_map[entity_type] = entry

    return resolved_paths["UNITE_LEGALE"], resolved_paths["ETABLISSEMENT"], meta_map


def _build_ul_merge_sql(temp_table: str) -> str:
    """Build SQL to deduplicate and upsert legal units from a staging temp table."""
    cols_csv = ", ".join(UNITE_LEGALE_COLUMNS)
    non_pk = [c for c in UNITE_LEGALE_COLUMNS if c != "siren"]
    select_cols = ", ".join(
        "COALESCE(te.code_tranche, 'NN') AS code_tranche_effectifs"
        if col == "code_tranche_effectifs"
        else f"d.{col}"
        for col in UNITE_LEGALE_COLUMNS
    )
    set_clauses = ", ".join(f"{col} = EXCLUDED.{col}" for col in non_pk)
    target_tuple = ", ".join(f"target.{col}" for col in non_pk)
    excluded_tuple = ", ".join(f"EXCLUDED.{col}" for col in non_pk)

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
            WHERE ({target_tuple}) IS DISTINCT FROM ({excluded_tuple})
            RETURNING (xmax = 0) AS is_insert
        )
        SELECT
            COALESCE(SUM(CASE WHEN is_insert THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN NOT is_insert THEN 1 ELSE 0 END), 0)
        FROM upserted
    """


def _build_etab_merge_sql(temp_table: str) -> str:
    """Build SQL to deduplicate and upsert establishments from a staging temp table."""
    cols_csv = ", ".join(ETABLISSEMENT_COLUMNS)
    non_pk = [c for c in ETABLISSEMENT_COLUMNS if c != "siret"]
    select_cols = ", ".join(
        "COALESCE(te.code_tranche, 'NN') AS code_tranche_effectifs"
        if col == "code_tranche_effectifs"
        else f"d.{col}"
        for col in ETABLISSEMENT_COLUMNS
    )
    set_clauses = ", ".join(f"{col} = EXCLUDED.{col}" for col in non_pk)
    target_tuple = ", ".join(f"target.{col}" for col in non_pk)
    excluded_tuple = ", ".join(f"EXCLUDED.{col}" for col in non_pk)

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
            WHERE ({target_tuple}) IS DISTINCT FROM ({excluded_tuple})
            RETURNING (xmax = 0) AS is_insert
        )
        SELECT
            COALESCE(SUM(CASE WHEN is_insert THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN NOT is_insert THEN 1 ELSE 0 END), 0)
        FROM upserted
    """


def _sync_sole_proprietors(conn: psycopg.Connection, siren_source_table: str) -> int:
    """Project sole proprietors to personnes and roles_entreprises."""
    ei_cte = f"""
        WITH target_sirens AS (
            SELECT DISTINCT siren FROM {siren_source_table}
        ),
        sole_proprietors AS (
            SELECT
                ul.siren,
                COALESCE(ul.nom_naissance, ul.nom_usage) AS nom,
                ul.prenoms,
                ul.prenom_usuel,
                ul.sexe,
                ul.etat_administratif,
                encode(
                    sha256(convert_to('SIRENE_EI|' || ul.siren, 'UTF8')),
                    'hex'
                ) AS cle_dedup
            FROM unites_legales ul
            JOIN target_sirens ts ON ts.siren = ul.siren
            WHERE (
                ul.code_cj LIKE '1%%'
                OR (ul.denomination IS NULL AND ul.nom_naissance IS NOT NULL)
            )
              AND (
                COALESCE(ul.nom_naissance, ul.nom_usage) IS NOT NULL
                OR COALESCE(ul.prenom_usuel, ul.prenoms) IS NOT NULL
            )
        )
    """
    personnes_sql = (
        ei_cte
        + """
        INSERT INTO personnes (
            type_personne, nom, prenoms, prenom_usuel, sexe, cle_deduplication
        )
        SELECT
            'PHYSIQUE',
            sp.nom,
            sp.prenoms,
            sp.prenom_usuel,
            sp.sexe,
            sp.cle_dedup
        FROM sole_proprietors sp
        ON CONFLICT (cle_deduplication) DO UPDATE SET
            nom = EXCLUDED.nom,
            prenoms = EXCLUDED.prenoms,
            prenom_usuel = EXCLUDED.prenom_usuel,
            sexe = EXCLUDED.sexe,
            updated_at = NOW()
        WHERE (
            personnes.nom,
            personnes.prenoms,
            personnes.prenom_usuel,
            personnes.sexe
        ) IS DISTINCT FROM (
            EXCLUDED.nom,
            EXCLUDED.prenoms,
            EXCLUDED.prenom_usuel,
            EXCLUDED.sexe
        )
        """
    )
    roles_sql = (
        ei_cte
        + """
        , upserted_roles AS (
            INSERT INTO roles_entreprises (
                siren, personne_id, type_role, date_debut, actif, source_donnee
            )
            SELECT
                sp.siren,
                p.id,
                'ENTREPRENEUR_INDIVIDUEL',
                NULL,
                (sp.etat_administratif = 'A'),
                'SIRENE'
            FROM sole_proprietors sp
            JOIN personnes p ON p.cle_deduplication = sp.cle_dedup
            ON CONFLICT (siren, personne_id, type_role, date_debut) DO UPDATE SET
                actif = EXCLUDED.actif,
                source_donnee = EXCLUDED.source_donnee
            WHERE (roles_entreprises.actif, roles_entreprises.source_donnee)
                  IS DISTINCT FROM (EXCLUDED.actif, EXCLUDED.source_donnee)
            RETURNING id
        )
        SELECT COUNT(*) FROM sole_proprietors
        """
    )
    with conn.cursor() as cur:
        cur.execute(personnes_sql)
        cur.execute(roles_sql)
        row = cur.fetchone()
    return int(row[0]) if row else 0


def _ensure_orphan_sirens(conn: psycopg.Connection, temp_table: str) -> int:
    """Create minimal inactive placeholder units for orphan establishment SIRENs."""
    query = f"""
        WITH inserted AS (
            INSERT INTO unites_legales (
                siren,
                statut_diffusion,
                unite_purgee,
                etat_administratif,
                code_cj,
                code_naf,
                code_tranche_effectifs
            )
            SELECT DISTINCT
                t.siren,
                'P',
                FALSE,
                'C',
                '0000',
                '00.00Z',
                'NN'
            FROM {temp_table} t
            LEFT JOIN unites_legales ul ON ul.siren = t.siren
            WHERE ul.siren IS NULL
            ON CONFLICT (siren) DO NOTHING
            RETURNING siren
        )
        SELECT COUNT(*) FROM inserted
    """
    with conn.cursor() as cur:
        cur.execute(query)
        row = cur.fetchone()
    return int(row[0]) if row else 0


def _ingest_unite_legale_full(
    conn: psycopg.Connection,
    *,
    file_path: Path,
    meta: dict[str, Any],
    batch_size: int,
    limit_rows: int | None,
) -> tuple[int, int, int, int]:
    """Stream and merge a full-stock UniteLegale file in batches."""
    cols_csv = ", ".join(UNITE_LEGALE_COLUMNS)
    log_id = start_etl_log(
        conn,
        run_type="FULL_IMPORT",
        entity_type="UNITE_LEGALE",
        resource_id=meta.get("resource_id") or None,
        source_url=meta.get("url") or None,
        file_name=file_path.name,
        file_version=str(meta.get("last_modified") or "") or None,
        checksum_type=meta.get("checksum_type"),
        checksum_value=meta.get("checksum_value"),
        metadata={"limit_rows": limit_rows},
    )

    processed = 0
    inserted = 0
    updated = 0
    roles_synced = 0
    merge_sql = _build_ul_merge_sql("tmp_full_ul")
    copy_sql = f"COPY tmp_full_ul ({cols_csv}) FROM STDIN"

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE TEMP TABLE tmp_full_ul ON COMMIT PRESERVE ROWS "
                f"AS SELECT {cols_csv} FROM unites_legales WITH NO DATA"
            )
        conn.commit()

        for raw_batch in iter_records_from_file(
            file_path, batch_size=batch_size, limit_rows=limit_rows
        ):
            transformed: list[tuple[Any, ...]] = []
            naf_codes: set[str] = set()
            cj_codes: set[str] = set()

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
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE tmp_full_ul")
                with cur.copy(copy_sql) as copy:
                    for item in transformed:
                        copy.write_row(item)

            ensure_missing_referential_codes(
                conn,
                naf_codes=naf_codes,
                cj_codes=cj_codes,
                commune_codes=set(),
                pays_codes=set(),
            )

            with conn.cursor() as cur:
                cur.execute(merge_sql)
                counts = cur.fetchone()
                if counts:
                    inserted += int(counts[0])
                    updated += int(counts[1])

            roles_synced += _sync_sole_proprietors(conn, "tmp_full_ul")
            conn.commit()

        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS tmp_full_ul")
        conn.commit()

        finish_etl_log(
            conn,
            log_id,
            status="SUCCESS",
            rows_processed=processed,
            rows_inserted=inserted,
            rows_updated=updated,
            metadata={"roles_synced": roles_synced},
        )
        return processed, inserted, updated, roles_synced
    except Exception as exc:
        conn.rollback()
        try:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS tmp_full_ul")
            conn.commit()
        except Exception:
            conn.rollback()
        finish_etl_log(
            conn,
            log_id,
            status="FAILED",
            rows_processed=processed,
            rows_inserted=inserted,
            rows_updated=updated,
            error_message=str(exc),
        )
        raise


def _ingest_etablissement_full(
    conn: psycopg.Connection,
    *,
    file_path: Path,
    meta: dict[str, Any],
    batch_size: int,
    limit_rows: int | None,
) -> tuple[int, int, int, int]:
    """Stream and merge a full-stock Etablissement file in batches."""
    cols_csv = ", ".join(ETABLISSEMENT_COLUMNS)
    log_id = start_etl_log(
        conn,
        run_type="FULL_IMPORT",
        entity_type="ETABLISSEMENT",
        resource_id=meta.get("resource_id") or None,
        source_url=meta.get("url") or None,
        file_name=file_path.name,
        file_version=str(meta.get("last_modified") or "") or None,
        checksum_type=meta.get("checksum_type"),
        checksum_value=meta.get("checksum_value"),
        metadata={"limit_rows": limit_rows},
    )

    processed = 0
    inserted = 0
    updated = 0
    orphan_placeholders = 0
    merge_sql = _build_etab_merge_sql("tmp_full_etab")
    copy_sql = f"COPY tmp_full_etab ({cols_csv}) FROM STDIN"

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE TEMP TABLE tmp_full_etab ON COMMIT PRESERVE ROWS "
                f"AS SELECT {cols_csv} FROM etablissements WITH NO DATA"
            )
        conn.commit()

        for raw_batch in iter_records_from_file(
            file_path, batch_size=batch_size, limit_rows=limit_rows
        ):
            transformed: list[tuple[Any, ...]] = []
            naf_codes: set[str] = set()
            commune_codes: set[str] = set()
            pays_codes: set[str] = set()

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
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE tmp_full_etab")
                with cur.copy(copy_sql) as copy:
                    for item in transformed:
                        copy.write_row(item)

            ensure_missing_referential_codes(
                conn,
                naf_codes=naf_codes,
                cj_codes=set(),
                commune_codes=commune_codes,
                pays_codes=pays_codes,
            )
            orphan_placeholders += _ensure_orphan_sirens(conn, "tmp_full_etab")

            with conn.cursor() as cur:
                cur.execute(merge_sql)
                counts = cur.fetchone()
                if counts:
                    inserted += int(counts[0])
                    updated += int(counts[1])

            conn.commit()

        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS tmp_full_etab")
        conn.commit()

        finish_etl_log(
            conn,
            log_id,
            status="SUCCESS",
            rows_processed=processed,
            rows_inserted=inserted,
            rows_updated=updated,
            metadata={"orphan_sirens_created": orphan_placeholders},
        )
        return processed, inserted, updated, orphan_placeholders
    except Exception as exc:
        conn.rollback()
        try:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS tmp_full_etab")
            conn.commit()
        except Exception:
            conn.rollback()
        finish_etl_log(
            conn,
            log_id,
            status="FAILED",
            rows_processed=processed,
            rows_inserted=inserted,
            rows_updated=updated,
            error_message=str(exc),
        )
        raise


def run_full_import(
    settings: Settings,
    *,
    ul_file: Path | None = None,
    etab_file: Path | None = None,
    ref_dir: Path | None = None,
    offline_refs: bool = False,
    limit_rows: int | None = None,
    force: bool = False,
    resource_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute idempotent full-stock Sirene import with index rebuild and role sync."""
    resolved_ul, resolved_etab, meta_map = _resolve_input_files(
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
        "orphan_sirens_created": 0,
        "skipped": False,
    }

    with get_connection(settings.database_url) as conn:
        acquire_etl_lock(conn)
        try:
            apply_sql_file(conn, Path(settings.sql_dir) / "01_schema_3nf.sql")
            seed_all_referentials(
                conn, settings, ref_dir=ref_dir, offline_only=offline_refs
            )
            conn.commit()

            ul_meta = meta_map["UNITE_LEGALE"]
            etab_meta = meta_map["ETABLISSEMENT"]
            ul_skip = (not force) and is_checksum_already_imported(
                conn, "UNITE_LEGALE", str(ul_meta.get("checksum_value") or "")
            )
            etab_skip = (not force) and is_checksum_already_imported(
                conn, "ETABLISSEMENT", str(etab_meta.get("checksum_value") or "")
            )
            conn.commit()

            if ul_skip:
                skip_id = start_etl_log(
                    conn,
                    run_type="FULL_IMPORT",
                    entity_type="UNITE_LEGALE",
                    file_name=resolved_ul.name,
                    checksum_type=ul_meta.get("checksum_type"),
                    checksum_value=ul_meta.get("checksum_value"),
                    metadata={"reason": "checksum_already_imported"},
                )
                finish_etl_log(conn, skip_id, status="SKIPPED")

            if etab_skip:
                skip_id = start_etl_log(
                    conn,
                    run_type="FULL_IMPORT",
                    entity_type="ETABLISSEMENT",
                    file_name=resolved_etab.name,
                    checksum_type=etab_meta.get("checksum_type"),
                    checksum_value=etab_meta.get("checksum_value"),
                    metadata={"reason": "checksum_already_imported"},
                )
                finish_etl_log(conn, skip_id, status="SKIPPED")

            if ul_skip and etab_skip:
                stats["skipped"] = True
                logger.info(
                    "Full import skipped because both checksums already succeeded.",
                    extra={"event": "full_import_skipped"},
                )
                return stats

            dropped = drop_secondary_indexes(conn)
            conn.commit()
            logger.info(
                "Dropped secondary indexes prior to bulk load.",
                extra={"event": "indexes_dropped", "count": len(dropped)},
            )

            try:
                if not ul_skip:
                    ul_proc, ul_ins, ul_upd, roles = _ingest_unite_legale_full(
                        conn,
                        file_path=resolved_ul,
                        meta=ul_meta,
                        batch_size=settings.batch_size,
                        limit_rows=limit_rows,
                    )
                    stats["ul_processed"] = ul_proc
                    stats["ul_inserted"] = ul_ins
                    stats["ul_updated"] = ul_upd
                    stats["roles_synced"] = roles

                if not etab_skip:
                    etab_proc, etab_ins, etab_upd, orphans = _ingest_etablissement_full(
                        conn,
                        file_path=resolved_etab,
                        meta=etab_meta,
                        batch_size=settings.batch_size,
                        limit_rows=limit_rows,
                    )
                    stats["etab_processed"] = etab_proc
                    stats["etab_inserted"] = etab_ins
                    stats["etab_updated"] = etab_upd
                    stats["orphan_sirens_created"] = orphans
            finally:
                with contextlib.suppress(Exception):
                    conn.rollback()
                rebuild_indexes_and_analyze(conn, Path(settings.sql_dir))
                conn.commit()
                logger.info(
                    "Rebuilt secondary indexes and ran ANALYZE.",
                    extra={"event": "indexes_rebuilt"},
                )

            logger.info(
                "Completed Sirene full-stock import.",
                extra={"event": "full_import_completed", "stats": stats},
            )
            return stats
        finally:
            with contextlib.suppress(Exception):
                conn.rollback()
                release_etl_lock(conn)
                conn.rollback()


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for full_import."""
    parser = argparse.ArgumentParser(
        description="Run idempotent full-stock INSEE Sirene import into PostgreSQL."
    )
    parser.add_argument(
        "--ul-file",
        type=Path,
        default=None,
        help="Path to local StockUniteLegale (.parquet, .csv, .csv.gz, .zip).",
    )
    parser.add_argument(
        "--etab-file",
        type=Path,
        default=None,
        help="Path to local StockEtablissement (.parquet, .csv, .csv.gz, .zip).",
    )
    parser.add_argument(
        "--ref-dir",
        type=Path,
        default=None,
        help="Directory containing pre-downloaded INSEE COG and NAF files.",
    )
    parser.add_argument(
        "--offline-refs",
        action="store_true",
        help="Use built-in offline referentials without downloading COG/NAF files.",
    )
    parser.add_argument(
        "--limit-rows",
        type=int,
        default=None,
        help="Optional maximum rows to read per entity file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-import even if file checksums already succeeded in etl_logs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for full Sirene stock import."""
    args = _build_parser().parse_args(argv)
    settings = load_settings()
    run_full_import(
        settings,
        ul_file=args.ul_file,
        etab_file=args.etab_file,
        ref_dir=args.ref_dir,
        offline_refs=args.offline_refs,
        limit_rows=args.limit_rows,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
