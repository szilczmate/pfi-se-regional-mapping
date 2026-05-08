# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N4 — Sweden equity dimensions matrix (component-level breakdown of N1).

21 regions × 4 equity components, percentile-ranked. Surfaces WHERE the equity
gap sits — is it driven by foreign-born share? Education? Mortality? Healthcare-
amenable mortality? Different from N1 which shows just the composite rank.

Output: delivery/figures/region_profiles/_overview/N4_equity_dimensions.png
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load equity composite
df = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Equity composite")
df = df.sort_values("SES composite rank (1=highest need)", ascending=True).reset_index(drop=True)
df["region_short"] = df["Region"].str.replace("Region ", "")
df["region_short"] = df["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})

EXEMPLARS = {"Stockholm", "Västerbotten"}

# Components — note that for foreign-born + post-secondary education, the
# direction of "high need" is mixed. We standardise:
# - Foreign-born %: higher = higher need (more equity-friction risk)
# - Post-secondary education: LOWER = higher need (so we invert)
# - Premature mortality: higher = higher need
# - HC-amenable mortality: higher = higher need

components = {
    "Foreign-born %":             ("Foreign-born %",                    False),
    "Post-secondary edu %":       ("Post-secondary education 25–64 %",  True),   # invert
    "Premature mort. 25-64":      ("Premature mortality 25–64 /100k",   False),
    "HC-amenable mortality":      ("Healthcare-amenable mortality /100k", False),
}

# Build matrix: rows = regions, cols = components, values = need-rank percentile
matrix = pd.DataFrame(index=df["region_short"])
raw_values = pd.DataFrame(index=df["region_short"])
for label, (col, invert) in components.items():
    s = df[col].values
    raw_values[label] = s
    if invert:
        # Lower education = higher need → rank ascending (lowest = 0, highest = 1)
        ranked = pd.Series(s).rank(pct=True, ascending=False).values
    else:
        ranked = pd.Series(s).rank(pct=True, ascending=True).values
    matrix[label] = ranked

# Custom heatmap colormap: white → light blue → blue → amber (need)
need_cmap = LinearSegmentedColormap.from_list(
    "viti_need_gradient",
    [(0.0,  COLORS["viti_light"]),
     (0.50, COLORS["viti_medium"]),
     (0.75, COLORS["pfizer_blue"]),
     (1.0,  COLORS["highlight_amber"])],
)

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.18, right=0.94, top=0.66, bottom=0.10)
ax = fig.add_subplot(111)

n_rows, n_cols = matrix.shape

im = ax.imshow(matrix.values, cmap=need_cmap, aspect="auto", vmin=0, vmax=1)

# Annotate cells with raw values
for r in range(n_rows):
    for c in range(n_cols):
        col_pct = matrix.iloc[r, c]
        val = raw_values.iloc[r, c]
        col_label = matrix.columns[c]
        if "%" in col_label:
            txt = f"{val:.1f}%"
        else:
            txt = f"{val:.0f}"
        text_color = "white" if col_pct > 0.7 else COLORS["viti_dark"]
        ax.text(c, r, txt, ha="center", va="center",
                 fontsize=9, color=text_color,
                 fontweight="semibold" if col_pct > 0.5 else "regular",
                 zorder=3)

# Region labels left
ax.set_yticks(range(n_rows))
ax.set_yticklabels([])
for r, region in enumerate(matrix.index):
    is_exemplar = region in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
    rank = df.iloc[r]["SES composite rank (1=highest need)"]
    ax.text(-0.6, r, f"#{int(rank)}  {region}",
             ha="right", va="center",
             fontsize=10, color=color, fontweight=weight)

# Column labels top
ax.set_xticks(range(n_cols))
ax.set_xticklabels([])
for c, comp in enumerate(matrix.columns):
    ax.text(c, -0.7, comp,
             ha="center", va="bottom",
             fontsize=10, color=COLORS["viti_dark"],
             fontweight="semibold")

# Grid lines
ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="both", bottom=False, left=False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.xaxis.tick_top()

# Colorbar
cbar_ax = fig.add_axes([0.95, 0.15, 0.012, 0.45])
cbar = plt.colorbar(im, cax=cbar_ax)
cbar.outline.set_visible(False)
cbar.set_ticks([0, 0.5, 1.0])
cbar.set_ticklabels(["Lowest", "Median", "Highest"])
cbar.ax.tick_params(labelsize=8.5, length=0)
cbar.ax.set_title("Need\n(0–100%)",
                   fontsize=8.5, color=COLORS["viti_gray"],
                   fontweight="semibold", pad=10, loc="left")

# Title block
ax.figure.text(0.04, 0.92,
                "NATIONAL  ·  HEALTHCARE EQUITY DIMENSIONS  ·  21 REGIONS",
                fontsize=10, color=COLORS["viti_blue"],
                fontweight="semibold", va="top")
# Cyan accent rule
from matplotlib.lines import Line2D
rule = Line2D([0.04, 0.09], [0.91, 0.91], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.87,
          "Where each region's equity gap sits — by component, not just composite.",
          fontsize=15, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.82,
          "Cell colour = within-component need percentile across 21 regions. "
          "Cells annotated with the underlying value. Stockholm + Västerbotten highlighted as exemplars.",
          fontsize=10.5, color=COLORS["viti_dark"])

fig.text(0.04, 0.025,
          "Source: Workbook v30 \"Equity composite\". Components: foreign-born % (SCB 2024), "
          "post-secondary education 25–64 % (SCB 2024, inverted so lower = higher need), "
          "premature mortality 25–64 /100k age-standardised (Socialstyrelsen 2024), "
          "healthcare-amenable mortality /100k 3-yr MA.",
          fontsize=8, color=COLORS["viti_gray"])

plt.savefig(OUT / "N4_equity_dimensions.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N4_equity_dimensions.png'}")
