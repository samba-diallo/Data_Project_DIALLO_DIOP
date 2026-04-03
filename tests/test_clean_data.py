"""
Tests unitaires pour src/utils/clean_data.py.

Doc cours  : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest : https://docs.pytest.org/en/stable/
"""

import pytest
import pandas as pd
from src.utils.clean_data import (
    remove_duplicates,
    handle_missing_values,
    normalize_columns,
)


# ─────────────────────────────────────────────────────────────────
# Tests – Données
# ─────────────────────────────────────────────────────────────────

def test_remove_duplicates():
    """
    Vérifie que remove_duplicates() supprime exactement les doublons
    sans altérer les lignes uniques du DataFrame.
    """
    # TODO: df avec doublons → remove_duplicates(df) → assert len == attendu
    pass


def test_handle_missing_values():
    """
    Vérifie que handle_missing_values() traite correctement les NaN
    selon la stratégie définie (aucun NaN restant ou marquage cohérent).
    """
    # TODO: df avec NaN → handle_missing_values(df) → assert df.isnull().sum() == 0
    pass


def test_normalize_columns():
    """
    Vérifie que normalize_columns() retourne le DataFrame avec
    les noms de colonnes en snake_case et les types de données corrects.
    """
    # TODO: vérifier les noms et types des colonnes après normalisation
    pass
