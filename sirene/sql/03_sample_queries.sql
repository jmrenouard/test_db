-- =============================================================================
-- SIRENE PostgreSQL 18 Analytical & Search Query Catalog (15 Queries)
-- =============================================================================
-- Read-only reference queries validated on PostgreSQL 18 (postgres:18-bookworm)
-- and designed to execute cleanly against any initialized SIRENE 3NF database
-- (empty sentinel-seeded or full production).
-- Zero psql meta-commands are used so every statement runs under psql or
-- psycopg multi-statement execution with ON_ERROR_STOP=1.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Exact SIREN / SIRET lookup (legal unit, address, NAF, CJ,
--          workforce bracket, and WGS84 / Lambert-93 coordinates)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 2: Active establishments by NAF division/subclass in target regions
--          joined with active corporate officers and sole proprietors
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 3: Unified pg_trgm fuzzy search (% and similarity()) across
--          nom_recherche, enseigne_recherche, and nom_complet_recherche
-- -----------------------------------------------------------------------------
-- Splitting each indexed % predicate into its own CTE branch allows PostgreSQL
-- to leverage idx_ul_nom_trgm, idx_etab_enseigne_trgm, and idx_personnes_nom_trgm.
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

-- -----------------------------------------------------------------------------
-- Query 4: Officer / shareholder corporate portfolio lookup
--          (roles_entreprises + personnes + siren_personne_morale)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 5: Sole proprietors (ENTREPRENEUR_INDIVIDUEL) directory by department
--          and NAF activity
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 6: WGS84 bounding-box + Haversine radius search (km) using
--          longitude/latitude alongside Lambert-93 planar distance
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 7: NAF 5-level hierarchy rollup
--          (Section -> Division -> Groupe -> Classe -> Sous-classe)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 8: Regional & departmental active vs. closed density and minimum
--          headcount floor (SUM(effectif_min))
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
-- Query 9: Enterprise size category (PME, ETI, GE), legal category level 1,
--          Social & Solidarity Economy (ESS), and mission-driven companies
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
-- Query 10: Top multi-establishment corporate networks (COUNT(siret) per siren)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 11: Administrative closure / reopening churn audit
--           (etablissements_historique_etat)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 12: Company creation cohorts and survival / longevity by decade & year
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 13: Foreign-located establishments (code_pays_etranger + ref_pays)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 14: Data quality audit: [ND] partial diffusion (statut_diffusion = 'P')
--           and auto-registered historical / fallback referentials (HIST / UNK)
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 15: ETL operational health (etl_logs throughput & SHA-256 history)
--           and PostgreSQL table/index storage introspection (pg_stat_user_tables)
-- -----------------------------------------------------------------------------
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
