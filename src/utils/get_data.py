"""
Module de téléchargement et de stockage des données brutes ADEME.
Récupère le fichier Excel source depuis l'URL configurée et le stocke
dans la table `raw` de la base SQLite `data/db.sqlite` (stockage local
imposé par le cahier des charges pour permettre l'exécution hors ligne).
"""

import os
import sqlite3

import pandas as pd

import config


def download_data() -> pd.DataFrame:
    """
    Télécharge les données brutes depuis l'URL distante configurée.
    En cas d'échec (absence de connexion internet), tente de charger
    le fichier Excel local s'il est présent.

    Returns:
        pd.DataFrame: Les données lues depuis la feuille Excel spécifiée.
    """
    local_path = os.path.join(os.path.dirname(config.DATABASE), "raw", "bilan-ges.xlsx")
    try:
        # pandas sait lire directement des fichiers depuis une URL HTTP/HTTPS.
        return pd.read_excel(config.DATA_URL, sheet_name=config.DATA_SHEET)
    except Exception as e:
        if os.path.exists(local_path):
            print(f"Échec du téléchargement, chargement de la copie locale : {local_path}")
            return pd.read_excel(local_path, sheet_name=config.DATA_SHEET)
        raise e


def save_raw_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame brut dans la table `raw` de la base SQLite.
    Remplace la table existante pour rester idempotent : ré-exécuter
    get_data écrase la table avec les données les plus récentes.

    Args:
        df (pd.DataFrame): Les données à sauvegarder.
    """
    # Création du dossier data/ si nécessaire (sinon sqlite3.connect
    # plante quand le répertoire parent du fichier .sqlite n'existe pas).
    os.makedirs(os.path.dirname(config.DATABASE), exist_ok=True)

    # Connexion SQLite via `with` : commit implicite + fermeture propre.
    # if_exists="replace" garantit que la table reflète toujours le dernier
    # téléchargement (pas d'accumulation par concaténation).
    with sqlite3.connect(config.DATABASE) as conn:
        df.to_sql(
            config.TABLE_RAW,
            con=conn,
            if_exists="replace",
            index=False,
        )


def main() -> None:
    """
    Fonction principale du script de téléchargement.
    Télécharge le fichier si la table `raw` n'est pas déjà présente en base.
    """
    # Comportement idempotent : on ne re-télécharge pas si la table existe
    # déjà (le dashboard doit pouvoir fonctionner hors ligne après une
    # première exécution réussie).
    if os.path.exists(config.DATABASE) and _table_exists(config.TABLE_RAW):
        print(f"Données déjà présentes : {config.DATABASE} (table {config.TABLE_RAW})")
        return

    print(f"Téléchargement depuis : {config.DATA_URL}")
    df = download_data()
    save_raw_data(df)

    print(
        f"Téléchargement terminé : {config.DATABASE} "
        f"({len(df):,} lignes dans la table {config.TABLE_RAW})"
    )


def _table_exists(table_name: str) -> bool:
    """Indique si une table SQL portant ce nom existe dans la base."""
    # Lecture du catalogue système sqlite_master (plus sûr qu'un SELECT
    # qui lèverait une OperationalError si la table manquait).
    with sqlite3.connect(config.DATABASE) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None


if __name__ == "__main__":
    main()
