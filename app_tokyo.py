"""Appli de déploiement du sujet 1 : estimer le prix d'un appartement d'occasion à Tokyo.

Lancer :  streamlit run app_tokyo.py
Le modèle (modeles/tokyo_prix.joblib) est produit par le notebook tokyo_immo.ipynb.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

import tokyo_prep

DOSSIER = Path(__file__).parent / "modeles"


@st.cache_resource
def charger():
    modele = joblib.load(DOSSIER / "tokyo_prix.joblib")
    gares = json.loads((DOSSIER / "tokyo_gares.json").read_text(encoding="utf-8"))
    fourchette = json.loads((DOSSIER / "tokyo_fourchette.json").read_text(encoding="utf-8"))
    return modele, gares, fourchette


def estimer(modele, infos, commune, gare, surface, annee_construction, minutes, plan, renove, annee, trimestre):
    """Même calcul que la fonction estimer() du notebook."""
    ligne = pd.DataFrame([{"Municipality": commune, "NearestStation": gare, "MinTimeToNearestStation": minutes,
                           "Area": surface, "FloorPlan": plan, "BuildingYear": annee_construction,
                           "Structure": infos["Structure"], "Renovation": "Done" if renove else "Not yet",
                           "CityPlanning": infos["CityPlanning"], "CoverageRatio": infos["CoverageRatio"],
                           "FloorAreaRatio": infos["FloorAreaRatio"], "Year": annee, "Quarter": trimestre}])
    return float(np.exp(modele.predict(tokyo_prep.variables(ligne))[0]))


st.set_page_config(page_title="Prix d'un appartement à Tokyo", page_icon="🏢")
st.title("Combien vaut cet appartement à Tokyo ?")
st.caption("Modèle de gradient boosting appris sur 160 000 ventes d'appartements d'occasion (2005-2019, "
           "données du ministère japonais MLIT via Kaggle).")

modele, gares, fourchette = charger()

g, d = st.columns(2)
communes = sorted(gares)
commune = g.selectbox("Commune", communes, index=communes.index("Setagaya Ward") if "Setagaya Ward" in communes else 0)
liste_gares = sorted(gares[commune], key=lambda x: -gares[commune][x]["ventes"])
gare = d.selectbox("Gare la plus proche", liste_gares)
surface = g.slider("Surface (m²)", 15, 150, 55)
plan = d.selectbox("Plan", ["1R", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3DK", "3LDK", "4LDK", "2LDK+S", "3LDK+S"],
                   index=6)
annee_construction = g.slider("Année de construction", 1960, 2019, 2005)
minutes = d.slider("Minutes à pied jusqu'à la gare", 1, 30, 7)
renove = g.checkbox("Appartement rénové")
annee = d.selectbox("Date de vente (année)", list(range(2019, 2004, -1)))
trimestre = 3 if annee == 2019 else 2

if annee_construction > annee:
    st.error("L'immeuble doit être construit avant la vente.")
else:
    prix = estimer(modele, gares[commune][gare], commune, gare, surface, annee_construction, minutes, plan,
                   renove, annee, trimestre)
    st.metric("Prix estimé", f"{prix / 1e6:,.1f} millions de yens")
    st.write(f"Soit **{prix / surface / 1e3:,.0f} milliers de yens par m²**. "
             f"La moitié des ventes réelles tombent entre **{prix * fourchette['bas'] / 1e6:,.1f}** et "
             f"**{prix * fourchette['haut'] / 1e6:,.1f} M¥** pour une telle estimation.")
    st.caption(f"{gares[commune][gare]['ventes']} ventes connues près de la gare {gare}. Le zonage et la densité "
               "sont ceux les plus fréquents autour de cette gare.")
