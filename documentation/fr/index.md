# Index de Documentation

Bienvenue dans la documentation technique de `test_db`. Cette documentation couvre l'architecture, les outils et les pratiques de benchmarking de l'environnement de test MariaDB.

Veuillez suivre les guides dans l'ordre, ou accéder directement à un sujet d'intérêt :

## 1. Environnement et Outils

1. [Gestion MariaDB](mariadb_management.md) - Cycle de vie du conteneur, configuration de l'environnement et injection de données.
2. [Guide des Outils](guide_outils.md) - Aperçu de Sysbench, des analyseurs Python et de l'architecture générale de test.
3. [Rapports Interactifs & Dashboards](interactive_reporting.md) - Utilisation de `make interactive` et affichage des rapports HTML/Tailwind CSS.

## 2. Performances & Analyse

1. [Benchmarking & Sysbench](benchmarking.md) - Plongée approfondie dans le benchmarking évolutif et glossaire des métriques.
2. [Analyseur SQL](sql_analyzer.md) - Utilisation de l'analyseur de requêtes SQL assisté par l'IA et génération d'index manquants.

## 3. Expériences de Concurrence

1. [Expérience Deadlock](deadlock_experiment.md) - Simulation et suivi des interblocages "wait-for-graph".
2. [Expérience Gap Locking](gap_locking_experiment.md) - Démonstration des "gap locks" InnoDB sur des index non uniques.

---
*Retour au [README](../../README_fr.md) Principal*
