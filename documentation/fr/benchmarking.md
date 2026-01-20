# Tests de Performance avec Sysbench

Le projet inclut des tests de performance automatisés pour la simulation de haute concurrence et les tests de charge en utilisant `sysbench`.

## Présentation du Benchmark

La suite de tests utilise un script Lua personnalisé (`scripts/employees_sysbench.lua`) pour exécuter des requêtes SQL réelles à partir de votre jeu de données.

### Cibles Disponibles

- **Benchmark Standard** : `make bench`  
  Exécute le jeu de requêtes de manière séquentielle, en répétant l'ensemble 10 fois pour mesurer le débit moyen.
- **Échelonnage des Threads** : `make perf-threads`  
  Lance un test de scalabilité sur 1, 2, 4, 8, 16, 32 et 64 threads pendant 60 secondes chacun.
- **Transactions basées sur un Répertoire**: `make test-data`  
  Exécute tous les fichiers SQL de chaque sous-répertoire de `tests/data/` en parallèle.
  - Tout exécuter : `make test-data`
  - Un test spécifique : `make test-data TEST=deadlock`
- **Exécuteur Manuel**: `scripts/run_dir_bench.sh`  
  Lanceur CLI direct pour des répertoires SQL personnalisés.

## Métriques Capturées

- **QPS (Requêtes par Seconde)** : Mesure le débit brut de la base de données.
- **Latence** : Temps de réponse moyen en millisecondes (inclut l'analyse du 95ème percentile).
- **Échelonnage des Threads** : Aide à identifier le point de saturation où l'ajout de threads supplémentaires n'améliore plus les performances.
- **Métadonnées d'Infrastructure** : Capture le système d'exploitation, l'architecture processeur, la RAM et le nom d'hôte pour une reproductibilité totale.
- **Détection des Deadlocks** : Identifie automatiquement les verrous mortels MariaDB et les met en évidence dans les rapports.

## Rapports de Sortie

Les résultats sont sauvegardés dans :

- `reports/perf_threads/results_{N}_threads.txt`
- `reports/simulator_report.md` / `reports/simulator_report.html` (lors de l'utilisation de `db_simulator.py`)
- **Tableau de Bord Interactif** : Rapports HTML modernes avec graphiques en barres CSS et transparence des commandes.
- Résumé affiché dans la console du terminal.
