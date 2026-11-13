# Fondements et Application de Big Data : travaux pratiques

**Quentin Chamberlan**, FISA 5A (identifiant 12) · rendu des TP1, TP2 et TP3, date limite 18/11/2026.

Chaque TP est dans son dossier, avec son propre README. Les notebooks sont enregistrés **avec leurs sorties** :
on peut les lire sur GitHub sans rien exécuter.

| Dossier | Sujet | Notebooks | Outils |
|---|---|---|---|
| [`TP1/`](TP1/) | **Comptage de mots** par les quatre méthodes demandées (Python séquentiel, pseudo-MapReduce en Python, Hadoop MapReduce, PySpark en RDD et en DataFrame), mesurées de 100 000 à 20 millions de lignes | [`comptage_mots.ipynb`](TP1/comptage_mots.ipynb), [`comptage_mots_spark.ipynb`](TP1/comptage_mots_spark.ipynb) | Python, Hadoop (HDFS + YARN dans Docker), PySpark |
| [`TP2/`](TP2/) | **Accidents de la route** d'Australie-Méridionale (2012-2019) avec PySpark, d'après un article Medium refait et corrigé | [`road_crash_pyspark.ipynb`](TP2/road_crash_pyspark.ipynb) | PySpark (RDD, DataFrame, SparkSQL), pandas pour les tests |
| [`TP3_ID12/`](TP3_ID12/) | **Deux cas personnels**, chaîne complète Data → EDA → Prétraitement → Transformation → ML → Éval → Déploiement | [`Small/tokyo_immo.ipynb`](TP3_ID12/Small/tokyo_immo.ipynb) (prix de l'immobilier à Tokyo), [`Big/chicago_velos.ipynb`](TP3_ID12/Big/chicago_velos.ipynb) (vélos Divvy à Chicago) | Small : pandas, scikit-learn, **PySpark** ; Big : HDFS (Docker), Spark SQL, Spark MLlib ; Streamlit pour les deux |

## Ce que contient chaque notebook

- **Première cellule** : titre du TP, nom, date ; pour le TP2 et le TP3, la **contribution** : le notebook
  s'exécute-t-il de bout en bout, les problèmes rencontrés, les modifications apportées, les autres informations.
- **Étapes étiquetées** (TP2 et TP3) : avant chaque section, une cellule `## [Étape]` (Data, EDA, Prétraitement,
  Transformation, ML, Éval, Déploiement, plus Environnement, Tests et Conclusion quand il le faut).
- Des **tests** `verifier(...)` qui affichent OK ou ÉCHEC, avec un bilan en fin de notebook, des commentaires et
  une conclusion.
- TP3 Small : le cas d'origine utilisait pandas ; une **partie 8 « Le même traitement avec PySpark »** refait la
  lecture, le nettoyage et les variables avec Spark et vérifie que le résultat est identique à pandas.

## Résultats en bref

| TP | Résultat principal |
|---|---|
| TP1 | Sur 20 millions de lignes : Spark DataFrame 3,1 s, Python simple 5,2 s, Spark RDD 27,5 s, Hadoop MapReduce 54,3 s (coût fixe de Hadoop : 30 à 35 s selon la mesure) |
| TP2 | Un accident avec alcool est 8 fois plus souvent mortel, avec drogue 15 fois, avec les deux 31 fois ; le code de l'article décalait 16,7 % des lignes (`split(',')`), corrigé |
| TP3 Small | HistGradientBoosting : R² 0,917 (log du prix), erreur relative médiane 9,8 % ; Spark et pandas donnent le même nettoyage |
| TP3 Big | 5,9 millions de trajets dans HDFS ; GBT MLlib : RMSE 1,74 départ / heure, R² 0,604 (moyenne historique : 0,392) |

## Lancer

Chaque TP se lance depuis son dossier (`cd TP1`, `cd TP2`, `cd TP3_ID12/Small` ou `cd TP3_ID12/Big`) ; les
prérequis et les commandes sont dans le README du TP. Les données ne sont pas versionnées : les notebooks les
téléchargent au premier lancement. Les clusters Hadoop de `TP1/` et de `TP3_ID12/Big/` utilisent les mêmes
ports (9870...) : arrêter l'un (`docker compose down`) avant de démarrer l'autre.

Sous Windows, cloner avec `git clone -c core.longpaths=true ...` : le chemin du modèle MLlib sauvegardé dépasse
260 caractères.
