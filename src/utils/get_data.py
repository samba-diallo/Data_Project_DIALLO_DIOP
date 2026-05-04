"""
Module de récupération des données brutes.
Télécharge le fichier Excel ADEME depuis l'URL définie dans config.py
et le sauvegarde dans data/raw/.

Doc pandas : https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
"""

# os : pour gérer les chemins de fichiers et créer les répertoires
import os

# pandas : pour lire et écrire les fichiers Excel sous forme de DataFrame
import pandas as pd

# config : contient les chemins (DATA_RAW), l'URL ADEME (DATA_URL) et le nom
# de la feuille Excel à lire (DATA_SHEET) - centralise la configuration
import config


# ─────────────────────────────────────────────────────────────────
# BACKEND – Données
# ─────────────────────────────────────────────────────────────────

def download_data() -> pd.DataFrame:
    """
    Télécharge les données brutes depuis l'URL définie dans config.DATA_URL.
    Lit la feuille config.DATA_SHEET du fichier Excel ADEME.

    Returns:
        pd.DataFrame: DataFrame contenant les données brutes telles que
                      récupérées depuis la source (aucune modification).

    Raises:
        ConnectionError: Si la source ADEME est inaccessible.
        ValueError: Si le format du fichier n'est pas supporté.
    """
    # pd.read_excel sait lire directement depuis une URL HTTP/HTTPS.
    # On précise sheet_name pour ne charger que la feuille "données" et
    # ignorer les feuilles "jeu de données" et "requête" qui ne contiennent
    # que des métadonnées sans intérêt pour notre dashboard.
    return pd.read_excel(config.DATA_URL, sheet_name=config.DATA_SHEET)


def save_raw_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame brut au format Excel dans data/raw/
    sans aucune modification des données.

    Args:
        df (pd.DataFrame): DataFrame brut à sauvegarder.

    Returns:
        None
    """
    # On s'assure que le répertoire data/raw/ existe avant d'écrire dedans.
    # exist_ok=True évite l'erreur si le répertoire existe déjà.
    os.makedirs(os.path.dirname(config.DATA_RAW), exist_ok=True)

    # index=False pour ne pas écrire les indices pandas (0, 1, 2...) en
    # première colonne, ce qui polluerait le fichier Excel.
    # sheet_name garde le même nom de feuille que la source ADEME.
    df.to_excel(config.DATA_RAW, index=False, sheet_name=config.DATA_SHEET)


def main() -> None:
    """
    Point d'entrée principal du module get_data.
    Télécharge les données ADEME si elles ne sont pas déjà présentes localement,
    pour permettre l'exécution du dashboard hors ligne.

    Usage:
        $ python -m src.utils.get_data

    Returns:
        None
    """
    # Comportement idempotent : on ne re-télécharge pas si le fichier est
    # déjà présent. Cela évite des appels réseau inutiles et permet au
    # dashboard de fonctionner sans connexion (exigence du cahier des charges).
    if os.path.exists(config.DATA_RAW):
        print(f"Données déjà présentes : {config.DATA_RAW}")
        return

    # Téléchargement effectif : appel à l'API ADEME puis écriture sur disque.
    print(f"Téléchargement depuis : {config.DATA_URL}")
    df = download_data()
    save_raw_data(df)

    # On affiche un résumé pour confirmer la réussite et donner du contexte
    # (le formatage {:,} ajoute des séparateurs de milliers).
    print(f"Téléchargement terminé : {config.DATA_RAW} ({len(df):,} lignes)")


# Bloc exécuté seulement si le fichier est lancé directement via
# "python -m src.utils.get_data". Si un autre module l'importe, ce bloc
# n'est pas déclenché.
if __name__ == "__main__":
    main()
