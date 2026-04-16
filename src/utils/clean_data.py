"""
Module de nettoyage des données.
Charge les données brutes, les nettoie et les sauvegarde
dans data/cleaned/ pour consommation par le dashboard.

Référence cours : https://perso.esiee.fr/.../python-23-codequality.html#responsabilite-unique
Doc pandas     : https://pandas.pydata.org/docs/user_guide/missing_data.html
"""

import pandas as pd
import config


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données
# ─────────────────────────────────────────────────────────────────

def load_raw_data() -> pd.DataFrame:
    """
    Charge le fichier CSV brut depuis data/raw/.

    Returns:
        pd.DataFrame: DataFrame brut non modifié.

    Raises:
        FileNotFoundError: Si rawdata.csv est absent (get_data.py non exécuté).
    """
    # TODO: lire config.DATA_RAW avec pd.read_csv
    pass


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les lignes dupliquées du DataFrame.

    Args:
        df (pd.DataFrame): DataFrame brut pouvant contenir des doublons.

    Returns:
        pd.DataFrame: DataFrame sans doublons.
    """
    # TODO: utiliser df.drop_duplicates()
    pass


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Détecte et traite les valeurs manquantes (NaN).
    Stratégie à définir selon le jeu de données :
    suppression, imputation par moyenne/médiane, ou marquage.

    Args:
        df (pd.DataFrame): DataFrame pouvant contenir des NaN.

    Returns:
        pd.DataFrame: DataFrame sans valeurs manquantes problématiques.
    """
    # TODO: analyser les NaN et choisir la stratégie adaptée
    pass


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme les colonnes en snake_case et caste les types de données
    (float, int, datetime) pour garantir la compatibilité avec Plotly.

    Args:
        df (pd.DataFrame): DataFrame avec colonnes brutes.

    Returns:
        pd.DataFrame: DataFrame avec colonnes normalisées et types corrects.
    """
    # TODO: df.rename(columns={...}), df.astype({...})
    pass


def save_cleaned_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame nettoyé au format CSV dans data/cleaned/.

    Args:
        df (pd.DataFrame): DataFrame nettoyé prêt pour le dashboard.

    Returns:
        None
    """
    # TODO: df.to_csv(config.DATA_CLEAN, index=False)
    pass
