"""
Composant en-tete editorial des pages du dashboard.
Affiche un kicker (label en majuscules), un titre serif et un sous-titre.
Inspire des couvertures de revues (Le Monde Diplo, Bloomberg Green).

Doc Dash HTML : https://dash.plotly.com/dash-html-components
"""

from dash import html


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

def create_header(
    title: str,
    subtitle: str = "",
    kicker: str = "",
) -> html.Div:
    """
    Construit un en-tete editorial pour une page du dashboard.

    Args:
        title (str): Titre principal de la page (en serif Fraunces).
        subtitle (str): Phrase d'accroche sous le titre (optionnel).
        kicker (str): Petit label en majuscules au-dessus du titre,
                      facon presse (optionnel). Ex: "Vue d'ensemble".

    Returns:
        html.Div: Composant Dash html.Div pret a etre integre dans un layout.
    """
    # On construit progressivement la liste d'enfants : kicker affiche
    # uniquement s'il est fourni, idem pour le sous-titre. Cela evite des
    # divs vides qui produiraient des espaces blancs inutiles.
    children: list = []

    # Kicker optionnel : petit texte en majuscules au-dessus du titre.
    # Sert a indiquer la "rubrique" (Vue d'ensemble, Explorer, etc.).
    if kicker:
        children.append(html.Div(kicker, className="kicker"))

    # Titre principal en h1 : un seul h1 par page pour le SEO et l'accessibilite.
    children.append(html.H1(title))

    # Sous-titre optionnel : explication courte du contenu de la page.
    if subtitle:
        children.append(html.P(subtitle, className="subtitle"))

    # html.Header : balise semantique HTML5 pour les en-tetes (mieux que div
    # pour les lecteurs d'ecran).
    return html.Header(
        className="page-header",
        children=children,
    )
