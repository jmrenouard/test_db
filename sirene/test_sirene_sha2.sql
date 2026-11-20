-- =============================================================================
-- SIRENE PostgreSQL 18 Integrity Verification Using Built-In SHA-256 Checksums
-- =============================================================================
-- Mirrors postgresql/test_employees_sha2.sql across all 12 domain and
-- referential tables using built-in PostgreSQL sha256(bytea) (no pgcrypto).
-- =============================================================================

SELECT 'TESTING SIRENE INSTALLATION' AS info;

DROP TABLE IF EXISTS expected_values, found_values;
CREATE TABLE expected_values (
    table_name VARCHAR(40) NOT NULL PRIMARY KEY,
    recs       INT         NOT NULL,
    crc_sha2   VARCHAR(100) NOT NULL
);

CREATE TABLE found_values (LIKE expected_values);

INSERT INTO expected_values (table_name, recs, crc_sha2) VALUES
('ref_regions',                    25,    '7db0f872761b8cc9215b6d8c8f3cb214c393df934acfed85d1fd4a71f6492c4b'),
('ref_departements',               112,   '08e8d5cea4a0a9cbfcab1438f237bb8a9c83738a6b385b53334acd425e81801f'),
('ref_communes',                   563,   '3349552354a42878e8ebf75d2f6842b84a3c43c333f0baf3ce1baf1405129946'),
('ref_pays',                       11,    '65c2701961adfdab66440d4515bf04bc80278a0b150a5245a8755b6ada0a30dc'),
('ref_naf',                        39,    '31fc98203d5b3baaa2ff4d44a3a6c46e074c41e53c73729d5b465d1dca1fc26a'),
('ref_categories_juridiques',      113,   '9e44d820f4c41d8b0814e7dad7c34dc82ecdbec06a719748703562c8e35f9e4d'),
('ref_tranches_effectifs',         17,    '9a85884fa7e14c4c95ac3b88da2a0434901942e39889e9c353149ae71ba5beb7'),
('unites_legales',                 15000, '3625daa7193be62890817fab74bb960fb47cd0a1f80082c287adacf1934b0e8c'),
('etablissements',                 30000, 'c7dc6ec325d59d8521b8f96a094c8308de70430d587aa52e2633be4c1778263b'),
('etablissements_historique_etat', 1200,  'ae81915ec8a2601731e9a7df397d8aff0d3882914d02c7f1289c410fcce6d743'),
('personnes',                      8000,  'ad3706a3e97fa7744664507d08f122aa13f35bf20a4a0977fc0eac32e0b07310'),
('roles_entreprises',              12000, '664a167c4819fba977d163e5f49addb6ede2ec945c9423ed2fa6efd96fab16c0');

SELECT table_name, recs AS expected_records, crc_sha2 AS expected_crc
FROM expected_values
ORDER BY table_name;

CREATE OR REPLACE FUNCTION compute_table_sha256(p_query TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    crc TEXT := '';
    r   RECORD;
BEGIN
    FOR r IN EXECUTE p_query LOOP
        crc := encode(sha256(convert_to(crc || '#' || r.row_text, 'UTF8')), 'hex');
    END LOOP;
    RETURN crc;
END;
$$;

INSERT INTO found_values (table_name, recs, crc_sha2) VALUES
('ref_regions',
    (SELECT COUNT(*) FROM ref_regions),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_region, cheflieu, nom_majuscule, libelle) AS row_text FROM ref_regions ORDER BY code_region$$))),
('ref_departements',
    (SELECT COUNT(*) FROM ref_departements),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_departement, code_region, cheflieu, nom_majuscule, libelle) AS row_text FROM ref_departements ORDER BY code_departement$$))),
('ref_communes',
    (SELECT COUNT(*) FROM ref_communes),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_commune, code_departement, type_commune, nom_majuscule, libelle, est_active) AS row_text FROM ref_communes ORDER BY code_commune$$))),
('ref_pays',
    (SELECT COUNT(*) FROM ref_pays),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_pays, code_iso2, code_iso3, libelle) AS row_text FROM ref_pays ORDER BY code_pays$$))),
('ref_naf',
    (SELECT COUNT(*) FROM ref_naf),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_naf, nomenclature, code_section, libelle_section, code_division, libelle_division, code_groupe, libelle_groupe, code_classe, libelle_classe, libelle_sous_classe) AS row_text FROM ref_naf ORDER BY code_naf$$))),
('ref_categories_juridiques',
    (SELECT COUNT(*) FROM ref_categories_juridiques),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_cj, code_niveau1, libelle_niveau1, code_niveau2, libelle_niveau2, libelle) AS row_text FROM ref_categories_juridiques ORDER BY code_cj$$))),
('ref_tranches_effectifs',
    (SELECT COUNT(*) FROM ref_tranches_effectifs),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', code_tranche, effectif_min, effectif_max, libelle) AS row_text FROM ref_tranches_effectifs ORDER BY code_tranche$$))),
('unites_legales',
    (SELECT COUNT(*) FROM unites_legales),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', siren, statut_diffusion, unite_purgee, etat_administratif, date_creation, date_debut_periode, to_char(date_dernier_traitement AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), denomination, sigle, denomination_usuelle_1, denomination_usuelle_2, denomination_usuelle_3, nom_naissance, nom_usage, prenom_usuel, prenoms, pseudonyme, sexe, identifiant_association, categorie_entreprise, annee_categorie_entreprise, code_cj, code_naf, nomenclature_activite, code_naf_2025, code_tranche_effectifs, annee_effectifs, nic_siege, economie_sociale_solidaire, societe_mission, caractere_employeur) AS row_text FROM unites_legales ORDER BY siren$$))),
('etablissements',
    (SELECT COUNT(*) FROM etablissements),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', siret, siren, nic, etablissement_siege, statut_diffusion, etat_administratif, date_creation, date_debut_periode, to_char(date_dernier_traitement AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), enseigne_1, enseigne_2, enseigne_3, denomination_usuelle, code_naf, nomenclature_activite, code_naf_2025, activite_artisanale, code_tranche_effectifs, annee_effectifs, caractere_employeur, numero_voie, indice_repetition, type_voie, libelle_voie, complement_adresse, distribution_speciale, code_postal, libelle_commune, code_commune, code_cedex, libelle_cedex, code_pays_etranger, libelle_commune_etranger, identifiant_adresse_ban, coord_lambert_x, coord_lambert_y, longitude, latitude) AS row_text FROM etablissements ORDER BY siret$$))),
('etablissements_historique_etat',
    (SELECT COUNT(*) FROM etablissements_historique_etat),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', id, siret, ancien_etat, nouvel_etat, date_effet, to_char(changed_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), etl_log_id) AS row_text FROM etablissements_historique_etat ORDER BY id$$))),
('personnes',
    (SELECT COUNT(*) FROM personnes),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', id, type_personne, nom, prenoms, prenom_usuel, sexe, date_naissance, siren_personne_morale, cle_deduplication) AS row_text FROM personnes ORDER BY id$$))),
('roles_entreprises',
    (SELECT COUNT(*) FROM roles_entreprises),
    (SELECT compute_table_sha256($$SELECT CONCAT_WS('#', id, siren, personne_id, type_role, qualite_detaillee, pourcentage_detention, pourcentage_droits_vote, date_debut, date_fin, actif, source_donnee) AS row_text FROM roles_entreprises ORDER BY id$$)));

SELECT table_name, recs AS found_records, crc_sha2 AS found_crc
FROM found_values
ORDER BY table_name;

SELECT
    e.table_name,
    CASE WHEN e.recs = f.recs THEN 'OK' ELSE 'not ok' END AS records_match,
    CASE WHEN e.crc_sha2 = f.crc_sha2 THEN 'OK' ELSE 'not ok' END AS crc_match
FROM expected_values e
INNER JOIN found_values f USING (table_name)
ORDER BY e.table_name;

SELECT
    'CRC' AS summary,
    CASE WHEN NOT EXISTS (
        SELECT 1
        FROM expected_values e
        JOIN found_values f ON e.table_name = f.table_name
        WHERE f.crc_sha2 <> e.crc_sha2
    ) THEN 'OK' ELSE 'FAIL' END AS result
UNION ALL
SELECT
    'count' AS summary,
    CASE WHEN NOT EXISTS (
        SELECT 1
        FROM expected_values e
        JOIN found_values f ON e.table_name = f.table_name
        WHERE f.recs <> e.recs
    ) THEN 'OK' ELSE 'FAIL' END AS result;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM expected_values e
        JOIN found_values f ON e.table_name = f.table_name
        WHERE f.recs <> e.recs OR f.crc_sha2 <> e.crc_sha2
    ) THEN
        RAISE EXCEPTION 'SIRENE SHA-256 verification failed';
    END IF;
END $$;

DROP FUNCTION compute_table_sha256(TEXT);
DROP TABLE expected_values, found_values;
