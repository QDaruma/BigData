# Comptage de mots : Python, MapReduce, Hadoop et Spark

TP du cours *Fondements et Application de Big Data*. Un seul problème, compter les occurrences de chaque mot d'un fichier, résolu de cinq façons et mesuré sur des fichiers de 100 000 à 20 millions de lignes.

| | Méthode | Principe | Code |
|---|---|---|---|
| V1 | Python simple | lecture complète du fichier + dictionnaire | `wordcount.py` |
| V2 | Pseudo-MapReduce | fonctions `mapper` / `shuffle` / `reducer` exécutées en local | `mapreduce_wordcount.py` |
| V3 | Hadoop MapReduce | job `wordcount` sur un cluster HDFS + YARN (Docker) | `hadoop/` |
| V4 | Spark RDD | `textFile` → `flatMap` → `map` → `reduceByKey` | `spark_wordcount.py` |
| V5 | Spark DataFrame | `split` + `explode` → `groupBy` → `count`, exécuté dans la JVM | `spark_wordcount.py` |

## Les deux notebooks

| Notebook | Contenu |
|---|---|
| **`comptage_mots.ipynb`** | TP 1 : V1, V2 et V3, effet de la taille des blocs HDFS |
| **`comptage_mots_spark.ipynb`** | TP 2 : V4 et V5 avec PySpark, puis comparaison des cinq méthodes sur les mêmes fichiers, effet du nombre de partitions et de cœurs |

Chacun contient le problème, les explications, le code, les tests, les comparaisons et la conclusion. Ils sont enregistrés avec leurs sorties : on peut les lire sans rien exécuter.

## Résultats en bref

Mesures du second notebook : les cinq méthodes le même jour, sur la même machine (Windows 11, 12 cœurs logiques). Les temps Spark sont ceux du job, session déjà démarrée.

| Lignes | V1 Python simple | V2 pseudo-MapReduce | V3 Hadoop | V4 Spark RDD | V5 Spark DataFrame |
|---|---|---|---|---|---|
| 100 000 | 0,019 s | 0,068 s | 34,6 s | 5,0 s | 0,29 s |
| 5 millions | 1,19 s | 3,82 s | 39,3 s | 10,3 s | 1,11 s |
| 20 millions | 5,17 s | 19,0 s | 54,3 s | 27,5 s | 3,07 s |

- Les cinq méthodes donnent **exactement les mêmes comptes** à toutes les tailles.
- **Python simple** reste le plus rapide sur les petits fichiers.
- **Pseudo-MapReduce** est 3 à 4 fois plus lent, sans rien gagner sur une seule machine.
- **Hadoop** repaie environ 35 s à chaque job, quelle que soit la taille. Il ne devient intéressant que sur de très gros volumes répartis sur plusieurs machines.
- **Spark** paie son démarrage une seule fois (environ 11 s). Ensuite un job DataFrame coûte quelques dixièmes de seconde.
- **Spark DataFrame** dépasse Python simple à partir d'environ 5 millions de lignes, grâce aux 12 cœurs. Limité à un seul cœur, il est presque deux fois plus lent.
- **Spark RDD** est 9 à 17 fois plus lent que le DataFrame : chaque tâche passe par un processus Python, relancé à chaque fois sous Windows.

## Lancer les notebooks

Prérequis :
- Python 3.10 ou plus récent ;
- Docker Desktop lancé, pour Hadoop. Le notebook télécharge l'image `apache/hadoop:3.4.1` (environ 3 Go) ;
- Java 8, 11 ou 17, pour Spark. PySpark 3.5 est utilisé ici (PySpark 4 demande Java 17).

```bash
pip install jupyter pandas matplotlib "pyspark>=3.5,<3.6"

jupyter notebook comptage_mots.ipynb          # TP 1, une dizaine de minutes
jupyter notebook comptage_mots_spark.ipynb    # TP 2, une vingtaine de minutes
```

Les notebooks génèrent eux-mêmes les fichiers de test dans `data/` (environ 200 Mo, non versionnés) et démarrent le cluster Hadoop, dont la configuration est dans `hadoop/`. Spark tourne en mode local (`local[*]`), sans cluster.

Le script Spark se lance aussi seul :

```bash
python spark_wordcount.py data/mots.txt df    # ou rdd
```

Quand vous avez fini, arrêtez le cluster :

```bash
docker compose -f hadoop/docker-compose.yml down
```

## Contenu du dépôt

```
comptage_mots.ipynb          TP 1 : Python, pseudo-MapReduce, Hadoop
comptage_mots_spark.ipynb    TP 2 : Spark (RDD et DataFrame), comparaison des cinq méthodes
wordcount.py                 V1
mapreduce_wordcount.py       V2
spark_wordcount.py           V4 et V5
hadoop/                      docker-compose.yml et configuration du cluster (V3)
data/                        fichiers de test générés (ignoré par git)
```
