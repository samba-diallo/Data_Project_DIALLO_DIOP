"""
Page 'Methodologie' du dashboard.
Documente le referentiel BEGES, les sources de donnees, le pipeline
de traitement et les credits du projet.

Doc Dash layout : https://dash.plotly.com/layout
"""

from dash import html

# Import du header editorial commun a toutes les pages
from src.components.header import create_header


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout de la page 'Methodologie'.
    Contiendra (Phase 6) un schema Mermaid du pipeline, un glossaire
    BEGES (Scope 1/2/3, postes P1.x a P6.x) et les credits.

    Returns:
        html.Div: Layout complet de la page methodologie.
    """
    return html.Div(
        className="page-container",
        children=[
            # Header editorial : signale qu'on entre dans la partie
            # documentaire/transparence du produit.
            create_header(
                kicker="Méthodologie",
                title="Comment lire ce tableau de bord",
                subtitle=(
                    "Glossaire du référentiel BEGES, pipeline de traitement "
                    "des données ADEME et déclaration d'originalité du code."
                ),
            ),
            # Placeholder : sera remplace par schema Mermaid + glossaire +
            # copyright en Phase 6.
            html.Div(
                "Contenu à venir : schéma d'architecture, glossaire BEGES, "
                "section copyright.",
                style={"padding": "2rem", "color": "var(--color-text-muted)"},
            ),
        ],
    )


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks specifiques a la page methodologie.
    Vide : page purement documentaire, pas d'interactivite prevue.

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """
    # Aucune interaction prevue sur cette page.
    pass
