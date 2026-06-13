"""
Point d'entrée principal de l'application GES Insight.
Ce fichier configure et démarre le serveur web Dash, charge la structure
globale de l'interface (en-tête, navigation, contenu, pied de page)
et gère le routage entre les différentes pages de l'application.

Lancement local :
    $ python main.py
"""

from __future__ import annotations

from typing import Any

# Importation du framework de dashboarding Dash
import dash
from dash import html, dcc, Input, Output

# Importation de la bibliothèque de composants Bootstrap pour le style et la mise en page
import dash_bootstrap_components as dbc

# Importation du fichier de configuration globale du projet
import config

# Importation des composants d'interface partagés
from src.components.navbar import create_navbar
from src.components.footer import create_footer

# Importation des contrôleurs de pages (modules python de pages)
from src.pages import home, analysis, about

# ── Configuration du Routage de l'Application ──────────────────
# Dictionnaire associant les chemins d'URL aux modules correspondants.
# Pour ajouter une page :
#   1) Créer un fichier de page dans src/pages/
#   2) Définir les fonctions layout() et register_callbacks()
#   3) Ajouter la route correspondante ci-dessous
ROUTES: dict[str, Any] = {
    "/":             home,
    "/explorer":     analysis,
    "/methodologie": about,
}


def create_app() -> dash.Dash:
    """
    Instancie et configure l'application Dash.

    Returns:
        dash.Dash: Instance de l'application configurée.
    """
    # Création de l'application en incluant le thème Bootstrap par défaut
    # suppress_callback_exceptions=True est obligatoire pour le routage multi-pages
    # car les composants ciblés par les callbacks n'existent pas tous en même temps dans la page.
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title=config.APP_TITLE,
        suppress_callback_exceptions=True,
        # update_title=None désactive l'affichage automatique de "Updating..." dans l'onglet
        update_title=None,  # pyrefly: ignore
    )
    return app


def define_layout(app: dash.Dash) -> None:
    """
    Définit l'agencement ou gabarit global de l'application.
    Ce gabarit est identique pour chaque page visitée.

    Args:
        app (dash.Dash): Instance de l'application Dash.
    """
    # Le composant Location écoute les changements d'adresse URL dans le navigateur
    # Le contenu de la balise Main (id="page-content") sera mis à jour par le routeur
    app.layout = html.Div(
        children=[
            # Suivi de la navigation de l'utilisateur
            dcc.Location(id="url", refresh=False),

            # Barre de navigation supérieure commune
            create_navbar(),

            # Conteneur principal dans lequel s'affichera le contenu de chaque page
            html.Main(id="page-content"),

            # Pied de page informatif commun
            create_footer(),
        ],
    )


def register_callbacks(app: dash.Dash) -> None:
    """
    Enregistre les mécanismes d'interactivité (les callbacks) de l'application.
    Gère notamment le chargement dynamique des pages lors d'un clic sur un lien.

    Args:
        app (dash.Dash): Instance de l'application Dash.
    """

    # ── Callback de Routage Dynamique ─────────────────────────────
    # Déclenché dès que l'adresse URL du navigateur change
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname: str | None) -> Any:
        """
        Détermine et renvoie la mise en page à afficher selon l'URL.

        Args:
            pathname (str | None): Chemin d'accès demandé.

        Returns:
            Any: Contenu graphique de la page à injecter.
        """
        # Si le chemin demandé n'existe pas, on redirige par défaut vers la page d'accueil (home)
        page_module = ROUTES.get(pathname or "/", home)
        return page_module.layout()

    # ── Enregistrement des callbacks de chaque page ──────────────
    # Permet de lier l'interactivité propre à chaque page (recherches, filtres, graphiques)
    for page_module in (home, analysis, about):
        page_module.register_callbacks(app)


# ── Initialisation Automatique des Données ──────────────────────
# Si la base SQLite n'existe pas encore (ex: après un clone git),
# on l'initialise automatiquement à partir des fichiers bruts locaux ou de l'API.
import os
if not os.path.exists(config.DATABASE):
    print("Base de données SQLite manquante. Initialisation automatique...")
    try:
        from src.utils.get_data import main as init_get_data
        from src.utils.clean_data import main as init_clean_data
        init_get_data()
        init_clean_data()
        print("Initialisation de la base SQLite terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation automatique : {e}")


# Étape 1 : Création de l'application Dash
app = create_app()

# Étape 2 : Définition du gabarit graphique commun
define_layout(app)

# Étape 3 : Liaison des callbacks d'interactivité
register_callbacks(app)

# Exposition de l'instance Flask sous-jacente pour les déploiements de production (Gunicorn)
server = app.server


def main() -> None:
    """
    Fonction principale lançant le serveur web de développement.
    """
    # Lancement du serveur Web local avec les paramètres définis dans config.py
    app.run(
        debug=config.DEBUG_MODE,
        host=config.HOST,
        port=config.PORT,
    )


# Sécurité pour éviter de lancer le serveur si le script est importé ailleurs (ex: tests unitaires)
if __name__ == "__main__":
    main()
