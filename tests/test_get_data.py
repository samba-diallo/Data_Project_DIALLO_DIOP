"""
Tests unitaires pour src/utils/get_data.py.

Doc cours  : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest : https://docs.pytest.org/en/stable/how-to/assert.html
"""

import pytest
import pandas as pd
import inspect
from src.utils.get_data import download_data, save_raw_data, main


# ─────────────────────────────────────────────────────────────────
# Tests – Structure et Signatures
# ─────────────────────────────────────────────────────────────────

def test_download_data_callable():
    """
    Vérifie que download_data est une fonction callable.
    """
    assert callable(download_data), "download_data doit être une fonction"


def test_download_data_has_docstring():
    """
    Vérifie que download_data() a une docstring.
    """
    assert download_data.__doc__ is not None, "download_data() doit avoir une docstring"
    assert len(download_data.__doc__.strip()) > 0, "docstring ne doit pas être vide"


def test_download_data_return_type_annotation():
    """
    Vérifie que download_data() a une annotation de type de retour.
    """
    sig = inspect.signature(download_data)
    assert sig.return_annotation != inspect.Signature.empty, \
        "download_data() doit avoir une annotation de type de retour (-> pd.DataFrame)"


def test_download_data_return_annotation_is_dataframe():
    """
    Vérifie que l'annotation de retour mentionne DataFrame.
    """
    sig = inspect.signature(download_data)
    return_annotation = str(sig.return_annotation)
    assert "DataFrame" in return_annotation, \
        f"Annotation doit mentionner DataFrame, trouvé : {return_annotation}"


def test_save_raw_data_callable():
    """
    Vérifie que save_raw_data est une fonction callable.
    """
    assert callable(save_raw_data), "save_raw_data doit être une fonction"


def test_save_raw_data_has_docstring():
    """
    Vérifie que save_raw_data() a une docstring.
    """
    assert save_raw_data.__doc__ is not None, "save_raw_data() doit avoir une docstring"


def test_save_raw_data_has_required_parameters():
    """
    Vérifie que save_raw_data() a les paramètres attendus.
    """
    sig = inspect.signature(save_raw_data)
    params = list(sig.parameters.keys())
    
    assert len(params) >= 1, "save_raw_data() doit avoir au moins 1 paramètre"
    assert params[0] in ["df", "data", "dataframe"], \
        f"Premier paramètre doit être DataFrame (df/data/dataframe), trouvé : {params[0]}"


def test_save_raw_data_return_annotation():
    """
    Vérifie que save_raw_data() retourne None.
    """
    sig = inspect.signature(save_raw_data)
    return_annotation = str(sig.return_annotation)
    assert "None" in return_annotation or sig.return_annotation == type(None), \
        f"save_raw_data() doit retourner None, annotation : {return_annotation}"


def test_main_callable():
    """
    Vérifie que main est une fonction callable.
    """
    assert callable(main), "main doit être une fonction"


def test_main_has_docstring():
    """
    Vérifie que main() a une docstring.
    """
    assert main.__doc__ is not None, "main() doit avoir une docstring"


def test_main_no_required_parameters():
    """
    Vérifie que main() n'a pas de paramètres obligatoires.
    """
    sig = inspect.signature(main)
    required_params = [
        p for p in sig.parameters.values()
        if p.default == inspect.Parameter.empty and p.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD
        )
    ]
    
    assert len(required_params) == 0, \
        f"main() ne doit pas avoir de paramètres obligatoires, trouvés : {[p.name for p in required_params]}"
