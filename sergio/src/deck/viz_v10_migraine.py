# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V10 — Migraine class lead (deck slide 11).

Vydura is the dominant first-line oral gepant in 20 of 21 regions. Uppsala is
the lone outlier where Atogepant leads — Akademiska prescribing-preference
structural anomaly.

Output: delivery/figures/deck/V10_migraine_class_lead.png
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
INTERIM = ROOT / "working" / "data" / "interim"
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

regional = pd.read_csv(INTERIM / "ava_w3b_first_drug_by_region.csv")
slope = pd.read_csv(INTERIM / "ava_w3_migraine_sweden_slope.csv")
print(regional.head(8))

# Sort regions by total volume for top 12
top = regional.nlargest(12, "Total").copy()
top = top.sort_values("Vydura_first_pct", ascending=True)

# ---------------------------------------------------------------------------
# Figure: ranked bars left, class growth side panel right
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 6.4))
gs = fig.add_gridspec(1, 5, left=0.08, right=0.97,
                       top=0.74, bottom=0.10,
                       wspace=0.10)
ax = fig.add_subplot(gs[0, :3])
ax_panel = fig.add_subplot(gs[0, 3:])
ax_panel.axis("off")

UPPSALA = "Uppsala"
def color_for(region):
    if region == UPPSALA:
        return COLORS["highlight_amber"]
    return COLORS["pfizer_blue"]

# Bars: each region's Vydura first-drug %
ax.barh(top["region"], top["Vydura_first_pct"],
        color=[color_for(r) for r in top["region"]],
        edgecolor="white", linewidth=1.5, height=0.62)

# Atogepant share as a faint backdrop (showing what's NOT Vydura)
for i, (_, row) in enumerate(top.iterrows()):
    ax.text(row["Vydura_first_pct"] + 1.2, i, f"{row['Vydura_first_pct']:.0f}%",
            ha="left", va="center",
            color=color_for(row["region"]),
            fontsize=10, fontweight="semibold")

# National 75% reference
NATIONAL_VYDURA_FIRST = 75.0
ax.axvline(NATIONAL_VYDURA_FIRST, color=COLORS["viti_gray"],
           lw=0.9, ls=(0, (4, 4)), alpha=0.7, zorder=1)
ax.text(NATIONAL_VYDURA_FIRST, len(top) - 0.3,
        f"  Sweden\n  {NATIONAL_VYDURA_FIRST:.0f}%",
        ha="left", va="bottom",
        color=COLORS["viti_gray"], fontsize=8.5, alpha=0.85)

# Uppsala callout
ax.annotate("Uppsala anomaly:\nAtogepant first in 56%",
             xy=(top.set_index("region").loc["Uppsala", "Vydura_first_pct"],
                 list(top["region"]).index("Uppsala")),
             xytext=(60, -10), textcoords="offset points",
             ha="left", va="center",
             color=COLORS["highlight_amber"], fontsize=9.5,
             fontweight="semibold",
             arrowprops=dict(arrowstyle="-",
                              color=COLORS["highlight_amber"],
                              lw=0.8, alpha=0.6))

ax.set_xlim(0, 100)
ax.set_xlabel("Vydura share of first-line oral gepant patients, AVA 2022–2026 (%)",
              fontsize=10, color=COLORS["viti_dark"])
style_axes(ax, hide_x_grid=True)
ax.grid(True, axis="x", alpha=0.25)
ax.tick_params(axis="y", labelsize=10)

# ---------------------------------------------------------------------------
# Right panel: national class metrics
# ---------------------------------------------------------------------------
ax_panel.text(0.04, 0.97, "NATIONAL CLASS METRICS",
               transform=ax_panel.transAxes,
               fontsize=10, fontweight="bold",
               color=COLORS["pfizer_blue"], va="top")
ax_panel.text(0.04, 0.92, "AVA last-6 vs prev-6",
               transform=ax_panel.transAxes,
               fontsize=8.5, color=COLORS["viti_gray"], va="top")

# Vydura PWD growth
vydura_pwd = slope[slope["drug"] == "Vydura"].iloc[0]
ato_pwd = slope[slope["drug"] == "Atogepant"].iloc[0]

stats = [
    ("Vydura PWD", f"+{vydura_pwd['PWD_pct']:.0f}%", "1,314 patients/mo"),
    ("Atogepant PWD", f"+{ato_pwd['PWD_pct']:.0f}%", "715 patients/mo"),
    ("Vydura new starts", f"+{vydura_pwd['NDU_pct']:.0f}%", "1,337 last 6mo"),
    ("Atogepant new starts", f"+{ato_pwd['NDU_pct']:.0f}%", "439 last 6mo"),
]

y = 0.82
for label, value, sub in stats:
    ax_panel.text(0.04, y, label,
                   transform=ax_panel.transAxes,
                   fontsize=10, color=COLORS["viti_dark"],
                   fontweight="semibold", va="top")
    ax_panel.text(0.96, y, value,
                   transform=ax_panel.transAxes,
                   fontsize=14, color=COLORS["pfizer_blue"],
                   fontweight="bold", va="top", ha="right")
    ax_panel.text(0.04, y - 0.045, sub,
                   transform=ax_panel.transAxes,
                   fontsize=8.5, color=COLORS["viti_gray"], va="top")
    y -= 0.16

# Footer interpretation
ax_panel.text(0.04, 0.13,
               "Class is growing on both ends.\nVydura share holds on a\nrising base. P6 defends the\nclass-leader position.",
               transform=ax_panel.transAxes,
               fontsize=10, color=COLORS["viti_dark"],
               fontweight="semibold", va="top", linespacing=1.4)

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="P6 MIGRAINE CLASS LEAD · ORAL GEPANTS · 2022–2026",
    headline="Vydura is the first-line oral gepant in 20 of 21 regions.",
    takeaway="Uppsala is the exception — Atogepant leads at 56% first-line. Akademiska prescribing-preference structural anomaly.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: AVA Vydura individual-patient data (lopnr × drug × edate, Nov 2022–Mar 2026). "
                "First-drug = patient's earliest dispensation in the dataset. "
                "Class growth: PWD = patients with dispensations, NDU = new drug users.",
                x=0.06, y=0.03)

plt.savefig(OUT / "V10_migraine_class_lead.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V10_migraine_class_lead.png'}")
