# Guides pratiques et procédures opérationnelles

Cette section regroupe les procédures opérationnelles et les runbooks d'incident de **test_db**, rédigés en
**Français Technique Simplifié (ASD-STF100)**.

## Déploiement

| Guide | Objectif |
| :--- | :--- |
| [Déployer les piles MariaDB et PostgreSQL](deploiement/deployer-piles-mariadb-et-postgresql.md) | Configurer les fichiers `.env`, démarrer MariaDB 11.8 et PostgreSQL 18, puis charger les jeux de base. |

## Exploitation

| Guide | Objectif |
| :--- | :--- |
| [Exécuter Sysbench et l'analyse SQL](exploitation/executer-sysbench-et-analyse-sql.md) | Lancer les campagnes `sysbench`, les profils OLTP, les simulations et les audits `EXPLAIN`. |
| [Exécuter l'ETL Sirene complet et incrémental](exploitation/executer-etl-sirene-complet-et-incremental.md) | Lancer les imports `COPY`, les synchronisations delta, les échantillons Parquet et le watcher. |
| [Qualifier PostgreSQL 18 multi-maître](exploitation/qualifier-postgresql18-multimaitre.md) | Déployer le laboratoire de réplication bidirectionnelle et exécuter les sondes `P1` à `P5`. |

## Gestion des incidents

| Guide | Objectif |
| :--- | :--- |
| [Remédier aux deadlocks, gap locks et dérives ETL](gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) | Résoudre les deadlocks InnoDB, les attentes de gap lock, les annulations `INTRANS` et les divergences `P3`. |

## Sécurité

| Guide | Objectif |
| :--- | :--- |
| [Vérifier les sommes de contrôle et la confidentialité](securite/verifier-sommes-controle-et-confidentialite.md) | Valider les empreintes SHA-256 `employees` et Sirene, contrôler l'absence de PII et auditer `.env`. |

## Autres quadrants documentaires

- [Portail documentaire](../index.md)
- [Tutoriels](../01-tutoriels/index.md)
- [Spécifications de référence](../03-reference/index.md)
- [Explications d'architecture](../04-explications/index.md)
