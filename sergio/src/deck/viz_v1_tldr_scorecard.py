# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V1 — TL;DR scorecard (deck slide 2).

Five headline numbers laid out as a single page. The "what's inside" frame.

Output: delivery/figures/deck/V1_tldr_scorecard.png
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

# Five headline numbers
CARDS = [
    {"big": "17.5%",
     "label": "Pfizer's current CDK4/6 SEK share",
     "context": "Down from 58.6% in Sep 2023 — a 41-point collapse.",
     "tag": "P2 reframe"},
    {"big": "7%",
     "label": "Pfizer's share of class-naive new starts",
     "context": "Of 620 patients starting CDK4/6, only 45 chose Ibrance.",
     "tag": "P2 leading indicator"},
    {"big": "9.3M kr",
     "label": "Field-deployable recovery opportunity",
     "context": "Across 11 priority bricks. Top 8 alone capture 4.1M kr.",
     "tag": "P2 deployment"},
    {"big": "8.1×",
     "label": "Norrland over-index on ATTR-PN",
     "context": "Cornerstone confirmed — but it's hereditary polyneuropathy, not cardiomyopathy.",
     "tag": "P1 correction"},
    {"big": "8",
     "label": "Named tier-1 cornerstones, mapped",
     "context": "90% combined contact coverage across Sweden's national governance tier.",
     "tag": "Stakeholder map"},
]

# ---------------------------------------------------------------------------
# Figure: 5 cards in a row across the slide
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 6.0))
fig.subplots_adjust(left=0.04, right=0.96, top=0.74, bottom=0.10)

ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

n = len(CARDS)
gap = 1.5
total_gap = gap * (n - 1)
card_w = (100 - total_gap) / n
card_h = 78

for i, card in enumerate(CARDS):
    x = i * (card_w + gap)
    y = 5

    # Card background — subtle Light Tint
    box = FancyBboxPatch(
        (x, y), card_w, card_h,
        boxstyle="round,pad=0,rounding_size=2",
        linewidth=0,
        facecolor=COLORS["viti_light"],
        zorder=1,
    )
    ax.add_patch(box)

    # Top accent bar
    accent = Rectangle((x, y + card_h - 1.2), card_w, 1.2,
                        facecolor=COLORS["pfizer_blue"],
                        zorder=2, linewidth=0)
    ax.add_patch(accent)

    # Tag (top of card, small, viti blue)
    ax.text(x + card_w / 2, y + card_h - 7,
             card["tag"].upper(),
             ha="center", va="top",
             fontsize=8.5, color=COLORS["viti_blue"],
             fontweight="semibold", zorder=3)

    # Big number — centered vertically
    ax.text(x + card_w / 2, y + card_h - 22,
             card["big"],
             ha="center", va="center",
             fontsize=32, color=COLORS["pfizer_blue"],
             fontweight="bold", zorder=3)

    # Label (wrapped to card width)
    import textwrap
    label_lines = textwrap.wrap(card["label"], width=22)
    label_y = y + card_h - 38
    for j, line in enumerate(label_lines):
        ax.text(x + card_w / 2, label_y - j * 3.6,
                 line,
                 ha="center", va="top",
                 fontsize=10.5, color=COLORS["viti_dark"],
                 fontweight="semibold", zorder=3)
    label_block_h = len(label_lines) * 3.6

    # Context (wrapped)
    context_lines = textwrap.wrap(card["context"], width=26)
    context_y = label_y - label_block_h - 3
    for j, line in enumerate(context_lines):
        ax.text(x + card_w / 2, context_y - j * 3.2,
                 line,
                 ha="center", va="top",
                 fontsize=9, color=COLORS["viti_gray"],
                 zorder=3)

# Title block
add_accent_rule(fig, x=0.04, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="PFIZER SWEDEN REGIONAL LANDSCAPE · MAY 2026",
    headline="What's inside.",
    takeaway="Five findings on Pfizer's current position, leading-indicator dynamics, and engagement priorities.",
    x=0.04, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
)

add_source_line(fig,
                "Sources: IQVIA Sell-In SEK Apr 2023–Mar 2026 (Vaccines, RD/IM, Oncology); AVA patient-level data Aug 2025–Jan 2026; "
                "Stakeholder mapping v10 with verified, HIGH, and MEDIUM-confidence email tiers.",
                x=0.04, y=0.02)

plt.savefig(OUT / "V1_tldr_scorecard.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V1_tldr_scorecard.png'}")
