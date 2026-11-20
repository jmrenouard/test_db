"""End-to-end integration tests against live PostgreSQL 18."""

from __future__ import annotations

import csv
from dataclasses import replace
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
from pathlib import Path
import threading
import zipfile

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from sirene_etl.config import Settings, load_settings
from sirene_etl.downloader import compute_file_checksum
from sirene_etl.full_import import run_full_import
from sirene_etl.incremental_import import run_incremental_import
from sirene_etl.watcher import check_and_sync_once

pytestmark = pytest.mark.integration

UL_SCHEMA = pa.schema(
    [
        ("siren", pa.string()),
        ("statutDiffusionUniteLegale", pa.string()),
        ("unitePurgeeUniteLegale", pa.bool_()),
        ("dateCreationUniteLegale", pa.string()),
        ("sigleUniteLegale", pa.string()),
        ("sexeUniteLegale", pa.string()),
        ("prenom1UniteLegale", pa.string()),
        ("prenom2UniteLegale", pa.string()),
        ("prenom3UniteLegale", pa.string()),
        ("prenom4UniteLegale", pa.string()),
        ("prenomUsuelUniteLegale", pa.string()),
        ("pseudonymeUniteLegale", pa.string()),
        ("identifiantAssociationUniteLegale", pa.string()),
        ("trancheEffectifsUniteLegale", pa.string()),
        ("anneeEffectifsUniteLegale", pa.int64()),
        ("dateDernierTraitementUniteLegale", pa.string()),
        ("categorieEntreprise", pa.string()),
        ("anneeCategorieEntreprise", pa.int64()),
        ("dateDebut", pa.string()),
        ("etatAdministratifUniteLegale", pa.string()),
        ("nomUniteLegale", pa.string()),
        ("nomUsageUniteLegale", pa.string()),
        ("denominationUniteLegale", pa.string()),
        ("denominationUsuelle1UniteLegale", pa.string()),
        ("denominationUsuelle2UniteLegale", pa.string()),
        ("denominationUsuelle3UniteLegale", pa.string()),
        ("categorieJuridiqueUniteLegale", pa.string()),
        ("activitePrincipaleUniteLegale", pa.string()),
        ("nomenclatureActivitePrincipaleUniteLegale", pa.string()),
        ("nicSiegeUniteLegale", pa.string()),
        ("economieSocialeSolidaireUniteLegale", pa.string()),
        ("societeMissionUniteLegale", pa.string()),
        ("caractereEmployeurUniteLegale", pa.string()),
    ]
)

ETAB_COLUMNS = [
    "siret",
    "siren",
    "nic",
    "etablissementSiege",
    "statutDiffusionEtablissement",
    "etatAdministratifEtablissement",
    "dateCreationEtablissement",
    "dateDebut",
    "dateDernierTraitementEtablissement",
    "enseigne1Etablissement",
    "enseigne2Etablissement",
    "enseigne3Etablissement",
    "denominationUsuelleEtablissement",
    "activitePrincipaleEtablissement",
    "nomenclatureActivitePrincipaleEtablissement",
    "activitePrincipaleRegistreMetiersEtablissement",
    "trancheEffectifsEtablissement",
    "anneeEffectifsEtablissement",
    "caractereEmployeurEtablissement",
    "numeroVoieEtablissement",
    "indiceRepetitionEtablissement",
    "typeVoieEtablissement",
    "libelleVoieEtablissement",
    "complementAdresseEtablissement",
    "distributionSpecialeEtablissement",
    "codePostalEtablissement",
    "libelleCommuneEtablissement",
    "codeCommuneEtablissement",
    "codeCedexEtablissement",
    "libelleCedexEtablissement",
    "codePaysEtrangerEtablissement",
    "libelleCommuneEtrangerEtablissement",
    "identifiantAdresseEtablissement",
    "coordonneeLambertAbscisseEtablissement ",
    "coordonneeLambertOrdonneeEtablissement ",
]


def _make_ul_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {field.name: None for field in UL_SCHEMA}
    base.update(
        {
            "statutDiffusionUniteLegale": "O",
            "unitePurgeeUniteLegale": False,
            "etatAdministratifUniteLegale": "A",
            "categorieJuridiqueUniteLegale": "5710",
            "activitePrincipaleUniteLegale": "62.01Z",
            "nomenclatureActivitePrincipaleUniteLegale": "NAFRev2",
            "trancheEffectifsUniteLegale": "NN",
        }
    )
    base.update(overrides)
    return base


def _make_etab_row(**overrides: object) -> dict[str, str]:
    base: dict[str, str] = {col.strip(): "" for col in ETAB_COLUMNS}
    base.update(
        {
            "etablissementSiege": "false",
            "statutDiffusionEtablissement": "O",
            "etatAdministratifEtablissement": "A",
            "activitePrincipaleEtablissement": "62.01Z",
            "nomenclatureActivitePrincipaleEtablissement": "NAFRev2",
            "trancheEffectifsEtablissement": "NN",
        }
    )
    base.update({k: str(v) for k, v in overrides.items()})
    return base


def _write_ul_parquet(path: Path, rows: list[dict[str, object]]) -> Path:
    table = pa.Table.from_pylist(rows, schema=UL_SCHEMA)
    pq.write_table(table, path)
    return path


def _write_etab_zipped_csv(path: Path, rows: list[dict[str, str]]) -> Path:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(ETAB_COLUMNS)
    for row in rows:
        writer.writerow([row.get(col.strip(), "") for col in ETAB_COLUMNS])
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("StockEtablissement_utf8.csv", buf.getvalue().encode("utf-8"))
    return path


def _reset_database(conn: psycopg.Connection) -> None:
    """Truncate SIRENE entity/log tables and remove synthetic test referentials."""
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
                IF to_regclass('public.ref_communes') IS NOT NULL THEN
                    DELETE FROM ref_communes WHERE code_commune IN ('75999', '99999');
                END IF;
                IF to_regclass('public.ref_naf') IS NOT NULL THEN
                    DELETE FROM ref_naf WHERE code_naf = '99.99Z';
                END IF;
            END $$;
            """
        )
    conn.commit()


def _build_settings(database_url: str, sql_dir: Path, staging_dir: Path) -> Settings:
    staging_dir.mkdir(parents=True, exist_ok=True)
    return replace(
        load_settings(),
        database_url=database_url,
        staging_dir=staging_dir,
        sql_dir=sql_dir,
        batch_size=2,
    )


def _create_golden_dataset(dataset_dir: Path) -> tuple[Path, Path]:
    dataset_dir.mkdir(parents=True, exist_ok=True)
    ul_rows = [
        _make_ul_row(
            siren="111111111",
            etatAdministratifUniteLegale="A",
            categorieJuridiqueUniteLegale="5710",
            denominationUniteLegale="ACME TECHNOLOGIES",
            sigleUniteLegale="ACME",
            activitePrincipaleUniteLegale="62.01Z",
            trancheEffectifsUniteLegale="11",
            anneeEffectifsUniteLegale=2023,
            categorieEntreprise="PME",
            anneeCategorieEntreprise=2023,
            nicSiegeUniteLegale="00014",
            dateCreationUniteLegale="2015-03-10",
            dateDebut="2020-01-01",
            dateDernierTraitementUniteLegale="2025-01-10T10:00:00Z",
        ),
        _make_ul_row(
            siren="222222222",
            etatAdministratifUniteLegale="A",
            categorieJuridiqueUniteLegale="1000",
            denominationUniteLegale=None,
            nomUniteLegale="DUPONT",
            prenom1UniteLegale="JEAN",
            prenom2UniteLegale="PIERRE",
            prenomUsuelUniteLegale="JEAN",
            sexeUniteLegale="M",
            activitePrincipaleUniteLegale="70.22Z",
            trancheEffectifsUniteLegale="NN",
            nicSiegeUniteLegale="00018",
            dateCreationUniteLegale="2019-06-01",
            dateDebut="2019-06-01",
            dateDernierTraitementUniteLegale="2025-01-10T10:00:00Z",
        ),
        _make_ul_row(
            siren="333333333",
            statutDiffusionUniteLegale="P",
            etatAdministratifUniteLegale="A",
            categorieJuridiqueUniteLegale="5499",
            denominationUniteLegale="[ND]",
            nomUniteLegale="[ND]",
            prenom1UniteLegale="[ND]",
            prenomUsuelUniteLegale="[ND]",
            activitePrincipaleUniteLegale="62.01Z",
            trancheEffectifsUniteLegale="[ND]",
            nicSiegeUniteLegale="00015",
            dateCreationUniteLegale="2021-02-01",
            dateDebut="2021-02-01",
            dateDernierTraitementUniteLegale="2025-01-10T10:00:00Z",
        ),
        _make_ul_row(
            siren="444444444",
            etatAdministratifUniteLegale="C",
            categorieJuridiqueUniteLegale="5710",
            denominationUniteLegale="ANCIENNE SOCIETE",
            activitePrincipaleUniteLegale="99.99Z",
            nomenclatureActivitePrincipaleUniteLegale="NAF1993",
            trancheEffectifsUniteLegale="00",
            nicSiegeUniteLegale="00011",
            dateCreationUniteLegale="1995-01-01",
            dateDebut="2010-05-01",
            dateDernierTraitementUniteLegale="2025-01-10T10:00:00Z",
        ),
    ]
    etab_rows = [
        _make_etab_row(
            siret="11111111100014",
            siren="111111111",
            nic="00014",
            etablissementSiege="true",
            etatAdministratifEtablissement="A",
            codeCommuneEtablissement="75101",
            codePostalEtablissement="75001",
            libelleCommuneEtablissement="PARIS 1ER ARRONDISSEMENT",
            numeroVoieEtablissement="10",
            typeVoieEtablissement="RUE",
            libelleVoieEtablissement="DE RIVOLI",
            enseigne1Etablissement="ACME PARIS HQ",
            activitePrincipaleEtablissement="62.01Z",
            trancheEffectifsEtablissement="11",
            coordonneeLambertAbscisseEtablissement="652469.02",
            coordonneeLambertOrdonneeEtablissement="6862035.26",
            dateCreationEtablissement="2015-03-10",
            dateDebut="2020-01-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
        _make_etab_row(
            siret="11111111100022",
            siren="111111111",
            nic="00022",
            etablissementSiege="false",
            etatAdministratifEtablissement="A",
            codeCommuneEtablissement="31555",
            codePostalEtablissement="31000",
            libelleCommuneEtablissement="TOULOUSE",
            numeroVoieEtablissement="1",
            typeVoieEtablissement="PLACE",
            libelleVoieEtablissement="DU CAPITOLE",
            enseigne1Etablissement="ACME TOULOUSE LAB",
            activitePrincipaleEtablissement="62.01Z",
            trancheEffectifsEtablissement="02",
            coordonneeLambertAbscisseEtablissement="574359.00",
            coordonneeLambertOrdonneeEtablissement="6279660.00",
            dateCreationEtablissement="2018-05-01",
            dateDebut="2020-01-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
        _make_etab_row(
            siret="22222222200018",
            siren="222222222",
            nic="00018",
            etablissementSiege="true",
            etatAdministratifEtablissement="A",
            codeCommuneEtablissement="75101",
            codePostalEtablissement="75001",
            libelleCommuneEtablissement="PARIS 1ER ARRONDISSEMENT",
            enseigne1Etablissement="DUPONT CONSEIL",
            activitePrincipaleEtablissement="70.22Z",
            trancheEffectifsEtablissement="NN",
            dateCreationEtablissement="2019-06-01",
            dateDebut="2019-06-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
        _make_etab_row(
            siret="33333333300015",
            siren="333333333",
            nic="00015",
            etablissementSiege="true",
            statutDiffusionEtablissement="P",
            etatAdministratifEtablissement="A",
            codeCommuneEtablissement="[ND]",
            codePostalEtablissement="[ND]",
            libelleCommuneEtablissement="[ND]",
            libelleVoieEtablissement="[ND]",
            activitePrincipaleEtablissement="62.01Z",
            trancheEffectifsEtablissement="[ND]",
            coordonneeLambertAbscisseEtablissement="[ND]",
            coordonneeLambertOrdonneeEtablissement="[ND]",
            dateCreationEtablissement="2021-02-01",
            dateDebut="2021-02-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
        _make_etab_row(
            siret="44444444400011",
            siren="444444444",
            nic="00011",
            etablissementSiege="true",
            etatAdministratifEtablissement="F",
            codeCommuneEtablissement="75999",
            codePostalEtablissement="75999",
            libelleCommuneEtablissement="ANCIEN ARRONDISSEMENT",
            activitePrincipaleEtablissement="99.99Z",
            trancheEffectifsEtablissement="00",
            dateCreationEtablissement="1995-01-01",
            dateDebut="2010-05-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
        _make_etab_row(
            siret="55555555500017",
            siren="555555555",
            nic="00017",
            etablissementSiege="true",
            etatAdministratifEtablissement="A",
            codeCommuneEtablissement="75101",
            codePostalEtablissement="75001",
            libelleCommuneEtablissement="PARIS 1ER ARRONDISSEMENT",
            enseigne1Etablissement="ORPHAN ESTABLISHMENT",
            activitePrincipaleEtablissement="62.01Z",
            trancheEffectifsEtablissement="NN",
            dateCreationEtablissement="2022-01-01",
            dateDebut="2022-01-01",
            dateDernierTraitementEtablissement="2025-01-10T10:00:00Z",
        ),
    ]

    ul_path = _write_ul_parquet(dataset_dir / "StockUniteLegale_full.parquet", ul_rows)
    etab_path = _write_etab_zipped_csv(
        dataset_dir / "StockEtablissement_full.csv.zip", etab_rows
    )
    return ul_path, etab_path


class _QuietHandler(SimpleHTTPRequestHandler):
    """HTTP file handler suppressing per-request stdout noise during tests."""

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


def _start_http_server(directory: Path) -> tuple[ThreadingHTTPServer, str]:
    handler = functools.partial(_QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


def test_postgres_server_version_is_18(db_conn: psycopg.Connection) -> None:
    """Verify the target PostgreSQL instance runs major version 18 or newer."""
    with db_conn.cursor() as cur:
        cur.execute("SHOW server_version_num")
        version_num = int(cur.fetchone()[0])
    assert version_num >= 180000, f"Expected PostgreSQL 18+, got server_version_num={version_num}"


def test_full_import_incremental_idempotency_and_sample_queries(
    db_conn: psycopg.Connection,
    sql_dir: Path,
    tmp_path: Path,
    database_url: str,
) -> None:
    """Verify full import, referential auto-registration, fuzzy search, incremental sync, and SQL queries."""
    _reset_database(db_conn)
    settings = _build_settings(database_url, sql_dir, tmp_path / "staging")
    ul_full, etab_full = _create_golden_dataset(tmp_path / "golden")

    # 1. Full import from golden Parquet + zipped CSV dataset
    full_stats = run_full_import(
        settings,
        ul_file=ul_full,
        etab_file=etab_full,
        offline_refs=True,
        force=True,
    )
    assert full_stats["ul_processed"] == 4
    assert full_stats["etab_processed"] == 6

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM unites_legales")
        assert cur.fetchone()[0] == 5  # 4 explicit + 1 orphan placeholder

        cur.execute("SELECT COUNT(*) FROM etablissements")
        assert cur.fetchone()[0] == 6

        # Sole proprietor projected into personnes + roles_entreprises
        cur.execute(
            """
            SELECT p.nom, p.prenom_usuel, r.type_role, r.actif
            FROM roles_entreprises r
            JOIN personnes p ON p.id = r.personne_id
            WHERE r.siren = '222222222'
            """
        )
        role_row = cur.fetchone()
        assert role_row == ("DUPONT", "JEAN", "ENTREPRENEUR_INDIVIDUEL", True)

        # Partial diffusion [ND] fields normalized to NULL
        cur.execute(
            """
            SELECT ul.denomination, e.libelle_voie, e.code_commune, e.longitude, e.latitude
            FROM unites_legales ul
            JOIN etablissements e ON e.siren = ul.siren
            WHERE ul.siren = '333333333'
            """
        )
        nd_row = cur.fetchone()
        assert nd_row == (None, None, "UNK00", None, None)

        # Unseen commune and obsolete NAF auto-registered in referentials
        cur.execute("SELECT COUNT(*) FROM ref_communes WHERE code_commune = '75999'")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM ref_naf WHERE code_naf = '99.99Z'")
        assert cur.fetchone()[0] == 1

        # Lambert-93 to WGS84 projection stored on active establishments
        cur.execute(
            "SELECT longitude, latitude FROM etablissements WHERE siret = '11111111100014'"
        )
        paris_lon, paris_lat = cur.fetchone()
        assert paris_lon is not None and abs(paris_lon - 2.3522) < 0.01
        assert paris_lat is not None and abs(paris_lat - 48.8566) < 0.01

        # Orphan establishment placeholder SIREN created gracefully
        cur.execute(
            "SELECT etat_administratif FROM unites_legales WHERE siren = '555555555'"
        )
        assert cur.fetchone()[0] == "C"

        # pg_trgm GIN fuzzy search
        cur.execute(
            """
            SELECT siren, similarity(nom_recherche, %s) AS sim
            FROM unites_legales
            WHERE nom_recherche %% %s
               OR similarity(nom_recherche, %s) > 0.3
            ORDER BY sim DESC
            """,
            ("ACME TECHNOLOGIE", "ACME TECHNOLOGIE", "ACME TECHNOLOGIE"),
        )
        fuzzy_rows = cur.fetchall()
        assert any(row[0] == "111111111" for row in fuzzy_rows)

    # 2. Full import idempotency (re-run with force=True)
    run_full_import(
        settings,
        ul_file=ul_full,
        etab_file=etab_full,
        offline_refs=True,
        force=True,
    )
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM unites_legales")
        assert cur.fetchone()[0] == 5
        cur.execute("SELECT COUNT(*) FROM etablissements")
        assert cur.fetchone()[0] == 6
        cur.execute("SELECT COUNT(*) FROM personnes")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM roles_entreprises")
        assert cur.fetchone()[0] == 1

    # 3. Incremental delta: A -> F transition + stale monotonic guard
    delta_dir = tmp_path / "delta"
    delta_dir.mkdir(parents=True, exist_ok=True)
    ul_delta = _write_ul_parquet(
        delta_dir / "StockUniteLegale_delta.parquet",
        [
            _make_ul_row(
                siren="111111111",
                denominationUniteLegale="SHOULD_NOT_OVERWRITE_STALE",
                dateDernierTraitementUniteLegale="2024-01-01T00:00:00Z",
            ),
            _make_ul_row(
                siren="222222222",
                etatAdministratifUniteLegale="A",
                categorieJuridiqueUniteLegale="1000",
                denominationUniteLegale=None,
                nomUniteLegale="DUPONT",
                prenom1UniteLegale="JEAN",
                prenom2UniteLegale="PIERRE",
                prenomUsuelUniteLegale="JEAN",
                sexeUniteLegale="M",
                activitePrincipaleUniteLegale="70.22Z",
                dateDernierTraitementUniteLegale="2025-02-01T12:00:00Z",
            ),
        ],
    )
    etab_delta = _write_etab_zipped_csv(
        delta_dir / "StockEtablissement_delta.csv.zip",
        [
            _make_etab_row(
                siret="11111111100022",
                siren="111111111",
                nic="00022",
                etablissementSiege="false",
                etatAdministratifEtablissement="F",
                codeCommuneEtablissement="31555",
                codePostalEtablissement="31000",
                libelleCommuneEtablissement="TOULOUSE",
                enseigne1Etablissement="ACME TOULOUSE LAB",
                coordonneeLambertAbscisseEtablissement="574359.00",
                coordonneeLambertOrdonneeEtablissement="6279660.00",
                dateDebut="2025-02-01",
                dateDernierTraitementEtablissement="2025-02-01T12:00:00Z",
            ),
            _make_etab_row(
                siret="11111111100014",
                siren="111111111",
                nic="00014",
                etablissementSiege="true",
                etatAdministratifEtablissement="F",
                codeCommuneEtablissement="75101",
                enseigne1Etablissement="STALE_OVERWRITE_ATTEMPT",
                dateDernierTraitementEtablissement="2024-01-01T00:00:00Z",
            ),
        ],
    )

    inc_stats = run_incremental_import(
        settings, ul_file=ul_delta, etab_file=etab_delta, force=False
    )
    assert inc_stats["state_transitions"] == 1

    with db_conn.cursor() as cur:
        # Transition A -> F recorded
        cur.execute(
            "SELECT etat_administratif FROM etablissements WHERE siret = '11111111100022'"
        )
        assert cur.fetchone()[0] == "F"
        cur.execute(
            """
            SELECT ancien_etat, nouvel_etat
            FROM etablissements_historique_etat
            WHERE siret = '11111111100022'
            """
        )
        assert cur.fetchall() == [("A", "F")]

        # Stale records did NOT overwrite newer DB state
        cur.execute(
            "SELECT denomination FROM unites_legales WHERE siren = '111111111'"
        )
        assert cur.fetchone()[0] == "ACME TECHNOLOGIES"
        cur.execute(
            "SELECT etat_administratif, enseigne_1 FROM etablissements WHERE siret = '11111111100014'"
        )
        assert cur.fetchone() == ("A", "ACME PARIS HQ")

    # 4. Incremental idempotency: re-run twice with force=True, then once without force
    run_incremental_import(
        settings, ul_file=ul_delta, etab_file=etab_delta, force=True
    )
    run_incremental_import(
        settings, ul_file=ul_delta, etab_file=etab_delta, force=True
    )
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM etablissements_historique_etat WHERE siret = '11111111100022'"
        )
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM unites_legales")
        assert cur.fetchone()[0] == 5
        cur.execute("SELECT COUNT(*) FROM etablissements")
        assert cur.fetchone()[0] == 6

    skipped_stats = run_incremental_import(
        settings, ul_file=ul_delta, etab_file=etab_delta, force=False
    )
    assert skipped_stats.get("skipped") is True or (
        skipped_stats.get("ul_updated", 0) == 0
        and skipped_stats.get("etab_updated", 0) == 0
    )
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT status
            FROM etl_logs
            WHERE run_type = 'INCREMENTAL_IMPORT'
            ORDER BY id DESC
            LIMIT 2
            """
        )
        recent_statuses = [r[0] for r in cur.fetchall()]
        assert "SKIPPED" in recent_statuses

    # 5. Execute all queries in 03_sample_queries.sql cleanly
    sample_sql = (sql_dir / "03_sample_queries.sql").read_text(encoding="utf-8")
    query_count = 0
    with db_conn.cursor() as cur:
        cur.execute(sample_sql)
        while True:
            if cur.description is not None:
                query_count += 1
                cur.fetchall()
            if not cur.nextset():
                break
    assert query_count == 15


def test_watcher_http_sync_and_checksum_rejection(
    db_conn: psycopg.Connection,
    sql_dir: Path,
    tmp_path: Path,
    database_url: str,
) -> None:
    """Verify watcher HTTP download with valid SHA-256 and checksum mismatch rejection."""
    _reset_database(db_conn)
    settings = _build_settings(database_url, sql_dir, tmp_path / "watcher_staging")

    # Ensure schema exists before watcher inspects unites_legales
    from sirene_etl.db import apply_sql_file
    from sirene_etl.referentials import seed_all_referentials

    apply_sql_file(db_conn, sql_dir / "01_schema_3nf.sql")
    seed_all_referentials(db_conn, settings, offline_only=True)
    db_conn.commit()

    serve_dir = tmp_path / "http_root"
    serve_dir.mkdir(parents=True, exist_ok=True)

    ul_watch = _write_ul_parquet(
        serve_dir / "StockUniteLegale_watch.parquet",
        [
            _make_ul_row(
                siren="666666666",
                denominationUniteLegale="WATCHER SYNC CORP",
                categorieJuridiqueUniteLegale="5710",
                activitePrincipaleUniteLegale="62.01Z",
                dateDernierTraitementUniteLegale="2025-03-01T08:00:00Z",
            )
        ],
    )
    etab_watch = _write_etab_zipped_csv(
        serve_dir / "StockEtablissement_watch.csv.zip",
        [
            _make_etab_row(
                siret="66666666600010",
                siren="666666666",
                nic="00010",
                etablissementSiege="true",
                etatAdministratifEtablissement="A",
                codeCommuneEtablissement="75101",
                codePostalEtablissement="75001",
                libelleCommuneEtablissement="PARIS 1ER ARRONDISSEMENT",
                enseigne1Etablissement="WATCHER PARIS",
                dateDernierTraitementEtablissement="2025-03-01T08:00:00Z",
            )
        ],
    )

    ul_sha256 = compute_file_checksum(ul_watch, "sha256")
    etab_sha256 = compute_file_checksum(etab_watch, "sha256")

    bad_ul = _write_ul_parquet(
        serve_dir / "StockUniteLegale_corrupt.parquet",
        [
            _make_ul_row(
                siren="777777777",
                denominationUniteLegale="CORRUPT SHOULD NOT LOAD",
                dateDernierTraitementUniteLegale="2025-03-02T08:00:00Z",
            )
        ],
    )

    server, base_url = _start_http_server(serve_dir)
    try:
        valid_payload = {
            "resources": [
                {
                    "id": "res-ul-1",
                    "title": "StockUniteLegale_utf8.parquet",
                    "url": f"{base_url}/{ul_watch.name}",
                    "format": "parquet",
                    "last_modified": "2025-03-01T08:00:00+00:00",
                    "checksum": {"type": "sha256", "value": ul_sha256},
                },
                {
                    "id": "res-etab-1",
                    "title": "StockEtablissement_utf8.csv.zip",
                    "url": f"{base_url}/{etab_watch.name}",
                    "format": "csv.zip",
                    "last_modified": "2025-03-01T08:00:00+00:00",
                    "checksum": {"type": "sha256", "value": etab_sha256},
                },
            ]
        }

        result = check_and_sync_once(settings, api_payload_override=valid_payload)
        assert result is not None

        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT denomination FROM unites_legales WHERE siren = '666666666'"
            )
            assert cur.fetchone() == ("WATCHER SYNC CORP",)
            cur.execute(
                "SELECT COUNT(*) FROM etl_logs WHERE run_type = 'WATCHER_CHECK'"
            )
            assert cur.fetchone()[0] >= 1

        # Now verify checksum mismatch rejects download and does not corrupt DB
        bad_payload = {
            "resources": [
                {
                    "id": "res-ul-bad",
                    "title": "StockUniteLegale_utf8.parquet",
                    "url": f"{base_url}/{bad_ul.name}",
                    "format": "parquet",
                    "last_modified": "2025-03-02T08:00:00+00:00",
                    "checksum": {"type": "sha256", "value": "0" * 64},
                },
                {
                    "id": "res-etab-1",
                    "title": "StockEtablissement_utf8.csv.zip",
                    "url": f"{base_url}/{etab_watch.name}",
                    "format": "csv.zip",
                    "last_modified": "2025-03-01T08:00:00+00:00",
                    "checksum": {"type": "sha256", "value": etab_sha256},
                },
            ]
        }

        with pytest.raises(ValueError, match="checksum"):
            check_and_sync_once(settings, api_payload_override=bad_payload)

        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM unites_legales WHERE siren = '777777777'")
            assert cur.fetchone()[0] == 0
            cur.execute(
                "SELECT denomination FROM unites_legales WHERE siren = '666666666'"
            )
            assert cur.fetchone() == ("WATCHER SYNC CORP",)
    finally:
        server.shutdown()
        server.server_close()
