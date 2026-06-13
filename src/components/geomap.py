"""
Composant carte choroplèthe France par région - VERSION HEATMAP ENTERPRISE.
Livrable OBLIGATOIRE selon le cahier des charges du projet (représentation
géolocalisée).

Design "climate intelligence platform" :
  - heatmap environnementale (vert → rouge)
  - TOUTES les régions toujours visibles, même quand on filtre par région
  - région(s) sélectionnée(s) mise(s) en évidence (bordure or, halo)
  - labels des régions directement sur la carte (Scattergeo overlay)
  - cadrage France métropolitaine fixe

Doc Plotly choropleth : https://plotly.com/python/choropleth-maps/
Doc Plotly scattergeo : https://plotly.com/python/scatter-plots-on-maps/
"""

# Permet la syntaxe PEP 604 (list[str] | None) sur Python 3.9 :
# les annotations restent des chaînes et ne sont pas évaluées à l'import.
from __future__ import annotations

import json
import os

import pandas as pd
import plotly.graph_objects as go

# Helper de thème mutualisé (palette + polices Fraunces/DM Sans)
from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP


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


# Centroïdes approximatifs des 13 régions de France métropolitaine + Corse.
# Coordonnées (lat, lon) calculées manuellement à partir des préfectures
# pour ancrer les labels textuels sur la carte sans dépendre de geopandas.
# On exclut volontairement les DOM (Guadeloupe, Martinique, etc.) car le
# cadrage géographique est centré sur la France métropolitaine.
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


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_geomap(
    df_for_aggregation: pd.DataFrame,
    highlighted_regions: list[str] | None = None,
    metric: str = "total_emissions",
    agg: str = "sum",
) -> go.Figure:
    """
    Génère une carte choroplèthe HEATMAP des régions françaises.
    TOUTES les régions sont toujours rendues (contexte géographique
    préservé) ; les régions sélectionnées sont mises en évidence par
    une bordure or et un marqueur central.

    Args:
        df_for_aggregation: DataFrame filtré par année + type de structure
            UNIQUEMENT (pas par région), pour préserver la vue globale
            de la France quand on filtre par région.
        highlighted_regions: Liste optionnelle de régions à mettre en
            évidence (sélection courante du filtre Région). None ou liste
            vide = aucun highlight, vue d'ensemble normale.
        metric: Nom de la colonne à agréger (par défaut 'total_emissions').
        agg: Fonction d'agrégation ('sum', 'mean', 'count').

    Returns:
        go.Figure: Carte choroplèthe Plotly prête à passer à dcc.Graph.
    """
    # Cas vide global : aucune donnée du tout pour les filtres année/structure.
    if df_for_aggregation.empty:
        return _empty_map("Aucune donnée pour les filtres sélectionnés.")

    # Agrégation des émissions par région SUR L'ENSEMBLE de la France
    # (pas seulement la sélection régionale). C'est la clé du fix : la
    # carte garde toujours toutes les régions visibles avec leur valeur.
    if agg == "count":
        aggregated = (
            df_for_aggregation.groupby("region", as_index=False)
              .size()
              .rename(columns={"size": metric})
        )
        legend_title = "Nombre de bilans"
        hover_unit = "bilans"
    else:
        aggregated = df_for_aggregation.groupby("region", as_index=False)[metric].agg(agg)
        legend_title = "Émissions (tCO₂eq)"
        hover_unit = "tCO₂eq"

    # Bornes communes pour l'échelle de couleur : on les fige pour que la
    # palette reste cohérente quand on highlight (sinon le 2e trace
    # recalculerait sa propre échelle et casserait la lecture).
    z_min = float(aggregated[metric].min())
    z_max = float(aggregated[metric].max())

    # Construction figure manuelle (go.Figure + add_trace) plutôt que via
    # plotly.express : permet d'empiler plusieurs traces (choropleth de
    # base + overlay des régions sélectionnées + labels textuels).
    fig = go.Figure()

    # ── TRACE 1 : Choropleth de base (TOUTES les régions) ───────
    # Bordure blanche fine pour distinguer les régions entre elles.
    fig.add_trace(go.Choropleth(
        geojson=REGIONS_GEOJSON,
        locations=aggregated["region"],
        z=aggregated[metric],
        featureidkey="properties.nom",
        colorscale=SEQUENTIAL_HEATMAP,
        zmin=z_min,
        zmax=z_max,
        marker_line_color=COLORS["surface"],
        marker_line_width=1.2,
        colorbar=dict(
            title=dict(
                text=legend_title,
                font=dict(size=12, color=COLORS["text_muted"]),
                side="top",
            ),
            orientation="h",
            yanchor="bottom",
            y=-0.06,
            xanchor="center",
            x=0.5,
            thickness=14,
            len=0.65,
            tickformat=".2s",
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

    # ── TRACE 2 : Overlay HIGHLIGHT (bordure or sur sélectionnées) ──
    # Si l'utilisateur a sélectionné une ou plusieurs régions, on rajoute
    # une trace par-dessus avec un fond transparent (pour ne pas masquer
    # les couleurs d'émissions) et une grosse bordure or pour signaler
    # visuellement la sélection. Toutes les autres régions restent visibles.
    if highlighted_regions:
        # On ne garde que les régions effectivement présentes dans nos
        # données pour éviter les warnings Plotly sur featureidkey orphelin.
        present = [r for r in highlighted_regions if r in aggregated["region"].values]
        if present:
            fig.add_trace(go.Choropleth(
                geojson=REGIONS_GEOJSON,
                locations=present,
                z=[1] * len(present),  # z dummy : on ne veut pas colorer
                featureidkey="properties.nom",
                # Colorscale 100% transparente : la couleur d'émissions
                # de la trace 1 reste visible en dessous.
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                marker_line_color=COLORS["accent"],   # or pâle = accent
                marker_line_width=4.0,                # bordure prominente
                showscale=False,
                hoverinfo="skip",   # tooltip déjà fourni par la trace 1
                name="Sélection",
                showlegend=False,
            ))

    # ── TRACE 3 : Labels des régions (Scattergeo texte) ─────────
    # Affiche le nom de chaque région à son centroïde. Lecture immédiate
    # sans hover, comme sur une carte météo professionnelle.
    label_lons = []
    label_lats = []
    label_texts = []
    for region, (lat, lon) in REGION_CENTROIDS.items():
        # On ne label que les régions qui ont des données dans la sélection
        # (sinon on pollue avec des labels sur des zones sans émissions).
        if region in aggregated["region"].values:
            label_lats.append(lat)
            label_lons.append(lon)
            # Format du label : nom court (sans tirets pour respiration).
            # Mise en gras si la région est sélectionnée pour renforcer
            # la hiérarchie visuelle.
            short_name = _short_region_name(region)
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

    # update_geos : cadrage France métropolitaine fixe. On ne change PAS
    # ce cadrage selon la sélection (Design.md : "preserve overall spatial
    # understanding"). Mercator centré sur la France hexagonale + Corse.
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

    # Marges réduites pour maximiser la surface utile de la carte.
    fig.update_layout(margin=dict(t=20, b=60, l=10, r=10))

    # Application du thème global, hauteur maintenue à 720px.
    apply_theme(fig, height=720, show_legend=False)
    return fig


# ─────────────────────────────────────────────────────────────────
# Helpers privés
# ─────────────────────────────────────────────────────────────────

def _short_region_name(region: str) -> str:
    """
    Raccourcit certains noms de régions très longs pour l'affichage en
    superposition sur la carte (où l'espace est limité).
    """
    # Mappings spécifiques pour les noms qui débordent sinon sur la carte.
    abbreviations = {
        "Provence-Alpes-Côte d'Azur": "PACA",
        "Bourgogne-Franche-Comté": "BFC",
        "Centre-Val de Loire": "Centre-VdL",
        "Auvergne-Rhône-Alpes": "Auv.-Rhône-Alpes",
    }
    return abbreviations.get(region, region)


def _empty_map(message: str) -> go.Figure:
    """Carte vide avec message centré (filtres trop restrictifs)."""
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
