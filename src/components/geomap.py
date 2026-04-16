"""
Composant carte géolocalisée interactive.
Livrable OBLIGATOIRE selon le cahier des charges du projet.

Doc cours  : https://perso.esiee.fr/.../python-27-plotly.html#plotly-express
Doc Plotly : https://plotly.com/python/maps/
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_geomap(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    value_col: str
) -> go.Figure:
    """
    Génère et retourne une carte géolocalisée Plotly (scatter_mapbox
    ou choropleth selon la nature des données).

    Args:
        df (pd.DataFrame): DataFrame contenant les données géolocalisées.
        lat_col (str): Nom de la colonne contenant les latitudes.
        lon_col (str): Nom de la colonne contenant les longitudes.
        value_col (str): Nom de la colonne numérique représentée par la couleur/taille.

    Returns:
        go.Figure: Figure Plotly prête à être passée à un composant dcc.Graph.
    """
    # TODO: px.scatter_mapbox(df, lat=lat_col, lon=lon_col, color=value_col, ...)
    pass
