# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R4 — Vaccine Landscape dashboard (regional profile slide 4 of 6).

Layout:
  Left half: 3 vaccine class mini-cards (TBE / RSV / Pneumococcal),
             each with Pfizer share %, total market, Pfizer SEK + 1-line context.
  Top-right: Regional Vaccination Coverage (KPI card)
  Bottom-right: Market Penetration narrative
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source,
                                 draw_kpi_card, draw_narrative_card,
                                 fmt_pct, out_path)
from region_data import get_region
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


def vaccine_card(ax, x, y, w, h, name, brand, total_sek, pfizer_sek,
                   pfizer_share, context_line, accent):
    """Single vaccine class card showing share + market split."""
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.8",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((x, y), 0.5, h, facecolor=accent,
                              linewidth=0, zorder=2))

    # Title row
    ax.text(x + 1.5, y + h - 1.3, f"{name}",
             fontsize=12, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(x + 1.5, y + h - 3.2, f"{brand}",
             fontsize=9, color=COLORS["viti_gray"], va="top")

    # Big share % on right
    ax.text(x + w - 1.5, y + h - 1.3,
             f"{pfizer_share:.1f}%",
             fontsize=22, color=accent,
             fontweight="bold", va="top", ha="right")
    ax.text(x + w - 1.5, y + h - 5.0,
             "Pfizer share",
             fontsize=9, color=COLORS["viti_gray"],
             va="top", ha="right")

    # Share bar
    bar_x = x + 1.5
    bar_y = y + 2.4
    bar_w = w - 3.0
    bar_h = 1.2
    ax.add_patch(Rectangle((bar_x, bar_y), bar_w, bar_h,
                              facecolor=COLORS["viti_light"],
                              linewidth=0, zorder=2))
    ax.add_patch(Rectangle((bar_x, bar_y),
                              bar_w * pfizer_share / 100, bar_h,
                              facecolor=accent, linewidth=0, zorder=3))

    # Numbers below bar
    ax.text(bar_x, bar_y - 0.5,
             f"Pfizer  {pfizer_sek/1e6:,.0f}M kr",
             fontsize=9, color=COLORS["viti_dark"],
             fontweight="semibold", va="top")
    ax.text(bar_x + bar_w, bar_y - 0.5,
             f"Total market  {total_sek/1e6:,.0f}M kr",
             fontsize=9, color=COLORS["viti_gray"],
             va="top", ha="right")

    # Context line
    ax.text(x + 1.5, y + h - 6.7, context_line,
             fontsize=9, color=COLORS["viti_dark"],
             va="top", style="italic")


def render_r4(region_full_name):
    d = get_region(region_full_name)
    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGION PROFILE  ·  PART B",
                title=d["region_short"],
                subtitle="Vaccine Landscape")

    # --- Left: 3 vaccine product cards ---
    left_x = 5.0
    card_w = 42.0
    card_h = 11.0
    gap = 1.5
    top_card_y = 31.0
    mid_card_y = top_card_y - card_h - gap
    bot_card_y = mid_card_y - card_h - gap

    # TBE — note that NaN in TBE cases means FoHM did not report counts for this region,
    # not that TBE isn't endemic. Many northern regions have TBE risk without FoHM aggregate counts.
    if d["tbe_cases_2025"] == d["tbe_cases_2025"]:
        tbe_context = (f"{int(d['tbe_cases_2025'])} TBE cases (2025), "
                       f"{d['tbe_per100k_2025']:.1f}/100k. Endemic area, Pfizer dominant.")
    elif d["tbe_pfizer_share"] >= 50:
        tbe_context = "Established market. Pfizer dominant share."
    else:
        tbe_context = "Maintenance market. ENCEPUR competition."
    vaccine_card(ax, left_x, top_card_y, card_w, card_h,
                  "TBE", "FSME-IMMUN VUXEN + JUNIOR",
                  d["tbe_market_total"], d["tbe_pfizer_sek"],
                  d["tbe_pfizer_share"], tbe_context,
                  COLORS["pfizer_blue"])

    # RSV
    rsv_context = "Growing market. 65+ population is the key target — demographic tailwind."
    vaccine_card(ax, left_x, mid_card_y, card_w, card_h,
                  "RSV", "Abrysvo",
                  d["rsv_market_total"], d["rsv_pfizer_sek"],
                  d["rsv_pfizer_share"], rsv_context,
                  COLORS["pfizer_blue"])

    # Pneumococcal
    pneu_context = (f"{int(d['ipd_cases_2025'])} IPD cases (2025) — {'gap opportunity' if d['pneu_pfizer_share'] < 25 else 'leadership position'}."
                    if d["ipd_cases_2025"] == d["ipd_cases_2025"]
                    else "Adult pneumococcal market — 65+ target.")
    vaccine_card(ax, left_x, bot_card_y, card_w, card_h,
                  "Pneumococcal", "Prevenar 20",
                  d["pneu_market_total"], d["pneu_pfizer_sek"],
                  d["pneu_pfizer_share"], pneu_context,
                  COLORS["pfizer_blue"])

    # --- Right top: Coverage card ---
    right_x = 51.0
    coverage_h = 16.5
    coverage_y = 27.0
    coverage_kpis = [
        (fmt_pct(d["mpr_2yo_pct"]), "MPR 2yo"),
        (fmt_pct(d["hpv_girls_pct"]), "HPV girls"),
        (f"{int(d['vaccine_sellin_per_capita'])} SEK", "Vaccine sell-in / capita"),
        (f"{int(d['antibiotic_rx_per1000'])}/1k", "Antibiotic Rx rate"),
    ]
    draw_kpi_card(ax, right_x, coverage_y, 44.0, coverage_h,
                   "Regional Vaccination Coverage", coverage_kpis,
                   accent_color=COLORS["competitor_charcoal"],
                   n_cols=2, value_fontsize=18, label_fontsize=10)

    # --- Right bottom: Penetration narrative ---
    pen_y = 4.0
    pen_h = 21.0

    # Determine narrative text from share thresholds
    tbe_str = (f"TBE (FSME-IMMUN): Pfizer share {d['tbe_pfizer_share']:.1f}%. "
               + ("Dominant — defend." if d['tbe_pfizer_share'] > 60
                  else "Maintain position." if d['tbe_pfizer_share'] > 30
                  else "Limited market presence."))
    rsv_str = (f"RSV (Abrysvo): Pfizer share {d['rsv_pfizer_share']:.1f}%. "
               + ("Strong launch traction." if d['rsv_pfizer_share'] > 50
                  else "Building share."))
    pneu_str = (f"Pneumococcal (Prevenar 20): Pfizer share {d['pneu_pfizer_share']:.1f}%. "
                + ("Gap opportunity — adult 65+ untapped." if d['pneu_pfizer_share'] < 25
                   else "Established position."))
    sellin_pct_above_or_below = ("above" if d["vaccine_sellin_per_capita"] > 70
                                  else "below")

    bullets = [
        tbe_str,
        rsv_str,
        pneu_str,
        f"Vaccine sell-in per capita ({int(d['vaccine_sellin_per_capita'])} SEK) sits {sellin_pct_above_or_below} the Sweden median — capacity for expansion in the under-served class.",
    ]

    draw_narrative_card(ax, right_x, pen_y, 44.0, pen_h,
                         "Market Penetration & Opportunity",
                         bullets,
                         accent_color=COLORS["competitor_charcoal"],
                         body_fontsize=10, line_step=1.55, wrap_width=58)

    draw_source(ax,
                 "Source: IQVIA Sweden Sell-In SEK 3-year aggregate (Apr 2023–Mar 2026), "
                 "Folkhälsomyndigheten Vaccination Coverage 2024, Folkhälsomyndigheten "
                 "Infectious Disease Surveillance 2025.")

    plt.savefig(out_path(d["region_short"], "R4_vaccine_landscape"),
                facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path(d['region_short'], 'R4_vaccine_landscape')}")


if __name__ == "__main__":
    render_r4("Region Stockholm")
