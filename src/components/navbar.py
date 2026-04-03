"""
Barre de navigation multi-pages du dashboard.
Utilise dcc.Link pour la navigation sans rechargement de page.

Doc Dash multi-pages : https://dash.plotly.com/urls
"""

from dash import html, dcc


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

def create_navbar() -> html.Nav:
    """
    Construit et retourne la barre de navigation du dashboard.
    Contient des liens vers les pages : Accueil, Analyse, À propos.

    Returns:
        html.Nav: Composant Dash de navigation prêt à être intégré.
    """
    # TODO: retourner html.Nav([dcc.Link("Accueil", href="/"), ...])
    pass
