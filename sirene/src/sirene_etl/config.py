"""Configuration loader for the Sirene PostgreSQL ETL pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATABASE_URL = (
    "postgresql://sirene:pg_sirene_ephemeral@localhost:15432/sirene"
)
DEFAULT_STAGING_DIR = Path("./staging")
DEFAULT_SQL_DIR = Path(__file__).resolve().parents[2] / "sql"
DEFAULT_BATCH_SIZE = 50_000
DEFAULT_DATAGOUV_DATASET_API = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/"
)
DEFAULT_COG_REGIONS_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_region_2026.csv"
)
DEFAULT_COG_DEPARTEMENTS_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv"
)
DEFAULT_COG_COMMUNES_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv"
)
DEFAULT_COG_COMMUNES_HIST_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv"
)
DEFAULT_COG_COMER_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_comer_2026.csv"
)
DEFAULT_COG_PAYS_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/8740222/v_pays_territoire_2026.csv"
)
DEFAULT_NAF_PARQUET_URL = (
    "https://static.data.gouv.fr/resources/naf-1/20231123-121750/nafr2.parquet"
)
DEFAULT_WATCHER_INTERVAL_SECONDS = 3600
DEFAULT_PREFERRED_FORMAT = "parquet"


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings for the Sirene ETL and watcher."""

    database_url: str = DEFAULT_DATABASE_URL
    staging_dir: Path = DEFAULT_STAGING_DIR
    sql_dir: Path = DEFAULT_SQL_DIR
    batch_size: int = DEFAULT_BATCH_SIZE
    datagouv_dataset_api: str = DEFAULT_DATAGOUV_DATASET_API
    cog_regions_url: str = DEFAULT_COG_REGIONS_URL
    cog_departements_url: str = DEFAULT_COG_DEPARTEMENTS_URL
    cog_communes_url: str = DEFAULT_COG_COMMUNES_URL
    cog_communes_hist_url: str = DEFAULT_COG_COMMUNES_HIST_URL
    cog_comer_url: str = DEFAULT_COG_COMER_URL
    cog_pays_url: str = DEFAULT_COG_PAYS_URL
    naf_parquet_url: str = DEFAULT_NAF_PARQUET_URL
    watcher_interval_seconds: int = DEFAULT_WATCHER_INTERVAL_SECONDS
    preferred_format: str = DEFAULT_PREFERRED_FORMAT


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw.strip())


def load_settings() -> Settings:
    """Load settings from environment variables and optional .env files."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None

    if load_dotenv is not None:
        load_dotenv(override=False)
        package_env = Path(__file__).resolve().parents[2] / ".env"
        if package_env.is_file():
            load_dotenv(package_env, override=False)

    staging_raw = os.getenv("STAGING_DIR")
    staging_dir = (
        Path(staging_raw.strip())
        if staging_raw and staging_raw.strip()
        else DEFAULT_STAGING_DIR
    )

    sql_raw = os.getenv("SQL_DIR")
    sql_dir = (
        Path(sql_raw.strip())
        if sql_raw and sql_raw.strip()
        else DEFAULT_SQL_DIR
    )

    return Settings(
        database_url=_env_str("DATABASE_URL", DEFAULT_DATABASE_URL),
        staging_dir=staging_dir,
        sql_dir=sql_dir,
        batch_size=_env_int("BATCH_SIZE", DEFAULT_BATCH_SIZE),
        datagouv_dataset_api=_env_str(
            "DATAGOUV_DATASET_API", DEFAULT_DATAGOUV_DATASET_API
        ),
        cog_regions_url=_env_str("COG_REGIONS_URL", DEFAULT_COG_REGIONS_URL),
        cog_departements_url=_env_str(
            "COG_DEPARTEMENTS_URL", DEFAULT_COG_DEPARTEMENTS_URL
        ),
        cog_communes_url=_env_str("COG_COMMUNES_URL", DEFAULT_COG_COMMUNES_URL),
        cog_communes_hist_url=_env_str(
            "COG_COMMUNES_HIST_URL", DEFAULT_COG_COMMUNES_HIST_URL
        ),
        cog_comer_url=_env_str("COG_COMER_URL", DEFAULT_COG_COMER_URL),
        cog_pays_url=_env_str("COG_PAYS_URL", DEFAULT_COG_PAYS_URL),
        naf_parquet_url=_env_str("NAF_PARQUET_URL", DEFAULT_NAF_PARQUET_URL),
        watcher_interval_seconds=_env_int(
            "WATCHER_INTERVAL_SECONDS", DEFAULT_WATCHER_INTERVAL_SECONDS
        ),
        preferred_format=_env_str(
            "PREFERRED_FORMAT", DEFAULT_PREFERRED_FORMAT
        ).lower(),
    )
