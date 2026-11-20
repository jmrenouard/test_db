-- =============================================================================
-- SIRENE PostgreSQL 18 Direct Bulk SQL Loader (Zero Python Required)
-- =============================================================================
-- Idempotently creates the 3NF schema, resets tables for clean repeatable runs,
-- drops non-constraint secondary indexes for bulk COPY throughput, loads all
-- synthetic referential/entity/governance dumps, rebuilds indexes, and analyzes.
-- =============================================================================

SELECT 'CREATING SIRENE 3NF SCHEMA' AS status;
\ir sql/01_schema_3nf.sql

SELECT 'TRUNCATING TABLES FOR IDEMPOTENT LOAD' AS status;
TRUNCATE TABLE
    etablissements_historique_etat,
    roles_entreprises,
    personnes,
    etablissements,
    unites_legales,
    etl_logs,
    ref_communes,
    ref_departements,
    ref_regions,
    ref_pays,
    ref_naf,
    ref_categories_juridiques,
    ref_tranches_effectifs
RESTART IDENTITY CASCADE;

SELECT 'DROPPING SECONDARY INDEXES BEFORE BULK COPY' AS status;
DO $$
DECLARE
    idx_rec RECORD;
BEGIN
    FOR idx_rec IN
        SELECT pi.schemaname, pi.indexname
        FROM pg_indexes pi
        JOIN pg_namespace n ON n.nspname = pi.schemaname
        JOIN pg_class c
          ON c.relname = pi.indexname
         AND c.relnamespace = n.oid
         AND c.relkind IN ('i', 'I')
        JOIN pg_index i ON i.indexrelid = c.oid
        WHERE pi.schemaname = ANY(current_schemas(false))
          AND pi.tablename IN (
              'ref_departements',
              'ref_communes',
              'unites_legales',
              'etablissements',
              'etablissements_historique_etat',
              'personnes',
              'roles_entreprises',
              'etl_logs'
          )
          AND NOT i.indisprimary
          AND NOT EXISTS (
              SELECT 1
              FROM pg_constraint con
              WHERE con.conindid = i.indexrelid
          )
    LOOP
        EXECUTE format(
            'DROP INDEX IF EXISTS %I.%I',
            idx_rec.schemaname,
            idx_rec.indexname
        );
    END LOOP;
END $$;

SELECT 'LOADING SYNTHETIC REFERENTIALS' AS status;
\ir data/sql/01_load_referentials.sql

SELECT 'LOADING SYNTHETIC LEGAL UNITS (15,000)' AS status;
\ir data/sql/02_load_unites_legales.sql

SELECT 'LOADING SYNTHETIC ESTABLISHMENTS (30,000)' AS status;
\ir data/sql/03_load_etablissements.sql

SELECT 'LOADING GOVERNANCE, HISTORY, AND ETL LOGS' AS status;
\ir data/sql/04_load_governance_and_history.sql

SELECT 'REBUILDING SECONDARY AND GIN INDEXES' AS status;
\ir sql/02_indexes.sql

SELECT 'ANALYZING TABLES' AS status;
ANALYZE;

SELECT 'SIRENE DATABASE LOAD COMPLETE' AS status;
