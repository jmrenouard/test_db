"""Unit tests for SIRENE data cleaning, projection, and file batch readers."""

from __future__ import annotations

import csv
from datetime import date, datetime
import io
from pathlib import Path
import zipfile

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from sirene_etl.transforms import (
    clean_sirene_str,
    iter_records_from_file,
    lambert93_to_wgs84,
    parse_bool,
    parse_date,
    parse_float,
    parse_int,
    parse_timestamp,
    transform_etablissement_row,
    transform_unite_legale_row,
)

pytestmark = pytest.mark.unit


class TestCleanSireneStr:
    """Tests for SIRENE string normalization and sentinel handling."""

    @pytest.mark.parametrize(
        "raw",
        [
            None,
            "",
            "   ",
            "\t\n",
            "[ND]",
            "[nd]",
            "  [ND]  ",
            "null",
        ],
    )
    def test_returns_none_for_empty_and_sentinels(self, raw: object) -> None:
        assert clean_sirene_str(raw) is None

    def test_strips_surrounding_whitespace(self) -> None:
        assert clean_sirene_str("  ACME TECHNOLOGIES  ") == "ACME TECHNOLOGIES"

    def test_converts_non_string_values(self) -> None:
        assert clean_sirene_str(5710) == "5710"


class TestDateTimestampAndNumericParsers:
    """Tests for scalar type parsers."""

    def test_parse_date_variants(self) -> None:
        assert parse_date("2020-01-15") == date(2020, 1, 15)
        assert parse_date("2020-01-15T08:30:00") == date(2020, 1, 15)
        assert parse_date(date(2020, 1, 15)) == date(2020, 1, 15)
        assert parse_date(datetime(2020, 1, 15, 14, 0, 0)) == date(2020, 1, 15)

    @pytest.mark.parametrize("raw", [None, "", "[ND]", "not-a-date", "2020-99-99"])
    def test_parse_date_invalid_returns_none(self, raw: object) -> None:
        assert parse_date(raw) is None

    def test_parse_timestamp_variants(self) -> None:
        ts_iso = parse_timestamp("2024-05-01T12:30:45")
        assert ts_iso is not None
        assert (ts_iso.year, ts_iso.month, ts_iso.day, ts_iso.hour, ts_iso.minute) == (
            2024,
            5,
            1,
            12,
            30,
        )

        ts_utc = parse_timestamp("2024-05-01T12:30:45Z")
        assert ts_utc is not None
        assert ts_utc.year == 2024 and ts_utc.second == 45

        ts_space = parse_timestamp("2024-05-01 12:30:45")
        assert ts_space is not None
        assert ts_space.hour == 12

        dt = datetime(2024, 5, 1, 12, 30, 45)
        assert parse_timestamp(dt) == dt

    @pytest.mark.parametrize("raw", [None, "", "[ND]", "invalid-ts"])
    def test_parse_timestamp_invalid_returns_none(self, raw: object) -> None:
        assert parse_timestamp(raw) is None

    def test_parse_bool_variants(self) -> None:
        assert parse_bool(True) is True
        assert parse_bool("true") is True
        assert parse_bool("TRUE") is True
        assert parse_bool("1") is True
        assert parse_bool(1) is True

        assert parse_bool(False) is False
        assert parse_bool("false") is False
        assert parse_bool("FALSE") is False
        assert parse_bool("0") is False
        assert parse_bool(0) is False
        assert parse_bool(None) is False
        assert parse_bool("") is False
        assert parse_bool("[ND]") is False

    def test_parse_int_and_float(self) -> None:
        assert parse_int("2024") == 2024
        assert parse_int(2024.0) == 2024
        assert parse_int("[ND]") is None
        assert parse_int("abc") is None

        assert parse_float("652469.02") == pytest.approx(652469.02)
        assert parse_float("[ND]") is None
        assert parse_float("nan") is None


class TestLambert93ToWgs84:
    """Tests for EPSG:2154 Lambert-93 to WGS84 projection."""

    def test_paris_coordinates_within_tolerance(self) -> None:
        lon, lat = lambert93_to_wgs84(652469.02, 6862035.26)
        assert lon is not None and lat is not None
        assert abs(lon - 2.3522) < 0.01
        assert abs(lat - 48.8566) < 0.01

    def test_toulouse_coordinates_within_tolerance(self) -> None:
        lon, lat = lambert93_to_wgs84(574359.0, 6279660.0)
        assert lon is not None and lat is not None
        assert abs(lon - 1.4442) < 0.01
        assert abs(lat - 43.6047) < 0.01

    @pytest.mark.parametrize(
        ("x", "y"),
        [
            (None, None),
            (652469.0, None),
            (None, 6862035.0),
            (0.0, 0.0),
            (-100000.0, 6862035.0),
            (99999999.0, 99999999.0),
            (float("nan"), 6862035.0),
            (652469.0, float("inf")),
        ],
    )
    def test_invalid_or_out_of_bounds_returns_none_pair(
        self, x: float | None, y: float | None
    ) -> None:
        assert lambert93_to_wgs84(x, y) == (None, None)


class TestIterRecordsFromFile:
    """Tests for Parquet and zipped CSV streaming readers."""

    def test_reads_parquet_in_batches_with_limit(self, tmp_path: Path) -> None:
        parquet_path = tmp_path / "sample.parquet"
        rows = [
            {"siren": "111111111", "denominationUniteLegale": "ALPHA"},
            {"siren": "222222222", "denominationUniteLegale": "BETA"},
            {"siren": "333333333", "denominationUniteLegale": "[ND]"},
        ]
        table = pa.Table.from_pylist(rows)
        pq.write_table(table, parquet_path)

        batches = list(iter_records_from_file(parquet_path, batch_size=2))
        assert [len(b) for b in batches] == [2, 1]
        flattened = [row for batch in batches for row in batch]
        assert [r["siren"] for r in flattened] == [
            "111111111",
            "222222222",
            "333333333",
        ]

        limited = [
            row
            for batch in iter_records_from_file(
                parquet_path, batch_size=2, limit_rows=2
            )
            for row in batch
        ]
        assert len(limited) == 2

    def test_reads_zipped_csv_and_strips_trailing_header_spaces(
        self, tmp_path: Path
    ) -> None:
        zip_path = tmp_path / "StockEtablissement_utf8.csv.zip"
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "siret ",
                "siren",
                "nic",
                "etatAdministratifEtablissement",
                "coordonneeLambertAbscisseEtablissement ",
                "coordonneeLambertOrdonneeEtablissement ",
            ]
        )
        writer.writerow(
            [
                "11111111100014",
                "111111111",
                "00014",
                "A",
                "652469.02",
                "6862035.26",
            ]
        )
        writer.writerow(
            [
                "22222222200018",
                "222222222",
                "00018",
                "A",
                "[ND]",
                "[ND]",
            ]
        )

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("StockEtablissement_utf8.csv", buf.getvalue().encode("utf-8"))

        batches = list(iter_records_from_file(zip_path, batch_size=1))
        assert len(batches) == 2
        first = batches[0][0]
        assert "siret" in first
        assert "coordonneeLambertAbscisseEtablissement" in first
        assert "coordonneeLambertOrdonneeEtablissement" in first
        assert first["coordonneeLambertAbscisseEtablissement"] == "652469.02"
        assert first["coordonneeLambertOrdonneeEtablissement"] == "6862035.26"


class TestRowTransformations:
    """Tests for row-level SIRENE normalization helpers."""

    def test_transform_unite_legale_row_cleans_nd_and_concatenates_prenoms(self) -> None:
        raw = {
            "siren": "222222222",
            "statutDiffusionUniteLegale": "O",
            "unitePurgeeUniteLegale": "false",
            "etatAdministratifUniteLegale": "A",
            "dateCreationUniteLegale": "2018-04-01",
            "dateDebut": "2020-01-01",
            "dateDernierTraitementUniteLegale": "2025-01-10T10:00:00",
            "denominationUniteLegale": "[ND]",
            "nomUniteLegale": "DUPONT",
            "prenomUsuelUniteLegale": "JEAN",
            "prenom1UniteLegale": "JEAN",
            "prenom2UniteLegale": "PIERRE",
            "prenom3UniteLegale": "[ND]",
            "prenom4UniteLegale": None,
            "categorieJuridiqueUniteLegale": "1000",
            "activitePrincipaleUniteLegale": "70.22Z",
            "trancheEffectifsUniteLegale": "NN",
        }
        transformed = transform_unite_legale_row(raw)
        assert transformed is not None
        assert transformed[0] == "222222222"
        assert "DUPONT" in transformed
        assert "JEAN PIERRE" in transformed

    def test_transform_unite_legale_rejects_invalid_siren(self) -> None:
        assert transform_unite_legale_row({"siren": "12345"}) is None
        assert transform_unite_legale_row({"siren": None}) is None

    def test_transform_etablissement_row_projects_coordinates(self) -> None:
        raw = {
            "siret": "11111111100014",
            "siren": "111111111",
            "nic": "00014",
            "etablissementSiege": "true",
            "statutDiffusionEtablissement": "O",
            "etatAdministratifEtablissement": "A",
            "codeCommuneEtablissement": "75101",
            "activitePrincipaleEtablissement": "62.01Z",
            "trancheEffectifsEtablissement": "NN",
            "coordonneeLambertAbscisseEtablissement": "652469.02",
            "coordonneeLambertOrdonneeEtablissement": "6862035.26",
        }
        transformed = transform_etablissement_row(raw)
        assert transformed is not None
        assert transformed[0] == "11111111100014"
        assert transformed[1] == "111111111"
        assert any(
            isinstance(v, float) and abs(v - 2.3522) < 0.01 for v in transformed
        )
        assert any(
            isinstance(v, float) and abs(v - 48.8566) < 0.01 for v in transformed
        )

    def test_transform_etablissement_rejects_invalid_siret(self) -> None:
        assert (
            transform_etablissement_row({"siret": "123", "siren": "111111111"}) is None
        )
