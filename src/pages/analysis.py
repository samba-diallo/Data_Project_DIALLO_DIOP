"""
Page 'Explorer' du dashboard GES Insight.

Structure :
1. Barre de filtres sticky (année, régions, types structures, reset)
2. Heat timeline (heatmap d'intensité annuelle)
3. Bandeau KPI (5 indicateurs contextuels)
4. Carte choroplèthe (France complète toujours visible)
5. Inspecteur d'organisations (recherche + détail bilan)
6. Histogramme multi-vues (top organisations, paliers, secteurs)
7. Décomposition Scope 1/2/3 (top 15 organisations)

Architecture de filtrage à 2 niveaux :
- df_year_struct : filtres année + structure (toutes régions visibles)
  -> pour la carte et heat timeline (contexte national)
- df_full : df_year_struct + filtre région (sélection complète)
  -> pour histogramme, scope breakdown, statistiques principales
"""

import pandas as pd

from dash import html, dcc, Input, Output

# DashIconify : icônes SVG pour le bandeau de stats
from dash_iconify import DashIconify

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
from src.components.histogram import (
    create_histogram,
    VIEW_TOP_ORGS,
    VIEW_BINS,
    VIEW_SECTORS,
)
from src.components.scope_breakdown import create_scope_breakdown
from src.components.heat_timeline import create_heat_timeline
from src.components.organization_inspector import (
    create_inspector,
    build_org_detail,
    INSPECTOR_DROPDOWN_ID,
    INSPECTOR_DETAIL_ID,
)

# Loader + filtre des données + bornes de période officielles
from src.utils.common_functions import (
    load_cleaned_data,
    filter_data,
    YEAR_MIN,
    YEAR_MAX,
)


GRAPH_GEOMAP_ID = "graph-geomap"
GRAPH_HISTOGRAM_ID = "graph-histogram"
GRAPH_HEAT_TIMELINE_ID = "graph-heat-timeline"
STATS_BANNER_ID = "explorer-stats-banner"
HISTOGRAM_VIEW_TOGGLE_ID = "histogram-view-toggle"


# ─────────────────────────────────────────────────────────────────
# Helper - bandeau de stats contextuelles synchronisé sur les filtres
# ─────────────────────────────────────────────────────────────────

def _build_stats_banner(
    df_full_selection: pd.DataFrame,
    df_year_struct: pd.DataFrame,
    selected_range: tuple[int, int],
) -> list:
    """
    Construit le bandeau de 5 indicateurs KPI synchronisés avec les filtres.

    Indicateurs :
    1. Nombre de bilans dans la sélection
    2. Nombre d'organisations distinctes (SIREN)
    3. Émissions cumulées
    4. Tendance d'évolution entre année début et année fin
    5. Région la plus émettrice (sur le périmètre national filtré)

    Args:
        df_full_selection : DataFrame avec tous les filtres appliqués
        df_year_struct : DataFrame filtrés par année + structure uniquement
        selected_range : Tuple (annee_debut, annee_fin) pour tendance

    Returns:
        list : Éléments html.Div à afficher dans le bandeau
    """
    if df_full_selection.empty:
        return [
            html.Div(
                "Aucun bilan ne correspond aux filtres sélectionnés.",
                className="stats-banner-empty",
            ),
        ]

    nb_bilans = len(df_full_selection)
    nb_orgs = df_full_selection["siren"].nunique()
    total_t = float(df_full_selection["total_emissions"].sum())

    bilans_str = f"{nb_bilans:,}".replace(",", " ")
    orgs_str = f"{nb_orgs:,}".replace(",", " ")
    total_str = _format_emissions(total_t)

    evolution_value, evolution_label, evolution_icon, evolution_class = (
        _compute_trend(df_year_struct, selected_range)
    )

    if not df_year_struct.empty:
        top_region = (
            df_year_struct.groupby("region")["total_emissions"]
              .sum()
              .idxmax()
        )
    else:
        top_region = "—"

    return [
        _stat_item("tabler:file-text", "Bilans", bilans_str, "dans la sélection"),
        _stat_item("tabler:building", "Organisations", orgs_str, "SIREN distincts"),
        _stat_item("tabler:cloud", "Émissions", total_str, "CO2eq cumulées"),
        _stat_item(
            evolution_icon,
            "Évolution",
            evolution_value,
            evolution_label,
            extra_class=evolution_class,
        ),
        _stat_item("tabler:map-pin", "Région #1", top_region, "la plus émettrice"),
    ]


def _compute_trend(
    df: pd.DataFrame,
    selected_range: tuple[int, int],
) -> tuple[str, str, str, str]:
    """
    Calcule la variation d'intensité médiane entre année début et fin.

    Utilise la médiane plutôt que la somme pour éviter les biais
    dus à l'augmentation du nombre de déclarants au fil des années.

    Args:
        df : DataFrame filtré par année et structure
        selected_range : Tuple (annee_debut, annee_fin)

    Returns:
        tuple : (valeur_formatée, label, nom_icone, classe_css)
    """
    start_year, end_year = selected_range

    if start_year == end_year:
        return ("—", f"sur l'année {start_year}", "tabler:minus", "stat-trend-neutral")

    if df.empty:
        return ("—", f"{start_year} -> {end_year}", "tabler:minus", "stat-trend-neutral")

    start_df = df.loc[
        (df["annee_reporting"] == start_year) & (df["total_emissions"] > 0)
    ]
    end_df = df.loc[
        (df["annee_reporting"] == end_year) & (df["total_emissions"] > 0)
    ]

    if start_df.empty or end_df.empty:
        return ("n/d", f"{start_year} -> {end_year}", "tabler:minus", "stat-trend-neutral")

    start_median = float(start_df["total_emissions"].median())
    end_median = float(end_df["total_emissions"].median())

    if start_median == 0:
        return ("n/d", f"{start_year} -> {end_year}", "tabler:minus", "stat-trend-neutral")

    pct_change = (end_median - start_median) / start_median * 100

    if pct_change > 1:
        icon = "tabler:trending-up"
        css_class = "stat-trend-up"
        prefix = "+"
    elif pct_change < -1:
        icon = "tabler:trending-down"
        css_class = "stat-trend-down"
        prefix = ""
    else:
        icon = "tabler:arrow-right"
        css_class = "stat-trend-neutral"
        prefix = ""

    value_str = f"{prefix}{pct_change:.1f} %".replace(".", ",")
    label_str = f"intensité médiane {start_year}-{end_year}"

    return value_str, label_str, icon, css_class


def _format_emissions(total_t: float) -> str:
    """Formate des émissions en t/Mt/Gt selon l'ordre de grandeur."""
    if total_t >= 1_000_000_000:
        return f"{total_t / 1_000_000_000:.1f}".replace(".", ",") + " Gt"
    if total_t >= 1_000_000:
        return f"{total_t / 1_000_000:.1f}".replace(".", ",") + " Mt"
    return f"{total_t:,.0f}".replace(",", " ") + " t"


def _stat_item(
    icon: str,
    label: str,
    value: str,
    sublabel: str,
    extra_class: str = "",
) -> html.Div:
    """Construit un item du bandeau de stats (icône + label + valeur + sublabel)."""
    return html.Div(
        className=f"stat-item {extra_class}".strip(),
        children=[
            html.Div(
                className="stat-icon",
                children=DashIconify(icon=icon, width=20, color="#1F3A2C"),
            ),
            html.Div(
                className="stat-content",
                children=[
                    html.Div(label, className="stat-label"),
                    html.Div(value, className="stat-value"),
                    html.Div(sublabel, className="stat-sublabel"),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit le layout complet de la page Explorer.

    Sections (dans l'ordre) :
    1. Header avec titre et description
    2. Barre de filtres sticky
    3. Heat timeline (intensité d'émissions par année)
    4. Bandeau KPI (5 indicateurs contextuels)
    5. Carte choroplèthe (France complète)
    6. Inspecteur d'organisations (recherche + détail)
    7. Histogramme multi-vues (top orgs, paliers, secteurs)
    8. Décomposition Scope 1/2/3 (top 15 orgs)

    Returns:
        html.Div : Layout complet de la page
    """
    df = load_cleaned_data()

    plotly_config = {
        "displayModeBar": False,
        "displaylogo": False,
        "responsive": True,
    }

    timeline_config = {
        "displayModeBar": False,
        "displaylogo": False,
        "staticPlot": False,
        "scrollZoom": False,
    }

    return html.Div(
        className="explorer-page",
        children=[
            create_header(
                kicker="Explorer",
                title="Explorer les Bilans GES",
                subtitle=(
                    "Filtrez par région, année et type de structure. La "
                    "carte conserve toujours l'ensemble du territoire "
                    "français pour préserver le contexte géographique. "
                    f"Période : {YEAR_MIN}–{YEAR_MAX}."
                ),
            ),

            create_filters_bar(df),

            html.Div(
                className="heat-timeline-container",
                children=[
                    html.Div(
                        className="heat-timeline-header",
                        children=[
                            DashIconify(
                                icon="tabler:flame",
                                width=16,
                                color="#1F3A2C",
                            ),
                            html.Span(
                                "Intensité d'émissions par année",
                                className="heat-timeline-title",
                            ),
                            html.Span(
                                " — du vert (faibles) au rouge (critiques)",
                                className="heat-timeline-hint",
                            ),
                        ],
                    ),
                    dcc.Loading(
                        type="circle",
                        color="#1F3A2C",
                        children=dcc.Graph(
                            id=GRAPH_HEAT_TIMELINE_ID,
                            config=timeline_config,
                        ),
                    ),
                ],
            ),

            html.Div(
                id=STATS_BANNER_ID,
                className="stats-banner",
            ),

            html.Section(
                className="content-section",
                children=[
                    html.Div(
                        className="section-header",
                        children=[
                            html.Div(
                                className="section-header-icon",
                                children=DashIconify(
                                    icon="tabler:map-2", width=20, color="#1F3A2C"
                                ),
                            ),
                            html.Div(
                                children=[
                                    html.H2(
                                        "Cartographie des émissions par région",
                                        className="section-title",
                                    ),
                                    html.P(
                                        "Heatmap environnementale : toutes "
                                        "les régions de France restent "
                                        "visibles. Les régions sélectionnées "
                                        "via les filtres sont mises en "
                                        "évidence par une bordure dorée.",
                                        className="section-subtitle",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card chart-card-map",
                        children=[
                            dcc.Loading(
                                type="circle",
                                color="#1F3A2C",
                                children=dcc.Graph(
                                    id=GRAPH_GEOMAP_ID,
                                    config=plotly_config,
                                    style={"width": "100%"},
                                ),
                            ),
                        ],
                    ),
                ],
            ),

            html.Section(
                className="content-section",
                children=[
                    html.Div(
                        className="section-header",
                        children=[
                            html.Div(
                                className="section-header-icon",
                                children=DashIconify(
                                    icon="tabler:zoom-scan",
                                    width=20, color="#1F3A2C",
                                ),
                            ),
                            html.Div(
                                children=[
                                    html.H2(
                                        "Inspecter une organisation",
                                        className="section-title",
                                    ),
                                    html.P(
                                        "Cherchez n'importe quelle "
                                        "organisation pour afficher son "
                                        "bilan détaillé : émissions "
                                        "totales, évolution annuelle et "
                                        "décomposition Scope 1 / 2 / 3.",
                                        className="section-subtitle",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    create_inspector(df),
                ],
            ),

            html.Section(
                className="content-section",
                children=[
                    html.Div(
                        className="section-header",
                        children=[
                            html.Div(
                                className="section-header-icon",
                                children=DashIconify(
                                    icon="tabler:chart-histogram",
                                    width=20, color="#1F3A2C",
                                ),
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    html.Div(
                                        className="section-header-row",
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.H2(
                                                        "Distribution des émissions",
                                                        className="section-title",
                                                    ),
                                                    html.P(
                                                        "Trois vues complémentaires "
                                                        "pour analyser les émissions "
                                                        "selon différentes dimensions.",
                                                        className="section-subtitle",
                                                    ),
                                                ],
                                            ),
                                            dcc.RadioItems(
                                                id=HISTOGRAM_VIEW_TOGGLE_ID,
                                                options=[
                                                    {"label": "Top 15 émetteurs", "value": VIEW_TOP_ORGS},
                                                    {"label": "Paliers", "value": VIEW_BINS},
                                                    {"label": "Top 15 secteurs", "value": VIEW_SECTORS},
                                                ],
                                                value=VIEW_TOP_ORGS,
                                                className="view-toggle",
                                                inputClassName="view-toggle-input",
                                                labelClassName="view-toggle-label",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
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

        ],
    )


# ─────────────────────────────────────────────────────────────────
# CALLBACKS - graphes dynamiques pilotés par les filtres
# ─────────────────────────────────────────────────────────────────

def register_callbacks(app) -> None:
    """
    Enregistre les callbacks Dash de la page Explorer.

    Architecture de filtrage à 2 niveaux :
    - df_year_struct : filtres année + structure (toutes régions visibles)
      -> pour la carte (France complète) et heat timeline
    - df_full : df_year_struct + filtre région (sélection complète)
      -> pour histogramme, scope breakdown, statistiques

    Args:
        app : Instance Dash
    """

    @app.callback(
        [
            Output(GRAPH_GEOMAP_ID, "figure"),
            Output(GRAPH_HISTOGRAM_ID, "figure"),
            Output(GRAPH_HEAT_TIMELINE_ID, "figure"),
            Output(STATS_BANNER_ID, "children"),
        ],
        [
            Input(FILTER_YEAR_RANGE_ID, "value"),
            Input(FILTER_REGION_ID, "value"),
            Input(FILTER_STRUCTURE_ID, "value"),
            Input(HISTOGRAM_VIEW_TOGGLE_ID, "value"),
        ],
    )
    def update_charts(year_range, regions, structures, histogram_view):
        """
        Recalcule tous les graphes et statistiques à chaque changement de filtre.

        Applique d'abord les filtres année + structure pour obtenir df_year_struct
        (France complète), puis rajoute le filtre région pour df_full.
        """
        df = load_cleaned_data()

        if not year_range or len(year_range) != 2:
            year_range = [YEAR_MIN, YEAR_MAX]
        start_year, end_year = int(year_range[0]), int(year_range[1])

        df_year_struct = df[df["annee_reporting"].between(start_year, end_year)]
        df_year_struct = filter_data(df_year_struct, type_structure=structures)

        df_full = filter_data(df_year_struct, region=regions)

        df_struct_only = filter_data(df, type_structure=structures)

        geomap_fig = create_geomap(
            df_year_struct,
            highlighted_regions=regions if regions else None,
        )
        histogram_fig = create_histogram(
            df_full, view=histogram_view or VIEW_TOP_ORGS
        )
        timeline_fig = create_heat_timeline(
            df_struct_only,
            selected_range=(start_year, end_year),
        )
        stats_banner = _build_stats_banner(
            df_full,
            df_year_struct,
            selected_range=(start_year, end_year),
        )

        return geomap_fig, histogram_fig, timeline_fig, stats_banner

    @app.callback(
        Output(INSPECTOR_DETAIL_ID, "children"),
        Input(INSPECTOR_DROPDOWN_ID, "value"),
    )
    def update_inspector(selected_org):
        """
        Met à jour le panneau de détail quand une organisation est sélectionnée.

        L'inspecteur affiche le bilan COMPLET sur 2010-2025 (pas filtré par
        les filtres globaux région/année/structure).
        """
        if not selected_org:
            return build_org_detail(load_cleaned_data().iloc[0:0], None)

        df = load_cleaned_data()
        df_org = df[df["raison_sociale"] == selected_org]
        return build_org_detail(df_org, selected_org)

    @app.callback(
        [
            Output(FILTER_YEAR_RANGE_ID, "value"),
            Output(FILTER_REGION_ID, "value"),
            Output(FILTER_STRUCTURE_ID, "value"),
        ],
        Input(FILTER_RESET_BTN_ID, "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        """Réinitialise tous les filtres à leurs valeurs par défaut."""
        return [YEAR_MIN, YEAR_MAX], None, None
