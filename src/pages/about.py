"""
Page 'Méthodologie' du dashboard.
Documente le référentiel BEGES (Scope 1/2/3 et postes P1.x à P6.x), le
pipeline de traitement des données ADEME (get_data -> clean_data -> dashboard)
et la déclaration d'originalité du code (copyright exigé par le cahier
des charges du projet — D. Courivaud, ESIEE).

Page purement documentaire : pas de callback, pas de filtre, pas de
chargement de données dynamique. Tout le contenu est statique et reflète
la logique réelle du code (cf. src/utils/clean_data.py).

Doc Dash layout : https://dash.plotly.com/layout
"""

# Permet la syntaxe PEP 604 (list | None) sur Python 3.9 si jamais on en
# ajoute plus tard. Pas indispensable aujourd'hui mais cohérent avec les
# autres modules du projet.
from __future__ import annotations

from dash import html

# DashIconify : icônes SVG (Tabler / Lucide) pour décorer les sections
# sans utiliser d'emoji (cf. checklist UI/UX du projet).
from dash_iconify import DashIconify

# Header éditorial commun à toutes les pages (kicker + h1 serif + sous-titre).
from src.components.header import create_header

# Couleurs des scopes BEGES : on les réutilise ici pour que les cartes de
# glossaire aient la même sémantique colorée que les graphes (donut scope,
# tooltip de la carte, etc.).
from src.components.charts_theme import SCOPE_COLORS


# ─────────────────────────────────────────────────────────────────
# DONNÉES DOCUMENTAIRES (statiques)
# ─────────────────────────────────────────────────────────────────

# Glossaire des 3 scopes BEGES. La source officielle est le référentiel
# ADEME "Méthode pour la réalisation des bilans d'émissions de gaz à effet
# de serre" (article L. 229-25 du code de l'environnement). Les libellés
# repris ici suivent la version V5 utilisée par notre dataset (colonne
# `methode_beges` dans cleaneddata.csv).
SCOPES_BEGES: list[dict] = [
    {
        "id": "scope_1",
        "label": "Scope 1",
        "title": "Émissions directes",
        "color": SCOPE_COLORS["scope_1"],
        "icon": "tabler:flame",
        "summary": (
            "Émissions issues de sources fixes ou mobiles détenues ou "
            "contrôlées par l'organisation (combustion d'énergies fossiles, "
            "fuites de fluides frigorigènes, biomasse, procédés industriels)."
        ),
        "posts": [
            ("P1.1", "Sources fixes de combustion (chaudières, fours…)"),
            ("P1.2", "Sources mobiles à moteur thermique (flotte de véhicules)"),
            ("P1.3", "Procédés hors énergie (chimie, ciment, agriculture)"),
            ("P1.4", "Émissions directes fugitives (fluides frigorigènes, SF6)"),
            ("P1.5", "Émissions issues de la biomasse (sols, forêts)"),
        ],
    },
    {
        "id": "scope_2",
        "label": "Scope 2",
        "title": "Énergie achetée",
        "color": SCOPE_COLORS["scope_2"],
        "icon": "tabler:bolt",
        "summary": (
            "Émissions indirectes liées à la consommation d'énergie acquise "
            "et consommée par l'organisation (électricité, chaleur, vapeur, "
            "froid). Calcul par localisation du mix énergétique."
        ),
        "posts": [
            ("P2.1", "Consommation d'électricité"),
            ("P2.2", "Consommation de vapeur, chaleur ou froid en réseau"),
        ],
    },
    {
        "id": "scope_3",
        "label": "Scope 3",
        "title": "Chaîne de valeur (amont & aval)",
        "color": SCOPE_COLORS["scope_3"],
        "icon": "tabler:network",
        "summary": (
            "Autres émissions indirectes : produits achetés, transport et "
            "logistique, déplacements professionnels et domicile-travail, "
            "usage et fin de vie des produits vendus, immobilisations. "
            "Regroupe les groupes P3, P4, P5 et P6 du référentiel."
        ),
        "posts": [
            ("P3.1", "Achats de biens et services"),
            ("P3.2", "Immobilisations de biens"),
            ("P3.3", "Déchets générés par l'activité"),
            ("P3.4", "Transport de marchandises amont"),
            ("P3.5", "Déplacements professionnels"),
            ("P4.1", "Transport de marchandises aval"),
            ("P4.2", "Utilisation des produits vendus"),
            ("P4.3", "Fin de vie des produits vendus"),
            ("P4.4", "Franchise aval"),
            ("P4.5", "Leasing aval"),
            ("P5.1", "Déplacements domicile-travail"),
            ("P5.2", "Déplacements des visiteurs et clients"),
            ("P5.3", "Investissements"),
            ("P5.4", "Actifs en leasing amont"),
            ("P6.1", "Autres émissions indirectes (catégorie ouverte)"),
        ],
    },
]


# Étapes du pipeline de traitement des données. Cet ordre reflète
# fidèlement le contenu de src/utils/get_data.py et src/utils/clean_data.py
# (cf. la fonction `main()` qui orchestre les 4 étapes).
PIPELINE_STEPS: list[dict] = [
    {
        "n": "01",
        "icon": "tabler:cloud-download",
        "title": "Téléchargement",
        "module": "src/utils/get_data.py",
        "desc": (
            "Récupération du fichier Excel ADEME via l'API publique "
            "data.ademe.fr (feuille « données »). Idempotent : on ne "
            "re-télécharge pas si data/raw/bilan-ges.xlsx existe déjà."
        ),
    },
    {
        "n": "02",
        "icon": "tabler:filter",
        "title": "Sélection des colonnes",
        "module": "clean_data.normalize_columns",
        "desc": (
            "Le fichier brut contient 104 colonnes. On n'en conserve "
            "que 14 descriptives (région, SIREN, type de structure, "
            "méthode BEGES…) plus les 22 postes d'émissions P1.1 à P6.1."
        ),
    },
    {
        "n": "03",
        "icon": "tabler:wash",
        "title": "Nettoyage",
        "module": "clean_data.remove_duplicates · handle_missing_values",
        "desc": (
            "Déduplication par Id ADEME unique, suppression des lignes "
            "sans région ni année de reporting, retrait des caractères "
            "Unicode PUA et harmonisation des libellés de régions avec "
            "le GeoJSON France (ex : « Hauts de France » → « Hauts-de-France »)."
        ),
    },
    {
        "n": "04",
        "icon": "tabler:calculator",
        "title": "Calcul des totaux par scope",
        "module": "clean_data._add_scope_totals",
        "desc": (
            "Sommation horizontale des 22 postes pour obtenir les 4 "
            "agrégats utilisés partout dans le dashboard : "
            "total_scope_1, total_scope_2, total_scope_3 et total_emissions."
        ),
    },
    {
        "n": "05",
        "icon": "tabler:database-export",
        "title": "Persistance & cache",
        "module": "data/cleaned/cleaneddata.csv",
        "desc": (
            "Le DataFrame nettoyé est sérialisé en CSV UTF-8. Le dashboard "
            "le relit à chaque appel de layout via load_cleaned_data(), "
            "qui restreint la fenêtre temporelle à 2010–2025 (cf. YEAR_MIN/MAX)."
        ),
    },
]


# Inventaire des dépendances tierces utilisées dans le projet, avec leur
# rôle exact. C'est le cœur de la « déclaration d'originalité » exigée par
# le cahier des charges : tout code emprunté doit être listé explicitement
# pour ne pas tomber sous la qualification de plagiat.
CODE_DEPENDENCIES: list[tuple[str, str]] = [
    ("Dash 2.x", "Framework du dashboard (routing, callbacks, dcc, html)"),
    ("dash-bootstrap-components", "Grille responsive et thème Bootstrap"),
    ("dash-iconify", "Icônes SVG (Tabler) — alternative aux emoji"),
    ("Plotly Express & Graph Objects", "Histogramme, donut, choroplèthe, scattergeo"),
    ("pandas", "Lecture Excel/CSV, agrégations et filtres"),
    ("openpyxl", "Lecture du format .xlsx fourni par l'API ADEME"),
    ("regions-france.geojson", "Tracés des 13 régions métropolitaines (france-geojson.gregoiredavid.fr, CC-BY)"),
    ("Google Fonts", "Polices Fraunces, DM Sans, JetBrains Mono (SIL Open Font License)"),
]


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Helpers de rendu
# ─────────────────────────────────────────────────────────────────

def _scope_card(scope: dict) -> html.Div:
    """
    Construit une carte de glossaire pour un scope BEGES.
    Affiche la pastille de couleur sémantique du scope, le libellé court,
    le titre, le résumé et la liste de ses postes (code + intitulé).

    Args:
        scope (dict): Entrée du dict SCOPES_BEGES (id, label, title, color,
            summary, posts).

    Returns:
        html.Div: Carte prête à être insérée dans la grille de glossaire.
    """
    # Liste des postes : on rend chaque entrée comme un <li> avec le code
    # en monospace (JetBrains Mono via .tabular-nums) puis l'intitulé.
    post_items = [
        html.Li(
            [
                html.Code(code, className="post-code"),
                html.Span(label, className="post-label"),
            ],
            className="post-item",
        )
        for code, label in scope["posts"]
    ]

    return html.Div(
        className="scope-card",
        # Bordure gauche colorée = signature visuelle du scope, lecture
        # immédiate de la sémantique (vert profond, vert mousse, or pâle).
        style={"borderLeftColor": scope["color"]},
        children=[
            # En-tête de carte : icône + label "Scope X" en majuscules.
            html.Div(
                className="scope-card-header",
                children=[
                    DashIconify(
                        icon=scope["icon"],
                        width=20,
                        color=scope["color"],
                    ),
                    html.Span(scope["label"], className="scope-card-label"),
                ],
            ),
            # Titre principal (« Émissions directes », etc.).
            html.H3(scope["title"], className="scope-card-title"),
            # Définition courte du scope.
            html.P(scope["summary"], className="scope-card-summary"),
            # Liste des postes BEGES couverts par ce scope.
            html.Ul(post_items, className="scope-card-posts"),
        ],
    )


def _pipeline_step(step: dict) -> html.Div:
    """
    Construit une étape du pipeline de traitement des données.
    Numéro éditorial en exergue, icône, titre, référence au module Python
    et description du rôle de l'étape.

    Args:
        step (dict): Entrée de PIPELINE_STEPS.

    Returns:
        html.Div: Carte « étape » du pipeline.
    """
    return html.Div(
        className="pipeline-step",
        children=[
            # Bandeau d'en-tête : numéro éditorial + icône.
            html.Div(
                className="pipeline-step-head",
                children=[
                    html.Span(step["n"], className="pipeline-step-number"),
                    DashIconify(
                        icon=step["icon"],
                        width=22,
                        color="#1F3A2C",
                    ),
                ],
            ),
            html.H3(step["title"], className="pipeline-step-title"),
            # Référence au module Python exact qui implémente cette étape
            # (utile pour le correcteur qui veut vérifier l'implémentation).
            html.Code(step["module"], className="pipeline-step-module"),
            html.P(step["desc"], className="pipeline-step-desc"),
        ],
    )


def _dependency_row(name: str, role: str) -> html.Tr:
    """Construit une ligne de tableau pour une dépendance déclarée."""
    return html.Tr(
        [
            html.Td(html.Code(name, className="dep-name")),
            html.Td(role, className="dep-role"),
        ]
    )


# ─────────────────────────────────────────────────────────────────
# FRONTEND – Page
# ─────────────────────────────────────────────────────────────────

def layout() -> html.Div:
    """
    Construit et retourne le layout de la page « Méthodologie ».
    Sections :
      1. Comment lire ce tableau de bord (guide de navigation).
      2. Glossaire du référentiel BEGES (Scope 1/2/3 + 22 postes).
      3. Pipeline de traitement des données ADEME (5 étapes).
      4. Déclaration d'originalité du code (auteurs + dépendances tierces).

    Returns:
        html.Div: Layout complet de la page méthodologie.
    """
    return html.Div(
        className="page-container",
        children=[
            # Header éditorial : entrée dans la partie documentation /
            # transparence du produit.
            create_header(
                kicker="Méthodologie",
                title="Comment lire ce tableau de bord",
                subtitle=(
                    "Glossaire du référentiel BEGES, pipeline de traitement "
                    "des données ADEME et déclaration d'originalité du code."
                ),
            ),

            # ── Section 1 : guide de lecture des 3 pages ───────────
            # Mini repère pour orienter le correcteur (ou tout nouvel
            # utilisateur) vers les 3 pages réellement accessibles via
            # la navbar (Accueil, Explorer, Méthodologie).
            html.Section(
                className="content-section",
                children=[
                    html.H2("Trois pages, trois lectures", className="section-title"),
                    html.P(
                        "Le dashboard est volontairement segmenté en trois "
                        "vues complémentaires : une synthèse statique, une "
                        "exploration interactive et cette page documentaire.",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="reading-grid",
                        children=[
                            html.Div(
                                className="reading-card",
                                children=[
                                    html.Span("Accueil", className="reading-card-kicker"),
                                    html.H3("Vue d'ensemble", className="reading-card-title"),
                                    html.P(
                                        "4 KPIs nationaux, l'évolution annuelle "
                                        "des déclarations et la répartition par "
                                        "type de structure.",
                                        className="reading-card-desc",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="reading-card",
                                children=[
                                    html.Span("Explorer", className="reading-card-kicker"),
                                    html.H3("Analyse interactive", className="reading-card-title"),
                                    html.P(
                                        "Filtres dynamiques (année, région, type), "
                                        "carte choroplèthe, histogramme, heat "
                                        "timeline et inspecteur d'organisation.",
                                        className="reading-card-desc",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="reading-card",
                                children=[
                                    html.Span("Méthodologie", className="reading-card-kicker"),
                                    html.H3("Cette page", className="reading-card-title"),
                                    html.P(
                                        "Définitions BEGES, pipeline de données "
                                        "et déclaration d'originalité du code.",
                                        className="reading-card-desc",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # ── Section 2 : Glossaire BEGES ───────────────────────
            html.Section(
                className="content-section",
                children=[
                    html.H2("Glossaire du référentiel BEGES", className="section-title"),
                    html.P(
                        "Le Bilan d'Émissions de Gaz à Effet de Serre (BEGES) "
                        "est l'obligation réglementaire issue de l'article "
                        "L. 229-25 du code de l'environnement. Le référentiel "
                        "ADEME découpe les émissions en trois scopes et "
                        "22 postes — c'est cette grille qui structure les "
                        "colonnes du dataset et les agrégats du dashboard.",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="scope-grid",
                        children=[_scope_card(s) for s in SCOPES_BEGES],
                    ),
                ],
            ),

            # ── Section 3 : Pipeline de traitement ────────────────
            html.Section(
                className="content-section",
                children=[
                    html.H2("Pipeline de traitement des données ADEME", className="section-title"),
                    html.P(
                        "De la source publique ADEME jusqu'à l'affichage dans "
                        "le navigateur, les données suivent un flux en cinq "
                        "étapes. Chaque étape est isolée dans une fonction "
                        "Python dédiée et reste rejouable individuellement.",
                        className="section-subtitle",
                    ),
                    html.Div(
                        className="pipeline-grid",
                        children=[_pipeline_step(s) for s in PIPELINE_STEPS],
                    ),
                    # Petit pied de section : pointe vers la source et le
                    # chemin local du fichier (utile au correcteur pour
                    # vérifier la reproductibilité).
                    html.Div(
                        className="pipeline-source",
                        children=[
                            DashIconify(
                                icon="tabler:link",
                                width=16,
                                color="#6B6B6B",
                            ),
                            html.Span(
                                "Source : data.ademe.fr/datasets/bilan-ges — "
                                "fichier local : data/raw/bilan-ges.xlsx "
                                "(feuille « données »).",
                                className="pipeline-source-text",
                            ),
                        ],
                    ),
                ],
            ),

            # ── Section 4 : Déclaration d'originalité ─────────────
            html.Section(
                className="content-section",
                children=[
                    html.H2("Déclaration d'originalité du code", className="section-title"),
                    html.P(
                        "Conformément aux exigences du projet (E4-DSIA "
                        "« Python 2 — manipulation de données », D. Courivaud, "
                        "ESIEE), tout code emprunté doit être déclaré "
                        "explicitement, sous peine d'être qualifié de plagiat.",
                        className="section-subtitle",
                    ),

                    # Tableau des dépendances tierces déclarées.
                    html.H3(
                        "Bibliothèques et ressources empruntées",
                        className="originality-subtitle",
                    ),
                    html.Div(
                        className="chart-card",
                        children=html.Table(
                            className="originality-table",
                            children=[
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("Dépendance"),
                                            html.Th("Rôle dans le projet"),
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    [_dependency_row(n, r) for n, r in CODE_DEPENDENCIES]
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )


def register_callbacks(app) -> None:
    """
    Enregistre les callbacks spécifiques à la page Méthodologie.
    Vide : page purement documentaire, pas d'interactivité prévue.

    Args:
        app: Instance de l'application Dash (dash.Dash).

    Returns:
        None
    """
    # Aucune interaction prévue sur cette page.
    pass
