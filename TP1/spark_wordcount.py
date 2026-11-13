import os
import sys
from operator import add

from pyspark.sql import SparkSession, functions as F


def compter_spark_rdd(sc, fichier, partitions=None):
    comptes = (sc.textFile(str(fichier), partitions)
                 .flatMap(lambda ligne: ligne.split())
                 .map(lambda mot: (mot, 1))
                 .reduceByKey(add))
    return dict(comptes.collect())


def compter_spark_df(spark, fichier):
    mots = (spark.read.text(str(fichier))
                 .select(F.explode(F.split(F.col("value"), r"\s+")).alias("mot"))
                 .where(F.col("mot") != ""))
    comptes = mots.groupBy("mot").count()
    return {ligne["mot"]: ligne["count"] for ligne in comptes.collect()}


if __name__ == "__main__":
    fichier = sys.argv[1] if len(sys.argv) > 1 else "mots.txt"
    api = sys.argv[2] if len(sys.argv) > 2 else "rdd"
    sys.stdout.reconfigure(encoding="utf-8")    # même redirigée, la sortie reste en UTF-8 (accents)
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    spark = SparkSession.builder.master("local[*]").appName("wordcount").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    if api == "df":
        resultats = compter_spark_df(spark, fichier)
    else:
        resultats = compter_spark_rdd(spark.sparkContext, fichier)
    for mot, nb in sorted(resultats.items(), key=lambda x: x[1], reverse=True):
        print(f"{mot} : {nb}")
    spark.stop()
