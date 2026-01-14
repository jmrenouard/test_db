# Script d'Analyse SQL

Le script `sql_analyzer.py` est un outil puissant pour analyser les performances et la qualité des requêtes SQL.

## Fonctionnalités

- **Analyse EXPLAIN Automatisée** : Exécute automatiquement `EXPLAIN` sur les requêtes fournies.
- **Évaluation de Performance** : Attribue une note de 1 à 5 étoiles selon l'efficacité.
- **Suggestions d'Optimisation** : Fournit des conseils ciblés pour améliorer les requêtes lentes.
- **Recommandations d'Index** : Détecte les index manquants et génère le DDL `CREATE INDEX` correspondant.
- **Contexte de Schéma** : Affiche la structure des tables impliquées et les index existants.
- **Rapports HTML de Qualité** : Génère un tableau de bord analytique moderne basé sur Tailwind CSS.

## Utilisation

### Analyser un Fichier

```bash
python3 scripts/sql_analyzer.py --container mariadb-11-8 --query-file employees/req_employees.sql
```

### Analyser une Requête Unique

```bash
python3 scripts/sql_analyzer.py --container mariadb-11-8 --query "SELECT * FROM employees WHERE emp_no = 10001" --stdout
```

## Paramètres

| Paramètre | Défaut | Description |
| :--- | :--- | :--- |
| `--container` | Aucun | Nom du conteneur Docker MariaDB. |
| `--query-file` | `employees/req_employees.sql` | Chemin vers le fichier SQL contenant les requêtes. |
| `--query` | Aucun | Une chaîne de requête SQL unique à analyser. |
| `--db` | `employees` | Le nom de la base de données cible. |
| `--stdout` | Faux | Affiche les résultats directement dans le terminal. |
| `--html-file` | `reports/performance_report.html` | Chemin pour le tableau de bord HTML généré. |
| `[Autres params DB]` | - | `--host`, `--port`, `--user`, `--password` pour les connexions hors Docker. |
