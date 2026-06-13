"""
Composant de barre de filtres utilisé pour le filtrage de la page Explorer.
Il permet de filtrer les données par plage d'années, par régions, et par types de structure.
"""

import pandas as pd
from dash import html, dcc
from dash_iconify import DashIconify

# Importation des constantes de bornes temporelles officielles
from src.utils.common_functions import YEAR_MIN, YEAR_MAX

# Définition des identifiants (IDs) uniques des composants Dash.
# Ils servent à lier ces filtres aux callbacks du tableau de bord.
FILTER_YEAR_RANGE_ID = "filter-year-range"
FILTER_REGION_ID = "filter-region"
FILTER_STRUCTURE_ID = "filter-structure"
FILTER_RESET_BTN_ID = "filter-reset"


def create_filters_bar(df: pd.DataFrame) -> html.Div:
    """
    Génère la structure de la barre de filtres de la page Explorer.
    Calcule dynamiquement les options de filtres à partir du DataFrame des données.

    Args:
        df (pd.DataFrame): Données nettoyées servant à extraire les options possibles.

    Returns:
        html.Div: Conteneur HTML de la barre de filtres.
    """
    # Utilisation des constantes officielles pour les années minimales et maximales
    annee_min = YEAR_MIN
    annee_max = YEAR_MAX

    # Extraction de la liste unique des régions triée par ordre alphabétique
    # dropna() permet d'exclure les données manquantes
    regions = sorted(df["region"].dropna().unique())

    # Extraction de la liste unique des types de structures (Entreprise, Public, etc.)
    structures = sorted(df["type_structure"].dropna().unique())

    return html.Div(
        className="filters-bar",
        children=[
            # En-tête de la barre de filtres
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
            # Grille de composants Bootstrap (row) regroupant les différents filtres
            html.Div(
                className="row g-4 align-items-end",
                children=[
                    _build_year_filter(annee_min, annee_max), # Sélecteur d'années
                    _build_region_filter(regions),           # Sélecteur de régions
                    _build_structure_filter(structures),     # Sélecteur de structures
                    _build_reset_button(),                   # Bouton de remise à zéro
                ],
            ),
        ],
    )


def _build_year_filter(annee_min: int, annee_max: int) -> html.Div:
    """
    Construit le filtre RangeSlider permettant de choisir une plage d'années.

    Args:
        annee_min (int): Année minimale du slider.
        annee_max (int): Année maximale du slider.

    Returns:
        html.Div: Bloc HTML du filtre.
    """
    return html.Div(
        className="col-md-4",
        children=[
            # Titre du filtre
            _build_label("tabler:calendar-stats", "Plage d'années"),

            # RangeSlider Dash permettant de sélectionner un intervalle (début - fin)
            dcc.RangeSlider(
                id=FILTER_YEAR_RANGE_ID,
                min=annee_min,
                max=annee_max,
                value=[annee_min, annee_max],
                step=1,
                # Génération des graduations textuelles tous les 3 ans
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
                # Infobulle affichant la valeur au survol du curseur
                tooltip={"placement": "bottom", "always_visible": False},
                className="filter-slider",
            ),
        ],
    )


def _build_region_filter(regions: list[str]) -> html.Div:
    """
    Construit le menu déroulant (Dropdown) de sélection multiple des régions.

    Args:
        regions (list[str]): Liste des régions à proposer en option.

    Returns:
        html.Div: Bloc HTML du filtre.
    """
    return html.Div(
        className="col-md-3",
        children=[
            # Titre du filtre
            _build_label("tabler:map", "Régions"),
            # Menu déroulant Dash avec sélection multiple (multi=True)
            dcc.Dropdown(
                id=FILTER_REGION_ID,
                options=[{"label": r, "value": r} for r in regions],
                multi=True,
                placeholder="Toutes les régions",
                value=None,
                className="filter-dropdown",
                clearable=True, # Permet d'effacer la sélection d'un clic
            ),
        ],
    )


def _build_structure_filter(structures: list[str]) -> html.Div:
    """
    Construit le menu déroulant (Dropdown) pour filtrer par type de structure.

    Args:
        structures (list[str]): Liste des structures à proposer en option.

    Returns:
        html.Div: Bloc HTML du filtre.
    """
    return html.Div(
        className="col-md-3",
        children=[
            # Titre du filtre
            _build_label("tabler:building-skyscraper", "Types de structure"),
            # Menu déroulant Dash multi-sélection
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
    """
    Construit le bouton permettant de réinitialiser tous les filtres actifs.

    Returns:
        html.Div: Bloc HTML contenant le bouton.
    """
    return html.Div(
        className="col-md-2",
        children=[
            # Bouton classique capturé par Dash via l'argument n_clicks
            html.Button(
                id=FILTER_RESET_BTN_ID,
                n_clicks=0,
                className="filter-reset-btn",
                children=[
                    DashIconify(
                        icon="tabler:refresh",
                        width=16,
                        style={"marginRight": "8px"},
                    ),
                    "Réinitialiser",
                ],
            ),
        ],
    )


def _build_label(icon: str, text: str) -> html.Label:
    """
    Génère un label textuel avec une petite icône alignée sur sa gauche.

    Args:
        icon (str): Identifiant de l'icône SVG.
        text (str): Texte du label.

    Returns:
        html.Label: Label HTML configuré.
    """
    return html.Label(
        className="filter-label d-flex align-items-center gap-2",
        children=[
            DashIconify(icon=icon, width=14, color="#6B6B6B"),
            html.Span(text),
        ],
    )
