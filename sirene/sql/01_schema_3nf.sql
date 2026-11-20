-- =============================================================================
-- SIRENE PostgreSQL 18 3NF Relational Schema (postgres:18-bookworm)
-- =============================================================================
-- Idempotent DDL for INSEE SIRENE legal units, establishments, geographic and
-- economic referentials, corporate officers / sole proprietors, state audit
-- history, and ETL execution tracking.
--
-- Requirements & Replication Notes:
--   - PostgreSQL 18 (postgres:18-bookworm; compatible with PostgreSQL >= 15
--     for UNIQUE NULLS NOT DISTINCT and STORED generated columns)
--   - All 13 tables define explicit PRIMARY KEYs (REPLICA IDENTITY DEFAULT) for
--     logical replication and multi-master qualification compatibility
--   - pg_trgm extension for trigram fuzzy search indexes (see 02_indexes.sql)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- -----------------------------------------------------------------------------
-- 1. Geographic and Economic Referential Tables (3NF Lookup Dimensions)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ref_regions (
    code_region   VARCHAR(3)   PRIMARY KEY,
    cheflieu      VARCHAR(5),
    nom_majuscule VARCHAR(100) NOT NULL,
    libelle       VARCHAR(120) NOT NULL
);

COMMENT ON TABLE ref_regions IS 'INSEE Official Geographic Code (COG) regions referential.';

CREATE TABLE IF NOT EXISTS ref_departements (
    code_departement VARCHAR(4)   PRIMARY KEY,
    code_region      VARCHAR(3)   NOT NULL REFERENCES ref_regions(code_region),
    cheflieu         VARCHAR(5),
    nom_majuscule    VARCHAR(100) NOT NULL,
    libelle          VARCHAR(120) NOT NULL
);

COMMENT ON TABLE ref_departements IS 'INSEE Official Geographic Code (COG) departments referential.';

CREATE TABLE IF NOT EXISTS ref_communes (
    code_commune     VARCHAR(5)   PRIMARY KEY,
    code_departement VARCHAR(4)   NOT NULL REFERENCES ref_departements(code_departement),
    type_commune     VARCHAR(6)   NOT NULL DEFAULT 'COM',
    nom_majuscule    VARCHAR(150) NOT NULL,
    libelle          VARCHAR(150) NOT NULL,
    est_active       BOOLEAN      NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE ref_communes IS 'INSEE Official Geographic Code (COG) current and historical municipalities.';

CREATE TABLE IF NOT EXISTS ref_pays (
    code_pays VARCHAR(5)   PRIMARY KEY,
    code_iso2 CHAR(2),
    code_iso3 CHAR(3),
    libelle   VARCHAR(150) NOT NULL
);

COMMENT ON TABLE ref_pays IS 'INSEE countries and foreign territories referential.';

CREATE TABLE IF NOT EXISTS ref_naf (
    code_naf            VARCHAR(6)   PRIMARY KEY,
    nomenclature        VARCHAR(12)  NOT NULL DEFAULT 'NAFRev2',
    code_section        VARCHAR(2),
    libelle_section     VARCHAR(255),
    code_division       VARCHAR(2),
    libelle_division    VARCHAR(255),
    code_groupe         VARCHAR(4),
    libelle_groupe      VARCHAR(255),
    code_classe         VARCHAR(5),
    libelle_classe      VARCHAR(255),
    libelle_sous_classe VARCHAR(255) NOT NULL
);

COMMENT ON TABLE ref_naf IS 'INSEE French Nomenclature of Activities (NAF) referential.';

CREATE TABLE IF NOT EXISTS ref_categories_juridiques (
    code_cj         VARCHAR(4)   PRIMARY KEY,
    code_niveau1    VARCHAR(1),
    libelle_niveau1 VARCHAR(255),
    code_niveau2    VARCHAR(2),
    libelle_niveau2 VARCHAR(255),
    libelle         VARCHAR(255) NOT NULL
);

COMMENT ON TABLE ref_categories_juridiques IS 'INSEE legal categories (Nature Juridique) referential.';

CREATE TABLE IF NOT EXISTS ref_tranches_effectifs (
    code_tranche VARCHAR(2)   PRIMARY KEY,
    effectif_min INTEGER,
    effectif_max INTEGER,
    libelle      VARCHAR(120) NOT NULL
);

COMMENT ON TABLE ref_tranches_effectifs IS 'INSEE employee headcount brackets referential.';

-- -----------------------------------------------------------------------------
-- 2. Sentinel Reference Seed Data (Idempotent FK Fallbacks)
-- -----------------------------------------------------------------------------

INSERT INTO ref_regions (code_region, cheflieu, nom_majuscule, libelle)
VALUES ('UNK', NULL, 'UNKNOWN', 'Unknown or unspecified region')
ON CONFLICT (code_region) DO NOTHING;

INSERT INTO ref_departements (code_departement, code_region, cheflieu, nom_majuscule, libelle)
VALUES ('UNK', 'UNK', NULL, 'UNKNOWN', 'Unknown or unspecified department')
ON CONFLICT (code_departement) DO NOTHING;

INSERT INTO ref_communes (code_commune, code_departement, type_commune, nom_majuscule, libelle, est_active)
VALUES ('UNK00', 'UNK', 'COM', 'UNKNOWN', 'Unknown or unspecified municipality', FALSE)
ON CONFLICT (code_commune) DO NOTHING;

INSERT INTO ref_pays (code_pays, code_iso2, code_iso3, libelle)
VALUES
    ('UNK',   NULL, NULL,  'Unknown or unspecified country'),
    ('99100', 'FR', 'FRA', 'France')
ON CONFLICT (code_pays) DO NOTHING;

INSERT INTO ref_naf (
    code_naf, nomenclature, code_section, libelle_section,
    code_division, libelle_division, code_groupe, libelle_groupe,
    code_classe, libelle_classe, libelle_sous_classe
)
VALUES (
    '00.00Z', 'NAFRev2', NULL, NULL,
    NULL, NULL, NULL, NULL,
    NULL, NULL, 'Unknown or unspecified principal activity'
)
ON CONFLICT (code_naf) DO NOTHING;

INSERT INTO ref_categories_juridiques (
    code_cj, code_niveau1, libelle_niveau1,
    code_niveau2, libelle_niveau2, libelle
)
VALUES ('0000', NULL, NULL, NULL, NULL, 'Unknown or unspecified legal category')
ON CONFLICT (code_cj) DO NOTHING;

INSERT INTO ref_tranches_effectifs (code_tranche, effectif_min, effectif_max, libelle)
VALUES
    ('NN', NULL, NULL, 'Non-employing unit or unspecified headcount'),
    ('UN', NULL, NULL, 'Confidential or masked headcount ([ND])')
ON CONFLICT (code_tranche) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. Core SIRENE Entities (Legal Units & Establishments)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS unites_legales (
    siren                      VARCHAR(9)   PRIMARY KEY CHECK (siren ~ '^[0-9]{9}$'),
    statut_diffusion           CHAR(1)      NOT NULL DEFAULT 'O',
    unite_purgee               BOOLEAN      NOT NULL DEFAULT FALSE,
    etat_administratif         CHAR(1)      NOT NULL CHECK (etat_administratif IN ('A', 'C')),
    date_creation              DATE,
    date_debut_periode         DATE,
    date_dernier_traitement    TIMESTAMPTZ,
    denomination               VARCHAR(255),
    sigle                      VARCHAR(50),
    denomination_usuelle_1     VARCHAR(150),
    denomination_usuelle_2     VARCHAR(150),
    denomination_usuelle_3     VARCHAR(150),
    nom_naissance              VARCHAR(150),
    nom_usage                  VARCHAR(150),
    prenom_usuel               VARCHAR(100),
    prenoms                    VARCHAR(255),
    pseudonyme                 VARCHAR(150),
    sexe                       CHAR(1),
    identifiant_association    VARCHAR(20),
    categorie_entreprise       VARCHAR(5)   CHECK (categorie_entreprise IS NULL OR categorie_entreprise IN ('PME', 'ETI', 'GE')),
    annee_categorie_entreprise SMALLINT,
    code_cj                    VARCHAR(4)   NOT NULL DEFAULT '0000' REFERENCES ref_categories_juridiques(code_cj),
    code_naf                   VARCHAR(6)   NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf),
    nomenclature_activite      VARCHAR(15),
    code_naf_2025              VARCHAR(6),
    code_tranche_effectifs     VARCHAR(2)   NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche),
    annee_effectifs            SMALLINT,
    nic_siege                  VARCHAR(5),
    economie_sociale_solidaire CHAR(1),
    societe_mission            CHAR(1),
    caractere_employeur        CHAR(1),
    -- Immutable concatenation matching TRIM(CONCAT_WS(' ', ...)) for GIN pg_trgm indexing.
    nom_recherche              TEXT GENERATED ALWAYS AS (
        TRIM(
            COALESCE(' ' || NULLIF(TRIM(denomination), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(sigle), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(denomination_usuelle_1), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(COALESCE(NULLIF(TRIM(nom_usage), ''), nom_naissance)), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(prenom_usuel), ''), '')
        )
    ) STORED,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE unites_legales IS 'SIRENE legal units (companies, associations, public bodies, sole proprietors) keyed by 9-digit SIREN.';

CREATE TABLE IF NOT EXISTS etablissements (
    siret                    VARCHAR(14)      PRIMARY KEY CHECK (siret ~ '^[0-9]{14}$'),
    siren                    VARCHAR(9)       NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE,
    nic                      VARCHAR(5)       NOT NULL,
    etablissement_siege      BOOLEAN          NOT NULL DEFAULT FALSE,
    statut_diffusion         CHAR(1)          NOT NULL DEFAULT 'O',
    etat_administratif       CHAR(1)          NOT NULL CHECK (etat_administratif IN ('A', 'F')),
    date_creation            DATE,
    date_debut_periode       DATE,
    date_dernier_traitement  TIMESTAMPTZ,
    enseigne_1               VARCHAR(150),
    enseigne_2               VARCHAR(150),
    enseigne_3               VARCHAR(150),
    denomination_usuelle     VARCHAR(150),
    code_naf                 VARCHAR(6)       NOT NULL DEFAULT '00.00Z' REFERENCES ref_naf(code_naf),
    nomenclature_activite    VARCHAR(15),
    code_naf_2025            VARCHAR(6),
    activite_artisanale      VARCHAR(15),
    code_tranche_effectifs   VARCHAR(2)       NOT NULL DEFAULT 'NN' REFERENCES ref_tranches_effectifs(code_tranche),
    annee_effectifs          SMALLINT,
    caractere_employeur      CHAR(1),
    numero_voie              VARCHAR(20),
    indice_repetition        VARCHAR(15),
    type_voie                VARCHAR(40),
    libelle_voie             VARCHAR(150),
    complement_adresse       VARCHAR(150),
    distribution_speciale    VARCHAR(50),
    code_postal              VARCHAR(15),
    libelle_commune          VARCHAR(150),
    code_commune             VARCHAR(5)       NOT NULL DEFAULT 'UNK00' REFERENCES ref_communes(code_commune),
    code_cedex               VARCHAR(20),
    libelle_cedex            VARCHAR(120),
    code_pays_etranger       VARCHAR(5)       REFERENCES ref_pays(code_pays),
    libelle_commune_etranger VARCHAR(150),
    -- Immutable single-space address normalization for query presentation and text search.
    adresse_complete         TEXT GENERATED ALWAYS AS (
        TRIM(
            COALESCE(' ' || NULLIF(TRIM(numero_voie), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(indice_repetition), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(type_voie), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(libelle_voie), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(complement_adresse), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(code_postal), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(COALESCE(NULLIF(TRIM(libelle_commune), ''), libelle_commune_etranger)), ''), '')
        )
    ) STORED,
    -- Immutable trade sign search projection indexed by GIN pg_trgm.
    enseigne_recherche       TEXT GENERATED ALWAYS AS (
        TRIM(
            COALESCE(' ' || NULLIF(TRIM(enseigne_1), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(enseigne_2), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(enseigne_3), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(denomination_usuelle), ''), '')
        )
    ) STORED,
    identifiant_adresse_ban  VARCHAR(30),
    coord_lambert_x          NUMERIC(12, 2),
    coord_lambert_y          NUMERIC(12, 2),
    longitude                DOUBLE PRECISION,
    latitude                 DOUBLE PRECISION,
    updated_at               TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE etablissements IS 'SIRENE physical establishments keyed by 14-digit SIRET, linked to legal units and geographic referentials.';

CREATE TABLE IF NOT EXISTS etablissements_historique_etat (
    id          BIGSERIAL   PRIMARY KEY,
    siret       VARCHAR(14) NOT NULL REFERENCES etablissements(siret) ON DELETE CASCADE,
    ancien_etat CHAR(1)     NOT NULL,
    nouvel_etat CHAR(1)     NOT NULL,
    date_effet  DATE,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    etl_log_id  BIGINT
);

COMMENT ON TABLE etablissements_historique_etat IS 'Audit log of establishment administrative status transitions detected during incremental updates.';

-- -----------------------------------------------------------------------------
-- 4. Governance & Sole Proprietors (Persons & Roles)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS personnes (
    id                    BIGSERIAL    PRIMARY KEY,
    type_personne         VARCHAR(10)  NOT NULL CHECK (type_personne IN ('PHYSIQUE', 'MORALE')),
    nom                   VARCHAR(150),
    prenoms               VARCHAR(255),
    prenom_usuel          VARCHAR(100),
    sexe                  CHAR(1),
    date_naissance        DATE,
    siren_personne_morale VARCHAR(9)   REFERENCES unites_legales(siren) ON DELETE SET NULL,
    cle_deduplication     VARCHAR(128) NOT NULL UNIQUE,
    -- Immutable full-name projection indexed by GIN pg_trgm.
    nom_complet_recherche TEXT GENERATED ALWAYS AS (
        TRIM(
            COALESCE(' ' || NULLIF(TRIM(nom), ''), '') ||
            COALESCE(' ' || NULLIF(TRIM(prenoms), ''), '')
        )
    ) STORED,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE personnes IS 'Natural and legal persons acting as sole proprietors, corporate officers, or beneficial owners.';

CREATE TABLE IF NOT EXISTS roles_entreprises (
    id                    BIGSERIAL     PRIMARY KEY,
    siren                 VARCHAR(9)    NOT NULL REFERENCES unites_legales(siren) ON DELETE CASCADE,
    personne_id           BIGINT        NOT NULL REFERENCES personnes(id) ON DELETE CASCADE,
    type_role             VARCHAR(40)   NOT NULL CHECK (
        type_role IN (
            'ENTREPRENEUR_INDIVIDUEL',
            'GERANT',
            'PRESIDENT',
            'DIRECTEUR_GENERAL',
            'ADMINISTRATEUR',
            'ASSOCIE',
            'ACTIONNAIRE',
            'BENEFICIAIRE_EFFECTIF',
            'AUTRE'
        )
    ),
    qualite_detaillee     VARCHAR(150),
    pourcentage_detention NUMERIC(5, 2) CHECK (pourcentage_detention IS NULL OR (pourcentage_detention >= 0 AND pourcentage_detention <= 100)),
    pourcentage_droits_vote NUMERIC(5, 2) CHECK (pourcentage_droits_vote IS NULL OR (pourcentage_droits_vote >= 0 AND pourcentage_droits_vote <= 100)),
    date_debut            DATE,
    date_fin              DATE,
    actif                 BOOLEAN       NOT NULL DEFAULT TRUE,
    source_donnee         VARCHAR(30)   NOT NULL DEFAULT 'SIRENE',
    UNIQUE NULLS NOT DISTINCT (siren, personne_id, type_role, date_debut)
);

COMMENT ON TABLE roles_entreprises IS 'Associative entity linking legal units and persons with governance or ownership roles.';

-- -----------------------------------------------------------------------------
-- 5. ETL Observability & Idempotency Log
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS etl_logs (
    id             BIGSERIAL    PRIMARY KEY,
    run_type       VARCHAR(30)  NOT NULL CHECK (run_type IN ('REFERENTIALS', 'FULL_IMPORT', 'INCREMENTAL_IMPORT', 'WATCHER_CHECK')),
    entity_type    VARCHAR(40)  NOT NULL,
    resource_id    VARCHAR(100),
    source_url     TEXT,
    file_name      VARCHAR(255),
    file_version   VARCHAR(64),
    checksum_type  VARCHAR(16),
    checksum_value VARCHAR(128),
    rows_processed BIGINT       NOT NULL DEFAULT 0,
    rows_inserted  BIGINT       NOT NULL DEFAULT 0,
    rows_updated   BIGINT       NOT NULL DEFAULT 0,
    status         VARCHAR(20)  NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED')),
    started_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    finished_at    TIMESTAMPTZ,
    error_message  TEXT,
    metadata       JSONB        NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE etl_logs IS 'Execution audit trail and checksum ledger for idempotent SIRENE ETL runs.';
