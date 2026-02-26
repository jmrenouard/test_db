[🏠 Accueil](index.md) | [⬅️ Précédent](deadlock_experiment.md) | [➡️ Suivant](index.md)
***

# Expérience sur le Gap Locking dans MariaDB

Cette expérience démontre pourquoi la création de verrous sur des plages d'index (Gap Locking) dans InnoDB peut provoquer une dégradation des performances et des blocages d'insertion, en particulier lorsque des clés étrangères sont impliquées.

## Configuration de l'Expérience

- **Tables** : `gap_parent` (clés PK éparses : 10, 20, 30) et `gap_child` (FK vers parent).
- **Contention** :
    1. **Transaction de Verrouillage** : `SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE`. Cela crée un verrou de type "Gap Lock" sur l'espace compris entre les ID 10 et 20.
    2. **Transaction Conflictuelle** : `INSERT INTO gap_parent (id, name) VALUES (15, 'Intruder')`. Cette tentative d'insertion dans le "gap" ATTENDRA la validation (commit) ou l'annulation (rollback) de la première transaction.

## Scénarios Complexes : Variante 4

Dans le scénario `gap_locking_4`, nous explorons une interaction plus subtile impliquant les **Contraintes d'Unicité et les Clés Étrangères**.

- **Configuration** : Une table avec une colonne à clé unique non primaire référencée par une table enfant.
- **Interférence DML** : Lorsqu'une transaction effectue un `DELETE` ou un `UPDATE` sur la colonne unique, InnoDB place des verrous sur les intervalles environnants (gaps) pour garantir la cohérence de l'unicité.
- **Observation** : Des insertions concomitantes dans la même table enfant ou sur des clés parent liées peuvent déclencher des verrous mortels (deadlocks) ou de longues attentes, même si les clés primaires ne se chevauchent pas.

## Actifs Techniques

### 1. Configuration MariaDB

Configuration utilisée dans le conteneur standard MariaDB 11.8 (paramètres par défaut). Notez que le Gap Locking est activé par défaut dans le niveau d'isolation `REPEATABLE READ` (le mode par défaut de MariaDB).

### 2. Exécution Sysbench

Commande orchestrée par `db_simulator.py` :

```bash
sysbench scripts/dir_transactions_sysbench.lua \
  --mysql-host=127.0.0.1 \
  --mysql-user=root \
  --mysql-password= \
  --mysql-db=employees \
  --sql-dir=/tmp/bench_dir/sql/ \
  --threads=4 \
  --time=20 \
  run
```

### 3. Logique des Transactions (SQL)

- **Sélection/Verrouillage** : `SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE;`
- **Insertion (Gap)** : `INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'Intruder');`
- **Insertion (Enfant)** : `INSERT IGNORE INTO gap_child (id, parent_id, description) VALUES (100, 20, 'Child');`

### 4. Script Lua

Le script [dir_transactions_sysbench.lua](file:///home/jmren/GIT_REPOS/test_db/scripts/dir_transactions_sysbench.lua) est utilisé pour charger et exécuter ces requêtes SQL en parallèle, exposant ainsi la contention sur les intervalles d'index.

## Résultats Observés

...

Utilisation de `db_simulator.py` avec 4 threads concurrents :

| Métrique | Résultats |
| :--- | :--- |
| **TPS** | ~60 |
| **Latence Moyenne** | ~64 ms |
| **Latence 95ème** | ~180 ms |

**Conclusion** : L'écart significatif entre la latence moyenne et le 95ème percentile confirme que les transactions attendaient fréquemment la libération des verrous. Le gap lock a réussi à empêcher les insertions entre les clés existantes, garantissant une stabilité absolue de la plage pendant la durée de la transaction `FOR UPDATE`.

## Comment Reproduire

1. Injecter l'environnement :

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root employees < tests/data/gap_locking/setup.sql
   ```

2. Lancer la simulation :

   ```bash
   # Verrou d'intervalle standard
   python3 scripts/db_simulator.py --sql-dir tests/data/gap_locking/ --container mariadb-11-8 --threads 4 --time 20
   
   # Variante 4 : Contentions sur clés étrangères uniques
   python3 scripts/db_simulator.py --sql-dir tests/data/gap_locking_4/ --container mariadb-11-8 --threads 4 --time 20
   ```

***
[🏠 Accueil](index.md) | [⬅️ Précédent](deadlock_experiment.md) | [➡️ Suivant](index.md)
