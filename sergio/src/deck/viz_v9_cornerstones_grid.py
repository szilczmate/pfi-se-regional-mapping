# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V9 — Eight-cornerstone portfolio grid (deck slide 10).

Pfizer's national-tier engagement portfolio: 8 named individuals who together
control or shape access decisions across NT-rådet, NSG, sjukvårdsregioner,
and the largest läkemedelskommittéer.

Output: delivery/figures/deck/V9_cornerstones_grid.png
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

CORNERSTONES = [
    {"name": "Mårten Lindström",
     "title": "NT-rådet acting Chair",
     "region": "Sydöstra · Jönköping",
     "why": "National prioritisation lever",
     "angle": "Successor (Holmström) takes over 2026-07-01 — engage now"},
    {"name": "Pia Näsvall",
     "title": "NSG Läkemedel ordförande + HSD",
     "region": "National + Västerbotten",
     "why": "Cross-regional access architecture",
     "angle": "Moved Norrbotten → Västerbotten 2024 · still NSG chair"},
    {"name": "Anders Bergström",
     "title": "NT-rådet Vice Chair · apotekare",
     "region": "Norra · Norrbotten",
     "why": "NT-rådet operating tier",
     "angle": "Closest to Norrland ATTR-PN cornerstone geography"},
    {"name": "Maria Ekelund",
     "title": "LK ordf + NT-rådet Sydöstra",
     "region": "Sydöstra · Jönköping",
     "why": "Dual-role access node",
     "angle": "Same region as Lindström — joint engagement window"},
    {"name": "Jan Melin",
     "title": "LK ordf + NT-rådet Mellansverige",
     "region": "Mellansverige · Uppsala",
     "why": "Dual-role access node",
     "angle": "Sits over the Uppsala migraine anomaly (Atogepant-leads region)"},
    {"name": "Mats Ek",
     "title": "LK ordförande Stockholm",
     "region": "Stockholm",
     "why": "Stockholm CDK4/6 expert-group recommendation",
     "angle": "Primary P2 engagement — Stockholm explicitly recommends Kisqali"},
    {"name": "Johan Bratt",
     "title": "NSG ledamot",
     "region": "Stockholm-Gotland",
     "why": "Stockholm sjukvårdsregion access",
     "angle": "Email verified 2026-04-29 — direct engagement viable"},
    {"name": "Rickard Malmström",
     "title": "Docent klinisk farmakologi · Karolinska",
     "region": "Stockholm-Gotland",
     "why": "Clinical-academic gravitational pull",
     "angle": "Vice-ledamot Stockholm LK · academic-network influence"},
]

# ---------------------------------------------------------------------------
# Figure: 4×2 grid
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.5, 7.5))
fig.subplots_adjust(left=0.04, right=0.96, top=0.78, bottom=0.06)

ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

n_cols = 4
n_rows = 2
gap_x = 1.5
gap_y = 3.5
total_gap_x = gap_x * (n_cols - 1)
total_gap_y = gap_y * (n_rows - 1)
card_w = (100 - total_gap_x) / n_cols
card_h = (100 - total_gap_y) / n_rows

import textwrap

for idx, cs in enumerate(CORNERSTONES):
    col = idx % n_cols
    row = idx // n_cols
    x = col * (card_w + gap_x)
    # invert row (top first) — figure y=100 at top
    y = (n_rows - 1 - row) * (card_h + gap_y)

    # Card body
    box = FancyBboxPatch(
        (x, y), card_w, card_h,
        boxstyle="round,pad=0,rounding_size=2",
        linewidth=0.8, edgecolor=COLORS["viti_medium"],
        facecolor="white",
        zorder=1,
    )
    ax.add_patch(box)

    # Top accent bar
    accent = Rectangle((x, y + card_h - 1.2), card_w, 1.2,
                        facecolor=COLORS["pfizer_blue"],
                        zorder=2, linewidth=0)
    ax.add_patch(accent)

    # Number badge top-left
    ax.text(x + 2, y + card_h - 6, f"{idx+1}",
             ha="left", va="top",
             fontsize=11, color=COLORS["viti_blue"],
             fontweight="bold", zorder=3)

    # Name
    ax.text(x + card_w / 2, y + card_h - 6,
             cs["name"],
             ha="center", va="top",
             fontsize=12.5, color=COLORS["viti_dark"],
             fontweight="bold", zorder=3)

    # Title (wrapped)
    title_lines = textwrap.wrap(cs["title"], width=30)
    title_y = y + card_h - 14
    for j, line in enumerate(title_lines):
        ax.text(x + card_w / 2, title_y - j * 3.2,
                 line,
                 ha="center", va="top",
                 fontsize=9.5, color=COLORS["viti_blue"],
                 fontweight="semibold", zorder=3)
    title_h = len(title_lines) * 3.2

    # Region
    ax.text(x + card_w / 2, title_y - title_h - 1.5,
             cs["region"],
             ha="center", va="top",
             fontsize=8.5, color=COLORS["viti_gray"],
             zorder=3)

    # Why-they-matter (bold)
    why_y = title_y - title_h - 8
    why_lines = textwrap.wrap(cs["why"], width=32)
    for j, line in enumerate(why_lines):
        ax.text(x + card_w / 2, why_y - j * 3.2,
                 line,
                 ha="center", va="top",
                 fontsize=10, color=COLORS["viti_dark"],
                 fontweight="semibold", zorder=3)
    why_h = len(why_lines) * 3.2

    # Engagement angle
    angle_y = why_y - why_h - 3
    angle_lines = textwrap.wrap(cs["angle"], width=34)
    for j, line in enumerate(angle_lines):
        ax.text(x + card_w / 2, angle_y - j * 3.0,
                 line,
                 ha="center", va="top",
                 fontsize=8.8, color=COLORS["viti_gray"],
                 zorder=3, style="italic")

# Title block
add_accent_rule(fig, x=0.04, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="P5 NATIONAL-TIER GOVERNANCE · 8 CORNERSTONES",
    headline="Eight individuals at the centre of Pfizer's Sweden access decisions.",
    takeaway="Five operate at the national tier (NT-rådet, NSG); three at sjukvårdsregion level. Two carry dual roles.",
    x=0.04, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
)

add_source_line(fig,
                "Source: Stakeholder mapping v10 (delivery/07_stakeholder_mapping_v10.xlsx). "
                "Verified canonical via samverkanlakemedel.se 2026-04-26 + region websites. "
                "Cross-references: NT-rådet, NSG Läkemedel och medicinteknik, regional läkemedelskommittéer.",
                x=0.04, y=0.02)

plt.savefig(OUT / "V9_cornerstones_grid.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V9_cornerstones_grid.png'}")
