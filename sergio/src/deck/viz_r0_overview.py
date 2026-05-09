# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R0 — Sweden 21-region overview / scorecard (regional mapping cover).

Anchors the prime directive deliverable: the regional mapping covers all 21
Swedish regions across consistent dimensions. Stockholm and Västerbotten are
shown in full R1–R6 detail as exemplars; the same template scales to the
other 19 regions.

Output: delivery/figures/region_profiles/_overview/R0_21_region_scorecard.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source)
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v30.xlsx"

# Exemplar regions deep-dived in R1–R6
EXEMPLARS = {"Region Stockholm", "Region Västerbotten"}


def render_r0():
    rm = pd.read_excel(WB, sheet_name="Region master")
    pf = pd.read_excel(WB, sheet_name="Pfizer total footprint")
    pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
    pf = pf.dropna(subset=["Region"])
    tp = pd.read_excel(WB, sheet_name="Top product per region")

    m = (rm.merge(pf[["Region", "Total Pfizer SEK", "Pfizer SEK rank"]], on="Region")
            .merge(tp[["Region", "Top Pfizer product"]], on="Region"))
    m = m.sort_values("Total Pfizer SEK", ascending=False).reset_index(drop=True)

    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGIONAL MAPPING  ·  PART A  ·  OVERVIEW",
                title="Sweden — 21 regions mapped",
                subtitle="Six dimensions per region. Stockholm and Västerbotten shown in full R1–R6 detail; same template scales across the remaining nineteen.")

    # ---------- Top: 4 summary stat cards ----------
    cards = [
        ("21",   "Regions mapped",
         "Across 6 healthcare regions (sjukvårdsregioner)"),
        (f"{int(m['Population'].sum() / 1e6 * 10) / 10}M",
         "Total population covered",
         "10.6M inhabitants — the entire Swedish patient base"),
        (f"{m['Total Pfizer SEK'].sum() / 1e9:.1f}B kr",
         "Total Pfizer Sell-In · 3 yr",
         "IQVIA across Vaccines + RD/IM + Oncology"),
        ("138",  "Stakeholders mapped",
         "Verified or HIGH-confidence reach for 92%"),
    ]
    n = 4
    gap = 1.2
    card_w = (90 - gap * (n - 1)) / n
    card_h = 9.5
    card_y = 33.0
    for i, (big, lbl, sub) in enumerate(cards):
        cx = 5.0 + i * (card_w + gap)
        ax.add_patch(FancyBboxPatch(
            (cx, card_y), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=1.0",
            linewidth=0,
            facecolor=COLORS["viti_light"], zorder=1))
        ax.add_patch(Rectangle((cx, card_y + card_h - 0.4), card_w, 0.4,
                                  facecolor=COLORS["pfizer_blue"],
                                  linewidth=0, zorder=2))
        ax.text(cx + card_w / 2, card_y + card_h - 2.5, big,
                 ha="center", va="center",
                 fontsize=22, color=COLORS["pfizer_blue"],
                 fontweight="bold", zorder=3)
        ax.text(cx + card_w / 2, card_y + card_h - 5.0, lbl,
                 ha="center", va="center",
                 fontsize=10, color=COLORS["viti_dark"],
                 fontweight="semibold", zorder=3)
        # Wrap sub
        import textwrap
        sub_lines = textwrap.wrap(sub, width=30)
        for j, line in enumerate(sub_lines):
            ax.text(cx + card_w / 2, card_y + card_h - 6.8 - j * 1.4, line,
                     ha="center", va="center",
                     fontsize=8.5, color=COLORS["viti_gray"], zorder=3)

    # ---------- Bottom: 21-region ranked table ----------
    table_x = 5.0
    table_y = 3.0
    table_w = 90.0
    table_h = 28.0

    # Card body
    ax.add_patch(FancyBboxPatch(
        (table_x, table_y), table_w, table_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1))
    ax.add_patch(Rectangle((table_x, table_y), 0.5, table_h,
                              facecolor=COLORS["pfizer_blue"],
                              linewidth=0, zorder=2))

    ax.text(table_x + 1.5, table_y + table_h - 1.4,
             "21-region ranked overview",
             fontsize=12, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(table_x + 1.5, table_y + table_h - 3.0,
             "Sorted by Pfizer 3-year Sell-In SEK · ★ = R1–R6 deep-dive in this set",
             fontsize=9, color=COLORS["viti_gray"], va="top")

    # Column layout — 2 columns of 11+10 rows
    col_width = (table_w - 3.0) / 2
    rows_per_col = 11

    # Header row
    header_y = table_y + table_h - 5.0
    headers = [
        ("#",        2.5),
        ("Region",   16.0),
        ("Pop",      8.0),
        ("Pfizer 3yr", 8.5),
        ("Top product", 12.0),
    ]
    for col_i in range(2):
        cx_offset = table_x + 1.5 + col_i * col_width
        col_x = cx_offset
        for label, width in headers:
            ax.text(col_x, header_y, label,
                     fontsize=8.5, color=COLORS["viti_blue"],
                     fontweight="bold", va="bottom")
            col_x += width

    # Header rule
    ax.add_patch(Rectangle((table_x + 1.5, header_y - 0.4),
                              table_w - 3.0, 0.05,
                              facecolor=COLORS["viti_medium"],
                              linewidth=0, zorder=3))

    # Data rows
    row_y_start = header_y - 1.6
    row_step = 1.85
    for idx, row in m.iterrows():
        col_i = 0 if idx < rows_per_col else 1
        row_in_col = idx if col_i == 0 else idx - rows_per_col
        ry = row_y_start - row_in_col * row_step
        col_x_offset = table_x + 1.5 + col_i * col_width

        is_exemplar = row["Region"] in EXEMPLARS
        text_color = COLORS["pfizer_blue"] if is_exemplar else COLORS["viti_dark"]
        weight = "bold" if is_exemplar else "regular"
        marker = "★" if is_exemplar else " "

        # Alternating row stripe
        if idx % 2 == 1:
            ax.add_patch(Rectangle((col_x_offset - 0.3, ry - 1.0),
                                      col_width - 1.5, row_step,
                                      facecolor=COLORS["viti_light"],
                                      alpha=0.5,
                                      linewidth=0, zorder=2))

        cx = col_x_offset
        # Rank
        ax.text(cx, ry, f"{int(row['Pfizer SEK rank'])}",
                 fontsize=9, color=text_color, fontweight=weight,
                 va="top", zorder=3)
        cx += 2.5
        # Region (drop "Region " prefix, trim long names)
        region_display = (row["Region"]
                          .replace("Region ", "")
                          .replace("Västra Götalandsregionen", "Västra Götaland")
                          .replace("Region Jämtland Härjedalen", "Jämtland H."))
        # Truncate
        if len(region_display) > 18:
            region_display = region_display[:18]
        ax.text(cx, ry, f"{marker} {region_display}",
                 fontsize=9, color=text_color, fontweight=weight,
                 va="top", zorder=3)
        cx += 16.0
        # Population
        pop_str = f"{int(row['Population'] / 1000):,}k"
        ax.text(cx, ry, pop_str,
                 fontsize=9, color=text_color, fontweight=weight,
                 va="top", zorder=3)
        cx += 8.0
        # Pfizer SEK 3yr
        sek_str = f"{row['Total Pfizer SEK'] / 1e6:,.0f}M"
        ax.text(cx, ry, sek_str,
                 fontsize=9, color=text_color, fontweight=weight,
                 va="top", zorder=3)
        cx += 8.5
        # Top product
        top_p = row["Top Pfizer product"] or "—"
        if len(top_p) > 24:
            top_p = top_p[:24]
        ax.text(cx, ry, top_p,
                 fontsize=8.5, color=COLORS["viti_gray"],
                 va="top", zorder=3)

    draw_source(ax,
                 "Source: SCB (Population), IQVIA Sell-In SEK Apr 2023–Mar 2026 (Vaccines + RD/IM + Oncology), "
                 "Workbook v30 \"Top product per region\". ★ = exemplar regions with full R1–R6 deep-dive in this delivery.")

    out_dir = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "R0_21_region_scorecard.png"
    plt.savefig(out_path, facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    render_r0()
