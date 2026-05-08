# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N8 — Sweden Pfizer category mix across 21 regions.

Stacked horizontal bars: 21 regions × Vaccines / RD-IM / Oncology shares of
total Pfizer 3-year SEK. Surfaces the DIFFERENT shape of Pfizer's footprint
in each region — Norrland RDIM-dominated (Vyndaqel), Stockholm balanced.

Output: delivery/figures/region_profiles/_overview/N8_pfizer_category_mix.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load Pfizer footprint
pf = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Pfizer total footprint")
pf = pf.dropna(subset=["Region"])
pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
pf["region_short"] = pf["Region"].str.replace("Region ", "")
pf["region_short"] = pf["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})

# Compute category percentages
pf["vac_pct"] = pf["Vaccines SEK"] / pf["Total Pfizer SEK"] * 100
pf["rdim_pct"] = pf["RD/IM SEK"] / pf["Total Pfizer SEK"] * 100
pf["onco_pct"] = pf["Oncology SEK"] / pf["Total Pfizer SEK"] * 100

# Sort by Pfizer SEK rank
pf = pf.sort_values("Pfizer SEK rank").reset_index(drop=True)

EXEMPLARS = {"Stockholm", "Västerbotten"}

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.18, right=0.95, top=0.71, bottom=0.10)
ax = fig.add_subplot(111)

n = len(pf)
y_pos = list(range(n))

cumulative = [0] * n
cats = [
    ("Vaccines", "vac_pct",  COLORS["pfizer_blue"]),
    ("RD / IM",  "rdim_pct", COLORS["competitor_charcoal"]),
    ("Oncology", "onco_pct", COLORS["competitor_gray"]),
]
for name, col, color in cats:
    values = pf[col].tolist()
    ax.barh(y_pos, values, left=cumulative,
             color=color, edgecolor="white",
             linewidth=1.5, height=0.7)
    # Inline labels
    for i, (val, cum) in enumerate(zip(values, cumulative)):
        if val >= 8:
            text_color = "white" if name != "Oncology" else COLORS["viti_dark"]
            weight = "bold" if name == "Vaccines" else "regular"
            ax.text(cum + val / 2, i, f"{int(val)}%",
                     ha="center", va="center",
                     fontsize=9, color=text_color, fontweight=weight)
    cumulative = [c + v for c, v in zip(cumulative, values)]

# Region labels
ax.set_yticks(y_pos)
ax.set_yticklabels([])
for i, row in pf.iterrows():
    region = row["region_short"]
    is_exemplar = region in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
    ax.text(-2, i,
             f"#{int(row['Pfizer SEK rank'])}  {region}",
             ha="right", va="center",
             fontsize=10, color=color, fontweight=weight)

# Total Pfizer SEK on the right
for i, row in pf.iterrows():
    sek_m = row["Total Pfizer SEK"] / 1e6
    ax.text(102, i, f"{sek_m:,.0f}M kr",
             ha="left", va="center",
             fontsize=10, color=COLORS["viti_gray"])

ax.invert_yaxis()
ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(COLORS["viti_gray"])
ax.spines["bottom"].set_linewidth(0.6)
ax.tick_params(axis="x", which="both", length=0, colors=COLORS["viti_gray"])
ax.grid(False)

# Legend
legend_handles = [
    Rectangle((0, 0), 1, 1, color=COLORS["pfizer_blue"]),
    Rectangle((0, 0), 1, 1, color=COLORS["competitor_charcoal"]),
    Rectangle((0, 0), 1, 1, color=COLORS["competitor_gray"]),
]
leg = ax.legend(legend_handles, ["Vaccines", "RD / IM", "Oncology"],
                 loc="upper left", bbox_to_anchor=(0.0, 1.07),
                 ncol=3, frameon=False, fontsize=10,
                 handlelength=1.2, handletextpad=0.6, columnspacing=2.0)
for t in leg.get_texts():
    t.set_color(COLORS["viti_dark"])

# Title block
fig.text(0.04, 0.94,
          "NATIONAL  ·  PFIZER PORTFOLIO MIX  ·  21 REGIONS",
          fontsize=10, color=COLORS["viti_blue"],
          fontweight="semibold")
rule = Line2D([0.04, 0.09], [0.93, 0.93], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.88,
          "Pfizer category mix varies by region — Norrland RD/IM-dominated; southern regions more balanced.",
          fontsize=14, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.83,
          "Each row = total Pfizer 3-year Sell-In SEK, split by category. Sorted by Pfizer SEK rank. "
          "Total in M kr shown on the right.",
          fontsize=10, color=COLORS["viti_dark"])

fig.text(0.04, 0.025,
          "Source: IQVIA Sell-In SEK monthly Apr 2023–Mar 2026, aggregated by Pfizer category. "
          "Categories: Vaccines (Abrysvo, Prevenar, FSME-IMMUN), RD/IM (Vyndaqel, Vydura, BeneFIX, Refacto, Paxlovid), "
          "Oncology (Xtandi, Ibrance, Elrexfio, Lorviqua, Tukysa, Talzenna).",
          fontsize=8, color=COLORS["viti_gray"])

plt.savefig(OUT / "N8_pfizer_category_mix.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N8_pfizer_category_mix.png'}")
