"""
Page d'accueil 'Vue d'ensemble' du tableau de bord.
Affiche les chiffres clés globaux (KPIs nationaux), l'historique de publication des bilans carbone
et la répartition par type de structure (entreprises, collectivités, services de l'État).
"""

import pandas as pd
import plotly.express as px
from dash import html, dcc

# Importation des composants réutilisables
from src.components.header import create_header
from src.components.kpi_card import create_kpi_card
from src.components.charts_theme import apply_theme, COLORS, CATEGORICAL

# Utilitaires de données
from src.utils.common_functions import load_cleaned_data


def compute_kpis(df: pd.DataFrame) -> dict[str, str]:
    """
    Calcule les indicateurs clés à afficher en haut de la page.

    Args:
        df (pd.DataFrame): Jeu de données nettoyé.

    Returns:
        dict[str, str]: Valeurs formatées des indicateurs (bilans, organisations, émissions, période).
    """
    # Nombre total de déclarations BEGES enregistrées
    nb_bilans = len(df)
    bilans_str = f"{nb_bilans:,}".replace(",", " ")

    # Nombre d'organisations uniques (identifiées par leur SIREN principal)
    nb_orgs = df["siren"].nunique()
    orgs_str = f"{nb_orgs:,}".replace(",", " ")

    # Volume cumulé des émissions (tous scopes confondus) converti en Gigatonnes (Gt) pour la lisibilité
    total_t = df["total_emissions"].sum()
    total_gt = total_t / 1_000_000_000
    emissions_str = f"{total_gt:.1f}".replace(".", ",") + " Gt CO₂eq"

    # Période chronologique couverte par le jeu de données
    annee_min = int(df["annee_reporting"].min())
    annee_max = int(df["annee_reporting"].max())
    periode_str = f"{annee_min}–{annee_max}"
    duree_str = f"{annee_max - annee_min + 1} années couvertes"

    return {
        "bilans": bilans_str,
        "organisations": orgs_str,
        "emissions": emissions_str,
        "periode": periode_str,
        "duree": duree_str,
    }


def build_evolution_chart(df: pd.DataFrame):
    """
    Construit le graphique en aire décrivant l'évolution du nombre annuel de publications.

    Args:
        df (pd.DataFrame): Jeu de données nettoyé.

    Returns:
        plotly.graph_objects.Figure: Graphique en aire configuré.
    """
    # Regroupement et comptage des bilans par année de reporting
    yearly = (
        df.groupby("annee_reporting")
          .size()
          .reset_index(name="bilans")
          .sort_values("annee_reporting")
    )

    # Tracé en aire (aire remplie sous la courbe de tendance)
    fig = px.area(
        yearly,
        x="annee_reporting",
        y="bilans",
        labels={
            "annee_reporting": "Année de reporting",
            "bilans": "Nombre de bilans publiés",
        },
    )

    fig.update_traces(
        line=dict(color=COLORS["primary"], width=2.5),
        fillcolor="rgba(31, 58, 44, 0.12)", # Teinte verte transparente
        mode="lines+markers",
        marker=dict(
            size=6,
            color=COLORS["primary"],
            line=dict(color=COLORS["surface"], width=1),
        ),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y:,.0f} bilans publiés"
            "<extra></extra>"
        ),
    )

    fig.update_xaxes(dtick=1) # Graduation d'axe calée sur une année
    apply_theme(fig, height=380, show_legend=False)
    return fig


def build_structure_donut(df: pd.DataFrame):
    """
    Génère un graphique Donut décrivant la répartition des bilans par type de structure.

    Args:
        df (pd.DataFrame): Jeu de données nettoyé.

    Returns:
        plotly.graph_objects.Figure: Graphique Donut configuré.
    """
    # Distribution des bilans par type de structure
    types = df["type_structure"].value_counts().reset_index()
    types.columns = ["type_structure", "bilans"]

    # Graphique en secteurs circulaire évidé au centre (Donut)
    fig = px.pie(
        types,
        names="type_structure",
        values="bilans",
        hole=0.55,
        color_discrete_sequence=CATEGORICAL,
    )

    fig.update_traces(
        textinfo="none", # Masquer les étiquettes internes pour éviter les superpositions
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} bilans (%{percent})"
            "<extra></extra>"
        ),
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
    )

    apply_theme(fig, height=380, show_legend=True)
    return fig


def layout() -> html.Div:
    """
    Définit la mise en page de la page d'accueil.

    Returns:
        html.Div: Conteneur principal de la page.
    """
    df = load_cleaned_data()

    # Calcul des indicateurs et graphiques statiques globaux
    kpis = compute_kpis(df)
    fig_evolution = build_evolution_chart(df)
    fig_structures = build_structure_donut(df)

    return html.Div(
        className="page-container",
        children=[
            create_header(
                kicker="Vue d'ensemble",
                title="Le bilan carbone des organisations françaises",
                subtitle=(
                    f"{kpis['bilans']} déclarations BEGES publiées par "
                    f"{kpis['organisations']} organisations françaises "
                    f"sur la période {kpis['periode']}. Source : ADEME."
                ),
            ),

            # Grille des KPI Cards globales
            html.Section(
                className="kpi-grid",
                children=[
                    create_kpi_card(
                        label="Bilans publiés",
                        value=kpis["bilans"],
                        sublabel="Déclarations BEGES enregistrées",
                        icon="tabler:file-text",
                    ),
                    create_kpi_card(
                        label="Organisations",
                        value=kpis["organisations"],
                        sublabel="SIREN distincts ayant déclaré",
                        icon="tabler:building",
                    ),
                    create_kpi_card(
                        label="Émissions cumulées",
                        value=kpis["emissions"],
                        sublabel="Tous scopes confondus",
                        icon="tabler:cloud",
                    ),
                    create_kpi_card(
                        label="Période couverte",
                        value=kpis["periode"],
                        sublabel=kpis["duree"],
                        icon="tabler:calendar",
                    ),
                ],
            ),

            # Section décrivant la croissance du nombre de bilans
            html.Section(
                className="content-section",
                children=[
                    html.H2(
                        "Une dynamique réglementaire qui s'accélère",
                        className="section-title",
                    ),
                    html.P(
                        "Le nombre de bilans GES publiés chaque année a "
                        "fortement augmenté depuis 2018, porté par "
                        "l'élargissement progressif de l'obligation "
                        "réglementaire (loi Grenelle II, loi Climat et "
                        "Résilience).",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            dcc.Graph(
                                figure=fig_evolution,
                                config={
                                    "displayModeBar": False,
                                    "displaylogo": False,
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # Section décrivant le profil typique des déclarants
            html.Section(
                className="content-section",
                children=[
                    html.H2(
                        "Qui publie ses bilans GES ?",
                        className="section-title",
                    ),
                    html.P(
                        "Les entreprises représentent la majorité des "
                        "déclarants, suivies par les établissements "
                        "publics et les collectivités territoriales. "
                        "L'État et le tissu associatif complètent le "
                        "paysage déclaratif.",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            dcc.Graph(
                                figure=fig_structures,
                                config={
                                    "displayModeBar": False,
                                    "displaylogo": False,
                                },
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks de la page d'accueil (statique).
    """
    pass
