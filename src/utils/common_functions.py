"""
Fonctions utilitaires partagées par tous les composants du dashboard.
Chargement, filtrage et agrégation des données nettoyées.
"""

# Any : pour typer les valeurs arbitraires acceptées par filter_data
# (peuvent être int, str, list, tuple, etc.)
from typing import Any

# pandas : manipulation tabulaire (DataFrame, isin, groupby, agg...)
import pandas as pd

# config : pour récupérer le chemin du fichier nettoyé (DATA_CLEAN)
import config


# ─────────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES – Période d'étude officielle
# ─────────────────────────────────────────────────────────────────

# Période standardisée pour TOUS les graphiques et filtres du dashboard.
# - 2010 : début de l'obligation réglementaire BEGES (loi Grenelle II)
# - 2025 : dernière année complète de reporting disponible
# Les bilans 2026 sont exclus car les déclarations ne sont pas encore
# publiées (ADEME publie en N+1). Les années < 2010 sont anecdotiques
# (quelques dizaines de bilans, biais d'analyse).
YEAR_MIN: int = 2010
YEAR_MAX: int = 2025


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données / Commun
# ─────────────────────────────────────────────────────────────────

def load_cleaned_data() -> pd.DataFrame:
    """
    Charge les données nettoyées depuis data/cleaned/ et applique le
    filtre de période officielle [YEAR_MIN, YEAR_MAX] pour garantir
    la cohérence de toutes les visualisations du dashboard.

    Returns:
        pd.DataFrame: DataFrame nettoyé filtré sur 2010-2025.

    Raises:
        FileNotFoundError: Si le fichier nettoyé n'existe pas.
    """
    # Lecture simple du CSV produit par clean_data.main(). pandas gère
    # automatiquement l'inférence des types numériques.
    df = pd.read_csv(config.DATA_CLEAN)

    # Application du filtre de période OFFICIELLE.
    # On filtre ici (point central) plutôt que dans chaque composant pour
    # garantir que toutes les pages voient la même période et éviter les
    # incohérences (ex: KPI sur 2009-2026 vs slider 2010-2025).
    df = df[df["annee_reporting"].between(YEAR_MIN, YEAR_MAX)].copy()
    return df


def filter_data(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """
    Filtre dynamiquement le DataFrame selon des critères arbitraires.
    Une valeur scalaire applique un filtre d'égalité, une liste/tuple
    applique un filtre d'appartenance (isin), None est ignoré.

    Args:
        df (pd.DataFrame): DataFrame source.
        **kwargs: Paires colonne=valeur à utiliser comme filtres.
                  Ex: filter_data(df, region="Île-de-France",
                                  annee_reporting=[2022, 2023])

    Returns:
        pd.DataFrame: Sous-ensemble filtré du DataFrame.
    """
    # On part du DataFrame complet et on rétrécit progressivement à
    # chaque critère (filtres combinés en AND logique).
    result = df

    # **kwargs permet d'appeler filter_data(df, region=..., annee=...)
    # sans devoir lister toutes les colonnes possibles dans la signature.
    # On itère sur chaque paire (nom_colonne, valeur_filtre).
    for column, value in kwargs.items():
        # On ignore les filtres "vides" : None ou colonne inexistante.
        # Cela permet aux callbacks Dash de passer des filtres optionnels
        # sans avoir à les construire conditionnellement.
        if value is None or column not in result.columns:
            continue

        # Filtre par appartenance : si l'utilisateur passe une liste,
        # tuple ou set, on utilise .isin() (ex: années 2022, 2023, 2024).
        # Pratique pour les Dropdown multi-sélection de Dash.
        if isinstance(value, (list, tuple, set)):
            result = result[result[column].isin(value)]
        else:
            # Filtre d'égalité simple pour une valeur scalaire.
            result = result[result[column] == value]

    return result


def aggregate_data(
    df: pd.DataFrame,
    group_by: str,
    metric: str,
    agg: str = "sum",
) -> pd.DataFrame:
    """
    Agrège les données par groupe pour alimenter les graphiques.

    Args:
        df (pd.DataFrame): DataFrame source.
        group_by (str): Nom de la colonne de regroupement (ex: "region").
        metric (str): Nom de la colonne numérique à agréger (ex: "total_emissions").
        agg (str): Fonction d'agrégation pandas ("sum", "mean", "median", "count").

    Returns:
        pd.DataFrame: DataFrame agrégé avec les colonnes group_by et metric,
                      trié par metric décroissant.
    """
    # groupby(...) regroupe les lignes par valeur de group_by.
    # as_index=False garde group_by comme colonne normale plutôt que comme
    # index - plus pratique à manipuler ensuite (ex: passer à plotly).
    # [metric].agg(agg) applique la fonction d'agrégation choisie sur la
    # colonne métrique (sum, mean, median, count...).
    aggregated = df.groupby(group_by, as_index=False)[metric].agg(agg)

    # Tri décroissant sur la métrique : utile pour afficher des "top N"
    # (top régions émettrices, top secteurs, etc.).
    # reset_index(drop=True) renumérote proprement les indices après tri.
    return aggregated.sort_values(metric, ascending=False).reset_index(drop=True)
