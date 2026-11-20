"""Deterministic synthetic INSEE Sirene generator for SQL dumps and offline Parquet/CSV."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
from pathlib import Path
import random
import sys
import zipfile

import pyarrow as pa
import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
SIRENE_DIR = SCRIPT_DIR.parent
SRC_DIR = SIRENE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirene_etl.referentials import (  # noqa: E402
    _CJ_LEVEL1_LABELS,
    _CJ_LEVEL2_LABELS,
    BUILTIN_CATEGORIES_JURIDIQUES,
    BUILTIN_DEPARTEMENTS,
    BUILTIN_NAF,
    BUILTIN_PAYS,
    BUILTIN_REGIONS,
    BUILTIN_TRANCHES_EFFECTIFS,
)
from sirene_etl.transforms import (  # noqa: E402
    ETABLISSEMENT_COLUMNS,
    UNITE_LEGALE_COLUMNS,
    lambert93_to_wgs84,
)

SEED = 20261120
FIXED_TS = "2026-11-20 00:00:00+00"
FIXED_ISO = "2026-11-20T00:00:00Z"
DELTA_ISO = "2026-11-20T10:00:00Z"

TOTAL_UL = 15_000
SOLE_PROPRIETORS_COUNT = 3_000
TOTAL_ETAB = 30_000
TOTAL_PERSONNES = 8_000
NATURAL_OFFICERS_COUNT = 4_500
CORP_OFFICERS_COUNT = 500
TOTAL_ROLES = 12_000
TOTAL_HISTORY = 1_200

DELTA_UL_UPDATES = 200
DELTA_UL_NEW = 50
DELTA_ETAB_UPDATES = 400
DELTA_ETAB_CLOSURES = 150
DELTA_ETAB_NEW = 100

SYNTH_LAST_NAMES = (
    "VALMONT",
    "LUMIERE",
    "VERDIER",
    "DELACROIX",
    "MONTAIGNE",
    "CARPENTIER",
    "MOREAU",
    "LAURENT",
    "ROUSSEAU",
    "GIRARD",
    "MERCIER",
    "BLANCHARD",
    "DUPONT",
    "ACME",
    "FONTAINE",
    "MARCHAND",
)
SYNTH_FIRST_NAMES = (
    "ALICE",
    "BENOIT",
    "CAMILLE",
    "DAVID",
    "ELENA",
    "FABRICE",
    "GAELLE",
    "HENRI",
    "INES",
    "JULIEN",
    "KARINE",
    "LUCAS",
    "MARION",
    "NICOLAS",
    "OLIVIA",
    "PIERRE",
)
SYNTH_COMPANY_PREFIX = (
    "NEXUS",
    "SOLARIS",
    "ATELIER",
    "ALPES",
    "OCCITANIE",
    "HEXAGONE",
    "LUMIERE",
    "AURA",
    "NORDIS",
    "VALLEE",
    "HORIZON",
    "VERITAS",
    "KINETIC",
    "PRISMA",
    "ORION",
    "VECTOR",
)
SYNTH_COMPANY_SECTOR = (
    "SYSTEMS",
    "CONSEIL",
    "LOGISTIQUE",
    "DATA",
    "INGENIERIE",
    "BATIMENT",
    "DIGITAL",
    "ENERGIE",
    "SERVICES",
    "INDUSTRIE",
    "MOBILITE",
    "LABS",
)
VOIE_TYPES = ("RUE", "AVENUE", "BOULEVARD", "PLACE", "IMPASSE", "ALLEE")
VOIE_NAMES = (
    "DE LA REPUBLIQUE",
    "JEAN JAURES",
    "VICTOR HUGO",
    "PASTEUR",
    "GAMBETTA",
    "DES LILAS",
    "DE LA GARE",
    "DU CAPITOLE",
    "DE RIVOLI",
    "DES SCIENCES",
)
ROLE_TYPES_CORP = (
    "GERANT",
    "PRESIDENT",
    "DIRECTEUR_GENERAL",
    "ADMINISTRATEUR",
    "ASSOCIE",
    "ACTIONNAIRE",
    "BENEFICIAIRE_EFFECTIF",
    "AUTRE",
)
CORP_CJ_CODES = ("5710", "5720", "5499", "5498", "5599", "9220")
TRANCHE_ACTIVE = ("00", "01", "02", "03", "11", "12", "21", "22", "31", "41", "51")

EXTRA_PAYS = (
    ("99109", "DE", "DEU", "Allemagne"),
    ("99127", "IT", "ITA", "Italie"),
    ("99131", "BE", "BEL", "Belgique"),
    ("99132", "GB", "GBR", "Royaume-Uni"),
    ("99134", "ES", "ESP", "Espagne"),
    ("99140", "CH", "CHE", "Suisse"),
    ("99217", "JP", "JPN", "Japon"),
    ("99401", "CA", "CAN", "Canada"),
    ("99404", "US", "USA", "États-Unis"),
)

EXTRA_NAF = (
    ("01.11Z", "NAFRev2", "A", "Agriculture, sylviculture et pêche", "01", "Culture et production animale", "01.1", "Cultures non permanentes", "01.11", "Culture de céréales", "Culture de céréales (à l'exception du riz)"),
    ("10.71C", "NAFRev2", "C", "Industrie manufacturière", "10", "Industries alimentaires", "10.7", "Fabrication de produits de boulangerie-pâtisserie", "10.71", "Boulangerie et boulangerie-pâtisserie", "Boulangerie et boulangerie-pâtisserie"),
    ("35.11Z", "NAFRev2", "D", "Production et distribution d'électricité", "35", "Production et distribution d'électricité", "35.1", "Production d'électricité", "35.11", "Production d'électricité", "Production d'électricité"),
    ("72.2Z", "HIST", None, None, None, None, None, None, None, None, "Historical NAF1993 code (72.2Z)"),
    ("99.99Z", "HIST", None, None, None, None, None, None, None, None, "Historical unlisted NAF code (99.99Z)"),
)

ANCHOR_COMMUNES = (
    ("75101", "75", "ARM", "PARIS 1ER ARRONDISSEMENT", "Paris 1er Arrondissement", True, "75001", 652469.02, 6862035.26),
    ("75108", "75", "ARM", "PARIS 8E ARRONDISSEMENT", "Paris 8e Arrondissement", True, "75008", 649400.00, 6864100.00),
    ("92050", "92", "COM", "NANTERRE", "Nanterre", True, "92000", 642650.00, 6866100.00),
    ("69123", "69", "COM", "LYON", "Lyon", True, "69001", 842550.00, 6520100.00),
    ("38185", "38", "COM", "GRENOBLE", "Grenoble", True, "38000", 914400.00, 6457900.00),
    ("31555", "31", "COM", "TOULOUSE", "Toulouse", True, "31000", 574359.00, 6279660.00),
    ("13055", "13", "COM", "MARSEILLE", "Marseille", True, "13001", 892200.00, 6246700.00),
    ("33063", "33", "COM", "BORDEAUX", "Bordeaux", True, "33000", 418100.00, 6421100.00),
    ("59350", "59", "COM", "LILLE", "Lille", True, "59000", 704500.00, 7059300.00),
    ("44109", "44", "COM", "NANTES", "Nantes", True, "44000", 355100.00, 6688300.00),
    ("67482", "67", "COM", "STRASBOURG", "Strasbourg", True, "67000", 1050600.00, 6840400.00),
    ("35238", "35", "COM", "RENNES", "Rennes", True, "35000", 353800.00, 6789200.00),
    ("34172", "34", "COM", "MONTPELLIER", "Montpellier", True, "34000", 770700.00, 6279400.00),
    ("06088", "06", "COM", "NICE", "Nice", True, "06000", 1042400.00, 6300200.00),
)

HIST_COMMUNES = (
    ("75999", "75", "HIST", "ANCIEN ARRONDISSEMENT PARIS", "Ancien arrondissement Paris", False),
    ("69999", "69", "HIST", "ANCIENNE COMMUNE RHONE", "Ancienne commune Rhône", False),
    ("31999", "31", "HIST", "ANCIENNE COMMUNE GARONNE", "Ancienne commune Haute-Garonne", False),
)


def _pg_copy_cell(val: object) -> str:
    """Format a Python scalar into PostgreSQL text COPY FROM STDIN representation."""
    if val is None:
        return r"\N"
    if isinstance(val, bool):
        return "t" if val else "f"
    if isinstance(val, dt.datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S+00")
    if isinstance(val, dt.date):
        return val.isoformat()
    text = str(val)
    return (
        text.replace("\\", "\\\\")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _write_copy_block(
    handle: io.TextIOBase,
    table: str,
    columns: tuple[str, ...],
    rows: list[tuple[object, ...]],
) -> None:
    """Write a COPY table (cols) FROM stdin block terminated by backslash-dot."""
    cols_sql = ", ".join(columns)
    handle.write(f"COPY {table} ({cols_sql}) FROM stdin;\n")
    for row in rows:
        handle.write("\t".join(_pg_copy_cell(v) for v in row) + "\n")
    handle.write("\\.\n\n")


def _build_referentials() -> dict[str, list[tuple[object, ...]]]:
    """Build deterministic data for all 7 referential lookup tables."""
    regions = list(BUILTIN_REGIONS)
    departements = list(BUILTIN_DEPARTEMENTS)

    communes: list[tuple[object, ...]] = [
        ("UNK00", "UNK", "COM", "UNKNOWN", "Unknown or unspecified municipality", False)
    ]
    seen_communes = {"UNK00"}
    commune_geo: list[tuple[str, str, str, float, float]] = []

    for code, dep, ctype, ncc, lib, active, cp, lx, ly in ANCHOR_COMMUNES:
        communes.append((code, dep, ctype, ncc, lib, active))
        seen_communes.add(code)
        commune_geo.append((code, lib, cp, lx, ly))

    for code, dep, ctype, ncc, lib, active in HIST_COMMUNES:
        communes.append((code, dep, ctype, ncc, lib, active))
        seen_communes.add(code)

    # Generate deterministic representative communes across all departments (~500 total).
    for dep_row in departements:
        dep_code = dep_row[0]
        if dep_code in {"UNK", "99", "20"}:
            continue
        for idx in range(1, 6):
            if len(dep_code) == 2:
                com_code = f"{dep_code}{idx:03d}"
                cp = f"{dep_code}{idx:02d}0"
            else:
                com_code = f"{dep_code}{idx:02d}"[:5]
                cp = f"{dep_code[:3]}{idx:02d}"
            if com_code in seen_communes:
                continue
            seen_communes.add(com_code)
            lib = f"Commune Synth {dep_code}-{idx:02d}"
            communes.append((com_code, dep_code, "COM", lib.upper(), lib, True))
            # Assign plausible metropolitan Lambert-93 offsets.
            lx = 500_000.0 + ((hashlib.md5(com_code.encode()).digest()[0] % 50) * 8_000.0)
            ly = 6_350_000.0 + ((hashlib.md5(com_code.encode()).digest()[1] % 50) * 12_000.0)
            commune_geo.append((com_code, lib, cp, lx, ly))

    pays = list(BUILTIN_PAYS) + list(EXTRA_PAYS)

    naf_rows: list[tuple[object, ...]] = []
    seen_naf: set[str] = set()
    for code, nom, sec, lsec, div, ldiv, lsc in BUILTIN_NAF:
        grp = code[:4] if nom != "UNKNOWN" and len(code) >= 4 else None
        cls = code[:5] if nom != "UNKNOWN" and len(code) >= 5 else None
        naf_rows.append((code, nom, sec, lsec, div, ldiv, grp, ldiv, cls, lsc, lsc))
        seen_naf.add(code)
    for row in EXTRA_NAF:
        if row[0] not in seen_naf:
            naf_rows.append(row)
            seen_naf.add(row[0])

    cj_rows: list[tuple[object, ...]] = []
    for code, lib in BUILTIN_CATEGORIES_JURIDIQUES:
        l1 = code[:1]
        l2 = code[:2]
        cj_rows.append(
            (
                code,
                l1,
                _CJ_LEVEL1_LABELS.get(l1),
                l2,
                _CJ_LEVEL2_LABELS.get(l2),
                lib,
            )
        )

    tranches = list(BUILTIN_TRANCHES_EFFECTIFS)
    return {
        "ref_regions": regions,
        "ref_departements": departements,
        "ref_communes": communes,
        "ref_pays": pays,
        "ref_naf": naf_rows,
        "ref_categories_juridiques": cj_rows,
        "ref_tranches_effectifs": tranches,
        "_commune_geo": commune_geo,  # type: ignore[dict-item]
    }


def _generate_dataset() -> tuple[
    dict[str, list[tuple[object, ...]]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    """Generate deterministic SQL tuples and matching raw INSEE Parquet/CSV records."""
    rng = random.Random(SEED)
    refs = _build_referentials()
    commune_geo: list[tuple[str, str, str, float, float]] = refs.pop("_commune_geo")  # type: ignore[assignment]
    naf_active = [r[0] for r in refs["ref_naf"] if r[1] == "NAFRev2"]
    naf_div62 = [c for c in naf_active if str(c).startswith("62.")]
    foreign_pays = [r for r in refs["ref_pays"] if r[0] not in {"UNK", "99100"}]

    ul_sql_rows: list[tuple[object, ...]] = []
    ul_parquet_rows: list[dict[str, object]] = []
    ul_meta: list[dict[str, object]] = []

    base_start = dt.date(1955, 1, 1)
    base_span_days = (dt.date(2026, 6, 30) - base_start).days

    # Sole proprietors: 100 in first 500 (indices 400..499) + 2,900 at 1000..3899.
    sole_indices = set(range(400, 500)) | set(range(1000, 3900))
    assert len(sole_indices) == SOLE_PROPRIETORS_COUNT

    for idx in range(TOTAL_UL):
        siren = f"{900_000_001 + idx:09d}"
        is_sole = idx in sole_indices
        is_anchor = idx < 3
        # Keep first 400 rows active non-ND for delta tests; keep sole proprietors non-ND.
        if idx < 400 or is_sole:
            etat = "A" if (idx < 500 or rng.random() < 0.85) else "C"
            statut_diff = "O"
        else:
            etat = "A" if rng.random() < 0.85 else "C"
            statut_diff = "P" if (idx >= 500 and rng.random() < 0.02) else "O"

        d_create = base_start + dt.timedelta(days=rng.randint(0, base_span_days))
        d_debut = min(dt.date(2026, 11, 1), d_create + dt.timedelta(days=rng.randint(0, 365)))
        ts_trait = dt.datetime(2025, 1, 1, 8, 0, tzinfo=dt.timezone.utc) + dt.timedelta(
            days=rng.randint(0, 650)
        )
        ts_iso = ts_trait.strftime("%Y-%m-%dT%H:%M:%SZ")

        nic_siege = f"{11 + (idx % 80):05d}"
        is_orphan_placeholder = 14_990 <= idx < 15_000

        if is_orphan_placeholder:
            statut_diff = "P"
            etat = "C"
            denom = None
            sigle = None
            nom_n = None
            nom_u = None
            prenom_u = None
            p1 = p2 = None
            prenoms = None
            sexe = None
            cj = "0000"
            naf = "00.00Z"
            nomenclature = "NAFRev2"
            tranche = "UN"
            annee_eff = None
            cat_ent = None
            annee_cat = None
            ess = None
            mission = None
            emp = "N"
        elif idx == 0:
            denom = "ACME TECHNOLOGIE"
            sigle = "ACME"
            nom_n = nom_u = prenom_u = p1 = p2 = prenoms = sexe = None
            cj = "5710"
            naf = "62.01Z"
            nomenclature = "NAFRev2"
            tranche = "21"
            annee_eff = 2024
            cat_ent = "PME"
            annee_cat = 2024
            ess = "N"
            mission = "O"
            emp = "O"
        elif idx == 1:
            denom = "BOULANGERIE DUPONT"
            sigle = "BDUP"
            nom_n = nom_u = prenom_u = p1 = p2 = prenoms = sexe = None
            cj = "5499"
            naf = "10.71C"
            nomenclature = "NAFRev2"
            tranche = "02"
            annee_eff = 2024
            cat_ent = "PME"
            annee_cat = 2024
            ess = "N"
            mission = "N"
            emp = "O"
        elif idx == 2:
            denom = "AURA DATA SERVICES"
            sigle = "ADS"
            nom_n = nom_u = prenom_u = p1 = p2 = prenoms = sexe = None
            cj = "5710"
            naf = "62.02A"
            nomenclature = "NAFRev2"
            tranche = "12"
            annee_eff = 2024
            cat_ent = "PME"
            annee_cat = 2024
            ess = "O"
            mission = "O"
            emp = "O"
        elif is_sole:
            cj = "1000"
            denom = None
            sigle = None
            if statut_diff == "P":
                nom_n = nom_u = prenom_u = p1 = p2 = prenoms = sexe = None
            else:
                nom_n = f"{rng.choice(SYNTH_LAST_NAMES)}_{idx:04d}"
                nom_u = None
                p1 = rng.choice(SYNTH_FIRST_NAMES)
                p2 = rng.choice(SYNTH_FIRST_NAMES) if idx % 3 == 0 else None
                prenom_u = p1
                prenoms = f"{p1} {p2}" if p2 else p1
                sexe = "M" if idx % 2 == 0 else "F"
            naf = rng.choice(naf_div62 if idx % 5 == 0 else naf_active)
            nomenclature = "NAFRev2"
            tranche = "NN" if idx % 2 == 0 else rng.choice(("00", "01", "02"))
            annee_eff = 2024 if tranche != "NN" else None
            cat_ent = "PME" if idx % 4 == 0 else None
            annee_cat = 2024 if cat_ent else None
            ess = "N"
            mission = "N"
            emp = "O" if tranche not in {"NN", "00"} else "N"
        else:
            cj = rng.choice(CORP_CJ_CODES)
            if idx % 250 == 0 and idx >= 500:
                cj = "0000"
            if statut_diff == "P":
                denom = None
                sigle = None
            else:
                denom = (
                    f"{rng.choice(SYNTH_COMPANY_PREFIX)} "
                    f"{rng.choice(SYNTH_COMPANY_SECTOR)} {idx:05d}"
                )
                sigle = f"SY{idx:04d}" if idx % 4 == 0 else None
            nom_n = nom_u = prenom_u = p1 = p2 = prenoms = sexe = None
            if idx >= 500 and idx % 300 == 0:
                naf = "99.99Z"
                nomenclature = "HIST"
            else:
                naf = rng.choice(naf_div62 if idx % 6 == 0 else naf_active)
                nomenclature = "NAFRev2"
            if statut_diff == "P" and idx % 3 == 0:
                tranche = "UN"
            elif idx % 4 == 0:
                tranche = "NN"
            else:
                tranche = rng.choice(TRANCHE_ACTIVE)
            annee_eff = 2024 if tranche not in {"NN", "UN"} else None
            cat_ent = rng.choices(("PME", "ETI", "GE", None), weights=(55, 15, 5, 25))[0]
            annee_cat = 2024 if cat_ent else None
            ess = "O" if (cj == "9220" or rng.random() < 0.05) else "N"
            mission = "O" if (ess == "O" and rng.random() < 0.4) or rng.random() < 0.02 else "N"
            emp = "O" if tranche not in {"NN", "00", "UN"} else "N"

        assoc_id = f"W751{idx:06d}" if cj == "9220" else None

        ul_sql_rows.append(
            (
                siren,
                statut_diff,
                False,
                etat,
                d_create,
                d_debut,
                ts_trait,
                denom,
                sigle,
                None,
                None,
                None,
                nom_n,
                nom_u,
                prenom_u,
                prenoms,
                None,
                sexe,
                assoc_id,
                cat_ent,
                annee_cat,
                cj,
                naf,
                nomenclature,
                None,
                tranche,
                annee_eff,
                nic_siege,
                ess,
                mission,
                emp,
                FIXED_TS,
            )
        )

        def _nd(val: object) -> object:
            return "[ND]" if (statut_diff == "P" and val is None and not is_orphan_placeholder) else val

        ul_parquet_rows.append(
            {
                "siren": siren,
                "statutDiffusionUniteLegale": statut_diff,
                "unitePurgeeUniteLegale": False,
                "etatAdministratifUniteLegale": etat,
                "dateCreationUniteLegale": d_create.isoformat(),
                "dateDebut": d_debut.isoformat(),
                "dateDernierTraitementUniteLegale": ts_iso,
                "denominationUniteLegale": "[ND]" if (statut_diff == "P" and not is_sole and not is_orphan_placeholder) else denom,
                "sigleUniteLegale": sigle,
                "denominationUsuelle1UniteLegale": None,
                "denominationUsuelle2UniteLegale": None,
                "denominationUsuelle3UniteLegale": None,
                "nomUniteLegale": "[ND]" if (statut_diff == "P" and is_sole) else nom_n,
                "nomUsageUniteLegale": nom_u,
                "prenomUsuelUniteLegale": "[ND]" if (statut_diff == "P" and is_sole) else prenom_u,
                "prenom1UniteLegale": "[ND]" if (statut_diff == "P" and is_sole) else p1,
                "prenom2UniteLegale": p2,
                "prenom3UniteLegale": None,
                "prenom4UniteLegale": None,
                "pseudonymeUniteLegale": None,
                "sexeUniteLegale": sexe,
                "identifiantAssociationUniteLegale": assoc_id,
                "categorieEntreprise": cat_ent,
                "anneeCategorieEntreprise": annee_cat,
                "categorieJuridiqueUniteLegale": cj,
                "activitePrincipaleUniteLegale": naf,
                "nomenclatureActivitePrincipaleUniteLegale": nomenclature,
                "activitePrincipaleNAF25UniteLegale": None,
                "trancheEffectifsUniteLegale": "[ND]" if (statut_diff == "P" and tranche == "NN") else tranche,
                "anneeEffectifsUniteLegale": annee_eff,
                "nicSiegeUniteLegale": nic_siege,
                "economieSocialeSolidaireUniteLegale": ess,
                "societeMissionUniteLegale": mission,
                "caractereEmployeurUniteLegale": emp,
            }
        )
        ul_meta.append(
            {
                "idx": idx,
                "siren": siren,
                "is_sole": is_sole,
                "etat": etat,
                "statut_diff": statut_diff,
                "d_create": d_create,
                "d_debut": d_debut,
                "ts_trait": ts_trait,
                "ts_iso": ts_iso,
                "denom": denom,
                "nom_n": nom_n,
                "prenom_u": prenom_u,
                "prenoms": prenoms,
                "sexe": sexe,
                "cj": cj,
                "naf": naf,
                "tranche": tranche,
                "nic_siege": nic_siege,
                "is_anchor": is_anchor,
                "is_orphan_placeholder": is_orphan_placeholder,
            }
        )

    # Establishments: 15,000 HQ + 15,000 secondary = 30,000 total.
    etab_sql_rows: list[tuple[object, ...]] = []
    etab_parquet_rows: list[dict[str, object]] = []
    etab_sirets_by_ul: dict[int, list[str]] = {idx: [] for idx in range(TOTAL_UL)}
    etab_records_meta: list[tuple[str, str, dt.date]] = []

    def _make_etab(
        *,
        ul_idx: int,
        nic: str,
        siege: bool,
        branch_seq: int,
        force_foreign: bool = False,
        force_hist_commune: bool = False,
        force_hist_naf: bool = False,
    ) -> None:
        meta = ul_meta[ul_idx]
        siren = str(meta["siren"])
        siret = f"{siren}{nic}"
        statut_diff = str(meta["statut_diff"]) if siege else ("P" if rng.random() < 0.02 else "O")
        if ul_idx < 400 and siege:
            etat = "A"
            statut_diff = "O"
        elif meta["etat"] == "C":
            etat = "F"
        else:
            etat = "A" if rng.random() < 0.88 else "F"

        d_create = meta["d_create"]
        d_debut = meta["d_debut"]
        ts_trait = meta["ts_trait"]
        ts_iso = str(meta["ts_iso"])

        if ul_idx == 0 and siege:
            com_code, lib_com, cp, lx, ly = commune_geo[0]  # Paris 75101
            naf = "62.01Z"
            nomenclature = "NAFRev2"
            enseigne = "ACME TECHNOLOGIE HQ"
        elif ul_idx == 1 and siege:
            com_code, lib_com, cp, lx, ly = commune_geo[0]  # Paris 75101
            naf = "10.71C"
            nomenclature = "NAFRev2"
            enseigne = "BOULANGERIE DUPONT PARIS"
        elif ul_idx == 2 and siege:
            com_code, lib_com, cp, lx, ly = commune_geo[3]  # Lyon 69123 (region 84)
            naf = "62.02A"
            nomenclature = "NAFRev2"
            enseigne = "AURA DATA LYON"
        else:
            naf = "99.99Z" if force_hist_naf else str(meta["naf"])
            nomenclature = "HIST" if force_hist_naf else ("HIST" if naf in {"99.99Z", "72.2Z"} else "NAFRev2")
            enseigne = (
                None
                if statut_diff == "P" or meta["is_orphan_placeholder"]
                else (
                    f"{meta['denom'] or 'ETAB ' + str(meta['nom_n'] or siren)}"
                    if siege
                    else f"AGENCE {siren[-4:]}-{branch_seq:02d}"
                )
            )
            if force_foreign:
                com_code = "UNK00"
                lib_com = None
                cp = None
                lx = ly = None
            elif force_hist_commune:
                com_code, _, _, _, lib_com, _ = rng.choice(HIST_COMMUNES)
                cp = com_code
                lx = ly = None
            elif statut_diff == "P" or meta["is_orphan_placeholder"]:
                com_code = "UNK00"
                lib_com = None
                cp = None
                lx = ly = None
            else:
                geo = commune_geo[0] if (ul_idx < 50 and siege) else (commune_geo[5] if 50 <= ul_idx < 80 and siege else rng.choice(commune_geo))
                com_code, lib_com, cp, base_x, base_y = geo
                jitter_x = ((ul_idx * 17 + branch_seq * 31) % 2000) - 1000
                jitter_y = ((ul_idx * 23 + branch_seq * 19) % 2000) - 1000
                lx = round(base_x + jitter_x, 2)
                ly = round(base_y + jitter_y, 2)

        if force_foreign:
            pays_row = rng.choice(foreign_pays)
            code_pays = str(pays_row[0])
            lib_com_ext = f"CITY_{pays_row[1]}_{ul_idx:04d}"
        else:
            code_pays = None
            lib_com_ext = None

        lon, lat = lambert93_to_wgs84(lx, ly)
        lx_sql = round(lx, 2) if lx is not None else None
        ly_sql = round(ly, 2) if ly is not None else None
        lon_sql = round(lon, 6) if lon is not None else None
        lat_sql = round(lat, 6) if lat is not None else None
        tranche = str(meta["tranche"])
        annee_eff = 2024 if tranche not in {"NN", "UN"} else None
        emp = "O" if tranche not in {"NN", "00", "UN"} else "N"

        masked_addr = statut_diff == "P" or meta["is_orphan_placeholder"] or force_foreign
        num_voie = None if masked_addr else str(1 + ((ul_idx + branch_seq) % 180))
        type_voie = None if masked_addr else rng.choice(VOIE_TYPES)
        lib_voie = None if masked_addr else rng.choice(VOIE_NAMES)
        ban_id = None if masked_addr else f"{com_code}_{ul_idx:05d}_{branch_seq:02d}"

        etab_sql_rows.append(
            (
                siret,
                siren,
                nic,
                siege,
                statut_diff,
                etat,
                d_create,
                d_debut,
                ts_trait,
                enseigne[:150] if enseigne else None,
                None,
                None,
                None,
                naf,
                nomenclature,
                None,
                None,
                tranche,
                annee_eff,
                emp,
                num_voie,
                None,
                type_voie,
                lib_voie,
                None,
                None,
                cp,
                lib_com,
                com_code,
                None,
                None,
                code_pays,
                lib_com_ext,
                ban_id,
                lx_sql,
                ly_sql,
                lon_sql,
                lat_sql,
                FIXED_TS,
            )
        )

        etab_parquet_rows.append(
            {
                "siret": siret,
                "siren": siren,
                "nic": nic,
                "etablissementSiege": siege,
                "statutDiffusionEtablissement": statut_diff,
                "etatAdministratifEtablissement": etat,
                "dateCreationEtablissement": d_create.isoformat(),
                "dateDebut": d_debut.isoformat(),
                "dateDernierTraitementEtablissement": ts_iso,
                "enseigne1Etablissement": "[ND]" if (statut_diff == "P" and not meta["is_orphan_placeholder"]) else (enseigne[:150] if enseigne else None),
                "enseigne2Etablissement": None,
                "enseigne3Etablissement": None,
                "denominationUsuelleEtablissement": None,
                "activitePrincipaleEtablissement": naf,
                "nomenclatureActivitePrincipaleEtablissement": nomenclature,
                "activitePrincipaleNAF25Etablissement": None,
                "activitePrincipaleRegistreMetiersEtablissement": None,
                "trancheEffectifsEtablissement": "[ND]" if (statut_diff == "P" and tranche == "NN") else tranche,
                "anneeEffectifsEtablissement": annee_eff,
                "caractereEmployeurEtablissement": emp,
                "numeroVoieEtablissement": num_voie,
                "indiceRepetitionEtablissement": None,
                "typeVoieEtablissement": type_voie,
                "libelleVoieEtablissement": "[ND]" if (statut_diff == "P" and not meta["is_orphan_placeholder"]) else lib_voie,
                "complementAdresseEtablissement": None,
                "distributionSpecialeEtablissement": None,
                "codePostalEtablissement": "[ND]" if (statut_diff == "P" and not meta["is_orphan_placeholder"]) else cp,
                "libelleCommuneEtablissement": "[ND]" if (statut_diff == "P" and not meta["is_orphan_placeholder"]) else lib_com,
                "codeCommuneEtablissement": "[ND]" if (statut_diff == "P" and not meta["is_orphan_placeholder"]) else com_code,
                "codeCedexEtablissement": None,
                "libelleCedexEtablissement": None,
                "codePaysEtrangerEtablissement": code_pays,
                "libelleCommuneEtrangerEtablissement": lib_com_ext,
                "identifiantAdresseEtablissement": ban_id,
                "coordonneeLambertAbscisseEtablissement": "[ND]" if statut_diff == "P" else (f"{lx:.2f}" if lx is not None else None),
                "coordonneeLambertOrdonneeEtablissement": "[ND]" if statut_diff == "P" else (f"{ly:.2f}" if ly is not None else None),
            }
        )
        etab_sirets_by_ul[ul_idx].append(siret)
        etab_records_meta.append((siret, etat, d_debut))

    # 15,000 HQ rows first (indices 0..14999) so limit_rows=500 aligns with UL 0..499.
    for ul_idx in range(TOTAL_UL):
        _make_etab(
            ul_idx=ul_idx,
            nic=str(ul_meta[ul_idx]["nic_siege"]),
            siege=True,
            branch_seq=0,
            force_hist_commune=(600 <= ul_idx < 640),
            force_hist_naf=(640 <= ul_idx < 680),
        )

    # Distribute exactly 15,000 secondary establishments:
    # ~400 multi-branch networks (5-25 branches) + remaining 1-2 branches across others.
    secondary_plan: list[tuple[int, int]] = []
    remaining = TOTAL_ETAB - TOTAL_UL
    network_idx = 0
    for ul_idx in range(10, 500):
        if ul_idx in sole_indices or remaining <= 0:
            continue
        count = min(remaining, 5 + ((ul_idx * 7) % 21))
        secondary_plan.append((ul_idx, count))
        remaining -= count
        network_idx += 1
        if remaining <= 4_000:
            break

    cursor_ul = 500
    while remaining > 0:
        if cursor_ul not in sole_indices and cursor_ul < TOTAL_UL - 20:
            take = min(remaining, 2 if cursor_ul % 3 == 0 else 1)
            secondary_plan.append((cursor_ul, take))
            remaining -= take
        cursor_ul = 500 if cursor_ul + 1 >= TOTAL_UL - 20 else cursor_ul + 1

    foreign_budget = 200
    branch_counter: dict[int, int] = {}
    for ul_idx, count in secondary_plan:
        for _ in range(count):
            seq = branch_counter.get(ul_idx, 0) + 1
            branch_counter[ul_idx] = seq
            nic = f"{200 + seq:05d}"
            if nic == ul_meta[ul_idx]["nic_siege"]:
                nic = f"{900 + seq:05d}"
            use_foreign = foreign_budget > 0 and ul_idx >= 500
            if use_foreign:
                foreign_budget -= 1
            _make_etab(
                ul_idx=ul_idx,
                nic=nic,
                siege=False,
                branch_seq=seq,
                force_foreign=use_foreign,
            )

    assert len(etab_sql_rows) == TOTAL_ETAB

    # Build 8,000 personnes: 3,000 EI + 4,500 natural officers + 500 corporate officers.
    personnes_rows: list[tuple[object, ...]] = []
    sole_personne_id: dict[int, int] = {}
    pid = 1

    for ul_idx in sorted(sole_indices):
        meta = ul_meta[ul_idx]
        siren = str(meta["siren"])
        personnes_rows.append(
            (
                pid,
                "PHYSIQUE",
                meta["nom_n"] or f"MASKED_{siren}",
                meta["prenoms"],
                meta["prenom_u"],
                meta["sexe"],
                None,
                None,
                f"EI:{siren}",
                FIXED_TS,
                FIXED_TS,
            )
        )
        sole_personne_id[ul_idx] = pid
        pid += 1

    for idx in range(NATURAL_OFFICERS_COUNT):
        if idx == 0:
            nom = "ACME"
            prenom_u = "TECHNOLOGIE"
            prenoms = "TECHNOLOGIE ALAIN"
        elif idx == 1:
            nom = "DUPONT"
            prenom_u = "CLAIRE"
            prenoms = "CLAIRE MARIE"
        else:
            nom = f"{rng.choice(SYNTH_LAST_NAMES)}_{idx:04d}"
            prenom_u = rng.choice(SYNTH_FIRST_NAMES)
            prenoms = f"{prenom_u} {rng.choice(SYNTH_FIRST_NAMES)}"
        sexe = "M" if idx % 2 == 0 else "F"
        bdate = dt.date(1955, 1, 1) + dt.timedelta(days=rng.randint(0, 16_000))
        personnes_rows.append(
            (
                pid,
                "PHYSIQUE",
                nom,
                prenoms,
                prenom_u,
                sexe,
                bdate,
                None,
                f"NAT:{idx:06d}",
                FIXED_TS,
                FIXED_TS,
            )
        )
        pid += 1

    corp_pool = [i for i in range(TOTAL_UL - 20) if i not in sole_indices]
    for idx in range(CORP_OFFICERS_COUNT):
        holding_idx = corp_pool[(idx * 13) % len(corp_pool)]
        holding_meta = ul_meta[holding_idx]
        holding_siren = str(holding_meta["siren"])
        personnes_rows.append(
            (
                pid,
                "MORALE",
                holding_meta["denom"] or f"HOLDING_{holding_siren}",
                None,
                None,
                None,
                None,
                holding_siren,
                f"MOR:{holding_siren}:{idx:04d}",
                FIXED_TS,
                FIXED_TS,
            )
        )
        pid += 1

    assert len(personnes_rows) == TOTAL_PERSONNES

    # Build 12,000 roles_entreprises: 3,000 EI + 9,000 corporate mandates.
    roles_rows: list[tuple[object, ...]] = []
    seen_role_keys: set[tuple[str, int, str, dt.date | None]] = set()
    rid = 1

    for ul_idx in sorted(sole_indices):
        meta = ul_meta[ul_idx]
        siren = str(meta["siren"])
        p_id = sole_personne_id[ul_idx]
        d_start = meta["d_create"]
        roles_rows.append(
            (
                rid,
                siren,
                p_id,
                "ENTREPRENEUR_INDIVIDUEL",
                "Entrepreneur individuel",
                None,
                None,
                d_start,
                None,
                meta["etat"] == "A",
                "SIRENE",
            )
        )
        seen_role_keys.add((siren, p_id, "ENTREPRENEUR_INDIVIDUEL", d_start))  # type: ignore[arg-type]
        rid += 1

    # Ensure anchor companies 0, 1, 2 get explicit active officers first.
    anchor_assignments = [
        (0, SOLE_PROPRIETORS_COUNT + 1, "PRESIDENT", "President", 60.0, 60.0),
        (1, SOLE_PROPRIETORS_COUNT + 2, "GERANT", "Gerant majoritaire", 55.0, 55.0),
        (2, SOLE_PROPRIETORS_COUNT + 3, "DIRECTEUR_GENERAL", "Directeur general", 25.0, 25.0),
    ]
    for ul_idx, p_id, rtype, detail, det, vote in anchor_assignments:
        siren = str(ul_meta[ul_idx]["siren"])
        d_start = ul_meta[ul_idx]["d_create"]
        roles_rows.append(
            (rid, siren, p_id, rtype, detail, det, vote, d_start, None, True, "RNE")
        )
        seen_role_keys.add((siren, p_id, rtype, d_start))  # type: ignore[arg-type]
        rid += 1

    officer_pids = list(range(SOLE_PROPRIETORS_COUNT + 1, TOTAL_PERSONNES + 1))
    corp_idx_cursor = 0
    while len(roles_rows) < TOTAL_ROLES:
        ul_idx = corp_pool[corp_idx_cursor % len(corp_pool)]
        corp_idx_cursor += 1
        meta = ul_meta[ul_idx]
        siren = str(meta["siren"])
        p_id = officer_pids[(rid * 7 + corp_idx_cursor) % len(officer_pids)]
        rtype = ROLE_TYPES_CORP[(rid + corp_idx_cursor) % len(ROLE_TYPES_CORP)]
        d_start = meta["d_create"]
        key = (siren, p_id, rtype, d_start)
        if key in seen_role_keys:
            continue
        seen_role_keys.add(key)  # type: ignore[arg-type]
        is_active = meta["etat"] == "A"
        det = round(rng.choice((10.0, 25.0, 50.0, 100.0)), 2) if rtype in {"ASSOCIE", "ACTIONNAIRE", "BENEFICIAIRE_EFFECTIF"} else None
        vote = det
        roles_rows.append(
            (
                rid,
                siren,
                p_id,
                rtype,
                rtype.replace("_", " ").title(),
                det,
                vote,
                d_start,
                None if is_active else dt.date(2025, 12, 31),
                is_active,
                "RNE",
            )
        )
        rid += 1

    assert len(roles_rows) == TOTAL_ROLES

    # Build 4 baseline etl_logs + 1,200 etablissements_historique_etat.
    etl_logs_rows: list[tuple[object, ...]] = [
        (1, "REFERENTIALS", "ALL", "ref-2026", "https://www.insee.fr/", "cog_2026_synthetic", "2026", "sha256", "0" * 64, 600, 600, 0, "SUCCESS", FIXED_TS, FIXED_TS, None, "{}"),
        (2, "FULL_IMPORT", "UNITE_LEGALE", "ul-synth", "offline://synthetic", "StockUniteLegale_synthetic.parquet", "2026-11-20", "sha256", "1" * 64, TOTAL_UL, TOTAL_UL, 0, "SUCCESS", FIXED_TS, FIXED_TS, None, "{}"),
        (3, "FULL_IMPORT", "ETABLISSEMENT", "etab-synth", "offline://synthetic", "StockEtablissement_synthetic.parquet", "2026-11-20", "sha256", "2" * 64, TOTAL_ETAB, TOTAL_ETAB, 0, "SUCCESS", FIXED_TS, FIXED_TS, None, "{}"),
        (4, "INCREMENTAL_IMPORT", "ETABLISSEMENT", "etab-hist-synth", "offline://synthetic", "DeltaEtablissement_synthetic.parquet", "2026-11-20", "sha256", "3" * 64, TOTAL_HISTORY, 0, TOTAL_HISTORY, "SUCCESS", FIXED_TS, FIXED_TS, None, '{"state_transitions": 1200}'),
    ]

    history_rows: list[tuple[object, ...]] = []
    for hid in range(1, TOTAL_HISTORY + 1):
        # Pick closed establishments for A->F and active establishments for F->A.
        siret, cur_etat, d_eff = etab_records_meta[(hid * 19) % len(etab_records_meta)]
        if cur_etat == "F":
            old_state, new_state = "A", "F"
        else:
            old_state, new_state = "F", "A"
        history_rows.append((hid, siret, old_state, new_state, d_eff, FIXED_TS, 4))

    assert len(history_rows) == TOTAL_HISTORY

    sql_tables: dict[str, list[tuple[object, ...]]] = {
        **refs,
        "unites_legales": ul_sql_rows,
        "etablissements": etab_sql_rows,
        "personnes": personnes_rows,
        "roles_entreprises": roles_rows,
        "etablissements_historique_etat": history_rows,
        "etl_logs": etl_logs_rows,
    }

    # Build Delta Parquet & CSV datasets:
    # 200 updates to UL 0..199 + 50 new UL (900015001..900015050).
    delta_ul_rows: list[dict[str, object]] = []
    for idx in range(DELTA_UL_UPDATES):
        row = dict(ul_parquet_rows[idx])
        row["dateDernierTraitementUniteLegale"] = DELTA_ISO
        row["dateDebut"] = "2026-11-20"
        if idx > 2:
            row["denominationUniteLegale"] = f"{row['denominationUniteLegale']} UPDATED"
        else:
            row["trancheEffectifsUniteLegale"] = "22"
        delta_ul_rows.append(row)

    for new_i in range(DELTA_UL_NEW):
        siren = f"{900_015_001 + new_i:09d}"
        delta_ul_rows.append(
            {
                "siren": siren,
                "statutDiffusionUniteLegale": "O",
                "unitePurgeeUniteLegale": False,
                "etatAdministratifUniteLegale": "A",
                "dateCreationUniteLegale": "2026-11-20",
                "dateDebut": "2026-11-20",
                "dateDernierTraitementUniteLegale": DELTA_ISO,
                "denominationUniteLegale": f"NOUVELLE SYNTH {new_i + 1:03d}",
                "sigleUniteLegale": None,
                "denominationUsuelle1UniteLegale": None,
                "denominationUsuelle2UniteLegale": None,
                "denominationUsuelle3UniteLegale": None,
                "nomUniteLegale": None,
                "nomUsageUniteLegale": None,
                "prenomUsuelUniteLegale": None,
                "prenom1UniteLegale": None,
                "prenom2UniteLegale": None,
                "prenom3UniteLegale": None,
                "prenom4UniteLegale": None,
                "pseudonymeUniteLegale": None,
                "sexeUniteLegale": None,
                "identifiantAssociationUniteLegale": None,
                "categorieEntreprise": "PME",
                "anneeCategorieEntreprise": 2026,
                "categorieJuridiqueUniteLegale": "5710",
                "activitePrincipaleUniteLegale": "62.01Z",
                "nomenclatureActivitePrincipaleUniteLegale": "NAFRev2",
                "activitePrincipaleNAF25UniteLegale": None,
                "trancheEffectifsUniteLegale": "01",
                "anneeEffectifsUniteLegale": 2026,
                "nicSiegeUniteLegale": "00014",
                "economieSocialeSolidaireUniteLegale": "N",
                "societeMissionUniteLegale": "N",
                "caractereEmployeurUniteLegale": "O",
            }
        )

    # 400 updates to first 400 active HQ establishments (0..149 -> 'F', 150..399 -> updated 'A') + 100 new.
    delta_etab_rows: list[dict[str, object]] = []
    for idx in range(DELTA_ETAB_UPDATES):
        row = dict(etab_parquet_rows[idx])
        row["dateDernierTraitementEtablissement"] = DELTA_ISO
        row["dateDebut"] = "2026-11-20"
        if idx < DELTA_ETAB_CLOSURES:
            row["etatAdministratifEtablissement"] = "F"
        else:
            row["enseigne1Etablissement"] = f"{row['enseigne1Etablissement']} V2"
        delta_etab_rows.append(row)

    for new_i in range(DELTA_ETAB_NEW):
        if new_i < DELTA_UL_NEW:
            siren = f"{900_015_001 + new_i:09d}"
            nic = "00014"
            siege = True
        else:
            siren = f"{900_000_001 + (new_i - DELTA_UL_NEW):09d}"
            nic = "00999"
            siege = False
        delta_etab_rows.append(
            {
                "siret": f"{siren}{nic}",
                "siren": siren,
                "nic": nic,
                "etablissementSiege": siege,
                "statutDiffusionEtablissement": "O",
                "etatAdministratifEtablissement": "A",
                "dateCreationEtablissement": "2026-11-20",
                "dateDebut": "2026-11-20",
                "dateDernierTraitementEtablissement": DELTA_ISO,
                "enseigne1Etablissement": f"NOUVEAU SITE {new_i + 1:03d}",
                "enseigne2Etablissement": None,
                "enseigne3Etablissement": None,
                "denominationUsuelleEtablissement": None,
                "activitePrincipaleEtablissement": "62.01Z",
                "nomenclatureActivitePrincipaleEtablissement": "NAFRev2",
                "activitePrincipaleNAF25Etablissement": None,
                "activitePrincipaleRegistreMetiersEtablissement": None,
                "trancheEffectifsEtablissement": "01",
                "anneeEffectifsEtablissement": 2026,
                "caractereEmployeurEtablissement": "O",
                "numeroVoieEtablissement": "10",
                "indiceRepetitionEtablissement": None,
                "typeVoieEtablissement": "RUE",
                "libelleVoieEtablissement": "DE RIVOLI",
                "complementAdresseEtablissement": None,
                "distributionSpecialeEtablissement": None,
                "codePostalEtablissement": "75001",
                "libelleCommuneEtablissement": "Paris 1er Arrondissement",
                "codeCommuneEtablissement": "75101",
                "codeCedexEtablissement": None,
                "libelleCedexEtablissement": None,
                "codePaysEtrangerEtablissement": None,
                "libelleCommuneEtrangerEtablissement": None,
                "identifiantAdresseEtablissement": f"75101_DELTA_{new_i:03d}",
                "coordonneeLambertAbscisseEtablissement": "652469.02",
                "coordonneeLambertOrdonneeEtablissement": "6862035.26",
            }
        )

    return sql_tables, ul_parquet_rows, etab_parquet_rows, delta_ul_rows, delta_etab_rows


def _write_sql_files(sql_tables: dict[str, list[tuple[object, ...]]]) -> None:
    """Write deterministic LF-only PostgreSQL COPY dump files under sirene/data/sql/."""
    sql_out = SIRENE_DIR / "data" / "sql"
    sql_out.mkdir(parents=True, exist_ok=True)

    with (sql_out / "01_load_referentials.sql").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- Deterministic INSEE Sirene synthetic referential load (LF).\n\n")
        _write_copy_block(
            fh,
            "ref_regions",
            ("code_region", "cheflieu", "nom_majuscule", "libelle"),
            sql_tables["ref_regions"],
        )
        _write_copy_block(
            fh,
            "ref_departements",
            ("code_departement", "code_region", "cheflieu", "nom_majuscule", "libelle"),
            sql_tables["ref_departements"],
        )
        _write_copy_block(
            fh,
            "ref_communes",
            ("code_commune", "code_departement", "type_commune", "nom_majuscule", "libelle", "est_active"),
            sql_tables["ref_communes"],
        )
        _write_copy_block(
            fh,
            "ref_pays",
            ("code_pays", "code_iso2", "code_iso3", "libelle"),
            sql_tables["ref_pays"],
        )
        _write_copy_block(
            fh,
            "ref_naf",
            ("code_naf", "nomenclature", "code_section", "libelle_section", "code_division", "libelle_division", "code_groupe", "libelle_groupe", "code_classe", "libelle_classe", "libelle_sous_classe"),
            sql_tables["ref_naf"],
        )
        _write_copy_block(
            fh,
            "ref_categories_juridiques",
            ("code_cj", "code_niveau1", "libelle_niveau1", "code_niveau2", "libelle_niveau2", "libelle"),
            sql_tables["ref_categories_juridiques"],
        )
        _write_copy_block(
            fh,
            "ref_tranches_effectifs",
            ("code_tranche", "effectif_min", "effectif_max", "libelle"),
            sql_tables["ref_tranches_effectifs"],
        )

    with (sql_out / "02_load_unites_legales.sql").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- Deterministic INSEE Sirene synthetic legal units load (15,000 rows, LF).\n\n")
        _write_copy_block(
            fh,
            "unites_legales",
            UNITE_LEGALE_COLUMNS + ("updated_at",),
            sql_tables["unites_legales"],
        )

    with (sql_out / "03_load_etablissements.sql").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- Deterministic INSEE Sirene synthetic establishments load (30,000 rows, LF).\n\n")
        _write_copy_block(
            fh,
            "etablissements",
            ETABLISSEMENT_COLUMNS + ("updated_at",),
            sql_tables["etablissements"],
        )

    with (sql_out / "04_load_governance_and_history.sql").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- Deterministic INSEE Sirene governance, audit history, and ETL logs load (LF).\n\n")
        _write_copy_block(
            fh,
            "personnes",
            ("id", "type_personne", "nom", "prenoms", "prenom_usuel", "sexe", "date_naissance", "siren_personne_morale", "cle_deduplication", "created_at", "updated_at"),
            sql_tables["personnes"],
        )
        _write_copy_block(
            fh,
            "roles_entreprises",
            ("id", "siren", "personne_id", "type_role", "qualite_detaillee", "pourcentage_detention", "pourcentage_droits_vote", "date_debut", "date_fin", "actif", "source_donnee"),
            sql_tables["roles_entreprises"],
        )
        _write_copy_block(
            fh,
            "etablissements_historique_etat",
            ("id", "siret", "ancien_etat", "nouvel_etat", "date_effet", "changed_at", "etl_log_id"),
            sql_tables["etablissements_historique_etat"],
        )
        _write_copy_block(
            fh,
            "etl_logs",
            ("id", "run_type", "entity_type", "resource_id", "source_url", "file_name", "file_version", "checksum_type", "checksum_value", "rows_processed", "rows_inserted", "rows_updated", "status", "started_at", "finished_at", "error_message", "metadata"),
            sql_tables["etl_logs"],
        )
        fh.write(
            "SELECT setval('personnes_id_seq', (SELECT COALESCE(MAX(id), 1) FROM personnes), true);\n"
            "SELECT setval('roles_entreprises_id_seq', (SELECT COALESCE(MAX(id), 1) FROM roles_entreprises), true);\n"
            "SELECT setval('etablissements_historique_etat_id_seq', (SELECT COALESCE(MAX(id), 1) FROM etablissements_historique_etat), true);\n"
            "SELECT setval('etl_logs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM etl_logs), true);\n"
        )


def _write_parquet_and_delta(
    ul_rows: list[dict[str, object]],
    etab_rows: list[dict[str, object]],
    delta_ul_rows: list[dict[str, object]],
    delta_etab_rows: list[dict[str, object]],
) -> None:
    """Write ZSTD Parquet stock/delta files and zipped CSV delta."""
    parquet_dir = SIRENE_DIR / "data" / "parquet"
    delta_dir = SIRENE_DIR / "data" / "delta"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    delta_dir.mkdir(parents=True, exist_ok=True)

    ul_schema = pa.schema(
        [
            ("siren", pa.string()),
            ("statutDiffusionUniteLegale", pa.string()),
            ("unitePurgeeUniteLegale", pa.bool_()),
            ("etatAdministratifUniteLegale", pa.string()),
            ("dateCreationUniteLegale", pa.string()),
            ("dateDebut", pa.string()),
            ("dateDernierTraitementUniteLegale", pa.string()),
            ("denominationUniteLegale", pa.string()),
            ("sigleUniteLegale", pa.string()),
            ("denominationUsuelle1UniteLegale", pa.string()),
            ("denominationUsuelle2UniteLegale", pa.string()),
            ("denominationUsuelle3UniteLegale", pa.string()),
            ("nomUniteLegale", pa.string()),
            ("nomUsageUniteLegale", pa.string()),
            ("prenomUsuelUniteLegale", pa.string()),
            ("prenom1UniteLegale", pa.string()),
            ("prenom2UniteLegale", pa.string()),
            ("prenom3UniteLegale", pa.string()),
            ("prenom4UniteLegale", pa.string()),
            ("pseudonymeUniteLegale", pa.string()),
            ("sexeUniteLegale", pa.string()),
            ("identifiantAssociationUniteLegale", pa.string()),
            ("categorieEntreprise", pa.string()),
            ("anneeCategorieEntreprise", pa.int64()),
            ("categorieJuridiqueUniteLegale", pa.string()),
            ("activitePrincipaleUniteLegale", pa.string()),
            ("nomenclatureActivitePrincipaleUniteLegale", pa.string()),
            ("activitePrincipaleNAF25UniteLegale", pa.string()),
            ("trancheEffectifsUniteLegale", pa.string()),
            ("anneeEffectifsUniteLegale", pa.int64()),
            ("nicSiegeUniteLegale", pa.string()),
            ("economieSocialeSolidaireUniteLegale", pa.string()),
            ("societeMissionUniteLegale", pa.string()),
            ("caractereEmployeurUniteLegale", pa.string()),
        ]
    )
    etab_schema = pa.schema(
        [
            ("siret", pa.string()),
            ("siren", pa.string()),
            ("nic", pa.string()),
            ("etablissementSiege", pa.bool_()),
            ("statutDiffusionEtablissement", pa.string()),
            ("etatAdministratifEtablissement", pa.string()),
            ("dateCreationEtablissement", pa.string()),
            ("dateDebut", pa.string()),
            ("dateDernierTraitementEtablissement", pa.string()),
            ("enseigne1Etablissement", pa.string()),
            ("enseigne2Etablissement", pa.string()),
            ("enseigne3Etablissement", pa.string()),
            ("denominationUsuelleEtablissement", pa.string()),
            ("activitePrincipaleEtablissement", pa.string()),
            ("nomenclatureActivitePrincipaleEtablissement", pa.string()),
            ("activitePrincipaleNAF25Etablissement", pa.string()),
            ("activitePrincipaleRegistreMetiersEtablissement", pa.string()),
            ("trancheEffectifsEtablissement", pa.string()),
            ("anneeEffectifsEtablissement", pa.int64()),
            ("caractereEmployeurEtablissement", pa.string()),
            ("numeroVoieEtablissement", pa.string()),
            ("indiceRepetitionEtablissement", pa.string()),
            ("typeVoieEtablissement", pa.string()),
            ("libelleVoieEtablissement", pa.string()),
            ("complementAdresseEtablissement", pa.string()),
            ("distributionSpecialeEtablissement", pa.string()),
            ("codePostalEtablissement", pa.string()),
            ("libelleCommuneEtablissement", pa.string()),
            ("codeCommuneEtablissement", pa.string()),
            ("codeCedexEtablissement", pa.string()),
            ("libelleCedexEtablissement", pa.string()),
            ("codePaysEtrangerEtablissement", pa.string()),
            ("libelleCommuneEtrangerEtablissement", pa.string()),
            ("identifiantAdresseEtablissement", pa.string()),
            ("coordonneeLambertAbscisseEtablissement", pa.string()),
            ("coordonneeLambertOrdonneeEtablissement", pa.string()),
        ]
    )

    pq.write_table(
        pa.Table.from_pylist(ul_rows, schema=ul_schema),
        parquet_dir / "StockUniteLegale_synthetic.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(etab_rows, schema=etab_schema),
        parquet_dir / "StockEtablissement_synthetic.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(delta_ul_rows, schema=ul_schema),
        delta_dir / "DeltaUniteLegale_synthetic.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(delta_etab_rows, schema=etab_schema),
        delta_dir / "DeltaEtablissement_synthetic.parquet",
        compression="zstd",
    )

    # Write matching zipped UTF-8 CSV delta for DeltaEtablissement.
    csv_cols = [field.name for field in etab_schema]
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(csv_cols)
    for row in delta_etab_rows:
        writer.writerow(
            [
                ("true" if row[c] is True else ("false" if row[c] is False else ("" if row[c] is None else str(row[c]))))
                for c in csv_cols
            ]
        )
    with zipfile.ZipFile(
        delta_dir / "DeltaEtablissement_synthetic.csv.zip",
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        zf.writestr("DeltaEtablissement_synthetic.csv", buf.getvalue().encode("utf-8"))


def main() -> int:
    """Generate deterministic SQL COPY dumps, Parquet stock/delta, and CSV.zip files."""
    sql_tables, ul_pq, etab_pq, delta_ul_pq, delta_etab_pq = _generate_dataset()
    _write_sql_files(sql_tables)
    _write_parquet_and_delta(ul_pq, etab_pq, delta_ul_pq, delta_etab_pq)

    counts = {tbl: len(rows) for tbl, rows in sql_tables.items()}
    print("Generated synthetic Sirene dataset:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
