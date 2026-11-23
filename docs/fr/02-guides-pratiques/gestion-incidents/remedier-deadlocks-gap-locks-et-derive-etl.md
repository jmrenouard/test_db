# Remédier aux deadlocks, gap locks et dérives ETL

Consultez la [Matrice des erreurs et alertes](../../03-reference/codes-erreurs/matrice-erreurs-et-alertes.md) avant de lancer ce runbook.

## Prérequis

1. Disposez d'un accès terminal vers l'hôte Docker de `mariadb-11-8` et `sirene-postgres`.
2. Relevez la cible `make` en échec, les journaux du conteneur ou le message d'erreur `etl_logs`.
3. Vérifiez l'accès aux clients `psql` ou `mariadb` dans le conteneur concerné.

## Consignes de sécurité

**ATTENTION :** N'envoyez jamais `SIGKILL` à `sirene-postgres` pendant un import ou une reconstruction d'index.
Un arrêt brutal laisse des tables temporaires partielles ou des relations sans index.

**ATTENTION :** Ne dirigez jamais des écritures concurrentes pour un même SIRET sur deux nœuds `origin=none`.
Les mises à jour simultanées causent une divergence silencieuse sur `etablissements`.

## Étapes

1. Si les deadlocks MariaDB augmentent, activez la trace complète et lisez les journaux :

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -e "SET GLOBAL innodb_print_all_deadlocks = 1;"
   docker logs --tail 100 mariadb-11-8
   ```

2. Si les transactions InnoDB bloquent sous `REPEATABLE READ`, examinez les attentes actives :

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -e "SHOW ENGINE INNODB STATUS\G"
   ```

3. Réduisez la durée des verrous SQL ou exécutez `teardown.sql` sur les tables de simulation bloquées.
4. Si PostgreSQL échoue sur le port hôte `5432`, définissez `POSTGRES_HOST_PORT=15432` dans `sirene/.env`.
5. Si `postgres:18-bookworm` échoue au démarrage, montez le volume Compose sur `/var/lib/postgresql`.
6. Si un autre ETL détient le verrou `84729101`, listez les sessions actives :

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT pid, state, query FROM pg_stat_activity WHERE datname = 'sirene';"
   ```

7. Attendez la fin des traitements légitimes, ou arrêtez uniquement les PID orphelins confirmés.
8. Si `incremental_import.py` n'enregistre aucune ligne, vérifiez que `conn.commit()` précède `with conn.transaction():`.
9. Si `drop_secondary_indexes` bloque sur `AccessShareLock`, validez les lectures inactives ou activez `autocommit=True`.
10. Si une requête `pg_trgm` paramétrée échoue sur `incomplete placeholder`, échappez `%` en `%%`.
11. Si des CSV INSEE échouent sur des espaces finaux ou `[ND]`, vérifiez `sirene_etl.transforms`.
12. Si `P3` signale une divergence split-brain, arrêtez le second nœud et gardez un primaire unique.

**NOTE :** `sirene/src/sirene_etl/db.py` acquiert le verrou consultatif `84729101` par session ETL.
PostgreSQL libère automatiquement ce verrou lorsque la session se ferme.

## Vérification

1. Exécutez `make verify` et confirmez le code retour `0` sur `mariadb-11-8`.
2. Examinez `etl_logs` dans `sirene-postgres` et confirmez `status = 'SUCCESS'` :

   ```bash
   docker compose -f sirene/docker-compose.yml exec -T sirene-postgres \
     psql -U sirene -d sirene -c "SELECT id, run_type, status, error_message FROM etl_logs ORDER BY id DESC LIMIT 5;"
   ```

3. Vérifiez que `pg_locks` n'affiche aucun verrou `AccessShareLock` ou `AccessExclusiveLock` en attente.

## Retour arrière

Si la remédiation crée une nouvelle contention ou un échec ETL, exécutez ces actions :

1. Arrêtez le démon `sirene-watcher` avec `make sirene-down`.
2. Arrêtez les benchmarks actifs et nettoyez les rapports avec `make clean`.
3. Redémarrez `sirene-postgres` seul avec `make sirene-up` et réappliquez `sirene/sql/02_indexes.sql`.
4. Rechargez les jeux synthétiques avec `make sirene-inject` ou `make inject` avant tout nouveau test.

## Documentation associée

- Référence : [Matrice des erreurs et alertes](../../03-reference/codes-erreurs/matrice-erreurs-et-alertes.md)
- Référence : [Catalogue des scripts CLI et SQL](../../03-reference/cli-et-scripts/catalogue-scripts-cli-et-sql.md)
- Explications :
  [Compromis concurrence, verrouillage et réplication](../../04-explications/analyses-internes/compromis-concurrence-verrous-et-replication.md)
- Explications : [Architecture plateforme et ETL](../../04-explications/vue-architecture/architecture-plateforme-et-etl.md)
