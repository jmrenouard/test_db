# Variables d'environnement, paramètres moteur et cibles Makefile

Spécification complète des cibles `Makefile`, variables d'environnement MariaDB/PostgreSQL et paramètres MkDocs.

## 1. Cibles `Makefile`

### 1.1 Cibles MariaDB et `employees`

| Cible | Commande exécutée | Surcharges | Rôle |
| :--- | :--- | :--- | :--- |
| `start` / `stop` / `status` | `docker start/stop/ps $(CONTAINER_NAME)` | `CONTAINER_NAME` | Cycle de vie du conteneur MariaDB `11.8` |
| `inject` | `docker cp employees/. ... && mariadb < employees.sql` | `CONTAINER_NAME` | Injection du jeu `employees` canonique |
| `inject-fake` | `python3 scripts/inject_fake_employees.py --count $(COUNT)` | `COUNT` (`10`) | Injection synthétique Faker ou repli intégré |
| `verify` | `bash scripts/test_runner.sh verify` | `USE_CONTAINER`, `DB_*` | Vérification comptages et `CHECKSUM TABLE` |
| `bench` / `perf-threads` | `bash scripts/test_runner.sh bench \| perf-threads` | `USE_CONTAINER`, `DB_*` | Benchmark mono-thread ou montée `1` à `64` threads |
| `analyze` | `bash scripts/test_runner.sh analyze` | `USE_CONTAINER`, `DB_*` | Analyse `EXPLAIN` et recommandations d'index |
| `oltp` | `bash scripts/test_runner.sh std-oltp $(TYPE) $(ACTION)` | `TYPE`, `ACTION`, `THREADS`, `TABLES`, `SIZE`, `TIME` | Charge OLTP Sysbench standard |
| `test-data` / `test-all` | `bash scripts/test_runner.sh data-tests \| all` | `TEST` | Tests de contention (`deadlock`, `gap_locking*`) |
| `interactive` / `clean` | `python3 interactive_runner.py` / `rm -rf reports/...` | `USE_CONTAINER` | Menu interactif HTML ou nettoyage `reports/` |

### 1.2 Cibles Sirene PostgreSQL 18 3NF et multi-maître

| Cible | Rôle |
| :--- | :--- |
| `sirene-up` / `sirene-down` | Démarre `sirene-postgres` (`127.0.0.1:15432`) ou arrête la pile Compose |
| `sirene-test` | Construit `sirene-etl` et lance la suite `pytest -v` dans Docker |
| `sirene-import` / `sirene-incremental` | Import complet initial ou synchronisation incrémentale delta |
| `sirene-watch` | Démarre le daemon de surveillance sous profil `daemon` |
| `sirene-mm-up` / `sirene-mm-probe` / `sirene-mm-down` | Lab 2 nœuds (`15441`/`15442`) et sondes `P1` à `P5` |
| `sirene-inject` / `sirene-verify` | Injection SQL directe (`15k` UL / `30k` SIRET) et contrôle SHA-256 |
| `sirene-import-sample` / `sirene-incremental-sample` | Pipelines Parquet et delta synthétiques hors ligne |

### 1.3 Cibles documentation MkDocs Material

| Cible | Commande | Résultat |
| :--- | :--- | :--- |
| `docs-check` | `$(PYTHON) -m pytest tests/test_diataxis_documentation.py tests/test_mkdocs_publishing.py tests/test_tutorials_and_howtos.py -v` | Valide Diátaxis EN/FR, STE/STF, liens et scripts |
| `docs-build` | `mkdocs build --strict -d site` puis `-f mkdocs.fr.yml --strict -d site/fr` | Génère `site/` (EN) et `site/fr/` (FR) |
| `docs-build-versioned` | `$(PYTHON) scripts/build_versioned_docs.py` | Génère `site_dist/` multi-versions EN et FR |
| `docs-serve` | `$(PYTHON) -m mkdocs serve` | Serveur de prévisualisation local |

---

## 2. Variables d'environnement principales

| Variable | Défaut | Composant | Rôle |
| :--- | :--- | :--- | :--- |
| `CONTAINER_NAME` | `mariadb-11-8` | `Makefile`, `scripts/*.sh` | Nom du conteneur MariaDB cible |
| `USE_CONTAINER` | `true` | `scripts/*.sh`, Python | Active Docker (`0`/`false` force le client local) |
| `POSTGRES_HOST_PORT` | `15432` | `sirene/docker-compose.yml` | Port loopback hôte vers PostgreSQL 18 |
| `MM_NODE_A_PORT` / `MM_NODE_B_PORT` | `15441` / `15442` | `docker-compose.pg18-birep.yml` | Ports loopback des 2 nœuds multi-maître |
| `BATCH_SIZE` | `50000` | `sirene_etl.config` | Taille des lots `COPY FROM STDIN` |
| `TEST_DB_DOCS_REF` | `master` | `scripts/mkdocs_hooks.py` | Référence Git pour réécriture des liens |
| `TEST_DB_DOCS_SITE_URL` | `https://test-db.lightpath.fr` | `build_versioned_docs.py` | URL de base des sites EN/FR |

## Documentation associée

- [ADR-002 : Architecture Diátaxis et publication MkDocs](../../04-explications/decisions-architecture/adr-002-diataxis-et-publication-mkdocs-versionnee.md)
- [Déployer les piles MariaDB et PostgreSQL](../../02-guides-pratiques/deploiement/deployer-piles-mariadb-et-postgresql.md)
- [Catalogue des scripts CLI et SQL](../cli-et-scripts/catalogue-scripts-cli-et-sql.md)
