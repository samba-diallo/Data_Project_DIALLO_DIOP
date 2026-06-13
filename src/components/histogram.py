"""
Composant d'histogramme multi-vues (Top organisations, Paliers d'émissions, Secteurs NAF).
Permet de commuter entre différentes représentations de la distribution des émissions carbone.
"""

import pandas as pd
import plotly.graph_objects as go

# Importation du thème de styles
from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP

# Constantes d'identifiants de vues
VIEW_TOP_ORGS = "top_orgs"
VIEW_BINS = "bins"
VIEW_SECTORS = "sectors"

# Bornes des paliers d'émissions (en tonnes de CO2 équivalent)
EMISSION_BINS = [0, 1_000, 10_000, 100_000, 1_000_000, float("inf")]

# Libellés associés aux paliers
EMISSION_BIN_LABELS = [
    "<1k tCO₂eq",
    "1k–10k",
    "10k–100k",
    "100k–1M",
    ">1M",
]

# Nombre d'éléments affichés dans les graphiques horizontaux (Top N)
TOP_N = 15

# Nombre minimal d'organisations pour considérer un secteur NAF comme représentatif
MIN_ORGS_PER_SECTOR = 3


def create_histogram(df: pd.DataFrame, view: str = VIEW_TOP_ORGS) -> go.Figure:
    """
    Construit l'histogramme ou graphique en barres correspondant à la vue demandée.

    Args:
        df (pd.DataFrame): Données filtrées à analyser.
        view (str): Type de représentation ('top_orgs', 'bins', 'sectors').

    Returns:
        go.Figure: Figure Plotly configurée.
    """
    # Si le DataFrame est vide, on renvoie un graphique vide contenant un message explicatif
    if df.empty:
        return _empty_figure("Aucun bilan ne correspond aux filtres.")

    # Aiguillage vers la fonction de construction adéquate
    if view == VIEW_BINS:
        return _build_bins_view(df)
    if view == VIEW_SECTORS:
        return _build_sectors_view(df)
    
    return _build_top_orgs_view(df)


def _build_top_orgs_view(df: pd.DataFrame) -> go.Figure:
    """
    Construit la vue du Top 15 des organisations les plus émettrices.

    Args:
        df (pd.DataFrame): Données à analyser.

    Returns:
        go.Figure: Graphique en barres horizontales Plotly.
    """
    # Exclusion des lignes sans raison sociale renseignée
    valid = df.dropna(subset=["raison_sociale"])
    if valid.empty:
        return _empty_figure("Aucune organisation identifiée.")

    # Somme des émissions cumulées par organisation
    by_org = (
        valid.groupby("raison_sociale", as_index=False)["total_emissions"]
             .sum()
    )
    # On ne garde que les émetteurs positifs
    by_org = by_org[by_org["total_emissions"] > 0]
    if by_org.empty:
        return _empty_figure("Aucune émission positive sur la sélection.")

    # Extraction des 15 plus grandes valeurs, triées par ordre croissant pour l'affichage horizontal
    top = by_org.nlargest(TOP_N, "total_emissions").sort_values(
        "total_emissions", ascending=True
    )
    
    # Raccourcissement des raisons sociales trop longues pour ne pas encombrer l'axe Y
    top["label"] = top["raison_sociale"].apply(
        lambda s: (s[:42] + "…") if isinstance(s, str) and len(s) > 45 else s
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["total_emissions"],
        y=top["label"],
        orientation="h", # Graphique horizontal
        marker=dict(
            color=top["total_emissions"],
            colorscale=SEQUENTIAL_HEATMAP, # Palette de couleurs séquentielle verte-jaune-rouge
            showscale=False,
            line=dict(color=COLORS["surface"], width=1),
        ),
        customdata=top["raison_sociale"],
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "%{x:,.0f} tCO₂eq"
            "<extra></extra>"
        ),
        # Affichage du classement à droite de chaque barre (#1, #2, etc.)
        text=[f"#{i+1}" for i in range(len(top) - 1, -1, -1)],
        textposition="outside",
        textfont=dict(family="DM Sans", size=11, color=COLORS["text_muted"]),
    ))

    # Calcul d'une hauteur proportionnelle au nombre de barres affichées
    chart_height = max(420, 80 + 28 * len(top))

    fig.update_layout(
        xaxis_title="Émissions cumulées (tCO₂eq)",
        yaxis_title=None,
        bargap=0.25,
    )
    fig.update_xaxes(tickformat=".2s")
    apply_theme(fig, height=chart_height, show_legend=False)
    return fig


def _build_bins_view(df: pd.DataFrame) -> go.Figure:
    """
    Construit la vue par paliers d'émissions (distribution logarithmique).

    Args:
        df (pd.DataFrame): Données à distribuer.

    Returns:
        go.Figure: Graphique en barres verticales.
    """
    # Filtrage des émissions supérieures à zéro
    valid = df[df["total_emissions"] > 0].copy()
    if valid.empty:
        return _empty_figure("Aucune émission positive sur la sélection.")

    # Découpage et classification des émissions dans les intervalles définis (paliers)
    valid["bin"] = pd.cut(
        valid["total_emissions"],
        bins=EMISSION_BINS,
        labels=EMISSION_BIN_LABELS,
        include_lowest=True,
    )
    # Calcul du nombre de bilans et de la somme des émissions par palier
    counts = valid.groupby("bin", observed=False).size()
    sums = valid.groupby("bin", observed=False)["total_emissions"].sum()

    # Sélection de 5 nuances de couleurs associées aux paliers
    bin_colors = [
        SEQUENTIAL_HEATMAP[0][1],    # Vert
        SEQUENTIAL_HEATMAP[1][1],    # Vert clair
        SEQUENTIAL_HEATMAP[2][1],    # Jaune
        SEQUENTIAL_HEATMAP[4][1],    # Orange
        SEQUENTIAL_HEATMAP[5][1],    # Rouge
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=EMISSION_BIN_LABELS,
        y=counts.values,
        marker=dict(
            color=bin_colors,
            line=dict(color=COLORS["surface"], width=1),
        ),
        # Affichage du nombre total de bilans au-dessus de chaque barre
        text=[
            f"<b>{c:,}</b>".replace(",", " ")
            for c in counts.values
        ],
        textposition="outside",
        textfont=dict(family="DM Sans", size=12, color=COLORS["text"]),
        # Informations détaillées affichées au survol
        customdata=[
            [int(c), float(s) / 1_000_000]
            for c, s in zip(counts.values, sums.values)
        ],
        hovertemplate=(
            "<b>Palier %{x}</b><br>"
            "%{customdata[0]:,} bilans<br>"
            "%{customdata[1]:,.1f} MtCO₂eq cumulés"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        xaxis_title="Palier d'émissions (tCO₂eq)",
        yaxis_title="Nombre de bilans",
        bargap=0.35,
    )
    fig.update_xaxes(tickfont=dict(size=12, color=COLORS["text"]))
    fig.update_yaxes(tickformat=",")
    apply_theme(fig, height=440, show_legend=False)
    return fig


def _build_sectors_view(df: pd.DataFrame) -> go.Figure:
    """
    Construit la vue du Top 15 des secteurs d'activité (NAF) les plus émetteurs.

    Args:
        df (pd.DataFrame): Données à analyser.

    Returns:
        go.Figure: Graphique en barres horizontales.
    """
    valid = df.dropna(subset=["libelle_naf", "raison_sociale"])
    if valid.empty:
        return _empty_figure("Aucun secteur NAF renseigné.")

    # Agrégation des émissions et comptage du nombre d'organisations distinctes par secteur
    by_sector = valid.groupby("libelle_naf").agg(
        total_emissions=("total_emissions", "sum"),
        nb_orgs=("raison_sociale", "nunique"),
    ).reset_index()

    # Exclusion des secteurs comptant moins de 3 organisations pour éviter les biais statistiques
    by_sector = by_sector[by_sector["nb_orgs"] >= MIN_ORGS_PER_SECTOR]
    by_sector = by_sector[by_sector["total_emissions"] > 0]

    if by_sector.empty:
        return _empty_figure(
            f"Aucun secteur ne compte ≥{MIN_ORGS_PER_SECTOR} organisations "
            "sur la sélection."
        )

    # Récupération et tri des 15 plus grands secteurs émetteurs
    top = by_sector.nlargest(TOP_N, "total_emissions").sort_values(
        "total_emissions", ascending=True
    )
    
    # Raccourcissement des noms longs des secteurs
    top["label"] = top["libelle_naf"].apply(
        lambda s: (s[:48] + "…") if isinstance(s, str) and len(s) > 50 else s
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["total_emissions"],
        y=top["label"],
        orientation="h",
        marker=dict(
            color=top["total_emissions"],
            colorscale=SEQUENTIAL_HEATMAP,
            showscale=False,
            line=dict(color=COLORS["surface"], width=1),
        ),
        customdata=list(zip(top["libelle_naf"], top["nb_orgs"])),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{x:,.0f} tCO₂eq cumulées<br>"
            "%{customdata[1]} organisations"
            "<extra></extra>"
        ),
        # Affichage du nombre d'organisations à droite de chaque barre
        text=[f"{n} orgs" for n in top["nb_orgs"]],
        textposition="outside",
        textfont=dict(family="DM Sans", size=11, color=COLORS["text_muted"]),
    ))

    chart_height = max(420, 80 + 28 * len(top))
    fig.update_layout(
        xaxis_title="Émissions cumulées par secteur (tCO₂eq)",
        yaxis_title=None,
        bargap=0.25,
    )
    fig.update_xaxes(tickformat=".2s")
    apply_theme(fig, height=chart_height, show_legend=False)
    return fig


def _empty_figure(message: str) -> go.Figure:
    """
    Génère un graphique vierge avec une note centrale en cas d'absence de données.

    Args:
        message (str): Texte explicatif à afficher.

    Returns:
        go.Figure: Graphique vide Plotly contenant l'annotation.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family="DM Sans", size=14, color=COLORS["text_muted"]),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    apply_theme(fig, height=440, show_legend=False)
    return fig
