"""Outils communs aux deux notebooks : style des graphiques, tests et schémas.

- `style()` règle matplotlib (couleurs, grille discrète, tailles de texte).
- `verifier()` compare une valeur à celle attendue et garde une trace ; `bilan_tests()` affiche le bilan.
- `schema()` dessine un schéma « boîtes et flèches » (workflow, architecture, blocs HDFS...).
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Palette catégorielle (ordre fixe, jamais recyclé) et encres, validées pour fond clair.
BLEU, ORANGE, VERT_EAU, JAUNE, ROSE, VERT, VIOLET, ROUGE = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
PALETTE = [BLEU, ORANGE, VERT_EAU, JAUNE, ROSE, VERT, VIOLET, ROUGE]
FOND, ENCRE, ENCRE_2, GRIS, GRILLE, AXE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SEQUENTIEL = "Blues"          # une seule teinte, du clair au foncé, pour les grandeurs

# Couleurs pâles pour le fond des boîtes des schémas, une par famille d'étape.
PALE = {"bleu": "#cde2fb", "orange": "#fbdccd", "vert": "#c9eedf", "jaune": "#fbe9bf",
        "violet": "#dcd8f6", "gris": "#ecebe6", "rose": "#f8dbe6"}
BORD = {"bleu": BLEU, "orange": ORANGE, "vert": VERT_EAU, "jaune": "#c98500",
        "violet": VIOLET, "gris": GRIS, "rose": ROSE}


def style():
    plt.rcParams.update({
        "figure.facecolor": FOND, "axes.facecolor": FOND, "savefig.facecolor": FOND,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "axes.edgecolor": AXE, "axes.labelcolor": ENCRE_2, "axes.titlecolor": ENCRE,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelsize": 11, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRILLE, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "xtick.color": GRIS, "ytick.color": GRIS, "xtick.labelcolor": ENCRE_2, "ytick.labelcolor": ENCRE_2,
        "legend.frameon": False, "legend.fontsize": 10, "lines.linewidth": 2,
        "figure.dpi": 100, "font.size": 10,
    })


# ---------------------------------------------------------------- tests
TESTS = []


def verifier(nom, condition, detail=""):
    """Enregistre un test : `condition` doit être vraie. `detail` explique la valeur obtenue."""
    ok = bool(condition)
    TESTS.append({"test": nom, "résultat": "OK" if ok else "ÉCHEC", "détail": str(detail)[:90]})
    print(("OK     " if ok else "ÉCHEC  ") + nom + (f"  ({detail})" if detail else ""))


def bilan_tests():
    import pandas as pd
    t = pd.DataFrame(TESTS)
    n_ok = (t["résultat"] == "OK").sum()
    print(f"{n_ok} tests réussis sur {len(t)}")
    return t


# ---------------------------------------------------------------- schémas
def schema(noeuds, fleches=(), taille=(12, 3), titre=None, cadres=()):
    """Dessine un schéma.

    noeuds  : liste de dict(id, x, y, texte, [sous], [couleur], [l], [h])
              x, y = centre de la boîte (coordonnées libres) ; l, h = largeur, hauteur.
    fleches : liste de (id_depart, id_arrivee) ou (id_depart, id_arrivee, "étiquette").
    cadres  : liste de dict(x0, y0, x1, y1, texte, [couleur]) : rectangles en pointillés qui regroupent.
    """
    fig, ax = plt.subplots(figsize=taille)
    ax.set_axis_off()
    boites = {}
    for c in cadres:
        coul = BORD.get(c.get("couleur", "gris"), GRIS)
        ax.add_patch(FancyBboxPatch((c["x0"], c["y0"]), c["x1"] - c["x0"], c["y1"] - c["y0"],
                                    boxstyle="round,pad=0.02,rounding_size=0.15", fill=False,
                                    ec=coul, lw=1.3, ls=(0, (4, 3))))
        ax.text(c["x0"] + 0.1, c["y1"] - 0.1, c["texte"], ha="left", va="top", fontsize=9.5,
                color=coul, fontweight="bold")
    for n in noeuds:
        l, h = n.get("l", 1.6), n.get("h", 0.9)
        coul = n.get("couleur", "bleu")
        x0, y0 = n["x"] - l / 2, n["y"] - h / 2
        ax.add_patch(FancyBboxPatch((x0, y0), l, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=PALE[coul], ec=BORD[coul], lw=1.6))
        if n.get("sous"):
            ax.text(n["x"], n["y"] + h * 0.16, n["texte"], ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=ENCRE)
            ax.text(n["x"], n["y"] - h * 0.2, n["sous"], ha="center", va="center", fontsize=8.5,
                    color=ENCRE_2, linespacing=1.15)
        else:
            ax.text(n["x"], n["y"], n["texte"], ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=ENCRE)
        boites[n["id"]] = (x0, y0, l, h)
    for f in fleches:
        a, b = boites[f[0]], boites[f[1]]
        ca = (a[0] + a[2] / 2, a[1] + a[3] / 2)
        cb = (b[0] + b[2] / 2, b[1] + b[3] / 2)
        pa, pb = _bord(a, cb), _bord(b, ca)
        ax.add_patch(FancyArrowPatch(pa, pb, arrowstyle="-|>", mutation_scale=14, color=ENCRE_2,
                                     lw=1.4, shrinkA=3, shrinkB=3))
        if len(f) > 2:
            ax.text((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2 + 0.12, f[2], ha="center", va="bottom",
                    fontsize=8.5, color=ENCRE_2, style="italic")
    xs = [b[0] for b in boites.values()] + [b[0] + b[2] for b in boites.values()] + \
         [c["x0"] for c in cadres] + [c["x1"] for c in cadres]
    ys = [b[1] for b in boites.values()] + [b[1] + b[3] for b in boites.values()] + \
         [c["y0"] for c in cadres] + [c["y1"] for c in cadres]
    ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2)
    ax.set_ylim(min(ys) - 0.2, max(ys) + 0.2)
    ax.set_aspect("equal")
    if titre:
        ax.set_title(titre, loc="left")
    plt.tight_layout()
    plt.show()


def _bord(boite, cible):
    """Point du bord de `boite` sur le segment qui va de son centre vers `cible`."""
    x0, y0, l, h = boite
    cx, cy = x0 + l / 2, y0 + h / 2
    dx, dy = cible[0] - cx, cible[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    tx = (l / 2) / abs(dx) if dx else float("inf")
    ty = (h / 2) / abs(dy) if dy else float("inf")
    t = min(tx, ty)
    return cx + dx * t, cy + dy * t


def workflow(actif=None, taille=(13, 1.9)):
    """Le workflow du TP. `actif` = numéro de l'étape en cours (1 à 7), mise en évidence."""
    etapes = ["Data", "EDA", "Prétraitement", "Transformation", "ML", "Évaluation", "Déploiement"]
    noeuds = []
    for i, e in enumerate(etapes, start=1):
        coul = "orange" if i == actif else ("bleu" if actif is None or i < actif else "gris")
        noeuds.append(dict(id=i, x=i * 1.85, y=0, texte=e, couleur=coul, l=1.55, h=0.75))
    schema(noeuds, [(i, i + 1) for i in range(1, 7)], taille=taille)
