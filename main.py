"""
Point d'entrée du dashboard GES Insight.
Lance le serveur Dash après avoir câblé le routing multi-pages,
les composants partagés (navbar, footer) et les callbacks de chaque page.

Usage :
    $ python main.py
"""

# Permet la syntaxe d'annotations PEP 604 (X | None) et PEP 585
# (list[str], dict[str, ...]) sur Python 3.9 — les annotations sont
# évaluées comme des chaînes et n'imposent plus la version 3.10+.
from __future__ import annotations

# dash : framework principal du dashboard
import dash
from dash import html, dcc, Input, Output

# dash-bootstrap-components : fournit la feuille de style Bootstrap pour
# les classes utilitaires (d-flex, row, col-md-X, gap-X) utilisées dans
# nos composants.
import dash_bootstrap_components as dbc

# Configuration centralisée (titre, host, port, debug)
import config

# Composants partagés affichés sur toutes les pages
from src.components.navbar import create_navbar
from src.components.footer import create_footer

# Pages du dashboard - chacune expose layout() et register_callbacks()
from src.pages import home, analysis, about


# ─────────────────────────────────────────────────────────────────
# CONFIGURATION DU ROUTING
# ─────────────────────────────────────────────────────────────────

# Mapping URL -> module de page. Ajouter une nouvelle page consiste à :
#   1) créer src/pages/ma_page.py exposant layout() et register_callbacks()
#   2) ajouter une ligne dans ce dict
#   3) ajouter l'entrée correspondante dans NAV_LINKS de navbar.py
ROUTES: dict[str, object] = {
    "/":             home,
    "/explorer":     analysis,
    "/methodologie": about,
}


# ─────────────────────────────────────────────────────────────────
# CONSTRUCTION DE L'APPLICATION
# ─────────────────────────────────────────────────────────────────

def create_app() -> dash.Dash:
    """
    Crée et configure l'instance Dash de l'application.

    Returns:
        dash.Dash: Instance Dash prête à recevoir layout et callbacks.
    """
    # external_stylesheets : on charge la CSS Bootstrap pour disposer des
    # classes utilitaires (grille, flex, espacement). Les fichiers de
    # assets/ sont chargés automatiquement en complément (style.css).
    # suppress_callback_exceptions : indispensable en multi-pages, car les
    # composants ciblés par les callbacks (ex: histogram, geomap) ne sont
    # pas tous présents dans le DOM au démarrage - ils n'apparaissent qu'à
    # la navigation vers la page concernée.
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title=config.APP_TITLE,
        suppress_callback_exceptions=True,
        # update_title=None désactive le "Updating..." dans l'onglet du
        # navigateur pendant les callbacks (rendu plus pro).
        update_title=None,
    )
    return app


def define_layout(app: dash.Dash) -> None:
    """
    Définit le layout principal de l'application.
    Structure : navbar fixe en haut, contenu de page au centre, footer en bas.
    Le contenu de page est injecté dynamiquement par le callback de routing.

    Args:
        app (dash.Dash): Instance de l'application Dash.

    Returns:
        None
    """
    # Le layout global est commun à toutes les pages. Seul le contenu du
    # html.Main(id="page-content") change selon l'URL.
    app.layout = html.Div(
        children=[
            # dcc.Location : composant invisible qui écoute l'URL du navigateur.
            # Sa propriété "pathname" sera l'input du callback de routing.
            dcc.Location(id="url", refresh=False),

            # Navbar : composant partagé, identique sur toutes les pages
            create_navbar(),

            # Container où sera injecté le layout de la page courante.
            # html.Main : balise sémantique HTML5 pour le contenu principal
            # (meilleure accessibilité que html.Div).
            html.Main(id="page-content"),

            # Footer : composant partagé, identique sur toutes les pages
            create_footer(),
        ],
    )


def register_callbacks(app: dash.Dash) -> None:
    """
    Enregistre tous les callbacks Dash de l'application.
    Inclut le callback de routing (URL -> contenu de page) et délègue
    aux modules de pages pour leurs callbacks spécifiques.

    Args:
        app (dash.Dash): Instance de l'application Dash.

    Returns:
        None
    """

    # ── Callback de routing ─────────────────────────────────────
    # Déclenché à chaque changement d'URL. Sélectionne le bon module
    # de page dans ROUTES et appelle son layout().
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname: str | None):
        """Renvoie le layout correspondant à l'URL demandée."""
        # Si l'URL ne correspond à aucune route connue, on retombe sur la
        # page d'accueil (comportement classique des SPA pour éviter
        # une page d'erreur disgracieuse).
        page_module = ROUTES.get(pathname or "/", home)
        return page_module.layout()

    # ── Callbacks spécifiques aux pages ────────────────────────
    # Chaque page enregistre ses propres callbacks (filtres, dropdowns...)
    # via sa fonction register_callbacks(app). Cette délégation évite que
    # main.py connaisse les détails de chaque page.
    for page_module in (home, analysis, about):
        page_module.register_callbacks(app)


# Construction en 3 étapes claires : création -> layout -> callbacks
app = create_app()
define_layout(app)
register_callbacks(app)

# Expose le serveur Flask pour les serveurs de production WSGI (comme gunicorn)
server = app.server


def main() -> None:
    """
    Démarre le serveur de développement local.

    Returns:
        None
    """
    # app.run() (et non plus app.run_server() qui est déprécié) : nouvelle
    # méthode préconisée par Dash 2.x. Évite le DeprecationWarning console.
    # debug, host, port viennent de config.py (pilotables par variables
    # d'environnement DEBUG, HOST, PORT pour le déploiement).
    app.run(
        debug=config.DEBUG_MODE,
        host=config.HOST,
        port=config.PORT,
    )


# Garde-fou : empêche l'exécution du serveur si main.py est importé par
# un autre module (ex: tests).
if __name__ == "__main__":
    main()

