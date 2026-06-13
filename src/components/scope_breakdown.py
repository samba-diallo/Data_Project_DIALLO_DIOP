"""
Composant 'décomposition par scope' : graphique en barres horizontales
empilées montrant la répartition Scope 1 / Scope 2 / Scope 3 des
émissions cumulées des TOP organisations émettrices.

Le référentiel BEGES distingue trois scopes :
  - Scope 1 : émissions directes (combustion, fuites)
  - Scope 2 : énergie achetée (électricité, chaleur)
  - Scope 3 : chaîne de valeur (achats, déplacements, déchets...)

Design.md spec :
  - X-axis : entreprises / organisations
  - Y-axis : émissions cumulées
  - Series : Scope 1 / 2 / 3
  - Stacked, comparable, lisible

Doc Plotly bar chart : https://plotly.com/python/bar-charts/
"""

import pandas as pd
import plotly.graph_objects as go

from src.components.charts_theme import apply_theme, COLORS, SCOPE_COLORS


# ─────────────────────────────────────────────────────────────────
# CONSTANTE - nombre de top organisations à afficher
# ─────────────────────────────────────────────────────────────────

# On limite à 15 organisations pour garder le graphe lisible. Au-delà,
# les barres deviennent trop fines et les labels s'entassent.
TOP_N: int = 15


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant graphique
# ─────────────────────────────────────────────────────────────────

def create_scope_breakdown(
    df: pd.DataFrame,
    top_n: int = TOP_N,
) -> go.Figure:
    """
    Construit un graphique à barres horizontales empilées montrant la
    décomposition Scope 1 / 2 / 3 des émissions cumulées des TOP_N
    organisations les plus émettrices (selon les filtres actifs).

    Args:
        df (pd.DataFrame): DataFrame filtré (issu de filter_data).
        top_n (int): Nombre d'organisations à afficher (par défaut 15).

    Returns:
        go.Figure: Graphe en barres empilées prêt à passer à dcc.Graph.
    """
    # Cas vide : on retourne une figure annotée plutôt qu'un graphe cassé.
    if df.empty:
        return _empty_figure("Aucun bilan ne correspond aux filtres.")

    # On exclut les bilans sans raison sociale (NaN) - on ne peut pas
    # nommer une barre "NaN", ça n'a aucun sens analytique.
    valid = df.dropna(subset=["raison_sociale"]).copy()
    if valid.empty:
        return _empty_figure("Aucune organisation identifiée dans cette sélection.")

    # Agrégation par organisation : somme des 3 scopes par raison sociale.
    # Une organisation peut avoir plusieurs bilans (années différentes,
    # méthodes différentes) - on cumule pour avoir l'empreinte totale
    # déclarée sur la période filtrée.
    aggregated = valid.groupby("raison_sociale", as_index=False).agg({
        "total_scope_1": "sum",
        "total_scope_2": "sum",
        "total_scope_3": "sum",
    })

    # Calcul du total pour le tri et la sélection des TOP_N.
    aggregated["total"] = (
        aggregated["total_scope_1"]
        + aggregated["total_scope_2"]
        + aggregated["total_scope_3"]
    )

    # On conserve les TOP_N organisations les plus émettrices, puis on
    # trie par total CROISSANT pour que la plus émettrice apparaisse en
    # haut du graphe (lecture top-down naturelle pour barres horizontales).
    top = aggregated.nlargest(top_n, "total").sort_values("total", ascending=True)

    # Truncate les noms trop longs pour éviter qu'ils ne débordent sur
    # la zone de tracé (les raisons sociales ADEME peuvent atteindre
    # 80+ caractères avec mentions juridiques complètes).
    top["raison_sociale_short"] = top["raison_sociale"].apply(
        lambda x: (x[:42] + "…") if isinstance(x, str) and len(x) > 45 else x
    )

    # Construction de 3 traces empilées via go.Figure.
    fig = go.Figure()

    # Définitions des 3 séries : (nom affiché, colonne, couleur).
    # Couleurs cohérentes avec le thème via SCOPE_COLORS centralisé.
    scopes = [
        ("Scope 1 — directes",   "total_scope_1", SCOPE_COLORS["scope_1"]),
        ("Scope 2 — énergie",    "total_scope_2", SCOPE_COLORS["scope_2"]),
        ("Scope 3 — indirectes", "total_scope_3", SCOPE_COLORS["scope_3"]),
    ]

    for name, column, color in scopes:
        fig.add_trace(go.Bar(
            name=name,
            # Barres horizontales : x = valeurs, y = catégories
            x=top[column],
            y=top["raison_sociale_short"],
            orientation="h",
            marker=dict(
                color=color,
                # Bordure blanche fine pour séparer les segments empilés
                line=dict(color=COLORS["surface"], width=1),
            ),
            # Tooltip : nom complet de l'organisation + scope + valeur.
            # On utilise customdata pour passer le nom non tronqué.
            customdata=top["raison_sociale"],
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                f"{name}<br>"
                "%{x:,.0f} tCO₂eq"
                "<extra></extra>"
            ),
        ))

    # barmode='stack' : empile les 3 traces (sinon elles seraient côte-à-côte).
    # Hauteur dynamique : 28 px par organisation + marges, plafonnée pour
    # éviter un graphe énorme si top_n est grand.
    chart_height = max(420, 60 + 28 * len(top))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Émissions cumulées (tCO₂eq)",
        yaxis_title=None,
        # bargap réduit pour un look "tableau de bord" compact mais aéré.
        bargap=0.25,
    )

    # Format des ticks X : notation SI (1k, 1M, 1G) - cohérent avec la
    # carte et lisible sur les très grandes valeurs.
    fig.update_xaxes(tickformat=".2s")

    # Application du thème + légende affichée (essentielle pour identifier
    # les 3 scopes empilés).
    apply_theme(fig, height=chart_height, show_legend=True)
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
