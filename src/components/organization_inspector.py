"""
Composant Inspecteur d'organisation.

Le dataset comporte 6 810 organisations distinctes, ce qui rend
impossible une visualisation exhaustive. Cet inspecteur permet de
chercher une organisation par nom et d'afficher en détail :

  - 4 KPIs contextuels (total, secteur, région, années déclarées)
  - une mini courbe d'évolution annuelle (si ≥2 années dispo)
  - un mini donut Scope 1/2/3

Usage : à brancher dans la page Explorer avec deux callbacks :
  1. options du dropdown = liste des orgs présentes dans la sélection
  2. contenu du détail = construit à partir de l'org sélectionnée

Doc Dash dropdown : https://dash.plotly.com/dash-core-components/dropdown
"""

# Permet la syntaxe PEP 604 (str | None) sur Python 3.9 :
# les annotations restent des chaînes et ne sont pas évaluées à l'import.
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
from dash_iconify import DashIconify

from src.components.charts_theme import apply_theme, COLORS, SCOPE_COLORS


# ─────────────────────────────────────────────────────────────────
# IDs Dash exposés (référencés par les callbacks dans analysis.py)
# ─────────────────────────────────────────────────────────────────

INSPECTOR_DROPDOWN_ID = "inspector-org-dropdown"
INSPECTOR_DETAIL_ID = "inspector-org-detail"


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant principal
# ─────────────────────────────────────────────────────────────────

def create_inspector(df: pd.DataFrame) -> html.Div:
    """
    Construit le squelette du panneau Inspecteur d'organisation.

    Args:
        df: DataFrame complet (toutes orgs disponibles) - sert à
            initialiser les options du dropdown.

    Returns:
        html.Div: Conteneur Dash du panneau.
    """
    # Liste des organisations disponibles (raison sociale + SIREN pour
    # désambiguïser les homonymes). Tri alphabétique pour faciliter la
    # recherche manuelle.
    options = _build_org_options(df)

    return html.Div(
        className="inspector-panel",
        children=[
            # Barre de recherche
            html.Div(
                className="inspector-search-bar",
                children=[
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
                    dcc.Dropdown(
                        id=INSPECTOR_DROPDOWN_ID,
                        options=options,
                        placeholder="Tapez le nom (ex: Renault, EDF, BNP, ENGIE…)",
                        value=None,
                        clearable=True,
                        # searchable par défaut. optionHeight=42 pour aérer.
                        optionHeight=42,
                        className="inspector-dropdown",
                    ),
                ],
            ),

            # Zone de détail (vide par défaut, remplie par callback)
            html.Div(
                id=INSPECTOR_DETAIL_ID,
                className="inspector-detail",
                children=_empty_state(),
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# Construction du panneau de détail (appelé depuis le callback)
# ─────────────────────────────────────────────────────────────────

def build_org_detail(df_org: pd.DataFrame, org_name: str | None) -> list:
    """
    Construit le contenu du panneau de détail pour une organisation.

    Args:
        df_org: Sous-DataFrame contenant uniquement les bilans de
            l'organisation sélectionnée (toutes années disponibles).
        org_name: Nom complet de l'organisation (raison sociale).

    Returns:
        list: Liste de composants Dash (children du conteneur de détail).
    """
    # Cas 'aucune sélection' : on rend l'état vide.
    if not org_name or df_org.empty:
        return _empty_state()

    # ── KPIs synthétiques ──────────────────────────────────────
    total_t = float(df_org["total_emissions"].sum())
    total_str = _format_emissions(total_t)
    nb_years = int(df_org["annee_reporting"].nunique())
    # Secteur NAF dominant (si plusieurs bilans avec NAF différents,
    # on prend le plus fréquent - rare mais possible).
    naf_mode = df_org["libelle_naf"].mode()
    sector = naf_mode.iloc[0] if not naf_mode.empty else "—"
    region_mode = df_org["region"].mode()
    region = region_mode.iloc[0] if not region_mode.empty else "—"

    return [
        # Header avec nom de l'org
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

        # 4 KPIs en ligne
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

        # Grille 2 colonnes : évolution annuelle + donut scope
        html.Div(
            className="inspector-charts-grid",
            children=[
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


# ─────────────────────────────────────────────────────────────────
# Helpers privés - construction des sous-composants
# ─────────────────────────────────────────────────────────────────

def _build_org_options(df: pd.DataFrame) -> list[dict]:
    """
    Construit la liste d'options du dropdown : une entrée par
    organisation distincte, triée alphabétiquement.

    On utilise raison_sociale comme value ET label : Dash gère
    naturellement la recherche fuzzy sur les labels.
    """
    orgs = (
        df.dropna(subset=["raison_sociale"])
          ["raison_sociale"]
          .drop_duplicates()
          .sort_values()
    )
    return [{"label": name, "value": name} for name in orgs]


def _empty_state() -> list:
    """Affichage par défaut quand aucune organisation n'est sélectionnée."""
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
    """Mini KPI card pour le bandeau de l'inspecteur."""
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
    Mini graphique d'évolution annuelle pour l'organisation sélectionnée.
    Si une seule année déclarée, on affiche un point + un message
    d'avertissement plutôt qu'une "courbe" trompeuse.
    """
    yearly = (
        df_org.groupby("annee_reporting")["total_emissions"]
              .sum()
              .reset_index()
              .sort_values("annee_reporting")
    )

    fig = go.Figure()
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

    # Avertissement si <2 années (lecture de tendance impossible).
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
    """Mini donut Scope 1/2/3 pour l'organisation sélectionnée."""
    s1 = float(df_org["total_scope_1"].sum())
    s2 = float(df_org["total_scope_2"].sum())
    s3 = float(df_org["total_scope_3"].sum())

    values = [s1, s2, s3]
    labels = ["Scope 1 — directes", "Scope 2 — énergie", "Scope 3 — indirectes"]
    colors = [SCOPE_COLORS["scope_1"], SCOPE_COLORS["scope_2"], SCOPE_COLORS["scope_3"]]

    # Cas dégénéré : tous les scopes à 0 (très rare, mais possible).
    if sum(values) == 0:
        return _empty_donut()

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
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
    """Donut vide quand aucun scope n'a de valeur."""
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
    """Formate des émissions en t/Mt/Gt selon l'ordre de grandeur."""
    if total_t >= 1_000_000_000:
        return f"{total_t / 1_000_000_000:.2f}".replace(".", ",") + " Gt"
    if total_t >= 1_000_000:
        return f"{total_t / 1_000_000:.2f}".replace(".", ",") + " Mt"
    if total_t >= 1_000:
        return f"{total_t / 1_000:.1f}".replace(".", ",") + " kt"
    return f"{total_t:,.0f}".replace(",", " ") + " t"
