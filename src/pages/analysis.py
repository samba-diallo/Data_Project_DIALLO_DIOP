"""
Page principale d'analyse du dashboard - 'Explorer'.
Contient l'histogramme, la carte choroplethe et les filtres interactifs.
Au moins un graphique DOIT etre dynamique (callback) - exigence du prof.

Doc Dash callbacks : https://dash.plotly.com/basic-callbacks
"""

from dash import html

# Import du header editorial commun a toutes les pages
from src.components.header import create_header


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout de la page d'analyse.
    Comportera (Phase 4) les filtres (Dropdown, Slider), l'histogramme
    et la carte choroplèthe dans un agencement responsive.

    Returns:
        html.Div: Layout complet de la page d'analyse.
    """
    return html.Div(
        className="page-container",
        children=[
            # Header éditorial : positionne la page comme l'outil principal
            # d'exploration des données.
            create_header(
                kicker="Explorer",
                title="Explorer les Bilans GES",
                subtitle=(
                    "Filtrez par région, année et type de structure pour "
                    "découvrir la distribution des émissions et leur "
                    "répartition géographique sur le territoire français."
                ),
            ),
            # Placeholder : sera remplacé par filters + carte + histogramme
            # + décomposition Scope 1/2/3 en Phase 4.
            html.Div(
                "Contenu à venir : carte choroplèthe, histogramme dynamique, "
                "décomposition des émissions par scope.",
                style={"padding": "2rem", "color": "var(--color-text-muted)"},
            ),
        ],
    )


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks Dash qui rendent les graphiques dynamiques.
    Sera implémenté en Phase 4 (filtres -> mise à jour des graphes).

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """
    pass
