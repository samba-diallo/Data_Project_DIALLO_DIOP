"""
Composant d'en-tête éditorial pour les pages du dashboard.
Affiche une catégorie (kicker), un titre principal et un descriptif sous-titré.
S'inspire de la mise en page des articles de presse.
"""

from dash import html


def create_header(
    title: str,
    subtitle: str = "",
    kicker: str = "",
) -> html.Header:
    """
    Construit un en-tête graphique pour structurer une page du tableau de bord.

    Args:
        title (str): Titre principal de la page.
        subtitle (str): Texte d'explication ou sous-titre de la page (optionnel).
        kicker (str): Petit label textuel placé au-dessus du titre principal (optionnel).

    Returns:
        html.Header: Le composant d'en-tête HTML5 prêt à être inséré dans le layout.
    """
    # Création d'une liste vide pour stocker les composants HTML à la suite
    children: list = []

    # Si un label de sur-titre (kicker) est fourni, on l'ajoute en premier
    if kicker:
        children.append(html.Div(kicker, className="kicker"))

    # Ajout du titre principal de la page sous la forme d'une balise H1
    # Important : il ne doit y avoir qu'un seul H1 par page pour un bon référencement SEO
    children.append(html.H1(title))

    # Si un sous-titre explicatif est fourni, on l'ajoute en dernier sous forme de paragraphe
    if subtitle:
        children.append(html.P(subtitle, className="subtitle"))

    # Renvoi du composant global structuré sous la balise sémantique <header>
    return html.Header(
        className="page-header",
        children=children,
    )
