# Vérifier les sommes de contrôle et la confidentialité

Consultez la [Matrice des jeux de données et schémas](../../03-reference/architecture-specs/matrice-jeux-donnees-et-schemas.md).
Consultez aussi la [Matrice des erreurs et alertes](../../03-reference/codes-erreurs/matrice-erreurs-et-alertes.md) avant d'auditer.

## Prérequis

1. Vérifiez que `mariadb-11-8` ou `sirene-postgres` tourne avec les jeux de test chargés.
2. Vérifiez que Python 3 et `git` sont disponibles à la racine du dépôt.
3. Vérifiez l'accès aux fichiers `sirene/test_sirene_sha2.sql` et `test_employees_sha2.sql`.

## Consignes de sécurité

**AVERTISSEMENT :** N'importez jamais de données personnelles réelles INSEE ou RH dans des dépôts publics.
Des données nominatives exposent des identifiants personnels et enfreignent les limites de confidentialité.

**ATTENTION :** Excluez `.env`, `sirene/.env`, `*.kdbx`, `*.keyx`, `*.pid` et `*.log` de Git et MkDocs.
Un fichier privé publié expose les secrets ou journaux sur le portail web.

## Étapes

1. Vérifiez les comptages et sommes CRC32 de la base `employees` :

   ```bash
   make verify
   ```

2. Exécutez la vérification `SHA2(..., 256)` sous MariaDB ou MySQL :

   ```bash
   docker exec -i mariadb-11-8 mariadb -u root -t < test_employees_sha2.sql
   ```

3. Sur PostgreSQL `employees`, lancez le script SHA-256 équivalent :

   ```bash
   psql -d employees -v ON_ERROR_STOP=1 -f postgresql/test_employees_sha2.sql
   ```

4. Vérifiez les comptages et sommes SHA-256 des douze tables Sirene PostgreSQL 18 :

   ```bash
   make sirene-verify
   ```

5. Exécutez les tests du jeu synthétique et de gouvernance dans Docker :

   ```bash
   make sirene-test
   ```

6. Recherchez toute fuite de chemin local dans `docs/` et `documentation/` :

   ```bash
   git grep -nE '(/Users/|/home/|[A-Za-z]:[/\\]Users[/\\])' docs/ documentation/ || true
   ```

7. Examinez `.gitignore`, `exclude_docs` dans `mkdocs.fr.yml` et `git status` avant chaque build.

**NOTE :** Les enregistrements synthétiques Sirene utilisent des SIREN `9xxxxxxxx` générés avec `seed = 20261120`.
Tous les noms et adresses de `sirene/data/` sont entièrement fictifs et sans PII.

## Vérification

1. Vérifiez que `make verify` retourne le code `0` et affiche `Data integrity verification passed`.
2. Vérifiez que `make sirene-verify` affiche `CRC | OK` et `count | OK` sans erreur.
3. Vérifiez que `git grep` retourne zéro chemin local et que `git status` exclut `.env`.

## Retour arrière

Si une divergence de somme ou une fuite privée survient, exécutez ces actions :

1. Interrompez immédiatement la publication web ou l'export de conteneur.
2. Videz les tables altérées, puis rechargez les références avec `make inject` ou `make sirene-inject`.
3. Retirez tout fichier `.env` ou secret de l'index Git et renouvelez les mots de passe de laboratoire.
4. Redémarrez `make verify`, `make sirene-verify` et `make sirene-test` jusqu'au succès complet.

## Documentation associée

- Référence : [Matrice des jeux de données et schémas](../../03-reference/architecture-specs/matrice-jeux-donnees-et-schemas.md)
- Référence : [Matrice des erreurs et alertes](../../03-reference/codes-erreurs/matrice-erreurs-et-alertes.md)
- Explications :
  [ADR-002 : Architecture Diátaxis et publication MkDocs](../../04-explications/decisions-architecture/adr-002-diataxis-et-publication-mkdocs-versionnee.md)
- Explications : [Architecture plateforme et ETL](../../04-explications/vue-architecture/architecture-plateforme-et-etl.md)
