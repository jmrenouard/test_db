# Catalogue des scripts CLI, codes retour et requêtes SQL

Syntaxe CLI, options, codes retour et catalogues SQL issus de `sirene/*.py`, `scripts/*`,
`interactive_runner.py`, `employees/req_employees.sql` (`60` requêtes) et `sirene/sql/03_sample_queries.sql` (`15` requêtes).

## 1. Scripts Python et Bash

| Script | Options principales | Codes retour |
| :--- | :--- | :--- |
| `sirene/full_import.py` | `--ul-file`, `--etab-file`, `--ref-dir`, `--offline-refs`, `--limit-rows`, `--force` | `0` succès/ignoré ; `1` erreur ; `2` CLI |
| `sirene/incremental_import.py` | `--ul-file`, `--etab-file`, `--force` | `0` succès/ignoré ; `1` erreur ; `2` CLI |
| `sirene/watcher.py` | `--once`, `--interval`, `--force`, `--offline-refs` | `0` succès ; non nul si échec `--once` |
| `sirene/mm_probe.py` | `--dsn-a`, `--dsn-b`, `--candidate-name`, `--setup-native-birep`, `--batch-rows`, `--timeout-sec`, `--output-md`, `--output-json` | `0` scorecard affiché ; non nul si échec |
| `scripts/db_simulator.py` | `--sql-dir` \| `--script`, `--host`, `--user`, `--password`, `--db`, `--threads`, `--time`, `--container`, `--output-dir` | `0` succès ; `1` simulation en échec ; `2` CLI |
| `scripts/sql_analyzer.py` | `--query-file`, `--query`, `--container`, `--host`, `--port`, `--user`, `--password`, `--db`, `--stdout` | `0` succès ; `1` fichier manquant ; `2` CLI |
| `scripts/inject_fake_employees.py` | `--count`, `--start-emp-no`, `--db-name`, `--container`, `--use-container`, `--dry-run`, `--output-sql`, `--seed` | `0` succès ; `1` erreur MariaDB |
| `scripts/perf_threads_reporter.py` | `--dir`, `--md`, `--html` | `0` succès ; `1` aucun résultat |
| `interactive_runner.py` | `-a/--auto`, `--run-all`, `-i/--interactive` | `0` fin normale ; non nul si erreur |
| `scripts/test_runner.sh` | `inject`, `verify`, `analyze`, `bench`, `perf-threads`, `std-oltp`, `data-tests`, `all`, `help` | `0` succès ; `1` argument/fichier invalide |
| `scripts/run_dir_bench.sh` | `--sql-dir`, `--script`, `--threads`, `--time`, `--host`, `--container`, `--user`, `--password`, `--db`, `-h/--help` | `0` succès ; `1` argument invalide |
| `scripts/verify_data.sh` | `[container] [user] [password] [db]` | `0` si 0 erreur ; `1` si écart |

## 2. Catalogue SQL Sirene (`sirene/sql/03_sample_queries.sql`, `15` requêtes)

| ID | Domaine analytique / recherche | Tables jointes | Index principaux |
| :---: | :--- | :--- | :--- |
| `1` | Recherche exacte SIREN / SIRET | `etablissements`, `unites_legales`, 7 référentiels | `unites_legales_pkey`, `etablissements_pkey`, `idx_etab_siren` |
| `2` | Division NAF active + dirigeants | `etablissements`, `unites_legales`, `roles_entreprises`, `personnes` | `idx_etab_code_naf`, `idx_roles_siren` |
| `3` | Recherche floue `pg_trgm` unifiée | `unites_legales`, `etablissements`, `personnes` | `idx_ul_nom_trgm`, `idx_etab_enseigne_trgm`, `idx_personnes_nom_trgm` |
| `4` | Portefeuille de mandats d'un dirigeant | `roles_entreprises`, `personnes`, `unites_legales`, `etablissements` | `idx_roles_personne_id`, `idx_personnes_siren_pm` |
| `5` | Entrepreneurs individuels actifs | `roles_entreprises`, `personnes`, `unites_legales`, `etablissements` | `idx_ul_etat_administratif`, `idx_etab_code_commune` |
| `6` | Proximité géographique WGS84 / Haversine | `etablissements`, `unites_legales` | `idx_etab_etat_administratif`, `unites_legales_pkey` |
| `7` | Agrégation hiérarchique `ROLLUP` NAF 5 niveaux | `etablissements`, `ref_naf` | `idx_etab_code_naf`, `ref_naf_pkey` |
| `8` | Densité régionale / départementale | `ref_regions`, `ref_departements`, `ref_communes`, `etablissements` | `idx_ref_communes_code_departement`, `idx_etab_code_commune` |
| `9` | Répartition `PME`/`ETI`/`GE`, ESS et mission | `unites_legales`, `ref_categories_juridiques`, `etablissements` | `idx_ul_categorie_entreprise`, `idx_ul_code_cj` |
| `10` | Groupes multi-établissements (`COUNT >= 2`) | `unites_legales`, `etablissements`, `ref_communes` | `idx_etab_siren`, `idx_etab_code_commune` |
| `11` | Historique de fermetures `'A' -> 'F'` | `etablissements_historique_etat`, `etablissements`, `etl_logs` | `idx_etab_hist_siret`, `etl_logs_pkey` |
| `12` | Cohortes de création par décennie/année | `unites_legales`, `ref_tranches_effectifs` | `idx_ul_etat_administratif` |
| `13` | Établissements implantés à l'étranger | `etablissements`, `ref_pays` | `idx_etab_code_pays_etranger` |
| `14` | Audit qualité (`[ND]`, `UNK00`, `HIST`, `'C'`) | `unites_legales`, `etablissements`, `ref_communes`, `ref_naf` | `idx_etab_code_commune`, `idx_etab_code_naf` |
| `15` | Santé `etl_logs` et volumétrie `pg_stat_user_tables` | `etl_logs`, `pg_stat_user_tables` | `idx_etl_logs_entity_status_finished` |

## Documentation associée

- [Exécuter Sysbench et l'analyse SQL](../../02-guides-pratiques/exploitation/executer-sysbench-et-analyse-sql.md)
- [Exécuter l'ETL Sirene complet et incrémental](../../02-guides-pratiques/exploitation/executer-etl-sirene-complet-et-incremental.md)
- [Matrice des jeux de données et schémas](../architecture-specs/matrice-jeux-donnees-et-schemas.md)
