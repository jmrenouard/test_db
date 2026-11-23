# Datasets, Relational Schemas, Indexes, and Checksum Baselines

Exhaustive schema, index, row-count, and SHA-256 verification specifications for `employees`, `sakila`, and `sirene`
derived from `employees/employees.sql`, `postgresql/employees.sql`, `sakila/sakila-mv-schema.sql`,
`sirene/sql/01_schema_3nf.sql`, `sirene/sql/02_indexes.sql`, and `sirene/test_sirene_sha2.sql`.

## 1. Platform Datasets Summary

| Dataset | Directory | Target Engines | Base Tables | Views | Routines / Triggers | Primary Verification Script |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Employees** | `employees/`, `postgresql/` | MariaDB `10.11+`, MySQL `5.6`–`9.6`, Percona `8.0`/`8.4`, PostgreSQL `12+` | `6` | `2` (+`2` PG views) | `7` routines (`objects.sql` / `postgresql/objects.sql`) | `test_employees_sha2.sql` / `postgresql/test_employees_sha2.sql` |
| **Sakila Spatial** | `sakila/` | MySQL `5.x`–`9.x`, MariaDB `10.x`–`12.x` | `16` | `7` | `3` procs, `3` funcs, `3` triggers (`film_text` sync) | Manual row-count / view checks |
| **INSEE Sirene 3NF** | `sirene/` | PostgreSQL `18` (`postgres:18-bookworm`, PG `15+` features) | `13` | `0` | `0` triggers (`compute_table_sha256` ephemeral in test) | `sirene/test_sirene_sha2.sql` |

---

## 2. Employees Schema & Integrity Baselines

### 2.1 Base Tables (`employees`)

| Table | Primary Key | Foreign Keys | Columns & Engine-Specific Types |
| :--- | :--- | :--- | :--- |
| `employees` | `emp_no` (`INT`) | — | `birth_date DATE`, `first_name VARCHAR(14)`, `last_name VARCHAR(16)`, `gender` (`ENUM('M','F')` in MySQL/MariaDB; `CHAR(1) CHECK (gender IN ('M','F'))` in PostgreSQL), `hire_date DATE` |
| `departments` | `dept_no` (`CHAR(4)`) | — | `dept_name VARCHAR(40) UNIQUE` |
| `dept_manager` | `(emp_no, dept_no)` | `emp_no -> employees(emp_no) ON DELETE CASCADE`, `dept_no -> departments(dept_no) ON DELETE CASCADE` | `from_date DATE NOT NULL`, `to_date DATE NOT NULL` |
| `dept_emp` | `(emp_no, dept_no)` | `emp_no -> employees(emp_no) ON DELETE CASCADE`, `dept_no -> departments(dept_no) ON DELETE CASCADE` | `from_date DATE NOT NULL`, `to_date DATE NOT NULL` |
| `titles` | `(emp_no, title, from_date)` | `emp_no -> employees(emp_no) ON DELETE CASCADE` | `title VARCHAR(50) NOT NULL`, `to_date DATE` (nullable) |
| `salaries` | `(emp_no, from_date)` | `emp_no -> employees(emp_no) ON DELETE CASCADE` | `salary INT NOT NULL`, `to_date DATE NOT NULL` |

### 2.2 Views, Variants & Stored Objects (`employees`)

| Object Name | Kind | Source File | Purpose |
| :--- | :--- | :--- | :--- |
| `dept_emp_latest_date` | View | `employees/employees.sql`, `postgresql/employees.sql` | Latest `from_date` and `to_date` per `emp_no` |
| `current_dept_emp` | View | `employees/employees.sql`, `postgresql/employees.sql` | Current department assignment per employee |
| `v_full_employees`, `v_full_departments` | Views (PG) | `postgresql/objects.sql` | Enriched employee-department and department-manager views |
| `emp_dept_id`, `emp_dept_name`, `emp_name`, `current_manager`, `employees_usage`, `show_departments`, `employees_help` | Functions / Procedures | `employees/objects.sql`, `postgresql/objects.sql` | Lookup helpers (`CALL show_departments()` in MySQL vs `SELECT * FROM show_departments()` in PostgreSQL) |
| Partitioned schemas | DDL variants | `employees/employees_partitioned.sql`, `employees/employees_partitioned_5.1.sql` | Range-partitioned `salaries` and `titles` layouts |

### 2.3 Employees Row Counts, `CHECKSUM TABLE`, and SHA-256 Baselines

Values verified in `scripts/verify_data.sh`, `test_employees_sha2.sql`, and `postgresql/test_employees_sha2.sql`:

| Table | Expected Row Count | MariaDB `CHECKSUM TABLE` | Canonical SHA-256 (`SHA2(..., 256)` / `pgcrypto`) |
| :--- | ---: | ---: | :--- |
| `employees` | `300,024` | `610052939` | `21f5d003842f24853e251d3d5116798bafe257ec3d1bb448b5365b68deaabbf4` |
| `departments` | `9` | `3407387832` | `377c5d727383a32633e2973f8e3411beffe29e2f4cc297c586fa6b24aa7df9ba` |
| `dept_manager` | `24` | `3048905531` | `3a4e69723deec413a7d8a4f5ce55013830303fa617b6380ed2b0fd2d48b1c768` |
| `dept_emp` | `331,603` | `3190576018` | `34548ee9989dd4d5e065168b43249c8d3eb48bfbbfb3f2fc1cf01be6658f6a75` |
| `titles` | `443,308` | `1842528371` | `a9e940ef9ba1029a8f0356fdbe495430bedc59eec5ceb4f71e0cc35ddcbf9980` |
| `salaries` | `2,844,047` | `4273816835` | `4e99e691a9ea98fefc0b4fec8ca4e758baeefba2967bd8d6474810a9a5f6e729` |

---

## 3. Sakila Spatial Overview (`sakila/sakila-mv-schema.sql`)

Modified multi-version Sakila schema (`v0.9`) using `InnoDB` (with conditional MySQL `5.6.10+` `film_text` `InnoDB`
conversion and MySQL `5.7.5+` `GEOMETRY` / `SPATIAL` support).

| Object Category | Count | Exact Object Names & Key Features |
| :--- | :---: | :--- |
| **Base Tables** | `16` | `actor`, `address` (conditional `location GEOMETRY` + `SPATIAL KEY idx_location`), `category`, `city`, `country`, `customer`, `film`, `film_actor`, `film_category`, `film_text` (`FULLTEXT KEY idx_title_description`), `inventory`, `language`, `payment`, `rental` (`UNIQUE (rental_date, inventory_id, customer_id)`), `staff`, `store` (`UNIQUE idx_unique_manager`) |
| **Views** | `7` | `customer_list`, `film_list`, `nicer_but_slower_film_list`, `staff_list`, `sales_by_store`, `sales_by_film_category`, `actor_info` |
| **Triggers** | `3` | `ins_film`, `upd_film`, `del_film` (synchronize `film` mutations to `film_text`) |
| **Stored Procedures** | `3` | `rewards_report`, `film_in_stock`, `film_not_in_stock` |
| **Stored Functions** | `3` | `get_customer_balance`, `inventory_held_by_customer`, `inventory_in_stock` |

---

## 4. Sirene PostgreSQL 18 3NF Schema (`sirene/sql/01_schema_3nf.sql`)

Requires `PostgreSQL >= 15` (tested on `postgres:18-bookworm`) for `UNIQUE NULLS NOT DISTINCT` and immutable
`GENERATED ALWAYS AS (...) STORED` columns, plus the `pg_trgm` extension. Every table defines an explicit
`PRIMARY KEY` (`REPLICA IDENTITY DEFAULT`).

### 4.1 Referential Lookup Tables (7 Tables) & Sentinels

| Table | Primary Key | Foreign Keys | Non-PK Columns & Constraints | Sentinel Key(s) |
| :--- | :--- | :--- | :--- | :--- |
| `ref_regions` | `code_region VARCHAR(3)` | — | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` | `'UNK'` |
| `ref_departements` | `code_departement VARCHAR(4)` | `code_region -> ref_regions(code_region)` | `cheflieu VARCHAR(5)`, `nom_majuscule VARCHAR(100) NOT NULL`, `libelle VARCHAR(120) NOT NULL` | `'UNK'` (`code_region='UNK'`) |
| `ref_communes` | `code_commune VARCHAR(5)` | `code_departement -> ref_departements(code_departement)` | `type_commune VARCHAR(6) NOT NULL DEFAULT 'COM'`, `nom_majuscule VARCHAR(150) NOT NULL`, `libelle VARCHAR(150) NOT NULL`, `est_active BOOLEAN NOT NULL DEFAULT TRUE` | `'UNK00'` (`est_active=FALSE`) |
| `ref_pays` | `code_pays VARCHAR(5)` | — | `code_iso2 CHAR(2)`, `code_iso3 CHAR(3)`, `libelle VARCHAR(150) NOT NULL` | `'UNK'`, `'99100'` (`FR`/`FRA`) |
| `ref_naf` | `code_naf VARCHAR(6)` | — | `nomenclature VARCHAR(12) NOT NULL DEFAULT 'NAFRev2'`, `code_section VARCHAR(2)`, `libelle_section VARCHAR(255)`, `code_division VARCHAR(2)`, `libelle_division VARCHAR(255)`, `code_groupe VARCHAR(4)`, `libelle_groupe VARCHAR(255)`, `code_classe VARCHAR(5)`, `libelle_classe VARCHAR(255)`, `libelle_sous_classe VARCHAR(255) NOT NULL` | `'00.00Z'` |
| `ref_categories_juridiques` | `code_cj VARCHAR(4)` | — | `code_niveau1 VARCHAR(1)`, `libelle_niveau1 VARCHAR(255)`, `code_niveau2 VARCHAR(2)`, `libelle_niveau2 VARCHAR(255)`, `libelle VARCHAR(255) NOT NULL` | `'0000'` |
| `ref_tranches_effectifs` | `code_tranche VARCHAR(2)` | — | `effectif_min INTEGER`, `effectif_max INTEGER`, `libelle VARCHAR(120) NOT NULL` | `'NN'` (non-employing), `'UN'` (`[ND]` masked) |

### 4.2 Core, History, Governance & Audit Tables (6 Tables)

| Table | Primary Key | Foreign Keys & Cascading | Key Columns & Domain Constraints |
| :--- | :--- | :--- | :--- |
| `unites_legales` | `siren VARCHAR(9)` (`CHECK (siren ~ '^[0-9]{9}$')`) | `code_cj -> ref_categories_juridiques`, `code_naf -> ref_naf`, `code_tranche_effectifs -> ref_tranches_effectifs` | `statut_diffusion CHAR(1) DEFAULT 'O'`, `unite_purgee BOOLEAN DEFAULT FALSE`, `etat_administratif CHAR(1) CHECK (IN ('A','C'))`, `date_creation`, `date_debut_periode`, `date_dernier_traitement`, `denomination`, `sigle`, `denomination_usuelle_1..3`, `nom_naissance`, `nom_usage`, `prenom_usuel`, `prenoms`, `pseudonyme`, `sexe`, `identifiant_association`, `categorie_entreprise CHECK (IS NULL OR IN ('PME','ETI','GE'))`, `annee_categorie_entreprise`, `nomenclature_activite`, `code_naf_2025`, `annee_effectifs`, `nic_siege`, `economie_sociale_solidaire`, `societe_mission`, `caractere_employeur`, `nom_recherche` (`STORED`), `updated_at` |
| `etablissements` | `siret VARCHAR(14)` (`CHECK (siret ~ '^[0-9]{14}$')`) | `siren -> unites_legales ON DELETE CASCADE`, `code_naf -> ref_naf`, `code_tranche_effectifs -> ref_tranches_effectifs`, `code_commune -> ref_communes`, `code_pays_etranger -> ref_pays` | `nic VARCHAR(5) NOT NULL`, `etablissement_siege BOOLEAN DEFAULT FALSE`, `statut_diffusion CHAR(1) DEFAULT 'O'`, `etat_administratif CHAR(1) CHECK (IN ('A','F'))`, `enseigne_1..3`, `denomination_usuelle`, `nomenclature_activite`, `code_naf_2025`, `activite_artisanale`, `annee_effectifs`, `caractere_employeur`, `numero_voie`, `indice_repetition`, `type_voie`, `libelle_voie`, `complement_adresse`, `distribution_speciale`, `code_postal`, `libelle_commune`, `code_cedex`, `libelle_cedex`, `libelle_commune_etranger`, `adresse_complete` (`STORED`), `enseigne_recherche` (`STORED`), `identifiant_adresse_ban`, `coord_lambert_x/y NUMERIC(12,2)`, `longitude/latitude DOUBLE PRECISION`, `updated_at` |
| `etablissements_historique_etat` | `id BIGSERIAL` | `siret -> etablissements ON DELETE CASCADE` | `ancien_etat CHAR(1) NOT NULL`, `nouvel_etat CHAR(1) NOT NULL`, `date_effet DATE`, `changed_at TIMESTAMPTZ DEFAULT NOW()`, `etl_log_id BIGINT` |
| `personnes` | `id BIGSERIAL` | `siren_personne_morale -> unites_legales ON DELETE SET NULL` | `type_personne VARCHAR(10) CHECK (IN ('PHYSIQUE','MORALE'))`, `nom`, `prenoms`, `prenom_usuel`, `sexe`, `date_naissance`, `cle_deduplication VARCHAR(128) NOT NULL UNIQUE`, `nom_complet_recherche` (`STORED`), `created_at`, `updated_at` |
| `roles_entreprises` | `id BIGSERIAL` | `siren -> unites_legales ON DELETE CASCADE`, `personne_id -> personnes ON DELETE CASCADE` | `type_role` (`ENTREPRENEUR_INDIVIDUEL`, `GERANT`, `PRESIDENT`, `DIRECTEUR_GENERAL`, `ADMINISTRATEUR`, `ASSOCIE`, `ACTIONNAIRE`, `BENEFICIAIRE_EFFECTIF`, `AUTRE`), `qualite_detaillee`, `pourcentage_detention` (`0..100`), `pourcentage_droits_vote` (`0..100`), `date_debut`, `date_fin`, `actif BOOLEAN DEFAULT TRUE`, `source_donnee DEFAULT 'SIRENE'`, `UNIQUE NULLS NOT DISTINCT (siren, personne_id, type_role, date_debut)` |
| `etl_logs` | `id BIGSERIAL` | — | `run_type CHECK (IN ('REFERENTIALS','FULL_IMPORT','INCREMENTAL_IMPORT','WATCHER_CHECK'))`, `entity_type`, `resource_id`, `source_url`, `file_name`, `file_version`, `checksum_type`, `checksum_value`, `rows_processed/inserted/updated`, `status CHECK (IN ('RUNNING','SUCCESS','FAILED','SKIPPED'))`, `started_at`, `finished_at`, `error_message`, `metadata JSONB DEFAULT '{}'::jsonb` |

### 4.3 Generated `STORED` Columns (`sirene/sql/01_schema_3nf.sql`)

| Table | Column | Source Expressions (`IMMUTABLE` `TRIM`/`COALESCE`/`NULLIF`/`\|\|`) | Backing Index |
| :--- | :--- | :--- | :--- |
| `unites_legales` | `nom_recherche` | `denomination`, `sigle`, `denomination_usuelle_1`, `COALESCE(NULLIF(TRIM(nom_usage), ''), nom_naissance)`, `prenom_usuel` | `idx_ul_nom_trgm` |
| `etablissements` | `adresse_complete` | `numero_voie`, `indice_repetition`, `type_voie`, `libelle_voie`, `complement_adresse`, `code_postal`, `COALESCE(NULLIF(TRIM(libelle_commune), ''), libelle_commune_etranger)` | — |
| `etablissements` | `enseigne_recherche` | `enseigne_1`, `enseigne_2`, `enseigne_3`, `denomination_usuelle` | `idx_etab_enseigne_trgm` |
| `personnes` | `nom_complet_recherche` | `nom`, `prenoms` | `idx_personnes_nom_trgm` |

---

## 5. Sirene Secondary & Trigram GIN Indexes (`sirene/sql/02_indexes.sql`)

All `25` indexes below are dropped by `db.drop_secondary_indexes()` before full-stock `COPY FROM STDIN` and rebuilt
by `db.rebuild_indexes_and_analyze()`. Constraint-backed `PRIMARY KEY` and `UNIQUE` indexes remain active.

### 5.1 Trigram GIN Indexes (`pg_trgm`)

| Index Name | Table | Indexed Column & Operator Class | Storage Options |
| :--- | :--- | :--- | :--- |
| `idx_ul_nom_trgm` | `unites_legales` | `(nom_recherche gin_trgm_ops)` | `USING GIN`, `WITH (fastupdate = on)` |
| `idx_etab_enseigne_trgm` | `etablissements` | `(enseigne_recherche gin_trgm_ops)` | `USING GIN`, `WITH (fastupdate = on)` |
| `idx_personnes_nom_trgm` | `personnes` | `(nom_complet_recherche gin_trgm_ops)` | `USING GIN`, `WITH (fastupdate = on)` |

### 5.2 Secondary B-Tree & Partial Indexes (`22` Indexes)

| Index Name | Table | Definition / Predicate | Role |
| :--- | :--- | :--- | :--- |
| `idx_ref_departements_code_region` | `ref_departements` | `(code_region)` | FK join acceleration |
| `idx_ref_communes_code_departement` | `ref_communes` | `(code_departement)` | FK join acceleration |
| `idx_ul_code_cj` | `unites_legales` | `(code_cj)` | FK & legal-category filter |
| `idx_ul_code_naf` | `unites_legales` | `(code_naf)` | FK & sector filter |
| `idx_ul_code_tranche_effectifs` | `unites_legales` | `(code_tranche_effectifs)` | FK & headcount filter |
| `idx_ul_etat_administratif` | `unites_legales` | `(etat_administratif)` | Active (`'A'`) vs ceased (`'C'`) filter |
| `idx_ul_categorie_entreprise` | `unites_legales` | `(categorie_entreprise)` | `PME` / `ETI` / `GE` filter |
| `idx_ul_date_dernier_traitement` | `unites_legales` | `(date_dernier_traitement)` | Temporal watermark scan |
| `idx_etab_siren` | `etablissements` | `(siren)` | FK join & multi-site grouping |
| `idx_etab_code_commune` | `etablissements` | `(code_commune)` | FK & municipality join |
| `idx_etab_code_naf` | `etablissements` | `(code_naf)` | FK & NAF aggregation |
| `idx_etab_code_tranche_effectifs` | `etablissements` | `(code_tranche_effectifs)` | FK & headcount aggregation |
| `idx_etab_code_pays_etranger` | `etablissements` | `(code_pays_etranger)` | FK & foreign site isolation |
| `idx_etab_code_postal` | `etablissements` | `(code_postal)` | Postal code lookup |
| `idx_etab_etat_administratif` | `etablissements` | `(etat_administratif)` | Active (`'A'`) vs closed (`'F'`) filter |
| `idx_etab_date_dernier_traitement` | `etablissements` | `(date_dernier_traitement)` | Temporal watermark scan |
| `idx_etab_naf_commune_actif` | `etablissements` | `(code_naf, code_commune) WHERE etat_administratif = 'A'` | Partial composite active-site lookup |
| `idx_etab_hist_siret` | `etablissements_historique_etat` | `(siret)` | FK lookup for transition history |
| `idx_personnes_siren_pm` | `personnes` | `(siren_personne_morale)` | FK lookup for corporate officers |
| `idx_roles_siren` | `roles_entreprises` | `(siren)` | FK lookup by company |
| `idx_roles_personne_id` | `roles_entreprises` | `(personne_id)` | FK lookup by officer portfolio |
| `idx_etl_logs_entity_status_finished` | `etl_logs` | `(entity_type, status, finished_at DESC)` | Latest successful checksum lookup |

---

## 6. Sirene Synthetic Baseline (`15k` UL / `30k` SIRET) & SHA-256 Matrix

Generated deterministically by `sirene/scripts/generate_synthetic_dataset.py` (`SEED = 20261120`, SIREN range
`900000001`–`900015050`, zero PII). Verified by `sirene/test_sirene_sha2.sql` using built-in PostgreSQL
`sha256(bytea)` (`encode(sha256(convert_to(crc || '#' || r.row_text, 'UTF8')), 'hex')`).

### 6.1 Cumulative SHA-256 & Row-Count Baseline (`sirene/test_sirene_sha2.sql`)

| Table | Expected Rows | Canonical SHA-256 (`crc_sha2`) |
| :--- | ---: | :--- |
| `ref_regions` | `25` | `7db0f872761b8cc9215b6d8c8f3cb214c393df934acfed85d1fd4a71f6492c4b` |
| `ref_departements` | `112` | `08e8d5cea4a0a9cbfcab1438f237bb8a9c83738a6b385b53334acd425e81801f` |
| `ref_communes` | `563` | `3349552354a42878e8ebf75d2f6842b84a3c43c333f0baf3ce1baf1405129946` |
| `ref_pays` | `11` | `65c2701961adfdab66440d4515bf04bc80278a0b150a5245a8755b6ada0a30dc` |
| `ref_naf` | `39` | `31fc98203d5b3baaa2ff4d44a3a6c46e074c41e53c73729d5b465d1dca1fc26a` |
| `ref_categories_juridiques` | `113` | `9e44d820f4c41d8b0814e7dad7c34dc82ecdbec06a719748703562c8e35f9e4d` |
| `ref_tranches_effectifs` | `17` | `9a85884fa7e14c4c95ac3b88da2a0434901942e39889e9c353149ae71ba5beb7` |
| `unites_legales` | `15,000` | `3625daa7193be62890817fab74bb960fb47cd0a1f80082c287adacf1934b0e8c` |
| `etablissements` | `30,000` | `c7dc6ec325d59d8521b8f96a094c8308de70430d587aa52e2633be4c1778263b` |
| `etablissements_historique_etat` | `1,200` | `ae81915ec8a2601731e9a7df397d8aff0d3882914d02c7f1289c410fcce6d743` |
| `personnes` | `8,000` | `ad3706a3e97fa7744664507d08f122aa13f35bf20a4a0977fc0eac32e0b07310` |
| `roles_entreprises` | `12,000` | `664a167c4819fba977d163e5f49addb6ede2ec945c9423ed2fa6efd96fab16c0` |

`etl_logs` holds `4` baseline entries after `sirene/load_sirene.sql` (`4` `REFERENTIALS`/`FULL_IMPORT` seed rows)
and is excluded from `test_sirene_sha2.sql` and `mm_probe.py` replication publications.

### 6.2 Embedded Offline Artifacts (`sirene/data/`)

| Artifact Path | Format | Row Count | File Size (bytes) |
| :--- | :--- | ---: | ---: |
| `sirene/data/sql/01_load_referentials.sql` | PostgreSQL `COPY` (LF) | `880` across `7` tables | `59,223` |
| `sirene/data/sql/02_load_unites_legales.sql` | PostgreSQL `COPY` (LF) | `15,000` | `2,863,248` |
| `sirene/data/sql/03_load_etablissements.sql` | PostgreSQL `COPY` (LF) | `30,000` | `8,635,625` |
| `sirene/data/sql/04_load_governance_and_history.sql` | PostgreSQL `COPY` + `setval` (LF) | `21,204` (`8k` / `12k` / `1.2k` / `4`) | `1,924,344` |
| `sirene/data/parquet/StockUniteLegale_synthetic.parquet` | ZSTD Parquet | `15,000` | `358,462` |
| `sirene/data/parquet/StockEtablissement_synthetic.parquet` | ZSTD Parquet | `30,000` | `1,116,994` |
| `sirene/data/delta/DeltaUniteLegale_synthetic.parquet` | ZSTD Parquet | `250` (`200` updates + `50` inserts) | `15,296` |
| `sirene/data/delta/DeltaEtablissement_synthetic.parquet` | ZSTD Parquet | `500` (`400` updates / `150` `'A'->'F'` + `100` inserts) | `29,356` |
| `sirene/data/delta/DeltaEtablissement_synthetic.csv.zip` | Zipped UTF-8 CSV | `500` | `22,728` |

## Related Reference & Guides

- Architecture rationale for PG 18 3NF and `mm_probe.py`:
  [ADR-001: PostgreSQL 18 3NF Sirene ETL & Multi-Master Qualification](../../04-explanation/design-decisions/adr-001-postgresql18-3nf-sirene-etl-and-mm-qualification.md)
- Checksum verification and privacy operational checks:
  [Verify Checksums and Privacy Boundaries](../../02-how-to-guides/security/verify-checksums-and-privacy-boundaries.md)
- CLI options and SQL query catalogs:
  [CLI Scripts and SQL Catalog](../cli-and-scripts/cli-scripts-and-sql-catalog.md)
