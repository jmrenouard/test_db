# 📊 test_db (Base de données Employees)

Une base de données exemple avec une suite de tests intégrée, utilisée pour tester vos applications et serveurs de bases de données. Ce dépôt fournit un ensemble de données conséquent (300 000 employés, 2,8M de salaires) pour les tests de performance et la pratique de requêtes complexes.

---

## 🚀 Démarrage Rapide (Méthode Moderne)

Ce projet est optimisé pour un environnement Docker **MariaDB 11.8+**. Un `Makefile` est fourni pour simplifier les opérations courantes.

### Prérequis

- Docker & Docker Compose
- Make
- Python 3 (pour les rapports)

### Commandes

| Commande | Description |
| :--- | :--- |
| `make start` | Démarre le conteneur MariaDB (`mariadb-11-8`). |
| `make stop` | Arrête le conteneur MariaDB. |
| `make status` | Vérifie le statut du conteneur. |
| `make inject` | Injecte le jeu de données `employees.sql`. |
| `make verify` | Exécute les tests d'intégrité des données (comptages/checksums). |
| `make bench` | Lance les tests de performance Sysbench. |
| `make analyze` | Génère les rapports EXPLAIN et de performance SQL. |
| `make test-all` | Exécute tous les tests (Verify + Analyze + Bench). |
| `make interactive` | Lance le gestionnaire de tests HTML <www.lightpath.fr>. |
| `make clean` | Nettoie les rapports générés. |

### 🤖 Workflows Agentiques

Ce projet inclut des workflows spécialisés dans `.agent/workflows/` pour une gestion facilitée :

- `/run-tests` : Exécute la suite complète de tests et synchronise la documentation.
- `/git-sync` : Gère le `pull`, le `commit` (conventionnel) et optionnellement la `release`.
- `/release` : Automatise le versionnement, la mise à jour du changelog et le tagage.
- `/maintain` : Réalise des tests de santé de l'environnement et du nettoyage.
- `/doc-sync` : Synchronise la documentation avec les changements de code.

---

## 📂 Structure du Projet

- `employees/` : Jeu de données principal et scripts SQL.
- `sakila/` : Exemple de base de données Sakila (Alternative).
- `scripts/` : Scripts utilitaires pour l'automatisation et les rapports.
- `reports/` : Plans EXPLAIN et analyses de performance générés.
- `documentation/` : Documentation technique détaillée (FR/EN).
- `doc_employees/` : Documentation étendue avec plus de 60 requêtes exemples et diagrammes ER.

---

## 🛠 Installation Manuelle

Si vous n'utilisez pas Docker, vous pouvez l'installer manuellement sur n'importe quel serveur compatible MySQL :

1. **Prérequis** : Assurez-vous que votre utilisateur possède les privilèges nécessaires (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `RELOAD`, `REFERENCES`, `INDEX`, `ALTER`, `SHOW DATABASES`, `CREATE TEMPORARY TABLES`, `LOCK TABLES`, `EXECUTE`, `CREATE VIEW`).
2. **Importation** :

   ```bash
   mysql < employees.sql
   ```

3. **Vérification** :

   ```bash
   mysql -t < test_employees_md5.sql
   ```

---

## 📊 Rapports & Analyses

Le projet inclut un système de reporting sophistiqué :

- **Analyse SQL** : Le script `sql_analyzer.py` génère des rapports de performance détaillés.
- **Tableaux de bord HTML** : Des tableaux de bord modernes basés sur Tailwind CSS sont disponibles dans `reports/`.
- **Plans EXPLAIN** : Les plans d'exécution détaillés sont stockés dans `reports/explain_reports/`.

---

## 📜 Crédits & Licence

### Origine

- Données créées par Fusheng Wang et Carlo Zaniolo chez Siemens Corporate Research.
- Schéma relationnel par Giuseppe Maxia.
- Export des données par Patrick Crews.

### Licence

Ce travail est sous licence **Creative Commons Attribution-Share Alike 3.0 Unported License**.

---
*Note : Ces données sont fictives et ne correspondent pas à des personnes réelles. Toute ressemblance est purement fortuite.*
