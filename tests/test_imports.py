"""
Tests unitaires pour les imports du projet.

Vérifie que tous les modules et fonctions peuvent être importés correctement.
Pas de données réelles requises.

Doc pytest : https://docs.pytest.org/en/stable/
"""

import pytest
import importlib


# ─────────────────────────────────────────────────────────────────
# Tests – Imports
# ─────────────────────────────────────────────────────────────────

def test_import_config():
    """
    Vérifie que le module config peut être importé.
    """
    try:
        import config
        assert config is not None
    except ImportError as e:
        pytest.fail(f"Impossible d'importer config : {e}")


def test_import_main():
    """
    Vérifie que le module main peut être importé.
    """
    try:
        import main
        assert main is not None
    except ImportError as e:
        pytest.fail(f"Impossible d'importer main : {e}")


def test_import_src_modules():
    """
    Vérifie que les packages src/ peuvent être importés.
    """
    modules = [
        "src",
        "src.components",
        "src.pages",
        "src.utils",
    ]
    
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"{module_name} est None"
        except ImportError as e:
            pytest.fail(f"Impossible d'importer {module_name} : {e}")


def test_import_utils_modules():
    """
    Vérifie que les modules utils/ peuvent être importés.
    """
    utils_modules = [
        "src.utils.get_data",
        "src.utils.clean_data",
        "src.utils.common_functions",
    ]
    
    for module_name in utils_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"{module_name} est None"
        except ImportError as e:
            pytest.fail(f"Impossible d'importer {module_name} : {e}")


def test_import_pages_modules():
    """
    Vérifie que les modules pages/ peuvent être importés.
    """
    page_modules = [
        "src.pages.home",
        "src.pages.analysis",
        "src.pages.about",
    ]
    
    for module_name in page_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"{module_name} est None"
        except ImportError as e:
            pytest.fail(f"Impossible d'importer {module_name} : {e}")


def test_import_components_modules():
    """
    Vérifie que les modules components/ peuvent être importés.
    """
    component_modules = [
        "src.components.navbar",
        "src.components.header",
        "src.components.footer",
        "src.components.histogram",
        "src.components.geomap",
    ]
    
    for module_name in component_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"{module_name} est None"
        except ImportError as e:
            pytest.fail(f"Impossible d'importer {module_name} : {e}")


def test_import_functions_get_data():
    """
    Vérifie que les fonctions de get_data peuvent être importées.
    """
    from src.utils.get_data import download_data, save_raw_data, main
    
    assert callable(download_data), "download_data doit être une fonction"
    assert callable(save_raw_data), "save_raw_data doit être une fonction"
    assert callable(main), "main doit être une fonction"


def test_import_functions_clean_data():
    """
    Vérifie que les fonctions de clean_data peuvent être importées.
    """
    from src.utils.clean_data import (
        load_raw_data,
        remove_duplicates,
        handle_missing_values,
        normalize_columns,
        save_cleaned_data,
        main,
    )
    
    assert callable(load_raw_data), "load_raw_data doit être une fonction"
    assert callable(remove_duplicates), "remove_duplicates doit être une fonction"
    assert callable(handle_missing_values), "handle_missing_values doit être une fonction"
    assert callable(normalize_columns), "normalize_columns doit être une fonction"
    assert callable(save_cleaned_data), "save_cleaned_data doit être une fonction"
    assert callable(main), "main doit être une fonction"


def test_import_functions_common_functions():
    """
    Vérifie que les fonctions de common_functions peuvent être importées.
    """
    from src.utils.common_functions import load_cleaned_data, filter_data, aggregate_data
    
    assert callable(load_cleaned_data), "load_cleaned_data doit être une fonction"
    assert callable(filter_data), "filter_data doit être une fonction"
    assert callable(aggregate_data), "aggregate_data doit être une fonction"


def test_import_functions_main():
    """
    Vérifie que les fonctions de main peuvent être importées.
    """
    from main import create_app, define_layout, register_callbacks, main
    
    assert callable(create_app), "create_app doit être une fonction"
    assert callable(define_layout), "define_layout doit être une fonction"
    assert callable(register_callbacks), "register_callbacks doit être une fonction"
    assert callable(main), "main doit être une fonction"


def test_import_functions_pages():
    """
    Vérifie que les fonctions layout et register_callbacks de chaque page peuvent être importées.
    """
    from src.pages.home import layout as home_layout, register_callbacks as home_callbacks
    from src.pages.analysis import layout as analysis_layout, register_callbacks as analysis_callbacks
    from src.pages.about import layout as about_layout, register_callbacks as about_callbacks
    
    assert callable(home_layout), "home.layout doit être une fonction"
    assert callable(home_callbacks), "home.register_callbacks doit être une fonction"
    
    assert callable(analysis_layout), "analysis.layout doit être une fonction"
    assert callable(analysis_callbacks), "analysis.register_callbacks doit être une fonction"
    
    assert callable(about_layout), "about.layout doit être une fonction"
    assert callable(about_callbacks), "about.register_callbacks doit être une fonction"


def test_import_functions_components():
    """
    Vérifie que les fonctions create_* de chaque composant peuvent être importées.
    """
    from src.components.navbar import create_navbar
    from src.components.header import create_header
    from src.components.footer import create_footer
    from src.components.histogram import create_histogram
    from src.components.geomap import create_geomap
    
    assert callable(create_navbar), "create_navbar doit être une fonction"
    assert callable(create_header), "create_header doit être une fonction"
    assert callable(create_footer), "create_footer doit être une fonction"
    assert callable(create_histogram), "create_histogram doit être une fonction"
    assert callable(create_geomap), "create_geomap doit être une fonction"
