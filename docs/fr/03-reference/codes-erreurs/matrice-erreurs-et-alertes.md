# Matrice des erreurs, RCA et alertes opérationnelles

Taxonomie consolidée des causes racines (`RCA-001` à `RCA-007`), codes d'erreur base de données, statuts de sonde
`mm_probe.py` et liens directs vers les runbooks de remédiation.

## 1. Matrice des analyses de causes racines (`docs/RCA_REGISTER.md`)

| Code / Échec | Composant | Symptôme observé | Cause racine | Runbook de remédiation |
| :--- | :--- | :--- | :--- | :--- |
| **`RCA-001`** Ambiguïté fork `gh` | GitHub CLI (`gh`) | `gh issue` / `gh pr` cible `upstream` (`datacharmer/test_db`) au lieu du fork. | Présence de `origin` et `upstream` sans `-R jmrenouard/test_db`. | [Vérifier les sommes de contrôle et la confidentialité](../../02-guides-pratiques/securite/verifier-sommes-controle-et-confidentialite.md) |
| **`RCA-002`** Espaces CSV et `[ND]` | `sirene_etl.transforms` | Colonne introuvable ou erreur de conversion sur `[ND]`. | En-têtes CSV avec espaces finaux et sentinelles `[ND]`/`[nd]`. | [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) |
| **`RCA-003`** Collision port `5432` | `sirene-postgres` | Échec d'écoute ou routage vers un PostgreSQL hôte existant. | Conflit avec un daemon système sur `127.0.0.1:5432` ; stack isolée sur `15432`. | [Déployer les piles MariaDB et PostgreSQL](../../02-guides-pratiques/deploiement/deployer-piles-mariadb-et-postgresql.md) |
| **`RCA-004`** `INTRANS` + `SAVEPOINT` | `sirene_etl.incremental_import` | L'import rapporte des mises à jour mais aucune ligne ne persiste. | Verrou/checksum préalable laissait `conn` en `INTRANS`, transformant `transaction()` en `SAVEPOINT`. | [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) |
| **`RCA-005`** `%%` et `AccessShareLock` | `psycopg` v3 / `sirene_etl.db` | Erreur `operator does not exist: text %% unknown` ou blocage `DROP INDEX`. | `psycopg` v3 ne dé-échappe `%%` qu'avec paramètres ; session ouverte sans `autocommit=True`. | [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) |
| **`RCA-006`** Montage volume PG 18 | Docker `postgres:18-bookworm` | Échec d'initialisation sur `/var/lib/postgresql/data`. | PG 18 exige le point de montage sur `/var/lib/postgresql`. | [Déployer les piles MariaDB et PostgreSQL](../../02-guides-pratiques/deploiement/deployer-piles-mariadb-et-postgresql.md) |
| **`RCA-007`** `pg_trgm` `%` et split-brain `P3` | `sirene_etl.mm_probe` | `incomplete placeholder: '%'` ou divergence silencieuse Nœud A / Nœud B. | Requête paramétrée nécessitant `%%`, et PG 18 `origin=none` sans résolution CRDT/LWW. | [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) |

## 2. Sondes de qualification multi-maître (`sirene/mm_probe.py`)

| Sonde | Statuts possibles | Impact sur le verdict | Guide associé |
| :--- | :--- | :--- | :--- |
| `P1_DDL_COMPAT` | `PASS` / `WARN` / `FAIL` | `WARN` (verrou consultatif local) -> `CONDITIONAL_PARTITIONED_WRITES_ONLY` | [Qualifier PostgreSQL 18 multi-maître](../../02-guides-pratiques/exploitation/qualifier-postgresql18-multimaitre.md) |
| `P2_SEQUENCE_SPLIT_BRAIN` | `PASS` / `FAIL` | `FAIL` -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Qualifier PostgreSQL 18 multi-maître](../../02-guides-pratiques/exploitation/qualifier-postgresql18-multimaitre.md) |
| `P3_CONCURRENT_SIRET_UPSERT` | `PASS` / `WARN` / `FAIL` | `FAIL` (`DIVERGED_SPLIT_BRAIN` sur `origin=none`) -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md) |
| `P4_CROSS_NODE_FK_CAUSALITY` | `PASS` / `WARN` / `FAIL` | `WARN` (`23503` transitoire) -> `CONDITIONAL_PARTITIONED_WRITES_ONLY` | [Qualifier PostgreSQL 18 multi-maître](../../02-guides-pratiques/exploitation/qualifier-postgresql18-multimaitre.md) |
| `P5_BULK_COPY_REPLICATION_LAG` | `PASS` / `FAIL` | `FAIL` si latence > `timeout_sec` -> `INCOMPATIBLE_WITH_SIRENE_3NF` | [Qualifier PostgreSQL 18 multi-maître](../../02-guides-pratiques/exploitation/qualifier-postgresql18-multimaitre.md) |

## Documentation associée

- [Compromis concurrence, verrouillage et réplication](../../04-explications/analyses-internes/compromis-concurrence-verrous-et-replication.md)
- [Remédier aux deadlocks, gap locks et dérives ETL](../../02-guides-pratiques/gestion-incidents/remedier-deadlocks-gap-locks-et-derive-etl.md)
- [Vérifier les sommes de contrôle et la confidentialité](../../02-guides-pratiques/securite/verifier-sommes-controle-et-confidentialite.md)
