"""
Module de nettoyage et de préparation des données brutes de l'ADEME.
Charge la table `raw` de la base SQLite, applique des filtres de qualité
(déduplication, normalisation des noms de région, suppression des
caractères PUA), puis écrit la table `cleaned` dans la même base.

Stockage SQLite imposé par le cahier des charges : une seule base
`data/db.sqlite` avec deux tables (`raw` et `cleaned`).
"""

import os
import sqlite3

import pandas as pd
import config

# ── Mapping de renommage des colonnes descriptives essentielles ──────────────────
COLUMN_MAPPING: dict[str, str] = {
    "Id": "id",
    "Année de reporting": "annee_reporting",
    "Année de référence": "annee_reference",
    "Région": "region",
    "Code département": "code_departement",
    "Département": "departement",
    "Type de structure": "type_structure",
    "Type de collectivité": "type_collectivite",
    "Raison sociale": "raison_sociale",
    "SIREN principal": "siren",
    "APE(NAF) associé": "code_naf",
    "Libellé": "libelle_naf",
    "Population": "population",
    "Méthode BEGES (V4,V5)": "methode_beges",
}

# Liste des couples (numéro_scope, numéro_poste) définissant les 22 postes BEGES officiels
EMISSION_POSTS: list[tuple[int, int]] = [
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    (2, 1), (2, 2),
    (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
    (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
    (5, 1), (5, 2), (5, 3), (5, 4),
    (6, 1),
]

# Construction dynamique du mapping de renommage des colonnes d'émissions (ex: "Emissions publication P1.1" -> "emissions_p1_1")
EMISSION_MAPPING: dict[str, str] = {
    f"Emissions publication P{s}.{i}": f"emissions_p{s}_{i}"
    for s, i in EMISSION_POSTS
}

# Plage Unicode des caractères de la "Private Use Area" (PUA) souvent présents suite à des copier-coller depuis Word
PUA_RANGE = range(0xE000, 0xF8FF + 1)

# Harmonisation des régions avec la nomenclature officielle INSEE présente dans le GeoJSON
REGION_NAME_FIXES: dict[str, str] = {
    "Hauts de France": "Hauts-de-France",
}

# Exclusion des régions fictives ou administratives non représentables géographiquement
REGIONS_TO_EXCLUDE: set[str] = {"DR ADEME"}


def load_raw_data() -> pd.DataFrame:
    """
    Charge le DataFrame brut depuis la table `raw` de la base SQLite.

    Returns:
        pd.DataFrame: Données brutes telles que stockées par get_data.py.

    Raises:
        FileNotFoundError: Si la base SQLite n'existe pas
                           (lancer get_data au préalable).
    """
    # Vérification explicite avant pd.read_sql pour produire un message
    # d'erreur parlant et la commande de réparation correspondante.
    if not os.path.exists(config.DATABASE):
        raise FileNotFoundError(
            f"Base SQLite introuvable : {config.DATABASE}\n"
            "Lancer 'python -m src.utils.get_data' pour la créer."
        )

    # Connexion en lecture seule du DataFrame brut. pd.read_sql_table
    # nécessiterait SQLAlchemy ; pd.read_sql_query reste sur sqlite3 stdlib.
    with sqlite3.connect(config.DATABASE) as conn:
        return pd.read_sql_query(f"SELECT * FROM {config.TABLE_RAW}", conn)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les doublons de bilans en se basant sur leur identifiant unique 'Id'.

    Args:
        df (pd.DataFrame): DataFrame brut.

    Returns:
        pd.DataFrame: DataFrame dédupliqué.
    """
    return df.drop_duplicates(subset="Id", keep="first")


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les bilans ne contenant pas les dimensions obligatoires de filtre (Région, Année de reporting).

    Args:
        df (pd.DataFrame): DataFrame d'entrée.

    Returns:
        pd.DataFrame: DataFrame épuré des lignes sans coordonnées de base.
    """
    # `how="any"` (défaut) : on supprime dès qu'au moins une des deux colonnes
    # critiques est manquante. Les NaN restants (postes d'émissions) sont
    # conservés — ils représentent une non-déclaration, pas un zéro réel.
    return df.dropna(subset=["Région", "Année de reporting"])


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtre les colonnes, applique le renommage, nettoie le texte et ajoute les agrégations de scopes.

    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes brutes.

    Returns:
        pd.DataFrame: DataFrame propre et structuré.
    """
    # Combinaison des colonnes d'identification et d'émissions à conserver
    columns_to_keep = list(COLUMN_MAPPING) + list(EMISSION_MAPPING)
    columns_present = [c for c in columns_to_keep if c in df.columns]

    # Renommage en snake_case
    cleaned = df[columns_present].rename(
        columns={**COLUMN_MAPPING, **EMISSION_MAPPING}
    ).copy()

    # Application des fonctions utilitaires de nettoyage
    cleaned = _strip_pua_characters(cleaned)
    cleaned = _normalize_region_names(cleaned)
    cleaned = _cast_types(cleaned)
    cleaned = _add_scope_totals(cleaned)

    return cleaned


def save_cleaned_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame nettoyé dans la table `cleaned` de la base
    SQLite `data/db.sqlite`. Remplace la table existante pour rester
    idempotent (ré-exécuter clean_data écrase la table).

    Args:
        df (pd.DataFrame): DataFrame final prêt pour l'application.
    """
    # Création du répertoire parent au cas où (sécurité, normalement
    # déjà créé par get_data.save_raw_data).
    os.makedirs(os.path.dirname(config.DATABASE), exist_ok=True)

    # Écriture dans la même base que les données brutes, mais dans une
    # table distincte `cleaned`. if_exists="replace" garantit que la
    # table reflète toujours le dernier nettoyage.
    with sqlite3.connect(config.DATABASE) as conn:
        df.to_sql(
            config.TABLE_CLEAN,
            con=conn,
            if_exists="replace",
            index=False,
        )


def main() -> None:
    """
    Orchestrateur principal du script de nettoyage.
    Lit la table `raw`, applique le pipeline en 4 étapes, écrit `cleaned`.
    """
    df = load_raw_data()
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = normalize_columns(df)

    save_cleaned_data(df)

    print(f"Données nettoyées : {len(df):,} lignes × {df.shape[1]} colonnes")
    print(f"Sauvegardé dans : {config.DATABASE} (table {config.TABLE_CLEAN})")


def _strip_pua_characters(df: pd.DataFrame) -> pd.DataFrame:
    """Retire les caractères de la Private Use Area des colonnes textuelles."""
    pua_chars = {chr(c) for c in PUA_RANGE}

    def clean(value: object) -> object:
        if isinstance(value, str):
            return "".join(c for c in value if c not in pua_chars).strip()
        return value

    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].map(clean)
    return df


def _normalize_region_names(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les lignes hors périmètre et corrige l'écriture des régions."""
    df = df[~df["region"].isin(REGIONS_TO_EXCLUDE)].copy()
    df["region"] = df["region"].replace(REGION_NAME_FIXES)
    return df


def _cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit les types de données vers les formats pandas appropriés (type entier nullable)."""
    nullable_int_cols = ["annee_reporting", "annee_reference", "population"]
    for col in nullable_int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def _add_scope_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les totaux cumulés pour les Scopes 1, 2, et 3 ainsi que les émissions totales."""
    # Identification des colonnes pour chaque scope
    scope_1_cols = [c for c in df.columns if c.startswith("emissions_p1_")]
    scope_2_cols = [c for c in df.columns if c.startswith("emissions_p2_")]
    scope_3_cols = [
        c for c in df.columns
        if c.startswith(("emissions_p3_", "emissions_p4_", "emissions_p5_", "emissions_p6_"))
    ]

    # Somme par ligne pour chaque scope en ignorant les valeurs manquantes (NaN)
    df["total_scope_1"] = df[scope_1_cols].sum(axis=1, skipna=True)
    df["total_scope_2"] = df[scope_2_cols].sum(axis=1, skipna=True)
    df["total_scope_3"] = df[scope_3_cols].sum(axis=1, skipna=True)

    # Calcul du total général
    df["total_emissions"] = (
        df["total_scope_1"] + df["total_scope_2"] + df["total_scope_3"]
    )
    return df


if __name__ == "__main__":
    main()
