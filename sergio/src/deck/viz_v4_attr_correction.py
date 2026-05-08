# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V4 — ATTR-PN vs ATTR-CM correction (deck slide 5).

The W2 correction in one figure: Norrland's Vyndaqel cornerstone is in ATTR-PN
(hereditary polyneuropathy, V30M founder cluster), not ATTR-CM (cardiomyopathy)
as earlier docs framed it. Norrland over-indexes 758× on PN but sits below the
Sweden mean on CM.

Output: delivery/figures/deck/V4_attr_pn_vs_cm.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, style_axes,
                         add_title_block, add_source_line, add_accent_rule)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

# Per-100k values from W2 drilldown (last 6mo, total ATTR-PN = DG1+DG2 across
# all drugs; total ATTR-CM = DG3 across all drugs)
data = pd.DataFrame({
    "region": ["Norrland", "Stockholm Sörmland", "Mellansverige",
               "VGR", "Södra", "Sydöstra"],
    "pn_per100k": [25.01, 1.53, 1.04, 0.79, 0.77, 0.54],
    "cm_per100k": [1.61, 1.77, 1.66, 1.15, 2.63, 2.83],
})

# Sweden means (computed by population-weighted sum / total pop)
POPULATIONS = {
    "Norrland": 902, "Stockholm Sörmland": 2809, "Mellansverige": 1849,
    "VGR": 1767, "Södra": 2124, "Sydöstra": 1088,
}
data["pop"] = data["region"].map(POPULATIONS)

pn_total_count = (data["pn_per100k"] * data["pop"] / 100).sum()
cm_total_count = (data["cm_per100k"] * data["pop"] / 100).sum()
total_pop = data["pop"].sum()
sweden_pn_mean = pn_total_count / total_pop * 100
sweden_cm_mean = cm_total_count / total_pop * 100

data["pn_index"] = data["pn_per100k"] / sweden_pn_mean * 100
data["cm_index"] = data["cm_per100k"] / sweden_cm_mean * 100

# Sort by PN per-100k descending for the PN panel
print(f"Sweden PN per-100k mean: {sweden_pn_mean:.2f}")
print(f"Sweden CM per-100k mean: {sweden_cm_mean:.2f}")
print(data.to_string(index=False))

# ---------------------------------------------------------------------------
# Figure: two panels
# ---------------------------------------------------------------------------
fig, (ax_pn, ax_cm) = plt.subplots(1, 2, figsize=(13, 6.4),
                                     gridspec_kw={"wspace": 0.25})
fig.subplots_adjust(left=0.08, right=0.96, top=0.66, bottom=0.13)

NORRLAND = "Norrland"

def color_for(region):
    return COLORS["pfizer_blue"] if region == NORRLAND else COLORS["competitor_gray"]

# PN panel — sort descending by PN per-100k
pn_sorted = data.sort_values("pn_per100k", ascending=True)  # asc for horiz bar (top = highest)
ax_pn.barh(pn_sorted["region"], pn_sorted["pn_per100k"],
            color=[color_for(r) for r in pn_sorted["region"]],
            edgecolor="white", linewidth=1.5, height=0.62)

# Sweden mean reference line
ax_pn.axvline(sweden_pn_mean, color=COLORS["viti_gray"],
               lw=0.9, ls=(0, (4, 4)), alpha=0.7, zorder=1)
ax_pn.text(sweden_pn_mean, len(pn_sorted) - 0.3,
            f"Sweden\n{sweden_pn_mean:.2f}",
            ha="left", va="bottom",
            color=COLORS["viti_gray"], fontsize=8.5, alpha=0.85)

# Value labels at end of each bar
for i, (_, row) in enumerate(pn_sorted.iterrows()):
    color = COLORS["pfizer_blue"] if row["region"] == NORRLAND else COLORS["viti_gray"]
    weight = "bold" if row["region"] == NORRLAND else "regular"
    multiplier = row["pn_index"] / 100
    label = f"  {row['pn_per100k']:.1f}"
    if row["region"] == NORRLAND:
        label += f"     {multiplier:.1f}× Sweden mean"
    ax_pn.text(row["pn_per100k"], i, label,
                ha="left", va="center",
                color=color, fontsize=10, fontweight=weight)

ax_pn.set_xlim(0, 33)
ax_pn.set_xlabel("ATTR-PN patients per 100,000 inhabitants",
                  fontsize=10, color=COLORS["viti_dark"])
ax_pn.set_title("ATTR-PN  (DG1 + DG2, V30M founder territory)",
                 fontsize=11.5, color=COLORS["pfizer_blue"],
                 fontweight="semibold", loc="left", pad=10)
style_axes(ax_pn, hide_x_grid=True)
ax_pn.grid(True, axis="x", alpha=0.25)
ax_pn.tick_params(axis="y", labelsize=10)

# CM panel — sort descending by CM per-100k
cm_sorted = data.sort_values("cm_per100k", ascending=True)
ax_cm.barh(cm_sorted["region"], cm_sorted["cm_per100k"],
            color=[color_for(r) for r in cm_sorted["region"]],
            edgecolor="white", linewidth=1.5, height=0.62)

ax_cm.axvline(sweden_cm_mean, color=COLORS["viti_gray"],
               lw=0.9, ls=(0, (4, 4)), alpha=0.7, zorder=1)
ax_cm.text(sweden_cm_mean, len(cm_sorted) - 0.3,
            f"Sweden\n{sweden_cm_mean:.2f}",
            ha="left", va="bottom",
            color=COLORS["viti_gray"], fontsize=8.5, alpha=0.85)

for i, (_, row) in enumerate(cm_sorted.iterrows()):
    color = COLORS["pfizer_blue"] if row["region"] == NORRLAND else COLORS["viti_gray"]
    weight = "bold" if row["region"] == NORRLAND else "regular"
    multiplier = row["cm_index"] / 100
    label = f"  {row['cm_per100k']:.1f}"
    if row["region"] == NORRLAND:
        label += f"     {multiplier:.2f}× Sweden mean"
    ax_cm.text(row["cm_per100k"], i, label,
                ha="left", va="center",
                color=color, fontsize=10, fontweight=weight)

ax_cm.set_xlim(0, 3.5)
ax_cm.set_xlabel("ATTR-CM patients per 100,000 inhabitants",
                  fontsize=10, color=COLORS["viti_dark"])
ax_cm.set_title("ATTR-CM  (DG3, cardiomyopathy)",
                 fontsize=11.5, color=COLORS["viti_dark"],
                 fontweight="semibold", loc="left", pad=10)
style_axes(ax_cm, hide_x_grid=True)
ax_cm.grid(True, axis="x", alpha=0.25)
ax_cm.tick_params(axis="y", labelsize=10)

# Title block
add_accent_rule(fig, x=0.06, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="P1 ATTR CORNERSTONE · CORRECTION · AVA LAST 6 MO",
    headline="Norrland's cornerstone is ATTR-PN, not ATTR-CM.",
    takeaway="Norrland over-indexes 8× on the hereditary polyneuropathy cluster but sits below the Sweden mean on cardiomyopathy. The Hympavzi + Elrexfio carry-in thesis stands — operational frame shifts from cardiology to rare-disease specialty centre.",
    x=0.06, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
    takeaway_width=110, takeaway_line_step=0.030,
)

add_source_line(fig,
                "Source: AVA patient-level data, Vyndaqel + Amvuttra + Beyonttra + Diflunisal across Diagnosgrupp 1/2/3 (DG1+2 = ATTR-PN total, DG3 = ATTR-CM). "
                "Window: last 6 months Aug 2025–Jan 2026. Per-100k normalised by sjukvårdsregion population.",
                x=0.06, y=0.04)

plt.savefig(OUT / "V4_attr_pn_vs_cm.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V4_attr_pn_vs_cm.png'}")
