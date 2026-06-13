"""
Composant 'distribution multi-vues' - système d'analyse scalable.

Le dataset contient 6 810 organisations distinctes : un histogramme
naïf de toutes les barres serait illisible et coûteux en performance.
Nous proposons donc 3 vues commutables, chacune adaptée à un besoin
analytique différent :

  1. TOP 15 ORGANISATIONS — qui sont les plus gros émetteurs ?
  2. PALIERS D'ÉMISSIONS — comment se répartissent les bilans par
     ordre de grandeur (<1k, 1-10k, 10-100k, 100k-1M, >1M tCO₂eq) ?
  3. TOP 15 SECTEURS NAF — quels secteurs concentrent les émissions ?
     (filtre minimum 3 organisations par secteur pour éviter qu'un
     secteur n'ait qu'une grosse boîte = duplication de la vue Top orgs)

Doc Plotly bar chart : https://plotly.com/python/bar-charts/
"""

import pandas as pd
import plotly.graph_objects as go

from src.components.charts_theme import apply_theme, COLORS, SEQUENTIAL_HEATMAP


# ─────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────

# Identifiants des 3 vues (utilisés par le toggle UI dans analysis.py).
VIEW_TOP_ORGS = "top_orgs"
VIEW_BINS = "bins"
VIEW_SECTORS = "sectors"

# Bornes des paliers d'émissions. Choisies sur les ordres de grandeur
# observés dans la base : médiane ~5 600 tCO2eq, max > 3 milliards.
# Chaque palier = facteur 10, qui correspond à une logique business
# (PME, ETI, grande entreprise, gros groupe industriel).
EMISSION_BINS = [0, 1_000, 10_000, 100_000, 1_000_000, float("inf")]
EMISSION_BIN_LABELS = [
    "<1k tCO₂eq",
    "1k–10k",
    "10k–100k",
    "100k–1M",
    ">1M",
]

# Nombre d'éléments à afficher dans les vues "Top".
TOP_N = 15

# Nombre minimum d'organisations pour qu'un secteur soit considéré
# comme représentatif (sinon = 1 grosse boîte = doublon de la vue Top).
MIN_ORGS_PER_SECTOR = 3


# ─────────────────────────────────────────────────────────────────
# Dispatcher principal
# ─────────────────────────────────────────────────────────────────

def create_histogram(df: pd.DataFrame, view: str = VIEW_TOP_ORGS) -> go.Figure:
    """
    Construit l'histogramme correspondant à la vue demandée.

    Args:
        df: DataFrame filtré (issu de filter_data).
        view: 'top_orgs' | 'bins' | 'sectors' — vue à afficher.

    Returns:
        go.Figure: Figure Plotly prête pour dcc.Graph.
    """
    if df.empty:
        return _empty_figure("Aucun bilan ne correspond aux filtres.")

    if view == VIEW_BINS:
        return _build_bins_view(df)
    if view == VIEW_SECTORS:
        return _build_sectors_view(df)
    # Par défaut : Top organisations.
    return _build_top_orgs_view(df)


# ─────────────────────────────────────────────────────────────────
# VUE 1 — Top 15 organisations émettrices
# ─────────────────────────────────────────────────────────────────

def _build_top_orgs_view(df: pd.DataFrame) -> go.Figure:
    """Top 15 organisations par émissions cumulées sur la sélection."""
    # Filtre des bilans avec organisation nommée.
    valid = df.dropna(subset=["raison_sociale"])
    if valid.empty:
        return _empty_figure("Aucune organisation identifiée.")

    # Agrégation par organisation : somme des émissions sur la sélection.
    by_org = (
        valid.groupby("raison_sociale", as_index=False)["total_emissions"]
             .sum()
    )
    by_org = by_org[by_org["total_emissions"] > 0]
    if by_org.empty:
        return _empty_figure("Aucune émission positive sur la sélection.")

    # Sélection des Top N et tri ascendant pour barres horizontales
    # (la plus grosse organisation apparaît en haut visuellement).
    top = by_org.nlargest(TOP_N, "total_emissions").sort_values(
        "total_emissions", ascending=True
    )
    # Tronque les noms longs pour rester lisible (raison sociale ADEME
    # peut atteindre 80+ caractères avec mentions juridiques).
    top["label"] = top["raison_sociale"].apply(
        lambda s: (s[:42] + "…") if isinstance(s, str) and len(s) > 45 else s
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["total_emissions"],
        y=top["label"],
        orientation="h",
        marker=dict(
            # Coloration heatmap par intensité : barre la plus longue =
            # rouge (gros émetteur), barres plus courtes = vert.
            color=top["total_emissions"],
            colorscale=SEQUENTIAL_HEATMAP,
            showscale=False,
            line=dict(color=COLORS["surface"], width=1),
        ),
        customdata=top["raison_sociale"],
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "%{x:,.0f} tCO₂eq"
            "<extra></extra>"
        ),
        # Affiche le rang à droite de chaque barre (#1, #2…).
        text=[f"#{i+1}" for i in range(len(top) - 1, -1, -1)],
        textposition="outside",
        textfont=dict(family="DM Sans", size=11, color=COLORS["text_muted"]),
    ))

    # Hauteur dynamique : 28 px par organisation + marges.
    chart_height = max(420, 80 + 28 * len(top))

    fig.update_layout(
        xaxis_title="Émissions cumulées (tCO₂eq)",
        yaxis_title=None,
        bargap=0.25,
    )
    fig.update_xaxes(tickformat=".2s")
    apply_theme(fig, height=chart_height, show_legend=False)
    return fig


# ─────────────────────────────────────────────────────────────────
# VUE 2 — Distribution par paliers d'émissions
# ─────────────────────────────────────────────────────────────────

def _build_bins_view(df: pd.DataFrame) -> go.Figure:
    """Distribution des bilans par palier d'émissions (5 bins logarithmiques)."""
    valid = df[df["total_emissions"] > 0].copy()
    if valid.empty:
        return _empty_figure("Aucune émission positive sur la sélection.")

    # Catégorisation des bilans par palier d'ordre de grandeur.
    # observed=False : on garde les bins vides dans le résultat pour
    # avoir un histogramme avec toujours 5 barres (lisibilité visuelle).
    valid["bin"] = pd.cut(
        valid["total_emissions"],
        bins=EMISSION_BINS,
        labels=EMISSION_BIN_LABELS,
        include_lowest=True,
    )
    counts = valid.groupby("bin", observed=False).size()
    sums = valid.groupby("bin", observed=False)["total_emissions"].sum()

    # Couleurs : on utilise la palette HEATMAP discrétisée sur les 5 bins
    # pour matcher visuellement le code couleur de la carte (vert→rouge).
    bin_colors = [
        SEQUENTIAL_HEATMAP[0][1],    # vert
        SEQUENTIAL_HEATMAP[1][1],    # vert clair
        SEQUENTIAL_HEATMAP[2][1],    # jaune
        SEQUENTIAL_HEATMAP[4][1],    # orange foncé
        SEQUENTIAL_HEATMAP[5][1],    # rouge profond
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=EMISSION_BIN_LABELS,
        y=counts.values,
        marker=dict(
            color=bin_colors,
            line=dict(color=COLORS["surface"], width=1),
        ),
        # Texte au-dessus de chaque barre : nb bilans + part en %
        text=[
            f"<b>{c:,}</b>".replace(",", " ")
            for c in counts.values
        ],
        textposition="outside",
        textfont=dict(family="DM Sans", size=12, color=COLORS["text"]),
        # Hover : nb bilans + émissions cumulées du palier
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


# ─────────────────────────────────────────────────────────────────
# VUE 3 — Top 15 secteurs NAF (avec ≥3 organisations)
# ─────────────────────────────────────────────────────────────────

def _build_sectors_view(df: pd.DataFrame) -> go.Figure:
    """Top 15 secteurs NAF par émissions cumulées (≥3 orgs/secteur)."""
    valid = df.dropna(subset=["libelle_naf", "raison_sociale"])
    if valid.empty:
        return _empty_figure("Aucun secteur NAF renseigné.")

    # Calcul par secteur : émissions cumulées + nombre d'organisations.
    # On vérifie les 2 critères pour qualifier un secteur "représentatif".
    by_sector = valid.groupby("libelle_naf").agg(
        total_emissions=("total_emissions", "sum"),
        nb_orgs=("raison_sociale", "nunique"),
    ).reset_index()

    # Filtre : on exclut les secteurs avec <3 organisations distinctes.
    # Sinon le secteur "Extraction de pétrole brut" = 1 boîte = doublon
    # de la vue Top organisations, sans valeur sectorielle réelle.
    by_sector = by_sector[by_sector["nb_orgs"] >= MIN_ORGS_PER_SECTOR]
    by_sector = by_sector[by_sector["total_emissions"] > 0]

    if by_sector.empty:
        return _empty_figure(
            f"Aucun secteur ne compte ≥{MIN_ORGS_PER_SECTOR} organisations "
            "sur la sélection."
        )

    # Tri + Top N + tri ascendant pour affichage horizontal naturel.
    top = by_sector.nlargest(TOP_N, "total_emissions").sort_values(
        "total_emissions", ascending=True
    )
    # Tronque les libellés NAF longs (certains atteignent 100+ caractères).
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
        # customdata : libellé complet + nb d'orgs pour le hover
        customdata=list(zip(top["libelle_naf"], top["nb_orgs"])),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{x:,.0f} tCO₂eq cumulées<br>"
            "%{customdata[1]} organisations"
            "<extra></extra>"
        ),
        # Affichage du nombre d'orgs à droite (donne le contexte sectoriel)
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


# ─────────────────────────────────────────────────────────────────
# Helper privé
# ─────────────────────────────────────────────────────────────────

def _empty_figure(message: str) -> go.Figure:
    """Figure vide avec message centré (filtres trop restrictifs)."""
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
