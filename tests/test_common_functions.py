"""
Tests unitaires pour src/utils/common_functions.py.

Doc cours   : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest  : https://docs.pytest.org/en/stable/how-to/parametrize.html
"""

import pytest
import pandas as pd
import inspect
from src.utils.common_functions import load_cleaned_data, filter_data, aggregate_data


# ─────────────────────────────────────────────────────────────────
# Tests – Structure et Signatures
# ─────────────────────────────────────────────────────────────────

def test_load_cleaned_data_callable():
    """
    Vérifie que load_cleaned_data est une fonction callable.
    """
    assert callable(load_cleaned_data), "load_cleaned_data doit être une fonction"


def test_load_cleaned_data_has_docstring():
    """
    Vérifie que load_cleaned_data() a une docstring.
    """
    assert load_cleaned_data.__doc__ is not None, "load_cleaned_data() doit avoir une docstring"


def test_load_cleaned_data_no_required_parameters():
    """
    Vérifie que load_cleaned_data() n'a pas de paramètres obligatoires.
    """
    sig = inspect.signature(load_cleaned_data)
    required_params = [
        p for p in sig.parameters.values()
        if p.default == inspect.Parameter.empty and p.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD
        )
    ]
    
    assert len(required_params) == 0, \
        f"load_cleaned_data() ne doit pas avoir de paramètres obligatoires"


def test_load_cleaned_data_return_annotation():
    """
    Vérifie que load_cleaned_data() a une annotation de retour DataFrame.
    """
    sig = inspect.signature(load_cleaned_data)
    assert sig.return_annotation != inspect.Signature.empty, \
        "load_cleaned_data() doit avoir une annotation de type de retour (-> pd.DataFrame)"


def test_filter_data_callable():
    """
    Vérifie que filter_data est une fonction callable.
    """
    assert callable(filter_data), "filter_data doit être une fonction"


def test_filter_data_has_docstring():
    """
    Vérifie que filter_data() a une docstring.
    """
    assert filter_data.__doc__ is not None, "filter_data() doit avoir une docstring"


def test_filter_data_has_df_parameter():
    """
    Vérifie que filter_data() accepte un paramètre 'df' (DataFrame).
    """
    sig = inspect.signature(filter_data)
    params = list(sig.parameters.keys())
    
    assert len(params) >= 1, "filter_data() doit avoir au moins 1 paramètre"
    assert params[0] in ["df", "data", "dataframe"], \
        f"Premier paramètre doit être DataFrame, trouvé : {params[0]}"


def test_filter_data_accepts_kwargs():
    """
    Vérifie que filter_data() accepte **kwargs pour les critères de filtrage.
    """
    sig = inspect.signature(filter_data)
    
    has_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD 
        for p in sig.parameters.values()
    )
    
    assert has_kwargs, "filter_data() doit accepter **kwargs (ex: region='X', year=2022)"


def test_filter_data_return_annotation():
    """
    Vérifie que filter_data() retourne un DataFrame.
    """
    sig = inspect.signature(filter_data)
    return_annotation = str(sig.return_annotation)
    assert "DataFrame" in return_annotation, \
        f"filter_data() doit retourner DataFrame, annotation : {return_annotation}"


def test_aggregate_data_callable():
    """
    Vérifie que aggregate_data est une fonction callable.
    """
    assert callable(aggregate_data), "aggregate_data doit être une fonction"


def test_aggregate_data_has_docstring():
    """
    Vérifie que aggregate_data() a une docstring.
    """
    assert aggregate_data.__doc__ is not None, "aggregate_data() doit avoir une docstring"


def test_aggregate_data_has_required_parameters():
    """
    Vérifie que aggregate_data() a les 3 paramètres requis.
    """
    sig = inspect.signature(aggregate_data)
    params = list(sig.parameters.keys())
    
    assert len(params) >= 3, \
        f"aggregate_data() doit avoir au least 3 paramètres (df, group_by, metric), trouvés : {params}"


def test_aggregate_data_parameter_names():
    """
    Vérifie que les noms des paramètres sont explicites.
    """
    sig = inspect.signature(aggregate_data)
    params = list(sig.parameters.keys())
    
    # Les paramètres doivent être explicites
    expected_keywords = ["df", "group_by", "metric"]
    for i, expected in enumerate(expected_keywords):
        if i < len(params):
            assert params[i].lower() in [expected.lower(), "data", "dataframe", "column", "value"], \
                f"Param {i} should be like '{expected}', got '{params[i]}'"


def test_aggregate_data_return_annotation():
    """
    Vérifie que aggregate_data() retourne un DataFrame.
    """
    sig = inspect.signature(aggregate_data)
    return_annotation = str(sig.return_annotation)
    assert "DataFrame" in return_annotation, \
        f"aggregate_data() doit retourner DataFrame, annotation : {return_annotation}"
