"""
Page d'accueil du dashboard - 'Vue d'ensemble'.
Présente le contexte du sujet (BEGES en France) sous forme de :
  - 4 cartes KPI (chiffres clés du dataset)
  - un graphique d'évolution annuelle des publications
  - un graphique en donut par type de structure

Doc Dash layout : https://dash.plotly.com/layout
"""

# pandas : pour les agrégations de KPIs et des graphes
import pandas as pd

# plotly.express : API haut niveau pour graphes simples (line, donut)
import plotly.express as px

# dash html / dcc : composants HTML et Graph
from dash import html, dcc

# Composant header éditorial (kicker + titre + sous-titre)
from src.components.header import create_header

# Composant KPI card réutilisable
from src.components.kpi_card import create_kpi_card

# Helper de thème Plotly (palette + polices + layout)
from src.components.charts_theme import apply_theme, COLORS, CATEGORICAL

# Loader des données nettoyées (CSV produit par clean_data.py)
from src.utils.common_functions import load_cleaned_data


# ─────────────────────────────────────────────────────────────────
# CALCUL DES KPIs
# ─────────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict[str, str]:
    """
    Calcule les 4 indicateurs clés affichés en haut de la page d'accueil.
    Reçoit le DataFrame nettoyé et retourne un dict de chaînes formatées
    prêtes à être affichées (avec séparateurs de milliers, unités...).

    Args:
        df (pd.DataFrame): DataFrame nettoyé issu de load_cleaned_data().

    Returns:
        dict[str, str]: Dict avec 4 clés : bilans, organisations,
                        emissions, periode.
    """
    # 1. Nombre total de bilans BEGES dans le dataset (= nombre de lignes).
    # Format avec espace insécable comme séparateur de milliers (norme
    # française), ex: "9 991". On utilise un f-string avec ',' puis on
    # remplace la virgule par une espace insécable.
    nb_bilans = len(df)
    bilans_str = f"{nb_bilans:,}".replace(",", " ")

    # 2. Nombre d'organisations distinctes (un SIREN = une entité).
    # nunique() compte les valeurs uniques en ignorant les NaN.
    nb_orgs = df["siren"].nunique()
    orgs_str = f"{nb_orgs:,}".replace(",", " ")

    # 3. Émissions totales cumulées sur tout le dataset.
    # On somme la colonne total_emissions (en tCO2eq, donc tonnes).
    # Pour l'affichage on convertit en gigatonnes (Gt) car c'est l'ordre
    # de grandeur du cumul (~7-8 Gt CO2eq).
    total_t = df["total_emissions"].sum()
    total_gt = total_t / 1_000_000_000  # tonnes -> gigatonnes
    # On affiche avec 1 décimale et la virgule française (str.replace).
    emissions_str = f"{total_gt:.1f}".replace(".", ",") + " Gt CO₂eq"

    # 4. Période couverte par les bilans publiés (min - max année).
    # On exclut les NaN éventuels (tous filtrés mais sécurité).
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


# ─────────────────────────────────────────────────────────────────
# GRAPHE 1 : évolution annuelle des publications BEGES
# ─────────────────────────────────────────────────────────────────

def build_evolution_chart(df: pd.DataFrame):
    """
    Construit un graphique en aire montrant le nombre de bilans BEGES
    publiés chaque année. Permet de visualiser la progression de la
    déclaration réglementaire (forte hausse depuis 2018, pic en 2023).

    Args:
        df (pd.DataFrame): DataFrame nettoyé.

    Returns:
        plotly.graph_objects.Figure: Figure prête à passer à dcc.Graph.
    """
    # Agrégation : nombre de bilans par année de reporting.
    # groupby retourne une série, .reset_index(name='bilans') la
    # transforme en DataFrame avec deux colonnes : annee_reporting et bilans.
    yearly = (
        df.groupby("annee_reporting")
          .size()
          .reset_index(name="bilans")
          .sort_values("annee_reporting")
    )

    # px.area : graphe en aire (line + remplissage en dessous), donne
    # un effet de "volume" qui souligne la croissance.
    fig = px.area(
        yearly,
        x="annee_reporting",
        y="bilans",
        # labels : noms affichés sur les axes (en français).
        labels={
            "annee_reporting": "Année de reporting",
            "bilans": "Nombre de bilans publiés",
        },
    )

    # Personnalisation des traces : couleur primaire, opacité de l'aire
    # plus douce, ligne plus marquée, points sur chaque année (markers).
    fig.update_traces(
        line=dict(color=COLORS["primary"], width=2.5),
        fillcolor="rgba(31, 58, 44, 0.12)",  # primary à 12% d'opacité
        mode="lines+markers",
        marker=dict(
            size=6,
            color=COLORS["primary"],
            line=dict(color=COLORS["surface"], width=1),
        ),
        # Template du tooltip : année en gras, valeur en clair.
        # <extra></extra> retire la boîte secondaire qui s'affiche par défaut.
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y:,.0f} bilans publiés"
            "<extra></extra>"
        ),
    )

    # Tick année par année (nous avons 14 années, c'est lisible).
    fig.update_xaxes(dtick=1)

    # Application du thème global (palette + typographie Fraunces/DM Sans).
    # Pas de légende ici : une seule série, légende inutile.
    apply_theme(fig, height=380, show_legend=False)
    return fig


# ─────────────────────────────────────────────────────────────────
# GRAPHE 2 : répartition par type de structure (donut)
# ─────────────────────────────────────────────────────────────────

def build_structure_donut(df: pd.DataFrame):
    """
    Construit un graphique en donut affichant la répartition des bilans
    par type de structure (Entreprise, Établissement public, etc.).

    Args:
        df (pd.DataFrame): DataFrame nettoyé.

    Returns:
        plotly.graph_objects.Figure: Figure prête à passer à dcc.Graph.
    """
    # value_counts() : compte les occurrences de chaque type, trié desc.
    # On en fait un DataFrame avec colonnes type_structure et count.
    types = df["type_structure"].value_counts().reset_index()
    types.columns = ["type_structure", "bilans"]

    # px.pie + hole=0.55 = donut chart (et non camembert plein).
    # Le donut est plus moderne et permet d'afficher un total au centre.
    fig = px.pie(
        types,
        names="type_structure",
        values="bilans",
        hole=0.55,
        # color_discrete_sequence : on impose notre palette catégorielle
        # plutôt que les couleurs par défaut de Plotly.
        color_discrete_sequence=CATEGORICAL,
    )

    # Personnalisation des traces : labels et pourcentages dans le tooltip,
    # textinfo="none" pour ne PAS afficher de texte sur les tranches
    # (plus propre, on lit via le hover et la légende).
    fig.update_traces(
        textinfo="none",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} bilans (%{percent})"
            "<extra></extra>"
        ),
        # Petit espace blanc entre les tranches pour un look papier
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
    )

    # Application du thème + on garde la légende cette fois (essentielle
    # pour identifier les types puisque les tranches n'ont pas de label).
    apply_theme(fig, height=380, show_legend=True)
    return fig


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout Dash de la page d'accueil.
    Affiche un en-tête éditorial, 4 KPIs, et 2 graphiques (évolution
    annuelle + donut des types de structure).

    Returns:
        html.Div: Layout complet de la page d'accueil.
    """
    # Chargement des données nettoyées (lecture du CSV produit par
    # clean_data.py). On le fait à chaque appel de layout() pour rester
    # simple - le CSV fait quelques Mo, la lecture est rapide.
    df = load_cleaned_data()

    # Calcul des KPIs et construction des graphes une seule fois ici.
    kpis = compute_kpis(df)
    fig_evolution = build_evolution_chart(df)
    fig_structures = build_structure_donut(df)

    return html.Div(
        className="page-container",
        children=[
            # En-tête éditorial : kicker + titre serif + sous-titre.
            # Les chiffres viennent des KPIs calculés pour rester cohérents
            # avec le dataset réel et la mise à jour ADEME du jour.
            create_header(
                kicker="Vue d'ensemble",
                title="Le bilan carbone des organisations françaises",
                subtitle=(
                    f"{kpis['bilans']} déclarations BEGES publiées par "
                    f"{kpis['organisations']} organisations françaises "
                    f"sur la période {kpis['periode']}. Source : ADEME."
                ),
            ),

            # ── Section 1 : ligne de KPIs ─────────────────────────
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

            # ── Section 2 : évolution annuelle des publications ───
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
                    # Wrapper "chart-card" : fond blanc + bordure subtile
                    html.Div(
                        className="chart-card",
                        children=[
                            dcc.Graph(
                                figure=fig_evolution,
                                # config Plotly : on retire la barre
                                # d'outils Plotly par défaut (zoom, pan...)
                                # qui pollue l'interface en B2B.
                                # On garde le téléchargement PNG seul.
                                config={
                                    "displayModeBar": False,
                                    "displaylogo": False,
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # ── Section 3 : répartition par type de structure ─────
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
    Enregistre les callbacks spécifiques à la page d'accueil.
    Vide pour l'instant : les graphiques sont statiques (pas de filtres
    sur cette page de synthèse). L'interactivité est portée par la
    page Explorer (Phase 4).

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """
    pass
