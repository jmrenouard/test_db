-- =============================================================================
-- SIRENE PostgreSQL Sample Analytical & Search Queries
-- =============================================================================
-- Read-only reference queries designed to run cleanly against any initialized
-- SIRENE 3NF database (both empty sentinel-seeded schemas and full datasets).
-- Zero psql meta-commands are used so every statement runs under psql or psycopg.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Active establishments by NAF division in a target region with
--          linked corporate officers or sole proprietors
-- -----------------------------------------------------------------------------
SELECT
    ul.siren,
    e.siret,
    e.etablissement_siege,
    COALESCE(ul.denomination, TRIM(CONCAT_WS(' ', ul.nom_usage, ul.nom_naissance, ul.prenom_usuel))) AS legal_unit_name,
    cj.libelle AS legal_category,
    e.code_naf,
    n.libelle_sous_classe AS activity_label,
    e.adresse_complete,
    c.libelle AS municipality,
    d.libelle AS department,
    r.libelle AS region,
    STRING_AGG(
        DISTINCT CONCAT_WS(
            ' ',
            p.nom,
            p.prenoms,
            '(' || re.type_role || ')'
        ),
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
  AND (n.code_division = '62' OR e.code_naf = '00.00Z')
  AND r.code_region IN ('11', '84', 'UNK')
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

-- -----------------------------------------------------------------------------
-- Query 2: Fuzzy pg_trgm search across legal units, establishment trade signs,
--          and corporate officers / sole proprietors
-- -----------------------------------------------------------------------------
-- Splitting each indexed % predicate into its own CTE branch lets the planner
-- exploit idx_ul_nom_trgm, idx_etab_enseigne_trgm, and idx_personnes_nom_trgm.
WITH search_params AS (
    SELECT 'BOULANGERIE DUPONT'::TEXT AS query_text
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
    MAX(cm.trgm_score) AS best_similarity_score,
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

-- -----------------------------------------------------------------------------
-- Query 3: Regional & departmental establishment density and headcount breakdown
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 4: Establishment administrative state transition and closure audit
-- -----------------------------------------------------------------------------
WITH ranked_transitions AS (
    SELECT
        h.id AS history_id,
        h.siret,
        e.siren,
        ul.nom_recherche AS legal_unit_name,
        e.code_naf,
        n.libelle_sous_classe AS activity_label,
        c.libelle AS municipality,
        h.ancien_etat,
        h.nouvel_etat,
        h.date_effet,
        h.changed_at,
        l.run_type,
        l.file_name,
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
    date_effet,
    changed_at,
    run_type,
    file_name
FROM ranked_transitions
WHERE transition_rank = 1
ORDER BY changed_at DESC, history_id DESC
LIMIT 100;

-- -----------------------------------------------------------------------------
-- Query 5: Enterprise size category, legal form level, ESS & mission companies
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 6: ETL run freshness, checksum audit, and throughput summary
-- -----------------------------------------------------------------------------
WITH latest_per_entity AS (
    SELECT
        id,
        run_type,
        entity_type,
        resource_id,
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
        error_message,
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
        COUNT(*) FILTER (WHERE status = 'SKIPPED') AS skipped_runs,
        MAX(finished_at) FILTER (WHERE status = 'SUCCESS') AS last_success_at,
        COALESCE(SUM(rows_processed) FILTER (WHERE status = 'SUCCESS'), 0) AS cumulative_rows_processed
    FROM etl_logs
    GROUP BY entity_type
)
SELECT
    ea.entity_type,
    lp.run_type AS latest_run_type,
    lp.status AS latest_status,
    lp.file_name AS latest_file_name,
    lp.file_version AS latest_file_version,
    lp.checksum_type AS latest_checksum_type,
    lp.checksum_value AS latest_checksum_value,
    lp.rows_processed AS latest_rows_processed,
    lp.rows_inserted AS latest_rows_inserted,
    lp.rows_updated AS latest_rows_updated,
    ROUND(EXTRACT(EPOCH FROM (lp.finished_at - lp.started_at))::NUMERIC, 2) AS latest_duration_seconds,
    ea.last_success_at,
    ea.total_runs,
    ea.success_runs,
    ea.failed_runs,
    ea.skipped_runs,
    ea.cumulative_rows_processed,
    lp.error_message AS latest_error_message
FROM entity_aggregates ea
JOIN latest_per_entity lp
    ON lp.entity_type = ea.entity_type
   AND lp.rn = 1
ORDER BY ea.entity_type;
