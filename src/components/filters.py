"""
Composant 'barre de filtres' utilisé sur la page Explorer.
Trois contrôles synchronisés : plage d'années, régions et types de structure.
Les valeurs sélectionnées alimentent les callbacks qui mettent à jour
la carte choroplèthe, l'histogramme et la décomposition par scope.

Doc Dash core components : https://dash.plotly.com/dash-core-components
"""

import pandas as pd

from dash import html, dcc

# DashIconify : icônes SVG pour décorer les labels de filtres
from dash_iconify import DashIconify

# Période officielle (2010-2025) - source de vérité unique
from src.utils.common_functions import YEAR_MIN, YEAR_MAX


# ─────────────────────────────────────────────────────────────────
# IDs des filtres (centralisés ici pour être référencés par les
# callbacks dans analysis.py sans risque de typo)
# ─────────────────────────────────────────────────────────────────

FILTER_YEAR_RANGE_ID = "filter-year-range"
FILTER_REGION_ID = "filter-region"
FILTER_STRUCTURE_ID = "filter-structure"
FILTER_RESET_BTN_ID = "filter-reset"


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

def create_filters_bar(df: pd.DataFrame) -> html.Div:
    """
    Construit la barre de filtres affichée en haut de la page Explorer.
    Reçoit le DataFrame complet pour calculer dynamiquement les options
    disponibles (régions et types présents dans les données).

    Args:
        df (pd.DataFrame): DataFrame nettoyé qui sert à peupler les options.

    Returns:
        html.Div: Conteneur Dash avec les 3 filtres + bouton de reset.
    """
    # Bornes du slider d'années : on utilise les CONSTANTES officielles
    # (2010-2025) pour garantir la cohérence visuelle imposée par
    # Design.md, indépendamment des éventuelles années marginales
    # encore présentes dans le dataset après filtrage.
    annee_min = YEAR_MIN
    annee_max = YEAR_MAX

    # Liste triée des régions disponibles (pour Dropdown).
    # On exclut explicitement les NaN avec dropna().
    regions = sorted(df["region"].dropna().unique())

    # Liste triée des types de structure (4-5 valeurs typiques).
    structures = sorted(df["type_structure"].dropna().unique())

    return html.Div(
        className="filters-bar",
        children=[
            # Mini titre éditorial pour ancrer la zone de filtres dans
            # la hiérarchie visuelle de la page (cohérence avec Design.md
            # qui demande des filtres immédiatement visibles et identifiables).
            html.Div(
                className="filters-bar-header",
                children=[
                    DashIconify(
                        icon="tabler:adjustments-horizontal",
                        width=18,
                        color="#1F3A2C",
                    ),
                    html.Span("Filtres d'exploration", className="filters-bar-title"),
                ],
            ),
            # Container interne pour la grille responsive Bootstrap
            html.Div(
                className="row g-4 align-items-end",
                children=[
                    _build_year_filter(annee_min, annee_max),
                    _build_region_filter(regions),
                    _build_structure_filter(structures),
                    _build_reset_button(),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# Helpers privés - construction de chaque filtre
# ─────────────────────────────────────────────────────────────────

def _build_year_filter(annee_min: int, annee_max: int) -> html.Div:
    """Slider de plage d'années (RangeSlider). Sélection d'un intervalle."""
    return html.Div(
        # col-md-4 = un tiers de la largeur sur desktop, pleine largeur mobile
        className="col-md-4",
        children=[
            # Label avec icône à gauche pour identification rapide
            _build_label("tabler:calendar-stats", "Plage d'années"),

            # dcc.RangeSlider : double curseur permettant de sélectionner
            # une plage continue d'années sur la période officielle 2010-2025.
            dcc.RangeSlider(
                id=FILTER_YEAR_RANGE_ID,
                min=annee_min,
                max=annee_max,
                # value : valeur initiale = plage complète
                value=[annee_min, annee_max],
                step=1,
                # marks : on affiche un label tous les 3 ans (2010, 2013,
                # 2016, 2019, 2022, 2025) pour une lecture sans encombrement.
                # Les ticks intermédiaires restent présents (step=1).
                marks={
                    year: {
                        "label": str(year),
                        "style": {
                            "fontSize": "11px",
                            "color": "#6B6B6B",
                            "fontFamily": "DM Sans, sans-serif",
                        },
                    }
                    for year in range(annee_min, annee_max + 1, 3)
                },
                # tooltip : affiche la valeur courante au survol du curseur.
                tooltip={"placement": "bottom", "always_visible": False},
                # className personnalisée pour overrider le style par défaut
                className="filter-slider",
            ),
        ],
    )


def _build_region_filter(regions: list[str]) -> html.Div:
    """Dropdown multi-select des régions disponibles."""
    return html.Div(
        className="col-md-3",
        children=[
            _build_label("tabler:map", "Régions"),
            dcc.Dropdown(
                id=FILTER_REGION_ID,
                # options : liste de dicts {label, value} attendus par Dash
                options=[{"label": r, "value": r} for r in regions],
                # multi=True : permet de sélectionner plusieurs régions
                # simultanément (case à cocher style chip)
                multi=True,
                placeholder="Toutes les régions",
                # value=None par défaut : aucune sélection -> on prendra
                # toutes les régions dans le callback (cf. analysis.py)
                value=None,
                # className personnalisée + clearable pour vider d'un clic
                className="filter-dropdown",
                clearable=True,
            ),
        ],
    )


def _build_structure_filter(structures: list[str]) -> html.Div:
    """Dropdown multi-select des types de structure (Entreprise, Public...)."""
    return html.Div(
        className="col-md-3",
        children=[
            _build_label("tabler:building-skyscraper", "Types de structure"),
            dcc.Dropdown(
                id=FILTER_STRUCTURE_ID,
                options=[{"label": s, "value": s} for s in structures],
                multi=True,
                placeholder="Tous les types",
                value=None,
                className="filter-dropdown",
                clearable=True,
            ),
        ],
    )


def _build_reset_button() -> html.Div:
    """Bouton 'Réinitialiser' qui remet tous les filtres à leur valeur initiale."""
    return html.Div(
        className="col-md-2",
        children=[
            html.Button(
                # n_clicks initialisé à 0 : le callback détectera les clics
                # via l'incrémentation de cette propriété.
                id=FILTER_RESET_BTN_ID,
                n_clicks=0,
                className="filter-reset-btn",
                children=[
                    DashIconify(
                        icon="tabler:refresh",
                        width=16,
                        # marginRight pour espacer l'icône du texte
                        style={"marginRight": "8px"},
                    ),
                    "Réinitialiser",
                ],
            ),
        ],
    )


def _build_label(icon: str, text: str) -> html.Label:
    """Label de filtre avec icône à gauche, style sobre."""
    return html.Label(
        className="filter-label d-flex align-items-center gap-2",
        children=[
            DashIconify(icon=icon, width=14, color="#6B6B6B"),
            html.Span(text),
        ],
    )
