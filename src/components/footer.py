"""
Composant pied de page du dashboard.
Mentionne les sources de données et les licences Open Data.

Doc Dash HTML : https://dash.plotly.com/dash-html-components
"""

from dash import html


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

def create_footer() -> html.Div:
    """
    Construit et retourne le composant Dash HTML du pied de page.
    Indique les sources de données et les crédits.

    Returns:
        html.Div: Composant Dash prêt à être intégré dans un layout.
    """
    # TODO: retourner html.Footer([html.P("Source : ..."), html.P("© 2025")])
    pass
