# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R6 — Competitive Landscape & Strategic Positioning (slide 6 of 6).

Layout:
  Top-left:    CDK4/6 Competitive Landscape (3 product mini-panels with units + Δ%)
  Top-right:   Opportunity × Actionability Quadrant (text summary)
  Middle band: GRP-Adjusted Pharmaceutical Usage (narrative)
  Bottom:      Strategic Summary (6 bullets in 2 columns)
"""

from pathlib import Path
import sys
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source, out_path)
from region_data import get_region, get_narratives
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")

# Quadrant counts per region (from workbook v30 Quadrant summary)
# Each entry: (HH, HL, LH, LL) Priority focus / Engagement build / Quick win / Deprioritise
# Aggregated across the 11 Pfizer products for each region
QUADRANT_PRODUCTS = {
    "Region Stockholm": {
        "HH": ["Paxlovid","Vydura","Tukysa","Vyndaqel","Talzenna","Elrexfio",
               "Lorbrena/Lorviqua","Abrysvo","Prevenar 20","Hympavzi","Ibrance"],
        "HL": [],
        "LH": [],
        "LL": [],
    },
    "Region Västerbotten": {
        # Source: Workbook v30 "Region x product matrix" (verified 2026-05-06)
        "HH": ["Vyndaqel","Tukysa","Paxlovid"],
        "HL": [],
        "LH": ["Lorbrena/Lorviqua","Talzenna","Prevenar 20","Vydura","Ibrance"],
        "LL": ["Abrysvo","Elrexfio","Hympavzi"],
    },
}


def render_r6(region_full_name):
    d = get_region(region_full_name)
    n = get_narratives(region_full_name)
    quad = QUADRANT_PRODUCTS.get(region_full_name, {"HH":[],"HL":[],"LH":[],"LL":[]})

    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGION PROFILE  ·  PART B",
                title=d["region_short"],
                subtitle="Competitive Landscape & Strategic Positioning")

    # ---------- Top-left: CDK4/6 panel ----------
    tl_x, tl_y, tl_w, tl_h = 5.0, 28.0, 42.0, 17.0
    ax.add_patch(FancyBboxPatch(
        (tl_x, tl_y), tl_w, tl_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((tl_x, tl_y), 0.5, tl_h,
                              facecolor=COLORS["pfizer_blue"], linewidth=0, zorder=2))

    ax.text(tl_x + 1.5, tl_y + tl_h - 1.5,
             "CDK4/6 Competitive Landscape",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(tl_x + 1.5, tl_y + tl_h - 4.0,
             f"Pfizer share: {d['cdk_pfizer_units_share']:.1f}% units  ·  {d['cdk_pfizer_sek_share']:.1f}% SEK",
             fontsize=10, color=COLORS["viti_gray"], va="top",
             fontweight="semibold")

    # 3 mini-panels for the three drugs (compact: drug name + units + Δ%)
    drugs = [
        ("Ibrance", d["ibrance_units"], d["ibrance_delta_18m"], COLORS["pfizer_blue"]),
        ("Verzenios", d["verzenios_units"], d["verzenios_delta_18m"], COLORS["competitor_charcoal"]),
        ("Kisqali", d["kisqali_units"], d["kisqali_delta_18m"], COLORS["competitor_gray"]),
    ]
    panel_w = (tl_w - 3.0) / 3
    for i, (name, units, delta, col) in enumerate(drugs):
        px = tl_x + 1.5 + i * panel_w
        py = tl_y + tl_h - 5.0
        ax.text(px, py, name,
                 fontsize=11, color=col,
                 fontweight="bold", va="top")
        ax.text(px, py - 2.0, f"{int(units):,}",
                 fontsize=18, color=COLORS["viti_dark"],
                 fontweight="bold", va="top")
        sign = "+" if delta >= 0 else ""
        delta_color = (COLORS["pfizer_blue"] if name == "Ibrance"
                       else COLORS["highlight_amber"] if delta > 50
                       else COLORS["viti_dark"])
        ax.text(px, py - 5.5, f"Δ {sign}{delta:.1f}%",
                 fontsize=11, color=delta_color,
                 fontweight="bold", va="top")

    # Substitution line + shared "units" legend at the card bottom
    sub_text = d.get("cdk_substitution_direction") or ""
    if sub_text and sub_text == sub_text:
        ax.text(tl_x + 1.5, tl_y + 2.0,
                 sub_text,
                 fontsize=9, color=COLORS["viti_dark"],
                 va="bottom", style="italic")
    ax.text(tl_x + 1.5, tl_y + 0.6,
             "Units (3-year)  ·  Δ = 1H vs 2H window",
             fontsize=8, color=COLORS["viti_gray"],
             va="bottom")

    # ---------- Top-right: Quadrant summary ----------
    tr_x, tr_y, tr_w, tr_h = 51.0, 28.0, 44.0, 17.0
    ax.add_patch(FancyBboxPatch(
        (tr_x, tr_y), tr_w, tr_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((tr_x, tr_y), 0.5, tr_h,
                              facecolor=COLORS["competitor_charcoal"],
                              linewidth=0, zorder=2))

    ax.text(tr_x + 1.5, tr_y + tr_h - 1.5,
             "Opportunity × Actionability",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")

    quad_rows = [
        ("Priority focus",     "HH", quad["HH"], COLORS["pfizer_blue"]),
        ("Engagement build",   "HL", quad["HL"], COLORS["competitor_charcoal"]),
        ("Quick win",          "LH", quad["LH"], COLORS["highlight_amber"]),
        ("Deprioritise",       "LL", quad["LL"], COLORS["competitor_gray"]),
    ]
    qy = tr_y + tr_h - 3.5
    for label, code, products, col in quad_rows:
        # Color dot
        ax.add_patch(Rectangle((tr_x + 1.5, qy - 0.8), 1.4, 1.4,
                                  facecolor=col, linewidth=0, zorder=3))
        # Label
        ax.text(tr_x + 3.7, qy, label,
                 fontsize=10.5, color=COLORS["viti_dark"],
                 fontweight="semibold", va="top")
        # Count
        ax.text(tr_x + 3.7, qy - 1.4,
                 f"{len(products)} product{'s' if len(products) != 1 else ''}",
                 fontsize=8.5, color=COLORS["viti_gray"], va="top")
        # Product list (wrapped) — allow up to 3 lines for the 11-product row
        product_str = ", ".join(products) if products else "—"
        wrapped = textwrap.wrap(product_str, width=44)
        max_lines = 3
        for j, line in enumerate(wrapped[:max_lines]):
            if j == max_lines - 1 and len(wrapped) > max_lines:
                line += " …"
            ax.text(tr_x + 17.0, qy - j * 1.25, line,
                     fontsize=8.5, color=COLORS["viti_dark"], va="top")
        qy -= 3.3

    # ---------- Middle band: GRP narrative (height matched to content) ----------
    grp_note = n.get("grp_pharma_note", "")
    wrap_width = 165
    grp_lines = textwrap.wrap(grp_note, width=wrap_width)
    mid_h = max(5.0, 2.5 + len(grp_lines) * 1.4)
    mid_x, mid_y, mid_w = 5.0, 17.0, 90.0
    ax.add_patch(FancyBboxPatch(
        (mid_x, mid_y), mid_w, mid_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor=COLORS["viti_light"], zorder=1,
    ))
    ax.text(mid_x + 1.5, mid_y + mid_h - 1.3,
             "GRP-Adjusted Pharmaceutical Usage",
             fontsize=11, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    for i, line in enumerate(grp_lines):
        ax.text(mid_x + 1.5, mid_y + mid_h - 3.0 - i * 1.4,
                 line, fontsize=9.5, color=COLORS["viti_dark"], va="top")

    # ---------- Bottom: Strategic Summary (2-col bullets) ----------
    bot_x, bot_y, bot_w, bot_h = 5.0, 4.0, 90.0, 13.0
    ax.add_patch(FancyBboxPatch(
        (bot_x, bot_y), bot_w, bot_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((bot_x, bot_y), 0.5, bot_h,
                              facecolor=COLORS["pfizer_blue"], linewidth=0, zorder=2))

    ax.text(bot_x + 1.5, bot_y + bot_h - 1.3,
             "Strategic Summary",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")

    bullets = n.get("strategic_summary", [])
    col_w = (bot_w - 3.0) / 2
    bullet_y_start = bot_y + bot_h - 3.4
    line_step = 1.25
    bullet_gap = 0.45

    # Two-column layout — track y per column
    col_ys = [bullet_y_start, bullet_y_start]
    for i, bullet in enumerate(bullets):
        col = i % 2
        x = bot_x + 1.5 + col * col_w
        y = col_ys[col]
        ax.text(x, y, "→", fontsize=10, color=COLORS["pfizer_blue"],
                 fontweight="bold", va="top")
        wrapped = textwrap.wrap(bullet, width=62)
        for j, line in enumerate(wrapped):
            ax.text(x + 1.5, y - j * line_step, line,
                     fontsize=9, color=COLORS["viti_dark"], va="top")
        col_ys[col] = y - len(wrapped) * line_step - bullet_gap

    draw_source(ax,
                 "Source: IQVIA, Region master + Quadrant summary (Workbook v30), "
                 "AVA patient-level data 2026-05, Viti Science composite analysis.")

    plt.savefig(out_path(d["region_short"], "R6_competitive_strategic"),
                facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path(d['region_short'], 'R6_competitive_strategic')}")


if __name__ == "__main__":
    render_r6("Region Stockholm")
