-- =============================================================================
-- SIRENE PostgreSQL Secondary & Search Indexes
-- =============================================================================
-- Idempotent index definitions applied after schema creation or rebuilt after
-- bulk full-stock ingestion (see db.rebuild_indexes_and_analyze).
--
-- Includes:
--   - B-Tree indexes on every foreign key and high-selectivity filter column
--   - Partial composite index for active establishments by NAF and municipality
--   - Trigram GIN indexes (pg_trgm) with fastupdate = on for fuzzy text search
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Referential Foreign-Key Indexes
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ref_departements_code_region
    ON ref_departements (code_region);

CREATE INDEX IF NOT EXISTS idx_ref_communes_code_departement
    ON ref_communes (code_departement);

-- -----------------------------------------------------------------------------
-- 2. Legal Units (unites_legales) B-Tree Indexes
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ul_code_cj
    ON unites_legales (code_cj);

CREATE INDEX IF NOT EXISTS idx_ul_code_naf
    ON unites_legales (code_naf);

CREATE INDEX IF NOT EXISTS idx_ul_code_tranche_effectifs
    ON unites_legales (code_tranche_effectifs);

CREATE INDEX IF NOT EXISTS idx_ul_etat_administratif
    ON unites_legales (etat_administratif);

CREATE INDEX IF NOT EXISTS idx_ul_categorie_entreprise
    ON unites_legales (categorie_entreprise);

CREATE INDEX IF NOT EXISTS idx_ul_date_dernier_traitement
    ON unites_legales (date_dernier_traitement);

-- -----------------------------------------------------------------------------
-- 3. Establishments (etablissements) B-Tree & Partial Composite Indexes
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_etab_siren
    ON etablissements (siren);

CREATE INDEX IF NOT EXISTS idx_etab_code_commune
    ON etablissements (code_commune);

CREATE INDEX IF NOT EXISTS idx_etab_code_naf
    ON etablissements (code_naf);

CREATE INDEX IF NOT EXISTS idx_etab_code_tranche_effectifs
    ON etablissements (code_tranche_effectifs);

CREATE INDEX IF NOT EXISTS idx_etab_code_pays_etranger
    ON etablissements (code_pays_etranger);

CREATE INDEX IF NOT EXISTS idx_etab_code_postal
    ON etablissements (code_postal);

CREATE INDEX IF NOT EXISTS idx_etab_etat_administratif
    ON etablissements (etat_administratif);

CREATE INDEX IF NOT EXISTS idx_etab_date_dernier_traitement
    ON etablissements (date_dernier_traitement);

CREATE INDEX IF NOT EXISTS idx_etab_naf_commune_actif
    ON etablissements (code_naf, code_commune)
    WHERE etat_administratif = 'A';

-- -----------------------------------------------------------------------------
-- 4. Audit History, Governance Roles & ETL Logs Indexes
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_etab_hist_siret
    ON etablissements_historique_etat (siret);

CREATE INDEX IF NOT EXISTS idx_personnes_siren_pm
    ON personnes (siren_personne_morale);

CREATE INDEX IF NOT EXISTS idx_roles_siren
    ON roles_entreprises (siren);

CREATE INDEX IF NOT EXISTS idx_roles_personne_id
    ON roles_entreprises (personne_id);

CREATE INDEX IF NOT EXISTS idx_etl_logs_entity_status_finished
    ON etl_logs (entity_type, status, finished_at DESC);

-- -----------------------------------------------------------------------------
-- 5. Fuzzy Text Search Trigram GIN Indexes (pg_trgm)
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ul_nom_trgm
    ON unites_legales USING GIN (nom_recherche gin_trgm_ops)
    WITH (fastupdate = on);

CREATE INDEX IF NOT EXISTS idx_etab_enseigne_trgm
    ON etablissements USING GIN (enseigne_recherche gin_trgm_ops)
    WITH (fastupdate = on);

CREATE INDEX IF NOT EXISTS idx_personnes_nom_trgm
    ON personnes USING GIN (nom_complet_recherche gin_trgm_ops)
    WITH (fastupdate = on);
