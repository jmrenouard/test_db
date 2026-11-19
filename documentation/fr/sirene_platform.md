[🏠 Accueil](index.md) | [⬅️ Précédent](gap_locking_experiment.md) | [Référence HTML Interactive](../sirene_documentation.html) | [🇬🇧 Version Anglaise](../en/sirene_platform.md)
***

# Plateforme PostgreSQL 3NF Sirene

Le sous-système `sirene/` fournit un pipeline ETL **Python 3.12** et **PostgreSQL 17** prêt pour la production afin d'ingérer, normaliser en Troisième Forme Normale (3NF), géocoder et synchroniser en continu le répertoire **INSEE Sirene** des entreprises et établissements depuis les distributions Parquet et CSV/ZIP de `data.gouv.fr`.

> Pour explorer interactivement le modèle SVG, rechercher dans les colonnes et copier les requêtes SQL en un clic, ouvrez la [Référence HTML Interactive](../sirene_documentation.html) (`make sirene-docs`).

---

## 1. Architecture & Flux de Données ETL

Le pipeline sépare le **chargement des référentiels**, le **nettoyage en streaming par lots**, l'injection **haute performance via `COPY FROM STDIN`** et la **veille autonome par polling API**.

```mermaid
flowchart LR
    DG["API Dataset data.gouv.fr (Parquet / CSV / ZIP)"] -->|"HTTPS + Retries Tenacity"| DL["downloader.py (staging .part + SHA-256)"]
    COG["CSV INSEE COG 2026 & Parquet NAF Rév. 2"] -->|"CSV / PyArrow Parquet"| REF["referentials.py (référentiels 3NF + sentinelles)"]
    DL -->|"Lots en streaming"| TR["transforms.py (nettoyage [ND] + EPSG:2154 vers WGS84)"]
    TR -->|"Tuples nettoyés"| ING["full_import.py & incremental_import.py (COPY FROM STDIN + TEMP TABLE)"]
    REF -->|"Upserts UNNEST + Auto-FK HIST"| PG[("PostgreSQL 17 (Schéma 3NF + GIN pg_trgm)")]
    ING -->|"Fusion idempotente + Projection EI"| PG
    WATCH["watcher.py (--once / mode démon)"] -->|"Vérifie etl_logs & dispatche"| ING
    WATCH -.->|"Interroge les métadonnées"| DG
```

### Étapes du Pipeline

1. **Découverte des Ressources & Téléchargement Vérifié (`downloader.py`)** :
   - Interroge l'API du jeu de données `data.gouv.fr` (`DATAGOUV_DATASET_API`) pour identifier les fichiers courants `StockUniteLegale` et `StockEtablissement`, tout en excluant les archives `Historique`, `LiensSuccession` et `Doublon`.
   - Classe les formats selon `PREFERRED_FORMAT` (`parquet` par défaut, avec ordre de priorité `parquet > zip/csv.zip > csv.gz/gz > csv`).
   - Télécharge en streaming par blocs de 1 Mio (`1_048_576` octets) vers des fichiers temporaires `.part` avec backoff exponentiel `tenacity` (`stop_after_attempt(4)`, attente de 1 à 8 s), calcule l'empreinte `sha256`/`sha1`/`md5` à la volée, supprime tout `.part` corrompu en cas d'écart et remplace atomiquement le fichier cible.
2. **Initialisation des Référentiels & Protection Dynamique des Clés Étrangères (`referentials.py`)** :
   - Précharge de manière idempotente les référentiels intégrés : tranches d'effectifs (`NN`, `00`–`53`, `UN`), 18+ régions + `COM` + `UNK`, 101+ départements + `99` (étranger) + `20` (Corse historique) + `UNK`, catégories juridiques, codes NAF de repli et pays (`UNK`, `99100`).
   - En mode en ligne ou via `--ref-dir`, ingère le **COG 2026 complet de l'INSEE** (`v_region_2026.csv`, `v_departement_2026.csv`, `v_commune_2026.csv`, `v_commune_comer_2026.csv`, `v_commune_depuis_1943.csv`, `v_pays_territoire_2026.csv`) et la nomenclature **NAF Rév. 2** (`nafr2.parquet`).
   - Insère automatiquement en masse via `ensure_missing_referential_codes()` tout code historique ou obsolète non encore référencé (`nomenclature = 'HIST'`, `type_commune = 'HIST'`, `est_active = FALSE`) avant la fusion des entités principales, évitant toute violation de clé étrangère.
3. **Nettoyage des Lignes & Projection Lambert-93 vers WGS84 (`transforms.py`)** :
   - Lit en streaming les fichiers `.parquet` (`pyarrow.parquet.ParquetFile.iter_batches`), `.csv`, `.csv.gz` et `.zip` par lots configurables (`BATCH_SIZE`, `50_000` par défaut), en nettoyant les espaces parasites en fin d'en-tête CSV (comme `"coordonneeLambertAbscisseEtablissement "`).
   - Convertit `""`, `"null"`, `"[ND]"` et `"[nd]"` en `NULL` SQL, normalise les codes avec zéros initiaux (`code_cj` sur 4 caractères, `nic` sur 5 caractères, `code_tranche_effectifs` à 1 chiffre sur 2 chiffres) et concatène `prenom1UniteLegale`..`prenom4UniteLegale`.
   - Convertit les coordonnées planes **EPSG:2154 (Lambert-93, GRS80)** (`coord_lambert_x`, `coord_lambert_y`) en coordonnées géographiques **WGS84** (`longitude`, `latitude`, arrondies à 6 décimales) par itération au point fixe en Python pur (`12` itérations max, tolérance `1e-11` rad).
4. **Chargement Initial en Masse vs. Synchronisation Incrémentale Transactionnelle (`full_import.py`, `incremental_import.py`, `db.py`)** :
   - Acquiert le verrou consultatif de session PostgreSQL `84729101` (`pg_try_advisory_lock`) et contrôle l'idempotence via les empreintes enregistrées dans `etl_logs`.
   - `full_import.py` supprime les index secondaires non contraints (`drop_secondary_indexes()`), injecte les lots par `COPY ... FROM STDIN` (`psycopg` v3) dans des tables temporaires (`tmp_full_ul`, `tmp_full_etab`), garantit les clés étrangères et unités légales orphelines (`etat_administratif = 'C'`, `statut_diffusion = 'P'`), applique des upserts filtrés par `IS DISTINCT FROM`, projette les entrepreneurs individuels dans `personnes` et `roles_entreprises`, puis reconstruit les 25 index avec `ANALYZE`.
   - `incremental_import.py` s'exécute dans un bloc `conn.transaction()` unique avec tables temporaires `ON COMMIT DROP` (`tmp_inc_ul`, `tmp_inc_etab`), déduplique par clé primaire sur le dernier `date_dernier_traitement`, audite les transitions `'A' <-> 'F'` dans `etablissements_historique_etat`, protège les mises à jour par garde monotone (`COALESCE(EXCLUDED.date_dernier_traitement, 'infinity'::timestamptz) >= COALESCE(target.date_dernier_traitement, '-infinity'::timestamptz)`), préserve les `date_creation` non nulles et met à jour `roles_entreprises.actif`.
5. **Veille Autonome (`watcher.py`)** :
   - Compare `checksum_value`, `last_modified`, `resource_id`, `file_name` et `title` distants au dernier succès de `get_last_successful_import()` dans `etl_logs`.
   - Lance `run_full_import` si `unites_legales` est vide ou `run_incremental_import` sinon, en traçant chaque cycle avec `run_type = 'WATCHER_CHECK'`.

---

## 2. Modèle de Données 3NF PostgreSQL 17 & Index

Le schéma (`sirene/sql/01_schema_3nf.sql`) requiert **PostgreSQL 15+** (utilisation de `UNIQUE NULLS NOT DISTINCT` et de colonnes générées `STORED` immuables) ainsi que l'extension `pg_trgm`.

### Diagramme Entité-Relation (Les 13 Tables)

```mermaid
erDiagram
    ref_regions {
        varchar code_region PK "VARCHAR(3), sentinelle UNK"
        varchar cheflieu "VARCHAR(5)"
        varchar nom_majuscule "VARCHAR(100) NOT NULL"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    ref_departements {
        varchar code_departement PK "VARCHAR(4), sentinelle UNK"
        varchar code_region FK "REFERENCES ref_regions"
        varchar cheflieu "VARCHAR(5)"
        varchar nom_majuscule "VARCHAR(100) NOT NULL"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    ref_communes {
        varchar code_commune PK "VARCHAR(5), sentinelle UNK00"
        varchar code_departement FK "REFERENCES ref_departements"
        varchar type_commune "VARCHAR(6), defaut COM"
        varchar nom_majuscule "VARCHAR(150) NOT NULL"
        varchar libelle "VARCHAR(150) NOT NULL"
        boolean est_active "BOOLEAN, defaut TRUE"
    }
    ref_pays {
        varchar code_pays PK "VARCHAR(5), sentinelles UNK et 99100"
        char code_iso2 "CHAR(2)"
        char code_iso3 "CHAR(3)"
        varchar libelle "VARCHAR(150) NOT NULL"
    }
    ref_naf {
        varchar code_naf PK "VARCHAR(6), sentinelle 00.00Z"
        varchar nomenclature "VARCHAR(12), defaut NAFRev2"
        varchar code_section "VARCHAR(2)"
        varchar code_division "VARCHAR(2)"
        varchar code_groupe "VARCHAR(4)"
        varchar code_classe "VARCHAR(5)"
        varchar libelle_sous_classe "VARCHAR(255) NOT NULL"
    }
    ref_categories_juridiques {
        varchar code_cj PK "VARCHAR(4), sentinelle 0000"
        varchar code_niveau1 "VARCHAR(1)"
        varchar code_niveau2 "VARCHAR(2)"
        varchar libelle "VARCHAR(255) NOT NULL"
    }
    ref_tranches_effectifs {
        varchar code_tranche PK "VARCHAR(2), sentinelles NN et UN"
        integer effectif_min "INTEGER"
        integer effectif_max "INTEGER"
        varchar libelle "VARCHAR(120) NOT NULL"
    }
    unites_legales {
        varchar siren PK "VARCHAR(9), 9 chiffres"
        char etat_administratif "CHAR(1), A ou C"
        char statut_diffusion "CHAR(1), defaut O"
        varchar denomination "VARCHAR(255)"
        varchar categorie_entreprise "PME, ETI ou GE"
        varchar code_cj FK "defaut 0000"
        varchar code_naf FK "defaut 00.00Z"
        varchar code_tranche_effectifs FK "defaut NN"
        text nom_recherche "GENERATED STORED"
        timestamptz updated_at "NOT NULL DEFAULT NOW()"
    }
    etablissements {
        varchar siret PK "VARCHAR(14), 14 chiffres"
        varchar siren FK "ON DELETE CASCADE"
        varchar nic "VARCHAR(5) NOT NULL"
        boolean etablissement_siege "DEFAULT FALSE"
        char etat_administratif "CHAR(1), A ou F"
        varchar code_naf FK "defaut 00.00Z"
        varchar code_tranche_effectifs FK "defaut NN"
        varchar code_commune FK "defaut UNK00"
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
        bigint etl_log_id "Reference audit"
    }
    personnes {
        bigserial id PK "BIGSERIAL"
        varchar type_personne "PHYSIQUE ou MORALE"
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
        varchar type_role "9 roles autorises"
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
        jsonb metadata "DEFAULT objet vide"
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

### Catalogue Complet des Tables (13 Tables)

#### A. Tables de Référentiels 3NF (7 Tables)

| Table | Clé Primaire | Clés Étrangères | Colonnes & Contraintes Principales |
| :--- | :--- | :--- | :--- |
| `ref_regions` | `code_region VARCHAR(3)` | — | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` |
| `ref_departements` | `code_departement VARCHAR(4)` | `code_region` -> `ref_regions(code_region)` | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` |
| `ref_communes` | `code_commune VARCHAR(5)` | `code_departement` -> `ref_departements(code_departement)` | `type_commune VARCHAR(6) NOT NULL DEFAULT 'COM'`, `nom_majuscule VARCHAR(150) NOT NULL`, `libelle VARCHAR(150) NOT NULL`, `est_active BOOLEAN NOT NULL DEFAULT TRUE` |
| `ref_pays` | `code_pays VARCHAR(5)` | — | `code_iso2 CHAR(2)`, `code_iso3 CHAR(3)`, `libelle VARCHAR(150) NOT NULL` |
| `ref_naf` | `code_naf VARCHAR(6)` | — | `nomenclature VARCHAR(12) NOT NULL DEFAULT 'NAFRev2'`, `code_section VARCHAR(2)`, `libelle_section VARCHAR(255)`, `code_division VARCHAR(2)`, `libelle_division VARCHAR(255)`, `code_groupe VARCHAR(4)`, `libelle_groupe VARCHAR(255)`, `code_classe VARCHAR(5)`, `libelle_classe VARCHAR(255)`, `libelle_sous_classe VARCHAR(255) NOT NULL` |
| `ref_categories_juridiques` | `code_cj VARCHAR(4)` | — | `code_niveau1 VARCHAR(1)`, `libelle_niveau1 VARCHAR(255)`, `code_niveau2 VARCHAR(2)`, `libelle_niveau2 VARCHAR(255)`, `libelle VARCHAR(255) NOT NULL` |
| `ref_tranches_effectifs` | `code_tranche VARCHAR(2)` | — | `effectif_min INTEGER`, `effectif_max INTEGER`, `libelle VARCHAR(120) NOT NULL` |

#### B. Entités Centrales SIRENE & Historique d'État (3 Tables)

1. **`unites_legales`** (`siren VARCHAR(9) PRIMARY KEY CHECK (siren ~ '^[0-9]{9}$')`) :
   - **Statut & Cycle de Vie** : `statut_diffusion CHAR(1) NOT NULL DEFAULT 'O'`, `unite_purgee BOOLEAN NOT NULL DEFAULT FALSE`, `etat_administratif CHAR(1) NOT NULL CHECK (etat_administratif IN ('A', 'C'))`, `date_creation DATE`, `date_debut_periode DATE`, `date_dernier_traitement TIMESTAMPTZ`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - **Identité & Dénomination** : `denomination VARCHAR(255)`, `sigle VARCHAR(50)`, `denomination_usuelle_1 VARCHAR(150)`, `denomination_usuelle_2 VARCHAR(150)`, `denomination_usuelle_3 VARCHAR(150)`, `nom_naissance VARCHAR(150)`, `nom_usage VARCHAR(150)`, `prenom_usuel VARCHAR(100)`, `prenoms VARCHAR(255)`, `pseudonyme VARCHAR(150)`, `sexe CHAR(1)`, `identifiant_association VARCHAR(20)`, `nom_recherche TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Classification & Attributs** : `categorie_entreprise VARCHAR(5) CHECK (categorie_entreprise IS NULL OR categorie_entreprise IN ('PME', 'ETI', 'GE'))`, `annee_categorie_entreprise SMALLINT`, `code_cj VARCHAR(4) NOT NULL DEFAULT '0000' REFERENCES ref_categories_juridiques(code_cj)`, `code_naf VARCHAR(6) NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf)`, `nomenclature_activite VARCHAR(15)`, `code_naf_2025 VARCHAR(6)`, `code_tranche_effectifs VARCHAR(2) NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche)`, `annee_effectifs SMALLINT`, `nic_siege VARCHAR(5)`, `economie_sociale_solidaire CHAR(1)`, `societe_mission CHAR(1)`, `caractere_employeur CHAR(1)`.

2. **`etablissements`** (`siret VARCHAR(14) PRIMARY KEY CHECK (siret ~ '^[0-9]{14}$')`) :
   - **Identité & Cycle de Vie** : `siren VARCHAR(9) NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE`, `nic VARCHAR(5) NOT NULL`, `etablissement_siege BOOLEAN NOT NULL DEFAULT FALSE`, `statut_diffusion CHAR(1) NOT NULL DEFAULT 'O'`, `etat_administratif CHAR(1) NOT NULL CHECK (etat_administratif IN ('A', 'F'))`, `date_creation DATE`, `date_debut_periode DATE`, `date_dernier_traitement TIMESTAMPTZ`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - **Activité & Effectifs** : `enseigne_1 VARCHAR(150)`, `enseigne_2 VARCHAR(150)`, `enseigne_3 VARCHAR(150)`, `denomination_usuelle VARCHAR(150)`, `code_naf VARCHAR(6) NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf)`, `nomenclature_activite VARCHAR(15)`, `code_naf_2025 VARCHAR(6)`, `activite_artisanale VARCHAR(15)`, `code_tranche_effectifs VARCHAR(2) NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche)`, `annee_effectifs SMALLINT`, `caractere_employeur CHAR(1)`, `enseigne_recherche TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Adresse Postale & Étrangère** : `numero_voie VARCHAR(20)`, `indice_repetition VARCHAR(15)`, `type_voie VARCHAR(40)`, `libelle_voie VARCHAR(150)`, `complement_adresse VARCHAR(150)`, `distribution_speciale VARCHAR(50)`, `code_postal VARCHAR(15)`, `libelle_commune VARCHAR(150)`, `code_commune VARCHAR(5) NOT NULL DEFAULT 'UNK00' REFERENCES ref_communes(code_commune)`, `code_cedex VARCHAR(20)`, `libelle_cedex VARCHAR(120)`, `code_pays_etranger VARCHAR(5) REFERENCES ref_pays(code_pays)`, `libelle_commune_etranger VARCHAR(150)`, `adresse_complete TEXT GENERATED ALWAYS AS (...) STORED`.
   - **Géolocalisation** : `identifiant_adresse_ban VARCHAR(30)`, `coord_lambert_x NUMERIC(12, 2)`, `coord_lambert_y NUMERIC(12, 2)`, `longitude DOUBLE PRECISION`, `latitude DOUBLE PRECISION`.

3. **`etablissements_historique_etat`** (`id BIGSERIAL PRIMARY KEY`) :
   - Colonnes : `siret VARCHAR(14) NOT NULL REFERENCES etablissements(siret) ON DELETE CASCADE`, `ancien_etat CHAR(1) NOT NULL`, `nouvel_etat CHAR(1) NOT NULL`, `date_effet DATE`, `changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `etl_log_id BIGINT`.

#### C. Gouvernance & Entrepreneurs Individuels (2 Tables)

1. **`personnes`** (`id BIGSERIAL PRIMARY KEY`) :
   - Colonnes : `type_personne VARCHAR(10) NOT NULL CHECK (type_personne IN ('PHYSIQUE', 'MORALE'))`, `nom VARCHAR(150)`, `prenoms VARCHAR(255)`, `prenom_usuel VARCHAR(100)`, `sexe CHAR(1)`, `date_naissance DATE`, `siren_personne_morale VARCHAR(9) REFERENCES unites_legales(siren) ON DELETE SET NULL`, `cle_deduplication VARCHAR(128) NOT NULL UNIQUE`, `nom_complet_recherche TEXT GENERATED ALWAYS AS (...) STORED`, `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   - Les entrepreneurs individuels projetés lors des imports utilisent la clé SHA-256 déterministe `encode(sha256(convert_to('SIRENE_EI|' || ul.siren, 'UTF8')), 'hex')`.

2. **`roles_entreprises`** (`id BIGSERIAL PRIMARY KEY`) :
   - Colonnes : `siren VARCHAR(9) NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE`, `personne_id BIGINT NOT NULL REFERENCES personnes(id) ON DELETE CASCADE`, `type_role VARCHAR(40) NOT NULL`, `qualite_detaillee VARCHAR(150)`, `pourcentage_detention NUMERIC(5, 2) CHECK (pourcentage_detention IS NULL OR (pourcentage_detention >= 0 AND pourcentage_detention <= 100))`, `pourcentage_droits_vote NUMERIC(5, 2) CHECK (pourcentage_droits_vote IS NULL OR (pourcentage_droits_vote >= 0 AND pourcentage_droits_vote <= 100))`, `date_debut DATE`, `date_fin DATE`, `actif BOOLEAN NOT NULL DEFAULT TRUE`, `source_donnee VARCHAR(30) NOT NULL DEFAULT 'SIRENE'`.
   - Valeurs autorisées pour `type_role` : `'ENTREPRENEUR_INDIVIDUEL'`, `'GERANT'`, `'PRESIDENT'`, `'DIRECTEUR_GENERAL'`, `'ADMINISTRATEUR'`, `'ASSOCIE'`, `'ACTIONNAIRE'`, `'BENEFICIAIRE_EFFECTIF'`, `'AUTRE'`.
   - Contrainte d'unicité PostgreSQL 15+ : `UNIQUE NULLS NOT DISTINCT (siren, personne_id, type_role, date_debut)`.

#### D. Observabilité ETL & Registre des Empreintes (1 Table)

1. **`etl_logs`** (`id BIGSERIAL PRIMARY KEY`) :
   - Colonnes : `run_type VARCHAR(30) NOT NULL CHECK (run_type IN ('REFERENTIALS', 'FULL_IMPORT', 'INCREMENTAL_IMPORT', 'WATCHER_CHECK'))`, `entity_type VARCHAR(40) NOT NULL`, `resource_id VARCHAR(100)`, `source_url TEXT`, `file_name VARCHAR(255)`, `file_version VARCHAR(64)`, `checksum_type VARCHAR(16)`, `checksum_value VARCHAR(128)`, `rows_processed BIGINT NOT NULL DEFAULT 0`, `rows_inserted BIGINT NOT NULL DEFAULT 0`, `rows_updated BIGINT NOT NULL DEFAULT 0`, `status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED'))`, `started_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `finished_at TIMESTAMPTZ`, `error_message TEXT`, `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`.

### Colonnes Générées (`STORED`)

PostgreSQL impose que les colonnes `GENERATED ALWAYS AS (...) STORED` n'utilisent que des opérateurs `IMMUTABLE`. Comme `CONCAT_WS` est `STABLE` (et non `IMMUTABLE`), `01_schema_3nf.sql` assemble les chaînes normalisées avec `TRIM(...)`, `COALESCE(...)`, `NULLIF(...)` et `||` :

| Table | Colonne | Expression Générée | Rôle |
| :--- | :--- | :--- | :--- |
| `unites_legales` | `nom_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(denomination), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(sigle), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(denomination_usuelle_1), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(COALESCE(NULLIF(TRIM(nom_usage), ''), nom_naissance)), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(prenom_usuel), ''), ''))` | Projection textuelle des unités légales / personnes physiques indexée par `idx_ul_nom_trgm` |
| `etablissements` | `adresse_complete` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(numero_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(indice_repetition), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(type_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(libelle_voie), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(complement_adresse), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(code_postal), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(COALESCE(NULLIF(TRIM(libelle_commune), ''), libelle_commune_etranger)), ''), ''))` | Adresse postale normalisée (France ou étranger) |
| `etablissements` | `enseigne_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(enseigne_1), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(enseigne_2), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(enseigne_3), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(denomination_usuelle), ''), ''))` | Projection des enseignes indexée par `idx_etab_enseigne_trgm` |
| `personnes` | `nom_complet_recherche` | `TRIM(COALESCE(' ' \|\| NULLIF(TRIM(nom), ''), '') \|\| COALESCE(' ' \|\| NULLIF(TRIM(prenoms), ''), ''))` | Projection des dirigeants et entrepreneurs indexée par `idx_personnes_nom_trgm` |

### Valeurs Sentinelles & Protection Historique des Clés Étrangères

Pour empêcher tout rejet par contrainte d'intégrité sur les stocks historiques (unités purgées, champs masqués `[ND]`, anciennes communes fusionnées ou codes obsolètes), `01_schema_3nf.sql` insère de façon idempotente des lignes sentinelles (`ON CONFLICT DO NOTHING`) :

| Table | Clé(s) Sentinelle(s) | Clé Étrangère par Défaut | Signification |
| :--- | :--- | :--- | :--- |
| `ref_regions` | `'UNK'` | `ref_departements.code_region` | Région inconnue ou non précisée |
| `ref_departements` | `'UNK'` | `ref_communes.code_departement` (`code_region = 'UNK'`) | Département inconnu ou non précisé |
| `ref_communes` | `'UNK00'` | `etablissements.code_commune DEFAULT 'UNK00'` | Commune inconnue ou non précisée (`est_active = FALSE`) |
| `ref_pays` | `'UNK'`, `'99100'` | `etablissements.code_pays_etranger` (nullable) | Pays inconnu (`UNK`) et France (`99100`, `FR`, `FRA`) |
| `ref_naf` | `'00.00Z'` | `unites_legales.code_naf` & `etablissements.code_naf DEFAULT '00.00Z'` | Activité principale inconnue ou non précisée |
| `ref_categories_juridiques` | `'0000'` | `unites_legales.code_cj DEFAULT '0000'` | Catégorie juridique inconnue ou non précisée |
| `ref_tranches_effectifs` | `'NN'`, `'UN'` | `unites_legales.code_tranche_effectifs` & `etablissements.code_tranche_effectifs DEFAULT 'NN'` | `NN` : unité non employeuse ; `UN` : effectif masqué (`[ND]`) |

De plus, `referentials.py` (`ensure_missing_referential_codes()`) enregistre automatiquement tout code historique rencontré pendant l'ingestion avec `nomenclature = 'HIST'` (`ref_naf`), `type_commune = 'HIST'` et `est_active = FALSE` (`ref_communes`), ou `'Historical or unlisted ...'` (`ref_categories_juridiques`, `ref_pays`).

### Index Secondaires & Recherche Floue (25 Index dans `sirene/sql/02_indexes.sql`)

| Nom de l'Index | Table | Définition / Colonnes | Type |
| :--- | :--- | :--- | :--- |
| `idx_ref_departements_code_region` | `ref_departements` | `(code_region)` | B-Tree (FK) |
| `idx_ref_communes_code_departement` | `ref_communes` | `(code_departement)` | B-Tree (FK) |
| `idx_ul_code_cj` | `unites_legales` | `(code_cj)` | B-Tree (FK) |
| `idx_ul_code_naf` | `unites_legales` | `(code_naf)` | B-Tree (FK) |
| `idx_ul_code_tranche_effectifs` | `unites_legales` | `(code_tranche_effectifs)` | B-Tree (FK) |
| `idx_ul_etat_administratif` | `unites_legales` | `(etat_administratif)` | B-Tree (Filtre) |
| `idx_ul_categorie_entreprise` | `unites_legales` | `(categorie_entreprise)` | B-Tree (Filtre) |
| `idx_ul_date_dernier_traitement` | `unites_legales` | `(date_dernier_traitement)` | B-Tree (Temporel) |
| `idx_etab_siren` | `etablissements` | `(siren)` | B-Tree (FK) |
| `idx_etab_code_commune` | `etablissements` | `(code_commune)` | B-Tree (FK) |
| `idx_etab_code_naf` | `etablissements` | `(code_naf)` | B-Tree (FK) |
| `idx_etab_code_tranche_effectifs` | `etablissements` | `(code_tranche_effectifs)` | B-Tree (FK) |
| `idx_etab_code_pays_etranger` | `etablissements` | `(code_pays_etranger)` | B-Tree (FK) |
| `idx_etab_code_postal` | `etablissements` | `(code_postal)` | B-Tree (Filtre) |
| `idx_etab_etat_administratif` | `etablissements` | `(etat_administratif)` | B-Tree (Filtre) |
| `idx_etab_date_dernier_traitement` | `etablissements` | `(date_dernier_traitement)` | B-Tree (Temporel) |
| `idx_etab_naf_commune_actif` | `etablissements` | `(code_naf, code_commune) WHERE etat_administratif = 'A'` | B-Tree Composite Partiel |
| `idx_etab_hist_siret` | `etablissements_historique_etat` | `(siret)` | B-Tree (FK) |
| `idx_personnes_siren_pm` | `personnes` | `(siren_personne_morale)` | B-Tree (FK) |
| `idx_roles_siren` | `roles_entreprises` | `(siren)` | B-Tree (FK) |
| `idx_roles_personne_id` | `roles_entreprises` | `(personne_id)` | B-Tree (FK) |
| `idx_etl_logs_entity_status_finished` | `etl_logs` | `(entity_type, status, finished_at DESC)` | B-Tree Composite |
| `idx_ul_nom_trgm` | `unites_legales` | `USING GIN (nom_recherche gin_trgm_ops) WITH (fastupdate = on)` | GIN `pg_trgm` |
| `idx_etab_enseigne_trgm` | `etablissements` | `USING GIN (enseigne_recherche gin_trgm_ops) WITH (fastupdate = on)` | GIN `pg_trgm` |
| `idx_personnes_nom_trgm` | `personnes` | `USING GIN (nom_complet_recherche gin_trgm_ops) WITH (fastupdate = on)` | GIN `pg_trgm` |

---

## 3. Scripts Python, Référence CLI & Opérations Docker

### Points d'Entrée CLI (`sirene/`)

Chaque script wrapper ajoute `sirene/src/` à `sys.path` afin d'être exécutable directement en Python ou dans Docker Compose.

#### 1. `sirene/full_import.py` (`sirene_etl.full_import:main`)

Exécute l'import initial idempotent du stock complet avec suppression/reconstruction des index secondaires et `ANALYZE`.

| Option CLI | Type | Défaut | Description |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (API) | Fichier local `StockUniteLegale` (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (API) | Fichier local `StockEtablissement` (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--ref-dir` | `Path` | `None` | Répertoire local contenant les CSV COG 2026 et `nafr2.parquet` |
| `--offline-refs` | Flag | `False` | Utilise uniquement les référentiels intégrés sans appels HTTP |
| `--limit-rows` | `int` | `None` | Nombre maximal de lignes lues par fichier d'entité |
| `--force` | Flag | `False` | Force le ré-import même si les empreintes figurent déjà en `SUCCESS` dans `etl_logs` |

```bash
python sirene/full_import.py --offline-refs --limit-rows 10000
python sirene/full_import.py --ul-file staging/ul.parquet --etab-file staging/etab.parquet --force
```

#### 2. `sirene/incremental_import.py` (`sirene_etl.incremental_import:main`)

Exécute une synchronisation différentielle transactionnelle avec garde monotone sur `date_dernier_traitement` et journalisation des transitions `'A' <-> 'F'`.

| Option CLI | Type | Défaut | Description |
| :--- | :--- | :--- | :--- |
| `--ul-file` | `Path` | `None` (API) | Fichier delta local `StockUniteLegale` (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--etab-file` | `Path` | `None` (API) | Fichier delta local `StockEtablissement` (`.parquet`, `.csv`, `.csv.gz`, `.zip`) |
| `--force` | Flag | `False` | Ré-applique les deltas même si les empreintes ont déjà réussi dans `etl_logs` |

```bash
python sirene/incremental_import.py --etab-file staging/delta_etab.csv.gz
```

#### 3. `sirene/watcher.py` (`sirene_etl.watcher:main`)

Surveille l'API `data.gouv.fr`, compare les empreintes/horodatages/ID/noms de fichiers à `etl_logs` et déclenche `full_import.py` (si `unites_legales` est vide) ou `incremental_import.py` (si la base est déjà peuplée).

| Option CLI | Type | Défaut | Description |
| :--- | :--- | :--- | :--- |
| `--once` | Flag | `False` | Exécute un cycle unique de vérification/synchronisation et quitte |
| `--interval` | `int` | `WATCHER_INTERVAL_SECONDS` | Surcharge l'intervalle d'interrogation (en secondes) en mode démon |
| `--force` | Flag | `False` | Force le téléchargement et l'exécution ETL même si les métadonnées sont inchangées |
| `--offline-refs` | Flag | `False` | Utilise les référentiels hors ligne lors d'un premier chargement complet |

```bash
python sirene/watcher.py --once --offline-refs
python sirene/watcher.py --interval 1800
```

### Modules Internes de la Bibliothèque (`sirene/src/sirene_etl/`)

| Module | Symboles Clés | Responsabilité Principale |
| :--- | :--- | :--- |
| `__init__.py` | `__version__` (`"1.9.0"`) | Export de la version du package |
| `config.py` | `Settings`, `load_settings()` | Dataclass immuable chargée depuis `.env` et les variables d'environnement |
| `logging_utils.py` | `JsonLineFormatter`, `get_logger()` | Journalisation JSON compacte horodatée UTC sur `sys.stdout` |
| `db.py` | `get_connection()`, `acquire_etl_lock()`, `release_etl_lock()`, `apply_sql_file()`, `drop_secondary_indexes()`, `rebuild_indexes_and_analyze()`, `start_etl_log()`, `finish_etl_log()`, `is_checksum_already_imported()`, `get_last_successful_import()` | Connexions `psycopg` v3, verrou consultatif (`84729101`), exécution SQL, gestion des index et journal `etl_logs` |
| `downloader.py` | `compute_file_checksum()`, `extract_sirene_resources_from_payload()`, `fetch_datagouv_sirene_resources()`, `download_with_verification()` | Résolution API `data.gouv.fr`, téléchargement `httpx` + `tenacity` vers `.part`, vérification SHA-256/SHA-1/MD5 |
| `referentials.py` | `seed_all_referentials()`, `ensure_missing_referential_codes()`, `BUILTIN_*` | Référentiels intégrés + CSV COG 2026 + Parquet `nafr2.parquet` et protection dynamique `HIST` |
| `transforms.py` | `clean_sirene_str()`, `parse_date()`, `parse_timestamp()`, `parse_int()`, `parse_float()`, `parse_bool()`, `lambert93_to_wgs84()`, `iter_records_from_file()`, `transform_unite_legale_row()`, `transform_etablissement_row()` | Streaming multi-format, filtrage `[ND]`, conversion Lambert-93 -> WGS84, projection des tuples |
| `full_import.py` | `run_full_import()`, `main()` | Verrou consultatif, DDL/référentiels, drop/rebuild d'index, `COPY FROM STDIN`, upsert `IS DISTINCT FROM`, projection EI |
| `incremental_import.py` | `run_incremental_import()`, `main()` | Transaction unique `ON COMMIT DROP` via `COPY FROM STDIN`, déduplication PK, audit `etablissements_historique_etat`, garde monotone |
| `watcher.py` | `check_and_sync_once()`, `run_daemon()`, `main()` | Comparaison des métadonnées contre `etl_logs`, gestion `SIGINT`/`SIGTERM`, dispatch complet ou incrémental |

### Variables d'Environnement

| Variable | Valeur par Défaut | Rôle |
| :--- | :--- | :--- |
| `POSTGRES_USER` | `sirene` | Rôle PostgreSQL du conteneur |
| `POSTGRES_PASSWORD` | `pg_sirene_ephemeral` | Mot de passe éphémère de laboratoire (ne jamais commiter de secrets réels) |
| `POSTGRES_DB` | `sirene` | Nom de la base de données cible |
| `POSTGRES_HOST_PORT` | `15432` | Port loopback hôte mappé vers `5432` (évite tout conflit avec un PostgreSQL local sur `5432`) |
| `DATABASE_URL` | `postgresql://sirene:pg_sirene_ephemeral@localhost:15432/sirene` | Chaîne DSN côté hôte (`sirene-postgres:5432` dans Docker Compose) |
| `STAGING_DIR` | `./staging` | Répertoire de staging `.part` et cache des référentiels |
| `SQL_DIR` | `<racine_package>/sql` | Répertoire contenant `01_schema_3nf.sql` et `02_indexes.sql` |
| `BATCH_SIZE` | `50000` | Taille des lots transmis via `COPY FROM STDIN` |
| `WATCHER_INTERVAL_SECONDS` | `3600` | Intervalle de polling en mode démon (secondes) |
| `PREFERRED_FORMAT` | `parquet` | Format prioritaire sur `data.gouv.fr` |
| `LOG_LEVEL` | `INFO` | Niveau de verbosité du logger JSON (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATAGOUV_DATASET_API` | `https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/` | URL de l'API métadonnées `data.gouv.fr` |
| `COG_REGIONS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_region_2026.csv` | CSV COG 2026 des régions INSEE |
| `COG_DEPARTEMENTS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv` | CSV COG 2026 des départements INSEE |
| `COG_COMMUNES_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv` | CSV COG 2026 des communes actives INSEE |
| `COG_COMMUNES_HIST_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv` | CSV historique des communes depuis 1943 |
| `COG_COMER_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_comer_2026.csv` | CSV des collectivités d'outre-mer (`COMER`) |
| `COG_PAYS_URL` | `https://www.insee.fr/fr/statistiques/fichier/8740222/v_pays_territoire_2026.csv` | CSV des pays et territoires INSEE |
| `NAF_PARQUET_URL` | `https://static.data.gouv.fr/resources/naf-1/20231123-121750/nafr2.parquet` | Fichier Parquet officiel NAF Rév. 2 |

### Services Docker Compose, Profils & Réglages PostgreSQL 17

Définis dans `sirene/docker-compose.yml` :

- **`sirene-postgres`** (`postgres:17-bookworm`, `shm_size: 1gb`) :
  - Expose `127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432`.
  - Monte `./sql:/docker-entrypoint-initdb.d:ro` (initialise `01_schema_3nf.sql` et `02_indexes.sql` au premier démarrage) ainsi que `sirene_pgdata:/var/lib/postgresql/data`.
  - Healthcheck : `pg_isready -U $${POSTGRES_USER:-sirene} -d $${POSTGRES_DB:-sirene}` toutes les `5s`.
  - Paramètres optimisés pour l'ingestion massive : `shared_buffers=1GB`, `work_mem=64MB`, `maintenance_work_mem=512MB`, `max_wal_size=4GB`, `checkpoint_timeout=15min`, `wal_level=minimal`, `max_wal_senders=0`, `effective_io_concurrency=200`.
- **`sirene-etl`** (construit via `sirene/Dockerfile`, `python:3.12-slim`) :
  - Attend `sirene-postgres` (`condition: service_healthy`).
  - Monte `./staging:/app/staging` et `..:/workspace:ro`.
  - Utilise `DATABASE_URL=postgresql://${POSTGRES_USER:-sirene}:${POSTGRES_PASSWORD:-pg_sirene_ephemeral}@sirene-postgres:5432/${POSTGRES_DB:-sirene}`.
- **`sirene-watcher`** (`profiles: ["daemon"]`, `restart: unless-stopped`) :
  - Activé explicitement avec `--profile daemon` (ou `make sirene-watch`) afin d'éviter tout polling Internet non sollicité pendant les tests hors ligne.
  - Exécute `python watcher.py` en continu.

### Cibles du `Makefile`

| Cible | Commande Exécutée | Rôle |
| :--- | :--- | :--- |
| `make sirene-up` | `docker compose -f sirene/docker-compose.yml up -d sirene-postgres` | Démarre le conteneur PostgreSQL 17 en arrière-plan |
| `make sirene-down` | `docker compose -f sirene/docker-compose.yml --profile daemon down` | Arrête la pile Sirene incluant le profil démon |
| `make sirene-test` | `up -d --wait sirene-postgres`, `build sirene-etl`, `run --rm sirene-etl pytest -v` | Exécute la suite complète `pytest` (unitaire, PostgreSQL 17, gouvernance) |
| `make sirene-import` | `docker compose -f sirene/docker-compose.yml run --rm sirene-etl python full_import.py $(ARGS)` | Lance l'import initial complet (options via `ARGS="..."`) |
| `make sirene-incremental` | `docker compose -f sirene/docker-compose.yml run --rm sirene-etl python incremental_import.py $(ARGS)` | Lance la synchronisation différentielle transactionnelle |
| `make sirene-watch` | `docker compose -f sirene/docker-compose.yml --profile daemon up -d sirene-watcher` | Démarre le démon autonome de veille `data.gouv.fr` |
| `make sirene-docs` | Affiche les chemins vers la page HTML et les guides EN/FR | Liste les points d'entrée documentaires Sirene |

---

## 4. Catalogue des 15 Requêtes SQL Analytiques et de Recherche

Les 15 requêtes ci-dessous sont des requêtes **PostgreSQL 17** en lecture seule issues exactement de `sirene/sql/03_sample_queries.sql`, validées avec `ON_ERROR_STOP=1` sur base vide (sentinelles seules) et sur base peuplée.

### Requête 1 — Recherche Exacte par SIREN / SIRET (Unité Légale, Adresse, NAF, CJ, Effectifs & WGS84)

Restitue la fiche complète d'une entreprise ou d'un établissement avec adresse normalisée, libellés NAF/CJ/effectifs, pays étranger et coordonnées Lambert-93 / WGS84.

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

- **Utilisation des Index** : S'appuie sur `idx_etab_siren`, `etablissements_pkey` et `unites_legales_pkey` (en OLTP, privilégier un prédicat unique `ul.siren = ...` ou `e.siret = ...`), puis jointures par clés primaires sur les référentiels.

---

### Requête 2 — Établissements Actifs par Division NAF et Régions Cibles + Dirigeants / Entrepreneurs

Liste les établissements actifs d'un secteur (`code_division = '62'` informatique, `'62.01Z'` ou sentinelle `'00.00Z'`) dans les régions cibles (`'11'`, `'76'`, `'84'`, `'UNK'`) avec agrégation des dirigeants actifs.

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

- **Utilisation des Index** : Exploite `idx_etab_etat_administratif`, `idx_etab_code_naf` (ou `idx_etab_naf_commune_actif`), `idx_ul_etat_administratif`, `idx_ref_departements_code_region`, `idx_ref_communes_code_departement` et `idx_roles_siren`.

---

### Requête 3 — Recherche Floue Unifiée `pg_trgm` (`%` et `similarity()`) Multi-Tables

Isole chaque prédicat trigramme `%` dans une branche CTE dédiée afin de permettre au planificateur PostgreSQL d'utiliser les trois index GIN simultanément au lieu d'un balayage séquentiel sur des clauses `OR`.

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

- **Utilisation des Index** : Sollicite directement les trois index GIN `pg_trgm` (`idx_ul_nom_trgm`, `idx_etab_enseigne_trgm`, `idx_personnes_nom_trgm`) ainsi que `idx_roles_personne_id` et `unites_legales_pkey`.

---

### Requête 4 — Portefeuille de Mandats et Participations d'un Dirigeant / Actionnaire

Recense les mandats et participations détenus par des personnes physiques (`PHYSIQUE`) ou morales (`MORALE` via `siren_personne_morale`), avec comptage d'établissements actifs et nombre total de mandats par acteur.

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

- **Utilisation des Index** : Utilise `idx_roles_personne_id`, `idx_roles_siren`, `idx_personnes_siren_pm`, `idx_etab_siren` et `unites_legales_pkey` (et `idx_personnes_nom_trgm` lors d'un filtrage par nom).

---

### Requête 5 — Annuaire des Entrepreneurs Individuels (`ENTREPRENEUR_INDIVIDUEL`) par Département et NAF

Liste les entrepreneurs individuels actifs projetés dans `personnes` / `roles_entreprises`, triés par département et code NAF avec l'adresse du siège.

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

- **Utilisation des Index** : Exploite `idx_ul_etat_administratif`, `idx_roles_siren`, `idx_roles_personne_id`, `idx_etab_siren`, `idx_etab_code_commune` et `idx_ref_communes_code_departement`.

---

### Requête 6 — Recherche Géographique par Boîte Englobante WGS84 + Rayon Haversine (km) & Distance Lambert-93

Recherche les établissements actifs dans un rayon de `25.0` km autour du centre de Paris (`48.856600, 2.352200` / Lambert-93 `652469.02, 6862035.26`), en filtrant d'abord via une boîte englobante avant le calcul trigonométrique Haversine sécurisé (`LEAST(1.0, ...)`) et euclidien Lambert-93.

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
        -- Formule de Haversine sécurisée numériquement (évite les erreurs de domaine ACOS > 1.0).
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

- **Utilisation des Index** : Utilise `idx_etab_etat_administratif` et `unites_legales_pkey` ; le préfiltrage par boîte englobante élimine les sites hors zone avant le calcul trigonométrique.

---

### Requête 7 — Agrégation Hiérarchique NAF à 5 Niveaux (Section -> Division -> Groupe -> Classe -> Sous-classe)

Agrège les établissements totaux, actifs et les unités légales distinctes sur les cinq niveaux de la nomenclature **NAF Rév. 2** grâce à `GROUP BY ROLLUP` et `GROUPING()`.

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
    n.code_section NULLS FIRST,
    n.code_division NULLS FIRST,
    n.code_groupe NULLS FIRST,
    n.code_classe NULLS FIRST,
    n.code_naf NULLS FIRST;
```

- **Utilisation des Index** : Jointure via `idx_etab_code_naf` et `ref_naf_pkey` (ajouter un filtre `WHERE n.code_section = '...'` pour des analyses interactives par secteur).

---

### Requête 8 — Densité Régionale/Départementale (Actifs vs. Fermés) et Plancher d'Effectifs (`SUM(effectif_min)`)

Calcule la répartition géographique par région et département, incluant sièges, établissements employeurs, plancher minimal d'effectifs salariés et part régionale en pourcentage.

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

- **Utilisation des Index** : Exploite `idx_ref_departements_code_region`, `idx_ref_communes_code_departement`, `idx_etab_code_commune` et `idx_etab_code_tranche_effectifs`.

---

### Requête 9 — Répartition par Taille d'Entreprise (`PME`, `ETI`, `GE`), Catégorie Juridique, ESS et Société à Mission

Ventile les unités légales selon `categorie_entreprise` (`PME`, `ETI`, `GE`), le niveau 1 juridique (`code_niveau1`), l'Économie Sociale et Solidaire (`economie_sociale_solidaire = 'O'`) et la qualité de société à mission (`societe_mission = 'O'`).

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

- **Utilisation des Index** : Exploite `idx_ul_categorie_entreprise`, `idx_ul_code_cj`, `idx_ul_etat_administratif` et `idx_etab_siren`.

---

### Requête 10 — Classement des Réseaux Multi-Établissements (`COUNT(siret)` par `siren`)

Identifie les groupes multi-sites (`COUNT(e.siret) >= 2`) par nombre d'établissements actifs et couverture départementale.

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

- **Utilisation des Index** : Agrège les établissements via `idx_etab_siren`, avec jointures `unites_legales_pkey` et `idx_etab_code_commune`.

---

### Requête 11 — Audit des Fermetures et Réouvertures Administratives (`etablissements_historique_etat`)

Analyse les dernières transitions d'état détectées par `incremental_import.py` (`'A' -> 'F'` fermeture ou `'F' -> 'A'` réouverture), avec comptage de l'historique par `siret` et rattachement à `etl_logs`.

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

- **Utilisation des Index** : S'appuie sur `idx_etab_hist_siret`, `etablissements_pkey`, `unites_legales_pkey` et `etl_logs_pkey`.

---

### Requête 12 — Cohortes de Création d'Entreprises, Taux de Survie et Longévité par Décennie / Année

Mesure la longévité, le taux de survie (`etat_administratif = 'A'`) et le plancher d'effectifs actifs des unités légales par décennie et année de création.

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

- **Utilisation des Index** : S'appuie sur `idx_ul_etat_administratif` et `idx_ul_code_tranche_effectifs` au cours d'un balayage unique de `unites_legales`.

---

### Requête 13 — Établissements Situés à l'Étranger (`code_pays_etranger` + `ref_pays`)

Agrège les établissements implantés hors de France (`code_pays_etranger <> '99100'`) par pays, avec codes ISO-2/ISO-3 et exemples de localités étrangères.

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

- **Utilisation des Index** : Utilise `idx_etab_code_pays_etranger` (B-Tree) pour cibler rapidement les établissements étrangers et `ref_pays_pkey`.

---

### Requête 14 — Audit de Qualité des Données : Diffusion Partielle `[ND]` (`statut_diffusion = 'P'`) & Référentiels Historiques (`HIST` / `UNK`)

Quantifie les enregistrements en diffusion partielle (`'P'`), les communes sentinelles (`'UNK00'`), les codes historiques (`'HIST'`), les codes de repli (`'0000'`, `'UN'`) et les unités légales orphelines créées en `'C'`.

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

- **Utilisation des Index** : Exploite `idx_etab_code_commune`, `idx_etab_code_naf`, `idx_ul_code_cj` et `idx_ul_code_tranche_effectifs`.

---

### Requête 15 — Santé Opérationnelle ETL (`etl_logs` & SHA-256) + Volumétrie des Tables et Index (`pg_stat_user_tables`)

Combine les statistiques des dernières exécutions `etl_logs` (débit, durée, SHA-256, compteurs de succès/échec) et la volumétrie réelle des tables et index PostgreSQL 17.

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

- **Utilisation des Index** : S'appuie sur `idx_etl_logs_entity_status_finished` pour `etl_logs` et interroge les vues système PostgreSQL (`pg_stat_user_tables`, `pg_relation_size`, `pg_indexes_size`, `pg_total_relation_size`).

---

***
[🏠 Accueil](index.md) | [⬅️ Précédent](gap_locking_experiment.md) | [Référence HTML Interactive](../sirene_documentation.html) | [🇬🇧 Version Anglaise](../en/sirene_platform.md)
