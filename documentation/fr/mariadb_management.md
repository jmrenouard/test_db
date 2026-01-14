# Gestion de MariaDB 11.8

Ce projet utilise MariaDB 11.8 dans un environnement Dockerisé pour garantir la reproductibilité et la cohérence des performances.

## Commandes de Cycle de Vie

Le `Makefile` simplifie la gestion du conteneur MariaDB :

- **Démarrage** : `make start` - Lance le conteneur `mariadb-11-8`.
- **Arrêt** : `make stop` - Arrête le conteneur en toute sécurité.
- **Statut** : `make status` - Vérifie si le conteneur est opérationnel et sain.

## Détails de l'Environnement

- **SGBD** : MariaDB 11.8
- **Nom du Conteneur par Défaut** : `mariadb-11-8`
- **Port par Défaut** : `3306`
- **Identifiants par Défaut** : Le mot de passe root est `root` (prévu pour un usage en laboratoire).

## Gestion des Données

Les requêtes et les données sont injectées via la cible `make inject`, qui :

1. Crée un répertoire temporaire dans le conteneur.
2. Copie le jeu de données (par exemple, `employees`) vers `/tmp`.
3. Exécute le script d'initialisation SQL via l'entrée standard `mariadb`.
