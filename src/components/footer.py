"""
Composant pied de page (Footer) pour l'application.
Affiche les sources de données, les contributeurs, et les mentions légales obligatoires.
"""

from dash import html
from dash_iconify import DashIconify

# URL officielle du jeu de données hébergé par l'ADEME
ADEME_URL = "https://data.ademe.fr/datasets/bilan-ges"


def create_footer() -> html.Footer:
    """
    Construit et retourne le pied de page général du dashboard.
    Il est structuré en trois colonnes descriptives et une ligne finale de copyright.

    Returns:
        html.Footer: Le composant de pied de page HTML5 configuré.
    """
    # Utilisation de la balise sémantique <footer> pour l'accessibilité
    return html.Footer(
        className="footer-ges",
        children=[
            # Conteneur alignant le footer sur la largeur maximale de la page
            html.Div(
                className="page-container",
                children=[
                    # Ligne principale divisée en plusieurs colonnes à l'aide de Bootstrap (row)
                    html.Div(
                        className="row g-4",
                        children=[
                            _build_about_column(), # Colonne d'explication du projet
                            _build_data_column(),  # Colonne de référence aux données
                            _build_team_column(),  # Colonne de présentation de l'équipe
                        ],
                    ),
                    # Ligne horizontale séparatrice de bas de page (méta-informations)
                    _build_meta_line(),
                ],
            ),
        ],
    )


def _build_about_column() -> html.Div:
    """
    Construit la première colonne contenant la description abrégée du projet.

    Returns:
        html.Div: Bloc HTML de la colonne.
    """
    return html.Div(
        className="col-md-4",
        children=[
            # Titre de la colonne
            html.Div("À propos", className="footer-section-title"),
            # Description succincte
            html.P(
                "Plateforme de visualisation des Bilans GES réglementaires "
                "publiés par les organisations françaises sur la plateforme "
                "ADEME."
            ),
        ],
    )


def _build_data_column() -> html.Div:
    """
    Construit la deuxième colonne contenant le lien vers les données sources de l'ADEME.

    Returns:
        html.Div: Bloc HTML de la colonne.
    """
    return html.Div(
        className="col-md-4",
        children=[
            # Titre de la colonne
            html.Div("Source des données", className="footer-section-title"),
            html.P([
                "Données publiques ADEME — ",
                # Lien hypertexte pointant vers les données brutes
                # target="_blank" permet d'ouvrir le lien dans un nouvel onglet
                # rel="noopener noreferrer" est une sécurité pour éviter les vulnérabilités de redirection
                html.A(
                    "Bilans GES",
                    href=ADEME_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                ),
                # Petit icône indiquant un lien externe vers le site de l'ADEME
                DashIconify(
                    icon="tabler:external-link",
                    width=14,
                    style={"marginLeft": "4px", "verticalAlign": "middle"},
                ),
            ]),
            # Explication sur l'utilisation hors ligne des données stockées en local
            html.P(
                "Mises à jour quotidiennes par l'ADEME ; un instantané est "
                "embarqué dans ce projet pour permettre un fonctionnement "
                "hors ligne.",
                style={"fontSize": "var(--fs-xs)", "color": "var(--color-text-subtle)"},
            ),
        ],
    )


def _build_team_column() -> html.Div:
    """
    Construit la troisième colonne présentant les auteurs du projet.

    Returns:
        html.Div: Bloc HTML de la colonne.
    """
    return html.Div(
        className="col-md-4",
        children=[
            # Titre de la colonne
            html.Div("Équipe", className="footer-section-title"),
            html.P([
                "Projet réalisé par ",
                html.Strong("Samba DIALLO"),
                " et ",
                html.Strong("Mouhamed DIOP"),
                ", étudiants ingénieurs à l'ESIEE Paris.",
            ]),
        ],
    )


def _build_meta_line() -> html.Div:
    """
    Construit la ligne de copyright tout en bas du pied de page.

    Returns:
        html.Div: Ligne finale contenant les crédits textuels.
    """
    return html.Div(
        className="footer-meta d-flex justify-content-between flex-wrap",
        children=[
            # Texte de copyright et école d'ingénieurs
            html.Span("© 2026 GES Insight — ESIEE Paris"),
            # Technologies clés utilisées
            html.Span("Dash · Plotly · Pandas"),
        ],
    )
