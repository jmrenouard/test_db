# Référence : schémas, configuration, CLI, SQL et matrice d'erreurs

Spécifications techniques de **test_db** (`v1.12.0`) : MariaDB `11.8` / MySQL / Percona (`employees`, `sakila`),
PostgreSQL `12+` (`employees`) et PostgreSQL `18` (`sirene` ETL 3NF et qualification multi-maître).

## Spécifications principales

| Document | Périmètre | Sources principales |
| :--- | :--- | :--- |
| [Matrice des jeux de données et schémas](architecture-specs/matrice-jeux-donnees-et-schemas.md) | `employees` (`6` tables, `2` vues), `sakila` (`16` tables, `7` vues), `sirene` (`13` tables, `7` sentinelles, `4` colonnes `STORED`, `25` index dont `3` GIN `pg_trgm`) et empreintes SHA-256. | `employees/employees.sql`, `sakila/sakila-mv-schema.sql`, `sirene/sql/01_schema_3nf.sql`, `sirene/test_sirene_sha2.sql` |
| [Variables d'environnement et cibles Makefile](configuration/variables-environnement-et-cibles-makefile.md) | Inventaire complet des cibles `Makefile`, surcharges `.env`, paramètres PostgreSQL 18 et secrets CI/CD MkDocs. | `Makefile`, `.env_local`, `.env_mariadb118`, `sirene/.env.example`, `sirene/docker-compose.yml` |
| [Catalogue des scripts CLI et SQL](cli-et-scripts/catalogue-scripts-cli-et-sql.md) | Options, arguments et codes retour des scripts Python/Bash et catalogues des `60` requêtes `employees` et `15` requêtes `sirene`. | `sirene/*.py`, `scripts/*`, `interactive_runner.py`, `employees/req_employees.sql`, `sirene/sql/03_sample_queries.sql` |
| [Matrice des erreurs et alertes](codes-erreurs/matrice-erreurs-et-alertes.md) | Codes d'erreur, taxonomie RCA (`RCA-001` à `RCA-007`), deadlocks/gap locks, verdicts `mm_probe.py` et liens de remédiation. | `docs/RCA_REGISTER.md`, `sirene/src/sirene_etl/*.py`, `scripts/verify_data.sh` |

## Guides techniques et références complémentaires

| Document | Périmètre |
| :--- | :--- |
| [Index des guides techniques (FR)](../../../documentation/fr/index.md) | Index des manuels techniques MariaDB, Sysbench, analyseur SQL et Sirene |
| [Guide plateforme PostgreSQL 18 3NF Sirene (FR)](../../../documentation/fr/sirene_platform.md) | Dictionnaire de données 13 tables, guide CLI et texte SQL des 15 requêtes Sirene |
| [Documentation schéma Employees (FR)](../../../doc_employees/employees_fr.md) | Modèle relationnel Employees et 60 requêtes SQL exemples |
| [Démarrage rapide Sirene (EN)](../../../sirene/README.md) | Arborescence du module, cibles Compose et guide `mm_probe.py` |

## Traçabilité et versions

| Registre | Périmètre | Emplacement |
| :--- | :--- | :--- |
| **Changelog** | Historique sémantique des versions jusqu'à `1.12.0` | [`Changelog`](../../../Changelog) |
| **Journal d'actions (EN)** | Jalons (`M1`–`M9`) et actions vérifiées (`ACT-000`–`ACT-005`) | [`ACTION_LOGBOOK.md`](../../ACTION_LOGBOOK.md) |
| **Registre RCA (EN)** | Analyses RCA (`RCA-001`–`RCA-007`), `IMP-*`, `APP-*` et `IDEA-*` | [`RCA_REGISTER.md`](../../RCA_REGISTER.md) |

## Autres quadrants documentaires

| Quadrant | Objectif | Point d'entrée |
| :--- | :--- | :--- |
| **Accueil** | Portail principal et vue d'ensemble Diátaxis | [Portail documentaire](../index.md) |
| **Tutoriels** | Travaux pratiques Docker isolés | [Index Tutoriels](../01-tutoriels/index.md) |
| **Guides pratiques** | Procédures opérationnelles et runbooks d'astreinte | [Index Guides pratiques](../02-guides-pratiques/index.md) |
| **Explications** | Architecture, décisions ADR et compromis techniques | [Index Explications](../04-explications/index.md) |
