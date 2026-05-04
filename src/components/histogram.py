"""
Composant histogramme dynamique des émissions totales par bilan.
Livrable OBLIGATOIRE selon le cahier des charges du projet.

La distribution des émissions BEGES est très asymétrique (médiane ~5 600 tCO2eq,
max > 3 milliards) : on utilise une échelle logarithmique sur l'axe X pour
rendre la distribution lisible.

Doc Plotly histogram : https://plotly.com/python/histograms/
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.components.charts_theme import apply_theme, COLORS


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_histogram(df: pd.DataFrame) -> go.Figure:
    """
    Construit l'histogramme de distribution des émissions totales (tCO2eq)
    en échelle logarithmique. Affiche également la médiane et la moyenne
    en lignes verticales annotées pour contextualiser la distribution.

    Args:
        df (pd.DataFrame): DataFrame filtré (issu de filter_data).

    Returns:
        go.Figure: Histogramme Plotly prêt à passer à dcc.Graph.
    """
    # On ne garde que les bilans avec émissions strictement positives :
    # log10(0) = -inf, donc impossible à représenter sur axe log.
    # Les bilans à 0 sont rares (organisation qui déclare 0 émission est
    # quasi inexistante) et faussent l'analyse.
    valid = df[df["total_emissions"] > 0].copy()

    # Si plus aucune ligne après filtrage, on retourne une figure vide
    # avec un message — évite un graphe cassé.
    if valid.empty:
        return _build_empty_figure(
            "Aucun bilan ne correspond aux filtres sélectionnés."
        )

    # Calcul de la transformation log10 pour utiliser des bins linéaires
    # sur l'axe log (sinon Plotly génère des bins de tailles inégales en
    # log scale). On convertit les bornes en log10 puis on créé 30 bins.
    log_values = np.log10(valid["total_emissions"])
    nbins = 30

    fig = px.histogram(
        valid,
        x="total_emissions",
        # log_x=True : axe X en échelle log10, les ticks deviennent
        # 1, 10, 100, 1k, 10k, 100k, 1M, 10M...
        log_x=True,
        nbins=nbins,
        labels={
            "total_emissions": "Émissions totales (tCO₂eq, échelle logarithmique)",
            "count": "Nombre de bilans",
        },
    )

    # Personnalisation des barres : couleur primaire avec opacité 0.85,
    # bordure plus foncée pour distinguer les bins.
    fig.update_traces(
        marker=dict(
            color=COLORS["primary"],
            opacity=0.85,
            line=dict(color=COLORS["primary"], width=1),
        ),
        # Tooltip personnalisé : range du bin + count.
        hovertemplate=(
            "<b>De %{x:,.0f} tCO₂eq</b><br>"
            "%{y:,.0f} bilans"
            "<extra></extra>"
        ),
    )

    # Calcul des statistiques descriptives pour les annoter sur le graphe.
    # médiane = valeur typique (resistente aux outliers, contrairement
    # à la moyenne très tirée par les gros émetteurs).
    median_val = valid["total_emissions"].median()
    mean_val = valid["total_emissions"].mean()

    # Lignes verticales (vline) pour la médiane et la moyenne.
    # add_vline ajoute une ligne + un label en haut.
    fig.add_vline(
        x=median_val,
        line=dict(color=COLORS["accent"], width=2, dash="dash"),
        annotation_text=f"Médiane : {median_val:,.0f}",
        annotation_position="top",
        annotation=dict(
            font=dict(color=COLORS["accent"], size=11, family="DM Sans"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLORS["accent"],
            borderwidth=1,
            borderpad=4,
        ),
    )
    fig.add_vline(
        x=mean_val,
        line=dict(color=COLORS["danger"], width=2, dash="dot"),
        annotation_text=f"Moyenne : {mean_val:,.0f}",
        # On positionne légèrement plus bas pour éviter le chevauchement
        # avec l'annotation de la médiane lorsque les deux sont proches.
        annotation_position="top right",
        annotation=dict(
            font=dict(color=COLORS["danger"], size=11, family="DM Sans"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLORS["danger"],
            borderwidth=1,
            borderpad=4,
        ),
    )

    # Configuration spécifique des axes pour l'échelle log
    fig.update_xaxes(
        # Format des ticks : sans notation scientifique, séparateurs de
        # milliers (norme française approximée par espace via tickformat).
        tickformat=",",
    )
    fig.update_yaxes(title_text="Nombre de bilans")

    apply_theme(fig, height=420, show_legend=False)
    return fig


# ─────────────────────────────────────────────────────────────────
# Helper privé - figure vide en cas de filtres trop restrictifs
# ─────────────────────────────────────────────────────────────────

def _build_empty_figure(message: str) -> go.Figure:
    """Construit une figure vide avec un message centré (état edge-case)."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family="DM Sans", size=14, color=COLORS["text_muted"]),
    )
    # On masque les axes puisqu'il n'y a rien à représenter
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    apply_theme(fig, height=420, show_legend=False)
    return fig
