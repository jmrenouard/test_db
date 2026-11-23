# Tutoriels

> [!NOTE]
> **Quadrant orienté apprentissage (`01-tutoriels/`) :** Suivez ces laboratoires Docker autonomes pour pratiquer
> `test_db` sur des conteneurs locaux isolés et des jeux de données synthétiques.

Chaque tutoriel démarre depuis un état propre, fournit des commandes `make` et `docker` exactes avec leurs sorties
attendues, et arrête ou nettoie les conteneurs en fin de séance.

---

## Parcours d'apprentissage guidé

| Leçon | Compétences pratiquées | Commandes et sous-systèmes clés |
| :--- | :--- | :--- |
| [1. Bac à sable MariaDB 11.8 Employees](01-bac-a-sable-mariadb-employees.md) | Démarrer `mariadb-11-8`, injecter le schéma `employees` à 6 tables, vérifier CRC32 et SHA-256, puis arrêter | `make start`, `make inject`, `make verify`, `test_employees_sha2.sql`, `make stop` |
| [2. Lab Sirene PostgreSQL 18 3NF hors ligne](02-lab-sirene-postgresql18-hors-ligne.md) | Démarrer PostgreSQL 18 sur `127.0.0.1:15432`, charger `15 000` UL / `30 000` SIRET en SQL et Parquet, et inspecter les deltas | `make sirene-up`, `make sirene-inject`, `make sirene-verify`, `make sirene-import-sample`, `make sirene-incremental-sample` |
| [3. Lab Concurrence et Benchmarks](03-lab-concurrence-et-benchmarks.md) | Exécuter les benchmarks Sysbench, simuler les deadlocks et gap locks InnoDB, lancer `EXPLAIN` et nettoyer | `make bench`, `make test-data TEST=deadlock`, `make test-data TEST=gap_locking`, `make analyze`, `make clean` |

---

## Manuels techniques

Pour les guides techniques thématiques en français :

- [Index des guides techniques (FR)](../../../documentation/fr/index.md)

---

## Étapes suivantes

- Exécuter les procédures de déploiement, d'ETL, de qualification multi-maître et de sécurité :
  [Guides pratiques](../02-guides-pratiques/index.md)
- Consulter les schémas complets, cibles `Makefile`, variables, options CLI et codes d'erreur :
  [Référence](../03-reference/index.md)
- Étudier la topologie, les verrous et les décisions d'architecture ADR :
  [Explications](../04-explications/index.md)
