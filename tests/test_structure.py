"""
Tests unitaires pour la structure du code.

Vérifie les signatures des fonctions, les types, et la documentation.
Pas de données réelles requises.

Doc pytest : https://docs.pytest.org/en/stable/
Doc inspect : https://docs.python.org/3/library/inspect.html
"""

import pytest
import inspect
from src.utils.get_data import download_data, save_raw_data
from src.utils.clean_data import (
    load_raw_data,
    remove_duplicates,
    handle_missing_values,
    normalize_columns,
    save_cleaned_data,
)
from src.utils.common_functions import load_cleaned_data, filter_data, aggregate_data
from main import create_app, define_layout, register_callbacks
from src.pages.home import layout as home_layout
from src.pages.analysis import layout as analysis_layout
from src.pages.about import layout as about_layout
from src.components.navbar import create_navbar
from src.components.header import create_header
from src.components.footer import create_footer
from src.components.histogram import create_histogram
from src.components.geomap import create_geomap


# ─────────────────────────────────────────────────────────────────
# Tests – Structure et Signatures
# ─────────────────────────────────────────────────────────────────

class TestGetDataStructure:
    """Tests de structure pour get_data.py"""

    def test_download_data_has_docstring(self):
        """Vérifie que download_data() a une docstring."""
        assert download_data.__doc__ is not None, "download_data() doit avoir une docstring"
        assert len(download_data.__doc__.strip()) > 0, "download_data() docstring ne doit pas être vide"

    def test_download_data_return_annotation(self):
        """Vérifie que download_data() a une annotation de retour."""
        sig = inspect.signature(download_data)
        assert sig.return_annotation != inspect.Signature.empty, "download_data() doit avoir une annotation de retour"

    def test_save_raw_data_has_docstring(self):
        """Vérifie que save_raw_data() a une docstring."""
        assert save_raw_data.__doc__ is not None, "save_raw_data() doit avoir une docstring"

    def test_save_raw_data_has_parameters(self):
        """Vérifie que save_raw_data() a au moins 1 paramètre."""
        sig = inspect.signature(save_raw_data)
        assert len(sig.parameters) >= 1, "save_raw_data() doit avoir au moins 1 paramètre"


class TestCleanDataStructure:
    """Tests de structure pour clean_data.py"""

    def test_load_raw_data_has_docstring(self):
        """Vérifie que load_raw_data() a une docstring."""
        assert load_raw_data.__doc__ is not None, "load_raw_data() doit avoir une docstring"

    def test_load_raw_data_return_annotation(self):
        """Vérifie que load_raw_data() a une annotation de retour."""
        sig = inspect.signature(load_raw_data)
        assert sig.return_annotation != inspect.Signature.empty, "load_raw_data() doit avoir une annotation de retour"

    def test_remove_duplicates_has_docstring(self):
        """Vérifie que remove_duplicates() a une docstring."""
        assert remove_duplicates.__doc__ is not None, "remove_duplicates() doit avoir une docstring"

    def test_remove_duplicates_has_parameter(self):
        """Vérifie que remove_duplicates() a au moins 1 paramètre."""
        sig = inspect.signature(remove_duplicates)
        assert len(sig.parameters) >= 1, "remove_duplicates() doit avoir au moins 1 paramètre"

    def test_handle_missing_values_has_docstring(self):
        """Vérifie que handle_missing_values() a une docstring."""
        assert handle_missing_values.__doc__ is not None, "handle_missing_values() doit avoir une docstring"

    def test_normalize_columns_has_docstring(self):
        """Vérifie que normalize_columns() a une docstring."""
        assert normalize_columns.__doc__ is not None, "normalize_columns() doit avoir une docstring"

    def test_save_cleaned_data_has_docstring(self):
        """Vérifie que save_cleaned_data() a une docstring."""
        assert save_cleaned_data.__doc__ is not None, "save_cleaned_data() doit avoir une docstring"


class TestCommonFunctionsStructure:
    """Tests de structure pour common_functions.py"""

    def test_load_cleaned_data_has_docstring(self):
        """Vérifie que load_cleaned_data() a une docstring."""
        assert load_cleaned_data.__doc__ is not None, "load_cleaned_data() doit avoir une docstring"

    def test_load_cleaned_data_return_annotation(self):
        """Vérifie que load_cleaned_data() a une annotation de retour."""
        sig = inspect.signature(load_cleaned_data)
        assert sig.return_annotation != inspect.Signature.empty, "load_cleaned_data() doit avoir une annotation de retour"

    def test_filter_data_has_docstring(self):
        """Vérifie que filter_data() a une docstring."""
        assert filter_data.__doc__ is not None, "filter_data() doit avoir une docstring"

    def test_filter_data_has_kwargs(self):
        """Vérifie que filter_data() accepte **kwargs."""
        sig = inspect.signature(filter_data)
        assert any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()), \
            "filter_data() doit accepter **kwargs"

    def test_aggregate_data_has_docstring(self):
        """Vérifie que aggregate_data() a une docstring."""
        assert aggregate_data.__doc__ is not None, "aggregate_data() doit avoir une docstring"

    def test_aggregate_data_has_parameters(self):
        """Vérifie que aggregate_data() a au moins 3 paramètres."""
        sig = inspect.signature(aggregate_data)
        assert len(sig.parameters) >= 3, "aggregate_data() doit avoir au moins 3 paramètres"


class TestMainStructure:
    """Tests de structure pour main.py"""

    def test_create_app_has_docstring(self):
        """Vérifie que create_app() a une docstring."""
        assert create_app.__doc__ is not None, "create_app() doit avoir une docstring"

    def test_define_layout_has_docstring(self):
        """Vérifie que define_layout() a une docstring."""
        assert define_layout.__doc__ is not None, "define_layout() doit avoir une docstring"

    def test_define_layout_has_app_parameter(self):
        """Vérifie que define_layout() prend un paramètre 'app'."""
        sig = inspect.signature(define_layout)
        assert 'app' in sig.parameters, "define_layout() doit avoir un paramètre 'app'"

    def test_register_callbacks_has_docstring(self):
        """Vérifie que register_callbacks() a une docstring."""
        assert register_callbacks.__doc__ is not None, "register_callbacks() doit avoir une docstring"

    def test_register_callbacks_has_app_parameter(self):
        """Vérifie que register_callbacks() prend un paramètre 'app'."""
        sig = inspect.signature(register_callbacks)
        assert 'app' in sig.parameters, "register_callbacks() doit avoir un paramètre 'app'"


class TestPagesStructure:
    """Tests de structure pour les pages"""

    def test_home_layout_has_docstring(self):
        """Vérifie que home.layout() a une docstring."""
        assert home_layout.__doc__ is not None, "home.layout() doit avoir une docstring"

    def test_home_layout_return_annotation(self):
        """Vérifie que home.layout() a une annotation de retour."""
        sig = inspect.signature(home_layout)
        assert sig.return_annotation != inspect.Signature.empty, "home.layout() doit avoir une annotation de retour"

    def test_analysis_layout_has_docstring(self):
        """Vérifie que analysis.layout() a une docstring."""
        assert analysis_layout.__doc__ is not None, "analysis.layout() doit avoir une docstring"

    def test_analysis_layout_return_annotation(self):
        """Vérifie que analysis.layout() a une annotation de retour."""
        sig = inspect.signature(analysis_layout)
        assert sig.return_annotation != inspect.Signature.empty, "analysis.layout() doit avoir une annotation de retour"

    def test_about_layout_has_docstring(self):
        """Vérifie que about.layout() a une docstring."""
        assert about_layout.__doc__ is not None, "about.layout() doit avoir une docstring"


class TestComponentsStructure:
    """Tests de structure pour les composants"""

    def test_create_navbar_has_docstring(self):
        """Vérifie que create_navbar() a une docstring."""
        assert create_navbar.__doc__ is not None, "create_navbar() doit avoir une docstring"

    def test_create_navbar_return_annotation(self):
        """Vérifie que create_navbar() a une annotation de retour."""
        sig = inspect.signature(create_navbar)
        assert sig.return_annotation != inspect.Signature.empty, "create_navbar() doit avoir une annotation de retour"

    def test_create_header_has_docstring(self):
        """Vérifie que create_header() a une docstring."""
        assert create_header.__doc__ is not None, "create_header() doit avoir une docstring"

    def test_create_footer_has_docstring(self):
        """Vérifie que create_footer() a une docstring."""
        assert create_footer.__doc__ is not None, "create_footer() doit avoir une docstring"

    def test_create_histogram_has_docstring(self):
        """Vérifie que create_histogram() a une docstring."""
        assert create_histogram.__doc__ is not None, "create_histogram() doit avoir une docstring"

    def test_create_histogram_has_parameters(self):
        """Vérifie que create_histogram() a au moins 3 paramètres."""
        sig = inspect.signature(create_histogram)
        assert len(sig.parameters) >= 3, "create_histogram() doit avoir au moins 3 paramètres"

    def test_create_histogram_return_annotation(self):
        """Vérifie que create_histogram() a une annotation de retour."""
        sig = inspect.signature(create_histogram)
        assert sig.return_annotation != inspect.Signature.empty, "create_histogram() doit avoir une annotation de retour"

    def test_create_geomap_has_docstring(self):
        """Vérifie que create_geomap() a une docstring."""
        assert create_geomap.__doc__ is not None, "create_geomap() doit avoir une docstring"

    def test_create_geomap_has_parameters(self):
        """Vérifie que create_geomap() a au moins 4 paramètres."""
        sig = inspect.signature(create_geomap)
        assert len(sig.parameters) >= 4, "create_geomap() doit avoir au moins 4 paramètres"

    def test_create_geomap_return_annotation(self):
        """Vérifie que create_geomap() a une annotation de retour."""
        sig = inspect.signature(create_geomap)
        assert sig.return_annotation != inspect.Signature.empty, "create_geomap() doit avoir une annotation de retour"
