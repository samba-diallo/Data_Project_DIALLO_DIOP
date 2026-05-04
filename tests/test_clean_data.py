"""
Tests unitaires pour src/utils/clean_data.py.

Doc cours  : https://perso.esiee.fr/.../python-23-codequality.html#tests-integres
Doc pytest : https://docs.pytest.org/en/stable/
"""

import pytest
import pandas as pd
import inspect
from src.utils.clean_data import (
    load_raw_data,
    remove_duplicates,
    handle_missing_values,
    normalize_columns,
    save_cleaned_data,
    main,
)


# ─────────────────────────────────────────────────────────────────
# Tests – Structure et Signatures
# ─────────────────────────────────────────────────────────────────

def test_load_raw_data_callable():
    """
    Vérifie que load_raw_data est une fonction callable.
    """
    assert callable(load_raw_data), "load_raw_data doit être une fonction"


def test_load_raw_data_has_docstring():
    """
    Vérifie que load_raw_data() a une docstring.
    """
    assert load_raw_data.__doc__ is not None, "load_raw_data() doit avoir une docstring"


def test_load_raw_data_return_annotation():
    """
    Vérifie que load_raw_data() a une annotation de retour DataFrame.
    """
    sig = inspect.signature(load_raw_data)
    assert sig.return_annotation != inspect.Signature.empty, \
        "load_raw_data() doit avoir une annotation de type de retour (-> pd.DataFrame)"


def test_remove_duplicates_callable():
    """
    Vérifie que remove_duplicates est une fonction callable.
    """
    assert callable(remove_duplicates), "remove_duplicates doit être une fonction"


def test_remove_duplicates_has_docstring():
    """
    Vérifie que remove_duplicates() a une docstring.
    """
    assert remove_duplicates.__doc__ is not None, "remove_duplicates() doit avoir une docstring"


def test_remove_duplicates_has_parameter():
    """
    Vérifie que remove_duplicates() accepte au moins 1 paramètre (DataFrame).
    """
    sig = inspect.signature(remove_duplicates)
    assert len(sig.parameters) >= 1, "remove_duplicates() doit avoir au moins 1 paramètre"


def test_remove_duplicates_return_annotation():
    """
    Vérifie que remove_duplicates() retourne un DataFrame.
    """
    sig = inspect.signature(remove_duplicates)
    return_annotation = str(sig.return_annotation)
    assert "DataFrame" in return_annotation, \
        f"remove_duplicates() doit retourner DataFrame, annotation : {return_annotation}"


def test_handle_missing_values_callable():
    """
    Vérifie que handle_missing_values est une fonction callable.
    """
    assert callable(handle_missing_values), "handle_missing_values doit être une fonction"


def test_handle_missing_values_has_docstring():
    """
    Vérifie que handle_missing_values() a une docstring.
    """
    assert handle_missing_values.__doc__ is not None, "handle_missing_values() doit avoir une docstring"


def test_handle_missing_values_has_parameter():
    """
    Vérifie que handle_missing_values() accepte au moins 1 paramètre.
    """
    sig = inspect.signature(handle_missing_values)
    assert len(sig.parameters) >= 1, "handle_missing_values() doit avoir au moins 1 paramètre"


def test_normalize_columns_callable():
    """
    Vérifie que normalize_columns est une fonction callable.
    """
    assert callable(normalize_columns), "normalize_columns doit être une fonction"


def test_normalize_columns_has_docstring():
    """
    Vérifie que normalize_columns() a une docstring.
    """
    assert normalize_columns.__doc__ is not None, "normalize_columns() doit avoir une docstring"


def test_normalize_columns_has_parameter():
    """
    Vérifie que normalize_columns() accepte au moins 1 paramètre.
    """
    sig = inspect.signature(normalize_columns)
    assert len(sig.parameters) >= 1, "normalize_columns() doit avoir au moins 1 paramètre"


def test_normalize_columns_return_annotation():
    """
    Vérifie que normalize_columns() retourne un DataFrame.
    """
    sig = inspect.signature(normalize_columns)
    return_annotation = str(sig.return_annotation)
    assert "DataFrame" in return_annotation, \
        f"normalize_columns() doit retourner DataFrame, annotation : {return_annotation}"


def test_save_cleaned_data_callable():
    """
    Vérifie que save_cleaned_data est une fonction callable.
    """
    assert callable(save_cleaned_data), "save_cleaned_data doit être une fonction"


def test_save_cleaned_data_has_docstring():
    """
    Vérifie que save_cleaned_data() a une docstring.
    """
    assert save_cleaned_data.__doc__ is not None, "save_cleaned_data() doit avoir une docstring"


def test_save_cleaned_data_has_parameter():
    """
    Vérifie que save_cleaned_data() accepte au moins 1 paramètre (DataFrame).
    """
    sig = inspect.signature(save_cleaned_data)
    assert len(sig.parameters) >= 1, "save_cleaned_data() doit avoir au moins 1 paramètre"


def test_save_cleaned_data_return_annotation():
    """
    Vérifie que save_cleaned_data() retourne None.
    """
    sig = inspect.signature(save_cleaned_data)
    return_annotation = str(sig.return_annotation)
    assert "None" in return_annotation or sig.return_annotation == type(None), \
        f"save_cleaned_data() doit retourner None, annotation : {return_annotation}"


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
