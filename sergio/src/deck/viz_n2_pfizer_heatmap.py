# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N2 — Pfizer Footprint per 100k Heatmap (national figure).

21 regions × 10 Pfizer products. Cell colour = 3-year Sell-In SEK per 100k
inhabitants, percentile-binned across all (region × product) cells. Surfaces
where Pfizer is over- or under-indexed across the country.

Output: delivery/figures/national/N2_pfizer_per100k_heatmap.png
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS, add_title_block, add_source_line, add_accent_rule

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load Pfizer total footprint
df = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Pfizer total footprint")
df = df[~df["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
df = df.dropna(subset=["Region"])

# Aggregate FSME-IMMUN VUXEN + JUNIOR
df["FSME-IMMUN total"] = df["FSME-IMMUN VUXEN SEK (3yr)"] + df["FSME-IMMUN JUNIOR SEK (3yr)"]

PRODUCTS = [
    ("FSME-IMMUN total",       "FSME-IMMUN"),
    ("ABRYSVO SEK (3yr)",      "Abrysvo"),
    ("PREVENAR 20 SEK (3yr)",  "Prevenar 20"),
    ("VYNDAQEL SEK (3yr)",     "Vyndaqel"),
    ("VYDURA SEK (3yr)",       "Vydura"),
    ("IBRANCE SEK (3yr)",      "Ibrance"),
    ("TUKYSA SEK (3yr)",       "Tukysa"),
    ("TALZENNA SEK (3yr)",     "Talzenna"),
    ("LORVIQUA SEK (3yr)",     "Lorviqua"),
    ("ELREXFIO SEK (3yr)",     "Elrexfio"),
]

# Build per-100k matrix
df["region_short"] = df["Region"].str.replace("Region ", "").replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})
# Sort by total Pfizer SEK descending
df = df.sort_values("Total Pfizer SEK", ascending=False).reset_index(drop=True)

# Build a (region × product) per-100k matrix
matrix = pd.DataFrame(index=df["region_short"])
for col_key, label in PRODUCTS:
    matrix[label] = df[col_key].values / df["Population"].values * 100000

# For colour scaling, percentile-rank each product column independently
# (so each product's column is comparable across regions, and zero stays zero)
def percentile_rank(s):
    ranked = s.rank(pct=True)
    ranked.loc[s == 0] = 0
    return ranked

color_matrix = matrix.apply(percentile_rank)

# Custom Viti gradient: white → light → blue → dark
viti_cmap = LinearSegmentedColormap.from_list(
    "viti_blue_gradient",
    [(0.0, "#FFFFFF"),
     (0.10, COLORS["viti_light"]),
     (0.45, COLORS["viti_medium"]),
     (0.75, COLORS["pfizer_blue"]),
     (1.0,  COLORS["competitor_charcoal"])],
)

EXEMPLARS = {"Stockholm", "Västerbotten"}

# ---------------------------------------------------------------------------
# Figure — use imshow for clean rectangular heatmap
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.14, right=0.92, top=0.70, bottom=0.10)
ax = fig.add_subplot(111)

n_rows, n_cols = matrix.shape

# imshow handles aspect ratio properly
im = ax.imshow(color_matrix.values, cmap=viti_cmap, aspect="auto",
                vmin=0, vmax=1)

# White grid lines between cells
ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="minor", bottom=False, left=False)

# Annotate cells with values
for r in range(n_rows):
    for c in range(n_cols):
        col_pct = color_matrix.iloc[r, c]
        val = matrix.iloc[r, c]
        if val >= 1e6:
            txt = f"{val/1e6:.1f}M"
        elif val >= 1e3:
            txt = f"{val/1e3:.0f}k"
        elif val > 0:
            txt = f"{val:.0f}"
        else:
            txt = ""
        text_color = "white" if col_pct > 0.65 else COLORS["viti_dark"]
        if txt:
            ax.text(c, r, txt,
                     ha="center", va="center",
                     fontsize=7.5, color=text_color,
                     fontweight="semibold" if col_pct > 0.5 else "regular",
                     zorder=3)

# Region labels on Y axis
ax.set_yticks(range(n_rows))
ax.set_yticklabels([])
for r, region in enumerate(matrix.index):
    is_exemplar = region in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
    ax.text(-0.6, r, region,
             ha="right", va="center",
             fontsize=9.5, color=color, fontweight=weight)

# Product labels on X axis (top)
ax.set_xticks(range(n_cols))
ax.set_xticklabels([])
for c, product in enumerate(matrix.columns):
    ax.text(c, -0.7, product,
             ha="center", va="bottom",
             fontsize=9.5, color=COLORS["viti_dark"],
             fontweight="semibold", rotation=35)

# Hide spines and tick marks
ax.tick_params(which="major", bottom=False, left=False)
for spine in ax.spines.values():
    spine.set_visible(False)
# Move x-axis labels to top
ax.xaxis.tick_top()

# Colorbar legend
cbar_ax = fig.add_axes([0.93, 0.15, 0.012, 0.50])
cbar = plt.colorbar(im, cax=cbar_ax)
cbar.outline.set_visible(False)
cbar.set_ticks([0, 0.5, 1.0])
cbar.set_ticklabels(["0", "median", "100%ile"])
cbar.ax.tick_params(labelsize=8.5, length=0, color=COLORS["viti_gray"])
cbar.ax.set_title("Per-100k\nrank", fontsize=8.5,
                   color=COLORS["viti_gray"], fontweight="semibold",
                   pad=10, loc="left")

# Title block
add_accent_rule(fig, x=0.06, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="NATIONAL  ·  PFIZER FOOTPRINT PER 100K  ·  21 REGIONS  ×  10 PRODUCTS",
    headline="Where Pfizer is over- or under-indexed across Sweden.",
    takeaway="Cell colour = 3-year Sell-In SEK per 100k inhabitants, ranked within each product column. Vyndaqel concentration in Norrland is the most extreme single-product over-index in the portfolio.",
    x=0.06, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
    takeaway_width=140, takeaway_line_step=0.027,
)

add_source_line(fig,
                "Source: IQVIA Sell-In SEK Apr 2023–Mar 2026 (Vaccines + RD/IM + Oncology) ÷ region population. "
                "Colour scale = within-product percentile to surface relative concentration. Stockholm + Västerbotten highlighted as exemplar regions.",
                x=0.06, y=0.025)

plt.savefig(OUT / "N2_pfizer_per100k_heatmap.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N2_pfizer_per100k_heatmap.png'}")
