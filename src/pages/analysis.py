"""
Page principale d'analyse du dashboard - 'Explorer'.
Cœur de l'application : barre de filtres synchronisée + carte choroplèthe
des régions françaises + histogramme dynamique des émissions + décomposition
Scope 1/2/3 par type de structure.

Au moins un graphique DOIT être dynamique (callback) selon le cahier des
charges. Ici les TROIS graphes sont synchronisés sur les mêmes filtres.

Doc Dash callbacks : https://dash.plotly.com/basic-callbacks
"""

from dash import html, dcc, Input, Output, State

# Composants partagés
from src.components.header import create_header
from src.components.filters import (
    create_filters_bar,
    FILTER_YEAR_RANGE_ID,
    FILTER_REGION_ID,
    FILTER_STRUCTURE_ID,
    FILTER_RESET_BTN_ID,
)
from src.components.geomap import create_geomap
from src.components.histogram import create_histogram
from src.components.scope_breakdown import create_scope_breakdown

# Loader + filtre des données
from src.utils.common_functions import load_cleaned_data, filter_data


# ─────────────────────────────────────────────────────────────────
# IDs Dash des graphiques (référencés par les callbacks)
# ─────────────────────────────────────────────────────────────────

GRAPH_GEOMAP_ID = "graph-geomap"
GRAPH_HISTOGRAM_ID = "graph-histogram"
GRAPH_SCOPE_ID = "graph-scope-breakdown"


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit le layout de la page Explorer : header + barre de filtres
    + grille (carte + histogramme) + section Scope 1/2/3.

    Returns:
        html.Div: Layout complet de la page Explorer.
    """
    # Chargement des données nettoyées pour peupler les options de filtres
    # (régions disponibles, types de structure, plage d'années).
    df = load_cleaned_data()

    # Options Plotly partagées par tous les graphes : on retire la barre
    # d'outils Plotly par défaut (zoom/pan/etc.) pour un rendu B2B propre.
    plotly_config = {"displayModeBar": False, "displaylogo": False}

    return html.Div(
        className="page-container",
        children=[
            # En-tête éditorial (sans chiffres dynamiques cette fois,
            # car la page propose une exploration interactive).
            create_header(
                kicker="Explorer",
                title="Explorer les Bilans GES",
                subtitle=(
                    "Filtrez par région, année et type de structure pour "
                    "découvrir la distribution des émissions et leur "
                    "répartition géographique sur le territoire français."
                ),
            ),

            # Barre de filtres sticky en haut (Année, Régions, Types, Reset)
            create_filters_bar(df),

            # Grille 60/40 : carte choroplèthe à gauche, histogramme à droite.
            # Sur mobile/tablette, les deux s'empilent (CSS media query).
            html.Div(
                className="explorer-grid",
                children=[
                    # Carte
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H2(
                                "Cartographie régionale des émissions",
                                className="section-title",
                            ),
                            html.P(
                                "Total des émissions BEGES déclarées par "
                                "région française. Survolez une région pour "
                                "voir le détail.",
                                className="section-subtitle",
                            ),
                            # dcc.Loading : affiche un spinner pendant que
                            # le callback recalcule la figure (UX fluide).
                            dcc.Loading(
                                type="circle",
                                color="#1F3A2C",
                                children=dcc.Graph(
                                    id=GRAPH_GEOMAP_ID,
                                    config=plotly_config,
                                ),
                            ),
                        ],
                    ),
                    # Histogramme
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H2(
                                "Distribution des émissions",
                                className="section-title",
                            ),
                            html.P(
                                "Échelle logarithmique pour absorber la "
                                "très forte asymétrie de la distribution. "
                                "Médiane et moyenne en lignes verticales.",
                                className="section-subtitle",
                            ),
                            dcc.Loading(
                                type="circle",
                                color="#1F3A2C",
                                children=dcc.Graph(
                                    id=GRAPH_HISTOGRAM_ID,
                                    config=plotly_config,
                                ),
                            ),
                        ],
                    ),
                ],
            ),

            # Section Scope 1/2/3 sur toute la largeur (barres horizontales,
            # mieux étalées en pleine largeur).
            html.Section(
                className="content-section",
                children=[
                    html.H2(
                        "Décomposition par scope BEGES",
                        className="section-title",
                    ),
                    html.P(
                        "Répartition des émissions Scope 1 (directes), "
                        "Scope 2 (énergie achetée) et Scope 3 (chaîne de "
                        "valeur) par type de structure déclarante.",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            dcc.Loading(
                                type="circle",
                                color="#1F3A2C",
                                children=dcc.Graph(
                                    id=GRAPH_SCOPE_ID,
                                    config=plotly_config,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# CALLBACKS - graphes dynamiques pilotés par les filtres
# ─────────────────────────────────────────────────────────────────

def register_callbacks(app) -> None:
    """
    Enregistre les callbacks Dash de la page Explorer.
    Deux callbacks :
      1. Mise à jour des 3 graphes en fonction des filtres
         (synchronisation simultanée).
      2. Bouton 'Réinitialiser' qui remet les filtres à leur valeur initiale.

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """

    # ── Callback principal : filtres -> 3 graphes ────────────────
    # Output multiple en liste : Dash met à jour les 3 graphes en
    # parallèle à chaque changement de filtre. Plus efficace que
    # 3 callbacks séparés (les 3 partagent le DataFrame filtré).
    @app.callback(
        [
            Output(GRAPH_GEOMAP_ID, "figure"),
            Output(GRAPH_HISTOGRAM_ID, "figure"),
            Output(GRAPH_SCOPE_ID, "figure"),
        ],
        [
            Input(FILTER_YEAR_RANGE_ID, "value"),
            Input(FILTER_REGION_ID, "value"),
            Input(FILTER_STRUCTURE_ID, "value"),
        ],
    )
    def update_charts(year_range, regions, structures):
        """Recalcule les 3 graphes à chaque modification des filtres."""
        # Chargement des données : on relit le CSV à chaque appel.
        # Le CSV est petit (~5 Mo) donc la lecture est instantanée.
        # Pour optimiser plus tard : @lru_cache sur load_cleaned_data().
        df = load_cleaned_data()

        # Filtrage par plage d'années : RangeSlider renvoie [min, max].
        # On filtre via une condition booléenne pandas (between inclusif).
        if year_range and len(year_range) == 2:
            df = df[df["annee_reporting"].between(year_range[0], year_range[1])]

        # Filtrage par régions et types via filter_data() qui gère
        # nativement les listes (None ou vide = pas de filtre, isin sinon).
        df = filter_data(df, region=regions, type_structure=structures)

        # Construction des 3 figures avec le DataFrame filtré.
        geomap_fig = create_geomap(df)
        histogram_fig = create_histogram(df)
        scope_fig = create_scope_breakdown(df)

        return geomap_fig, histogram_fig, scope_fig

    # ── Callback du bouton 'Réinitialiser' ───────────────────────
    # Remet les 3 filtres à leur valeur initiale au clic du bouton.
    @app.callback(
        [
            Output(FILTER_YEAR_RANGE_ID, "value"),
            Output(FILTER_REGION_ID, "value"),
            Output(FILTER_STRUCTURE_ID, "value"),
        ],
        Input(FILTER_RESET_BTN_ID, "n_clicks"),
        # prevent_initial_call=True : évite que le callback se déclenche
        # au chargement initial (sinon il écraserait les valeurs par défaut).
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        """Réinitialise les filtres aux valeurs par défaut au clic du bouton."""
        # Recalcul des bornes d'années pour rester cohérent avec le dataset.
        df = load_cleaned_data()
        annee_min = int(df["annee_reporting"].min())
        annee_max = int(df["annee_reporting"].max())

        # On retourne : plage complète d'années, aucune région, aucun type.
        # None pour les Dropdown multi = état vide = pas de filtre actif.
        return [annee_min, annee_max], None, None
