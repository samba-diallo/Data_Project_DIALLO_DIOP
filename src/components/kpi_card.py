"""
Composant réutilisable de carte KPI (Indicateur Clé de Performance).
Permet d'afficher de façon valorisée un grand nombre ou une métrique clé de données.
"""

from dash import html
from dash_iconify import DashIconify


def create_kpi_card(
    label: str,
    value: str,
    sublabel: str = "",
    icon: str = "",
) -> html.Div:
    """
    Construit une carte d'affichage d'un indicateur clé.

    Args:
        label (str): Titre ou description de la métrique (ex: "Bilans cumulés").
        value (str): Chiffre clé formaté sous forme de chaîne de caractères.
        sublabel (str): Texte d'accompagnement plus petit en bas de la carte (optionnel).
        icon (str): Identifiant de l'icône à afficher en en-tête (optionnel).

    Returns:
        html.Div: Composant conteneur HTML représentant la carte KPI.
    """
    # Liste qui contiendra la structure interne de la carte
    children: list = []

    # En-tête de la carte : contient le titre et éventuellement l'icône associée
    header_children: list = []
    if icon:
        header_children.append(
            DashIconify(
                icon=icon,
                width=18,
                color="#C9A961", # Couleur dorée pour mettre en valeur l'icône
            )
        )
    header_children.append(html.Span(label, className="kpi-label"))

    # Ajout du bloc en-tête dans la liste des enfants
    children.append(
        html.Div(header_children, className="kpi-header")
    )

    # Ajout de la valeur numérique affichée en grand format
    children.append(
        html.Div(value, className="kpi-value tabular-nums")
    )

    # Si un texte de contexte (sublabel) est présent, on l'ajoute en bas
    if sublabel:
        children.append(html.Div(sublabel, className="kpi-sublabel"))

    # Renvoi du conteneur final stylisé en tant que kpi-card
    return html.Div(children, className="kpi-card")
