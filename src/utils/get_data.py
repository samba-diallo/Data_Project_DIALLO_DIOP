"""
Module de récupération des données brutes.
Télécharge les données depuis la source définie dans config.py
et les sauvegarde dans data/raw/.

Référence cours : https://perso.esiee.fr/.../python-29-projet-data.html#acces
Doc pandas     : https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
"""

import pandas as pd
import config


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données
# ─────────────────────────────────────────────────────────────────

def download_data() -> pd.DataFrame:
    """
    Télécharge les données brutes depuis l'URL définie dans config.DATA_URL.

    Returns:
        pd.DataFrame: DataFrame contenant les données brutes telles que
                      récupérées depuis la source (aucune modification).

    Raises:
        ConnectionError: Si la source est inaccessible.
        ValueError: Si le format du fichier n'est pas supporté.
    """
    # TODO: implémenter le téléchargement
    pass


def save_raw_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame brut au format CSV dans data/raw/
    sans aucune modification des données.

    Args:
        df (pd.DataFrame): DataFrame brut à sauvegarder.

    Returns:
        None
    """
    # TODO: créer les répertoires si nécessaire et sauvegarder en CSV
    pass
