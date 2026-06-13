"""
Composant de barre de navigation (Navbar) pour le tableau de bord.
Permet de basculer d'une page à l'autre de manière fluide, sans rechargement complet de la page (technologie Single Page Application).
"""

from dash import html, dcc
from dash_iconify import DashIconify

# Configuration des liens de navigation sous forme de liste.
# Chaque élément contient : (Libellé affiché, chemin URL, nom de l'icône).
# Cela permet d'ajouter une nouvelle page très facilement.
NAV_LINKS: list[tuple[str, str, str]] = [
    ("Vue d'ensemble", "/",             "tabler:layout-dashboard"),
    ("Explorer",       "/explorer",     "tabler:chart-histogram"),
    ("Méthodologie",   "/methodologie", "tabler:notebook"),
]


def create_navbar() -> html.Nav:
    """
    Construit et retourne la barre de navigation supérieure.
    Comprend le logo/titre à gauche et les liens de navigation à droite.

    Returns:
        html.Nav: Le composant de navigation HTML5 prêt pour le gabarit global.
    """
    # Génération automatique des liens HTML à partir de la configuration NAV_LINKS
    nav_items = [_build_nav_link(label, href, icon)
                 for label, href, icon in NAV_LINKS]

    # Utilisation de la balise sémantique <nav> pour les critères d'accessibilité numérique
    return html.Nav(
        className="navbar-ges",
        # Renseigner le rôle d'accessibilité pour les lecteurs d'écran d'utilisateurs non-voyants
        **{"role": "navigation", "aria-label": "Navigation principale"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    # Logo et titre à gauche (qui renvoie vers la page d'accueil au clic)
                    _build_brand(),
                    # Conteneur des boutons de liens de pages alignés à droite
                    html.Div(
                        className="d-flex align-items-center gap-2",
                        children=nav_items,
                    ),
                ],
            ),
        ],
    )


def _build_brand() -> dcc.Link:
    """
    Génère le bouton logo/titre de l'application (Brand) placé à gauche.

    Returns:
        dcc.Link: Lien interactif Dash sans rechargement.
    """
    return dcc.Link(
        href="/",
        className="brand d-flex align-items-center gap-2",
        children=[
            # Icône SVG représentant une feuille pour évoquer l'écologie (aucune image png ou emoji)
            DashIconify(icon="tabler:leaf-2", width=24, color="#1F3A2C"),
            # Nom de l'application
            html.Span("GES Insight"),
        ],
    )


def _build_nav_link(label: str, href: str, icon: str) -> dcc.Link:
    """
    Génère un lien de navigation individuel pour le menu.

    Args:
        label (str): Texte à afficher.
        href (str): Chemin d'URL de destination.
        icon (str): Identifiant de l'icône à afficher à côté du texte.

    Returns:
        dcc.Link: Lien interactif Dash.
    """
    return dcc.Link(
        href=href,
        className="nav-link d-flex align-items-center gap-2",
        children=[
            # Icône associée au lien
            DashIconify(icon=icon, width=16),
            # Libellé du lien
            html.Span(label),
        ],
    )
