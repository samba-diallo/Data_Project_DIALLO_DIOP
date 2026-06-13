"""
Fonctions utilitaires partagées par l'ensemble des modules de l'application.
Regroupe les méthodes de chargement des données propres, de filtrage dynamique et d'agrégation.

Source des données : table `cleaned` de la base SQLite `data/db.sqlite`
(générée par src/utils/clean_data.py).
"""

import os
import sqlite3
from typing import Any

import pandas as pd
import config

# ── Bornes de la période d'analyse officielle ──────────────────
# 2010 : Année d'instauration des bilans carbone BEGES réglementaires
# 2025 : Dernière année complète pour laquelle les données sont consolidées et publiées
YEAR_MIN: int = 2010
YEAR_MAX: int = 2025


def load_cleaned_data() -> pd.DataFrame:
    """
    Charge le DataFrame nettoyé depuis la table `cleaned` de la base SQLite
    et applique les bornes temporelles officielles [YEAR_MIN, YEAR_MAX].

    Returns:
        pd.DataFrame: Données prêtes à l'analyse et restreintes sur l'intervalle [2010, 2025].

    Raises:
        FileNotFoundError: Si la base SQLite n'a pas encore été générée.
    """
    # Garde-fou pour produire un message d'erreur explicite si la base
    # n'existe pas (l'utilisateur n'a pas encore lancé get_data + clean_data).
    if not os.path.exists(config.DATABASE):
        raise FileNotFoundError(
            f"Base SQLite introuvable : {config.DATABASE}\n"
            "Lancer 'python -m src.utils.get_data' "
            "puis 'python -m src.utils.clean_data'."
        )

    # Connexion SQLite + lecture de la table `cleaned`. On reste sur
    # sqlite3 + pandas.read_sql_query (pas besoin de SQLAlchemy comme
    # dépendance supplémentaire).
    with sqlite3.connect(config.DATABASE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {config.TABLE_CLEAN}", conn)

    # Restriction stricte des données entre 2010 et 2025 pour assurer
    # la cohérence des graphiques (filtrage centralisé : toutes les
    # pages voient la même période).
    df = df[df["annee_reporting"].between(YEAR_MIN, YEAR_MAX)].copy()
    return df  # pyrefly: ignore


def filter_data(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """
    Filtre dynamiquement un DataFrame en fonction des colonnes et des critères fournis.

    Args:
        df (pd.DataFrame): Le DataFrame de départ à filtrer.
        **kwargs (Any): Les paires nom_colonne=valeur servant à appliquer les filtres.

    Returns:
        pd.DataFrame: Le DataFrame filtré résultant.
    """
    result = df

    # Parcours de l'ensemble des critères de filtrage passés en argument
    for column, value in kwargs.items():
        # Ignorer le critère si la valeur est nulle ou si la colonne n'existe pas
        if value is None or column not in result.columns:
            continue

        # Filtrage par appartenance si la valeur fournie est une liste ou un ensemble de valeurs
        if isinstance(value, (list, tuple, set)):
            result = result[result[column].isin(value)]
        else:
            # Filtrage par égalité simple si la valeur fournie est un scalaire
            result = result[result[column] == value]

    return result  # pyrefly: ignore


def aggregate_data(
    df: pd.DataFrame,
    group_by: str,
    metric: str,
    agg: str = "sum",
) -> pd.DataFrame:
    """
    Agrège les données d'un DataFrame selon une colonne et une métrique de regroupement.

    Args:
        df (pd.DataFrame): Le DataFrame d'origine.
        group_by (str): Nom de la colonne sur laquelle regrouper (ex: "region").
        metric (str): Nom de la colonne numérique à agréger.
        agg (str): Fonction d'agrégation à appliquer ("sum", "mean", "count", etc.).

    Returns:
        pd.DataFrame: DataFrame regroupé et trié dans l'ordre décroissant de la métrique.
    """
    # Regroupement et agrégation
    aggregated = df.groupby(group_by, as_index=False)[[metric]].agg(agg)

    # Tri du résultat du plus grand au plus petit pour faciliter la lecture des classements
    return aggregated.sort_values(metric, ascending=False).reset_index(drop=True)  # pyrefly: ignore
