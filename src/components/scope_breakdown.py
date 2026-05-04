"""
Composant 'décomposition par scope' : graphique en barres horizontales
empilées montrant la répartition Scope 1 / Scope 2 / Scope 3 des
émissions par type de structure (ou par région selon paramètre).

Le référentiel BEGES distingue trois scopes :
  - Scope 1 : émissions directes (combustion, fuites)
  - Scope 2 : énergie achetée (électricité, chaleur)
  - Scope 3 : chaîne de valeur (achats, déplacements, déchets...)

Doc Plotly bar chart : https://plotly.com/python/bar-charts/
"""

import pandas as pd
import plotly.graph_objects as go

from src.components.charts_theme import apply_theme, COLORS


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_scope_breakdown(
    df: pd.DataFrame,
    group_by: str = "type_structure",
) -> go.Figure:
    """
    Construit un graphique à barres horizontales empilées montrant la
    décomposition Scope 1 / 2 / 3 des émissions agrégées par catégorie.

    Args:
        df (pd.DataFrame): DataFrame filtré (issu de filter_data).
        group_by (str): Colonne de regroupement, 'type_structure' par défaut.

    Returns:
        go.Figure: Graphe en barres empilées prêt à passer à dcc.Graph.
    """
    # Cas vide : on retourne une figure annotée plutôt qu'un graphe cassé.
    if df.empty:
        return _empty_figure("Aucun bilan ne correspond aux filtres.")

    # Agrégation : somme des émissions de chaque scope par groupe.
    # On somme en colonnes via .agg() avec un dict (plus lisible que
    # multiple groupby chaînés).
    aggregated = df.groupby(group_by, as_index=False).agg({
        "total_scope_1": "sum",
        "total_scope_2": "sum",
        "total_scope_3": "sum",
    })

    # On trie par total décroissant (somme des 3 scopes) pour mettre en
    # haut les groupes les plus émetteurs (lecture top-down naturelle).
    aggregated["total"] = (
        aggregated["total_scope_1"]
        + aggregated["total_scope_2"]
        + aggregated["total_scope_3"]
    )
    aggregated = aggregated.sort_values("total", ascending=True)

    # Construction de 3 traces empilées via go.Figure (plus contrôlable
    # que plotly.express pour ce cas où on veut customiser chaque scope).
    fig = go.Figure()

    # Définitions des 3 séries : (nom affiché, colonne, couleur).
    # Couleurs cohérentes avec le thème : vert profond pour Scope 1
    # (émissions directes, "sérieuses"), vert moyen pour Scope 2,
    # or pâle pour Scope 3 (chaîne de valeur, plus diffus).
    scopes = [
        ("Scope 1 — directes",   "total_scope_1", COLORS["primary"]),
        ("Scope 2 — énergie",    "total_scope_2", "#5C7A4D"),
        ("Scope 3 — indirectes", "total_scope_3", COLORS["accent"]),
    ]

    for name, column, color in scopes:
        fig.add_trace(go.Bar(
            name=name,
            # Barres horizontales : x = valeurs, y = catégories
            x=aggregated[column],
            y=aggregated[group_by],
            orientation="h",
            marker=dict(
                color=color,
                # Bordure blanche fine pour séparer visuellement les
                # segments empilés
                line=dict(color=COLORS["surface"], width=1),
            ),
            # Tooltip personnalisé : groupe + scope + valeur formatée
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{name}<br>"
                "%{x:,.0f} tCO₂eq"
                "<extra></extra>"
            ),
        ))

    # barmode='stack' : empile les 3 traces (sinon elles seraient côte-à-côte)
    fig.update_layout(
        barmode="stack",
        xaxis_title="Émissions cumulées (tCO₂eq)",
        # Pas de title sur l'axe Y : les noms de groupes parlent d'eux-mêmes
        yaxis_title=None,
    )

    apply_theme(fig, height=420, show_legend=True)
    return fig


# ─────────────────────────────────────────────────────────────────
# Helper privé
# ─────────────────────────────────────────────────────────────────

def _empty_figure(message: str) -> go.Figure:
    """Figure vide avec message centré (cas filtres trop restrictifs)."""
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
