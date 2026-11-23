# 📊 test_db (Base de données Employees)

Une base de données exemple avec une suite de tests intégrée, utilisée pour tester vos applications et vos serveurs de bases de données. Ce dépôt fournit un ensemble de données conséquent (300 000 employés, 2,8M de salaires) pour les tests de performance et la pratique de requêtes complexes.

---

## 🚀 Configuration & Utilisation (Méthode Moderne)

Ce projet est optimisé pour un environnement Docker **MariaDB 11.8+**. Un `Makefile` est fourni pour simplifier les opérations courantes.

### 1. Prérequis

- Docker & Docker Compose
- Make
- Python 3 (pour le reporting premium)

### 2. Commandes Principales

| Commande | Action |
| :--- | :--- |
| `make start` | Démarre le conteneur MariaDB (`mariadb-11-8`). |
| `make status` | Vérifie si la base de données est opérationnelle. |
| `make inject` | Injecte le jeu de données `employees.sql` dans le conteneur. |
| `make test-all` | **Recommandé** : Exécute Verify + Analyze + Bench en une seule fois. |
| `make interactive` | Lance le gestionnaire de tests HTML <www.lightpath.fr>. |
| `make stop` | Arrête le conteneur MariaDB. |
| `make clean` | Supprime tous les rapports et artefacts générés. |

---

## 🌐 Portail MkDocs Publié & Documentation Diátaxis

La documentation unifiée et versionnée est publiée sur [**https://test-db.lightpath.fr/fr/**](https://test-db.lightpath.fr/fr/)
et structurée selon les quatre quadrants Diátaxis dans `docs/fr/` :

| Pilier | Périmètre | Point d'entrée |
| :--- | :--- | :--- |
| **Portail en ligne versionné** | Site MkDocs Material multi-versions (`master` / `latest` / `v1.9.0+`) | [**https://test-db.lightpath.fr/fr/**](https://test-db.lightpath.fr/fr/) |
| **Accueil Diátaxis (FR)** | Portail central de la documentation française | [`docs/fr/index.md`](docs/fr/index.md) |
| **1. Tutoriels (`docs/fr/01-tutoriels/`)** | Travaux pratiques Docker isolés (Employees, Sirene PG 18, concurrence et Sysbench) | [`docs/fr/01-tutoriels/index.md`](docs/fr/01-tutoriels/index.md) |
| **2. Guides pratiques (`docs/fr/02-guides-pratiques/`)** | Procédures ASD-STF100 d'exploitation, qualification multi-maître, runbooks et sécurité | [`docs/fr/02-guides-pratiques/index.md`](docs/fr/02-guides-pratiques/index.md) |
| **3. Référence (`docs/fr/03-reference/`)** | Schémas, sommes SHA-256, cibles Makefile, variables, catalogues CLI/SQL et matrice RCA | [`docs/fr/03-reference/index.md`](docs/fr/03-reference/index.md) |
| **4. Explications (`docs/fr/04-explications/`)** | Architecture plateforme/ETL, ADR (`ADR-001`, `ADR-002`) et compromis verrouillage/réplication | [`docs/fr/04-explications/index.md`](docs/fr/04-explications/index.md) |
| **Gouvernance & Versions (EN)** | Historique des versions, journal d'actions et registre des causes racines | [`Changelog`](Changelog) · [`ACTION_LOGBOOK.md`](docs/ACTION_LOGBOOK.md) · [`RCA_REGISTER.md`](docs/RCA_REGISTER.md) |

---

## 📚 Documentation Technique

Une documentation détaillée pour chaque composant est disponible dans le répertoire `documentation/` :

| Sujet | Documentation (FR) | Documentation (EN) |
| :--- | :--- | :--- |
| **Documentation Technique** | [index.md](documentation/fr/index.md) | [index.md](documentation/en/index.md) |
| **Analyse SQL** | [sql_analyzer.md](documentation/fr/sql_analyzer.md) | [sql_analyzer.md](documentation/en/sql_analyzer.md) |
| **MariaDB/Docker** | [mariadb_management.md](documentation/fr/mariadb_management.md) | [mariadb_management.md](documentation/en/mariadb_management.md) |
| **Benchmarking** | [benchmarking.md](documentation/fr/benchmarking.md) | [benchmarking.md](documentation/en/benchmarking.md) |
| **Outils & Métriques** | [guide_outils.md](documentation/fr/guide_outils.md) | [tools_guide.md](documentation/en/tools_guide.md) |
| **Rapports Interactifs** | [interactive_reporting.md](documentation/fr/interactive_reporting.md) | [interactive_reporting.md](documentation/en/interactive_reporting.md) |
| **Plateforme PostgreSQL 3NF Sirene** | [sirene_platform.md](documentation/fr/sirene_platform.md) | [sirene_platform.md](documentation/en/sirene_platform.md) |
| **Référence Interactive Sirene (HTML)** | [sirene_documentation.html](documentation/sirene_documentation.html) | [sirene_documentation.html](documentation/sirene_documentation.html) |

---

## 🤖 Automatisation & Workflows

Pour les utilisateurs travaillant avec des agents IA ou cherchant une maintenance automatisée, nous proposons des workflows spécialisés dans `.agent/workflows/` :

- `/run-tests` : Batterie complète de tests avec synchronisation documentaire.
- `/git-sync` : Automatisation des commits conventionnels et synchronisation distante.
- `/release` : **Flux de release complet** : gestion du versionnement, du changelog et des tags annotés.
- `/audit` : Audit structurel et de performance de l'environnement.

---

## 📂 Carte du Dépôt

- `employees/` : Jeu de données, définitions de schémas et plus de 60 requêtes exemples.
- `sirene/` : Plateforme ETL PostgreSQL 18 3NF pour INSEE Sirene, jeu de données synthétique embarqué (`15 000` unités légales / `30 000` établissements sans PII) injectable directement en SQL (`make sirene-inject`, `make sirene-verify`) ou hors-ligne en Parquet/delta (`make sirene-import-sample`, `make sirene-incremental-sample`), stack Docker Compose et suite `pytest` ([sirene/README.md](sirene/README.md)).
- `scripts/` : Automatisation Python/Bash (analyseur SQL, Lua sysbench, runners).
- `reports/` : Destination des plans EXPLAIN, résultats QPS et tableaux de bord HTML.
- `documentation/` : Guides techniques bilingues.
- `doc_employees/` : Documentation étendue incluant les diagrammes ER.

---

## 🛠 Installation Manuelle (Hors Docker)

1. **Privilèges** : Assurez-vous que votre utilisateur dispose des droits `CREATE`, `DROP`, `RELOAD`, `INDEX`, `ALTER`, et `CREATE VIEW`.
2. **Importer les données** :

   ```bash
   mysql < employees/employees.sql
   ```

3. **Lancer la vérification** :

   ```bash
   mysql -t < employees/test_employees_md5.sql
   ```

---

## 📜 Crédits & Licence

### Origine

- **Création des données** : Fusheng Wang et Carlo Zaniolo (Siemens Corporate Research).
- **Schéma relationnel** : Giuseppe Maxia.
- **Export des données** : Patrick Crews.

### Licence

Ce travail est sous licence **Creative Commons Attribution-Share Alike 3.0 Unported License**.

---
*Note : Ces données sont fictives et ne correspondent pas à des personnes réelles. Toute ressemblance est purement fortuite.*
