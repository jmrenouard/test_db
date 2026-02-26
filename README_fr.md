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
