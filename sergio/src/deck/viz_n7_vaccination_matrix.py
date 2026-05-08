# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N7 — Sweden vaccination & coverage matrix.

21 regions × 5 indicators: MPR 2yo, HPV girls, plus Pfizer share in TBE,
RSV, and Pneumococcal classes. Surfaces preventive-care coverage gradient
+ Pfizer footprint in each vaccine class.

Output: delivery/figures/region_profiles/_overview/N7_vaccination_matrix.png
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load data
rm = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Region master")
vm = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Vaccine market share")

m = rm.merge(vm[["Region", "Share %", "Share %.1", "Share %.2"]],
              on="Region", how="left")
m = m.rename(columns={"Share %": "RSV Pfizer share %",
                       "Share %.1": "Pneu Pfizer share %",
                       "Share %.2": "TBE Pfizer share %"})
m["region_short"] = m["Region"].str.replace("Region ", "")
m["region_short"] = m["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})
# Sort by total Pfizer footprint rank (Stockholm at top)
pf = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Pfizer total footprint")
pf = pf.dropna(subset=["Region"])
pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
m = m.merge(pf[["Region", "Pfizer SEK rank"]], on="Region")
m = m.sort_values("Pfizer SEK rank").reset_index(drop=True)

EXEMPLARS = {"Stockholm", "Västerbotten"}

# Build matrix — values are percentages
columns = [
    ("MPR 2yo coverage",      "MPR 2yo %"),
    ("HPV girls coverage",    "HPV girls %"),
    ("TBE — Pfizer share",    "TBE Pfizer share %"),
    ("RSV — Pfizer share",    "RSV Pfizer share %"),
    ("Pneumococcal — Pfizer", "Pneu Pfizer share %"),
]

matrix = pd.DataFrame(index=m["region_short"])
for label, col in columns:
    matrix[label] = m[col].values

# Color scale: 0 to 100 (percent)
viti_cmap = LinearSegmentedColormap.from_list(
    "viti_blue_gradient",
    [(0.0, COLORS["viti_light"]),
     (0.30, COLORS["viti_medium"]),
     (0.65, COLORS["pfizer_blue"]),
     (1.0,  COLORS["competitor_charcoal"])],
)

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.16, right=0.91, top=0.66, bottom=0.10)
ax = fig.add_subplot(111)

n_rows, n_cols = matrix.shape

# Normalize each cell to 0-1 for colormap (cap at 100%)
norm_matrix = matrix / 100.0

im = ax.imshow(norm_matrix.values, cmap=viti_cmap, aspect="auto", vmin=0, vmax=1)

for r in range(n_rows):
    for c in range(n_cols):
        val = matrix.iloc[r, c]
        if pd.isna(val):
            continue
        col_pct = norm_matrix.iloc[r, c]
        text_color = "white" if col_pct > 0.55 else COLORS["viti_dark"]
        ax.text(c, r, f"{val:.0f}%", ha="center", va="center",
                 fontsize=9, color=text_color,
                 fontweight="semibold" if col_pct > 0.5 else "regular",
                 zorder=3)

# Region labels
ax.set_yticks(range(n_rows))
ax.set_yticklabels([])
for r, region in enumerate(matrix.index):
    is_exemplar = region in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
    ax.text(-0.6, r, region, ha="right", va="center",
             fontsize=10, color=color, fontweight=weight)

# Column labels
ax.set_xticks(range(n_cols))
ax.set_xticklabels([])
for c, label in enumerate(matrix.columns):
    ax.text(c, -0.7, label,
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
cbar.set_ticklabels(["0%", "50%", "100%"])
cbar.ax.tick_params(labelsize=8.5, length=0)
cbar.ax.set_title("Coverage\nor share",
                   fontsize=8.5, color=COLORS["viti_gray"],
                   fontweight="semibold", pad=10, loc="left")

# Title block
fig.text(0.04, 0.92,
          "NATIONAL  ·  VACCINATION COVERAGE & PFIZER SHARE  ·  21 REGIONS",
          fontsize=10, color=COLORS["viti_blue"],
          fontweight="semibold")
rule = Line2D([0.04, 0.09], [0.91, 0.91], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.86,
          "Childhood coverage holds; adult Pfizer share varies by class.",
          fontsize=15, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.82,
          "MPR + HPV are population baseline coverage. TBE / RSV / Pneumococcal columns show Pfizer share of each adult-vaccine class. "
          "Sorted by total Pfizer SEK rank.",
          fontsize=10, color=COLORS["viti_dark"])

fig.text(0.04, 0.025,
          "Source: Folkhälsomyndigheten Vaccination Coverage 2024 (MPR, HPV); "
          "IQVIA Sell-In SEK 3-year aggregate (Apr 2023–Mar 2026) ÷ class total for Pfizer-share columns. "
          "Some regions had insufficient TBE/RSV market data for share calc — shown blank.",
          fontsize=8, color=COLORS["viti_gray"])

plt.savefig(OUT / "N7_vaccination_matrix.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N7_vaccination_matrix.png'}")
