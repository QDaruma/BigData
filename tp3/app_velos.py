"""Appli de déploiement du sujet 2 : prévoir les départs de vélos Divvy heure par heure.

Lancer :  streamlit run app_velos.py
Le modèle MLlib (modeles/velos_pipeline) est produit par le notebook chicago_velos.ipynb.
Pas besoin de HDFS : une session Spark locale suffit pour charger le modèle et prédire.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
# Windows : Spark a besoin de winutils.exe et hadoop.dll pour lire le modèle sur le disque (voir le README).
if sys.platform == "win32" and "HADOOP_HOME" not in os.environ and (Path.home() / "hadoop-3.3.5").exists():
    os.environ["HADOOP_HOME"] = str(Path.home() / "hadoop-3.3.5")
if os.environ.get("HADOOP_HOME"):
    os.environ["PATH"] = os.path.join(os.environ["HADOOP_HOME"], "bin") + os.pathsep + os.environ["PATH"]

DOSSIER = Path(__file__).parent / "modeles"
FERIES_2024 = ["2024-01-01", "2024-01-15", "2024-02-19", "2024-05-27", "2024-06-19", "2024-07-04",
               "2024-09-02", "2024-10-14", "2024-11-11", "2024-11-28", "2024-12-25"]


@st.cache_resource
def charger():
    from pyspark.ml import PipelineModel
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[2]").appName("app_velos")
             .config("spark.ui.enabled", "false").getOrCreate())
    modele = PipelineModel.load((DOSSIER / "velos_pipeline").resolve().as_uri())
    infos = json.loads((DOSSIER / "velos_stations.json").read_text(encoding="utf-8"))
    return spark, modele, infos


def prevoir(spark, modele, info, date, temperature, pluie_mm, vent_kmh):
    """Même calcul que la fonction prevoir() du notebook."""
    d = pd.Timestamp(date)
    weekend = int(d.dayofweek >= 5)
    lignes = [{"heure": h, "jour_semaine": (d.dayofweek + 1) % 7 + 1, "mois": d.month, "weekend": weekend,
               "ferie": int(d.strftime("%Y-%m-%d") in FERIES_2024), "temperature": float(temperature),
               "pluie_mm": float(pluie_mm), "pluie": int(pluie_mm > 0), "vent_kmh": float(vent_kmh),
               "station_moy": info["station_moy"], "station_heure_moy": info["profil"][f"{weekend}-{h}"],
               "lat": info["lat"], "lng": info["lng"]} for h in range(24)]
    p = modele.transform(spark.createDataFrame(pd.DataFrame(lignes))).select("heure", "prediction").toPandas()
    return p.set_index("heure")["prediction"].clip(lower=0)


st.set_page_config(page_title="Vélos Divvy : prévision des départs", page_icon="🚲")
st.title("Combien de vélos vont partir de cette station ?")
st.caption("Modèle Spark MLlib appris sur les 5,9 millions de trajets Divvy de 2024 (Chicago) et la météo horaire.")

with st.spinner("Démarrage de Spark et chargement du modèle..."):
    spark, modele, infos = charger()

stations = sorted(infos, key=lambda s: -infos[s]["station_moy"])
station = st.selectbox("Station (classées de la plus fréquentée à la moins fréquentée)", stations)
g, m, d = st.columns(3)
date = g.date_input("Date", dt.date(2024, 7, 16))
temperature = m.slider("Température (°C)", -20, 38, 24)
pluie = d.slider("Pluie (mm par heure)", 0.0, 10.0, 0.0, 0.5)
vent = d.slider("Vent (km/h)", 0, 60, 15)

prev = prevoir(spark, modele, infos[station], date, temperature, pluie, vent)
st.metric("Départs prévus sur la journée", f"{prev.sum():.0f} vélos")
st.bar_chart(prev.rename("départs prévus"), x_label="heure", y_label="départs")
pic = int(prev.idxmax())
st.write(f"Heure la plus chargée : **{pic} h** ({prev.max():.1f} départs). "
         "Prévoir de remplir la station avant cette heure.")
