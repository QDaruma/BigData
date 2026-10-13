# Comptage de mots : Python, pseudo-MapReduce et Hadoop

TP du cours *Fondements et Application de Big Data*. On compte les occurrences de mots de trois façons, puis on compare leurs temps d'exécution sur des fichiers de 100 000 à 20 millions de lignes.

| Méthode | Principe |
|---|---|
| Python simple (`wordcount.py`) | lecture complète du fichier + dictionnaire |
| Pseudo-MapReduce (`mapreduce_wordcount.py`) | fonctions `mapper` / `shuffle` / `reducer` exécutées en local |
| Hadoop MapReduce | job `wordcount` sur un cluster HDFS + YARN (Docker) |

Tout est dans le notebook **`comptage_mots.ipynb`** : explications, code, tests, comparaisons et conclusion.

## Lancer le notebook

Prérequis :
- Python 3.10 ou plus récent, avec `jupyter`, `pandas` et `matplotlib` ;
- Docker Desktop lancé, pour la partie Hadoop. Le notebook télécharge l'image `apache/hadoop:3.4.1` (environ 3 Go).

```bash
pip install jupyter pandas matplotlib
jupyter notebook comptage_mots.ipynb
```

Le notebook génère lui-même les fichiers de test dans `data/` (environ 200 Mo). Il démarre aussi le cluster Hadoop, dont la configuration est dans `hadoop/`. Une exécution complète prend une dizaine de minutes.

Quand vous avez fini, arrêtez le cluster :

```bash
docker compose -f hadoop/docker-compose.yml down
```

## Résultats en bref

| Lignes | Python simple | Pseudo-MapReduce | Hadoop |
|---|---|---|---|
| 100 000 | 0,015 s | 0,067 s | 31,5 s |
| 20 millions | 7,2 s | 20,5 s | 56,1 s |

- Les trois méthodes donnent exactement les mêmes comptes à toutes les tailles.
- **Python simple** est le plus rapide à toutes les tailles testées.
- **Pseudo-MapReduce** est 3 à 4 fois plus lent, sans rien gagner sur une seule machine.
- **Hadoop** perd environ 30 s à chaque lancement, quelle que soit la taille. Il ne devient intéressant que sur de très gros volumes répartis sur plusieurs machines.
