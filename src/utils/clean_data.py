"""
Module de nettoyage des données.
Charge les données brutes ADEME, les nettoie et les sauvegarde
dans data/cleaned/ pour consommation par le dashboard.

Le fichier brut contient 104 colonnes ; on n'en conserve que 14 essentielles
plus les 22 postes d'émissions (P1.1 à P6.1) et 4 totaux calculés.
"""

# os : pour vérifier l'existence du fichier brut et créer les répertoires
import os

# pandas : pour toute la manipulation tabulaire (DataFrame, dropna, groupby...)
import pandas as pd

# config : centralise les chemins et la feuille Excel à charger
import config


# ─────────────────────────────────────────────────────────────────
# CONSTANTES – Schéma de nettoyage
# ─────────────────────────────────────────────────────────────────

# Dictionnaire de renommage : à chaque colonne brute (clé), on associe son
# nom snake_case (valeur). Le snake_case est la convention Python, plus
# pratique que les espaces et caractères accentués pour la suite du code.
# On ne garde ici que les 14 colonnes descriptives essentielles parmi les 104.
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

# Liste des 22 postes d'émissions du référentiel BEGES (Bilan Carbone réglementaire) :
#   - Scope 1 (émissions directes)         : P1.1 à P1.5  -> 5 postes
#   - Scope 2 (énergie achetée)            : P2.1 à P2.2  -> 2 postes
#   - Scope 3 (chaîne de valeur amont/aval): P3.1 à P3.5,
#                                            P4.1 à P4.5,
#                                            P5.1 à P5.4,
#                                            P6.1          -> 15 postes
# Chaque tuple (s, i) représente le poste P{s}.{i}.
EMISSION_POSTS: list[tuple[int, int]] = [
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    (2, 1), (2, 2),
    (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
    (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
    (5, 1), (5, 2), (5, 3), (5, 4),
    (6, 1),
]

# Construction automatique du dict de renommage des colonnes émissions à
# partir de EMISSION_POSTS. Ex: "Emissions publication P1.1" -> "emissions_p1_1".
# Cela évite d'écrire 22 lignes répétitives à la main.
EMISSION_MAPPING: dict[str, str] = {
    f"Emissions publication P{s}.{i}": f"emissions_p{s}_{i}"
    for s, i in EMISSION_POSTS
}

# Plage Unicode "Private Use Area" (PUA). Les déclarants ADEME copient parfois
# du texte depuis Word/PDF avec des polices Wingdings/Symbol. Ces caractères
# atterrissent dans le CSV sous forme de codes U+E000 à U+F8FF qui s'affichent
# comme des carrés vides dans VS Code et brouillent la lecture.
PUA_RANGE = range(0xE000, 0xF8FF + 1)


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données
# ─────────────────────────────────────────────────────────────────

def load_raw_data() -> pd.DataFrame:
    """
    Charge le fichier Excel brut depuis data/raw/.

    Returns:
        pd.DataFrame: DataFrame brut avec les 104 colonnes ADEME.

    Raises:
        FileNotFoundError: Si le fichier xlsx est absent (lancer get_data.py).
    """
    # Vérification explicite avant pd.read_excel pour produire un message
    # d'erreur plus parlant que le FileNotFoundError natif de pandas
    # (et indiquer la commande de réparation).
    if not os.path.exists(config.DATA_RAW):
        raise FileNotFoundError(
            f"Fichier brut introuvable : {config.DATA_RAW}\n"
            "Lancer 'python -m src.utils.get_data' pour le télécharger."
        )

    # Lecture de la feuille "données" uniquement (les autres feuilles du
    # fichier ADEME contiennent juste des métadonnées).
    return pd.read_excel(config.DATA_RAW, sheet_name=config.DATA_SHEET)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les bilans dupliqués en se basant sur la colonne Id.
    Chaque bilan ADEME possède un identifiant unique.

    Args:
        df (pd.DataFrame): DataFrame brut pouvant contenir des doublons.

    Returns:
        pd.DataFrame: DataFrame sans doublons d'identifiants.
    """
    # subset="Id" : la dé-duplication ne se fait QUE sur l'identifiant unique
    # ADEME, pas sur toute la ligne. Cela permet de garder distinctes deux
    # déclarations identiques mais avec des Id différents.
    # keep="first" : si doublons d'Id, on garde la première occurrence.
    return df.drop_duplicates(subset="Id", keep="first")


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les lignes dont les colonnes critiques sont manquantes
    (Région, Année de reporting). Les valeurs manquantes des postes
    d'émissions sont conservées en NaN pour distinguer "non déclaré"
    de "0 émission".

    Args:
        df (pd.DataFrame): DataFrame pouvant contenir des NaN.

    Returns:
        pd.DataFrame: DataFrame sans NaN sur les colonnes essentielles.
    """
    # On supprime UNIQUEMENT les lignes où Région ou Année sont vides :
    # sans ces deux infos, la ligne est inutilisable pour le dashboard
    # (pas de placement sur la carte, pas de filtrage temporel).
    # On NE supprime PAS les lignes où des postes d'émissions sont vides :
    # un NaN signifie "non déclaré", pas zéro - et beaucoup d'organisations
    # ne déclarent qu'une partie des postes.
    return df.dropna(subset=["Région", "Année de reporting"])


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sélectionne les colonnes utiles, les renomme en snake_case, caste les
    types et calcule les totaux par scope (Scope 1, 2, 3, total).
    Strippe également les caractères Unicode "Private Use Area" qui
    polluent certains champs texte du fichier ADEME.

    Args:
        df (pd.DataFrame): DataFrame avec colonnes brutes ADEME.

    Returns:
        pd.DataFrame: DataFrame normalisé avec ~40 colonnes typées.
    """
    # Concaténation des deux dicts de mapping pour obtenir la liste complète
    # des colonnes brutes à conserver (descriptives + émissions = 36 colonnes).
    columns_to_keep = list(COLUMN_MAPPING) + list(EMISSION_MAPPING)

    # Filtre défensif : on ne garde que les colonnes qui existent réellement
    # dans le DataFrame source. Si l'ADEME modifie son schéma à l'avenir,
    # le code ne plantera pas - les colonnes manquantes seront simplement
    # ignorées et les éventuelles colonnes supplémentaires seront rejetées.
    columns_present = [c for c in columns_to_keep if c in df.columns]

    # Application du renommage : ** déballe les deux dicts en un seul
    # dictionnaire qu'on passe à rename().
    # .copy() pour éviter le SettingWithCopyWarning lors des modifications
    # qui suivent (pandas est strict sur les vues vs copies).
    cleaned = df[columns_present].rename(
        columns={**COLUMN_MAPPING, **EMISSION_MAPPING}
    ).copy()

    # Trois étapes de nettoyage chaînées, chacune dans une fonction privée
    # pour clarifier l'intention et faciliter les tests.
    cleaned = _strip_pua_characters(cleaned)
    cleaned = _cast_types(cleaned)
    cleaned = _add_scope_totals(cleaned)

    return cleaned


def save_cleaned_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame nettoyé au format CSV dans data/cleaned/
    avec encodage UTF-8.

    Args:
        df (pd.DataFrame): DataFrame nettoyé prêt pour le dashboard.

    Returns:
        None
    """
    # Création du répertoire data/cleaned/ s'il n'existe pas encore.
    os.makedirs(os.path.dirname(config.DATA_CLEAN), exist_ok=True)

    # Format CSV en sortie (et non Excel) car :
    #  - plus rapide à charger pour Dash (lecture multiple par les composants)
    #  - plus léger sur disque
    #  - plus universel (pas besoin d'openpyxl côté lecture)
    # encoding="utf-8" pour préserver les accents français des colonnes texte.
    df.to_csv(config.DATA_CLEAN, index=False, encoding="utf-8")


def main() -> None:
    """
    Point d'entrée principal du module clean_data.
    Orchestre le chargement, nettoyage et sauvegarde des données.

    Usage:
        $ python -m src.utils.clean_data

    Returns:
        None
    """
    # Pipeline en 4 étapes, dans l'ordre logique :
    #   1) charger le brut, 2) dédupliquer, 3) virer les NaN critiques,
    #   4) sélectionner/normaliser les colonnes et calculer les totaux.
    # Chaque étape produit un nouveau DataFrame que l'on passe à la suivante.
    df = load_raw_data()
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = normalize_columns(df)

    # Persistance sur disque pour que le dashboard puisse y accéder.
    save_cleaned_data(df)

    # Feedback console pour l'utilisateur (utile en debug et en démo).
    print(f"Données nettoyées : {len(df):,} lignes × {df.shape[1]} colonnes")
    print(f"Sauvegardé dans : {config.DATA_CLEAN}")


# ─────────────────────────────────────────────────────────────────
# Helpers privés (préfixe _ par convention Python pour signaler
# qu'ils ne sont pas destinés à être importés depuis l'extérieur)
# ─────────────────────────────────────────────────────────────────

def _strip_pua_characters(df: pd.DataFrame) -> pd.DataFrame:
    """Retire les caractères Unicode Private Use Area des colonnes texte."""
    # On précompute l'ensemble des caractères PUA une seule fois (set pour
    # un test d'appartenance en O(1)) plutôt qu'à chaque appel de clean().
    pua_chars = {chr(c) for c in PUA_RANGE}

    # Fonction interne qui sera appliquée à chaque cellule texte.
    # On utilise une compréhension de chaîne pour filtrer caractère par
    # caractère, puis .strip() pour enlever les espaces résiduels en bord.
    # Les valeurs non-string (NaN, nombres) sont retournées telles quelles.
    def clean(value: object) -> object:
        if isinstance(value, str):
            return "".join(c for c in value if c not in pua_chars).strip()
        return value

    # select_dtypes(include="object") cible les colonnes texte uniquement
    # (en pandas, les chaînes de caractères ont le dtype "object").
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        # .map(clean) applique la fonction à chaque cellule de la colonne.
        df[col] = df[col].map(clean)
    return df


def _cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """Caste les colonnes vers des types pandas adaptés (Int64 nullable pour
    les entiers pouvant contenir des NaN)."""
    # Les colonnes "année" et "population" sont conceptuellement des entiers
    # mais peuvent contenir des NaN (ex: année de référence souvent absente).
    # Le type "Int64" (avec I majuscule) est le type entier *nullable* de
    # pandas - il accepte NaN, contrairement à "int64" classique.
    nullable_int_cols = ["annee_reporting", "annee_reference", "population"]
    for col in nullable_int_cols:
        if col in df.columns:
            # pd.to_numeric(..., errors="coerce") convertit en numérique et
            # transforme les valeurs invalides en NaN au lieu de planter.
            # .astype("Int64") finalise le cast vers l'entier nullable.
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def _add_scope_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les totaux par scope BEGES à partir des 22 postes d'émissions."""
    # Repérage des colonnes par préfixe : on isole les postes Scope 1, 2 et 3
    # via la convention de nommage "emissions_p{s}_{i}".
    scope_1_cols = [c for c in df.columns if c.startswith("emissions_p1_")]
    scope_2_cols = [c for c in df.columns if c.startswith("emissions_p2_")]

    # Le Scope 3 regroupe les groupes P3, P4, P5 et P6 selon le référentiel
    # BEGES officiel (postes "indirects" liés à la chaîne de valeur).
    scope_3_cols = [
        c for c in df.columns
        if c.startswith(("emissions_p3_", "emissions_p4_",
                         "emissions_p5_", "emissions_p6_"))
    ]

    # axis=1 : somme HORIZONTALE (par ligne, donc par bilan).
    # skipna=True : les NaN sont ignorés dans la somme. Si toutes les
    # colonnes d'un scope sont NaN, le total vaut 0 (pas NaN). C'est un
    # choix discutable mais pratique pour les agrégations downstream.
    df["total_scope_1"] = df[scope_1_cols].sum(axis=1, skipna=True)
    df["total_scope_2"] = df[scope_2_cols].sum(axis=1, skipna=True)
    df["total_scope_3"] = df[scope_3_cols].sum(axis=1, skipna=True)

    # Le total global est la somme des trois scopes.
    df["total_emissions"] = (
        df["total_scope_1"] + df["total_scope_2"] + df["total_scope_3"]
    )
    return df


# Permet d'exécuter le module en standalone via "python -m src.utils.clean_data".
if __name__ == "__main__":
    main()
