"""
Composant pied de page du dashboard.
Affiche les sources de donnees, l'equipe, et la mention de copyright
exigee par le cahier des charges.

Doc Dash HTML : https://dash.plotly.com/dash-html-components
"""

from dash import html

# DashIconify : icones SVG, utilise ici pour le logo source de donnees
from dash_iconify import DashIconify


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

# URL officielle de la source de donnees (a citer dans le footer
# selon les exigences du prof, section "Data" du README).
ADEME_URL = "https://data.ademe.fr/datasets/bilan-ges"


def create_footer() -> html.Footer:
    """
    Construit et retourne le pied de page du dashboard.
    Contient trois colonnes (a propos, source de donnees, equipe)
    et une ligne meta avec copyright et mention BEGES.

    Returns:
        html.Footer: Composant Dash pret a etre integre dans un layout.
    """
    # html.Footer : balise semantique HTML5, equivalent de <footer>.
    return html.Footer(
        className="footer-ges",
        children=[
            # Container largeur max pour aligner avec le contenu de la page
            html.Div(
                className="page-container",
                children=[
                    # Bloc principal : 3 colonnes informatives
                    html.Div(
                        # className Bootstrap : grille 3 colonnes responsive,
                        # gap entre colonnes pour respirer
                        className="row g-4",
                        children=[
                            _build_about_column(),
                            _build_data_column(),
                            _build_team_column(),
                        ],
                    ),
                    # Ligne meta en bas : copyright et tech stack
                    _build_meta_line(),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────
# Helpers prives - construction des colonnes
# ─────────────────────────────────────────────────────────────────

def _build_about_column() -> html.Div:
    """Colonne 'A propos' : pitch produit court."""
    return html.Div(
        className="col-md-4",
        children=[
            html.Div("À propos", className="footer-section-title"),
            # Phrase de presentation courte du produit (mission)
            html.P(
                "Plateforme de visualisation des Bilans GES réglementaires "
                "publiés par les organisations françaises sur la plateforme "
                "ADEME."
            ),
        ],
    )


def _build_data_column() -> html.Div:
    """Colonne 'Source des donnees' : credit ADEME."""
    return html.Div(
        className="col-md-4",
        children=[
            html.Div("Source des données", className="footer-section-title"),
            html.P([
                "Données publiques ADEME — ",
                # Lien externe (target=_blank ouvre dans un nouvel onglet
                # pour ne pas perdre la consultation du dashboard).
                # rel="noopener" est une mesure de securite contre le
                # tab-napping (recommandation OWASP).
                html.A(
                    "Bilans GES",
                    href=ADEME_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                ),
                # Icone "lien externe" pour signaler que ca ouvre ailleurs
                DashIconify(
                    icon="tabler:external-link",
                    width=14,
                    style={"marginLeft": "4px", "verticalAlign": "middle"},
                ),
            ]),
            # Mention sur la frequence de mise a jour (transparence)
            html.P(
                "Mises à jour quotidiennes par l'ADEME ; un instantané est "
                "embarqué dans ce projet pour permettre un fonctionnement "
                "hors ligne.",
                style={"fontSize": "var(--fs-xs)", "color": "var(--color-text-subtle)"},
            ),
        ],
    )


def _build_team_column() -> html.Div:
    """Colonne 'Equipe' : auteurs du projet."""
    return html.Div(
        className="col-md-4",
        children=[
            html.Div("Équipe", className="footer-section-title"),
            html.P([
                # Liste des co-auteurs du projet ESIEE
                "Projet réalisé par ",
                html.Strong("Samba DIALLO"),
                " et ",
                html.Strong("Mouhamed DIOP"),
                ", étudiants ingénieurs à l'ESIEE Paris.",
            ]),
        ],
    )


def _build_meta_line() -> html.Div:
    """Ligne fine en bas du footer : copyright + stack technique."""
    return html.Div(
        className="footer-meta d-flex justify-content-between flex-wrap",
        children=[
            # Mention de copyright. 2026 = annee universitaire en cours
            # (date saisie en dur plutot que dynamique pour eviter une
            # dependance datetime au runtime).
            html.Span("© 2026 GES Insight — ESIEE Paris"),
            # Tech stack visible : transparence sur les outils utilises
            html.Span("Dash · Plotly · Pandas"),
        ],
    )
