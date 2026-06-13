"""
Tests unitaires pour config.py.

Vérifie que la configuration du projet est correcte et accessible.
Pas de données réelles requises.

Doc pytest : https://docs.pytest.org/en/stable/
"""

import pytest
import os
import config


# ─────────────────────────────────────────────────────────────────
# Tests – Configuration
# ─────────────────────────────────────────────────────────────────

def test_config_base_dir_exists():
    """
    Vérifie que BASE_DIR est défini et qu'il existe.
    """
    assert hasattr(config, 'BASE_DIR'), "config.BASE_DIR doit être défini"
    assert isinstance(config.BASE_DIR, str), "BASE_DIR doit être une chaîne"
    assert os.path.isdir(config.BASE_DIR), f"BASE_DIR n'existe pas : {config.BASE_DIR}"


def test_config_data_paths_defined():
    """
    Vérifie que les paramètres SQLite (base + noms de tables) sont définis.
    Le stockage des données est imposé en SQLite par le cahier des charges
    (une base unique `data/db.sqlite` avec deux tables `raw` et `cleaned`).
    """
    assert hasattr(config, 'DATABASE'), "config.DATABASE doit être défini"
    assert hasattr(config, 'TABLE_RAW'), "config.TABLE_RAW doit être défini"
    assert hasattr(config, 'TABLE_CLEAN'), "config.TABLE_CLEAN doit être défini"
    assert isinstance(config.DATABASE, str), "DATABASE doit être une chaîne"
    assert isinstance(config.TABLE_RAW, str), "TABLE_RAW doit être une chaîne"
    assert isinstance(config.TABLE_CLEAN, str), "TABLE_CLEAN doit être une chaîne"


def test_config_data_directories_exist():
    """
    Vérifie que le répertoire parent de la base SQLite existe (data/).
    """
    db_dir = os.path.dirname(config.DATABASE)
    assert os.path.isdir(db_dir), f"Répertoire data/ n'existe pas : {db_dir}"


def test_config_data_url_exists():
    """
    Vérifie que DATA_URL est défini.
    """
    assert hasattr(config, 'DATA_URL'), "config.DATA_URL doit être défini"
    assert isinstance(config.DATA_URL, str), "DATA_URL doit être une chaîne"


def test_config_dash_parameters():
    """
    Vérifie que les paramètres Dash sont définis et valides.
    """
    assert hasattr(config, 'APP_TITLE'), "config.APP_TITLE doit être défini"
    assert hasattr(config, 'DEBUG_MODE'), "config.DEBUG_MODE doit être défini"
    assert hasattr(config, 'HOST'), "config.HOST doit être défini"
    assert hasattr(config, 'PORT'), "config.PORT doit être défini"
    
    assert isinstance(config.APP_TITLE, str), "APP_TITLE doit être une chaîne"
    assert isinstance(config.DEBUG_MODE, bool), "DEBUG_MODE doit être un booléen"
    assert isinstance(config.HOST, str), "HOST doit être une chaîne"
    assert isinstance(config.PORT, int), "PORT doit être un entier"
    
    assert 1 <= config.PORT <= 65535, f"PORT doit être entre 1 et 65535, reçu : {config.PORT}"


def test_config_app_title_not_empty():
    """
    Vérifie que APP_TITLE n'est pas vide.
    """
    assert config.APP_TITLE.strip(), "APP_TITLE ne doit pas être vide"
