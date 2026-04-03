"""
Tests unitaires pour src/utils/common_functions.py.

Doc cours   : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest  : https://docs.pytest.org/en/stable/how-to/parametrize.html
"""

import pytest
import pandas as pd
from src.utils.common_functions import filter_data, aggregate_data


# ─────────────────────────────────────────────────────────────────
# Tests – Backend / Commun
# ─────────────────────────────────────────────────────────────────

def test_filter_data():
    """
    Vérifie que filter_data() retourne le bon sous-ensemble de données
    selon les critères passés en kwargs.
    Critique : cette fonction est appelée en temps réel par les callbacks Dash.
    """
    # TODO: df de test → filter_data(df, colonne="valeur") → assert résultat correct
    pass


def test_aggregate_data():
    """
    Vérifie que aggregate_data() produit les bons agrégats (sommes/moyennes)
    pour chaque groupe, garantissant la fiabilité des graphiques.
    """
    # TODO: df de test → aggregate_data(df, "region", "valeur") → assert sommes correctes
    pass
