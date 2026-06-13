"""
Module de téléchargement et de stockage des données brutes de l'ADEME.
Permet de récupérer le fichier Excel source depuis l'url configurée dans config.py
et de le sauvegarder localement pour le traitement ultérieur.
"""

import os
import pandas as pd
import config


def download_data() -> pd.DataFrame:
    """
    Télécharge les données brutes depuis l'URL distante configurée.

    Returns:
        pd.DataFrame: Les données lues depuis la feuille Excel spécifiée.
    """
    # pandas sait lire directement des fichiers depuis une URL HTTP/HTTPS
    return pd.read_excel(config.DATA_URL, sheet_name=config.DATA_SHEET)


def save_raw_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le DataFrame brut localement au format Excel.

    Args:
        df (pd.DataFrame): Les données à sauvegarder.
    """
    # Création du dossier de stockage des données brutes si nécessaire
    os.makedirs(os.path.dirname(config.DATA_RAW), exist_ok=True)
    
    # Écriture du fichier Excel
    df.to_excel(config.DATA_RAW, index=False, sheet_name=config.DATA_SHEET)


def main() -> None:
    """
    Fonction principale du script de téléchargement.
    Télécharge le fichier si celui-ci n'est pas déjà présent localement.
    """
    # Si le fichier existe déjà localement, on évite un nouveau téléchargement inutile
    if os.path.exists(config.DATA_RAW):
        print(f"Données déjà présentes : {config.DATA_RAW}")
        return

    print(f"Téléchargement depuis : {config.DATA_URL}")
    df = download_data()
    save_raw_data(df)

    print(f"Téléchargement terminé : {config.DATA_RAW} ({len(df):,} lignes)")


if __name__ == "__main__":
    main()
