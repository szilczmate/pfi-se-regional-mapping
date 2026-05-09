# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N9 — Equity gradient × solidarity-funded Pfizer specialty SEK per 100k.

Connects two prime-directive layers:
  - Equity composite (foreign-born + education + premature mortality + HC-amenable)
  - Solidarity-eligible Pfizer specialty products

Sweden's solidarisk finansiering reimburses 85–90% of regional spend above the
national average for "highly uneven patient distribution + expensive" specialty
drugs. Pfizer's rare-disease + specialty oncology portfolio (Vyndaqel,
Elrexfio, Lorviqua, Tukysa, Talzenna, BeneFIX/Refacto haemophilia products) is
the qualifying class.

The strategic insight: high-equity-need regions are structurally FAVORED for
this Pfizer portfolio — the state co-funds the expensive end via the equity
mechanism.

Output: delivery/figures/region_profiles/_overview/N9_equity_solidarity_pfizer.png
"""

from pathlib import Path
import sys
import numpy as np
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

# Solidarity-eligible Pfizer products: rare-disease + expensive specialty,
# highly uneven patient distribution. From Pfizer total footprint sheet.
SOLIDARITY_PRODUCTS = [
    "VYNDAQEL SEK (3yr)",       # ATTR rare disease
    "ELREXFIO SEK (3yr)",       # myeloma 4L
    "LORVIQUA SEK (3yr)",       # ALK+ NSCLC (~5%)
    "TUKYSA SEK (3yr)",         # HER2+ brain mets
    "TALZENNA SEK (3yr)",       # BRCA mCRPC
    "BENEFIX SEK (3yr)",        # haemophilia
    "REFACTO AF SEK (3yr)",     # haemophilia
]

# Load
eq = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Equity composite")
pf = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Pfizer total footprint")
pf = pf.dropna(subset=["Region"])
pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]

# Aggregate solidarity SEK per region
pf["solidarity_3yr"] = pf[SOLIDARITY_PRODUCTS].sum(axis=1)
pf["solidarity_per100k"] = pf["solidarity_3yr"] / pf["Population"] * 100000

# Merge with equity rank
m = eq.merge(pf[["Region", "solidarity_3yr", "solidarity_per100k", "Population"]],
              on="Region", how="left")
m["region_short"] = m["Region"].str.replace("Region ", "")
m["region_short"] = m["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})
m = m.rename(columns={"SES composite rank (1=highest need)": "equity_rank"})

# Solidarity tier band by equity rank quartile
def tier_color(rank):
    if rank <= 6:    return COLORS["highlight_amber"]      # highest need
    if rank <= 11:   return COLORS["competitor_charcoal"]
    if rank <= 16:   return COLORS["competitor_gray"]
    return COLORS["pfizer_blue"]                            # lowest need (best equity)

m["color"] = m["equity_rank"].apply(tier_color)

# National solidarity SEK per 100k (Sweden total / Sweden pop)
nat_solidarity = m["solidarity_3yr"].sum() / m["Population"].sum() * 100000

EXEMPLARS = {"Stockholm", "Västerbotten"}

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.08, right=0.92, top=0.66, bottom=0.18)
ax = fig.add_subplot(111)

# Bubble sizing — population scaled
size_min, size_max = 80, 1200
sizes = (m["Population"] - m["Population"].min()) / (m["Population"].max() - m["Population"].min())
sizes = sizes ** 0.6 * (size_max - size_min) + size_min

# Y values in M kr per 100k (1e6 SEK = 1 M kr)
m["y_val"] = m["solidarity_per100k"] / 1e6
nat_y = nat_solidarity / 1e6

# Scatter
for _, row in m.iterrows():
    ax.scatter(row["equity_rank"], row["y_val"],
                s=sizes[m.index[m["region_short"] == row["region_short"]][0]],
                c=row["color"], alpha=0.78,
                edgecolors="white", linewidths=1.2, zorder=3)

# National reference line
ax.axhline(nat_y, color=COLORS["viti_gray"],
           lw=0.9, ls=(0, (4, 4)), alpha=0.7, zorder=1)
ax.text(21.4, nat_y,
         f"  Sweden mean\n  {nat_y:.0f}M kr / 100k",
         ha="left", va="center",
         color=COLORS["viti_gray"], fontsize=8.5, alpha=0.85)

# Annotate exemplars + outliers
def annotate_pt(ax, row, dx=12, dy=10, color=None, weight="bold", fs=10):
    ax.annotate(row["region_short"],
                 xy=(row["equity_rank"], row["y_val"]),
                 xytext=(dx, dy), textcoords="offset points",
                 fontsize=fs, color=color or COLORS["pfizer_blue"],
                 fontweight=weight)

# Always label exemplars (Pfizer blue, bold)
for _, row in m[m["region_short"].isin(EXEMPLARS)].iterrows():
    annotate_pt(ax, row, dx=10, dy=10)

# Label top 3 by solidarity per100k (charcoal, semibold)
top_solid = m.nlargest(3, "solidarity_per100k")
for _, row in top_solid.iterrows():
    if row["region_short"] not in EXEMPLARS:
        annotate_pt(ax, row, dx=10, dy=-3, color=COLORS["viti_dark"], weight="semibold")

# Highlight high-need + low-solidarity (the OPPORTUNITY regions): amber
for _, row in m.iterrows():
    if (row["equity_rank"] <= 5 and
        row["y_val"] < nat_y * 0.55 and
        row["region_short"] not in EXEMPLARS):
        annotate_pt(ax, row, dx=8, dy=-12, color=COLORS["highlight_amber"],
                     weight="semibold", fs=9)

# Quadrant tints
ymax_val = m["y_val"].max() * 1.15
# Funding-aligned: high need (left) + above-mean SEK (upper)
ax.axvspan(0.5, 6.5, ymin=nat_y / ymax_val, ymax=1.0,
            color=COLORS["pfizer_blue"], alpha=0.06, zorder=0)
# Opportunity: high need (left) + below-mean SEK (lower)
ax.axvspan(0.5, 6.5, ymin=0, ymax=nat_y / ymax_val,
            color=COLORS["highlight_amber"], alpha=0.06, zorder=0)

# Quadrant labels — placed in the upper-left of each tinted region to stay
# clear of the data points
ax.text(1.0, ymax_val * 0.96,
         "FUNDING-ALIGNED",
         ha="left", va="top",
         fontsize=10, color=COLORS["pfizer_blue"], fontweight="bold",
         alpha=0.90, zorder=2)

ax.text(1.0, nat_y * 0.95,
         "OPPORTUNITY",
         ha="left", va="top",
         fontsize=10, color=COLORS["highlight_amber"], fontweight="bold",
         alpha=0.90, zorder=2)

# Polish
ax.set_xlim(0.3, 22.5)
ax.set_ylim(0, ymax_val)
ax.set_xticks([1, 6, 11, 16, 21])
ax.set_xticklabels(["#1\nhighest need", "#6", "#11", "#16", "#21\nbest equity"],
                    fontsize=9, color=COLORS["viti_dark"])
ax.set_xlabel("Equity composite rank (1 = highest need)",
               fontsize=10, color=COLORS["viti_dark"])
ax.set_ylabel("Solidarity-eligible Pfizer SEK per 100k inhabitants (M kr, 3-year)",
               fontsize=10, color=COLORS["viti_dark"])
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color(COLORS["viti_gray"])
ax.spines["bottom"].set_color(COLORS["viti_gray"])
ax.tick_params(which="both", length=0)
ax.grid(True, axis="both", alpha=0.20, zorder=0)

# Legend (need tiers + bubble size)
legend_handles = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["highlight_amber"], markersize=11,
           markeredgecolor="white", markeredgewidth=1, label="Highest need (#1–6)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["competitor_charcoal"], markersize=11,
           markeredgecolor="white", markeredgewidth=1, label="High need (#7–11)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["competitor_gray"], markersize=11,
           markeredgecolor="white", markeredgewidth=1, label="Moderate (#12–16)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["pfizer_blue"], markersize=11,
           markeredgecolor="white", markeredgewidth=1, label="Best equity (#17–21)"),
]
leg = ax.legend(handles=legend_handles, loc="upper right",
                 frameon=False, fontsize=9, labelspacing=0.6,
                 borderpad=0.5)
for t in leg.get_texts():
    t.set_color(COLORS["viti_dark"])
ax.text(21.7, ax.get_ylim()[1] * 0.50, "Bubble size = population",
         fontsize=8.5, color=COLORS["viti_gray"], ha="right", va="bottom")

# Title block
fig.text(0.04, 0.92,
          "NATIONAL  ·  EQUITY × SOLIDARITY-FUNDED PFIZER SPECIALTY  ·  21 REGIONS",
          fontsize=10, color=COLORS["viti_blue"],
          fontweight="semibold")
rule = Line2D([0.04, 0.09], [0.91, 0.91], transform=fig.transFigure,
               color=COLORS["viti_cyan"], linewidth=1.5)
fig.add_artist(rule)
fig.text(0.04, 0.86,
          "Sweden's solidarisk finansiering co-funds the expensive end of the Pfizer portfolio.",
          fontsize=15, color=COLORS["viti_dark"],
          fontweight="bold")
fig.text(0.04, 0.81,
          "Highly uneven specialty drugs above the regional cost threshold are state-reimbursed at 85–90%. "
          "Pfizer's rare-disease + specialty oncology portfolio is the qualifying class. "
          "Bubbles toward the upper-left = high-need regions where Pfizer specialty SEK already concentrates.",
          fontsize=10, color=COLORS["viti_dark"])

# Mechanism explanation (above source line)
fig.text(0.04, 0.052,
          "Mechanism: NT-rådet/NSG specialty-drug solidarisk finansiering. Threshold: regional spend > 30 SEK/capita above the national average. "
          "Reimbursement: 85% to tier 2, 90% above. Eligible Pfizer products counted: Vyndaqel, Elrexfio, Lorviqua, Tukysa, Talzenna, BeneFIX, Refacto AF.",
          fontsize=8, color=COLORS["viti_dark"])
fig.text(0.04, 0.020,
          "Sources: SKR \"Kostnadsutjämning + Solidariskt finansierade läkemedel\" (skr.se); NT-rådet beslutsdatabas + NSG Läkemedel samverkansdokument "
          "(samverkanlakemedel.se); TLV beslutsdatabas (tlv.se); Riksrevisionen RIR 2022:8; Statskontoret 2022:23; Workbook v30 \"Pfizer total footprint\" + "
          "\"Equity composite\".",
          fontsize=7.5, color=COLORS["viti_gray"])

plt.savefig(OUT / "N9_equity_solidarity_pfizer.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N9_equity_solidarity_pfizer.png'}")
