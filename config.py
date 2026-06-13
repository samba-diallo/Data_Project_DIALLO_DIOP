"""
Fichier de configuration globale du projet.
Centralise l'ensemble des chemins d'accès aux fichiers, des adresses URL,
et des paramètres réseau pour éviter les valeurs écrites en dur dans le code.
"""

import os


def _env_bool(name: str, default: bool) -> bool:
    """
    Lit et interprète une variable d'environnement sous forme de booléen.
    Accepte les valeurs textuelles courantes (1, true, yes, on).

    Args:
        name (str): Nom de la variable d'environnement à lire.
        default (bool): Valeur par défaut à renvoyer si la variable n'est pas définie.

    Returns:
        bool: Valeur booléenne résolue.
    """
    # Recherche de la variable d'environnement dans le système
    raw = os.getenv(name)
    # Si la variable n'existe pas, nous retournons la valeur de secours
    if raw is None:
        return default
    # Validation par rapport à un ensemble de valeurs considérées comme vraies
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# ── Chemins d'accès aux fichiers du projet ──────────────────────
# Répertoire de base contenant ce fichier de configuration
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))

# Fichier contenant les données initiales brutes de l'ADEME
DATA_RAW    = os.path.join(BASE_DIR, "data", "raw", "bilan-ges.xlsx")

# Fichier CSV contenant les données nettoyées et prêtes pour l'analyse
DATA_CLEAN  = os.path.join(BASE_DIR, "data", "cleaned", "cleaneddata.csv")

# Nom de la feuille de calcul Excel à extraire du fichier d'origine de l'ADEME
DATA_SHEET  = "données"

# ── Source distante des données ──────────────────────────────────
# URL officielle de l'API de l'ADEME pour télécharger le jeu de données des bilans GES
DATA_URL = "https://data.ademe.fr/api/explore/v2.1/catalog/datasets/bilan-ges/exports/xlsx?limit=-1"

# ── Paramètres de l'application Dash ──────────────────────────────
# Titre principal affiché dans l'onglet du navigateur internet
APP_TITLE   = "GES Insight — Bilans carbone des organisations françaises"

# Activation du mode débogage (vrai ou faux) lu depuis l'environnement
# Le mode débogage permet de voir les erreurs à l'écran mais doit être désactivé en production
DEBUG_MODE  = _env_bool("DEBUG", default=False)

# Adresse IP locale d'écoute pour le serveur Web (par défaut 127.0.0.1)
HOST        = os.getenv("HOST", "127.0.0.1")

# Port réseau d'écoute (par défaut 8050)
PORT        = int(os.getenv("PORT", "8050"))
