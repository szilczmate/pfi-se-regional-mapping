# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V12 — Eight cornerstones tactical card (deck slide 13).

Operational counterpart to V9. V9 frames the 8 cornerstones as a strategic
portfolio. V12 turns the same 8 names into a field-deployable call list:
contact tier, last verified, and the single recommended next action per
person.

Output: delivery/figures/deck/V12_cornerstones_tactical.png
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS,
                         add_title_block, add_source_line, add_accent_rule)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

# Tactical data — contact tier and recommended next action per cornerstone
ROWS = [
    {"name": "Mårten Lindström",
     "role": "NT-rådet acting Chair",
     "region": "Jönköping",
     "tier": "VERIFIED",
     "tier_color": "pfizer_blue",
     "next": "Joint scientific exchange before 2026-07-01 successor handover."},
    {"name": "Pia Näsvall",
     "role": "NSG ordförande + HSD",
     "region": "Västerbotten",
     "tier": "HIGH",
     "tier_color": "competitor_charcoal",
     "next": "ATTR-PN partnership proposal — Norrlands universitetssjukhus framing."},
    {"name": "Anders Bergström",
     "role": "NT-rådet Vice Chair",
     "region": "Norrbotten",
     "tier": "HIGH",
     "tier_color": "competitor_charcoal",
     "next": "Operational engagement on rare-disease pipeline (Hympavzi, Elrexfio)."},
    {"name": "Maria Ekelund",
     "role": "LK ordf + NT-rådet Sydöstra",
     "region": "Jönköping",
     "tier": "HIGH",
     "tier_color": "competitor_charcoal",
     "next": "Joint engagement with Lindström — same region, same agenda."},
    {"name": "Jan Melin",
     "role": "LK ordf + NT-rådet Mellansverige",
     "region": "Uppsala",
     "tier": "HIGH",
     "tier_color": "competitor_charcoal",
     "next": "Investigate Uppsala Atogepant-leads anomaly — P6 entry point."},
    {"name": "Mats Ek",
     "role": "LK ordförande Stockholm",
     "region": "Stockholm",
     "tier": "VERIFIED",
     "tier_color": "pfizer_blue",
     "next": "P2 primary engagement — Stockholm CDK4/6 expert-group authority."},
    {"name": "Johan Bratt",
     "role": "NSG ledamot",
     "region": "Stockholm-Gotland",
     "tier": "VERIFIED",
     "tier_color": "pfizer_blue",
     "next": "Direct outreach — email verified 2026-04-29."},
    {"name": "Rickard Malmström",
     "role": "Klinisk farmakologi · Karolinska",
     "region": "Stockholm",
     "tier": "VERIFIED",
     "tier_color": "pfizer_blue",
     "next": "Academic-network entry point for Stockholm LK and beyond."},
]

# ---------------------------------------------------------------------------
# Figure: dense table-style layout, 8 rows
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.5, 7.0))
fig.subplots_adjust(left=0.04, right=0.96, top=0.78, bottom=0.06)
ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Column layout (in axis x-coords 0..100)
COL_NUM = (1, 4)
COL_NAME = (4, 22)
COL_ROLE = (22, 44)
COL_REGION = (44, 56)
COL_TIER = (56, 67)
COL_ACTION = (67, 99)

# Header row
header_y = 88
for col_x, label in [(COL_NAME, "NAME"),
                      (COL_ROLE, "ROLE"),
                      (COL_REGION, "REGION"),
                      (COL_TIER, "CONTACT TIER"),
                      (COL_ACTION, "RECOMMENDED NEXT ACTION")]:
    ax.text(col_x[0], header_y, label,
             fontsize=8.5, color=COLORS["viti_blue"],
             fontweight="bold", va="bottom")

# Header rule
ax.add_patch(Rectangle((1, header_y - 1.5), 98, 0.4,
                         facecolor=COLORS["viti_medium"],
                         linewidth=0, zorder=1))

# Row layout
n_rows = len(ROWS)
row_top = 84
row_bottom = 4
row_h = (row_top - row_bottom) / n_rows

import textwrap

for i, row in enumerate(ROWS):
    y_top = row_top - i * row_h
    y_mid = y_top - row_h / 2

    # Alternating row stripe
    if i % 2 == 0:
        ax.add_patch(Rectangle((1, y_top - row_h), 98, row_h,
                                  facecolor=COLORS["viti_light"],
                                  linewidth=0, zorder=1, alpha=0.6))

    # Number badge
    ax.text(COL_NUM[0] + 0.5, y_mid, f"{i+1}",
             fontsize=11, color=COLORS["viti_blue"],
             fontweight="bold", va="center", zorder=3)

    # Name
    ax.text(COL_NAME[0], y_mid, row["name"],
             fontsize=11.5, color=COLORS["viti_dark"],
             fontweight="bold", va="center", zorder=3)

    # Role
    ax.text(COL_ROLE[0], y_mid, row["role"],
             fontsize=10, color=COLORS["viti_dark"],
             va="center", zorder=3)

    # Region
    ax.text(COL_REGION[0], y_mid, row["region"],
             fontsize=10, color=COLORS["viti_gray"],
             va="center", zorder=3)

    # Tier badge
    tier_color = COLORS[row["tier_color"]]
    badge_w = 7
    badge_x = COL_TIER[0]
    ax.add_patch(FancyBboxPatch(
        (badge_x, y_mid - 1.3), badge_w, 2.6,
        boxstyle="round,pad=0,rounding_size=0.7",
        facecolor=tier_color, linewidth=0, zorder=2,
    ))
    ax.text(badge_x + badge_w / 2, y_mid, row["tier"],
             fontsize=8.5, color="white",
             fontweight="bold", va="center", ha="center", zorder=4)

    # Next action (wrapped)
    action_lines = textwrap.wrap(row["next"], width=58)
    if len(action_lines) == 1:
        ax.text(COL_ACTION[0], y_mid, action_lines[0],
                 fontsize=9.5, color=COLORS["viti_dark"],
                 fontweight="semibold", va="center", zorder=3)
    else:
        offset = (len(action_lines) - 1) * 1.6
        for j, line in enumerate(action_lines):
            ax.text(COL_ACTION[0], y_mid + offset / 2 - j * 3.2,
                     line,
                     fontsize=9.5, color=COLORS["viti_dark"],
                     fontweight="semibold", va="center", zorder=3)

# Legend for tiers below the table
legend_y = 2.5
ax.text(1, legend_y, "CONTACT TIER",
         fontsize=8, color=COLORS["viti_blue"],
         fontweight="bold", va="center")
ax.add_patch(FancyBboxPatch((10, legend_y - 1), 5, 2,
                              boxstyle="round,pad=0,rounding_size=0.5",
                              facecolor=COLORS["pfizer_blue"], linewidth=0))
ax.text(12.5, legend_y, "VERIFIED", fontsize=7.5, color="white",
         fontweight="bold", va="center", ha="center")
ax.text(16, legend_y, "= email confirmed",
         fontsize=8.5, color=COLORS["viti_gray"], va="center")

ax.add_patch(FancyBboxPatch((34, legend_y - 1), 5, 2,
                              boxstyle="round,pad=0,rounding_size=0.5",
                              facecolor=COLORS["competitor_charcoal"], linewidth=0))
ax.text(36.5, legend_y, "HIGH", fontsize=7.5, color="white",
         fontweight="bold", va="center", ha="center")
ax.text(40, legend_y, "= inferred email candidate, high confidence",
         fontsize=8.5, color=COLORS["viti_gray"], va="center")

# Title block
add_accent_rule(fig, x=0.04, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="STAKEHOLDER MAP · 8 CORNERSTONES · ACTION LIST",
    headline="Eight cornerstones with recommended next actions.",
    takeaway="Four contacts are email-verified for direct outreach. Four are HIGH-confidence inferred candidates pending verification.",
    x=0.04, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
)

add_source_line(fig,
                "Source: Stakeholder mapping v10 Contacts sheet. VERIFIED = email confirmed via region website or direct verification. "
                "HIGH = inferred email candidate based on naming convention + role match.",
                x=0.04, y=0.005)

plt.savefig(OUT / "V12_cornerstones_tactical.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V12_cornerstones_tactical.png'}")
