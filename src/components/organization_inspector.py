"""
Composant d'inspection détaillée d'une organisation (raison sociale).
Permet de rechercher une entreprise ou entité publique pour afficher sa fiche analytique :
KPIs dédiés, courbe d'évolution temporelle et graphique en secteurs (donut) par scope.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
from dash_iconify import DashIconify

# Importation du thème graphique partagé
from src.components.charts_theme import apply_theme, COLORS, SCOPE_COLORS

# Identifiants uniques pour lier le dropdown et la zone de détail aux callbacks Dash
INSPECTOR_DROPDOWN_ID = "inspector-org-dropdown"
INSPECTOR_DETAIL_ID = "inspector-org-detail"


def create_inspector(df: pd.DataFrame) -> html.Div:
    """
    Construit l'ossature initiale du panneau d'inspection.

    Args:
        df (pd.DataFrame): Jeu de données complet pour initialiser la barre de recherche.

    Returns:
        html.Div: Conteneur du panneau de recherche et de la zone de résultats.
    """
    # Construction de la liste des options du menu déroulant (dropdown)
    options = _build_org_options(df)

    return html.Div(
        className="inspector-panel",
        children=[
            # Zone supérieure contenant la barre de recherche
            html.Div(
                className="inspector-search-bar",
                children=[
                    # Label d'information et statistiques de la base
                    html.Div(
                        className="inspector-search-label",
                        children=[
                            DashIconify(
                                icon="tabler:search",
                                width=18,
                                color="#1F3A2C",
                            ),
                            html.Span(
                                "Rechercher une organisation",
                                className="inspector-search-title",
                            ),
                            html.Span(
                                f"  ·  {len(options):,} organisations dans la base"
                                .replace(",", " "),
                                className="inspector-search-hint",
                            ),
                        ],
                    ),
                    # Menu déroulant Dash avec autocomplétion pour la recherche d'organisations
                    dcc.Dropdown(
                        id=INSPECTOR_DROPDOWN_ID,
                        options=options,
                        placeholder="Tapez le nom (ex: Renault, EDF, BNP, ENGIE…)",
                        value=None,
                        clearable=True,
                        optionHeight=42, # Hauteur aérée pour chaque ligne d'option
                        className="inspector-dropdown",
                    ),
                ],
            ),

            # Zone inférieure contenant la fiche détaillée (vide lors de l'affichage initial)
            html.Div(
                id=INSPECTOR_DETAIL_ID,
                className="inspector-detail",
                children=_empty_state(),
            ),
        ],
    )


def build_org_detail(df_org: pd.DataFrame, org_name: str | None) -> list:
    """
    Génère la structure de la fiche détaillée d'une organisation spécifique.
    Appelée dynamiquement par le callback de la page d'exploration.

    Args:
        df_org (pd.DataFrame): Données filtrées pour l'organisation sélectionnée.
        org_name (str | None): Raison sociale de l'organisation.

    Returns:
        list: Liste de composants HTML constituant la fiche.
    """
    # Si aucune organisation n'est sélectionnée, on retourne l'état vide informatif
    if not org_name or df_org.empty:
        return _empty_state()

    # Calcul des statistiques clés de l'organisation
    total_t = float(df_org["total_emissions"].sum())
    total_str = _format_emissions(total_t)
    nb_years = int(df_org["annee_reporting"].nunique())
    
    # Identification du secteur NAF et de la région dominants
    naf_mode = df_org["libelle_naf"].mode()
    sector = naf_mode.iloc[0] if not naf_mode.empty else "—"
    region_mode = df_org["region"].mode()
    region = region_mode.iloc[0] if not region_mode.empty else "—"

    return [
        # En-tête de la fiche d'identité de l'organisation
        html.Div(
            className="inspector-org-header",
            children=[
                html.H3(org_name, className="inspector-org-name"),
                html.Div(
                    className="inspector-org-meta",
                    children=[
                        html.Span(sector, className="inspector-org-sector"),
                        html.Span(" · ", className="inspector-org-sep"),
                        html.Span(region, className="inspector-org-region"),
                    ],
                ),
            ],
        ),

        # Grille de 4 cartes KPI résumant les chiffres clés
        html.Div(
            className="inspector-kpi-grid",
            children=[
                _kpi_card("tabler:cloud", "Émissions totales", total_str, "tous scopes"),
                _kpi_card(
                    "tabler:calendar-stats",
                    "Années déclarées",
                    str(nb_years),
                    f"de {df_org['annee_reporting'].min()} à {df_org['annee_reporting'].max()}",
                ),
                _kpi_card(
                    "tabler:file-text",
                    "Bilans publiés",
                    str(len(df_org)),
                    "déclarations BEGES",
                ),
                _kpi_card(
                    "tabler:trending-up",
                    "Bilan moyen",
                    _format_emissions(total_t / max(len(df_org), 1)),
                    "CO₂eq par bilan",
                ),
            ],
        ),

        # Zone d'affichage des deux graphiques détaillés (Évolution et répartition des Scopes)
        html.Div(
            className="inspector-charts-grid",
            children=[
                # Premier graphique : évolution dans le temps
                html.Div(
                    className="inspector-chart-block",
                    children=[
                        html.H4(
                            "Évolution annuelle",
                            className="inspector-chart-title",
                        ),
                        dcc.Graph(
                            figure=_build_evolution_chart(df_org),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                ),
                # Deuxième graphique : répartition en Scopes 1, 2, et 3
                html.Div(
                    className="inspector-chart-block",
                    children=[
                        html.H4(
                            "Décomposition par scope",
                            className="inspector-chart-title",
                        ),
                        dcc.Graph(
                            figure=_build_scope_donut(df_org),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                ),
            ],
        ),
    ]


def _build_org_options(df: pd.DataFrame) -> list[dict]:
    """
    Construit la liste des choix possibles (options) pour le dropdown.

    Args:
        df (pd.DataFrame): DataFrame brut des données.

    Returns:
        list[dict]: Liste de dictionnaires {"label": nom, "value": nom}.
    """
    orgs = (
        df.dropna(subset=["raison_sociale"])
          ["raison_sociale"]
          .drop_duplicates()
          .sort_values()
    )
    return [{"label": name, "value": name} for name in orgs]


def _empty_state() -> list:
    """
    Génère l'affichage informatif par défaut quand aucun choix n'est sélectionné.

    Returns:
        list: Composants affichant une icône de loupe et un texte indicatif.
    """
    return [
        html.Div(
            className="inspector-empty",
            children=[
                DashIconify(
                    icon="tabler:building-search",
                    width=48,
                    color="#9A9A9A",
                ),
                html.P(
                    "Sélectionnez une organisation ci-dessus pour "
                    "afficher son bilan détaillé : émissions totales, "
                    "évolution annuelle, et décomposition par scope.",
                    className="inspector-empty-text",
                ),
            ],
        ),
    ]


def _kpi_card(icon: str, label: str, value: str, sublabel: str) -> html.Div:
    """
    Génère une petite carte KPI adaptée au panneau d'inspection.

    Args:
        icon (str): Icône SVG à intégrer.
        label (str): Titre de l'indicateur.
        value (str): Valeur numérique.
        sublabel (str): Sous-titre textuel.

    Returns:
        html.Div: Composant HTML de la mini carte KPI.
    """
    return html.Div(
        className="inspector-kpi",
        children=[
            html.Div(
                className="inspector-kpi-icon",
                children=DashIconify(icon=icon, width=18, color="#1F3A2C"),
            ),
            html.Div(
                children=[
                    html.Div(label, className="inspector-kpi-label"),
                    html.Div(value, className="inspector-kpi-value"),
                    html.Div(sublabel, className="inspector-kpi-sublabel"),
                ],
            ),
        ],
    )


def _build_evolution_chart(df_org: pd.DataFrame) -> go.Figure:
    """
    Construit le graphique en lignes représentant l'évolution annuelle des émissions.

    Args:
        df_org (pd.DataFrame): Données chronologiques de l'organisation.

    Returns:
        go.Figure: Graphique linéaire Plotly.
    """
    yearly = (
        df_org.groupby("annee_reporting")["total_emissions"]
              .sum()
              .reset_index()
              .sort_values("annee_reporting")
    )

    fig = go.Figure()
    # Mode markers si une seule année, mode lines+markers si tendance possible
    fig.add_trace(go.Scatter(
        x=yearly["annee_reporting"],
        y=yearly["total_emissions"],
        mode="lines+markers" if len(yearly) >= 2 else "markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(
            size=10,
            color=COLORS["primary"],
            line=dict(color=COLORS["surface"], width=2),
        ),
        fill="tozeroy" if len(yearly) >= 2 else None,
        fillcolor="rgba(31, 58, 44, 0.10)",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y:,.0f} tCO₂eq"
            "<extra></extra>"
        ),
    ))

    # Message d'avertissement s'il n'y a pas assez de points de données pour tracer une courbe
    if len(yearly) < 2:
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.5, y=0.92,
            text="<i>Une seule année déclarée — pas de tendance disponible</i>",
            showarrow=False,
            font=dict(size=11, color=COLORS["text_muted"], family="DM Sans"),
        )

    fig.update_xaxes(
        dtick=1,
        title_text="Année",
        tickformat="d",
    )
    fig.update_yaxes(title_text="Émissions (tCO₂eq)", tickformat=".2s")
    apply_theme(fig, height=280, show_legend=False)
    fig.update_layout(margin=dict(t=30, b=40, l=60, r=20))
    return fig


def _build_scope_donut(df_org: pd.DataFrame) -> go.Figure:
    """
    Génère le graphique en secteurs (donut) pour la répartition des Scopes 1, 2, et 3.

    Args:
        df_org (pd.DataFrame): Données détaillées par Scope de l'organisation.

    Returns:
        go.Figure: Graphique Donut Plotly.
    """
    s1 = float(df_org["total_scope_1"].sum())
    s2 = float(df_org["total_scope_2"].sum())
    s3 = float(df_org["total_scope_3"].sum())

    values = [s1, s2, s3]
    labels = ["Scope 1 — directes", "Scope 2 — énergie", "Scope 3 — indirectes"]
    colors = [SCOPE_COLORS["scope_1"], SCOPE_COLORS["scope_2"], SCOPE_COLORS["scope_3"]]

    # Cas exceptionnel de valeurs nulles sur tous les Scopes
    if sum(values) == 0:
        return _empty_donut()

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.55, # Rendu sous forme d'anneau (Donut)
        marker=dict(colors=colors, line=dict(color=COLORS["surface"], width=2)),
        textinfo="percent",
        textfont=dict(family="DM Sans", size=12, color="#FFFFFF", weight=600),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} tCO₂eq<br>"
            "%{percent}"
            "<extra></extra>"
        ),
        sort=False,
    ))
    apply_theme(fig, height=280, show_legend=True)
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20))
    return fig


def _empty_donut() -> go.Figure:
    """
    Génère un donut vide en cas d'absence d'information de Scope.

    Returns:
        go.Figure: Graphique d'avertissement.
    """
    fig = go.Figure()
    fig.add_annotation(
        text="Aucun détail Scope renseigné",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family="DM Sans", size=13, color=COLORS["text_muted"]),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    apply_theme(fig, height=280, show_legend=False)
    return fig


def _format_emissions(total_t: float) -> str:
    """
    Formate la valeur numérique des émissions en t, kt, Mt, Gt pour une lecture simplifiée.

    Args:
        total_t (float): Émissions brutes en tonnes.

    Returns:
        str: Valeur formatée accompagnée de l'unité appropriée.
    """
    if total_t >= 1_000_000_000:
        return f"{total_t / 1_000_000_000:.2f}".replace(".", ",") + " Gt"
    if total_t >= 1_000_000:
        return f"{total_t / 1_000_000:.2f}".replace(".", ",") + " Mt"
    if total_t >= 1_000:
        return f"{total_t / 1_000:.1f}".replace(".", ",") + " kt"
    return f"{total_t:,.0f}".replace(",", " ") + " t"
