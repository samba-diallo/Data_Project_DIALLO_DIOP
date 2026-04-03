"""
Page principale d'analyse du dashboard.
Contient l'histogramme, la carte géolocalisée et les filtres interactifs.
Au moins un graphique DOIT être dynamique (callback).

Doc cours callbacks : https://perso.esiee.fr/.../python-28-dash.html#interaction-simple
Doc Dash callbacks  : https://dash.plotly.com/basic-callbacks
"""

from dash import html, dcc, Input, Output
from src.components.histogram import create_histogram
from src.components.geomap import create_geomap
from src.utils.common_functions import load_cleaned_data, filter_data


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout de la page d'analyse.
    Inclut les filtres (Dropdown, Slider), l'histogramme et la carte
    géolocalisée dans un agencement responsive.

    Returns:
        html.Div: Layout complet de la page d'analyse.
    """
    # TODO: ajouter dcc.Dropdown, dcc.Graph(id="histogram"), dcc.Graph(id="geomap")
    pass


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks Dash qui rendent les graphiques dynamiques.
    Met à jour l'histogramme et la carte en fonction des filtres sélectionnés.

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """
    # TODO: @app.callback(Output("histogram","figure"), Input("filtre","value"))
    # TODO: def update_histogram(selected_value): ...
    pass
