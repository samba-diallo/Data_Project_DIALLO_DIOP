"""
Composant Heat Timeline : visualisation horizontale des années 2010-2025
colorées par intensité d'émissions (vert → rouge). Chaque année devient
une "cellule analytique" lisible d'un coup d'œil.

Inspiré des plateformes de climate intelligence (Bloomberg ESG, ADEME).
Le composant est synchronisé avec les filtres (année + structure) et met
en évidence visuellement la plage sélectionnée par le RangeSlider.

Rendu via plotly.go.Bar avec colorscale : permet d'afficher les années
comme des barres courtes/uniformes colorées par intensité, avec la
plage active surlignée.
"""

import pandas as pd
import plotly.graph_objects as go

from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP
from src.utils.common_functions import YEAR_MIN, YEAR_MAX


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_heat_timeline(
    df: pd.DataFrame,
    selected_range: tuple[int, int] | None = None,
) -> go.Figure:
    """
    Construit la heat timeline année par année (2010-2025).
    Chaque cellule représente une année, colorée par intensité d'émissions
    cumulées (vert = faible, rouge = critique). La plage sélectionnée est
    encadrée pour signaler le périmètre actif.

    Args:
        df: DataFrame filtré par structure UNIQUEMENT (toutes années
            visibles pour montrer la trajectoire complète).
        selected_range: Tuple (year_start, year_end) à mettre en évidence.
            Si None, on prend toute la période.

    Returns:
        go.Figure: Heat timeline Plotly prête à passer à dcc.Graph.
    """
    # Calcul des émissions totales par année sur toute la période 2010-2025.
    # On force la présence de toutes les années (même celles à 0) avec
    # reindex pour que la timeline soit toujours complète visuellement.
    yearly = (
        df.groupby("annee_reporting")["total_emissions"]
          .sum()
          .reindex(range(YEAR_MIN, YEAR_MAX + 1), fill_value=0)
          .reset_index()
    )
    yearly.columns = ["annee", "emissions"]

    # Plage sélectionnée par défaut : toute la période.
    if selected_range is None:
        selected_range = (YEAR_MIN, YEAR_MAX)

    start_year, end_year = selected_range

    # Marquer chaque année comme "in_selection" ou "out_selection" pour
    # piloter l'opacité visuelle (les années hors sélection sont atténuées).
    yearly["in_selection"] = yearly["annee"].between(start_year, end_year)
    yearly["opacity"] = yearly["in_selection"].map({True: 1.0, False: 0.35})

    # Conversion en MtCO2eq pour les hovers (les valeurs brutes en
    # tonnes deviennent vite illisibles à 9-10 chiffres).
    yearly["emissions_mt"] = yearly["emissions"] / 1_000_000

    # Construction de la figure : barres uniformes (height = 1, color =
    # intensité). On utilise une seule trace go.Bar avec couleur par
    # marker.color (mapping interne via colorscale).
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly["annee"],
        y=[1] * len(yearly),  # hauteur uniforme : on veut une bande, pas un chart
        marker=dict(
            color=yearly["emissions"],
            colorscale=SEQUENTIAL_HEATMAP,
            showscale=False,
            opacity=yearly["opacity"],
            line=dict(color=COLORS["surface"], width=2),
        ),
        # Affichage de l'année dans la barre pour lecture immédiate
        text=yearly["annee"].astype(str),
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(
            family="DM Sans, sans-serif",
            size=11,
            color="#FFFFFF",
            weight=600,
        ),
        # Hover : année + émissions en Mt
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

    # Annotation des bornes sélectionnées : petite flèche en bas indiquant
    # le périmètre actif (renforce visuellement le RangeSlider du dessus).
    fig.add_annotation(
        x=start_year, y=-0.4,
        xref="x", yref="y",
        text=f"<b>{start_year}</b>",
        showarrow=False,
        font=dict(family="DM Sans", size=11, color=COLORS["primary"]),
    )
    if end_year != start_year:
        fig.add_annotation(
            x=end_year, y=-0.4,
            xref="x", yref="y",
            text=f"<b>{end_year}</b>",
            showarrow=False,
            font=dict(family="DM Sans", size=11, color=COLORS["primary"]),
        )

    # Configuration des axes : on retire tout (titre, ticks, grille)
    # pour ne garder que la "bande" colorée et propre.
    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,  # années déjà inscrites dans les barres
        zeroline=False,
        showline=False,
        range=[YEAR_MIN - 0.5, YEAR_MAX + 0.5],
    )
    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        showline=False,
        range=[-0.6, 1.1],
        fixedrange=True,
    )

    # Layout compact : timeline = bande de 110px de hauteur, marges très
    # réduites pour un look "barre de navigation analytique".
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
