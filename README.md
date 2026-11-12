# Fondements et Application de Big Data : travaux pratiques

Les trois TP du cours, chacun dans son dossier avec son propre README. Les notebooks sont enregistrés avec leurs
sorties : on peut les lire sur GitHub sans rien exécuter.

| Dossier | Sujet | Outils |
|---|---|---|
| [`tp1/`](tp1/) | **Comptage de mots** résolu de cinq façons (Python simple, pseudo-MapReduce, Hadoop MapReduce, Spark RDD, Spark DataFrame) et mesuré de 100 000 à 20 millions de lignes | Python, Hadoop (HDFS + YARN dans Docker), PySpark |
| [`tp2/`](tp2/) | **Étude de cas** : analyse des accidents de la route d'Australie-Méridionale (2012-2019) avec PySpark, d'après un article Medium refait partie par partie | PySpark |
| [`tp3/`](tp3/) | **Du jeu de données au modèle déployé** : prix des appartements à Tokyo (pandas + scikit-learn), puis départs de vélos Divvy à Chicago (HDFS + Spark MLlib), chaîne complète Data → EDA → Prétraitement → Transformation → ML → Évaluation → Déploiement | pandas, scikit-learn, HDFS (Docker), Spark MLlib, Streamlit |

Chaque TP se lance depuis son dossier (`cd tp1`, `cd tp2` ou `cd tp3`). Les clusters Hadoop de `tp1/` et de
`tp3/` utilisent les mêmes ports (9870...) : arrêter l'un (`docker compose down`) avant de démarrer l'autre.
