# Étude de cas : accidents de la route avec PySpark

Étude de cas du cours *Fondements et Application de Big Data* : l'article Medium *Big Data Analysis of Road Crash Data using PySpark* de Rakesh Nain, refait partie par partie dans un notebook, avec des explications simples, des tests et des comparaisons.

- Article : [Big Data Analysis of Road Crash Data using PySpark](https://medium.com/rakesh-nain/big-data-analysis-of-road-crash-data-using-pyspark-with-pyspark-tutorial-c78ff2c35588)
- Dépôt de l'auteur (notebook et données) : [RakeshNain/Big-data-Analysis-of-Road-Crash-Data-using-PySpark-with-PySpark-Tutorial](https://github.com/RakeshNain/Big-data-Analysis-of-Road-Crash-Data-using-PySpark-with-PySpark-Tutorial)

Les données sont celles des accidents d'Australie-Méridionale de 2012 à 2019 : 127 672 accidents et 272 591 unités impliquées (véhicules, piétons), en 16 fichiers CSV (80 Mo).

## Le notebook

**`road_crash_pyspark.ipynb`** contient le problème, les explications, le code, les tests, les comparaisons et la conclusion. Il est enregistré avec ses sorties : on peut le lire sans rien exécuter.

1. Environnement et données
2. Démarrer Spark
3. Analyse avec les RDD : partitions, `partitionBy`, `reduceByKey`, jointures
4. Analyse avec les DataFrames : filtres, tris, agrégations
5. Alcool, drogue et gravité des accidents
6. Une même requête écrite trois fois : RDD, DataFrame, SparkSQL
7. Tests : tout est recalculé avec pandas
8. Comparaison des temps
9. Conclusion

## Résultats en bref

- **L'alcool et la drogue rendent les accidents plus graves.** 0,42 % des accidents sans alcool ni drogue sont mortels, contre 3,42 % avec alcool (8 fois plus), 6,31 % avec drogue (15 fois plus) et 13,09 % avec les deux (31 fois plus).
- **Les obstacles fixes sont les plus meurtriers** : 245 morts sur la période, devant les collisions frontales (136) et les piétons renversés (109).
- **Le code de l'article contient des erreurs.** Il découpe les lignes avec `split(',')`, qui coupe aussi les virgules entre guillemets : 16,7 % des lignes d'accidents sont décalées. En plus, certains indices de colonnes sont faux, et ses versions RDD et DataFrame de la même requête ne donnent pas le même résultat (3 935 et 7 514 victimes à Adélaïde, au lieu de 43). Le notebook montre chaque erreur et la corrige. Les chiffres que l'article publie sont, eux, retrouvés exactement.
- **DataFrame et SparkSQL ont le même plan d'exécution**, donc les mêmes temps. Les RDD sont bien plus lents, car chaque ligne passe par un processus Python. Sur ce petit volume, pandas reste le plus rapide.

## Lancer le notebook

Prérequis : Python 3.10 ou plus récent, et Java 8, 11 ou 17. PySpark 3.5 est utilisé ici (PySpark 4 demande Java 17).

```bash
pip install jupyter pandas matplotlib "pyspark>=3.5,<3.6"
jupyter notebook road_crash_pyspark.ipynb    # une vingtaine de minutes
```

Au premier lancement, le notebook télécharge les CSV du dépôt de l'auteur dans `data/road_crash/` (80 Mo, non versionné). Spark tourne en mode local (`local[*]`), sans cluster.

Sous Windows, le notebook règle `spark.python.authenticate.socketTimeout` : sans ce réglage, PySpark 3.5 coupe au bout de 15 s la connexion entre Java et ses processus Python, et les jointures de RDD plantent.
