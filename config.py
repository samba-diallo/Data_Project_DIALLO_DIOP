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
# Dataset ADEME: Bilans GES (Gaz à Effet de Serre)
# Plateforme ADEME - https://data.ademe.fr/datasets/bilan-ges
# Variables: annee, region, secteur_naf, total_scope_1, total_scope_2, total_scope_3
DATA_URL = "https://data.ademe.fr/api/explore/v2.1/catalog/datasets/bilan-ges/exports/csv?limit=-1"

# ── Paramètres Dash ──────────────────────────────────────────────
APP_TITLE   = "Projet Data – Dashboard"
DEBUG_MODE  = True
HOST        = "0.0.0.0"
PORT        = 8050
