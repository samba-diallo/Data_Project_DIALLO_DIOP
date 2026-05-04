"""
Barre de navigation multi-pages du dashboard.
Utilise dcc.Link pour la navigation sans rechargement de page.

Doc Dash multi-pages : https://dash.plotly.com/urls
"""

# dash.html : composants HTML wrappes en Python (html.Nav, html.Div...)
# dash.dcc : composants Dash core, dont dcc.Link pour la navigation interne
from dash import html, dcc

# DashIconify : injection d'icones SVG depuis Iconify (Heroicons, Lucide,
# Tabler...). Conforme a la regle "no-emoji-icons" de la checklist UX.
from dash_iconify import DashIconify


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

# Liste des liens de navigation, definie comme constante au niveau module
# pour faciliter l'ajout/retrait de pages a un seul endroit.
# Tuple : (label affiche, chemin url, icone Iconify).
# Iconify : on utilise la collection "tabler" pour un look ligne fin uniforme.
NAV_LINKS: list[tuple[str, str, str]] = [
    ("Vue d'ensemble", "/",             "tabler:layout-dashboard"),
    ("Explorer",       "/explorer",     "tabler:chart-histogram"),
    ("Méthodologie",   "/methodologie", "tabler:notebook"),
]


def create_navbar() -> html.Nav:
    """
    Construit et retourne la barre de navigation du dashboard.
    Contient une marque (logo textuel) a gauche et les liens vers
    les pages principales a droite.

    Returns:
        html.Nav: Composant Dash de navigation pret a etre integre.
    """
    # On construit la liste des liens via une comprehension de liste plutot
    # qu'a la main : si on ajoute une page dans NAV_LINKS, le rendu suit.
    nav_items = [_build_nav_link(label, href, icon)
                 for label, href, icon in NAV_LINKS]

    # html.Nav : balise semantique HTML5 pour la navigation. Important pour
    # l'accessibilite (lecteurs d'ecran annoncent "navigation").
    # className : classes CSS appliquees, definies dans assets/style.css.
    return html.Nav(
        className="navbar-ges",
        # role="navigation" est implicite avec html.Nav, mais on le rend
        # explicite pour les lecteurs d'ecran plus anciens.
        **{"role": "navigation", "aria-label": "Navigation principale"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    # Brand a gauche : nom du produit avec icone, retour accueil au clic
                    _build_brand(),
                    # Liens de navigation a droite, regroupes dans un container
                    # avec gap pour respirer entre chaque lien
                    html.Div(
                        className="d-flex align-items-center gap-2",
                        children=nav_items,
                    ),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# Helpers prives
# ─────────────────────────────────────────────────────────────────

def _build_brand() -> dcc.Link:
    """Construit le bloc 'marque' (logo + nom) qui ramene a l'accueil."""
    # dcc.Link : navigation cote client, sans rechargement de page complet.
    # href="/" pointe vers la page d'accueil.
    return dcc.Link(
        href="/",
        className="brand d-flex align-items-center gap-2",
        children=[
            # Icone : feuille stylisee qui evoque l'environnement sans cliche
            # (on evite l'emoji feuille verte). Tabler icon "leaf-2".
            DashIconify(icon="tabler:leaf-2", width=24, color="#1F3A2C"),
            # Nom du produit : 2 mots avec hierarchie typographique implicite
            html.Span("GES Insight"),
        ],
    )


def _build_nav_link(label: str, href: str, icon: str) -> dcc.Link:
    """Construit un lien de navigation individuel avec icone + label."""
    return dcc.Link(
        href=href,
        # className "nav-link" : style defini dans style.css
        className="nav-link d-flex align-items-center gap-2",
        children=[
            # Icone discrete a gauche du label : 16px = bonne taille pour
            # un element de navigation (pas trop voyante)
            DashIconify(icon=icon, width=16),
            # Label texte
            html.Span(label),
        ],
    )
