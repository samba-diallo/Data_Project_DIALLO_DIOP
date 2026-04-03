"""
Fonctions utilitaires partagées par tous les composants du dashboard.
Chargement, filtrage et agrégation des données nettoyées.

Référence cours : https://perso.esiee.fr/.../python-28-dash.html#interaction-simple
Doc pandas     : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html
"""

import pandas as pd
import config


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données / Commun
# ─────────────────────────────────────────────────────────────────

def load_cleaned_data() -> pd.DataFrame:
    """
    Charge les données nettoyées depuis data/cleaned/.
    Fonction partagée par tous les composants du dashboard pour éviter
    de lire le CSV plusieurs fois.

    Returns:
        pd.DataFrame: DataFrame nettoyé prêt à l'emploi.
    """
    # TODO: pd.read_csv(config.DATA_CLEAN)
    pass


def filter_data(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Filtre dynamiquement le DataFrame selon des critères arbitraires.
    Appelée par les callbacks Dash lors des interactions utilisateur.

    Args:
        df (pd.DataFrame): DataFrame source.
        **kwargs: Paires colonne=valeur à utiliser comme filtres.
                  Ex: filter_data(df, region="Île-de-France", year=2022)

    Returns:
        pd.DataFrame: Sous-ensemble filtré du DataFrame.
    """
    # TODO: itérer sur kwargs et appliquer les filtres
    pass


def aggregate_data(df: pd.DataFrame, group_by: str, metric: str) -> pd.DataFrame:
    """
    Agrège les données par groupe pour alimenter les graphiques.

    Args:
        df (pd.DataFrame): DataFrame source.
        group_by (str): Nom de la colonne de regroupement (ex: "region").
        metric (str): Nom de la colonne numérique à agréger (ex: "valeur").

    Returns:
        pd.DataFrame: DataFrame agrégé avec les colonnes group_by et metric.
    """
    # TODO: df.groupby(group_by)[metric].sum().reset_index()
    pass
