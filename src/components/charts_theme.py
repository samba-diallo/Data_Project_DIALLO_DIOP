"""
Thème central pour tous les graphiques Plotly du dashboard.
Centralise la palette de couleurs, les polices, les marges et les
options de layout pour garantir une cohérence visuelle entre les
graphiques et le reste de l'interface (assets/style.css).

Doc Plotly layout : https://plotly.com/python/reference/layout/
"""

# Type hint pour préciser que apply_theme accepte une figure Plotly
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────────
# PALETTE - en miroir des variables CSS de assets/style.css
# ─────────────────────────────────────────────────────────────────

# Dictionnaire des couleurs principales : on duplique ici les valeurs
# définies dans :root de style.css. Plotly travaille en hex inline,
# il ne peut pas lire les variables CSS — d'où la duplication.
COLORS: dict[str, str] = {
    "bg":            "#FAFAF7",  # fond principal off-white papier
    "surface":       "#FFFFFF",  # fond des graphes (carte sur papier)
    "border":        "#E8E2D5",  # gridlines, axes
    "text":          "#1A1A1A",  # texte principal
    "text_muted":    "#6B6B6B",  # legendes, ticks
    "primary":       "#1F3A2C",  # vert profond (accent principal)
    "primary_light": "#5C7A4D",  # vert mousse (variation)
    "accent":        "#C9A961",  # or pâle (highlights ponctuels)
    "danger":        "#B91C1C",  # alertes
    "success":       "#16A34A",  # progrès
}


# Palette catégorielle pour distinguer plusieurs séries (ex: types
# de structure). Ordre choisi pour rester lisible à 5 catégories
# maximum, du plus contrasté au plus discret.
CATEGORICAL: list[str] = [
    "#1F3A2C",  # vert profond — catégorie dominante
    "#5C7A4D",  # vert mousse
    "#C9A961",  # or pâle
    "#A37840",  # caramel
    "#6B6B6B",  # gris (catégorie résiduelle "Autres")
]


# Échelle séquentielle pour les cartes choroplèthes (Phase 4).
# Du plus clair (faible) au plus foncé (élevé) — convention scientifique.
SEQUENTIAL_GREEN: list[str] = [
    "#FAFAF7",  # quasi blanc (très faible)
    "#D6DCC9",  # vert pâle
    "#A6B79B",  # vert moyen clair
    "#6F8870",  # vert moyen
    "#3F5648",  # vert foncé
    "#1F3A2C",  # vert profond (très élevé)
]


# Échelle ENVIRONNEMENTALE (heatmap) pour la cartographie GES.
# Inspirée des cartes météo / plateformes climatiques professionnelles :
# du vert (faible) au rouge (critique) en passant par jaune et orange.
# Plus parlante intuitivement qu'un dégradé monochrome pour l'utilisateur
# final - tout le monde lit "vert = bon, rouge = problème" sans légende.
SEQUENTIAL_HEATMAP: list[list] = [
    [0.00, "#1F7A4A"],  # vert profond - faibles émissions
    [0.20, "#7FB069"],  # vert clair
    [0.40, "#F2D74E"],  # jaune
    [0.60, "#F4A261"],  # orange clair
    [0.80, "#E76F51"],  # orange foncé
    [1.00, "#A91E2C"],  # rouge profond - émissions critiques
]


# Couleurs des trois scopes BEGES (cohérentes sur tout le dashboard).
# Convention : Scope 1 (directes) = couleur principale du thème,
# Scope 2 (énergie) = vert mousse intermédiaire, Scope 3 (chaîne de
# valeur, le plus diffus) = or pâle pour différencier visuellement.
SCOPE_COLORS: dict[str, str] = {
    "scope_1": "#1F3A2C",  # vert profond (directes)
    "scope_2": "#5C7A4D",  # vert mousse (énergie)
    "scope_3": "#C9A961",  # or pâle (indirectes)
}


# ─────────────────────────────────────────────────────────────────
# APPLICATION DU THEME
# ─────────────────────────────────────────────────────────────────

def apply_theme(
    fig: go.Figure,
    height: int = 380,
    show_legend: bool = True,
) -> go.Figure:
    """
    Applique le thème GES Insight à une figure Plotly.

    Args:
        fig (go.Figure): Figure Plotly à thématiser.
        height (int): Hauteur du graphique en pixels (par défaut 380px).
        show_legend (bool): Affiche ou non la légende.

    Returns:
        go.Figure: La même figure, modifiée en place et retournée pour
                   permettre le chaînage (fluent interface).
    """
    # update_layout permet de modifier toutes les options du layout en
    # un seul appel. Plus pratique que d'enchaîner fig.update_xaxes(),
    # fig.update_yaxes(), etc.
    fig.update_layout(
        # Fond de la zone graphique : blanc pur (carte sur papier)
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],

        # Police globale : DM Sans, fallback system-ui si DM Sans absent
        # (police de secours du navigateur, jamais 100% identique mais
        # garantit que rien n'est cassé si Google Fonts ne charge pas).
        font=dict(
            family="DM Sans, system-ui, -apple-system, sans-serif",
            color=COLORS["text"],
            size=13,
        ),

        # Titre du graphique : Fraunces serif, plus large
        title=dict(
            font=dict(
                family="Fraunces, Georgia, serif",
                size=20,
                color=COLORS["text"],
            ),
            # x=0.02 : aligné à gauche (pas centré, plus éditorial)
            x=0.02,
            # y plus bas pour rapprocher le titre du graphique
            y=0.95,
        ),

        # Marges : t=60 pour le titre, b=40 pour les labels d'axe X,
        # l=60 pour les labels d'axe Y (chiffres parfois larges),
        # r=20 simple respiration à droite.
        margin=dict(t=60, b=40, l=60, r=20),

        height=height,

        # Tooltip au survol : encadré blanc avec bordure subtile
        hoverlabel=dict(
            bgcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            font=dict(
                family="DM Sans, system-ui, sans-serif",
                size=13,
                color=COLORS["text"],
            ),
        ),

        # Légende horizontale en haut (mobile-friendly).
        # showlegend conditionnel : permet aux donuts de garder leur
        # propre légende intégrée si besoin.
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12, color=COLORS["text_muted"]),
            # Pas de bordure ni fond pour la légende — épure
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    # Configuration des axes : pas de grille verticale (gêne la lecture),
    # grille horizontale très subtile (aide à lire les valeurs).
    fig.update_xaxes(
        showgrid=False,
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"]),
        title_font=dict(color=COLORS["text"], size=13),
        # zeroline=False : pas de ligne épaisse à zéro (souvent superflue)
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS["border"],
        # gridwidth=1 (default) avec une couleur très claire est suffisant
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"]),
        title_font=dict(color=COLORS["text"], size=13),
        zeroline=False,
    )

    return fig
