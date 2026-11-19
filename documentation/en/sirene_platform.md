[🏠 Home](index.md) | [⬅️ Previous](gap_locking_experiment.md) | [Interactive HTML Reference](../sirene_documentation.html) | [🇫🇷 French Version](../fr/sirene_platform.md)
***

# Sirene PostgreSQL 3NF Platform

The `sirene/` subsystem provides a production-ready **Python 3.12** and **PostgreSQL 17** ETL platform to ingest, normalize into Third Normal Form (3NF), enrich geographically, and continuously synchronize the French **INSEE Sirene** business registry from `data.gouv.fr` Parquet and CSV/ZIP distributions.

> For visual SVG schema exploration, searchable column definitions, and one-click SQL query copying, open the [Interactive HTML Reference](../sirene_documentation.html) (`make sirene-docs`).

---

## 1. Architecture & ETL Data Flow

The pipeline separates **referential seeding**, **streaming extraction and cleansing**, **high-throughput `COPY FROM STDIN` staging**, and **autonomous metadata polling**.

```mermaid
flowchart LR
    DG["data.gouv.fr Dataset API (Parquet / CSV / ZIP)"] -->|"HTTPS + Tenacity Retries"| DL["downloader.py (.part staging + SHA-256)"]
    COG["INSEE COG 2026 CSVs & NAF Rev. 2 Parquet"] -->|"CSV / PyArrow Parquet"| REF["referentials.py (3NF lookup + sentinels)"]
    DL -->|"Streamed Batches"| TR["transforms.py ([ND] scrub + EPSG:2154 to WGS84)"]
    TR -->|"Cleaned Row Tuples"| ING["full_import.py & incremental_import.py (COPY FROM STDIN + TEMP TABLE)"]
    REF -->|"UNNEST Upserts + HIST Auto-FK"| PG[("PostgreSQL 17 (3NF Schema + pg_trgm GIN)")]
    ING -->|"Idempotent Merge + Sole Proprietor Sync"| PG
    WATCH["watcher.py (--once / daemon polling)"] -->|"Checks etl_logs & Dispatches"| ING
    WATCH -.->|"Polls Resource Metadata"| DG
```

### Pipeline Stages

1. **Resource Discovery & Verified Download (`downloader.py`)**:
   - Queries the `data.gouv.fr` dataset API (`DATAGOUV_DATASET_API`) to locate the latest `StockUniteLegale` and `StockEtablissement` files while excluding `Historique`, `LiensSuccession`, and `Doublon` archives.
   - Prioritizes formats by `PREFERRED_FORMAT` (default `parquet`, ranking `parquet > zip/csv.zip > csv.gz/gz > csv`).
   - Streams payloads in 1 MiB (`1_048_576` bytes) chunks into `.part` staging files with `tenacity` exponential backoff (`stop_after_attempt(4)`, 1–8 s wait), verifies `sha256`/`sha1`/`md5` checksums on the fly, removes corrupted `.part` files on mismatch, and atomically replaces the target file.
2. **Referential Seeding & Dynamic FK Protection (`referentials.py`)**:
   - Idempotently seeds built-in INSEE workforce brackets (`NN`, `00`–`53`, `UN`), 18+ administrative regions + overseas collectivities (`COM`) + `UNK`, 101+ departments + `99` (foreign) + `20` (historical Corsica) + `UNK`, legal categories, core NAF fallbacks, and countries (`UNK`, `99100`).
   - When online or supplied via `--ref-dir`, ingests full **INSEE COG 2026** CSVs (`v_region_2026.csv`, `v_departement_2026.csv`, `v_commune_2026.csv`, `v_commune_comer_2026.csv`, `v_commune_depuis_1943.csv`, `v_pays_territoire_2026.csv`) and **NAF Rev. 2** (`nafr2.parquet`).
   - Automatically inserts unseen historical or unlisted NAF, legal category, municipality, and country codes via `ensure_missing_referential_codes()` (`nomenclature = 'HIST'`, `type_commune = 'HIST'`, `est_active = FALSE`) before parent/child merges so foreign keys never fail.
3. **Row Cleansing & Lambert-93 -> WGS84 Projection (`transforms.py`)**:
   - Streams `.parquet` (`pyarrow.parquet.ParquetFile.iter_batches`), `.csv`, `.csv.gz`, and `.zip` archives in configurable batches (`BATCH_SIZE`, default `50_000`), stripping trailing whitespace from Sirene CSV headers (such as `"coordonneeLambertAbscisseEtablissement "`).
   - Converts `""`, `"null"`, `"[ND]"`, and `"[nd]"` diffusion masks into SQL `NULL`, pads numeric codes (`code_cj` to 4 chars, `nic` to 5 chars, single-digit `code_tranche_effectifs` to 2 digits), and concatenates `prenom1UniteLegale`..`prenom4UniteLegale`.
   - Converts planar **EPSG:2154 (Lambert-93, GRS80)** coordinates (`coord_lambert_x`, `coord_lambert_y`) to **WGS84** (`longitude`, `latitude`, rounded to 6 decimal places) using pure-Python fixed-point iteration (`12` iterations max, `1e-11` rad tolerance).
4. **Bulk Full Import vs. Transactional Incremental Sync (`full_import.py`, `incremental_import.py`, `db.py`)**:
   - Acquires PostgreSQL session-level advisory lock `84729101` (`pg_try_advisory_lock`) and verifies `etl_logs` checksum idempotency.
   - `full_import.py` drops non-constraint secondary indexes (`drop_secondary_indexes()`), streams transformed tuples via `psycopg` v3 `COPY ... FROM STDIN` into `TEMP TABLE` staging tables (`tmp_full_ul`, `tmp_full_etab`), resolves missing FKs and orphan establishment `siren` placeholders (`etat_administratif = 'C'`, `statut_diffusion = 'P'`), executes `IS DISTINCT FROM` upserts, projects sole proprietors into `personnes` and `roles_entreprises`, and rebuilds all 25 indexes followed by `ANALYZE`.
   - `incremental_import.py` runs inside a single `conn.transaction()` block using `ON COMMIT DROP` temp tables (`tmp_inc_ul`, `tmp_inc_etab`), deduplicates by PK keeping the newest `date_dernier_traitement`, records `'A' <-> 'F'` state transitions in `etablissements_historique_etat`, guards updates with a monotonic timestamp predicate (`COALESCE(EXCLUDED.date_dernier_traitement, 'infinity'::timestamptz) >= COALESCE(target.date_dernier_traitement, '-infinity'::timestamptz)`), preserves existing non-null `date_creation`, and updates `roles_entreprises.actif`.
5. **Autonomous Watcher (`watcher.py`)**:
   - Compares remote `checksum_value`, `last_modified`, `resource_id`, `file_name`, and `title` against `get_last_successful_import()` in `etl_logs`.
   - Runs `run_full_import` if `unites_legales` is empty or `run_incremental_import` if populated, recording every poll cycle as `run_type = 'WATCHER_CHECK'` in `etl_logs`.

---

## 2. PostgreSQL 17 3NF Data Model & Indexes

The schema (`sirene/sql/01_schema_3nf.sql`) requires **PostgreSQL 15+** (using `UNIQUE NULLS NOT DISTINCT` and immutable `STORED` generated columns) and the `pg_trgm` extension.

### Entity-Relationship Diagram (All 13 Tables)

```mermaid
erDiagram
    ref_regions {
        varchar code_region PK "VARCHAR(3), sentinel UNK"
        varchar cheflieu "VARCHAR(5)"
        varchar nom_majuscule "VARCHAR(100) NOT NULL"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    ref_departements {
        varchar code_departement PK "VARCHAR(4), sentinel UNK"
        varchar code_region FK "REFERENCES ref_regions"
        varchar cheflieu "VARCHAR(5)"
        varchar nom_majuscule "VARCHAR(100) NOT NULL"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    ref_communes {
        varchar code_commune PK "VARCHAR(5), sentinel UNK00"
        varchar code_departement FK "REFERENCES ref_departements"
        varchar type_commune "VARCHAR(6), default COM"
        varchar nom_majuscule "VARCHAR(150) NOT NULL"
        varchar libelle "VARCHAR(150) NOT NULL"
        boolean est_active "BOOLEAN, default TRUE"
    }
    ref_pays {
        varchar code_pays PK "VARCHAR(5), sentinels UNK and 99100"
        char code_iso2 "CHAR(2)"
        char code_iso3 "CHAR(3)"
        varchar libelle "VARCHAR(150) NOT NULL"
    }
    ref_naf {
        varchar code_naf PK "VARCHAR(6), sentinel 00.00Z"
        varchar nomenclature "VARCHAR(12), default NAFRev2"
        varchar code_section "VARCHAR(2)"
        varchar code_division "VARCHAR(2)"
        varchar code_groupe "VARCHAR(4)"
        varchar code_classe "VARCHAR(5)"
        varchar libelle_sous_classe "VARCHAR(255) NOT NULL"
    }
    ref_categories_juridiques {
        varchar code_cj PK "VARCHAR(4), sentinel 0000"
        varchar code_niveau1 "VARCHAR(1)"
        varchar code_niveau2 "VARCHAR(2)"
        varchar libelle "VARCHAR(255) NOT NULL"
    }
    ref_tranches_effectifs {
        varchar code_tranche PK "VARCHAR(2), sentinels NN and UN"
        integer effectif_min "INTEGER"
        integer effectif_max "INTEGER"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    unites_legales {
        varchar siren PK "VARCHAR(9), 9 digits"
        char etat_administratif "CHAR(1), A or C"
        char statut_diffusion "CHAR(1), default O"
        varchar denomination "VARCHAR(255)"
        varchar categorie_entreprise "PME, ETI, or GE"
        varchar code_cj FK "default 0000"
        varchar code_naf FK "default 00.00Z"
        varchar code_tranche_effectifs FK "default NN"
        text nom_recherche "GENERATED STORED"
        timestamptz updated_at "NOT NULL DEFAULT NOW()"
    }
    etablissements {
        varchar siret PK "VARCHAR(14), 14 digits"
        varchar siren FK "ON DELETE CASCADE"
        varchar nic "VARCHAR(5) NOT NULL"
        boolean etablissement_siege "DEFAULT FALSE"
        char etat_administratif "CHAR(1), A or F"
        varchar code_naf FK "default 00.00Z"
        varchar code_tranche_effectifs FK "default NN"
        varchar code_commune FK "default UNK00"
        varchar code_pays_etranger FK "REFERENCES ref_pays"
        text adresse_complete "GENERATED STORED"
        text enseigne_recherche "GENERATED STORED"
        double_precision longitude "WGS84"
        double_precision latitude "WGS84"
    }
    etablissements_historique_etat {
        bigserial id PK "BIGSERIAL"
        varchar siret FK "ON DELETE CASCADE"
        char ancien_etat "CHAR(1) NOT NULL"
        char nouvel_etat "CHAR(1) NOT NULL"
        date date_effet "DATE"
        timestamptz changed_at "NOT NULL DEFAULT NOW()"
        bigint etl_log_id "Audit reference"
    }
    personnes {
        bigserial id PK "BIGSERIAL"
        varchar type_personne "PHYSIQUE or MORALE"
        varchar nom "VARCHAR(150)"
        varchar prenoms "VARCHAR(255)"
        varchar siren_personne_morale FK "ON DELETE SET NULL"
        varchar cle_deduplication UK "VARCHAR(128) NOT NULL"
        text nom_complet_recherche "GENERATED STORED"
    }
    roles_entreprises {
        bigserial id PK "BIGSERIAL"
        varchar siren FK "ON DELETE CASCADE"
        bigint personne_id FK "ON DELETE CASCADE"
        varchar type_role "9 allowed roles"
        numeric pourcentage_detention "0..100"
        numeric pourcentage_droits_vote "0..100"
        date date_debut "UNIQUE NULLS NOT DISTINCT"
        boolean actif "DEFAULT TRUE"
    }
    etl_logs {
        bigserial id PK "BIGSERIAL"
        varchar run_type "REFERENTIALS, FULL_IMPORT, INCREMENTAL_IMPORT, WATCHER_CHECK"
        varchar entity_type "UNITE_LEGALE, ETABLISSEMENT, ALL"
        varchar checksum_value "VARCHAR(128)"
        bigint rows_processed "DEFAULT 0"
        varchar status "RUNNING, SUCCESS, FAILED, SKIPPED"
        jsonb metadata "DEFAULT empty object"
    }

    ref_regions ||--o{ ref_departements : "code_region"
    ref_departements ||--o{ ref_communes : "code_departement"
    ref_categories_juridiques ||--o{ unites_legales : "code_cj"
    ref_naf ||--o{ unites_legales : "code_naf"
    ref_tranches_effectifs ||--o{ unites_legales : "code_tranche_effectifs"
    unites_legales ||--o{ etablissements : "siren"
    ref_naf ||--o{ etablissements : "code_naf"
    ref_tranches_effectifs ||--o{ etablissements : "code_tranche_effectifs"
    ref_communes ||--o{ etablissements : "code_commune"
    ref_pays ||--o{ etablissements : "code_pays_etranger"
    etablissements ||--o{ etablissements_historique_etat : "siret"
    unites_legales |o--o{ personnes : "siren_personne_morale"
    unites_legales ||--o{ roles_entreprises : "siren"
    personnes ||--o{ roles_entreprises : "personne_id"
    etl_logs |o..o{ etablissements_historique_etat : "etl_log_id"
```

### Complete Table Catalog (13 Tables)

#### A. Referential Lookup Dimensions (7 Tables)

| Table | Primary Key | Foreign Keys | Columns & Key Constraints |
| :--- | :--- | :--- | :--- |
| `ref_regions` | `code_region VARCHAR(3)` | — | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` |
| `ref_departements` | `code_departement VARCHAR(4)` | `code_region` -> `ref_regions(code_region)` | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` |
| `ref_communes` | `code_commune VARCHAR(5)` | `code_departement` -> `ref_departements(code_departement)` | `type_commune VARCHAR(6) NOT NULL DEFAULT 'COM'`, `nom_majuscule VARCHAR(150) NOT NULL`, `libelle VARCHAR(150) NOT NULL`, `est_active BOOLEAN NOT NULL DEFAULT TRUE` |
| `ref_pays` | `code_pays VARCHAR(5)` | — | `code_iso2 CHAR(2)`, `code_iso3 CHAR(3)`, `libelle VARCHAR(150) NOT NULL` |
| `ref_naf` | `code_naf VARCHAR(6)` | — | `nomenclature VARCHAR(12) NOT NULL DEFAULT 'NAFRev2'`, `code_section VARCHAR(2)`, `libelle_section VARCHAR(255)`, `code_division VARCHAR(2)`, `libelle_division VARCHAR(255)`, `code_groupe VARCHAR(4)`, `libelle_groupe VARCHAR(255)`, `code_classe VARCHAR(5)`, `libelle_classe VARCHAR(255)`, `libelle_sous_classe VARCHAR(255) NOT NULL` |
| `ref_categories_juridiques` | `code_cj VARCHAR(4)` | — | `code_niveau1 VARCHAR(1)`, `libelle_niveau1 VARCHAR(255)`, `code_niveau2 VARCHAR(2)`, `libelle_niveau2 VARCHAR(255)`, `libelle VARCHAR(255) NOT NULL` |
| `ref_tranches_effectifs` | `code_tranche VARCHAR(2)` | — | `effectif_min INTEGER`, `effectif_max INTEGER`, `libelle VARCHAR(120) NOT NULL` |

#### B. Core SIRENE Entities & History (3 Tables)

1. **`unites_legales`** (`siren VARCHAR(9) PRIMARY KEY CHECK (siren ~ '^[0-9]{9}$')`):
   - **Status & Lifecycle**: `statut_diffusion CHAR(1) NOT NULL DEFAULT 'O'`, `unite_purgee BOOLEAN NOT NULL DEFAULT FALSE`, `etat_administratif CHAR(1) NOT NULL CHECK (etat_administratif IN ('A', 'C'))`, `date_creation DATE`, `date_debut_periode DATE`, `date_dernier_traitement TIMESTAMPTZ`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - **Identity & Naming**: `denomination VARCHAR(255)`, `sigle VARCHAR(50)`, `denomination_usuelle_1 VARCHAR(150)`, `denomination_usuelle_2 VARCHAR(150)`, `denomination_usuelle_3 VARCHAR(150)`, `nom_naissance VARCHAR(150)`, `nom_usage VARCHAR(150)`, `prenom_usuel VARCHAR(100)`, `prenoms VARCHAR(255)`, `pseudonyme VARCHAR(150)`, `sexe CHAR(1)`, `identifiant_association VARCHAR(20)`, `nom_recherche TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Classification & Flags**: `categorie_entreprise VARCHAR(5) CHECK (categorie_entreprise IS NULL OR categorie_entreprise IN ('PME', 'ETI', 'GE'))`, `annee_categorie_entreprise SMALLINT`, `code_cj VARCHAR(4) NOT NULL DEFAULT '0000' REFERENCES ref_categories_juridiques(code_cj)`, `code_naf VARCHAR(6) NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf)`, `nomenclature_activite VARCHAR(15)`, `code_naf_2025 VARCHAR(6)`, `code_tranche_effectifs VARCHAR(2) NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche)`, `annee_effectifs SMALLINT`, `nic_siege VARCHAR(5)`, `economie_sociale_solidaire CHAR(1)`, `societe_mission CHAR(1)`, `caractere_employeur CHAR(1)`.

2. **`etablissements`** (`siret VARCHAR(14) PRIMARY KEY CHECK (siret ~ '^[0-9]{14}$')`):
   - **Identity & Lifecycle**: `siren VARCHAR(9) NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE`, `nic VARCHAR(5) NOT NULL`, `etablissement_siege BOOLEAN NOT NULL DEFAULT FALSE`, `statut_diffusion CHAR(1) NOT NULL DEFAULT 'O'`, `etat_administratif CHAR(1) NOT NULL CHECK (etat_administratif IN ('A', 'F'))`, `date_creation DATE`, `date_debut_periode DATE`, `date_dernier_traitement TIMESTAMPTZ`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - **Activity & Workforce**: `enseigne_1 VARCHAR(150)`, `enseigne_2 VARCHAR(150)`, `enseigne_3 VARCHAR(150)`, `denomination_usuelle VARCHAR(150)`, `code_naf VARCHAR(6) NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf)`, `nomenclature_activite VARCHAR(15)`, `code_naf_2025 VARCHAR(6)`, `activite_artisanale VARCHAR(15)`, `code_tranche_effectifs VARCHAR(2) NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche)`, `annee_effectifs SMALLINT`, `caractere_employeur CHAR(1)`, `enseigne_recherche TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Postal & Foreign Address**: `numero_voie VARCHAR(20)`, `indice_repetition VARCHAR(15)`, `type_voie VARCHAR(40)`, `libelle_voie VARCHAR(150)`, `complement_adresse VARCHAR(150)`, `distribution_speciale VARCHAR(50)`, `code_postal VARCHAR(15)`, `libelle_commune VARCHAR(150)`, `code_commune VARCHAR(5) NOT NULL DEFAULT 'UNK00' REFERENCES ref_communes(code_commune)`, `code_cedex VARCHAR(20)`, `libelle_cedex VARCHAR(120)`, `code_pays_etranger VARCHAR(5) REFERENCES ref_pays(code_pays)`, `libelle_commune_etranger VARCHAR(150)`, `adresse_complete TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Geolocation**: `identifiant_adresse_ban VARCHAR(30)`, `coord_lambert_x NUMERIC(12, 2)`, `coord_lambert_y NUMERIC(12, 2)`, `longitude DOUBLE PRECISION`, `latitude DOUBLE PRECISION`.

3. **`etablissements_historique_etat`** (`id BIGSERIAL PRIMARY KEY`):
   - Columns: `siret VARCHAR(14) NOT NULL REFERENCES etablissements(siret) ON DELETE CASCADE`, `ancien_etat CHAR(1) NOT NULL`, `nouvel_etat CHAR(1) NOT NULL`, `date_effet DATE`, `changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `etl_log_id BIGINT`.

#### C. Governance & Sole Proprietors (2 Tables)

1. **`personnes`** (`id BIGSERIAL PRIMARY KEY`):
   - Columns: `type_personne VARCHAR(10) NOT NULL CHECK (type_personne IN ('PHYSIQUE', 'MORALE'))`, `nom VARCHAR(150)`, `prenoms VARCHAR(255)`, `prenom_usuel VARCHAR(100)`, `sexe CHAR(1)`, `date_naissance DATE`, `siren_personne_morale VARCHAR(9) REFERENCES unites_legales(siren) ON DELETE SET NULL`, `cle_deduplication VARCHAR(128) NOT NULL UNIQUE`, `nom_complet_recherche TEXT GENERATED ALWAYS AS (...) STORED`, `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - Sole proprietors projected by `full_import.py` and `incremental_import.py` use a deterministic SHA-256 deduplication key: `encode(sha256(convert_to('SIRENE_EI|' || ul.siren, 'UTF8')), 'hex')`.

2. **`roles_entreprises`** (`id BIGSERIAL PRIMARY KEY`):
   - Columns: `siren VARCHAR(9) NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE`, `personne_id BIGINT NOT NULL REFERENCES personnes(id) ON DELETE CASCADE`, `type_role VARCHAR(40) NOT NULL`, `qualite_detaillee VARCHAR(150)`, `pourcentage_detention NUMERIC(5, 2) CHECK (pourcentage_detention IS NULL OR (pourcentage_detention >= 0 AND pourcentage_detention <= 100))`, `pourcentage_droits_vote NUMERIC(5, 2) CHECK (pourcentage_droits_vote IS NULL OR (pourcentage_droits_vote >= 0 AND pourcentage_droits_vote <= 100))`, `date_debut DATE`, `date_fin DATE`, `actif BOOLEAN NOT NULL DEFAULT TRUE`, `source_donnee VARCHAR(30) NOT NULL DEFAULT 'SIRENE'`.
   - Allowed `type_role` values: `'ENTREPRENEUR_INDIVIDUEL'`, `'GERANT'`, `'PRESIDENT'`, `'DIRECTEUR_GENERAL'`, `'ADMINISTRATEUR'`, `'ASSOCIE'`, `'ACTIONNAIRE'`, `'BENEFICIAIRE_EFFECTIF'`, `'AUTRE'`.
   - PostgreSQL 15+ uniqueness constraint: `UNIQUE NULLS NOT DISTINCT (siren, personne_id, type_role, date_debut)`.

#### D. ETL Observability & Checksum Ledger (1 Table)

1. **`etl_logs`** (`id BIGSERIAL PRIMARY KEY`):
   - Columns: `run_type VARCHAR(30) NOT NULL CHECK (run_type IN ('REFERENTIALS', 'FULL_IMPORT', 'INCREMENTAL_IMPORT', 'WATCHER_CHECK'))`, `entity_type VARCHAR(40) NOT NULL`, `resource_id VARCHAR(100)`, `source_url TEXT`, `file_name VARCHAR(255)`, `file_version VARCHAR(64)`, `checksum_type VARCHAR(16)`, `checksum_value VARCHAR(128)`, `rows_processed BIGINT NOT NULL DEFAULT 0`, `rows_inserted BIGINT NOT NULL DEFAULT 0`, `rows_updated BIGINT NOT NULL DEFAULT 0`, `status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED'))`, `started_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `finished_at TIMESTAMPTZ`, `error_message TEXT`, `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`.

### Generated Columns (`STORED`)

PostgreSQL requires `GENERATED ALWAYS AS (...) STORED` expressions to rely solely on `IMMUTABLE` operators. Because `CONCAT_WS` is marked `STABLE` (not `IMMUTABLE`) in PostgreSQL, `01_schema_3nf.sql` constructs normalized search strings with `TRIM(...)`, `COALESCE(...)`, `NULLIF(...)`, and `||`:

| Table | Column | Generated Expression | Purpose |
| :--- | :--- | :--- | :--- |
| `unites_legales` | `nom_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(denomination), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(sigle), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(denomination_usuelle_1), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(COALESCE(NULLIF(TRIM(nom_usage), ''), nom_naissance)), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(prenom_usuel), ''), ''))` | Unified legal unit / natural person search projection backed by `idx_ul_nom_trgm` |
| `etablissements` | `adresse_complete` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(numero_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(indice_repetition), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(type_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(libelle_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(complement_adresse), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(code_postal), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(COALESCE(NULLIF(TRIM(libelle_commune), ''), libelle_commune_etranger)), ''), ''))` | Single-space normalized domestic or foreign postal address |
| `etablissements` | `enseigne_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(enseigne_1), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(enseigne_2), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(enseigne_3), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(denomination_usuelle), ''), ''))` | Establishment trade-sign search projection backed by `idx_etab_enseigne_trgm` |
| `personnes` | `nom_complet_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(nom), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(prenoms), ''), ''))` | Full-name officer/proprietor search projection backed by `idx_personnes_nom_trgm` |

### Sentinel Defaults & Historical FK Fallbacks

To guarantee zero foreign-key failures across decades of historical INSEE Sirene records (including purged units, `[ND]` masked attributes, and obsolete COG codes), `01_schema_3nf.sql` seeds idempotent sentinel rows (`ON CONFLICT DO NOTHING`):

| Table | Sentinel Key(s) | Default FK Usage | Meaning |
| :--- | :--- | :--- | :--- |
| `ref_regions` | `'UNK'` | `ref_departements.code_region` | Unknown or unspecified region |
| `ref_departements` | `'UNK'` | `ref_communes.code_departement` (`code_region = 'UNK'`) | Unknown or unspecified department |
| `ref_communes` | `'UNK00'` | `etablissements.code_commune DEFAULT 'UNK00'` | Unknown or unspecified municipality (`est_active = FALSE`) |
| `ref_pays` | `'UNK'`, `'99100'` | `etablissements.code_pays_etranger` (nullable) | Unknown country (`UNK`) and France (`99100`, `FR`, `FRA`) |
| `ref_naf` | `'00.00Z'` | `unites_legales.code_naf` & `etablissements.code_naf DEFAULT '00.00Z'` | Unknown or unspecified principal activity |
| `ref_categories_juridiques` | `'0000'` | `unites_legales.code_cj DEFAULT '0000'` | Unknown or unspecified legal category |
| `ref_tranches_effectifs` | `'NN'`, `'UN'` | `unites_legales.code_tranche_effectifs` & `etablissements.code_tranche_effectifs DEFAULT 'NN'` | `NN`: non-employing/unspecified; `UN`: masked `[ND]` headcount |

Additionally, `referentials.py` (`ensure_missing_referential_codes()`) auto-registers previously unseen codes encountered in Sirene stock or delta batches as `nomenclature = 'HIST'` (`ref_naf`), `type_commune = 'HIST'` with `est_active = FALSE` (`ref_communes`), or `'Historical or unlisted ...'` (`ref_categories_juridiques`, `ref_pays`).

### Secondary & Search Indexes (25 Indexes in `sirene/sql/02_indexes.sql`)

| Index Name | Table | Definition / Columns | Type |
| :--- | :--- | :--- | :--- |
| `idx_ref_departements_code_region` | `ref_departements` | `(code_region)` | B-Tree (FK) |
| `idx_ref_communes_code_departement` | `ref_communes` | `(code_departement)` | B-Tree (FK) |
| `idx_ul_code_cj` | `unites_legales` | `(code_cj)` | B-Tree (FK) |
| `idx_ul_code_naf` | `unites_legales` | `(code_naf)` | B-Tree (FK) |
| `idx_ul_code_tranche_effectifs` | `unites_legales` | `(code_tranche_effectifs)` | B-Tree (FK) |
| `idx_ul_etat_administratif` | `unites_legales` | `(etat_administratif)` | B-Tree (Filter) |
| `idx_ul_categorie_entreprise` | `unites_legales` | `(categorie_entreprise)` | B-Tree (Filter) |
| `idx_ul_date_dernier_traitement` | `unites_legales` | `(date_dernier_traitement)` | B-Tree (Temporal) |
| `idx_etab_siren` | `etablissements` | `(siren)` | B-Tree (FK) |
| `idx_etab_code_commune` | `etablissements` | `(code_commune)` | B-Tree (FK) |
| `idx_etab_code_naf` | `etablissements` | `(code_naf)` | B-Tree (FK) |
| `idx_etab_code_tranche_effectifs` | `etablissements` | `(code_tranche_effectifs)` | B-Tree (FK) |
| `idx_etab_code_pays_etranger` | `etablissements` | `(code_pays_etranger)` | B-Tree (FK) |
| `idx_etab_code_postal` | `etablissements` | `(code_postal)` | B-Tree (Filter) |
| `idx_etab_etat_administratif` | `etablissements` | `(etat_administratif)` | B-Tree (Filter) |
| `idx_etab_date_dernier_traitement` | `etablissements` | `(date_dernier_traitement)` | B-Tree (Temporal) |
| `idx_etab_naf_commune_actif` | `etablissements` | `(code_naf, code_commune) WHERE etat_administratif = 'A'` | Partial Composite B-Tree |
| `idx_etab_hist_siret` | `etablissements_historique_etat` | `(siret)` | B-Tree (FK) |
| `idx_personnes_siren_pm` | `personnes` | `(siren_personne_morale)` | B-Tree (FK) |
| `idx_roles_siren` | `roles_entreprises` | `(siren)` | B-Tree (FK) |
| `idx_roles_personne_id` | `roles_entreprises` | `(personne_id)` | B-Tree (FK) |
| `idx_etl_logs_entity_status_finished` | `etl_logs` | `(entity_type, status, finished_at DESC)` | Composite B-Tree |
| `idx_ul_nom_trgm` | `unites_legales` | `USING GIN (nom_recherche gin_trgm_ops) WITH (fastupdate = on)` | `pg_trgm` GIN |
| `idx_etab_enseigne_trgm` | `etablissements` | `USING GIN (enseigne_recherche gin_trgm_ops) WITH (fastupdate = on)` | `pg_trgm` GIN |
| `idx_personnes_nom_trgm` | `personnes` | `USING GIN (nom_complet_recherche gin_trgm_ops) WITH (fastupdate = on)` | `pg_trgm` GIN |

---

## 3. Python Scripts, CLI Reference & Docker Operations

### CLI Entrypoints (`sirene/`)

Each CLI wrapper prepends `sirene/src/` to `sys.path` so scripts can be invoked directly with Python or via Docker Compose.

#### 1. `sirene/full_import.py` (`sirene_etl.full_import:main`)

Performs an idempotent full-stock ingestion with secondary index drop/rebuild and `ANALYZE`.

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (API) | Local `StockUniteLegale` file (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (API) | Local `StockEtablissement` file (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--ref-dir` | `Path` | `None` | Local directory holding COG 2026 CSVs and `nafr2.parquet` |
| `--offline-refs` | Flag | `False` | Seed built-in offline INSEE referentials without remote HTTP calls |
| `--limit-rows` | `int` | `None` | Maximum number of rows to ingest per entity file (useful for smoke tests) |
| `--force` | Flag | `False` | Re-import even if file checksums already succeeded in `etl_logs` |

```bash
python sirene/full_import.py --offline-refs --limit-rows 10000
python sirene/full_import.py --ul-file staging/ul.parquet --etab-file staging/etab.parquet --force
```

#### 2. `sirene/incremental_import.py` (`sirene_etl.incremental_import:main`)

Runs transactional delta synchronization with monotonic `date_dernier_traitement` protection and `'A' <-> 'F'` state-transition auditing.

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (API) | Local delta `StockUniteLegale` file (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (API) | Local delta `StockEtablissement` file (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--force` | Flag | `False` | Re-apply delta files even if checksums already succeeded in `etl_logs` |

```bash
python sirene/incremental_import.py --etab-file staging/delta_etab.csv.gz
```

#### 3. `sirene/watcher.py` (`sirene_etl.watcher:main`)

Polls `data.gouv.fr` dataset metadata, compares checksums/timestamps/IDs/filenames against `etl_logs`, and dispatches either `full_import.py` (when `unites_legales` is empty) or `incremental_import.py` (when populated).

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--once` | Flag | `False` | Execute a single check-and-sync cycle and exit |
| `--interval` | `int` | `WATCHER_INTERVAL_SECONDS` | Override polling interval in seconds for daemon mode |
| `--force` | Flag | `False` | Force download and ETL run even if remote metadata matches `etl_logs` |
| `--offline-refs` | Flag | `False` | Seed built-in offline referentials if an initial full import is triggered |

```bash
python sirene/watcher.py --once --offline-refs
python sirene/watcher.py --interval 1800
```

### Internal Library Modules (`sirene/src/sirene_etl/`)

| Module | Key Public Symbols | Core Responsibility |
| :--- | :--- | :--- |
| `__init__.py` | `__version__` (`"1.9.0"`) | Package metadata export |
| `config.py` | `Settings`, `load_settings()` | Frozen dataclass config loaded from `.env` and environment variables |
| `logging_utils.py` | `JsonLineFormatter`, `get_logger()` | Compact single-line UTC JSON logger emitting to active `sys.stdout` |
| `db.py` | `get_connection()`, `acquire_etl_lock()`, `release_etl_lock()`, `apply_sql_file()`, `drop_secondary_indexes()`, `rebuild_indexes_and_analyze()`, `start_etl_log()`, `finish_etl_log()`, `is_checksum_already_imported()`, `get_last_successful_import()` | `psycopg` v3 connection context, advisory lock (`84729101`), DDL execution, index lifecycle management, and `etl_logs` ledger |
| `downloader.py` | `compute_file_checksum()`, `extract_sirene_resources_from_payload()`, `fetch_datagouv_sirene_resources()`, `download_with_verification()` | `data.gouv.fr` JSON API parsing, `httpx` + `tenacity` streaming downloads to `.part`, SHA-256/SHA-1/MD5 verification |
| `referentials.py` | `seed_all_referentials()`, `ensure_missing_referential_codes()`, `BUILTIN_*` | Built-in + COG 2026 CSV + `nafr2.parquet` `UNNEST` upserts and dynamic `HIST` FK protection |
| `transforms.py` | `clean_sirene_str()`, `parse_date()`, `parse_timestamp()`, `parse_int()`, `parse_float()`, `parse_bool()`, `lambert93_to_wgs84()`, `iter_records_from_file()`, `transform_unite_legale_row()`, `transform_etablissement_row()` | Multi-format batch streaming, `[ND]` scrubbing, EPSG:2154 Lambert-93 -> WGS84 conversion, schema-aligned tuple projection |
| `full_import.py` | `run_full_import()`, `main()` | Advisory lock, schema & referential setup, index drop/rebuild, `COPY FROM STDIN`, `IS DISTINCT FROM` upsert, sole-proprietor projection |
| `incremental_import.py` | `run_incremental_import()`, `main()` | Single-transaction `ON COMMIT DROP` `COPY FROM STDIN`, PK deduplication, `etablissements_historique_etat` transition capture, monotonic guard |
| `watcher.py` | `check_and_sync_once()`, `run_daemon()`, `main()` | Metadata diffing against `etl_logs`, `SIGINT`/`SIGTERM` shutdown handling, full/incremental dispatch |

### Environment Variables

| Variable | Default Value | Purpose |
| :--- | :--- | :--- |
| `POSTGRES_USER` | `sirene` | PostgreSQL container role name |
| `POSTGRES_PASSWORD` | `pg_sirene_ephemeral` | Ephemeral local PoC password (do not commit real credentials) |
| `POSTGRES_DB` | `sirene` | Target PostgreSQL database name |
| `POSTGRES_HOST_PORT` | `15432` | Host loopback port mapped to container `5432` (avoids local `5432` conflict) |
| `DATABASE_URL` | `postgresql://sirene:pg_sirene_ephemeral@localhost:15432/sirene` | SQL DSN used on host (`sirene-postgres:5432` inside Docker Compose) |
| `STAGING_DIR` | `./staging` | Directory for `.part` downloads and cached referentials |
| `SQL_DIR` | `<package_root>/sql` | Directory containing `01_schema_3nf.sql` and `02_indexes.sql` |
| `BATCH_SIZE` | `50000` | Rows streamed per `COPY FROM STDIN` batch |
| `WATCHER_INTERVAL_SECONDS` | `3600` | Daemon polling interval in seconds |
| `PREFERRED_FORMAT` | `parquet` | Preferred `data.gouv.fr` resource format |
| `LOG_LEVEL` | `INFO` | Structured JSON logger level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATAGOUV_DATASET_API` | `https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/` | Dataset metadata API URL |
| `COG_REGIONS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_region_2026.csv` | INSEE COG 2026 regions CSV |
| `COG_DEPARTEMENTS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv` | INSEE COG 2026 departments CSV |
| `COG_COMMUNES_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv` | INSEE COG 2026 active municipalities CSV |
| `COG_COMMUNES_HIST_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv` | INSEE historical municipalities since 1943 CSV |
| `COG_COMER_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_comer_2026.csv` | INSEE overseas collectivities (`COMER`) CSV |
| `COG_PAYS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_pays_territoire_2026.csv` | INSEE countries and territories CSV |
| `NAF_PARQUET_URL` | `https://static.data.gouv.fr/resources/naf-1/20231123-121750/nafr2.parquet` | Official NAF Rev. 2 hierarchy Parquet file |

### Docker Compose Services, Profiles & PostgreSQL 17 Tuning

Defined in `sirene/docker-compose.yml`:

- **`sirene-postgres`** (`postgres:17-bookworm`, `shm_size: 1gb`):
  - Binds `127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432`.
  - Mounts `./sql:/docker-entrypoint-initdb.d:ro` (automatically executes `01_schema_3nf.sql` and `02_indexes.sql` on first database initialization) and `sirene_pgdata:/var/lib/postgresql/data`.
  - Healthcheck: `pg_isready -U $${POSTGRES_USER:-sirene} -d $${POSTGRES_DB:-sirene}` every `5s`.
  - Ingestion-tuned parameters: `shared_buffers=1GB`, `work_mem=64MB`, `maintenance_work_mem=512MB`, `max_wal_size=4GB`, `checkpoint_timeout=15min`, `wal_level=minimal`, `max_wal_senders=0`, `effective_io_concurrency=200`.
- **`sirene-etl`** (built from `sirene/Dockerfile`, `python:3.12-slim`):
  - Waits for `sirene-postgres` (`condition: service_healthy`).
  - Mounts `./staging:/app/staging` and `..:/workspace:ro`.
  - Connects via `DATABASE_URL=postgresql://${POSTGRES_USER:-sirene}:${POSTGRES_PASSWORD:-pg_sirene_ephemeral}@sirene-postgres:5432/${POSTGRES_DB:-sirene}`.
- **`sirene-watcher`** (`profiles: ["daemon"]`, `restart: unless-stopped`):
  - Activated explicitly with `--profile daemon` (or `make sirene-watch`) so unit/integration runs never spawn unsolicited background network polling.
  - Executes `python watcher.py` continuously.

### `Makefile` Targets Reference

| Target | Command Executed | Purpose |
| :--- | :--- | :--- |
| `make sirene-up` | `docker compose -f sirene/docker-compose.yml up -d sirene-postgres` | Start PostgreSQL 17 container in background |
| `make sirene-down` | `docker compose -f sirene/docker-compose.yml --profile daemon down` | Stop all Sirene Compose services including daemon |
| `make sirene-test` | `up -d --wait sirene-postgres`, `build sirene-etl`, `run --rm sirene-etl pytest -v` | Run full unit, live PostgreSQL 17 integration, and governance test suite |
| `make sirene-import` | `docker compose -f sirene/docker-compose.yml run --rm sirene-etl python full_import.py $(ARGS)` | Run initial full bulk import (pass custom flags via `ARGS="..."`) |
| `make sirene-incremental` | `docker compose -f sirene/docker-compose.yml run --rm sirene-etl python incremental_import.py $(ARGS)` | Run incremental delta sync inside a transaction |
| `make sirene-watch` | `docker compose -f sirene/docker-compose.yml --profile daemon up -d sirene-watcher` | Start autonomous `data.gouv.fr` watcher daemon |
| `make sirene-docs` | Prints paths to HTML reference and EN/FR Markdown guides | Display local entrypoints for Sirene technical documentation |

---

## 4. Catalog of 15 Analytical & Search SQL Queries

All 15 queries below are read-only **PostgreSQL 17** SQL statements matching `sirene/sql/03_sample_queries.sql` verbatim and verified to execute cleanly (`ON_ERROR_STOP=1`) against both sentinel-only and fully populated Sirene databases.

### Query 1 — Exact SIREN / SIRET Lookup (Legal Unit, Address, NAF, Legal Category, Workforce & WGS84)

Retrieves a complete company and establishment profile including normalized address, NAF label, legal form, headcount bracket, foreign country, Lambert-93 coordinates, and WGS84 coordinates.

```sql
SELECT
    ul.siren,
    e.siret,
    e.nic,
    e.etablissement_siege,
    ul.etat_administratif AS legal_unit_status,
    e.etat_administratif AS establishment_status,
    COALESCE(
        ul.denomination,
        TRIM(CONCAT_WS(' ', ul.nom_usage, ul.nom_naissance, ul.prenom_usuel))
    ) AS legal_unit_name,
    e.enseigne_1 AS trade_sign,
    cj.code_cj,
    cj.libelle AS legal_category,
    e.code_naf,
    n.libelle_sous_classe AS naf_activity_label,
    e.code_tranche_effectifs,
    te.libelle AS workforce_bracket,
    e.adresse_complete,
    c.code_commune,
    c.libelle AS municipality,
    d.code_departement,
    r.libelle AS region_name,
    p_ext.libelle AS foreign_country,
    e.coord_lambert_x,
    e.coord_lambert_y,
    e.longitude,
    e.latitude
FROM etablissements e
JOIN unites_legales ul
    ON ul.siren = e.siren
JOIN ref_categories_juridiques cj
    ON cj.code_cj = ul.code_cj
JOIN ref_naf n
    ON n.code_naf = e.code_naf
JOIN ref_tranches_effectifs te
    ON te.code_tranche = e.code_tranche_effectifs
JOIN ref_communes c
    ON c.code_commune = e.code_commune
JOIN ref_departements d
    ON d.code_departement = c.code_departement
JOIN ref_regions r
    ON r.code_region = d.code_region
LEFT JOIN ref_pays p_ext
    ON p_ext.code_pays = e.code_pays_etranger
WHERE ul.siren = '111111111'
   OR e.siret = '11111111100014'
ORDER BY
    e.etablissement_siege DESC,
    e.siret;
```

- **Index Usage**: Uses `idx_etab_siren`, `etablissements_pkey`, and `unites_legales_pkey` (prefer a single-predicate `WHERE ul.siren = ...` or `WHERE e.siret = ...` in OLTP APIs to avoid BitmapOr) followed by PK lookups across all 3NF referential dimensions.

---

### Query 2 — Active Establishments by NAF Division/Subclass in Target Regions + Linked Officers / Sole Proprietors

Lists active sites in a sector (`code_division = '62'` IT services, `'62.01Z'`, or `'00.00Z'` sentinel) within selected regions (`'11'`, `'76'`, `'84'`, `'UNK'`), aggregating active officers and sole proprietors.

```sql
SELECT
    ul.siren,
    e.siret,
    e.etablissement_siege,
    COALESCE(
        ul.denomination,
        TRIM(CONCAT_WS(' ', ul.nom_usage, ul.nom_naissance, ul.prenom_usuel))
    ) AS legal_unit_name,
    cj.libelle AS legal_category,
    e.code_naf,
    n.libelle_sous_classe AS activity_label,
    e.adresse_complete,
    c.libelle AS municipality,
    d.libelle AS department,
    r.libelle AS region,
    STRING_AGG(
        DISTINCT CONCAT_WS(' ', p.nom, p.prenoms, '(' || re.type_role || ')'),
        '; '
        ORDER BY CONCAT_WS(' ', p.nom, p.prenoms, '(' || re.type_role || ')')
    ) FILTER (WHERE p.id IS NOT NULL) AS officers_and_proprietors
FROM etablissements e
JOIN unites_legales ul
    ON ul.siren = e.siren
JOIN ref_naf n
    ON n.code_naf = e.code_naf
JOIN ref_categories_juridiques cj
    ON cj.code_cj = ul.code_cj
JOIN ref_communes c
    ON c.code_commune = e.code_commune
JOIN ref_departements d
    ON d.code_departement = c.code_departement
JOIN ref_regions r
    ON r.code_region = d.code_region
LEFT JOIN roles_entreprises re
    ON re.siren = ul.siren
   AND re.actif = TRUE
LEFT JOIN personnes p
    ON p.id = re.personne_id
WHERE e.etat_administratif = 'A'
  AND ul.etat_administratif = 'A'
  AND (n.code_division = '62' OR e.code_naf = '62.01Z' OR e.code_naf = '00.00Z')
  AND r.code_region IN ('11', '76', '84', 'UNK')
GROUP BY
    ul.siren,
    e.siret,
    e.etablissement_siege,
    ul.denomination,
    ul.nom_usage,
    ul.nom_naissance,
    ul.prenom_usuel,
    cj.libelle,
    e.code_naf,
    n.libelle_sous_classe,
    e.adresse_complete,
    c.libelle,
    d.libelle,
    r.libelle
ORDER BY
    e.etablissement_siege DESC,
    ul.siren,
    e.siret
LIMIT 50;
```

- **Index Usage**: Leverages `idx_etab_etat_administratif`, `idx_etab_code_naf` (or `idx_etab_naf_commune_actif`), `idx_ul_etat_administratif`, `idx_ref_departements_code_region`, `idx_ref_communes_code_departement`, and `idx_roles_siren`.

---

### Query 3 — Unified `pg_trgm` Fuzzy Search (`%` and `similarity()`) Across `nom_recherche`, `enseigne_recherche` & `nom_complet_recherche`

Separates each `%` trigram predicate into its own CTE branch so the PostgreSQL planner performs bitmap index scans on all three GIN indexes instead of falling back to sequential scans across `OR` clauses.

```sql
WITH search_params AS (
    SELECT 'ACME TECHNOLOGIE'::TEXT AS query_text
),
ul_matches AS (
    SELECT
        ul.siren,
        'LEGAL_UNIT'::TEXT AS match_source,
        ul.nom_recherche AS matched_text,
        similarity(ul.nom_recherche, sp.query_text) AS trgm_score
    FROM unites_legales ul
    CROSS JOIN search_params sp
    WHERE ul.nom_recherche % sp.query_text
),
etab_matches AS (
    SELECT
        e.siren,
        'ESTABLISHMENT_SIGN'::TEXT AS match_source,
        e.enseigne_recherche AS matched_text,
        similarity(e.enseigne_recherche, sp.query_text) AS trgm_score
    FROM etablissements e
    CROSS JOIN search_params sp
    WHERE e.enseigne_recherche % sp.query_text
),
person_matches AS (
    SELECT
        re.siren,
        'PERSON_ROLE'::TEXT AS match_source,
        p.nom_complet_recherche AS matched_text,
        similarity(p.nom_complet_recherche, sp.query_text) AS trgm_score
    FROM personnes p
    CROSS JOIN search_params sp
    JOIN roles_entreprises re
        ON re.personne_id = p.id
    WHERE p.nom_complet_recherche % sp.query_text
),
combined_matches AS (
    SELECT * FROM ul_matches
    UNION ALL
    SELECT * FROM etab_matches
    UNION ALL
    SELECT * FROM person_matches
)
SELECT
    cm.siren,
    ul.etat_administratif,
    ul.nom_recherche AS legal_unit_search_name,
    ul.code_naf,
    ROUND(MAX(cm.trgm_score)::NUMERIC, 4) AS best_similarity_score,
    ARRAY_AGG(DISTINCT cm.match_source ORDER BY cm.match_source) AS matched_dimensions,
    STRING_AGG(DISTINCT cm.matched_text, ' | ') AS matched_labels
FROM combined_matches cm
JOIN unites_legales ul
    ON ul.siren = cm.siren
GROUP BY
    cm.siren,
    ul.etat_administratif,
    ul.nom_recherche,
    ul.code_naf
ORDER BY
    best_similarity_score DESC,
    cm.siren
LIMIT 25;
```

- **Index Usage**: Directly utilizes all three `pg_trgm` GIN indexes (`idx_ul_nom_trgm`, `idx_etab_enseigne_trgm`, `idx_personnes_nom_trgm`) plus `idx_roles_personne_id` and `unites_legales_pkey`.

---

### Query 4 — Officer / Shareholder Corporate Portfolio Lookup (`roles_entreprises` + `personnes` + `siren_personne_morale`)

Inspects all corporate mandates and ownership links held by natural (`PHYSIQUE`) or legal (`MORALE`) actors, computing total active establishments and total mandates per actor.

```sql
WITH site_counts AS (
    SELECT
        siren,
        COUNT(*) FILTER (WHERE etat_administratif = 'A') AS active_sites
    FROM etablissements
    GROUP BY siren
)
SELECT
    p.id AS personne_id,
    p.type_personne,
    COALESCE(pm.denomination, TRIM(CONCAT_WS(' ', p.nom, p.prenoms))) AS actor_name,
    p.siren_personne_morale AS holding_siren,
    re.type_role,
    re.qualite_detaillee,
    re.pourcentage_detention,
    re.pourcentage_droits_vote,
    re.actif AS role_active,
    re.source_donnee,
    ul.siren AS target_siren,
    COALESCE(ul.denomination, ul.nom_recherche) AS target_company_name,
    ul.etat_administratif AS target_status,
    cj.libelle AS target_legal_category,
    n.code_naf AS target_naf,
    COALESCE(sc.active_sites, 0) AS target_active_sites,
    COUNT(*) OVER (PARTITION BY p.id) AS total_mandates_for_actor
FROM roles_entreprises re
JOIN personnes p
    ON p.id = re.personne_id
JOIN unites_legales ul
    ON ul.siren = re.siren
JOIN ref_categories_juridiques cj
    ON cj.code_cj = ul.code_cj
JOIN ref_naf n
    ON n.code_naf = ul.code_naf
LEFT JOIN unites_legales pm
    ON pm.siren = p.siren_personne_morale
LEFT JOIN site_counts sc
    ON sc.siren = ul.siren
ORDER BY
    total_mandates_for_actor DESC,
    actor_name,
    target_siren
LIMIT 100;
```

- **Index Usage**: Uses `idx_roles_personne_id`, `idx_roles_siren`, `idx_personnes_siren_pm`, `idx_etab_siren`, and `unites_legales_pkey` (and combines cleanly with `WHERE p.nom_complet_recherche % ...` via `idx_personnes_nom_trgm` when filtering by actor name).

---

### Query 5 — Sole Proprietors (`ENTREPRENEUR_INDIVIDUEL`) Directory by Department and NAF Activity

Lists active sole proprietors projected into `personnes`/`roles_entreprises`, ordered by department and NAF activity with their headquarters address.

```sql
SELECT
    d.code_departement,
    d.libelle AS department_name,
    n.code_naf,
    n.libelle_sous_classe AS naf_label,
    ul.siren,
    e.siret AS headquarters_siret,
    p.nom AS proprietor_last_name,
    COALESCE(p.prenom_usuel, p.prenoms) AS proprietor_first_name,
    e.adresse_complete,
    c.libelle AS municipality,
    ul.date_creation,
    re.actif AS role_active
FROM roles_entreprises re
JOIN personnes p
    ON p.id = re.personne_id
JOIN unites_legales ul
    ON ul.siren = re.siren
JOIN ref_naf n
    ON n.code_naf = ul.code_naf
LEFT JOIN etablissements e
    ON e.siren = ul.siren
   AND e.etablissement_siege = TRUE
LEFT JOIN ref_communes c
    ON c.code_commune = e.code_commune
LEFT JOIN ref_departements d
    ON d.code_departement = c.code_departement
WHERE re.type_role = 'ENTREPRENEUR_INDIVIDUEL'
  AND ul.etat_administratif = 'A'
ORDER BY
    d.code_departement,
    n.code_naf,
    p.nom,
    ul.siren
LIMIT 100;
```

- **Index Usage**: Uses `idx_ul_etat_administratif`, `idx_roles_siren`, `idx_roles_personne_id`, `idx_etab_siren`, `idx_etab_code_commune`, and `idx_ref_communes_code_departement`.

---

### Query 6 — WGS84 Bounding-Box + Haversine Radius Search (km) Alongside Lambert-93 Planar Distance

Finds active establishments within a `25.0` km radius around central Paris (`48.856600, 2.352200` / Lambert-93 `652469.02, 6862035.26`), pruning candidates via a bounding box before computing numerically safe Haversine (`LEAST(1.0, ...)`) and Euclidean Lambert-93 distances.

```sql
WITH geo_anchor AS (
    SELECT
        48.856600::DOUBLE PRECISION AS center_lat,
        2.352200::DOUBLE PRECISION AS center_lon,
        652469.02::DOUBLE PRECISION AS center_l93_x,
        6862035.26::DOUBLE PRECISION AS center_l93_y,
        25.0::DOUBLE PRECISION AS radius_km,
        0.25::DOUBLE PRECISION AS lat_delta,
        0.35::DOUBLE PRECISION AS lon_delta
),
candidate_sites AS (
    SELECT
        e.siret,
        e.siren,
        COALESCE(ul.denomination, ul.nom_recherche) AS legal_unit_name,
        e.enseigne_1,
        e.code_naf,
        e.adresse_complete,
        e.longitude,
        e.latitude,
        e.coord_lambert_x,
        e.coord_lambert_y,
        -- Numerically safe Haversine formula avoiding ACOS(>1.0) domain errors.
        (
            6371.0 * 2.0 * ASIN(
                SQRT(
                    LEAST(
                        1.0,
                        POWER(SIN(RADIANS(e.latitude - ga.center_lat) / 2.0), 2) +
                        COS(RADIANS(ga.center_lat)) * COS(RADIANS(e.latitude)) *
                        POWER(SIN(RADIANS(e.longitude - ga.center_lon) / 2.0), 2)
                    )
                )
            )
        ) AS haversine_km,
        CASE
            WHEN e.coord_lambert_x IS NOT NULL AND e.coord_lambert_y IS NOT NULL THEN
                SQRT(
                    POWER(e.coord_lambert_x::DOUBLE PRECISION - ga.center_l93_x, 2) +
                    POWER(e.coord_lambert_y::DOUBLE PRECISION - ga.center_l93_y, 2)
                ) / 1000.0
            ELSE NULL
        END AS lambert93_km,
        ga.radius_km
    FROM etablissements e
    JOIN unites_legales ul
        ON ul.siren = e.siren
    CROSS JOIN geo_anchor ga
    WHERE e.etat_administratif = 'A'
      AND e.latitude IS NOT NULL
      AND e.longitude IS NOT NULL
      AND e.latitude BETWEEN (ga.center_lat - ga.lat_delta) AND (ga.center_lat + ga.lat_delta)
      AND e.longitude BETWEEN (ga.center_lon - ga.lon_delta) AND (ga.center_lon + ga.lon_delta)
)
SELECT
    siret,
    siren,
    legal_unit_name,
    enseigne_1,
    code_naf,
    adresse_complete,
    longitude,
    latitude,
    ROUND(haversine_km::NUMERIC, 3) AS distance_wgs84_km,
    ROUND(lambert93_km::NUMERIC, 3) AS distance_lambert93_km
FROM candidate_sites
WHERE haversine_km <= radius_km
ORDER BY
    haversine_km ASC,
    siret
LIMIT 50;
```

- **Index Usage**: Uses `idx_etab_etat_administratif` and `unites_legales_pkey`; the bounding-box CTE filters candidates before computing `SIN`/`COS`/`SQRT`.

---

### Query 7 — NAF 5-Level Hierarchy Rollup (Section -> Division -> Groupe -> Classe -> Sous-classe)

Rolls up total establishments, active establishments, and distinct legal units across all five levels of the **NAF Rev. 2** hierarchy using `GROUP BY ROLLUP` and `GROUPING()`.

```sql
SELECT
    CASE
        WHEN GROUPING(n.code_section) = 1 THEN 'GRAND_TOTAL'
        WHEN GROUPING(n.code_division) = 1 THEN '1_SECTION'
        WHEN GROUPING(n.code_groupe) = 1 THEN '2_DIVISION'
        WHEN GROUPING(n.code_classe) = 1 THEN '3_GROUPE'
        WHEN GROUPING(n.code_naf) = 1 THEN '4_CLASSE'
        ELSE '5_SOUS_CLASSE'
    END AS hierarchy_level,
    n.code_section,
    n.libelle_section,
    n.code_division,
    n.libelle_division,
    n.code_groupe,
    n.code_classe,
    n.code_naf,
    n.libelle_sous_classe,
    COUNT(e.siret) AS total_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A') AS active_establishments,
    COUNT(DISTINCT e.siren) AS distinct_legal_units
FROM etablissements e
JOIN ref_naf n
    ON n.code_naf = e.code_naf
GROUP BY ROLLUP (
    (n.code_section, n.libelle_section),
    (n.code_division, n.libelle_division),
    (n.code_groupe, n.libelle_groupe),
    (n.code_classe, n.libelle_classe),
    (n.code_naf, n.libelle_sous_classe)
)
ORDER BY
    n.code_section NULLS LAST,
    n.code_division NULLS LAST,
    n.code_groupe NULLS LAST,
    n.code_classe NULLS LAST,
    n.code_naf NULLS LAST;
```

- **Index Usage**: Joins via `idx_etab_code_naf` and `ref_naf_pkey` (consider adding a `WHERE n.code_section = '...'` filter when drilling down interactively).

---

### Query 8 — Regional & Departmental Active vs. Closed Density and Minimum Headcount Floor (`SUM(effectif_min)`)

Computes geographic distribution across regions and departments, including active/closed establishment counts, headquarters counts, employing sites, minimum headcount floor (`SUM(effectif_min)`), and regional share percentage.

```sql
SELECT
    r.code_region,
    r.libelle AS region_name,
    d.code_departement,
    d.libelle AS department_name,
    COUNT(e.siret) AS total_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A') AS active_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'F') AS closed_establishments,
    COUNT(e.siret) FILTER (WHERE e.etablissement_siege) AS headquarters_count,
    COUNT(e.siret) FILTER (WHERE e.caractere_employeur = 'O' AND e.etat_administratif = 'A') AS active_employing_sites,
    COALESCE(SUM(COALESCE(te.effectif_min, 0)) FILTER (WHERE e.etat_administratif = 'A'), 0) AS min_headcount_floor,
    ROUND(
        100.0 * COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A')
        / NULLIF(SUM(COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A')) OVER (PARTITION BY r.code_region), 0),
        2
    ) AS pct_of_regional_active_sites
FROM ref_regions r
JOIN ref_departements d
    ON d.code_region = r.code_region
LEFT JOIN ref_communes c
    ON c.code_departement = d.code_departement
LEFT JOIN etablissements e
    ON e.code_commune = c.code_commune
LEFT JOIN ref_tranches_effectifs te
    ON te.code_tranche = e.code_tranche_effectifs
GROUP BY
    r.code_region,
    r.libelle,
    d.code_departement,
    d.libelle
ORDER BY
    active_establishments DESC,
    r.code_region,
    d.code_departement;
```

- **Index Usage**: Uses `idx_ref_departements_code_region`, `idx_ref_communes_code_departement`, `idx_etab_code_commune`, and `idx_etab_code_tranche_effectifs`.

---

### Query 9 — Enterprise Size Category (`PME`, `ETI`, `GE`), Legal Category Level 1, ESS & Mission-Driven Companies

Segments legal units by INSEE enterprise size category (`PME`, `ETI`, `GE`), top-level legal category (`code_niveau1`), Social & Solidarity Economy (`economie_sociale_solidaire = 'O'`), and mission-driven status (`societe_mission = 'O'`).

```sql
WITH estab_counts AS (
    SELECT
        siren,
        COUNT(*) AS total_sites,
        COUNT(*) FILTER (WHERE etat_administratif = 'A') AS active_sites
    FROM etablissements
    GROUP BY siren
)
SELECT
    COALESCE(ul.categorie_entreprise, 'UNSPECIFIED') AS enterprise_category,
    COALESCE(cj.code_niveau1, '0') AS legal_level1_code,
    COALESCE(cj.libelle_niveau1, cj.libelle) AS legal_level1_label,
    COUNT(ul.siren) AS total_legal_units,
    COUNT(ul.siren) FILTER (WHERE ul.etat_administratif = 'A') AS active_legal_units,
    COUNT(ul.siren) FILTER (WHERE ul.economie_sociale_solidaire = 'O') AS ess_units,
    COUNT(ul.siren) FILTER (WHERE ul.societe_mission = 'O') AS mission_driven_units,
    COALESCE(SUM(ec.active_sites), 0) AS total_active_establishments,
    ROUND(AVG(COALESCE(ec.active_sites, 0)), 2) AS avg_active_sites_per_unit
FROM unites_legales ul
JOIN ref_categories_juridiques cj
    ON cj.code_cj = ul.code_cj
LEFT JOIN estab_counts ec
    ON ec.siren = ul.siren
GROUP BY
    COALESCE(ul.categorie_entreprise, 'UNSPECIFIED'),
    COALESCE(cj.code_niveau1, '0'),
    COALESCE(cj.libelle_niveau1, cj.libelle)
ORDER BY
    active_legal_units DESC,
    enterprise_category,
    legal_level1_code;
```

- **Index Usage**: Uses `idx_ul_categorie_entreprise`, `idx_ul_code_cj`, `idx_ul_etat_administratif`, and `idx_etab_siren`.

---

### Query 10 — Top Multi-Establishment Corporate Networks (`COUNT(siret)` per `siren`)

Ranks multi-site corporate groups (`COUNT(e.siret) >= 2`) by active establishment footprint and departmental reach.

```sql
SELECT
    ul.siren,
    COALESCE(ul.denomination, ul.nom_recherche) AS legal_unit_name,
    ul.categorie_entreprise,
    cj.libelle AS legal_category,
    n.code_naf,
    n.libelle_sous_classe AS principal_activity,
    COUNT(e.siret) AS total_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A') AS active_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'F') AS closed_establishments,
    COUNT(DISTINCT c.code_departement) FILTER (WHERE e.etat_administratif = 'A') AS active_departments_covered,
    BOOL_OR(e.etablissement_siege) AS has_headquarters_site
FROM unites_legales ul
JOIN etablissements e
    ON e.siren = ul.siren
JOIN ref_categories_juridiques cj
    ON cj.code_cj = ul.code_cj
JOIN ref_naf n
    ON n.code_naf = ul.code_naf
JOIN ref_communes c
    ON c.code_commune = e.code_commune
GROUP BY
    ul.siren,
    ul.denomination,
    ul.nom_recherche,
    ul.categorie_entreprise,
    cj.libelle,
    n.code_naf,
    n.libelle_sous_classe
HAVING COUNT(e.siret) >= 2
ORDER BY
    active_establishments DESC,
    total_establishments DESC,
    ul.siren
LIMIT 50;
```

- **Index Usage**: Aggregates establishments via `idx_etab_siren`, joining `unites_legales_pkey` and `idx_etab_code_commune`.

---

### Query 11 — Administrative Closure / Reopening Churn Audit (`etablissements_historique_etat`)

Inspects the latest administrative status transitions captured by `incremental_import.py` in `etablissements_historique_etat`, distinguishing `'A' -> 'F'` closures from `'F' -> 'A'` reopenings and counting total transitions per `siret`.

```sql
WITH ranked_transitions AS (
    SELECT
        h.id AS history_id,
        h.siret,
        e.siren,
        COALESCE(ul.denomination, ul.nom_recherche) AS legal_unit_name,
        e.code_naf,
        n.libelle_sous_classe AS activity_label,
        c.libelle AS municipality,
        h.ancien_etat,
        h.nouvel_etat,
        h.date_effet,
        h.changed_at,
        l.run_type,
        l.file_name,
        COUNT(*) OVER (PARTITION BY h.siret) AS transitions_for_siret,
        ROW_NUMBER() OVER (
            PARTITION BY h.siret
            ORDER BY h.changed_at DESC, h.id DESC
        ) AS transition_rank
    FROM etablissements_historique_etat h
    JOIN etablissements e
        ON e.siret = h.siret
    JOIN unites_legales ul
        ON ul.siren = e.siren
    JOIN ref_naf n
        ON n.code_naf = e.code_naf
    JOIN ref_communes c
        ON c.code_commune = e.code_commune
    LEFT JOIN etl_logs l
        ON l.id = h.etl_log_id
)
SELECT
    history_id,
    siret,
    siren,
    legal_unit_name,
    code_naf,
    activity_label,
    municipality,
    ancien_etat,
    nouvel_etat,
    CASE
        WHEN ancien_etat = 'A' AND nouvel_etat = 'F' THEN 'CLOSURE'
        WHEN ancien_etat = 'F' AND nouvel_etat = 'A' THEN 'REOPENING'
        ELSE 'OTHER_TRANSITION'
    END AS transition_category,
    transitions_for_siret,
    date_effet,
    changed_at,
    run_type,
    file_name
FROM ranked_transitions
WHERE transition_rank = 1
ORDER BY
    changed_at DESC,
    history_id DESC
LIMIT 100;
```

- **Index Usage**: Uses `idx_etab_hist_siret`, `etablissements_pkey`, `unites_legales_pkey`, and `etl_logs_pkey`.

---

### Query 12 — Company Creation Cohorts and Survival / Longevity by Decade & Year

Analyzes legal unit survival rates, average age, and minimum active workforce floor grouped by creation decade and creation year.

```sql
SELECT
    (FLOOR(EXTRACT(YEAR FROM ul.date_creation) / 10.0) * 10)::INTEGER AS creation_decade,
    EXTRACT(YEAR FROM ul.date_creation)::INTEGER AS creation_year,
    COUNT(ul.siren) AS cohort_size,
    COUNT(ul.siren) FILTER (WHERE ul.etat_administratif = 'A') AS still_active_units,
    COUNT(ul.siren) FILTER (WHERE ul.etat_administratif = 'C') AS ceased_units,
    ROUND(
        100.0 * COUNT(ul.siren) FILTER (WHERE ul.etat_administratif = 'A')
        / NULLIF(COUNT(ul.siren), 0),
        2
    ) AS active_survival_rate_pct,
    ROUND(
        AVG(GREATEST(0.0, EXTRACT(YEAR FROM AGE(CURRENT_DATE, ul.date_creation))))::NUMERIC,
        1
    ) AS avg_age_years,
    COALESCE(SUM(COALESCE(te.effectif_min, 0)) FILTER (WHERE ul.etat_administratif = 'A'), 0) AS active_min_headcount_floor
FROM unites_legales ul
LEFT JOIN ref_tranches_effectifs te
    ON te.code_tranche = ul.code_tranche_effectifs
WHERE ul.date_creation IS NOT NULL
GROUP BY
    (FLOOR(EXTRACT(YEAR FROM ul.date_creation) / 10.0) * 10)::INTEGER,
    EXTRACT(YEAR FROM ul.date_creation)::INTEGER
ORDER BY
    creation_year DESC;
```

- **Index Usage**: Uses `idx_ul_etat_administratif` and `idx_ul_code_tranche_effectifs` alongside a single scan over `unites_legales`.

---

### Query 13 — Foreign-Located Establishments (`code_pays_etranger` + `ref_pays`)

Aggregates establishments located outside metropolitan/overseas France (`code_pays_etranger <> '99100'`) by country with ISO-2/ISO-3 codes and sample foreign city names.

```sql
SELECT
    rp.code_pays,
    rp.code_iso2,
    rp.code_iso3,
    rp.libelle AS country_name,
    COUNT(e.siret) AS total_foreign_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'A') AS active_foreign_establishments,
    COUNT(e.siret) FILTER (WHERE e.etat_administratif = 'F') AS closed_foreign_establishments,
    COUNT(DISTINCT e.siren) AS distinct_legal_units,
    STRING_AGG(DISTINCT e.libelle_commune_etranger, ', ' ORDER BY e.libelle_commune_etranger)
        FILTER (WHERE e.libelle_commune_etranger IS NOT NULL) AS sample_foreign_cities
FROM etablissements e
JOIN ref_pays rp
    ON rp.code_pays = e.code_pays_etranger
WHERE e.code_pays_etranger IS NOT NULL
  AND e.code_pays_etranger <> '99100'
GROUP BY
    rp.code_pays,
    rp.code_iso2,
    rp.code_iso3,
    rp.libelle
ORDER BY
    total_foreign_establishments DESC,
    rp.code_pays;
```

- **Index Usage**: Uses `idx_etab_code_pays_etranger` (B-Tree) to isolate foreign-located establishments plus `ref_pays_pkey`.

---

### Query 14 — Data Quality Audit: `[ND]` Partial Diffusion (`statut_diffusion = 'P'`) & Historical / Sentinel Referentials (`HIST` / `UNK`)

Quantifies privacy-masked (`statut_diffusion = 'P'`), sentinel (`UNK00`, `00.00Z`, `0000`, `UN`), historical (`HIST`), and orphan `'C'` placeholder records with percentages.

```sql
WITH quality_metrics AS (
    SELECT
        1 AS sort_order,
        'LEGAL_UNITS_PARTIAL_DIFFUSION_P'::TEXT AS metric_name,
        COUNT(*) FILTER (WHERE statut_diffusion = 'P') AS affected_rows,
        COUNT(*) AS total_scope_rows
    FROM unites_legales
    UNION ALL
    SELECT
        2,
        'ESTABLISHMENTS_PARTIAL_DIFFUSION_P',
        COUNT(*) FILTER (WHERE statut_diffusion = 'P'),
        COUNT(*)
    FROM etablissements
    UNION ALL
    SELECT
        3,
        'ESTABLISHMENTS_SENTINEL_COMMUNE_UNK00',
        COUNT(*) FILTER (WHERE code_commune = 'UNK00'),
        COUNT(*)
    FROM etablissements
    UNION ALL
    SELECT
        4,
        'ESTABLISHMENTS_HISTORICAL_OR_INACTIVE_COMMUNE',
        COUNT(*) FILTER (WHERE c.type_commune = 'HIST' OR c.est_active = FALSE),
        COUNT(*)
    FROM etablissements e
    JOIN ref_communes c
        ON c.code_commune = e.code_commune
    UNION ALL
    SELECT
        5,
        'ESTABLISHMENTS_HIST_OR_SENTINEL_NAF',
        COUNT(*) FILTER (WHERE n.nomenclature = 'HIST' OR n.code_naf = '00.00Z'),
        COUNT(*)
    FROM etablissements e
    JOIN ref_naf n
        ON n.code_naf = e.code_naf
    UNION ALL
    SELECT
        6,
        'LEGAL_UNITS_FALLBACK_CJ_0000_OR_TRANCHE_UN',
        COUNT(*) FILTER (WHERE code_cj = '0000' OR code_tranche_effectifs = 'UN'),
        COUNT(*)
    FROM unites_legales
    UNION ALL
    SELECT
        7,
        'LEGAL_UNITS_ORPHAN_PLACEHOLDER_C',
        COUNT(*) FILTER (
            WHERE etat_administratif = 'C'
              AND denomination IS NULL
              AND nom_naissance IS NULL
        ),
        COUNT(*)
    FROM unites_legales
)
SELECT
    metric_name,
    affected_rows,
    total_scope_rows,
    ROUND(100.0 * affected_rows / NULLIF(total_scope_rows, 0), 2) AS affected_pct
FROM quality_metrics
ORDER BY sort_order;
```

- **Index Usage**: Exploits `idx_etab_code_commune`, `idx_etab_code_naf`, `idx_ul_code_cj`, and `idx_ul_code_tranche_effectifs`.

---

### Query 15 — ETL Operational Health (`etl_logs` Throughput & SHA-256) + Table & Index Size Introspection (`pg_stat_user_tables`)

Combines latest `etl_logs` run health (throughput, duration, SHA-256 checksums, success/failure counts) with live PostgreSQL 17 table, index, and total relation storage sizes.

```sql
WITH latest_per_entity AS (
    SELECT
        id,
        run_type,
        entity_type,
        file_name,
        file_version,
        checksum_type,
        checksum_value,
        rows_processed,
        rows_inserted,
        rows_updated,
        status,
        started_at,
        finished_at,
        ROW_NUMBER() OVER (
            PARTITION BY entity_type
            ORDER BY started_at DESC, id DESC
        ) AS rn
    FROM etl_logs
),
entity_aggregates AS (
    SELECT
        entity_type,
        COUNT(*) AS total_runs,
        COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success_runs,
        COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
        COALESCE(SUM(rows_processed) FILTER (WHERE status = 'SUCCESS'), 0) AS cumulative_rows_processed,
        MAX(finished_at) FILTER (WHERE status = 'SUCCESS') AS last_success_at
    FROM etl_logs
    GROUP BY entity_type
),
etl_health AS (
    SELECT
        'ETL_RUN_HEALTH'::TEXT AS audit_scope,
        ea.entity_type AS subject_name,
        lp.run_type AS latest_run_type,
        lp.status AS latest_status,
        lp.file_name AS latest_file_name,
        lp.checksum_value AS latest_sha256_or_checksum,
        lp.rows_processed AS rows_or_live_tuples,
        lp.rows_inserted AS inserted_or_dead_tuples,
        lp.rows_updated AS updated_rows,
        ROUND(EXTRACT(EPOCH FROM (lp.finished_at - lp.started_at))::NUMERIC, 2) AS latest_duration_seconds,
        ea.total_runs,
        ea.success_runs,
        ea.failed_runs,
        ea.cumulative_rows_processed,
        NULL::TEXT AS table_size_pretty,
        NULL::TEXT AS indexes_size_pretty,
        NULL::TEXT AS total_size_pretty,
        ea.last_success_at AS last_event_or_analyze_at
    FROM entity_aggregates ea
    JOIN latest_per_entity lp
        ON lp.entity_type = ea.entity_type
       AND lp.rn = 1
),
table_storage AS (
    SELECT
        'PG_TABLE_STORAGE'::TEXT AS audit_scope,
        s.relname::TEXT AS subject_name,
        NULL::TEXT AS latest_run_type,
        NULL::TEXT AS latest_status,
        NULL::TEXT AS latest_file_name,
        NULL::TEXT AS latest_sha256_or_checksum,
        s.n_live_tup AS rows_or_live_tuples,
        s.n_dead_tup AS inserted_or_dead_tuples,
        NULL::BIGINT AS updated_rows,
        NULL::NUMERIC AS latest_duration_seconds,
        NULL::BIGINT AS total_runs,
        NULL::BIGINT AS success_runs,
        NULL::BIGINT AS failed_runs,
        NULL::BIGINT AS cumulative_rows_processed,
        pg_size_pretty(pg_relation_size(s.relid)) AS table_size_pretty,
        pg_size_pretty(pg_indexes_size(s.relid)) AS indexes_size_pretty,
        pg_size_pretty(pg_total_relation_size(s.relid)) AS total_size_pretty,
        GREATEST(s.last_analyze, s.last_autoanalyze) AS last_event_or_analyze_at
    FROM pg_stat_user_tables s
    WHERE s.schemaname = 'public'
)
SELECT *
FROM etl_health
UNION ALL
SELECT *
FROM table_storage
ORDER BY
    audit_scope,
    subject_name;
```

- **Index Usage**: Uses `idx_etl_logs_entity_status_finished` on `etl_logs` and reads PostgreSQL catalog statistics (`pg_stat_user_tables`, `pg_relation_size`, `pg_indexes_size`, `pg_total_relation_size`).

---

***
[🏠 Home](index.md) | [⬅️ Previous](gap_locking_experiment.md) | [Interactive HTML Reference](../sirene_documentation.html) | [🇫🇷 French Version](../fr/sirene_platform.md)
