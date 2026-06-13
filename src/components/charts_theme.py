"""
Thème graphique unifié pour l'ensemble des visualisations Plotly de l'application.
Centralise les choix de couleurs, de typographies et de mises en page pour
garantir la cohérence visuelle avec le style général CSS du site.
"""

import plotly.graph_objects as go

# ── Dictionnaire des couleurs du projet ──────────────────────────
# Ces valeurs correspondent à la charte graphique définie dans style.css
COLORS: dict[str, str] = {
    "bg":            "#FAFAF7",  # Fond général (teinte papier crème léger)
    "surface":       "#FFFFFF",  # Fond blanc des zones de graphiques
    "border":        "#E8E2D5",  # Couleur pour les lignes d'axes et de grille
    "text":          "#1A1A1A",  # Couleur des textes principaux (presque noir)
    "text_muted":    "#6B6B6B",  # Couleur pour les légendes et textes secondaires
    "primary":       "#1F3A2C",  # Vert foncé officiel (identité visuelle principale)
    "primary_light": "#5C7A4D",  # Vert moyen complémentaire
    "accent":        "#C9A961",  # Doré discret utilisé pour la mise en valeur
    "danger":        "#B91C1C",  # Rouge pour les alertes ou valeurs critiques
    "success":       "#16A34A",  # Vert pour les progrès ou valeurs positives
}

# Liste ordonnée de couleurs catégorielles pour différencier des groupes de données
CATEGORICAL: list[str] = [
    "#1F3A2C",  # Vert foncé principal
    "#5C7A4D",  # Vert mousse secondaire
    "#C9A961",  # Doré d'accentuation
    "#A37840",  # Couleur caramel complémentaire
    "#6B6B6B",  # Gris neutre de repli (ex: catégorie 'Autres')
]

# Dégradé séquentiel monochrome vert pour les analyses régulières
SEQUENTIAL_GREEN: list[str] = [
    "#FAFAF7",  # Valeur la plus faible
    "#D6DCC9",
    "#A6B79B",
    "#6F8870",
    "#3F5648",
    "#1F3A2C",  # Valeur la plus élevée
]

# Dégradé séquentiel environnemental allant du vert vertueux au rouge critique
# Utilisé pour colorier les émissions de carbone de façon intuitive (Heatmap)
SEQUENTIAL_HEATMAP: list[list] = [
    [0.00, "#1F7A4A"],  # Vert (émissions très faibles)
    [0.20, "#7FB069"],
    [0.40, "#F2D74E"],  # Jaune (transition)
    [0.60, "#F4A261"],
    [0.80, "#E76F51"],  # Orange (émissions élevées)
    [1.00, "#A91E2C"],  # Rouge (émissions critiques)
]

# Couleurs fixes attribuées à chaque scope réglementaire du bilan GES
# Scope 1 = Émissions directes (ex: combustion de fioul)
# Scope 2 = Émissions indirectes liées à l'énergie (ex: électricité)
# Scope 3 = Autres émissions indirectes (ex: chaîne logistique)
SCOPE_COLORS: dict[str, str] = {
    "scope_1": "#1F3A2C",  # Vert foncé
    "scope_2": "#5C7A4D",  # Vert moyen
    "scope_3": "#C9A961",  # Doré
}


def apply_theme(
    fig: go.Figure,
    height: int = 380,
    show_legend: bool = True,
) -> go.Figure:
    """
    Applique la charte graphique GES Insight sur un objet Figure Plotly.

    Args:
        fig (go.Figure): Figure Plotly à styliser.
        height (int): Hauteur du graphique en pixels.
        show_legend (bool): Indique s'il faut afficher la légende.

    Returns:
        go.Figure: La figure mise en conformité visuelle.
    """
    # Mise à jour globale du layout (agencement général) de la figure
    fig.update_layout(
        # Remplissage des couleurs de fond de la zone de graphique
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],

        # Choix de la typographie globale
        font=dict(
            family="DM Sans, system-ui, -apple-system, sans-serif",
            color=COLORS["text"],
            size=13,
        ),

        # Paramétrage de la typographie des titres
        title=dict(
            font=dict(
                family="Fraunces, Georgia, serif",
                size=20,
                color=COLORS["text"],
            ),
            x=0.02, # Légèrement décalé à gauche pour un effet asymétrique
            y=0.95,
        ),

        # Marges de sécurité autour de la figure
        margin=dict(t=60, b=40, l=60, r=20),
        height=height,

        # Personnalisation visuelle de l'infobulle au survol (Tooltip)
        hoverlabel=dict(
            bgcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            font=dict(
                family="DM Sans, system-ui, sans-serif",
                size=13,
                color=COLORS["text"],
            ),
        ),

        # Positionnement horizontal de la légende au-dessus du graphique
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12, color=COLORS["text_muted"]),
            bgcolor="rgba(0,0,0,0)", # Fond transparent
        ),
    )

    # Paramétrage de l'axe des abscisses (X)
    fig.update_xaxes(
        showgrid=False,                 # Masquage de la grille verticale pour alléger la lecture
        linecolor=COLORS["border"],     # Ligne d'axe fine de séparation
        tickfont=dict(color=COLORS["text_muted"]),
        title_font=dict(color=COLORS["text"], size=13),
        zeroline=False,
    )

    # Paramétrage de l'axe des ordonnées (Y)
    fig.update_yaxes(
        showgrid=True,                  # Affichage d'une grille horizontale pour lire les niveaux
        gridcolor=COLORS["border"],     # Couleur discrète pour les lignes de grille
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"]),
        title_font=dict(color=COLORS["text"], size=13),
        zeroline=False,
    )

    return fig
