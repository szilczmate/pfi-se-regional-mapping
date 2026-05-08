# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V11 — Stakeholder portfolio quadrant (deck slide 12).

Per-Pfizer-product 4-quadrant breakdown across 21 Swedish regions:
  HH = Priority focus      (high opportunity × high actionability)
  HL = Engagement build    (high opportunity × low actionability)
  LH = Quick win           (low opportunity × high actionability)
  LL = Deprioritise        (low opportunity × low actionability)

Output: delivery/figures/deck/V11_stakeholder_quadrant.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, style_axes,
                         add_title_block, add_source_line, add_accent_rule)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

# Load and clean Quadrant summary
raw = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                     sheet_name="Quadrant summary")
# Header sits at row index 1, data starts at index 2
raw.columns = raw.iloc[1].tolist()
df = raw.iloc[2:].reset_index(drop=True)
df = df.dropna(subset=["Product"])
# Drop summary/legend rows: TOTAL, and rows starting with "HH —", "HL —", "LH —", "LL —"
df = df[~df["Product"].astype(str).str.upper().str.startswith("TOTAL")]
df = df[~df["Product"].astype(str).str.contains("—")]
# Drop rows with NaN in the data columns
df = df.dropna(subset=["HH (Priority focus)"])

# Coerce numerics
for c in ["HH (Priority focus)", "HL (Engagement build)",
          "LH (Quick win)", "LL (Deprioritize)", "Total"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Sort by total HH+HL+LH (active engagement = non-Deprioritise)
df["active"] = df["HH (Priority focus)"] + df["HL (Engagement build)"] + df["LH (Quick win)"]
df = df.sort_values("active", ascending=True)
print(df[["Product", "HH (Priority focus)", "HL (Engagement build)",
          "LH (Quick win)", "LL (Deprioritize)"]].to_string(index=False))

# National totals
totals = {
    "HH (Priority focus)": df["HH (Priority focus)"].sum(),
    "HL (Engagement build)": df["HL (Engagement build)"].sum(),
    "LH (Quick win)": df["LH (Quick win)"].sum(),
    "LL (Deprioritize)": df["LL (Deprioritize)"].sum(),
}

# Color mapping
QCOLORS = {
    "HH (Priority focus)":   COLORS["pfizer_blue"],
    "HL (Engagement build)": COLORS["competitor_charcoal"],
    "LH (Quick win)":        COLORS["highlight_amber"],
    "LL (Deprioritize)":     COLORS["competitor_gray"],
}
QLABELS = {
    "HH (Priority focus)":   "Priority focus",
    "HL (Engagement build)": "Engagement build",
    "LH (Quick win)":        "Quick win",
    "LL (Deprioritize)":     "Deprioritise",
}

# ---------------------------------------------------------------------------
# Figure: stacked horizontal bars
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 7.0))
gs = fig.add_gridspec(1, 5, left=0.10, right=0.97,
                       top=0.74, bottom=0.10,
                       wspace=0.08)
ax = fig.add_subplot(gs[0, :3])
ax_panel = fig.add_subplot(gs[0, 3:])
ax_panel.axis("off")

cumulative = [0] * len(df)
products = df["Product"].tolist()
y_pos = list(range(len(products)))

for col, color in QCOLORS.items():
    values = df[col].tolist()
    ax.barh(y_pos, values, left=cumulative,
             color=color, edgecolor="white", linewidth=1.2,
             height=0.62)
    # Inline value labels
    for i, (val, cum) in enumerate(zip(values, cumulative)):
        if val > 1:  # only label if >1 cell
            text_color = "white" if col != "LL (Deprioritize)" else COLORS["viti_dark"]
            weight = "bold" if col == "HH (Priority focus)" else "regular"
            ax.text(cum + val / 2, i, f"{int(val)}",
                    ha="center", va="center",
                    color=text_color, fontsize=10, fontweight=weight)
    cumulative = [c + v for c, v in zip(cumulative, values)]

ax.set_yticks(y_pos)
ax.set_yticklabels(products, fontsize=10.5, color=COLORS["viti_dark"])
ax.set_xlabel("Regions (out of 21)", fontsize=10, color=COLORS["viti_dark"])
ax.set_xlim(0, 21)
ax.set_xticks([0, 5, 10, 15, 20, 21])
style_axes(ax, hide_x_grid=True)
ax.grid(True, axis="x", alpha=0.25)

# Legend at top of chart
from matplotlib.lines import Line2D
legend_handles = [
    Rectangle((0, 0), 1, 1, color=QCOLORS[k]) for k in QCOLORS
]
legend_labels = [QLABELS[k] for k in QCOLORS]
leg = ax.legend(legend_handles, legend_labels,
                 loc="upper center", bbox_to_anchor=(0.5, 1.10),
                 ncol=4, frameon=False, fontsize=10,
                 handlelength=1.2, handletextpad=0.5,
                 columnspacing=2.0)
for text in leg.get_texts():
    text.set_color(COLORS["viti_dark"])

# ---------------------------------------------------------------------------
# Right panel: total counts
# ---------------------------------------------------------------------------
ax_panel.text(0.04, 0.97, "PORTFOLIO TOTALS",
               transform=ax_panel.transAxes,
               fontsize=10, fontweight="bold",
               color=COLORS["pfizer_blue"], va="top")
ax_panel.text(0.04, 0.92, "Across 11 products × 21 regions",
               transform=ax_panel.transAxes,
               fontsize=8.5, color=COLORS["viti_gray"], va="top")

quadrant_order = [
    ("HH (Priority focus)",   "Priority focus",  "Deploy field hardest"),
    ("HL (Engagement build)", "Engagement build","Build access first"),
    ("LH (Quick win)",        "Quick win",       "Capture and protect"),
    ("LL (Deprioritize)",     "Deprioritise",    "Maintain only"),
]

y = 0.82
for key, label, sub in quadrant_order:
    val = totals[key]
    color = QCOLORS[key]
    # Color swatch
    ax_panel.add_patch(Rectangle((0.04, y - 0.04), 0.04, 0.04,
                                   facecolor=color, transform=ax_panel.transAxes,
                                   clip_on=False, zorder=3))
    # Label
    ax_panel.text(0.12, y, label,
                   transform=ax_panel.transAxes,
                   fontsize=11, color=COLORS["viti_dark"],
                   fontweight="semibold", va="top")
    # Big count
    ax_panel.text(0.95, y - 0.005, f"{int(val)}",
                   transform=ax_panel.transAxes,
                   fontsize=18, color=color,
                   fontweight="bold", va="top", ha="right")
    # Sub
    ax_panel.text(0.12, y - 0.045, sub,
                   transform=ax_panel.transAxes,
                   fontsize=9, color=COLORS["viti_gray"], va="top")
    y -= 0.18

# Footer interpretation
ax_panel.text(0.04, 0.13,
               f"{int(totals['HH (Priority focus)'] + totals['LH (Quick win)'])} of 231 cells\nare active engagement.\nFocus the field on these.",
               transform=ax_panel.transAxes,
               fontsize=10, color=COLORS["viti_dark"],
               fontweight="semibold", va="top", linespacing=1.4)

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="ENGAGEMENT PORTFOLIO · 11 PRODUCTS × 21 REGIONS · 231 CELLS",
    headline="Most Pfizer products show a concentrated priority cluster and a long deprioritise tail.",
    takeaway="Priority-focus + Quick-win cells total 116 of 231 (50%) — the active engagement set. Deprioritise dominates by count at 91.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: Workbook v30 sheet \"Quadrant summary\". "
                "Opportunity = burden × penetration gap; Actionability = stakeholder access × policy state. "
                "Each cell = one Pfizer product in one region.",
                x=0.06, y=0.03)

plt.savefig(OUT / "V11_stakeholder_quadrant.png", facecolor="#FFFFFF")
print(f"\nWrote {OUT / 'V11_stakeholder_quadrant.png'}")
