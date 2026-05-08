# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Render 2×2 Opportunity × Actionability quadrant plots.

Produces:
  - 00_quadrant_overview.png           (all 231 cells, colored by product)
  - 01_quadrant_per_product.png        (small-multiples grid: 11 sub-plots)
  - 02_quadrant_HL_focus.png           (zoom on the 24 Engagement-build cells with labels)
  - data also re-rendered as SVG for deck embedding

Reads opportunity_matrix_v2.csv. Output to working/data/master/figures_actionability/.
"""
import sys
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from adjustText import adjust_text

sys.stdout.reconfigure(encoding="utf-8")

# Centralised Pfizer chart styling (registers IBM Plex Sans, palette, rcParams).
# Aligns Python typography with R theme_pfizer() — chart audit fix 2026-04-25.
sys.path.insert(0, str(Path(__file__).parent))
from _pf_chart_setup import apply_pf_style, PF
apply_pf_style()

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/opportunity_matrix_v2.csv"
OUT_DIR = ROOT / "working/data/master/figures_actionability"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Pfizer palette aliases — defer to PF namespace (chart audit fix 2026-04-25)
PF_NAVY = PF.navy
PF_LIGHT_BLUE = PF.blue_soft
PF_GREY = PF.text_secondary
PF_LIGHT_GREY = PF.grey_mist
PF_RED = PF.red
PF_AMBER = "#F39C12"
PF_GREEN = "#27AE60"

# 11 product colors (perceptually distinguishable)
PRODUCT_COLORS = {
    "Tukysa":            "#003F7F",  # Pfizer navy
    "Lorbrena/Lorviqua": "#0072B2",
    "Elrexfio":          "#56B4E9",
    "Ibrance":           "#E4002B",  # Pfizer red
    "Talzenna":          "#D55E00",
    "Vyndaqel":          "#CC79A7",
    "Hympavzi":          "#F0E442",
    "Paxlovid":          "#009E73",
    "Vydura":            "#882255",
    "Prevenar 20":       "#117733",
    "Abrysvo":           "#AA4499",
}

# Quadrant background fills (light, transparent)
Q_HH_FILL = "#D7EDD9"   # very light green
Q_HL_FILL = "#FBE5C8"   # very light amber
Q_LH_FILL = "#E1ECF7"   # very light blue
Q_LL_FILL = "#EFEFEF"   # very light grey

OPP_T = 45
ACT_T = 60

# Per-figure overrides on top of apply_pf_style() defaults
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "axes.grid": False,         # quadrant plots use background fills, no gridlines
    "legend.fontsize": 8,
    "savefig.dpi": 200,
})


def load():
    rows = []
    with SRC.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["opportunity"] = float(row["opportunity"])
            row["actionability"] = float(row["actionability"])
            rows.append(row)
    return rows


def draw_quadrant_background(ax, x_lim=(0, 100), y_lim=(0, 100)):
    """Fill quadrants with subtle background colors + draw threshold lines."""
    # LL (bottom-left)
    ax.axhspan(y_lim[0], ACT_T, xmin=0, xmax=OPP_T / x_lim[1],
               facecolor=Q_LL_FILL, zorder=0)
    # LH (top-left)
    ax.axhspan(ACT_T, y_lim[1], xmin=0, xmax=OPP_T / x_lim[1],
               facecolor=Q_LH_FILL, zorder=0)
    # HL (bottom-right)
    ax.axhspan(y_lim[0], ACT_T, xmin=OPP_T / x_lim[1], xmax=1,
               facecolor=Q_HL_FILL, zorder=0)
    # HH (top-right)
    ax.axhspan(ACT_T, y_lim[1], xmin=OPP_T / x_lim[1], xmax=1,
               facecolor=Q_HH_FILL, zorder=0)
    # Threshold lines
    ax.axvline(OPP_T, color=PF_GREY, linestyle="--", linewidth=0.7, alpha=0.6, zorder=1)
    ax.axhline(ACT_T, color=PF_GREY, linestyle="--", linewidth=0.7, alpha=0.6, zorder=1)


def annotate_quadrants(ax, x_lim=(0, 100), y_lim=(0, 100), small=False):
    label_size = 7 if small else 9
    label_color = PF_GREY
    label_alpha = 0.55
    # HH (top-right)
    ax.text(x_lim[1] - 2, y_lim[1] - 2, "HH  Priority focus",
            ha="right", va="top", fontsize=label_size,
            color=label_color, alpha=label_alpha, weight="bold")
    # HL (bottom-right)
    ax.text(x_lim[1] - 2, y_lim[0] + 2, "HL  Engagement build",
            ha="right", va="bottom", fontsize=label_size,
            color=label_color, alpha=label_alpha, weight="bold")
    # LH (top-left)
    ax.text(x_lim[0] + 2, y_lim[1] - 2, "LH  Quick win",
            ha="left", va="top", fontsize=label_size,
            color=label_color, alpha=label_alpha, weight="bold")
    # LL (bottom-left)
    ax.text(x_lim[0] + 2, y_lim[0] + 2, "LL  Deprioritize",
            ha="left", va="bottom", fontsize=label_size,
            color=label_color, alpha=label_alpha, weight="bold")


# ============================================================================
# PLOT 1 — overview (clean redesign)
# ============================================================================
# Design rationale: 231 cells colored across eleven products is visually overloaded
# and the legend doesn't help reading. Replaced with a single neutral colour for
# the bulk, prominent quadrant counts as the headline, and a small top-N highlight
# in each quadrant so the strategic cells can be picked out by eye.
def plot_overview(rows):
    from collections import Counter

    fig, ax = plt.subplots(figsize=(11, 8))
    draw_quadrant_background(ax)

    # Bulk dots — single neutral colour, small, low opacity. Reads as a density cloud.
    xs_all = [r["opportunity"] for r in rows]
    ys_all = [r["actionability"] for r in rows]
    ax.scatter(xs_all, ys_all, c=PF_NAVY, s=22, alpha=0.32, edgecolors="white",
               linewidths=0.4, zorder=3)

    # Highlight the top-3 by Opportunity in each quadrant — bigger marker + label.
    # These are the cells a strategist's eye is drawn to first.
    quadrants = {"HH": [], "HL": [], "LH": [], "LL": []}
    for r in rows:
        if r["quadrant"] in quadrants:
            quadrants[r["quadrant"]].append(r)
    text_objs = []
    for q, q_rows in quadrants.items():
        q_rows.sort(key=lambda r: -r["opportunity"])
        for r in q_rows[:3]:
            ax.scatter(r["opportunity"], r["actionability"], c=PF_NAVY, s=85,
                       alpha=0.95, edgecolors="white", linewidths=1.0, zorder=5)
            short = (r["region"].replace("Region ", "")
                                .replace("Västra Götalandsregionen", "VGR")
                                .replace("Jämtland Härjedalen", "Jämtland H")
                                .replace(" län", ""))
            label = f"{short[:10]} × {r['product'].split('/')[0][:8]}"
            t = ax.text(r["opportunity"], r["actionability"], label,
                        fontsize=7.5, color=PF_NAVY, weight="semibold", zorder=6)
            text_objs.append(t)
    if text_objs:
        adjust_text(
            text_objs, ax=ax,
            expand_points=(1.4, 1.6), expand_text=(1.2, 1.3),
            force_points=(0.5, 0.7), force_text=(0.4, 0.6),
            arrowprops=dict(arrowstyle="-", color=PF_GREY, lw=0.4, alpha=0.5),
        )

    # Quadrant headline counts — number + clear label of what the number means.
    # Each block reads: "70  cells" then below it "Priority focus" then a tiny
    # one-line description so the meaning is unmissable at a glance.
    qcount = Counter(r["quadrant"] for r in rows)
    quad_blocks = {
        "HH": (94, 84, "right", "top",
               "Priority focus",  "high opp · high act"),
        "HL": (94, 26, "right", "bottom",
               "Engagement build", "high opp · low act"),
        "LH": (16, 84, "left",  "top",
               "Quick win",        "low opp · high act"),
        "LL": (16, 26, "left",  "bottom",
               "Deprioritise",     "low opp · low act"),
    }
    for q, (x, y, ha, va, name, descr) in quad_blocks.items():
        n = qcount.get(q, 0)
        # Big count + " cells" caption attached on the same baseline
        ax.text(x, y, f"{n}", fontsize=30, color=PF_NAVY, weight="bold",
                ha=ha, va=va, zorder=2, alpha=0.92)
        # Quadrant name — larger and darker than before so it's actually readable
        y_off1 = -4.0 if va == "top" else 4.5
        ax.text(x, y + y_off1, name, fontsize=11, color=PF_NAVY, weight="bold",
                ha=ha, va=va, zorder=2, alpha=0.92)
        # One-line description
        y_off2 = -7.0 if va == "top" else 7.5
        ax.text(x, y + y_off2, descr, fontsize=8.5, color=PF_GREY,
                style="italic", ha=ha, va=va, zorder=2, alpha=0.85)

    # Range and labels
    ax.set_xlim(15, 95)
    ax.set_ylim(25, 85)
    ax.set_xlabel("Opportunity score (higher = more attractive)",
                  color=PF_NAVY, fontweight="bold")
    ax.set_ylabel("Actionability score (higher = within reach)",
                  color=PF_NAVY, fontweight="bold")
    ax.set_title("Region × product opportunity matrix — 231 cells\n"
                 f"Thresholds at data medians (Opportunity {OPP_T}, Actionability {ACT_T}); "
                 "labelled cells = top 3 by opportunity in each quadrant",
                 color=PF_NAVY, pad=14)

    fig.text(0.01, -0.02,
             "Source: region × product opportunity matrix. Composite scores Modeled.",
             ha="left", va="top", fontsize=7, color=PF_GREY, style="italic")

    out_png = OUT_DIR / "00_quadrant_overview.png"
    out_svg = OUT_DIR / "00_quadrant_overview.svg"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  Wrote {out_png.name}")
    print(f"  Wrote {out_svg.name}")


# ============================================================================
# PLOT 2 — per-product small multiples
# ============================================================================
def plot_per_product(rows):
    products = list(PRODUCT_COLORS.keys())
    n = len(products)
    cols = 4
    rows_n = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols, figsize=(15, 11), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, product in enumerate(products):
        ax = axes[i]
        draw_quadrant_background(ax)
        annotate_quadrants(ax, small=True)

        prows = [r for r in rows if r["product"] == product]
        xs = [r["opportunity"] for r in prows]
        ys = [r["actionability"] for r in prows]
        labels = [r["region"].replace("Region ", "").replace("Västra Götalandsregionen", "VGR")
                                                    .replace("Jämtland Härjedalen", "Jämtland H")
                  for r in prows]

        ax.scatter(xs, ys, c=PRODUCT_COLORS[product], s=46, alpha=0.85,
                   edgecolors="white", linewidths=0.8, zorder=3)

        # Label points in HH and HL quadrants only (the strategic ones)
        for r, x, y, label in zip(prows, xs, ys, labels):
            if r["quadrant"] in ("HH", "HL"):
                ax.annotate(label, (x, y), xytext=(4, 3), textcoords="offset points",
                            fontsize=6.5, color=PF_GREY, alpha=0.85)

        ax.set_xlim(15, 95)
        ax.set_ylim(25, 85)
        ax.set_title(product, color=PF_NAVY, fontsize=10, pad=4)
        if i % cols == 0:
            ax.set_ylabel("Actionability", fontsize=8, color=PF_NAVY)
        if i // cols == rows_n - 1:
            ax.set_xlabel("Opportunity", fontsize=8, color=PF_NAVY)

    # Hide any unused subplots
    for i in range(n, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle("Pfizer Sweden — Opportunity × Actionability by product (small multiples)",
                 fontsize=13, color=PF_NAVY, fontweight="bold", y=0.995)
    fig.text(0.01, 0.01,
             f"231 cells across 11 products × 21 regions. Thresholds: Opp {OPP_T} / Act {ACT_T}. "
             "HH + HL cells labeled with region name.",
             ha="left", fontsize=7, color=PF_GREY, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 0.98])

    out_png = OUT_DIR / "01_quadrant_per_product.png"
    out_svg = OUT_DIR / "01_quadrant_per_product.svg"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  Wrote {out_png.name}")
    print(f"  Wrote {out_svg.name}")


# ============================================================================
# PLOT 3 — HL focus (clean redesign)
# ============================================================================
# Design rationale: prior version used eleven product colours on the 24 highlighted
# cells, which made the figure read like a colour-key puzzle rather than a clear
# focus on which cells to engage. New design: every HL cell in one accent colour,
# every other cell in a near-invisible grey, and labels with leader lines so the
# reader's eye lands on the names rather than the legend.
def plot_hl_focus(rows):
    hl_rows = [r for r in rows if r["quadrant"] == "HL"]
    hl_rows.sort(key=lambda r: -r["opportunity"])

    fig, ax = plt.subplots(figsize=(13, 9))
    draw_quadrant_background(ax)

    # Background — every non-HL cell, very faint, very small
    other = [r for r in rows if r["quadrant"] != "HL"]
    ax.scatter([r["opportunity"] for r in other],
               [r["actionability"] for r in other],
               c=PF_GREY, s=14, alpha=0.22, edgecolors="white",
               linewidths=0.3, zorder=2)

    # HL cells — single accent colour, larger, with white edge for separation
    HL_ACCENT = "#D97A1F"  # warm amber, calmer than red, distinct from navy
    xs = [r["opportunity"] for r in hl_rows]
    ys = [r["actionability"] for r in hl_rows]
    ax.scatter(xs, ys, c=HL_ACCENT, s=130, alpha=0.95,
               edgecolors="white", linewidths=1.4, zorder=4)

    text_objs = []
    for r in hl_rows:
        short = (r["region"].replace("Region ", "")
                            .replace("Västra Götalandsregionen", "VGR")
                            .replace("Jämtland Härjedalen", "Jämtland H")
                            .replace(" län", ""))
        label = f"{short} × {r['product'].split('/')[0]}"
        t = ax.text(r["opportunity"], r["actionability"], label,
                    fontsize=8.5, color=PF_NAVY, weight="semibold", zorder=6)
        text_objs.append(t)

    # Collision-avoiding label placement with leader lines
    adjust_text(
        text_objs, ax=ax,
        expand_points=(1.7, 1.9), expand_text=(1.3, 1.4),
        force_points=(0.7, 0.9), force_text=(0.5, 0.7),
        arrowprops=dict(arrowstyle="-", color=PF_GREY, lw=0.5, alpha=0.55),
    )

    # Quadrant labels — quiet, in the corners
    annotate_quadrants(ax)

    ax.set_xlim(15, 95)
    ax.set_ylim(25, 85)
    ax.set_xlabel("Opportunity score", color=PF_NAVY, fontweight="bold")
    ax.set_ylabel("Actionability score", color=PF_NAVY, fontweight="bold")
    ax.set_title(f"Engagement build — {len(hl_rows)} cells worth investing in\n"
                 "High opportunity but actionability below threshold; "
                 "where relationship and footprint work pays off",
                 color=PF_NAVY, pad=14)

    fig.text(0.01, -0.01,
             f"Highlighted points: opportunity ≥ {OPP_T} and actionability < {ACT_T}. "
             f"Faint grey points: the other 207 cells, shown for reference.",
             ha="left", fontsize=8, color=PF_GREY, style="italic")

    out_png = OUT_DIR / "02_quadrant_HL_focus.png"
    out_svg = OUT_DIR / "02_quadrant_HL_focus.svg"
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  Wrote {out_png.name}")
    print(f"  Wrote {out_svg.name}")


def main():
    print(f"Loading {SRC.name} ...")
    rows = load()
    print(f"Loaded {len(rows)} rows")

    print("\nRendering plots ...")
    plot_overview(rows)
    plot_per_product(rows)
    plot_hl_focus(rows)

    # Summary
    from collections import Counter
    qcount = Counter(r["quadrant"] for r in rows)
    print(f"\nQuadrant distribution: {dict(qcount)}")
    print(f"Output directory: {OUT_DIR}")


if __name__ == "__main__":
    main()
