# TP3 (identifiant 12) : du jeu de données au modèle déployé

**Quentin Chamberlan**, FISA 5A.

Cours « Fondements et Application de Big Data ». Deux projets complets, chacun suivant la chaîne
**[Data] → [EDA] → [Prétraitement] → [Transformation] → [ML] → [Évaluation] → [Déploiement]** :

| | Sujet 1 : prix de l'immobilier à Tokyo | Sujet 2 : vélos en libre-service à Chicago |
|---|---|---|
| Dossier | [`Small/`](Small/) | [`Big/`](Big/) |
| Notebook | [`Small/tokyo_immo.ipynb`](Small/tokyo_immo.ipynb) | [`Big/chicago_velos.ipynb`](Big/chicago_velos.ipynb) |
| Données | Kaggle, ventes immobilières du MLIT (Tokyo, 2005-2019), 406 575 lignes | Divvy, tous les trajets 2024 (12 fichiers CSV, ~1 Go) + météo horaire Open-Meteo |
| Outils | pandas + scikit-learn, et le même traitement refait avec PySpark | HDFS (Hadoop 3.4 dans Docker) + Spark 3.5 / MLlib |
| Question | Combien vaut cet appartement d'occasion ? | Combien de vélos partiront de cette station, heure par heure ? |
| Déploiement | Appli Streamlit [`Small/app_tokyo.py`](Small/app_tokyo.py) | Appli Streamlit [`Big/app_velos.py`](Big/app_velos.py) (modèle MLlib) |

Chaque notebook est exécuté (sorties et graphiques visibles sur GitHub) et contient des tests
`verifier(...)` qui affichent OK ou ÉCHEC à chaque étape ; le bilan des tests est en fin de notebook.

## Sujet 1 : prix des appartements d'occasion à Tokyo

- 406 575 transactions, dont 184 331 appartements ; 160 626 gardés après nettoyage (87,1 %).
- 17 variables (surface, âge, commune, gare, minutes à pied, plan, zonage, date...) → 81 colonnes encodées.
- Cible : log du prix. Découpage aléatoire 80/20 (128 500 / 32 126 ventes).

| Modèle | Erreur absolue moyenne | Erreur relative médiane | R² (log) | Apprentissage |
|---|---|---|---|---|
| Règle simple (prix au m² de la gare × surface) | 7,85 M¥ | 23,8 % | 0,658 | – |
| Ridge | 5,36 M¥ | 15,15 % | 0,841 | 1 s |
| Forêt aléatoire | 3,95 M¥ | 10,49 % | 0,906 | 20 s |
| **HistGradientBoosting** | **3,62 M¥** | **9,84 %** | **0,917** | 38 s |

- Validation croisée 5 plis : R² 0,9147 ± 0,0008. 51 % des estimations à ±10 %, 80 % à ±20 %.
- Test temporel (appris avant 2018, testé sur 2018-2019) : erreur médiane 11,1 %, R² 0,89, biais −6 %
  (le marché a monté plus vite que ce que le modèle a vu).
- Variables les plus utiles (importance par permutation) : surface, âge, commune, date de vente.
- **PySpark (partie 8, ajoutée pour le rendu)** : lecture, 7 règles de nettoyage, 17 variables et une
  agrégation SparkSQL refaites avec Spark ; résultats identiques à pandas (vérifié ligne pour ligne). À cette
  taille (104 Mo), Spark n'est pas plus rapide que pandas.

## Sujet 2 : départs de vélos Divvy à Chicago

- 5 860 568 trajets Divvy 2024 (12 CSV, 1,1 Go) déposés dans HDFS (16 blocs), convertis en Parquet (211 Mo).
- 4 716 358 trajets gardés après nettoyage (départ d'une station, durée plausible) ; 1 808 stations, dont les
  300 plus utilisées (86 % des départs) sont modélisées.
- Météo horaire Open-Meteo convertie en heure de Chicago (heure d'été comprise) : 8 783 heures en 2024.
- Grille complète station × heure : 2 634 900 cases (une case sur deux à 0 départ, moyenne 1,53).
- Découpage dans le temps : du 1er au 23 de chaque mois pour l'apprentissage (1 986 900 cases), du 24 à la fin du
  mois pour le test (648 000), pour que toutes les saisons soient dans les deux parts.

| Modèle (Spark MLlib) | RMSE | MAE | R² | Apprentissage |
|---|---|---|---|---|
| Moyenne historique (station × heure) | 2,157 | 1,220 | 0,392 | – |
| Régression linéaire | 2,020 | 1,223 | 0,467 | 17 s |
| Forêt aléatoire | 1,765 | 1,009 | 0,593 | 570 s |
| **Gradient boosting (GBT)** | **1,739** | **0,999** | **0,604** | 408 s |

- Variables les plus utiles : profil horaire de la station, température, heure, position.
- Été / hiver : plus de 5 fois plus de trajets ; corrélation trajets–température 0,87.
- Limite connue : le GBT n'est pas monotone en la pluie (en juillet, une forte averse fait parfois monter la
  prévision, car les orages d'été sont rares dans les données) ; détaillé dans le notebook.
- Temps de lecture d'une colonne : pandas 8,3 s, Spark depuis le CSV 10,3 s, Spark depuis le Parquet 2,1 s
  (sur un seul PC à 12 cœurs ; pandas doit en plus tenir toute la colonne en mémoire, 468 Mo).

## Lancer le projet

Python 3.11, Java 8 ou 17 (pour Spark, y compris la partie 8 du cas Small), Docker (cas Big).

Les commandes du sujet 1 se lancent depuis `Small/`, celles du sujet 2 depuis `Big/`. Si le cluster Hadoop du
TP1 tourne, l'arrêter d'abord (`docker compose down` dans `../../TP1/hadoop`) : il utilise le même port 9870.

```bash
pip install pandas numpy scikit-learn matplotlib joblib streamlit "pyspark==3.5.*" kagglehub jupyter

# Sujet 1 (dans Small/) : le notebook télécharge les données Kaggle
cd Small
jupyter notebook tokyo_immo.ipynb
streamlit run app_tokyo.py
cd ..

# Sujet 2 (dans Big/) : démarrer HDFS (NameNode + DataNode), puis le notebook télécharge Divvy et remplit HDFS
cd Big
cd hadoop && docker compose up -d && cd ..
jupyter notebook chicago_velos.ipynb
streamlit run app_velos.py
```

**Windows seulement** : Spark (Hadoop 3.3.4) a besoin de `winutils.exe` et `hadoop.dll` pour écrire sur le
disque local. Les copier depuis [cdarlint/winutils](https://github.com/cdarlint/winutils) (`hadoop-3.3.5/bin`)
dans `%USERPROFILE%\hadoop-3.3.5\bin` ; le notebook et l'appli règlent `HADOOP_HOME` et `PATH` eux-mêmes.

## Organisation

```
Small/                 sujet 1 (petites données)
  tokyo_immo.ipynb     notebook : pandas + scikit-learn, puis partie 8 en PySpark
  tokyo_prep.py        préparation des variables, partagée entre le notebook et l'appli
  app_tokyo.py         déploiement (Streamlit)
  outils.py            verifier() et petites aides communes
  modeles/             modèle entraîné (joblib) et tables utilisées par l'appli
Big/                   sujet 2 (Big Data)
  chicago_velos.ipynb  notebook : HDFS + Spark SQL + Spark MLlib
  app_velos.py         déploiement (Streamlit, modèle MLlib)
  outils.py            verifier() et petites aides communes
  hadoop/              docker-compose.yml et configuration du mini-cluster HDFS
  modeles/             pipeline MLlib sauvegardé et table des stations
data/ (dans chaque dossier)  données brutes, non versionnées, recréées par les notebooks
```

## Sources

- Japan Real Estate Transaction Prices, Kaggle (nishiodens), d'après le MLIT japonais.
- Divvy Trip Data, `https://divvy-tripdata.s3.amazonaws.com/` (licence Divvy Data License Agreement).
- Météo historique horaire : Open-Meteo Archive API (`archive-api.open-meteo.com`).
