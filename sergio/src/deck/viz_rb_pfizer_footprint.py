# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R-B — Pfizer Commercial Footprint (compressed R3 + R4 in 4-slide format).

Layout:
  Header             eyebrow + title + 1-line takeaway
  Total band         Total Pfizer SEK + category split bar (Vac/RDIM/Onc)
  3 category cards   Vaccines (folds in class shares) │ RD/IM │ Oncology
  Coverage strip     MPR · HPV · Vaccine sell-in/cap · Antibiotic Rx
  + 1-line takeaway

Output: delivery/figures/region_profiles/<region>/RB_pfizer_footprint.png
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import make_canvas, out_path
from region_data import get_region, get_region_ranks
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


def render_rb(region_full_name):
    d = get_region(region_full_name)
    ranks = get_region_ranks(region_full_name)

    fig, ax = make_canvas()

    # ---------- Header ----------
    ax.add_patch(Rectangle((0, 56.0), 100, 0.25,
                              facecolor=COLORS["pfizer_blue"], linewidth=0))
    ax.text(5.0, 53.5, f"REGION PROFILE  ·  {d['region_short'].upper()}  ·  PFIZER FOOTPRINT",
             fontsize=10, color=COLORS["viti_blue"],
             fontweight="semibold", va="top")
    ax.text(5.0, 52.0, d["region_short"],
             fontsize=22, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(5.0, 47.5,
             f"3-year IQVIA Sell-In SEK across Vaccines + RD/IM + Oncology  ·  Sweden rank #{int(ranks.get('Total Pfizer SEK', 0))}",
             fontsize=10.5, color=COLORS["viti_gray"], va="top")

    # ---------- Total band: Big number + category split bar ----------
    band_y = 36.0
    band_h = 9.0
    band_x = 5.0
    band_w = 90.0
    ax.add_patch(FancyBboxPatch(
        (band_x, band_y), band_w, band_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0,
        facecolor=COLORS["viti_light"], zorder=1,
    ))
    ax.add_patch(Rectangle((band_x, band_y), 0.5, band_h,
                              facecolor=COLORS["pfizer_blue"], linewidth=0))

    # Big number on left
    ax.text(band_x + 1.5, band_y + band_h - 1.5, "Total Pfizer Footprint",
             fontsize=11, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(band_x + 1.5, band_y + band_h - 3.5,
             f"{d['pfizer_total_3yr']/1e6:,.0f}M kr",
             fontsize=30, color=COLORS["pfizer_blue"],
             fontweight="bold", va="top")
    ax.text(band_x + 1.5, band_y + 1.0,
             "3-year Sell-In SEK",
             fontsize=8.5, color=COLORS["viti_gray"], va="bottom")

    # Stacked category bar on right
    bar_x = band_x + 26.0
    bar_y_pos = band_y + band_h / 2 - 1.5
    bar_w = band_w - 30.0
    bar_h = 3.0

    total = d["pfizer_total_3yr"]
    cats = [
        ("Vaccines", d["pfizer_vaccines_3yr"], COLORS["pfizer_blue"]),
        ("RD / IM",  d["pfizer_rdim_3yr"],     COLORS["competitor_charcoal"]),
        ("Oncology", d["pfizer_oncology_3yr"], COLORS["competitor_gray"]),
    ]
    cumulative = 0
    for name, sek, col in cats:
        seg_w = sek / total * bar_w
        ax.add_patch(Rectangle((bar_x + cumulative, bar_y_pos), seg_w, bar_h,
                                  facecolor=col, edgecolor="white",
                                  linewidth=2, zorder=3))
        # Adapt label depth to segment width: full inline if wide, name-only
        # if narrow, callout below if very narrow
        full_label = f"{name}  ·  {sek/1e6:,.0f}M  ·  {sek/total*100:.0f}%"
        short_label = f"{name}  {sek/total*100:.0f}%"
        if seg_w >= 17:
            ax.text(bar_x + cumulative + seg_w / 2, bar_y_pos + bar_h / 2,
                     full_label,
                     ha="center", va="center", color="white",
                     fontsize=10, fontweight="bold", zorder=4)
        elif seg_w > 6:
            ax.text(bar_x + cumulative + seg_w / 2, bar_y_pos + bar_h / 2,
                     short_label,
                     ha="center", va="center", color="white",
                     fontsize=9, fontweight="bold", zorder=4)
        else:
            # Very narrow — callout below the bar
            ax.text(bar_x + cumulative + seg_w / 2, bar_y_pos - 0.6,
                     short_label,
                     ha="center", va="top", color=col,
                     fontsize=9, fontweight="bold", zorder=4)
        cumulative += seg_w

    ax.text(bar_x, band_y + band_h - 1.5, "Category split (3-year SEK)",
             fontsize=10, color=COLORS["viti_dark"],
             fontweight="semibold", va="top")

    # ---------- 3 category cards ----------
    card_w = 28.5
    card_h = 23.0
    gap = 1.7
    card_y = 9.5
    cat_xs = [5.0, 5.0 + card_w + gap, 5.0 + 2 * (card_w + gap)]

    # Vaccines: products + class shares folded in
    vaccines_products = [
        ("FSME-IMMUN VUXEN", d["fsme_vuxen_3yr"]),
        ("FSME-IMMUN JUNIOR", d["fsme_junior_3yr"]),
        ("Abrysvo (RSV)", d["abrysvo_3yr"]),
        ("Prevenar 20", d["prevenar20_3yr"]),
    ]
    vaccines_shares = [
        ("TBE", d["tbe_pfizer_share"], d["tbe_market_total"], d["tbe_pfizer_sek"]),
        ("RSV", d["rsv_pfizer_share"], d["rsv_market_total"], d["rsv_pfizer_sek"]),
        ("Pneu", d["pneu_pfizer_share"], d["pneu_market_total"], d["pneu_pfizer_sek"]),
    ]

    rdim_products = [
        ("Vyndaqel", d["vyndaqel_3yr"]),
        ("Vydura", d["vydura_3yr"]),
        ("BeneFIX (haem.)", d["benefix_3yr"]),
        ("Refacto AF", d["refacto_3yr"]),
    ]
    oncology_products = [
        ("Xtandi (co-Astellas)", d["xtandi_3yr"]),
        ("Ibrance", d["ibrance_3yr"]),
        ("Elrexfio", d["elrexfio_3yr"]),
        ("Lorviqua", d["lorviqua_3yr"]),
        ("Tukysa", d["tukysa_3yr"]),
        ("Talzenna", d["talzenna_3yr"]),
    ]

    def draw_category_card(x, y, name, total_sek, products, accent,
                            class_shares=None):
        ax.add_patch(FancyBboxPatch(
            (x, y), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=1.0",
            linewidth=0.6, edgecolor=COLORS["viti_medium"],
            facecolor="#FFFFFF", zorder=1,
        ))
        ax.add_patch(Rectangle((x, y), 0.5, card_h,
                                  facecolor=accent, linewidth=0))
        # Title
        ax.text(x + 1.5, y + card_h - 1.5, name,
                 fontsize=12, color=COLORS["viti_dark"],
                 fontweight="bold", va="top")
        # Subtotal
        ax.text(x + 1.5, y + card_h - 3.8,
                 f"{total_sek/1e6:,.0f}M kr",
                 fontsize=20, color=accent,
                 fontweight="bold", va="top")
        ax.text(x + 1.5, y + card_h - 7.0,
                 "3-year Sell-In SEK",
                 fontsize=8.5, color=COLORS["viti_gray"], va="top")

        # If class shares provided (Vaccines), show them as compact rows
        # at the top of the card
        next_y = y + card_h - 9.0
        if class_shares:
            ax.text(x + 1.5, next_y, "Class share",
                     fontsize=8.5, color=COLORS["viti_blue"],
                     fontweight="semibold", va="top")
            next_y -= 1.5
            for class_name, share, market, pfizer in class_shares:
                ax.text(x + 1.5, next_y, class_name,
                         fontsize=9, color=COLORS["viti_dark"],
                         fontweight="semibold", va="top")
                share_str = f"{share:.0f}%" if share == share else "—"
                ax.text(x + card_w - 1.0, next_y, share_str,
                         fontsize=9.5, color=accent,
                         fontweight="bold", va="top", ha="right")
                next_y -= 1.5
            next_y -= 0.3
            # Divider
            ax.add_patch(Rectangle((x + 1.5, next_y), card_w - 3.0, 0.04,
                                      facecolor=COLORS["viti_medium"],
                                      linewidth=0))
            next_y -= 1.4

        # Top products section header
        ax.text(x + 1.5, next_y, "Top products",
                 fontsize=8.5, color=COLORS["viti_blue"],
                 fontweight="semibold", va="top")
        next_y -= 1.5

        # Product list
        sorted_products = sorted([(n, s) for n, s in products if s and s > 0],
                                   key=lambda t: -t[1])
        avail = next_y - (y + 1.0)
        n_show = min(len(sorted_products), 6)
        row_step = avail / max(n_show, 1)
        row_step = min(row_step, 2.4)
        for prod_name, sek in sorted_products[:6]:
            pct = sek / total_sek * 100 if total_sek else 0
            ax.text(x + 1.5, next_y, prod_name,
                     fontsize=9, color=COLORS["viti_dark"], va="top")
            ax.text(x + card_w - 1.0, next_y,
                     f"{sek/1e6:,.0f}M  ·  {pct:.0f}%",
                     fontsize=9, color=COLORS["viti_gray"],
                     va="top", ha="right")
            next_y -= row_step

    draw_category_card(cat_xs[0], card_y, "Vaccines",
                        d["pfizer_vaccines_3yr"], vaccines_products,
                        COLORS["pfizer_blue"], class_shares=vaccines_shares)
    draw_category_card(cat_xs[1], card_y, "RD / IM",
                        d["pfizer_rdim_3yr"], rdim_products,
                        COLORS["competitor_charcoal"])
    draw_category_card(cat_xs[2], card_y, "Oncology",
                        d["pfizer_oncology_3yr"], oncology_products,
                        COLORS["competitor_gray"])

    # ---------- Coverage strip ----------
    strip_y = 4.0
    strip_h = 4.5
    ax.add_patch(FancyBboxPatch(
        (5.0, strip_y), 90.0, strip_h,
        boxstyle="round,pad=0,rounding_size=0.8",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor=COLORS["viti_light"], zorder=1,
    ))
    ax.text(6.5, strip_y + strip_h - 0.7,
             "COVERAGE & ACCESS  ·  Population baseline",
             fontsize=8.5, color=COLORS["viti_blue"],
             fontweight="bold", va="top")

    # 4 KPI tiles in the strip
    cov_kpis = [
        (f"{d['mpr_2yo_pct']:.0f}%",   "MPR 2yo coverage"),
        (f"{d['hpv_girls_pct']:.0f}%", "HPV girls coverage"),
        (f"{int(d['vaccine_sellin_per_capita'])} SEK", "Vaccine sell-in / cap"),
        (f"{int(d['antibiotic_rx_per1000'])}/1k", "Antibiotic Rx rate"),
    ]
    tile_w = 88.0 / 4
    for i, (val, lbl) in enumerate(cov_kpis):
        tx = 6.5 + i * tile_w
        ax.text(tx, strip_y + strip_h - 2.4, val,
                 fontsize=14, color=COLORS["viti_dark"],
                 fontweight="bold", va="top")
        ax.text(tx, strip_y + strip_h - 4.1, lbl,
                 fontsize=8.5, color=COLORS["viti_gray"], va="top")

    # ---------- Source ----------
    ax.text(5.0, 1.5,
             "Source: IQVIA Sweden Sell-In SEK monthly Apr 2023–Mar 2026 (Vaccines, RD/IM, Oncology); "
             "Folkhälsomyndigheten Vaccination Coverage 2024 (MPR, HPV); Workbook v30 \"Pfizer total footprint\" + \"Vaccine market share\". "
             "Xtandi co-marketed with Astellas; counted in oncology total per Pfizer convention.",
             fontsize=7.5, color=COLORS["viti_gray"], va="bottom")

    out_p = out_path(d["region_short"], "compact_2_pfizer_footprint")
    plt.savefig(out_p, facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_p}")


if __name__ == "__main__":
    render_rb("Region Stockholm")
    render_rb("Region Västerbotten")
