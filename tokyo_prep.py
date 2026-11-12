"""Transformation des ventes d'appartements de Tokyo en variables pour le modèle.

Le notebook `tokyo_immo.ipynb` et l'appli `app_tokyo.py` utilisent la même fonction `variables()` :
le modèle déployé voit donc exactement les mêmes calculs qu'à l'entraînement.
"""
import re

import numpy as np
import pandas as pd

# Colonnes brutes attendues en entrée (noms du fichier Kaggle).
COLONNES_BRUTES = ["Municipality", "NearestStation", "MinTimeToNearestStation", "Area", "FloorPlan",
                   "BuildingYear", "Structure", "Renovation", "CityPlanning", "CoverageRatio",
                   "FloorAreaRatio", "Year", "Quarter"]

NUMERIQUES = ["surface_m2", "age_ans", "minutes_gare", "nb_pieces", "salon", "salle_a_manger",
              "cuisine", "piece_en_plus", "renove", "taux_emprise", "taux_densite", "date",
              "arrondissement_23"]
CATEGORIELLES = ["commune", "structure", "zonage"]
GARE = ["gare"]
VARIABLES = NUMERIQUES + CATEGORIELLES + GARE


def nb_pieces(plan):
    """'3LDK' -> 3 ; 'Studio Apartment' -> 1 ; 'Open Floor', 'Duplex' ou vide -> NaN."""
    if not isinstance(plan, str):
        return np.nan
    m = re.match(r"(\d+)", plan)
    if m:
        return float(m.group(1))
    return 1.0 if plan == "Studio Apartment" else np.nan


def _lettre(plan, lettre):
    """Le plan japonais contient-il L (salon), D (salle à manger), K (cuisine) ou +S (pièce en plus) ?"""
    if not isinstance(plan, str) or not re.match(r"\d", plan):
        return np.nan
    if lettre == "S":
        return float("+S" in plan)
    return float(lettre in plan.split("+")[0])


def structure(s):
    """RC (béton armé), SRC (béton + acier), sinon 'autre'."""
    if s in ("RC", "SRC"):
        return s
    return "autre" if isinstance(s, str) else np.nan


def variables(df):
    """Construit le tableau de variables du modèle à partir des colonnes brutes."""
    out = pd.DataFrame(index=df.index)
    out["surface_m2"] = df["Area"].astype(float)
    out["age_ans"] = (df["Year"] - df["BuildingYear"]).astype(float)
    out["minutes_gare"] = df["MinTimeToNearestStation"].astype(float)
    plans = df["FloorPlan"]
    out["nb_pieces"] = plans.map(nb_pieces)
    out["salon"] = plans.map(lambda p: _lettre(p, "L"))
    out["salle_a_manger"] = plans.map(lambda p: _lettre(p, "D"))
    out["cuisine"] = plans.map(lambda p: _lettre(p, "K"))
    out["piece_en_plus"] = plans.map(lambda p: _lettre(p, "S"))
    out["renove"] = (df["Renovation"] == "Done").astype(float)
    out["taux_emprise"] = df["CoverageRatio"].astype(float)
    out["taux_densite"] = df["FloorAreaRatio"].astype(float)
    out["date"] = df["Year"] + (df["Quarter"] - 1) / 4
    out["arrondissement_23"] = df["Municipality"].str.endswith("Ward").astype(float)
    out["commune"] = df["Municipality"]
    out["structure"] = df["Structure"].map(structure)
    out["zonage"] = df["CityPlanning"]
    out["gare"] = df["NearestStation"]
    # Les encodeurs de scikit-learn veulent des catégories en texte (NaN -> "inconnu").
    for c in CATEGORIELLES + GARE:
        out[c] = out[c].fillna("inconnu").astype(str)
    return out[VARIABLES]
