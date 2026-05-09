# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N6 — Sweden disease burden composite.

21 regions × 5 burden indicators: breast / prostate / lung cancer rates,
MI incidence, heart care quality (inverted so lower quality = higher need).

Output: delivery/figures/region_profiles/_overview/N6_disease_burden.png
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

df = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Region master")
df["region_short"] = df["Region"].str.replace("Region ", "")
df["region_short"] = df["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})

EXEMPLARS = {"Stockholm", "Västerbotten"}

components = {
    "Breast cancer /100k":     ("Breast ca rate /100k",      False),
    "Prostate cancer /100k":   ("Prostate ca rate /100k",    False),
    "Lung cancer /100k":       ("Lung ca incidence /100k",   False),
    "MI incidence /100k":      ("MI incidence /100k",        False),
    "Heart care quality":      ("Heart care quality (0-100)", True),  # invert (lower=worse)
}

# Build composite need score: average of percentile-need ranks
matrix = pd.DataFrame(index=df["region_short"])
raw = pd.DataFrame(index=df["region_short"])
for label, (col, invert) in components.items():
    s = df[col].values
    raw[label] = s
    if invert:
        ranked = pd.Series(s).rank(pct=True, ascending=False).values
    else:
        ranked = pd.Series(s).rank(pct=True, ascending=True).values
    matrix[label] = ranked

# Composite = simple mean
df["composite_need"] = matrix.mean(axis=1).values
df = df.sort_values("composite_need", ascending=False).reset_index(drop=True)

# Re-order matrix + raw to match new sort
matrix = matrix.reindex(df["region_short"])
raw = raw.reindex(df["region_short"])

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
fig.subplots_adjust(left=0.16, right=0.91, top=0.66, bottom=0.10)
ax = fig.add_subplot(111)

n_rows, n_cols = matrix.shape

im = ax.imshow(matrix.values, cmap=need_cmap, aspect="auto", vmin=0, vmax=1)

for r in range(n_rows):
    for c in range(n_cols):
        col_pct = matrix.iloc[r, c]
        val = raw.iloc[r, c]
        col_label = matrix.columns[c]
        if "quality" in col_label.lower():
            txt = f"{val:.0f}"
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
    ax.text(-0.6, r, region, ha="right", va="center",
             fontsize=10, color=color, fontweight=weight)

# Column labels top
ax.set_xticks(range(n_cols))
ax.set_xticklabels([])
for c, comp in enumerate(matrix.columns):
    ax.text(c, -0.7, comp,
             ha="center", va="bottom",
             fontsize=10, color=COLORS["viti_dark"],
             fontweight="semibold")

ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="both", bottom=False, left=False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.xaxis.tick_top()

# Colorbar
cbar_ax = fig.add_axes([0.92, 0.15, 0.012, 0.45])
cbar = plt.colorbar(im, cax=cbar_ax)
cbar.outline.set_visible(False)
cbar.set_ticks([0, 0.5, 1.0])
cbar.set_ticklabels(["Lowest", "Median", "Highest"])
cbar.ax.tick_params(labelsize=8.5, length=0)
cbar.ax.set_title("Need\n(0–100%)",
                   fontsize=8.5, color=COLORS["viti_gray"],
                   fontweight="semibold", pad=10, loc="left")

# Title block
fig.text(0.04, 0.92,
          "NATIONAL  ·  DISEASE BURDEN COMPOSITE  ·  21 REGIONS  ×  5 INDICATORS",
          fontsize=10, color=COLORS["viti_blue"],
          fontweight="semibold")
rule = Line2D([0.04, 0.09], [0.91, 0.91], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.86,
          "Cancer + cardiovascular burden ranked across 21 regions.",
          fontsize=15, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.82,
          "Sorted by composite-need score (mean of within-indicator percentile ranks). "
          "Cell colour = within-indicator need percentile. Heart care quality inverted: lower score = higher need.",
          fontsize=10, color=COLORS["viti_dark"])

fig.text(0.04, 0.025,
          "Source: Region master sheet, Workbook v30. Cancer incidence = Socialstyrelsen Cancer Register (2024); "
          "MI incidence = Riksstroke + Socialstyrelsen patientregister (2024); Heart care quality = Kolada (2024).",
          fontsize=8, color=COLORS["viti_gray"])

plt.savefig(OUT / "N6_disease_burden.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N6_disease_burden.png'}")
