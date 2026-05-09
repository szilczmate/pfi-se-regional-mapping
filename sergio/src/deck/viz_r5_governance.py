# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R5 — Governance & Stakeholder Engagement dashboard (slide 5 of 6).

Layout:
  Left card:  Key Decision-Makers (7 roles + names) + Top Influence Scores
  Top-right:  Top Product Priorities (3 ranked) + Archetype banner
  Bottom-right: Competitor Pipeline Threats (3 named threats)
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source, out_path)
from region_data import get_region, get_stakeholders, get_narratives
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


# Hand-curated influence scores (from workbook v30 "Stakeholder influence" sheet)
# Format: (name, role, score)
INFLUENCE = {
    "Region Stockholm": [
        ("Rickard Malmström", "NT-rådet rep", 114),
        ("Johan Bratt", "NSG rep", 102),
        ("Mats Ek", "Stockholm LK ordf", 75),
    ],
    "Region Västerbotten": [
        ("Anders Bergström", "NT-rådet Vice Chair (Norra)", 95),
        ("Pia Näsvall", "NSG Chair", 85),
        ("Bo Sundqvist", "Västerbotten LK ordf", 75),
    ],
}


def render_r5(region_full_name):
    d = get_region(region_full_name)
    s = get_stakeholders(region_full_name)
    n = get_narratives(region_full_name)
    influence = INFLUENCE.get(region_full_name, [])

    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGION PROFILE  ·  PART B",
                title=d["region_short"],
                subtitle="Governance & Stakeholder Engagement")

    # ---------- Left card: Decision-Makers + Influence ----------
    left_x = 5.0
    left_y = 4.0
    left_w = 42.0
    left_h = 40.0

    ax.add_patch(FancyBboxPatch(
        (left_x, left_y), left_w, left_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((left_x, left_y), 0.5, left_h,
                              facecolor=COLORS["pfizer_blue"],
                              linewidth=0, zorder=2))

    ax.text(left_x + 1.5, left_y + left_h - 1.5,
             "Key Decision-Makers",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")

    roles_table = [
        ("Regional Director",        s["regiondirektor"]),
        ("Healthcare Director",      s["hsd"]),
        ("Regional Council Chair",   s["rs_ordf"]),
        ("HC Board Chair",           s["hsn_ordf"]),
        ("Drug Committee Chair",     s["lk_ordf"]),
        ("NT-rådet Rep",             _strip_paren(s["nt_radet_rep"])),
        ("NSG Rep",                  _strip_paren(s["nsg_rep"])),
    ]
    row_y = left_y + left_h - 4.5
    for role, name in roles_table:
        ax.text(left_x + 1.5, row_y, role,
                 fontsize=10, color=COLORS["viti_gray"],
                 va="top", ha="left")
        ax.text(left_x + 17.0, row_y, str(name),
                 fontsize=10.5, color=COLORS["viti_dark"],
                 fontweight="semibold", va="top", ha="left")
        row_y -= 2.4

    # Divider
    ax.add_patch(Rectangle((left_x + 1.5, row_y - 0.3),
                              left_w - 3.0, 0.05,
                              facecolor=COLORS["viti_medium"],
                              linewidth=0, zorder=3))

    # Top Influence Scores
    inf_y = row_y - 2.0
    ax.text(left_x + 1.5, inf_y,
             "Top Influence Scores",
             fontsize=11, color=COLORS["viti_blue"],
             fontweight="bold", va="top")
    # Compact formula caption
    ax.text(left_x + left_w - 1.5, inf_y,
             "Score = Role × Confidence × SVR",
             fontsize=8, color=COLORS["viti_gray"],
             style="italic", va="top", ha="right")
    inf_y -= 2.2
    for name, role, score in influence:
        ax.text(left_x + 1.5, inf_y, name,
                 fontsize=10.5, color=COLORS["viti_dark"],
                 fontweight="semibold", va="top")
        ax.text(left_x + left_w - 1.5, inf_y, f"{score}",
                 fontsize=14, color=COLORS["pfizer_blue"],
                 fontweight="bold", va="top", ha="right")
        ax.text(left_x + 1.5, inf_y - 1.6, role,
                 fontsize=8.5, color=COLORS["viti_gray"], va="top")
        inf_y -= 3.1

    # Bottom legend strip — weight reference (very compact)
    legend_y = inf_y - 0.1
    ax.text(left_x + 1.5, legend_y,
             "NT-rådet 95 · NSG 85 · LK 75 · HSD 70 · RD 65 · HSN 55 · RS 50",
             fontsize=7.5, color=COLORS["viti_gray"], va="top")
    ax.text(left_x + 1.5, legend_y - 1.3,
             "Confidence: HIGH ×1.0 · MEDIUM ×0.7 · LOW ×0.4    SVR bonus: 1.00–1.20",
             fontsize=7.5, color=COLORS["viti_gray"], va="top")

    # ---------- Top-right: Top Product Priorities ----------
    right_x = 51.0
    right_w = 44.0
    top_card_y = 24.0
    top_card_h = 20.0

    ax.add_patch(FancyBboxPatch(
        (right_x, top_card_y), right_w, top_card_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((right_x, top_card_y), 0.5, top_card_h,
                              facecolor=COLORS["competitor_charcoal"],
                              linewidth=0, zorder=2))

    ax.text(right_x + 1.5, top_card_y + top_card_h - 1.5,
             "Top Product Priorities",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")

    products = [
        ("1", d["top_product_1"], d["top_product_1_score"]),
        ("2", d["top_product_2"], d["top_product_2_score"]),
        ("3", d["top_product_3"], d["top_product_3_score"]),
    ]
    py = top_card_y + top_card_h - 5.0
    for rank, prod_name, score in products:
        # Number badge
        ax.add_patch(FancyBboxPatch(
            (right_x + 1.5, py - 2.6), 2.5, 2.5,
            boxstyle="round,pad=0,rounding_size=0.4",
            facecolor=COLORS["pfizer_blue"], linewidth=0, zorder=3,
        ))
        ax.text(right_x + 2.75, py - 1.3, rank,
                 fontsize=14, color="white",
                 fontweight="bold", va="center", ha="center", zorder=4)

        # Name + score
        ax.text(right_x + 5.5, py, str(prod_name),
                 fontsize=11.5, color=COLORS["viti_dark"],
                 fontweight="semibold", va="top")
        score_str = f"Score: {score:.1f}" if isinstance(score, (int, float)) and score == score else "Score: —"
        ax.text(right_x + 5.5, py - 2.0, score_str,
                 fontsize=9, color=COLORS["viti_gray"], va="top")
        py -= 5.0

    # Archetype banner
    arch_y = top_card_y + 1.5
    archetype = n.get("archetype", "—")
    ax.text(right_x + 1.5, arch_y, "Regional archetype:",
             fontsize=9, color=COLORS["viti_gray"],
             va="top", fontweight="semibold")
    ax.text(right_x + 11.5, arch_y, archetype,
             fontsize=10, color=COLORS["pfizer_blue"],
             fontweight="bold", va="top")

    # ---------- Bottom-right: Competitor Threats ----------
    bot_card_y = 4.0
    bot_card_h = 19.0

    ax.add_patch(FancyBboxPatch(
        (right_x, bot_card_y), right_w, bot_card_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((right_x, bot_card_y), 0.5, bot_card_h,
                              facecolor=COLORS["highlight_amber"],
                              linewidth=0, zorder=2))

    ax.text(right_x + 1.5, bot_card_y + bot_card_h - 1.5,
             "Competitor Pipeline Threats",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")

    import textwrap
    threats = n.get("competitor_threats", [])
    ty = bot_card_y + bot_card_h - 3.4
    for name, body in threats:
        ax.text(right_x + 1.5, ty, name,
                 fontsize=10, color=COLORS["highlight_amber"],
                 fontweight="bold", va="top")
        body_lines = textwrap.wrap(body, width=60)
        for i, line in enumerate(body_lines):
            ax.text(right_x + 1.5, ty - 1.4 - i * 1.25, line,
                     fontsize=8.5, color=COLORS["viti_dark"], va="top")
        ty -= 1.4 + len(body_lines) * 1.25 + 0.6

    draw_source(ax,
                 "Source: samverkanlakemedel.se NT-rådet + NSG Läkemedel chairs (verified 2026-04-26), "
                 "regional websites, Stakeholder mapping v10, Workbook v30 \"Stakeholder influence\".")

    plt.savefig(out_path(d["region_short"], "R5_governance"),
                facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path(d['region_short'], 'R5_governance')}")


def _strip_paren(s):
    """Drop trailing parenthetical metadata like '(Region Stockholm, klinisk farmakologi)'."""
    if s is None or s != s:
        return ""
    s = str(s)
    return s.split(" (")[0].strip()


if __name__ == "__main__":
    render_r5("Region Stockholm")
