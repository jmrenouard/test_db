[🏠 Accueil](index.md) | [⬅️ Précédent](guide_outils.md) | [➡️ Suivant](benchmarking.md)
***

# Rapports Interactifs et Tableaux de Bord HTML

L'environnement de test fournit un outil Interactif (Interactive Runner) et un moteur de reporting automatisé (propulsé par Python et Tailwind CSS) pour présenter les données complexes de benchmark dans un format accessible.

## Le Lanceur Interactif (`make interactive`)

Pour exécuter des tests et générer des rapports sans mémoriser les arguments du Makefile, lancez :

```bash
make interactive
```

Ceci lance une interface utilisateur en terminal (`interactive_runner.py`) qui guide à travers :

1. La détection de l'environnement (Docker vs Local).
2. La sélection du type de test à exécuter :
   - **Vérification** : Comptage des données et intégrité structurelle.
   - **Bench Standard** : Tests OLTP de base avec `sysbench`.
   - **Performance (Threads)** : Graphiques QPS / Latence de 1 à 64 threads.
   - **Tests de Données** : Deadlocks, Gap Locks, tests d'isolation, etc.
   - **Analyse SQL** : `EXPLAIN` automatisé et détection d'index manquants.
3. L'exécution du test avec affichage de la progression en direct.
4. La génération automatique de rapports HTML améliorés une fois terminé.

---

## Le Simulateur de Base de Données (`db_simulator.py`)

Pour un contrôle avancé et une simulation spécifique de la charge de travail SQL avec une sortie HTML premium, le script `db_simulator.py` remplace la sortie terminal standard de `sysbench` par des tableaux de bord actionnables.

### Capacités Clés

1. **Visualisation des Deadlocks** : Met en évidence précisément quelles transactions sont entrées en collision.
2. **Graphiques Interactifs** : Trace les centiles de latence et le débit (QPS) par rapport au nombre de threads.
3. **Capture de l'Environnement** : Effectue un instantané de l'OS, de la RAM et de la version de la base de données pour une reproductibilité vérifiable.
4. **Style Tailwind** : Les rapports HTML sont autonomes et magnifiquement mis en page avec Tailwind CSS via CDN.

### Exemple d'Exécution

Pour exécuter manuellement une simulation de charge de travail depuis un répertoire :

```bash
python3 scripts/db_simulator.py \
  --sql-dir tests/data/deadlock/ \
  --container mariadb-11-8 \
  --threads 16 \
  --time 30
```

### Sortie des Rapports

Selon l'outil utilisé, les rapports finaux sont placés dans le répertoire `reports/`.

- `reports/performance_report.html` (Tableau de bord global d'exécution)
- `reports/perf_threads/scaling_report.html` (Scalabilité et comparaisons par threads)
- `reports/simulator_report.html` (Sorties spécifiques du simulateur et faits saillants des deadlocks)

Ces fichiers peuvent être ouverts directement dans tout navigateur web moderne.

***
[🏠 Accueil](index.md) | [⬅️ Précédent](guide_outils.md) | [➡️ Suivant](benchmarking.md)
