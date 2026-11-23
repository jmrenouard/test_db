# Architecture, décisions de conception et explications techniques

Ce quadrant explique comment **test_db** unifie la validation multi-moteurs (`MariaDB`, `MySQL`, `Percona`,
`PostgreSQL`), pourquoi le pipeline ETL Sirene PostgreSQL 18 3NF et la publication Diátaxis séparée EN/FR ont été
conçus ainsi, et comment se comportent les verrous et la réplication sous contention.

## Contenu

| Document | Thème | Sujets clés |
| :--- | :--- | :--- |
| [Architecture plateforme et ETL](vue-architecture/architecture-plateforme-et-etl.md) | Topologie système | Banc multi-moteurs MariaDB/MySQL/Percona/PostgreSQL, orchestration `Makefile` et pipeline ETL Sirene en 5 étapes |
| [ADR-001 : ETL Sirene PostgreSQL 18 3NF et qualification MM](decisions-architecture/adr-001-postgresql18-3nf-sirene-etl-et-qualification-mm.md) | Décision moteur et données | Schéma 3NF à 13 tables, `COPY FROM STDIN`, upsert monotone et disqualification `P3` de `origin=none` |
| [ADR-002 : Architecture Diátaxis et publication MkDocs](decisions-architecture/adr-002-diataxis-et-publication-mkdocs-versionnee.md) | Décision documentaire | Arborescence Diátaxis EN/FR séparée (`mkdocs.yml` + `mkdocs.fr.yml`), `git archive` creux, `versions.json` et SFTP IONOS |
| [Compromis concurrence, verrouillage et réplication](analyses-internes/compromis-concurrence-verrous-et-replication.md) | Analyse interne | Graphes d'attente InnoDB, gap locks `REPEATABLE READ`, verrous consultatifs PostgreSQL et causalité split-brain `P3` |

## Contexte et gouvernance

- **Guides techniques (FR)** : Consultez l'[Index des guides techniques (FR)](../../../documentation/fr/index.md), le
  [Guide plateforme Sirene (FR)](../../../documentation/fr/sirene_platform.md) et le
  [Démarrage rapide Sirene](../../../sirene/README.md).
- **Traçabilité d'ingénierie** : Consultez le [Journal d'actions](../../ACTION_LOGBOOK.md), le
  [Registre RCA](../../RCA_REGISTER.md) et le [Changelog](../../../Changelog).

## Autres quadrants documentaires

- **Accueil** : [Portail documentaire](../index.md)
- **Tutoriels** : [Travaux pratiques guidés](../01-tutoriels/index.md)
- **Guides pratiques** : [Procédures opérationnelles et runbooks](../02-guides-pratiques/index.md)
- **Référence** : [Schémas, configuration, CLI et codes d'erreur](../03-reference/index.md)
