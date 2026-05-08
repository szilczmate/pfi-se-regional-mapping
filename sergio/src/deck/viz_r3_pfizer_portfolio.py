# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R3 — Pfizer Product Portfolio dashboard (regional profile slide 3 of 6).

Layout:
  Top band:    Total Pfizer footprint (3yr SEK) with category split bar.
  Bottom row:  3 category cards (Vaccines / RD-IM / Oncology) listing top products.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source,
                                 fmt_msek, out_path)
from region_data import get_region
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


def render_r3(region_full_name):
    d = get_region(region_full_name)
    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGION PROFILE  ·  PART B",
                title=d["region_short"],
                subtitle="Pfizer Product Portfolio")

    # --- Top band: Total + category split ---
    band_y = 32.0
    band_h = 12.0
    band_x = 5.0
    band_w = 90.0

    # Card body
    ax.add_patch(FancyBboxPatch(
        (band_x, band_y), band_w, band_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((band_x, band_y), 0.5, band_h,
                              facecolor=COLORS["pfizer_blue"],
                              linewidth=0, zorder=2))

    ax.text(band_x + 1.5, band_y + band_h - 1.5,
             "Total Pfizer Footprint",
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(band_x + 1.5, band_y + band_h - 4.0,
             f"{d['pfizer_total_3yr']/1e6:,.0f}M kr",
             fontsize=34, color=COLORS["pfizer_blue"],
             fontweight="bold", va="top")
    ax.text(band_x + 1.5, band_y + band_h - 9.5,
             f"3-year IQVIA Sell-In SEK · Sweden rank #{int(d['pfizer_rank'])}",
             fontsize=10, color=COLORS["viti_gray"], va="top")

    # Category split horizontal bar (right side of top band)
    cat_x = band_x + 28.0
    cat_y = band_y + 4.0
    cat_w = band_w - 30.0
    cat_h = 3.5

    total = d["pfizer_total_3yr"]
    cats = [
        ("Vaccines", d["pfizer_vaccines_3yr"], COLORS["pfizer_blue"]),
        ("RD/IM",    d["pfizer_rdim_3yr"],     COLORS["competitor_charcoal"]),
        ("Oncology", d["pfizer_oncology_3yr"], COLORS["competitor_gray"]),
    ]
    cumulative = 0
    for name, sek, col in cats:
        seg_w = sek / total * cat_w
        ax.add_patch(Rectangle((cat_x + cumulative, cat_y), seg_w, cat_h,
                                  facecolor=col, edgecolor="white",
                                  linewidth=2, zorder=3))
        # Inline label if wide enough
        if seg_w > 8:
            ax.text(cat_x + cumulative + seg_w / 2, cat_y + cat_h / 2,
                     f"{name}\n{sek/1e6:,.0f}M kr  ·  {sek/total*100:.0f}%",
                     ha="center", va="center", color="white",
                     fontsize=10, fontweight="bold", zorder=4)
        cumulative += seg_w

    # Category bar header
    ax.text(cat_x, cat_y + cat_h + 1.5, "Category split (3-year SEK)",
             fontsize=10, color=COLORS["viti_dark"],
             fontweight="semibold", va="bottom")

    # --- Bottom: 3 category cards ---
    card_w = 28.5
    card_h = 22.0
    gap = 1.7
    bot_y = 4.0
    cat_xs = [5.0, 5.0 + card_w + gap, 5.0 + 2 * (card_w + gap)]

    # Compute per-category top products
    vaccines_products = [
        ("FSME-IMMUN VUXEN", d["fsme_vuxen_3yr"]),
        ("FSME-IMMUN JUNIOR", d["fsme_junior_3yr"]),
        ("Abrysvo", d["abrysvo_3yr"]),
        ("Prevenar 20", d["prevenar20_3yr"]),
    ]
    rdim_products = [
        ("Vyndaqel", d["vyndaqel_3yr"]),
        ("Vydura", d["vydura_3yr"]),
        ("BeneFIX (haem.)", d["benefix_3yr"]),
        ("Refacto AF", d["refacto_3yr"]),
    ]
    oncology_products = [
        ("Xtandi (co-mkt Astellas)", d["xtandi_3yr"]),
        ("Ibrance", d["ibrance_3yr"]),
        ("Elrexfio", d["elrexfio_3yr"]),
        ("Lorviqua", d["lorviqua_3yr"]),
        ("Tukysa", d["tukysa_3yr"]),
        ("Talzenna", d["talzenna_3yr"]),
    ]

    sections = [
        ("Vaccines",  d["pfizer_vaccines_3yr"],  vaccines_products,  COLORS["pfizer_blue"]),
        ("RD / IM",    d["pfizer_rdim_3yr"],     rdim_products,      COLORS["competitor_charcoal"]),
        ("Oncology",  d["pfizer_oncology_3yr"],  oncology_products,  COLORS["competitor_gray"]),
    ]

    for x, (name, total_sek, products, col) in zip(cat_xs, sections):
        # Card body
        ax.add_patch(FancyBboxPatch(
            (x, bot_y), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=1.0",
            linewidth=0.6, edgecolor=COLORS["viti_medium"],
            facecolor="#FFFFFF", zorder=1,
        ))
        ax.add_patch(Rectangle((x, bot_y), 0.5, card_h,
                                  facecolor=col, linewidth=0, zorder=2))

        # Title
        ax.text(x + 1.5, bot_y + card_h - 1.5,
                 name,
                 fontsize=13, color=COLORS["viti_dark"],
                 fontweight="bold", va="top")
        # Subtotal
        ax.text(x + 1.5, bot_y + card_h - 4.0,
                 f"{total_sek/1e6:,.0f}M kr",
                 fontsize=22, color=col,
                 fontweight="bold", va="top")
        ax.text(x + 1.5, bot_y + card_h - 7.5,
                 "3-year Sell-In SEK",
                 fontsize=9, color=COLORS["viti_gray"], va="top")

        # Product list — fit up to 6 cleanly within the card body
        # Available vertical space: roughly card_h - 11 (header) down to bot_y + 1 (footer pad)
        py = bot_y + card_h - 11.0
        list_bottom = bot_y + 1.0  # leave 1 unit pad above card edge
        sorted_products = sorted([(n, s) for n, s in products if s and s > 0],
                                   key=lambda t: -t[1])
        # Tighter row_step so 6 entries fit
        n_show = min(len(sorted_products), 6)
        avail = py - list_bottom
        row_step = avail / max(n_show, 1)
        # Cap row_step to avoid huge gaps when fewer than 6 entries
        row_step = min(row_step, 2.4)
        for prod_name, sek in sorted_products[:6]:
            pct = sek / total_sek * 100 if total_sek else 0
            ax.text(x + 1.5, py, prod_name,
                     fontsize=9.5, color=COLORS["viti_dark"], va="top")
            ax.text(x + card_w - 1.0, py, f"{sek/1e6:,.0f}M  ·  {pct:.0f}%",
                     fontsize=9.5, color=COLORS["viti_gray"],
                     va="top", ha="right")
            py -= row_step

    draw_source(ax,
                 "Source: IQVIA Sell-In SEK monthly Apr 2023–Mar 2026 (Vaccines, RD/IM, Oncology). "
                 "Xtandi co-marketed with Astellas; counted in oncology total per Pfizer convention.")

    plt.savefig(out_path(d["region_short"], "R3_pfizer_portfolio"),
                facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path(d['region_short'], 'R3_pfizer_portfolio')}")


if __name__ == "__main__":
    render_r3("Region Stockholm")
