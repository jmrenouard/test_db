# Tests de Performance avec Sysbench

Le projet inclut des tests de performance automatisés pour la simulation de haute concurrence et les tests de charge en utilisant `sysbench`.

## Présentation du Benchmark

La suite de tests utilise un script Lua personnalisé (`scripts/employees_sysbench.lua`) pour exécuter des requêtes SQL réelles à partir de votre jeu de données.

### Cibles Disponibles

- **Benchmark Standard** : `make bench`  
  Exécute le jeu de requêtes de manière séquentielle, en répétant l'ensemble 10 fois pour mesurer le débit moyen.
- **Échelonnage des Threads** : `make perf-threads`  
  Lance un test de scalabilité sur 1, 2, 4, 8, 16, 32 et 64 threads pendant 60 secondes chacun.
- **Transactions basées sur un Répertoire**: `scripts/run_dir_bench.sh`  
  Exécute des fichiers SQL à partir d'un répertoire spécifié en parallèle. Chaque fichier est traité comme un bloc de transaction unique.

## Métriques Capturées

- **QPS (Requêtes par Seconde)** : Mesure le débit brut de la base de données.
- **Latence** : Temps de réponse moyen en millisecondes.
- **Échelonnage des Threads** : Aide à identifier le point de saturation où l'ajout de threads supplémentaires n'améliore plus les performances.

## Rapports de Sortie

Les résultats sont sauvegardés dans :

- `reports/perf_threads/results_{N}_threads.txt`
- `reports/simulator_report.md` / `reports/simulator_report.html` (lors de l'utilisation de `db_simulator.py`)
- Résumé affiché dans la console du terminal.
