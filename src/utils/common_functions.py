"""
Fonctions utilitaires partagées par l'ensemble des modules de l'application.
Regroupe les méthodes de chargement des données propres, de filtrage dynamique et d'agrégation.
"""

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
    Charge le fichier CSV de données nettoyées et applique les bornes temporelles.

    Returns:
        pd.DataFrame: Données prêtes à l'analyse et restreintes sur l'intervalle [2010, 2025].
    """
    # Lecture du fichier CSV à l'aide de pandas
    df = pd.read_csv(config.DATA_CLEAN)

    # Restriction stricte des données entre 2010 et 2025 pour assurer la cohérence des graphiques
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
