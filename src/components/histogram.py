"""
Composant histogramme interactif.
Livrable OBLIGATOIRE selon le cahier des charges du projet.

Doc cours  : https://perso.esiee.fr/.../python-27-plotly.html#creation-d-un-graphique-elementaire
Doc Plotly : https://plotly.com/python/histograms/
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_histogram(df: pd.DataFrame, x_col: str, title: str) -> go.Figure:
    """
    Génère et retourne un histogramme Plotly interactif.
    La colonne x_col doit être numérique et non catégorielle.

    Args:
        df (pd.DataFrame): DataFrame contenant les données à visualiser.
        x_col (str): Nom de la colonne numérique à représenter sur l'axe X.
        title (str): Titre du graphique affiché au-dessus de la figure.

    Returns:
        go.Figure: Figure Plotly prête à être passée à un composant dcc.Graph.
    """
    # TODO: px.histogram(df, x=x_col, title=title, labels={x_col: "..."})
    pass
