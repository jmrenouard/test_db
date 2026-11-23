# Déployer les piles MariaDB et PostgreSQL

Consultez les [Variables d'environnement et cibles Makefile](../../03-reference/configuration/variables-environnement-et-cibles-makefile.md) avant de modifier un fichier `.env`.

## Prérequis

1. Installez Docker Engine, Docker Compose v2, `make` et `bash` sur le poste cible.
2. Vérifiez que le conteneur `mariadb-11-8` existe sur l'hôte Docker.
3. Vérifiez que les ports TCP `3306` et `15432` sont libres sur `127.0.0.1`.

## Consignes de sécurité

**ATTENTION :** Copiez les fichiers `.env` uniquement en local et excluez-les de Git.
Un fichier d'environnement suivi expose les mots de passe locaux.

**ATTENTION :** Montez le volume PostgreSQL 18 sur `/var/lib/postgresql` et jamais sur `/var/lib/postgresql/data`.
Un ancien chemin de montage bloque le démarrage du conteneur `postgres:18-bookworm`.

## Étapes

1. Copiez le modèle d'environnement pour la pile Sirene PostgreSQL 18 :

   ```bash
   cp sirene/.env.example sirene/.env
   ```

2. Modifiez `sirene/.env` si vous personnalisez `POSTGRES_PASSWORD`, `POSTGRES_HOST_PORT` ou `BATCH_SIZE`.
3. Démarrez le conteneur MariaDB 11.8 et vérifiez son état :

   ```bash
   make start
   make status
   ```

4. Injectez le jeu canonique `employees` dans `mariadb-11-8` :

   ```bash
   make inject
   ```

5. Démarrez le service Sirene PostgreSQL 18 sur `127.0.0.1:15432` :

   ```bash
   make sirene-up
   ```

6. Construisez l'image `sirene-etl` et lancez la suite `pytest` Docker :

   ```bash
   make sirene-test
   ```

7. Chargez le jeu synthétique Sirene hors ligne avec `psql` :

   ```bash
   make sirene-inject
   ```

8. Si vous activez la surveillance automatique, démarrez le service `sirene-watcher` :

   ```bash
   make sirene-watch
   ```

**NOTE :** `sirene/docker-compose.yml` isole `sirene-watcher` sous le profil `daemon`.
`make sirene-up` ne lance aucun polling réseau en arrière-plan.

## Vérification

1. Vérifiez que les deux conteneurs de base affichent un état sain :

   ```bash
   make status
   docker compose -f sirene/docker-compose.yml ps
   ```

2. Exécutez `make verify` et confirmez le code retour `0` pour les six tables `employees`.
3. Exécutez `make sirene-verify` et confirmez `CRC | OK` et `count | OK` sur douze tables.

## Retour arrière

Si le déploiement échoue ou endommage les données locales, exécutez ces actions :

1. Arrêtez la pile Sirene avec cette commande :

   ```bash
   make sirene-down
   ```

2. Si vous réinitialisez le volume `sirene_pgdata`, supprimez les volumes Compose :

   ```bash
   docker compose -f sirene/docker-compose.yml --profile daemon down -v
   ```

3. Arrêtez le conteneur MariaDB :

   ```bash
   make stop
   ```

4. Exécutez `make start` puis `make inject` pour restaurer un schéma `employees` propre.

## Documentation associée

- Référence : [Variables d'environnement et cibles Makefile](../../03-reference/configuration/variables-environnement-et-cibles-makefile.md)
- Référence : [Matrice des erreurs et alertes](../../03-reference/codes-erreurs/matrice-erreurs-et-alertes.md)
- Explications : [Architecture plateforme et ETL](../../04-explications/vue-architecture/architecture-plateforme-et-etl.md)
- Explications :
  [ADR-001 : ETL Sirene PostgreSQL 18 3NF et qualification MM](../../04-explications/decisions-architecture/adr-001-postgresql18-3nf-sirene-etl-et-qualification-mm.md)
