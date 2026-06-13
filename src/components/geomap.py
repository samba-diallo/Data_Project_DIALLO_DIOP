"""
Composant de carte géographique (Géomap) pour afficher les bilans GES par région.
Génère une carte de France choroplèthe interactive où l'intensité des couleurs
reflète le volume des émissions de gaz à effet de serre.
"""

from __future__ import annotations

import json
import os
import pandas as pd
import plotly.graph_objects as go

# Importation du thème de couleurs et de typographie partagé
from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP

# Détermination du chemin d'accès absolu au fichier GeoJSON contenant les contours des régions
GEOJSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "raw", "regions-france.geojson",
)


def _load_regions_geojson() -> dict:
    """
    Charge en mémoire les contours géographiques des régions de France (GeoJSON).

    Returns:
        dict: Objet dictionnaire contenant les structures géométriques.
    """
    # Ouverture et lecture du fichier avec encodage UTF-8
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# Chargement unique du GeoJSON lors du chargement du module pour optimiser les performances
REGIONS_GEOJSON: dict = _load_regions_geojson()

# Coordonnées géographiques de latitude et longitude choisies pour placer les étiquettes textuelles
# de manière lisible au centre (centroïde) de chaque région de France métropolitaine
REGION_CENTROIDS: dict[str, tuple[float, float]] = {
    "Auvergne-Rhône-Alpes":      (45.5, 4.6),
    "Bourgogne-Franche-Comté":   (47.3, 4.9),
    "Bretagne":                  (48.2, -2.9),
    "Centre-Val de Loire":       (47.5, 1.7),
    "Corse":                     (42.1, 9.1),
    "Grand Est":                 (48.7, 5.5),
    "Hauts-de-France":           (50.1, 2.8),
    "Île-de-France":             (48.85, 2.45),
    "Normandie":                 (49.2, 0.4),
    "Nouvelle-Aquitaine":        (45.3, 0.4),
    "Occitanie":                 (43.8, 1.9),
    "Pays de la Loire":          (47.5, -0.7),
    "Provence-Alpes-Côte d'Azur":(43.95, 6.0),
}


def create_geomap(
    df_for_aggregation: pd.DataFrame,
    highlighted_regions: list[str] | None = None,
    metric: str = "total_emissions",
    agg: str = "sum",
) -> go.Figure:
    """
    Génère la figure Plotly de la carte choroplèthe de France.

    Args:
        df_for_aggregation (pd.DataFrame): Données à agréger par région.
        highlighted_regions (list[str] | None): Liste des régions sélectionnées à mettre en valeur.
        metric (str): Colonne numérique à analyser (par exemple, total_emissions).
        agg (str): Type d'agrégation (sum, mean, count).

    Returns:
        go.Figure: Objet Figure de Plotly représentant la carte.
    """
    # Si le jeu de données transmis est vide, on renvoie une carte vide avec un message
    if df_for_aggregation.empty:
        return _empty_map("Aucune donnée pour les filtres sélectionnés.")

    # Agrégation des valeurs par région
    if agg == "count":
        aggregated = (
            df_for_aggregation.groupby("region", as_index=False)
              .size()
              .rename(columns={"size": metric})
        )
        legend_title = "Nombre de bilans"
        hover_unit = "bilans"
    else:
        aggregated = df_for_aggregation.groupby("region", as_index=False)[[metric]].agg(agg)
        legend_title = "Émissions (tCO₂eq)"
        hover_unit = "tCO₂eq"

    # Récupération des valeurs extrêmes pour calibrer l'échelle de couleurs
    z_min = float(aggregated[metric].min())
    z_max = float(aggregated[metric].max())

    # Création d'une figure vierge
    fig = go.Figure()

    # ── ÉTAPE 1 : Tracé de la carte de base (Choroplèthe) ───────
    # Coloration de chaque région en fonction de sa valeur d'émission
    fig.add_trace(go.Choropleth(
        geojson=REGIONS_GEOJSON,
        locations=aggregated["region"],
        z=aggregated[metric],
        featureidkey="properties.nom", # Propriété du GeoJSON servant d'identifiant
        colorscale=SEQUENTIAL_HEATMAP,  # Palette séquentielle (du vert au rouge)
        zmin=z_min,
        zmax=z_max,
        marker_line_color=COLORS["surface"], # Bordures inter-régions de couleur claire
        marker_line_width=1.2,
        colorbar=dict(
            title=dict(
                text=legend_title,
                font=dict(size=12, color=COLORS["text_muted"]),
                side="top",
            ),
            orientation="h",       # Position horizontale de la barre de légende
            yanchor="bottom",
            y=-0.06,
            xanchor="center",
            x=0.5,
            thickness=14,
            len=0.65,
            tickformat=".2s",      # Format abrégé des nombres (K, M, G...)
            tickfont=dict(size=11, color=COLORS["text_muted"]),
            outlinewidth=0,
        ),
        hovertemplate=(
            "<b>%{location}</b><br>"
            f"%{{z:,.0f}} {hover_unit}"
            "<extra></extra>"
        ),
        name="Émissions",
        showscale=True,
    ))

    # ── ÉTAPE 2 : Tracé de mise en évidence (Contour de sélection) ──
    # Si des régions sont sélectionnées, on ajoute une sur-couche avec des bordures épaisses dorées
    if highlighted_regions:
        present = [r for r in highlighted_regions if r in aggregated["region"].values]
        if present:
            fig.add_trace(go.Choropleth(
                geojson=REGIONS_GEOJSON,
                locations=present,
                z=[1] * len(present), # Donnée dummy non affichée
                featureidkey="properties.nom",
                # Rendu du fond transparent pour laisser voir la coloration d'origine
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                marker_line_color=COLORS["accent"],   # Couleur dorée d'accentuation
                marker_line_width=4.0,                # Bordure épaisse
                showscale=False,
                hoverinfo="skip",                     # Pas de double infobulle au survol
                name="Sélection",
                showlegend=False,
            ))

    # ── ÉTAPE 3 : Superposition des étiquettes de texte ───────
    # Affiche le nom des régions directement à leur emplacement pour une lecture immédiate
    label_lons = []
    label_lats = []
    label_texts = []
    for region, (lat, lon) in REGION_CENTROIDS.items():
        if region in aggregated["region"].values:
            label_lats.append(lat)
            label_lons.append(lon)
            short_name = _short_region_name(region)
            # Met le texte en gras si la région fait partie de la sélection active
            if highlighted_regions and region in highlighted_regions:
                label_texts.append(f"<b>{short_name}</b>")
            else:
                label_texts.append(short_name)

    fig.add_trace(go.Scattergeo(
        lon=label_lons,
        lat=label_lats,
        text=label_texts,
        mode="text",
        textfont=dict(
            family="DM Sans, sans-serif",
            size=11,
            color=COLORS["text"],
        ),
        hoverinfo="skip",
        showlegend=False,
        name="Labels",
    ))

    # Configuration de la projection géographique et du centrage sur la France métropolitaine
    fig.update_geos(
        visible=False,
        projection_type="mercator",
        center={"lat": 46.5, "lon": 2.5},
        lonaxis_range=[-5.5, 10.0],
        lataxis_range=[41.0, 51.5],
        bgcolor=COLORS["surface"],
        showframe=False,
        showcoastlines=False,
    )

    # Réglage des marges de la figure pour occuper un maximum d'espace
    fig.update_layout(margin=dict(t=20, b=60, l=10, r=10))

    # Application du thème de styles global
    apply_theme(fig, height=720, show_legend=False)
    return fig


def _short_region_name(region: str) -> str:
    """
    Raccourcit les noms longs de certaines régions pour optimiser l'affichage cartographique.

    Args:
        region (str): Nom complet de la région.

    Returns:
        str: Nom raccourci ou d'origine.
    """
    abbreviations = {
        "Provence-Alpes-Côte d'Azur": "PACA",
        "Bourgogne-Franche-Comté": "BFC",
        "Centre-Val de Loire": "Centre-VdL",
        "Auvergne-Rhône-Alpes": "Auv.-Rhône-Alpes",
    }
    return abbreviations.get(region, region)


def _empty_map(message: str) -> go.Figure:
    """
    Génère une figure de remplacement affichant un message textuel au centre.

    Args:
        message (str): Message à afficher à l'utilisateur.

    Returns:
        go.Figure: Figure Plotly contenant l'annotation.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family="DM Sans", size=14, color=COLORS["text_muted"]),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    apply_theme(fig, height=720, show_legend=False)
    return fig
