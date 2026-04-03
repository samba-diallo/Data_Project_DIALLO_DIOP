"""
Point d'entrée du projet.
Lance le serveur Dash après avoir enregistré toutes les pages.

Usage :
    $ python main.py
"""

import dash
from src.pages import home, analysis, about
from src.components.navbar import create_navbar
import config


def main() -> None:
    """
    Initialise l'application Dash, enregistre les callbacks
    de chaque page et démarre le serveur web.

    Returns:
        None
    """
    # TODO: créer l'instance Dash
    # TODO: définir le layout principal (navbar + page-content)
    # TODO: appeler register_callbacks(app) pour chaque page
    # TODO: app.run_server(debug=config.DEBUG_MODE, host=config.HOST, port=config.PORT)
    pass


if __name__ == "__main__":
    main()
