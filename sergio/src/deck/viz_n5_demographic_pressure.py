# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N5 — Sweden demographic pressure: 65+ growth 2024→2040.

21 regions ranked by 65+ growth percentage. Each row shows current 65+
share and projected 2040 share. Surfaces where Pfizer's adult-vaccine
demographic tailwind is strongest.

Output: delivery/figures/region_profiles/_overview/N5_demographic_pressure.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load Population projections
df = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Population projections")

# Ensure required cols + compute current 65+ share
df["65+ share 2024 %"] = df["65+ 2024"] / df["Pop 2024"] * 100
df["65+ share 2040 %"] = df["65+ 2040"] / df["Pop 2040"] * 100
df = df.sort_values("65+ growth % 2024→2040", ascending=False).reset_index(drop=True)

df["region_short"] = df["Region"].str.replace("Region ", "")
df["region_short"] = df["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})

EXEMPLARS = {"Stockholm", "Västerbotten"}

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.13, right=0.96, top=0.74, bottom=0.10)
ax = fig.add_subplot(111)

n = len(df)
y_pos = list(range(n))

max_growth = df["65+ growth % 2024→2040"].max()

# Compute color by growth tier
def color_for(growth):
    if growth >= 25:
        return COLORS["pfizer_blue"]    # strongest tailwind
    if growth >= 15:
        return COLORS["competitor_charcoal"]
    if growth >= 5:
        return COLORS["competitor_gray"]
    return COLORS["viti_medium"]

colors = [color_for(g) for g in df["65+ growth % 2024→2040"]]
bars = ax.barh(y_pos, df["65+ growth % 2024→2040"],
                color=colors, edgecolor="white",
                linewidth=0.8, height=0.7)

# Highlight exemplars
for i, region in enumerate(df["region_short"]):
    if region in EXEMPLARS:
        bars[i].set_edgecolor(COLORS["pfizer_blue"])
        bars[i].set_linewidth(2.2)

# Y axis labels
for i, region in enumerate(df["region_short"]):
    is_exemplar = region in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
    ax.text(-1.5, i, region,
             ha="right", va="center",
             fontsize=10, color=color, fontweight=weight)

# Bar end labels: growth %, current 65+ share, projected 65+ share
for i, row in df.iterrows():
    growth = row["65+ growth % 2024→2040"]
    cur = row["65+ share 2024 %"]
    proj = row["65+ share 2040 %"]
    ax.text(growth + 0.5, i,
             f"+{growth:.0f}%",
             ha="left", va="center",
             fontsize=10.5, color=COLORS["viti_dark"],
             fontweight="bold")
    ax.text(growth + 5.5, i,
             f"{cur:.1f}%  →  {proj:.1f}%  share 65+",
             ha="left", va="center",
             fontsize=9, color=COLORS["viti_gray"])

ax.invert_yaxis()
ax.set_yticks([])
ax.set_xlim(0, max_growth + 22)
ax.set_xticks([0, 10, 20, 30])
ax.set_xticklabels(["0%", "10%", "20%", "30%"])
ax.set_xlabel("")
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(COLORS["viti_gray"])
ax.spines["bottom"].set_linewidth(0.6)
ax.tick_params(axis="x", which="both", length=0, colors=COLORS["viti_gray"])
ax.grid(axis="x", alpha=0.25)
ax.set_axisbelow(True)

# Title block
fig.text(0.04, 0.94,
          "NATIONAL  ·  DEMOGRAPHIC PRESSURE  ·  21 REGIONS",
          fontsize=10, color=COLORS["viti_blue"],
          fontweight="semibold")
rule = Line2D([0.04, 0.09], [0.93, 0.93], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.88,
          "65+ population growth 2024–2040 highest in Stockholm, Uppsala, Halland.",
          fontsize=15, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.83,
          "Higher 65+ growth supports stronger demand for adult vaccines (Abrysvo, Prevenar 20) and ATTR therapy (Vyndaqel). "
          "Stockholm +35%; Västerbotten +10%.",
          fontsize=10.5, color=COLORS["viti_dark"])

fig.text(0.04, 0.025,
          "Source: SCB Population Projections (2024–2050). 65+ growth = (65+ pop 2040 − 65+ pop 2024) / 65+ pop 2024 × 100. "
          "Bands: blue ≥25% (strongest), charcoal 15–25%, gray 5–15%, light <5%.",
          fontsize=8, color=COLORS["viti_gray"])

plt.savefig(OUT / "N5_demographic_pressure.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N5_demographic_pressure.png'}")
