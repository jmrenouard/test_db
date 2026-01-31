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

## Environnement d'Exécution

La suite de performance supporte à la fois les modes d'exécution basés sur Docker et les modes locaux.

### 1. Changement de Mode (`USE_CONTAINER`)

Par défaut, le système détecte si le conteneur MariaDB est en cours d'exécution et l'utilise. Vous pouvez forcer le mode d'exécution à l'aide de la variable d'environnement `USE_CONTAINER` :

- **Forcer Docker** : (Par défaut si le conteneur existe)
- **Forcer le mode Local** : `export USE_CONTAINER=0`
  - Dans ce mode, les scripts tenteront de se connecter à une instance MariaDB locale et utiliseront les binaires `sysbench` locaux.

### 2. Paramètres de Connexion

Tous les scripts respectent les variables d'environnement standard pour la connectivité à la base de données :

- `DB_USER` (Défaut : root)
- `DB_PASS` (Défaut : vide)
- `DB_NAME` (Défaut : employees)
- `DB_HOST` (Défaut : 127.0.0.1)

## Scripts Sysbench Standard

En plus des tests SQL basés sur des répertoires, vous pouvez désormais exécuter des scripts sysbench standard (par exemple, à partir de `/usr/share/sysbench/`) :

### Utilisation de `db_simulator.py`

```bash
python3 scripts/db_simulator.py --script /usr/share/sysbench/oltp_read_only.lua --name "Test OLTP"
```

### Utilisation de `run_dir_bench.sh`

```bash
bash scripts/run_dir_bench.sh --script /usr/share/sysbench/oltp_read_only.lua --threads 8
```

### Paramètres OLTP Avancés

Vous pouvez contrôler l'échelle des tests OLTP standard en utilisant les variables `THREADS`, `TABLES`, `SIZE`, et `TIME` (durée en secondes) :

```bash
make oltp TYPE=read_write ACTION=prepare TABLES=10 SIZE=100000
make oltp TYPE=read_write THREADS=16 TIME=120
```

### Rapports Précis

Les tests OLTP standard génèrent automatiquement des rapports HTML dans des dossiers dédiés et précis :

- **Format du dossier** : `reports/oltp_{TYPE}_{THREADS}t_{TIME}s/`
- **Métadonnées** : Les rapports affichent le script utilisé, le nombre de threads et la durée.

## Métriques Capturées et Glossaire

La suite de simulation capture et analyse diverses métriques provenant de `sysbench`. Voici un glossaire expliquant chaque paramètre et son unité.

### 1. Métriques de Débit

- **TPS (Transactions par Seconde)** : Le nombre de transactions réussies exécutées par seconde. Une transaction est une unité logique de travail (ex: un script OLTP de lecture/écriture).
- **QPS (Requêtes par Seconde)** : Le nombre total de requêtes SQL (SELECT, INSERT, UPDATE, etc.) exécutées par seconde. Cela comptabilise les opérations SQL individuelles.

### 2. Métriques de Latence (Mesurées en Millisecondes, ms)

- **Latence Min** : Le temps d'exécution le plus court enregistré pour un événement/transaction.
- **Latence Moyenne** : La moyenne arithmétique des temps d'exécution de tous les événements.
- **Latence Max** : Le temps d'exécution le plus long enregistré pour un événement/transaction.
- **95ème Percentile** : Une métrique clé indiquant que 95 % de tous les événements ont été complétés dans ce laps de temps ou moins. Il représente la performance dans "le pire des cas" pour la grande majorité des utilisateurs.
- **Somme des Latences** : Le temps d'exécution cumulé de tous les événements à travers tous les threads.

### 3. Opérations de Base de Données (Comptages)

- **Lecture** : Nombre total de requêtes de lecture (ex: SELECT).
- **Écriture** : Nombre total de requêtes d'écriture (ex: INSERT, UPDATE, DELETE).
- **Autre** : Nombre total de requêtes administratives (ex: COMMIT, BEGIN, etc.).
- **Total des Événements** : Le nombre total de transactions ou d'itérations de script effectuées pendant le test.

### 4. Statistiques d'Équité des Threads

Métriques utilisées pour déterminer si le travail a été réparti uniformément sur tous les threads.

- **Événements (Moyenne/Écart-type)** :
  - **Moyenne** : Nombre moyen d'événements gérés par thread.
  - **Écart-type (Stddev)** : Mesure la variation par rapport à la moyenne. Une valeur faible indique une répartition uniforme ; une valeur élevée suggère des threads "bruyants" ou une contention.
- **Temps d'Exécution (Moyenne/Écart-type)** :
  - **Moyenne** : Temps total moyen passé par chaque thread.
  - **Écart-type** : La variation du temps d'exécution total entre les threads. Un écart-type élevé indique que certains threads ont été bloqués plus longtemps que d'autres.

---

## Métadonnées d'Infrastructure

Capture le contexte de l'environnement pour la reproductibilité :

- **OS** : Version du système d'exploitation et noyau (ex: Linux 6.5.0-26-generic).
- **Cœurs CPU** : Nombre total de processeurs logiques détectés.
- **RAM Totale** : Quantité de mémoire système (MB).
- **Version DB** : Version complète de MariaDB (ex: 11.8.1-MariaDB).
- **Concurrence/Threads** : Le nombre d'ouvriers parallèles utilisés pour le test.
- **Durée** : Le temps total d'exécution en secondes.

---

## Détection des Deadlocks

Identifie automatiquement les verrous mortels MariaDB et les met en évidence dans les rapports.

## Rapports de Sortie

Les résultats sont sauvegardés dans :

- `reports/perf_threads/results_{N}_threads.txt`
- `reports/simulator_report.md` / `reports/simulator_report.html` (lors de l'utilisation de `db_simulator.py`)
- **Tableau de Bord Interactif** : Rapports HTML modernes avec graphiques en barres CSS et transparence des commandes.
- Résumé affiché dans la console du terminal.
