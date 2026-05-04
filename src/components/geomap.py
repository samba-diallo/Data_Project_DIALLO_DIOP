"""
Composant carte choroplèthe France par région.
Livrable OBLIGATOIRE selon le cahier des charges du projet (représentation
géolocalisée). Utilise un GeoJSON local des régions françaises et joint
les agrégats d'émissions par nom de région.

Doc Plotly choropleth : https://plotly.com/python/choropleth-maps/
"""

import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Helper de thème mutualisé (palette + polices Fraunces/DM Sans)
from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_GREEN


# ─────────────────────────────────────────────────────────────────
# CHARGEMENT DU GEOJSON (une seule fois au démarrage)
# ─────────────────────────────────────────────────────────────────

# Chemin du GeoJSON France régions stocké localement (téléchargé en
# Phase 4 depuis https://france-geojson.gregoiredavid.fr/repo/regions.geojson).
# Placé dans data/raw/ pour rester avec les autres données brutes.
GEOJSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "raw", "regions-france.geojson",
)


def _load_regions_geojson() -> dict:
    """Charge le GeoJSON France régions depuis le disque (UTF-8)."""
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# Chargement à l'import : le GeoJSON est petit (~480 Ko) et ne change pas.
# On évite ainsi de relire le fichier à chaque mise à jour de la carte.
REGIONS_GEOJSON: dict = _load_regions_geojson()


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_geomap(
    df: pd.DataFrame,
    metric: str = "total_emissions",
    agg: str = "sum",
) -> go.Figure:
    """
    Génère une carte choroplèthe des régions françaises colorée par la
    métrique choisie (total ou moyenne d'émissions, nombre de bilans).

    Args:
        df (pd.DataFrame): DataFrame filtré (déjà passé par filter_data).
        metric (str): Nom de la colonne à agréger (par défaut 'total_emissions').
        agg (str): Fonction d'agrégation ('sum', 'mean', 'count').

    Returns:
        go.Figure: Carte choroplèthe Plotly prête à passer à dcc.Graph.
    """
    # Cas particulier 'count' : on compte les lignes par région, pas
    # une somme/moyenne d'une colonne numérique.
    if agg == "count":
        aggregated = (
            df.groupby("region", as_index=False)
              .size()
              .rename(columns={"size": metric})
        )
        legend_title = "Nombre de bilans"
        hover_unit = "bilans"
    else:
        aggregated = df.groupby("region", as_index=False)[metric].agg(agg)
        legend_title = "Émissions (tCO₂eq)"
        hover_unit = "tCO₂eq"

    # Construction de la choroplèthe via Plotly Express. featureidkey
    # indique à Plotly comment retrouver une région du GeoJSON à partir
    # de la valeur de 'locations' : ici properties.nom contient le nom
    # officiel INSEE qui correspond à notre colonne 'region'.
    fig = px.choropleth(
        aggregated,
        geojson=REGIONS_GEOJSON,
        locations="region",
        featureidkey="properties.nom",
        color=metric,
        # Palette séquentielle verte du thème (du clair au foncé)
        color_continuous_scale=SEQUENTIAL_GREEN,
        labels={metric: legend_title},
    )

    # update_geos : limite l'affichage à la France métropolitaine + DOM.
    # fitbounds="locations" recadre automatiquement sur les régions
    # présentes dans les données.
    fig.update_geos(
        fitbounds="locations",
        visible=False,  # masque les frontières mondiales par défaut
        bgcolor=COLORS["surface"],
    )

    # Tooltip personnalisé : nom de région en gras + valeur formatée.
    # %{z} = la valeur de la métrique colorée.
    fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>"
            f"%{{z:,.0f}} {hover_unit}"
            "<extra></extra>"
        ),
        # Bordure blanche fine entre les régions pour plus de lisibilité
        marker=dict(line=dict(color=COLORS["surface"], width=1)),
    )

    # Configuration de la barre de couleur (légende continue) :
    # horizontale en bas, alignée avec les conventions du thème.
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text=legend_title, font=dict(size=12)),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            thickness=12,
            len=0.6,
        ),
    )

    # Application du thème global (polices, marges, hoverlabel...).
    # show_legend=False car la barre de couleur sert déjà de légende.
    apply_theme(fig, height=520, show_legend=False)
    return fig
