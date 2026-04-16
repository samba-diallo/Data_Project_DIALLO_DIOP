"""
Tests unitaires pour les prérequis (requirements.txt).

Vérifie que tous les packages listés dans requirements.txt sont installés.
Pas de données réelles requises.

Doc pytest : https://docs.pytest.org/en/stable/
Doc importlib : https://docs.python.org/3/library/importlib.html
"""

import pytest
import importlib.util


# ─────────────────────────────────────────────────────────────────
# Tests – Packages / Requirements
# ─────────────────────────────────────────────────────────────────

def test_pandas_installed():
    """
    Vérifie que pandas est installé.
    Requis pour : manipulation de DataFrames.
    """
    spec = importlib.util.find_spec("pandas")
    assert spec is not None, "pandas doit être installé. Exécutez : pip install -r requirements.txt"


def test_dash_installed():
    """
    Vérifie que dash est installé.
    Requis pour : framework web du dashboard.
    """
    spec = importlib.util.find_spec("dash")
    assert spec is not None, "dash doit être installé. Exécutez : pip install -r requirements.txt"


def test_plotly_installed():
    """
    Vérifie que plotly est installé.
    Requis pour : création des graphiques interactifs.
    """
    spec = importlib.util.find_spec("plotly")
    assert spec is not None, "plotly doit être installé. Exécutez : pip install -r requirements.txt"


def test_pytest_installed():
    """
    Vérifie que pytest est installé.
    Requis pour : exécution des tests unitaires.
    """
    spec = importlib.util.find_spec("pytest")
    assert spec is not None, "pytest doit être installé. Exécutez : pip install -r requirements.txt"


def test_pandas_version():
    """
    Vérifie que pandas est une version récente (>= 1.0).
    """
    try:
        import pandas
        version_parts = pandas.__version__.split('.')
        major_version = int(version_parts[0])
        assert major_version >= 1, f"pandas >= 1.0 requis, trouvé {pandas.__version__}"
    except Exception as e:
        pytest.fail(f"Erreur en vérifiant la version de pandas : {e}")


def test_dash_version():
    """
    Vérifie que dash est une version récente (>= 2.0).
    """
    try:
        import dash
        version_parts = dash.__version__.split('.')
        major_version = int(version_parts[0])
        assert major_version >= 2, f"dash >= 2.0 requis, trouvé {dash.__version__}"
    except Exception as e:
        pytest.fail(f"Erreur en vérifiant la version de dash : {e}")


def test_plotly_version():
    """
    Vérifie que plotly est une version récente (>= 4.0).
    """
    try:
        import plotly
        version_parts = plotly.__version__.split('.')
        major_version = int(version_parts[0])
        assert major_version >= 4, f"plotly >= 4.0 requis, trouvé {plotly.__version__}"
    except Exception as e:
        pytest.fail(f"Erreur en vérifiant la version de plotly : {e}")
