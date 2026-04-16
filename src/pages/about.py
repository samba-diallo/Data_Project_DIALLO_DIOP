"""
Page 'À propos' du dashboard.
Présente les membres du projet, les sources de données et la méthodologie.

Doc Dash layout : https://dash.plotly.com/layout
"""

from dash import html


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout de la page 'À propos'.
    Contient les informations sur les membres (SAMBA, MOUHAMED),
    les liens vers les sources de données et la description de la méthodologie.

    Returns:
        html.Div: Layout complet de la page 'À propos'.
    """
    # TODO: assembler les sections membres, sources, méthodologie
    pass


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks spécifiques à la page 'À propos'.
    (Peut être vide si la page n'a pas d'interactivité)
    
    Args:
        app: Instance de l'application Dash (dash.Dash).
    
    Returns:
        None
    """
    # TODO: ajouter les callbacks si nécessaire (probablement aucun)
    pass
