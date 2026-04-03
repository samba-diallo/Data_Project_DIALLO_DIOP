"""
Configuration globale du projet.
Centralise tous les chemins, URLs et paramètres pour éviter
les valeurs en dur dispersées dans le code.
"""

import os

# ── Chemins ──────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_RAW    = os.path.join(BASE_DIR, "data", "raw", "rawdata.csv")
DATA_CLEAN  = os.path.join(BASE_DIR, "data", "cleaned", "cleaneddata.csv")

# ── Source des données ───────────────────────────────────────────
# Remplacer par l'URL réelle de votre jeu de données Open Data
DATA_URL = "https://example.com/dataset.csv"

# ── Paramètres Dash ──────────────────────────────────────────────
APP_TITLE   = "Projet Data – Dashboard"
DEBUG_MODE  = True
HOST        = "0.0.0.0"
PORT        = 8050
