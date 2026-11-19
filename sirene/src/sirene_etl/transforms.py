"""Data cleaning, coordinate conversion, and row transformers for INSEE Sirene."""

from __future__ import annotations

from collections.abc import Iterator
import csv
import datetime
import gzip
import io
import math
from pathlib import Path
import re
from typing import Any
import zipfile

_SIREN_RE = re.compile(r"^[0-9]{9}$")
_SIRET_RE = re.compile(r"^[0-9]{14}$")

_L93_A = 6378137.0
_L93_E = 0.0818191910428158
_L93_N = 0.725607765053267
_L93_C = 11754255.426096
_L93_XS = 700000.0
_L93_YS = 12655612.049876
_L93_LON0 = math.radians(3.0)

_TRANCHE_DEFAULT = "NN"
_VALID_CATEGORIES_ENTREPRISE = frozenset({"PME", "ETI", "GE"})
_TRUE_VALUES = frozenset({"true", "t", "1", "o", "oui", "y", "yes"})
_FALSE_VALUES = frozenset({"false", "f", "0", "n", "non", "no"})

UNITE_LEGALE_COLUMNS: tuple[str, ...] = (
    "siren",
    "statut_diffusion",
    "unite_purgee",
    "etat_administratif",
    "date_creation",
    "date_debut_periode",
    "date_dernier_traitement",
    "denomination",
    "sigle",
    "denomination_usuelle_1",
    "denomination_usuelle_2",
    "denomination_usuelle_3",
    "nom_naissance",
    "nom_usage",
    "prenom_usuel",
    "prenoms",
    "pseudonyme",
    "sexe",
    "identifiant_association",
    "categorie_entreprise",
    "annee_categorie_entreprise",
    "code_cj",
    "code_naf",
    "nomenclature_activite",
    "code_naf_2025",
    "code_tranche_effectifs",
    "annee_effectifs",
    "nic_siege",
    "economie_sociale_solidaire",
    "societe_mission",
    "caractere_employeur",
)

ETABLISSEMENT_COLUMNS: tuple[str, ...] = (
    "siret",
    "siren",
    "nic",
    "etablissement_siege",
    "statut_diffusion",
    "etat_administratif",
    "date_creation",
    "date_debut_periode",
    "date_dernier_traitement",
    "enseigne_1",
    "enseigne_2",
    "enseigne_3",
    "denomination_usuelle",
    "code_naf",
    "nomenclature_activite",
    "code_naf_2025",
    "activite_artisanale",
    "code_tranche_effectifs",
    "annee_effectifs",
    "caractere_employeur",
    "numero_voie",
    "indice_repetition",
    "type_voie",
    "libelle_voie",
    "complement_adresse",
    "distribution_speciale",
    "code_postal",
    "libelle_commune",
    "code_commune",
    "code_cedex",
    "libelle_cedex",
    "code_pays_etranger",
    "libelle_commune_etranger",
    "identifiant_adresse_ban",
    "coord_lambert_x",
    "coord_lambert_y",
    "longitude",
    "latitude",
)


def _unwrap_scalar(val: Any) -> Any:
    """Convert Arrow-like scalars to native Python values."""
    if hasattr(val, "as_py"):
        return val.as_py()
    return val


def _truncate(val: str | None, max_len: int) -> str | None:
    """Safely truncate non-null strings to match target VARCHAR lengths."""
    if val is None:
        return None
    return val[:max_len] if len(val) > max_len else val


def clean_sirene_str(val: Any) -> str | None:
    """Strip whitespace and convert empty, 'null', or '[ND]' sentinels to None."""
    val = _unwrap_scalar(val)
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        if val.is_integer():
            val = int(val)
    if isinstance(val, bytes):
        val = val.decode("utf-8", errors="replace")
    text = str(val).strip()
    if not text or text.lower() in {"null", "[nd]"}:
        return None
    return text


def parse_date(val: Any) -> datetime.date | None:
    """Parse Python, Arrow, or ISO/compact string values into datetime.date."""
    val = _unwrap_scalar(val)
    if val is None:
        return None
    if isinstance(val, datetime.datetime):
        return val.date()
    if isinstance(val, datetime.date):
        return val

    text = clean_sirene_str(val)
    if text is None:
        return None

    try:
        if len(text) >= 10 and text[4] == "-" and text[7] == "-":
            return datetime.date.fromisoformat(text[:10])
        if len(text) == 8 and text.isdigit():
            return datetime.datetime.strptime(text, "%Y%m%d").date()
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        return datetime.datetime.fromisoformat(normalized).date()
    except (ValueError, TypeError):
        return None


def parse_timestamp(val: Any) -> datetime.datetime | None:
    """Parse Python, Arrow, or ISO string values into datetime."""
    val = _unwrap_scalar(val)
    if val is None:
        return None
    if isinstance(val, datetime.datetime):
        return val
    if isinstance(val, datetime.date):
        return datetime.datetime(
            val.year, val.month, val.day, tzinfo=datetime.timezone.utc
        )

    text = clean_sirene_str(val)
    if text is None:
        return None

    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        dt = datetime.datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except (ValueError, TypeError):
        parsed_date = parse_date(text)
        if parsed_date is not None:
            return datetime.datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                tzinfo=datetime.timezone.utc,
            )
        return None


def parse_int(val: Any) -> int | None:
    """Parse integer values safely, returning None on invalid or sentinel input."""
    val = _unwrap_scalar(val)
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return int(val)

    text = clean_sirene_str(val)
    if text is None:
        return None
    try:
        return int(text)
    except ValueError:
        try:
            fval = float(text.replace(",", "."))
            if math.isnan(fval) or math.isinf(fval):
                return None
            return int(fval)
        except (ValueError, OverflowError):
            return None


def _parse_smallint(val: Any) -> int | None:
    """Parse integer clamped to PostgreSQL SMALLINT bounds."""
    parsed = parse_int(val)
    if parsed is None or parsed < -32768 or parsed > 32767:
        return None
    return parsed


def parse_float(val: Any) -> float | None:
    """Parse finite floating-point values safely."""
    val = _unwrap_scalar(val)
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        fval = float(val)
        return None if (math.isnan(fval) or math.isinf(fval)) else fval

    text = clean_sirene_str(val)
    if text is None:
        return None
    try:
        fval = float(text.replace(",", "."))
        return None if (math.isnan(fval) or math.isinf(fval)) else fval
    except ValueError:
        return None


def parse_bool(val: Any) -> bool:
    """Parse Sirene boolean representations ('O'/'true'/'1'/True) into bool."""
    val = _unwrap_scalar(val)
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return False
        return val == 1

    text = clean_sirene_str(val)
    if text is None:
        return False
    lowered = text.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    return False


def lambert93_to_wgs84(
    x: float | None,
    y: float | None,
) -> tuple[float | None, float | None]:
    """Convert EPSG:2154 (Lambert-93, GRS80) planar coordinates to WGS84 (lon, lat)."""
    if x is None or y is None or isinstance(x, bool) or isinstance(y, bool):
        return (None, None)
    try:
        fx = float(x)
        fy = float(y)
    except (TypeError, ValueError):
        return (None, None)

    if not math.isfinite(fx) or not math.isfinite(fy):
        return (None, None)
    # Reject sentinel zeros and coordinates outside the EPSG:2154 domain.
    if fx <= 0.0 or fx > 2_000_000.0 or fy < 5_000_000.0 or fy > 8_000_000.0:
        return (None, None)

    dx = fx - _L93_XS
    dy = _L93_YS - fy
    r = math.hypot(dx, dy)
    if r <= 0.0:
        return (None, None)

    gamma = math.atan2(dx, dy)
    lon = _L93_LON0 + gamma / _L93_N
    lat_iso = (-1.0 / _L93_N) * math.log(abs(r / _L93_C))

    # Fixed-point iteration for isometric to geodetic latitude on GRS80.
    lat = 2.0 * math.atan(math.exp(lat_iso)) - (math.pi / 2.0)
    for _ in range(12):
        e_sin = _L93_E * math.sin(lat)
        lat_next = (
            2.0
            * math.atan(
                math.exp(lat_iso) * ((1.0 + e_sin) / (1.0 - e_sin)) ** (_L93_E / 2.0)
            )
            - (math.pi / 2.0)
        )
        if abs(lat_next - lat) < 1e-11:
            lat = lat_next
            break
        lat = lat_next

    lon_deg = round(math.degrees(lon), 6)
    lat_deg = round(math.degrees(lat), 6)
    if not (-180.0 <= lon_deg <= 180.0 and -90.0 <= lat_deg <= 90.0):
        return (None, None)
    return (lon_deg, lat_deg)


def _iter_csv_batches(
    text_stream: io.TextIOBase,
    batch_size: int,
    limit_rows: int | None,
) -> Iterator[list[dict[str, Any]]]:
    """Stream CSV records in batches while stripping trailing header whitespace."""
    first_line = text_stream.readline()
    if not first_line:
        return

    delimiter = "," if "," in first_line else (";" if ";" in first_line else ",")
    raw_headers = next(csv.reader([first_line], delimiter=delimiter), [])
    headers = [h.strip() for h in raw_headers]
    if not headers:
        return

    reader = csv.reader(text_stream, delimiter=delimiter)
    batch: list[dict[str, Any]] = []
    yielded = 0
    num_headers = len(headers)

    for row in reader:
        if not row:
            continue
        record: dict[str, Any]
        if len(row) == num_headers:
            record = dict(zip(headers, row))
        else:
            record = {
                headers[idx]: (row[idx] if idx < len(row) else None)
                for idx in range(num_headers)
            }
        batch.append(record)
        yielded += 1

        if limit_rows is not None and yielded >= limit_rows:
            yield batch
            return
        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def iter_records_from_file(
    file_path: Path,
    batch_size: int = 50_000,
    limit_rows: int | None = None,
) -> Iterator[list[dict[str, Any]]]:
    """Stream row dicts in batches from .parquet, .csv, .csv.gz, or .zip files."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if limit_rows is not None and limit_rows <= 0:
        return

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    lower_name = path.name.lower()
    if lower_name.endswith(".parquet") or lower_name.endswith(".pq"):
        import pyarrow.parquet as pq

        parquet_file = pq.ParquetFile(path)
        yielded = 0
        for record_batch in parquet_file.iter_batches(batch_size=batch_size):
            names = record_batch.schema.names
            needs_strip = any(name != name.strip() for name in names)
            rows = record_batch.to_pylist()
            if needs_strip:
                rows = [{k.strip(): v for k, v in row.items()} for row in rows]
            if limit_rows is not None:
                remaining = limit_rows - yielded
                if remaining <= 0:
                    break
                if len(rows) > remaining:
                    rows = rows[:remaining]
            if rows:
                yield rows
                yielded += len(rows)
            if limit_rows is not None and yielded >= limit_rows:
                break
        return

    if lower_name.endswith(".zip"):
        with zipfile.ZipFile(path, "r") as zf:
            csv_entries = [
                info
                for info in zf.infolist()
                if not info.is_dir() and info.filename.lower().endswith(".csv")
            ]
            if not csv_entries:
                csv_entries = [info for info in zf.infolist() if not info.is_dir()]
            if not csv_entries:
                raise ValueError(f"ZIP archive contains no readable data files: {path}")
            with zf.open(csv_entries[0], "r") as raw_stream:
                text_stream = io.TextIOWrapper(
                    raw_stream, encoding="utf-8-sig", newline=""
                )
                yield from _iter_csv_batches(text_stream, batch_size, limit_rows)
        return

    if lower_name.endswith(".csv.gz") or lower_name.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as gz_stream:
            yield from _iter_csv_batches(gz_stream, batch_size, limit_rows)
        return

    with path.open("r", encoding="utf-8-sig", newline="") as csv_stream:
        yield from _iter_csv_batches(csv_stream, batch_size, limit_rows)


def _normalize_tranche_effectifs(val: Any) -> str:
    """Normalize INSEE workforce bracket codes to two-character referential keys."""
    cleaned = clean_sirene_str(val)
    if cleaned is None:
        return _TRANCHE_DEFAULT
    upper = cleaned.upper()
    if upper == "NN":
        return _TRANCHE_DEFAULT
    if upper.isdigit() and len(upper) == 1:
        return upper.zfill(2)
    if len(upper) > 2:
        return _TRANCHE_DEFAULT
    return upper


def _normalize_code_cj(val: Any) -> str:
    """Normalize INSEE legal category code (default '0000')."""
    cleaned = clean_sirene_str(val)
    if cleaned is None:
        return "0000"
    if cleaned.isdigit() and len(cleaned) < 4:
        return cleaned.zfill(4)
    return _truncate(cleaned, 4) or "0000"


def _normalize_code_naf(val: Any) -> str:
    """Normalize NAF activity code (default '00.00Z')."""
    cleaned = clean_sirene_str(val)
    if cleaned is None:
        return "00.00Z"
    return _truncate(cleaned, 6) or "00.00Z"


def _normalize_nic(val: Any) -> str | None:
    """Normalize 5-digit NIC code preserving leading zeros."""
    cleaned = clean_sirene_str(val)
    if cleaned is None:
        return None
    if cleaned.isdigit() and len(cleaned) < 5:
        return cleaned.zfill(5)
    return _truncate(cleaned, 5)


def transform_unite_legale_row(row: dict[str, Any]) -> tuple[Any, ...] | None:
    """Transform a raw Sirene UniteLegale record into an ordered SQL column tuple."""
    siren = clean_sirene_str(row.get("siren"))
    if siren is None or not _SIREN_RE.fullmatch(siren):
        return None

    unite_purgee = parse_bool(row.get("unitePurgeeUniteLegale"))
    raw_etat = clean_sirene_str(row.get("etatAdministratifUniteLegale"))
    if raw_etat is None:
        etat_administratif = "C" if unite_purgee else "A"
    else:
        etat_upper = raw_etat.upper()[:1]
        if etat_upper not in {"A", "C"}:
            return None
        etat_administratif = etat_upper

    statut_diffusion = (
        clean_sirene_str(row.get("statutDiffusionUniteLegale")) or "O"
    ).upper()[:1]
    date_debut = parse_date(row.get("dateDebut") or row.get("dateDebutUniteLegale"))

    prenom_parts = [
        clean_sirene_str(row.get(f"prenom{i}UniteLegale"))
        for i in range(1, 5)
    ]
    joined_prenoms = " ".join(part for part in prenom_parts if part)
    prenoms = _truncate(joined_prenoms or clean_sirene_str(row.get("prenoms")), 255)

    raw_cat = clean_sirene_str(row.get("categorieEntreprise"))
    categorie_entreprise = (
        raw_cat.upper()
        if raw_cat is not None and raw_cat.upper() in _VALID_CATEGORIES_ENTREPRISE
        else None
    )

    raw_sexe = clean_sirene_str(row.get("sexeUniteLegale"))
    sexe = raw_sexe.upper()[:1] if raw_sexe is not None else None

    code_naf_2025 = _truncate(
        clean_sirene_str(
            row.get("activitePrincipaleNAF25UniteLegale")
            or row.get("activitePrincipaleNaf25UniteLegale")
            or row.get("codeNaf2025UniteLegale")
        ),
        6,
    )

    return (
        siren,
        statut_diffusion,
        unite_purgee,
        etat_administratif,
        parse_date(row.get("dateCreationUniteLegale")),
        date_debut,
        parse_timestamp(row.get("dateDernierTraitementUniteLegale")),
        _truncate(clean_sirene_str(row.get("denominationUniteLegale")), 255),
        _truncate(clean_sirene_str(row.get("sigleUniteLegale")), 50),
        _truncate(clean_sirene_str(row.get("denominationUsuelle1UniteLegale")), 150),
        _truncate(clean_sirene_str(row.get("denominationUsuelle2UniteLegale")), 150),
        _truncate(clean_sirene_str(row.get("denominationUsuelle3UniteLegale")), 150),
        _truncate(clean_sirene_str(row.get("nomUniteLegale")), 150),
        _truncate(clean_sirene_str(row.get("nomUsageUniteLegale")), 150),
        _truncate(clean_sirene_str(row.get("prenomUsuelUniteLegale")), 100),
        prenoms,
        _truncate(clean_sirene_str(row.get("pseudonymeUniteLegale")), 150),
        sexe,
        _truncate(clean_sirene_str(row.get("identifiantAssociationUniteLegale")), 20),
        categorie_entreprise,
        _parse_smallint(row.get("anneeCategorieEntreprise")),
        _normalize_code_cj(row.get("categorieJuridiqueUniteLegale")),
        _normalize_code_naf(row.get("activitePrincipaleUniteLegale")),
        _truncate(
            clean_sirene_str(row.get("nomenclatureActivitePrincipaleUniteLegale")), 15
        ),
        code_naf_2025,
        _normalize_tranche_effectifs(row.get("trancheEffectifsUniteLegale")),
        _parse_smallint(row.get("anneeEffectifsUniteLegale")),
        _normalize_nic(row.get("nicSiegeUniteLegale")),
        _truncate(clean_sirene_str(row.get("economieSocialeSolidaireUniteLegale")), 1),
        _truncate(clean_sirene_str(row.get("societeMissionUniteLegale")), 1),
        _truncate(clean_sirene_str(row.get("caractereEmployeurUniteLegale")), 1),
    )


def transform_etablissement_row(row: dict[str, Any]) -> tuple[Any, ...] | None:
    """Transform a raw Sirene Etablissement record into an ordered SQL column tuple."""
    siret = clean_sirene_str(row.get("siret"))
    siren = clean_sirene_str(row.get("siren"))
    if siret is None or not _SIRET_RE.fullmatch(siret):
        return None
    if siren is None or not _SIREN_RE.fullmatch(siren):
        return None

    nic = _normalize_nic(row.get("nic")) or siret[9:14]

    raw_etat = clean_sirene_str(row.get("etatAdministratifEtablissement"))
    if raw_etat is None:
        etat_administratif = "A"
    else:
        etat_upper = raw_etat.upper()[:1]
        if etat_upper not in {"A", "F"}:
            return None
        etat_administratif = etat_upper

    statut_diffusion = (
        clean_sirene_str(row.get("statutDiffusionEtablissement")) or "O"
    ).upper()[:1]
    date_debut = parse_date(row.get("dateDebut") or row.get("dateDebutEtablissement"))

    code_commune = (
        _truncate(clean_sirene_str(row.get("codeCommuneEtablissement")), 5) or "UNK00"
    )
    code_pays = _truncate(clean_sirene_str(row.get("codePaysEtrangerEtablissement")), 5)

    coord_x = parse_float(
        row.get("coordonneeLambertAbscisseEtablissement")
        if row.get("coordonneeLambertAbscisseEtablissement") is not None
        else row.get("coordLambertX")
    )
    coord_y = parse_float(
        row.get("coordonneeLambertOrdonneeEtablissement")
        if row.get("coordonneeLambertOrdonneeEtablissement") is not None
        else row.get("coordLambertY")
    )
    if coord_x is not None and abs(coord_x) >= 1e10:
        coord_x = None
    if coord_y is not None and abs(coord_y) >= 1e10:
        coord_y = None
    if coord_x is not None:
        coord_x = round(coord_x, 2)
    if coord_y is not None:
        coord_y = round(coord_y, 2)

    longitude, latitude = lambert93_to_wgs84(coord_x, coord_y)

    code_naf_2025 = _truncate(
        clean_sirene_str(
            row.get("activitePrincipaleNAF25Etablissement")
            or row.get("activitePrincipaleNaf25Etablissement")
            or row.get("codeNaf2025Etablissement")
        ),
        6,
    )

    activite_artisanale = _truncate(
        clean_sirene_str(
            row.get("activitePrincipaleRegistreMetiersEtablissement")
            or row.get("activiteArtisanaleEtablissement")
        ),
        15,
    )

    identifiant_ban = _truncate(
        clean_sirene_str(
            row.get("identifiantAdresseEtablissement")
            or row.get("identifiantAdresseBanEtablissement")
        ),
        30,
    )

    return (
        siret,
        siren,
        nic,
        parse_bool(row.get("etablissementSiege")),
        statut_diffusion,
        etat_administratif,
        parse_date(row.get("dateCreationEtablissement")),
        date_debut,
        parse_timestamp(row.get("dateDernierTraitementEtablissement")),
        _truncate(clean_sirene_str(row.get("enseigne1Etablissement")), 150),
        _truncate(clean_sirene_str(row.get("enseigne2Etablissement")), 150),
        _truncate(clean_sirene_str(row.get("enseigne3Etablissement")), 150),
        _truncate(clean_sirene_str(row.get("denominationUsuelleEtablissement")), 150),
        _normalize_code_naf(row.get("activitePrincipaleEtablissement")),
        _truncate(
            clean_sirene_str(row.get("nomenclatureActivitePrincipaleEtablissement")), 15
        ),
        code_naf_2025,
        activite_artisanale,
        _normalize_tranche_effectifs(row.get("trancheEffectifsEtablissement")),
        _parse_smallint(row.get("anneeEffectifsEtablissement")),
        _truncate(clean_sirene_str(row.get("caractereEmployeurEtablissement")), 1),
        _truncate(clean_sirene_str(row.get("numeroVoieEtablissement")), 20),
        _truncate(clean_sirene_str(row.get("indiceRepetitionEtablissement")), 15),
        _truncate(clean_sirene_str(row.get("typeVoieEtablissement")), 40),
        _truncate(clean_sirene_str(row.get("libelleVoieEtablissement")), 150),
        _truncate(clean_sirene_str(row.get("complementAdresseEtablissement")), 150),
        _truncate(clean_sirene_str(row.get("distributionSpecialeEtablissement")), 50),
        _truncate(clean_sirene_str(row.get("codePostalEtablissement")), 15),
        _truncate(clean_sirene_str(row.get("libelleCommuneEtablissement")), 150),
        code_commune,
        _truncate(clean_sirene_str(row.get("codeCedexEtablissement")), 20),
        _truncate(clean_sirene_str(row.get("libelleCedexEtablissement")), 120),
        code_pays,
        _truncate(
            clean_sirene_str(row.get("libelleCommuneEtrangerEtablissement")), 150
        ),
        identifiant_ban,
        coord_x,
        coord_y,
        longitude,
        latitude,
    )
