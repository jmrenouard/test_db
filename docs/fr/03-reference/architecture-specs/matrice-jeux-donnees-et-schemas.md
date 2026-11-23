# Matrice des jeux de données, schémas, index et sommes de référence

Spécifications exactes des schémas, index, comptages et sommes SHA-256 pour `employees`, `sakila` et `sirene`.

## 1. Synthèse des jeux de données

| Jeu de données | Répertoire | Moteurs cibles | Tables | Vues | Routines / Triggers | Script de vérification |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Employees** | `employees/`, `postgresql/` | MariaDB `10.11+`, MySQL `5.6`–`9.6`, Percona `8.0`/`8.4`, PostgreSQL `12+` | `6` | `2` (+`2` PG) | `7` routines (`objects.sql`) | `test_employees_sha2.sql` / `postgresql/test_employees_sha2.sql` |
| **Sakila Spatial** | `sakila/` | MySQL `5.x`–`9.x`, MariaDB `10.x`–`12.x` | `16` | `7` | `3` procs, `3` foncs, `3` triggers | Contrôles SQL manuels |
| **INSEE Sirene 3NF** | `sirene/` | PostgreSQL `18` (`postgres:18-bookworm`) | `13` | `0` | `0` trigger | `sirene/test_sirene_sha2.sql` |

---

## 2. Empreintes de référence `employees`

| Table | Lignes attendues | `CHECKSUM TABLE` MariaDB | Empreinte SHA-256 canonique |
| :--- | ---: | ---: | :--- |
| `employees` | `300 024` | `610052939` | `21f5d003842f24853e251d3d5116798bafe257ec3d1bb448b5365b68deaabbf4` |
| `departments` | `9` | `3407387832` | `377c5d727383a32633e2973f8e3411beffe29e2f4cc297c586fa6b24aa7df9ba` |
| `dept_manager` | `24` | `3048905531` | `3a4e69723deec413a7d8a4f5ce55013830303fa617b6380ed2b0fd2d48b1c768` |
| `dept_emp` | `331 603` | `3190576018` | `34548ee9989dd4d5e065168b43249c8d3eb48bfbbfb3f2fc1cf01be6658f6a75` |
| `titles` | `443 308` | `1842528371` | `a9e940ef9ba1029a8f0356fdbe495430bedc59eec5ceb4f71e0cc35ddcbf9980` |
| `salaries` | `2 844 047` | `4273816835` | `4e99e691a9ea98fefc0b4fec8ca4e758baeefba2967bd8d6474810a9a5f6e729` |

---

## 3. Schéma PostgreSQL 18 3NF Sirene (`sirene/sql/01_schema_3nf.sql`)

### 3.1 Tables de référence (`7` tables) et clés sentinelles

| Table | Clé primaire | Clés étrangères | Sentinelle(s) |
| :--- | :--- | :--- | :--- |
| `ref_regions` | `code_region VARCHAR(3)` | — | `'UNK'` |
| `ref_departements` | `code_departement VARCHAR(4)` | `code_region -> ref_regions` | `'UNK'` |
| `ref_communes` | `code_commune VARCHAR(5)` | `code_departement -> ref_departements` | `'UNK00'` (`est_active=FALSE`) |
| `ref_pays` | `code_pays VARCHAR(5)` | — | `'UNK'`, `'99100'` (`FR`/`FRA`) |
| `ref_naf` | `code_naf VARCHAR(6)` | — | `'00.00Z'` |
| `ref_categories_juridiques` | `code_cj VARCHAR(4)` | — | `'0000'` |
| `ref_tranches_effectifs` | `code_tranche VARCHAR(2)` | — | `'NN'`, `'UN'` (`[ND]`) |

### 3.2 Tables métier, historique et audit (`6` tables)

| Table | Clé primaire | Rôle principal |
| :--- | :--- | :--- |
| `unites_legales` | `siren VARCHAR(9)` | Unités légales (`etat_administratif IN ('A','C')`, `nom_recherche STORED`) |
| `etablissements` | `siret VARCHAR(14)` | Établissements (`etat_administratif IN ('A','F')`, `adresse_complete` et `enseigne_recherche STORED`, `WGS84`) |
| `etablissements_historique_etat` | `id BIGSERIAL` | Journal des transitions `'A' <-> 'F'` lié à `etl_logs` |
| `personnes` | `id BIGSERIAL` | Personnes physiques et morales (`cle_deduplication UNIQUE`, `nom_complet_recherche STORED`) |
| `roles_entreprises` | `id BIGSERIAL` | Dirigeants, entrepreneurs individuels et bénéficiaires (`UNIQUE NULLS NOT DISTINCT`) |
| `etl_logs` | `id BIGSERIAL` | Trace des exécutions (`REFERENTIALS`, `FULL_IMPORT`, `INCREMENTAL_IMPORT`, `WATCHER_CHECK`) |

### 3.3 Base synthétique Sirene (`15k` UL / `30k` SIRET) et sommes SHA-256 (`sirene/test_sirene_sha2.sql`)

| Table | Lignes attendues | SHA-256 cumulé (`crc_sha2`) |
| :--- | ---: | :--- |
| `ref_regions` | `25` | `7db0f872761b8cc9215b6d8c8f3cb214c393df934acfed85d1fd4a71f6492c4b` |
| `ref_departements` | `112` | `08e8d5cea4a0a9cbfcab1438f237bb8a9c83738a6b385b53334acd425e81801f` |
| `ref_communes` | `563` | `3349552354a42878e8ebf75d2f6842b84a3c43c333f0baf3ce1baf1405129946` |
| `ref_pays` | `11` | `65c2701961adfdab66440d4515bf04bc80278a0b150a5245a8755b6ada0a30dc` |
| `ref_naf` | `39` | `31fc98203d5b3baaa2ff4d44a3a6c46e074c41e53c73729d5b465d1dca1fc26a` |
| `ref_categories_juridiques` | `113` | `9e44d820f4c41d8b0814e7dad7c34dc82ecdbec06a719748703562c8e35f9e4d` |
| `ref_tranches_effectifs` | `17` | `9a85884fa7e14c4c95ac3b88da2a0434901942e39889e9c353149ae71ba5beb7` |
| `unites_legales` | `15 000` | `3625daa7193be62890817fab74bb960fb47cd0a1f80082c287adacf1934b0e8c` |
| `etablissements` | `30 000` | `c7dc6ec325d59d8521b8f96a094c8308de70430d587aa52e2633be4c1778263b` |
| `etablissements_historique_etat` | `1 200` | `ae81915ec8a2601731e9a7df397d8aff0d3882914d02c7f1289c410fcce6d743` |
| `personnes` | `8 000` | `ad3706a3e97fa7744664507d08f122aa13f35bf20a4a0977fc0eac32e0b07310` |
| `roles_entreprises` | `12 000` | `664a167c4819fba977d163e5f49addb6ede2ec945c9423ed2fa6efd96fab16c0` |

## Références associées

- [ADR-001 : ETL Sirene PostgreSQL 18 3NF et qualification MM](../../04-explications/decisions-architecture/adr-001-postgresql18-3nf-sirene-etl-et-qualification-mm.md)
- [Vérifier les sommes de contrôle et la confidentialité](../../02-guides-pratiques/securite/verifier-sommes-controle-et-confidentialite.md)
- [Catalogue des scripts CLI et SQL](../cli-et-scripts/catalogue-scripts-cli-et-sql.md)
