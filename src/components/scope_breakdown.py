"""
Composant de décomposition par Scope carbone (Scope 1, 2, et 3).
Construit un graphique à barres horizontales empilées pour visualiser la part de chaque scope
dans les émissions des plus grandes organisations.
"""

import pandas as pd
import plotly.graph_objects as go

# Importation du thème de styles
from src.components.charts_theme import apply_theme, COLORS, SCOPE_COLORS

# Nombre maximum d'organisations affichées
TOP_N: int = 15


def create_scope_breakdown(
    df: pd.DataFrame,
    top_n: int = TOP_N,
) -> go.Figure:
    """
    Construit le graphique de répartition par Scope.

    Args:
        df (pd.DataFrame): Données filtrées.
        top_n (int): Nombre maximal d'organisations à tracer.

    Returns:
        go.Figure: Figure Plotly configurée.
    """
    # Si les données sont vides, on renvoie une figure vide avec un message
    if df.empty:
        return _empty_figure("Aucun bilan ne correspond aux filtres.")

    # Nettoyage pour exclure les bilans n'ayant pas de raison sociale
    valid = df.dropna(subset=["raison_sociale"]).copy()
    if valid.empty:
        return _empty_figure("Aucune organisation identifiée dans cette sélection.")

    # Agrégation des trois types d'émissions (Scope 1, 2, 3) par raison sociale
    aggregated = valid.groupby("raison_sociale", as_index=False).agg({
        "total_scope_1": "sum",
        "total_scope_2": "sum",
        "total_scope_3": "sum",
    })

    # Calcul des émissions totales cumulées pour chaque organisation
    aggregated["total"] = (
        aggregated["total_scope_1"]
        + aggregated["total_scope_2"]
        + aggregated["total_scope_3"]
    )

    # Récupération du Top N et tri par ordre croissant pour l'affichage horizontal
    top = aggregated.nlargest(top_n, "total").sort_values("total", ascending=True)

    # Tronquage du nom des organisations pour optimiser l'affichage sur l'axe Y
    top["raison_sociale_short"] = top["raison_sociale"].apply(
        lambda x: (x[:42] + "…") if isinstance(x, str) and len(x) > 45 else x
    )

    fig = go.Figure()

    # Définition des informations de tracé pour chacun des trois Scopes
    scopes = [
        ("Scope 1 — directes",   "total_scope_1", SCOPE_COLORS["scope_1"]),
        ("Scope 2 — énergie",    "total_scope_2", SCOPE_COLORS["scope_2"]),
        ("Scope 3 — indirectes", "total_scope_3", SCOPE_COLORS["scope_3"]),
    ]

    # Ajout d'une trace de barre pour chaque scope
    for name, column, color in scopes:
        fig.add_trace(go.Bar(
            name=name,
            x=top[column],
            y=top["raison_sociale_short"],
            orientation="h",
            marker=dict(
                color=color,
                line=dict(color=COLORS["surface"], width=1), # Séparateur blanc
            ),
            customdata=top["raison_sociale"],
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                f"{name}<br>"
                "%{x:,.0f} tCO₂eq"
                "<extra></extra>"
            ),
        ))

    # Calcul dynamique de la hauteur du conteneur du graphique
    chart_height = max(420, 60 + 28 * len(top))

    # Configuration du mode d'empilement (barmode="stack")
    fig.update_layout(
        barmode="stack",
        xaxis_title="Émissions cumulées (tCO₂eq)",
        yaxis_title=None,
        bargap=0.25,
    )

    # Formatage de l'axe X pour afficher les grands nombres
    fig.update_xaxes(tickformat=".2s")

    # Application du thème graphique avec affichage de la légende des Scopes
    apply_theme(fig, height=chart_height, show_legend=True)
    return fig


def _empty_figure(message: str) -> go.Figure:
    """
    Génère un graphique vierge avec une note centrale en cas d'absence de données.

    Args:
        message (str): Texte explicatif à afficher.

    Returns:
        go.Figure: Graphique vide Plotly contenant l'annotation.
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
    apply_theme(fig, height=420, show_legend=False)
    return fig
