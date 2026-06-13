"""
Composant Heat Timeline.
Affiche une frise chronologique horizontale (de 2010 à 2025) sous forme de cellules de couleurs.
La couleur de chaque année indique l'intensité globale des émissions de carbone (du vert au rouge).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

# Importation du thème graphique commun
from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP

# Bornes de début et fin de la frise chronologique
from src.utils.common_functions import YEAR_MIN, YEAR_MAX


def create_heat_timeline(
    df: pd.DataFrame,
    selected_range: tuple[int, int] | None = None,
) -> go.Figure:
    """
    Construit la figure Plotly de la frise chronologique thermique.

    Args:
        df (pd.DataFrame): Données à analyser par année.
        selected_range (tuple[int, int] | None): Intervalle d'années sélectionné (début, fin).

    Returns:
        go.Figure: Figure Plotly représentant la frise chronologique.
    """
    # Agrégation des émissions globales par année de reporting.
    # reindex() garantit que toutes les années entre les bornes minimales et maximales
    # sont présentes, même si leurs émissions sont nulles.
    yearly = (
        df.groupby("annee_reporting")["total_emissions"]
          .sum()
          .reindex(range(YEAR_MIN, YEAR_MAX + 1), fill_value=0)
          .reset_index()
    )
    # Renommage explicite des colonnes
    yearly.columns = ["annee", "emissions"]

    # Si aucune plage d'années n'est sélectionnée, on prend toute la période par défaut
    if selected_range is None:
        selected_range = (YEAR_MIN, YEAR_MAX)

    start_year, end_year = selected_range

    # Détection des années qui font partie de l'intervalle sélectionné
    yearly["in_selection"] = yearly["annee"].between(start_year, end_year)
    
    # Application d'une opacité différente : 100% si sélectionnée, atténuée à 35% si hors sélection
    yearly["opacity"] = yearly["in_selection"].map({True: 1.0, False: 0.35})

    # Conversion des émissions en millions de tonnes (MtCO2eq) pour simplifier l'affichage
    yearly["emissions_mt"] = yearly["emissions"] / 1_000_000

    fig = go.Figure()

    # Ajout du tracé des barres uniformes de la frise chronologique
    fig.add_trace(go.Bar(
        x=yearly["annee"],
        y=[1] * len(yearly),  # Hauteur uniforme pour toutes les barres afin de former une bande continue
        marker=dict(
            color=yearly["emissions"],
            colorscale=SEQUENTIAL_HEATMAP,
            showscale=False,
            opacity=yearly["opacity"],
            line=dict(color=COLORS["surface"], width=2), # Bordures blanches fines
        ),
        # Affichage direct du texte de l'année à l'intérieur de chaque barre
        text=yearly["annee"].astype(str),
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(
            family="DM Sans, sans-serif",
            size=11,
            color="#FFFFFF",
            weight=600,
        ),
        # Données personnalisées transmises à l'infobulle au survol
        customdata=yearly[["emissions_mt", "in_selection"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{customdata[0]:,.1f} MtCO₂eq<br>"
            "<extra></extra>"
        ),
        hoverlabel=dict(
            bgcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            font=dict(family="DM Sans", size=12, color=COLORS["text"]),
        ),
        showlegend=False,
    ))

    # Ajout d'une annotation textuelle en bas à gauche pour marquer le début de la sélection
    fig.add_annotation(
        x=start_year, y=-0.4,
        xref="x", yref="y",
        text=f"<b>{start_year}</b>",
        showarrow=False,
        font=dict(family="DM Sans", size=11, color=COLORS["primary"]),
    )
    # Ajout d'une annotation textuelle en bas à droite pour marquer la fin de la sélection
    if end_year != start_year:
        fig.add_annotation(
            x=end_year, y=-0.4,
            xref="x", yref="y",
            text=f"<b>{end_year}</b>",
            showarrow=False,
            font=dict(family="DM Sans", size=11, color=COLORS["primary"]),
        )

    # Masquage des graduations et grilles de l'axe des abscisses (X)
    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        showline=False,
        range=[YEAR_MIN - 0.5, YEAR_MAX + 0.5],
    )
    # Masquage de l'axe des ordonnées (Y)
    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        showline=False,
        range=[-0.6, 1.1],
        fixedrange=True,
    )

    # Réglage de la hauteur compacte et des marges minimales de la frise chronologique
    fig.update_layout(
        bargap=0.04,
        margin=dict(t=10, b=10, l=10, r=10),
        height=110,
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        showlegend=False,
        font=dict(
            family="DM Sans, sans-serif",
            color=COLORS["text"],
            size=12,
        ),
        hoverlabel=dict(
            bgcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            font=dict(family="DM Sans", size=12, color=COLORS["text"]),
        ),
    )
    return fig
