"""Tests for direct SQL dumps, SHA-256 verifier, and offline synthetic datasets."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re

import psycopg
import pyarrow.parquet as pq
import pytest

from sirene_etl.config import Settings, load_settings
from sirene_etl.full_import import run_full_import
from sirene_etl.incremental_import import run_incremental_import
from sirene_etl.transforms import iter_records_from_file

SYNTHETIC_SIREN_RE = re.compile(r"^9[0-9]{8}$")
GENERATED_COLUMNS = (
    "nom_recherche",
    "adresse_complete",
    "enseigne_recherche",
    "nom_complet_recherche",
)


def _reset_database(conn: psycopg.Connection) -> None:
    """Truncate SIRENE entity/log tables for clean integration testing."""
    with conn.cursor() as cur:
        cur.execute(
            """
            DO $$
            BEGIN
                IF to_regclass('public.unites_legales') IS NOT NULL THEN
                    TRUNCATE TABLE
                        etablissements_historique_etat,
                        roles_entreprises,
                        personnes,
                        etablissements,
                        unites_legales,
                        etl_logs
                    RESTART IDENTITY CASCADE;
                END IF;
            END $$;
            """
        )


def _build_settings(database_url: str, sql_dir: Path, staging_dir: Path) -> Settings:
    staging_dir.mkdir(parents=True, exist_ok=True)
    return replace(
        load_settings(),
        database_url=database_url,
        staging_dir=staging_dir,
        sql_dir=sql_dir,
        batch_size=250,
    )


@pytest.mark.unit
def test_direct_sql_and_shell_files_exist_with_lf_endings(sirene_dir: Path) -> None:
    """Verify SQL loaders, SHA-256 test script, and shell script exist with strict LF EOLs."""
    lf_files = (
        sirene_dir / "load_sirene.sql",
        sirene_dir / "load_sirene_db.sh",
        sirene_dir / "test_sirene_sha2.sql",
        sirene_dir / "data" / "sql" / "01_load_referentials.sql",
        sirene_dir / "data" / "sql" / "02_load_unites_legales.sql",
        sirene_dir / "data" / "sql" / "03_load_etablissements.sql",
        sirene_dir / "data" / "sql" / "04_load_governance_and_history.sql",
    )
    for path in lf_files:
        assert path.is_file(), f"Missing expected loader/SQL file: {path}"
        raw = path.read_bytes()
        assert len(raw) > 0, f"Empty file: {path}"
        assert b"\r" not in raw, f"CRLF detected in {path.name}; expected strict LF (\\n)"
        assert b"\n" in raw, f"Expected LF line endings in {path.name}"

    # Verify COPY headers do not attempt to load GENERATED ALWAYS columns
    for sql_dump in (
        sirene_dir / "data" / "sql" / "02_load_unites_legales.sql",
        sirene_dir / "data" / "sql" / "03_load_etablissements.sql",
        sirene_dir / "data" / "sql" / "04_load_governance_and_history.sql",
    ):
        head = "\n".join(sql_dump.read_text(encoding="utf-8").splitlines()[:25])
        for gen_col in GENERATED_COLUMNS:
            assert gen_col not in head, (
                f"Generated column {gen_col!r} should not appear in COPY header of {sql_dump.name}"
            )


@pytest.mark.unit
def test_synthetic_parquet_and_delta_datasets_structure_and_size(
    sirene_dir: Path,
) -> None:
    """Verify embedded Parquet/CSV datasets row counts, synthetic SIRENs, and < 30 MB budget."""
    data_dir = sirene_dir / "data"
    assert data_dir.is_dir(), f"Missing data directory: {data_dir}"

    total_bytes = sum(p.stat().st_size for p in data_dir.rglob("*") if p.is_file())
    assert total_bytes < 30 * 1024 * 1024, (
        f"sirene/data/ exceeds 30 MB budget: {total_bytes / (1024 * 1024):.2f} MB"
    )

    parquet_expectations = (
        (data_dir / "parquet" / "StockUniteLegale_synthetic.parquet", 15_000),
        (data_dir / "parquet" / "StockEtablissement_synthetic.parquet", 30_000),
        (data_dir / "delta" / "DeltaUniteLegale_synthetic.parquet", 250),
        (data_dir / "delta" / "DeltaEtablissement_synthetic.parquet", 500),
    )
    for pq_path, expected_rows in parquet_expectations:
        assert pq_path.is_file(), f"Missing Parquet dataset: {pq_path}"
        pf = pq.ParquetFile(pq_path)
        assert pf.metadata.num_rows == expected_rows, (
            f"{pq_path.name}: expected {expected_rows} rows, got {pf.metadata.num_rows}"
        )
        siren_col = pq.read_table(pq_path, columns=["siren"])["siren"].to_pylist()
        assert all(
            isinstance(val, str) and SYNTHETIC_SIREN_RE.fullmatch(val)
            for val in siren_col
        ), f"Non-synthetic SIREN detected in {pq_path.name}"

    delta_zip = data_dir / "delta" / "DeltaEtablissement_synthetic.csv.zip"
    assert delta_zip.is_file(), f"Missing zipped delta CSV: {delta_zip}"
    zip_rows = [
        row
        for batch in iter_records_from_file(delta_zip, batch_size=500)
        for row in batch
    ]
    assert len(zip_rows) == 500
    assert all(
        SYNTHETIC_SIREN_RE.fullmatch(str(row.get("siren", ""))) for row in zip_rows
    )


@pytest.mark.integration
def test_synthetic_parquet_full_and_incremental_import_on_pg18(
    db_conn: psycopg.Connection,
    sirene_dir: Path,
    sql_dir: Path,
    tmp_path: Path,
    database_url: str,
) -> None:
    """Verify full import (limit_rows=500) and delta import against embedded synthetic files."""
    _reset_database(db_conn)
    settings = _build_settings(database_url, sql_dir, tmp_path / "staging")

    ul_pq = sirene_dir / "data" / "parquet" / "StockUniteLegale_synthetic.parquet"
    etab_pq = sirene_dir / "data" / "parquet" / "StockEtablissement_synthetic.parquet"
    delta_ul_pq = sirene_dir / "data" / "delta" / "DeltaUniteLegale_synthetic.parquet"
    delta_etab_pq = sirene_dir / "data" / "delta" / "DeltaEtablissement_synthetic.parquet"

    full_stats = run_full_import(
        settings,
        ul_file=ul_pq,
        etab_file=etab_pq,
        offline_refs=True,
        limit_rows=500,
        force=True,
    )
    assert full_stats["ul_processed"] == 500
    assert full_stats["etab_processed"] == 500

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM etablissements")
        assert cur.fetchone()[0] == 500
        cur.execute("SELECT COUNT(*) FROM unites_legales")
        ul_count_after_full = int(cur.fetchone()[0])
        assert ul_count_after_full >= 500

    inc_stats = run_incremental_import(
        settings,
        ul_file=delta_ul_pq,
        etab_file=delta_etab_pq,
        force=True,
    )
    assert inc_stats["ul_processed"] == 250
    assert inc_stats["etab_processed"] == 500
    assert inc_stats["ul_inserted"] + inc_stats["ul_updated"] > 0
    assert inc_stats["etab_inserted"] + inc_stats["etab_updated"] == 500

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM etablissements_historique_etat")
        history_count = int(cur.fetchone()[0])
        assert history_count == inc_stats["state_transitions"]
        assert history_count == 150

        cur.execute(
            """
            SELECT run_type, entity_type, status, rows_processed
            FROM etl_logs
            WHERE status = 'SUCCESS'
            ORDER BY id
            """
        )
        log_rows = cur.fetchall()
        assert ("FULL_IMPORT", "UNITE_LEGALE", "SUCCESS", 500) in log_rows
        assert ("FULL_IMPORT", "ETABLISSEMENT", "SUCCESS", 500) in log_rows
        assert ("INCREMENTAL_IMPORT", "UNITE_LEGALE", "SUCCESS", 250) in log_rows
        assert ("INCREMENTAL_IMPORT", "ETABLISSEMENT", "SUCCESS", 500) in log_rows
