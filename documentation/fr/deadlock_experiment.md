# Expérience sur les Deadlocks dans MariaDB

Cette expérience démontre comment `db_simulator.py` peut détecter et analyser les deadlocks (verrous mortels) en surveillant le journal d'erreurs (error log) de MariaDB.

## Configuration de l'Expérience

- **Tables** : `deadlock_test` (2 lignes).
- **Modèle de Contention** :
  - **Thread 1** : Met à jour la ligne 1, attend (sleep), puis tente de mettre à jour la ligne 2.
  - **Thread 2** : Met à jour la ligne 2, attend (sleep), puis tente de mettre à jour la ligne 1.
  - Cela crée une dépendance circulaire (cycle dans le graphe d'attente), déclenchant un deadlock.

## Détection Automatisée

L'outil `db_simulator.py` automatise la détection de ces événements en :

1. Analysant les journaux du conteneur Docker pour les signatures `TRANSACTION DEADLOCK`.
2. Corrélant l'horodatage de l'événement avec le temps de la simulation.
3. Extrayant les requêtes SQL exactes impliquées dans le conflit à partir du journal d'erreurs MariaDB.

## Actifs Techniques

### 1. Configuration MariaDB

Activation de la journalisation détaillée des deadlocks :

```sql
SET GLOBAL innodb_print_all_deadlocks = 1;
```

### 2. Exécution Sysbench

Commande orchestrée par `db_simulator.py` :

```bash
sysbench scripts/dir_transactions_sysbench.lua \
  --mysql-host=127.0.0.1 \
  --mysql-user=root \
  --mysql-password= \
  --mysql-db=employees \
  --sql-dir=/tmp/bench_dir/sql/ \
  --threads=8 \
  --time=10 \
  run
```

### 3. Logique des Transactions (SQL)

Conçues pour entrer en collision :

- **Transaction A** : `UPDATE id=1; SLEEP; UPDATE id=2;`
- **Transaction B** : `UPDATE id=2; SLEEP; UPDATE id=1;`

### 4. Automatisation Lua

Le script [dir_transactions_sysbench.lua](file:///home/jmren/GIT_REPOS/test_db/scripts/dir_transactions_sysbench.lua) sélectionne aléatoirement ces fichiers SQL et les exécute via `db_query()`, enveloppé dans un `pcall` pour garantir que la simulation continue après l'annulation d'un deadlock.

## Résultats Observés

...

Exécution de la simulation avec 8 threads pendant 10 secondes :

- **Deadlocks Détectés** : 30
- **Latence de Pic** : Augmentation significative due aux annulations et ré-exécutions.

Le rapport HTML met désormais visuellement en évidence ces événements, fournissant les requêtes exactes des transactions impliquées dans le conflit.

## Comment Reproduire

1. Configurer l'environnement :

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root employees < tests/data/deadlock/setup.sql
   ```

2. Lancer la simulation :

   ```bash
   python3 scripts/db_simulator.py --sql-dir tests/data/deadlock/ --container mariadb-11-8 --threads 8 --time 10
   ```
