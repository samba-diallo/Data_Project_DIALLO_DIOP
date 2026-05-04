"""
Configuration globale du projet.
Centralise tous les chemins, URLs et paramètres pour éviter
les valeurs en dur dispersées dans le code.
"""

import os


def _env_bool(name: str, default: bool) -> bool:
    """Lit une variable d'environnement booléenne (accepte 1/true/yes/on)."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# ── Chemins ──────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_RAW    = os.path.join(BASE_DIR, "data", "raw", "bilan-ges.xlsx")
DATA_CLEAN  = os.path.join(BASE_DIR, "data", "cleaned", "cleaneddata.csv")

# Feuille Excel contenant les observations (le fichier ADEME en contient 3 :
# "données", "jeu de données" et "requête" — seule "données" nous intéresse).
DATA_SHEET  = "données"

# ── Source des données ───────────────────────────────────────────
# Dataset ADEME: Bilans GES (Gaz à Effet de Serre)
# Plateforme ADEME - https://data.ademe.fr/datasets/bilan-ges
# Format local : Excel (xlsx) — feuille "données"
DATA_URL = "https://data.ademe.fr/api/explore/v2.1/catalog/datasets/bilan-ges/exports/xlsx?limit=-1"

# ── Paramètres Dash ──────────────────────────────────────────────
APP_TITLE   = "GES Insight — Bilans carbone des organisations françaises"

# DEBUG_MODE piloté par la variable d'environnement DEBUG (défaut : False).
# Activer uniquement en local : la console Dash expose des détails sensibles.
DEBUG_MODE  = _env_bool("DEBUG", default=False)

# HOST à 127.0.0.1 en local pour ne pas exposer le serveur sur le réseau.
# Utiliser HOST=0.0.0.0 (via variable d'environnement) uniquement en conteneur.
HOST        = os.getenv("HOST", "127.0.0.1")
PORT        = int(os.getenv("PORT", "8050"))
