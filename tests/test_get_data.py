"""
Tests unitaires pour src/utils/get_data.py.

Doc cours  : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest : https://docs.pytest.org/en/stable/how-to/assert.html
"""

import pytest
import pandas as pd
from src.utils.get_data import download_data, save_raw_data


# ─────────────────────────────────────────────────────────────────
# Tests – Données
# ─────────────────────────────────────────────────────────────────

def test_download_data():
    """
    Vérifie que download_data() retourne un DataFrame non vide
    avec les colonnes attendues.
    Le test échouera si la source est inaccessible ou le format incorrect.
    """
    # TODO: df = download_data(); assert isinstance(df, pd.DataFrame); assert not df.empty
    pass


def test_save_raw_data(tmp_path):
    """
    Vérifie que save_raw_data() crée bien le fichier CSV
    dans le répertoire data/raw/ sans corruption des données.

    Args:
        tmp_path: Fixture pytest fournissant un répertoire temporaire.
    """
    # TODO: créer un df de test, appeler save_raw_data(df), vérifier existence du fichier
    pass
