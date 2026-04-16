"""
Page d'accueil du dashboard.
Présente le contexte du sujet d'intérêt public choisi et les KPIs principaux.

Doc Dash layout : https://dash.plotly.com/layout
"""

from dash import html, dcc


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout Dash de la page d'accueil.
    Contient une présentation du sujet, des KPIs clés et une introduction
    aux données utilisées.

    Returns:
        html.Div: Layout complet de la page d'accueil.
    """
    # TODO: assembler header + contenu + footer
    pass


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks spécifiques à la page d'accueil.
    (Peut être vide si la page n'a pas d'interactivité)
    
    Args:
        app: Instance de l'application Dash (dash.Dash).
    
    Returns:
        None
    """
    # TODO: ajouter les callbacks si nécessaire
    pass
