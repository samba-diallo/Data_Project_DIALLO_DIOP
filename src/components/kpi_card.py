"""
Composant KPI card - carte d'indicateur clé.
Réutilisable sur toutes les pages pour afficher une métrique
chiffrée avec son label et un éventuel sous-label de contexte.

Utilisé en Phase 3 sur la page d'accueil (4 KPIs principaux)
et potentiellement sur d'autres pages.
"""

from dash import html

# DashIconify : icône SVG optionnelle à gauche du KPI (Tabler icons)
from dash_iconify import DashIconify


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Composant
# ─────────────────────────────────────────────────────────────────

def create_kpi_card(
    label: str,
    value: str,
    sublabel: str = "",
    icon: str = "",
) -> html.Div:
    """
    Construit une carte KPI affichant un grand chiffre, son label
    descriptif et un sous-label optionnel pour le contexte.

    Args:
        label (str): Titre court du KPI (ex: "Bilans publiés").
        value (str): Valeur formatée à afficher en grand
                     (ex: "9 991", "7,8 Gt CO₂eq").
        sublabel (str): Précision sous le chiffre (ex: "Déclarations BEGES").
        icon (str): Identifiant Iconify optionnel (ex: "tabler:file-text")
                    affiché en haut à gauche de la carte.

    Returns:
        html.Div: Composant Dash html.Div prêt à être intégré dans une row.
    """
    # On construit progressivement la liste des enfants pour pouvoir
    # ajouter conditionnellement l'icône et le sous-label.
    children: list = []

    # Ligne du haut : icône (optionnelle) + label descriptif.
    # On regroupe icône et label dans un même flex pour qu'ils restent
    # alignés horizontalement, indépendamment de la présence de l'icône.
    header_children: list = []
    if icon:
        header_children.append(
            DashIconify(
                icon=icon,
                width=18,
                # Couleur en accent or pâle pour rappeler le kicker
                # éditorial des headers de page (cohérence visuelle).
                color="#C9A961",
            )
        )
    header_children.append(html.Span(label, className="kpi-label"))

    children.append(
        html.Div(header_children, className="kpi-header")
    )

    # Le chiffre principal : classe "tabular-nums" appliquée pour utiliser
    # JetBrains Mono avec alignement décimal propre (defini dans style.css).
    children.append(
        html.Div(value, className="kpi-value tabular-nums")
    )

    # Sous-label optionnel : précision contextuelle (unité, période...)
    if sublabel:
        children.append(html.Div(sublabel, className="kpi-sublabel"))

    # html.Div principal portant la classe "kpi-card" stylée dans style.css
    return html.Div(children, className="kpi-card")
