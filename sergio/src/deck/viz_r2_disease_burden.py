# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R2 — Disease Burden & Epidemiology dashboard (regional profile slide 2 of 6).

4 cards:
  Top-left:   Cancer Burden (KPI grid 3x3)
  Bottom-left: Infectious Disease Epidemiology (KPI grid 3x3)
  Top-right:  Pipeline Therapeutic Areas (narrative bullets)
  Bottom-right: Cardiovascular & Rare Disease (narrative bullets)
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import (make_canvas, draw_header, draw_source,
                                 draw_kpi_card, draw_narrative_card,
                                 fmt_int, fmt_pct, out_path)
from region_data import get_region, get_narratives
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


def render_r2(region_full_name):
    d = get_region(region_full_name)
    n = get_narratives(region_full_name)

    fig, ax = make_canvas()
    draw_header(ax,
                eyebrow="REGION PROFILE  ·  PART B",
                title=d["region_short"],
                subtitle="Disease Burden & Epidemiology")

    card_w = 43.0
    card_h = 17.0
    left_x, right_x = 5.0, 52.0
    top_y, bot_y = 27.0, 8.5

    # Cancer Burden KPIs (3 cols × 3 rows = 9 tiles)
    cancer_kpis = [
        (f"{d['breast_ca_rate']:.1f}/100k", "Breast cancer rate"),
        (f"{d['prostate_ca_rate']:.1f}/100k", "Prostate cancer rate"),
        (f"{d['lung_ca_incidence']:.1f}/100k", "Lung cancer rate"),
        (f"~{int(d['breast_implied_cases']):,}", "Implied breast cases"),
        (f"~{int(d['prostate_implied_cases']):,}", "Implied prostate cases"),
        (f"~{int(d['lung_implied_cases']):,}", "Implied lung cases"),
        (fmt_pct(d["breast_screening_pct"]), "Breast screening detect"),
        (fmt_pct(d["breast_surg_28d_pct"]), "Breast surgery <28 days"),
        (f"{d['lung_ca_mortality']:.1f}/100k", "Lung cancer mortality"),
    ]
    draw_kpi_card(ax, left_x, top_y, card_w, card_h,
                   "Cancer Burden", cancer_kpis, n_cols=3,
                   value_fontsize=13, label_fontsize=8.5)

    # Infectious Disease KPIs (3x3, but TBE/IPD may be NaN for non-endemic regions)
    tbe_cases_str = fmt_int(d["tbe_cases_2025"])
    tbe_per100k_str = (f"{d['tbe_per100k_2025']:.1f}/100k"
                       if d["tbe_per100k_2025"] == d["tbe_per100k_2025"] else "—")
    ipd_cases_str = fmt_int(d["ipd_cases_2025"])
    ipd_per100k_str = (f"{d['ipd_per100k_2025']:.1f}/100k"
                       if d["ipd_per100k_2025"] == d["ipd_per100k_2025"] else "—")

    infect_kpis = [
        (tbe_cases_str, "TBE cases 2025"),
        (tbe_per100k_str, "TBE incidence"),
        (ipd_cases_str, "IPD cases 2025"),
        (ipd_per100k_str, "IPD incidence"),
        (f"{d['antibiotic_rx_per1000']:.0f}/1k", "Antibiotic Rx"),
        (fmt_pct(d["mpr_2yo_pct"]), "MPR 2yo coverage"),
        (fmt_pct(d["hpv_girls_pct"]), "HPV girls coverage"),
        (f"{d['mi_incidence']:.0f}/100k", "MI incidence"),
        (f"{d['mi_prevalence']:.0f}/100k", "MI prevalence"),
    ]
    draw_kpi_card(ax, left_x, bot_y, card_w, card_h,
                   "Infectious & Cardiovascular Indicators", infect_kpis,
                   n_cols=3, value_fontsize=13, label_fontsize=8.5)

    # Pipeline Therapeutic Areas — narrative
    draw_narrative_card(ax, right_x, top_y, card_w, card_h,
                         "Pipeline Therapeutic Areas",
                         n.get("pipeline_areas", ()),
                         accent_color=COLORS["competitor_charcoal"],
                         body_fontsize=9.5, line_step=1.7, wrap_width=64)

    # Cardiovascular & Rare Disease — narrative
    draw_narrative_card(ax, right_x, bot_y, card_w, card_h,
                         "Cardiovascular & Rare Disease",
                         n.get("cv_rare_disease", ()),
                         accent_color=COLORS["competitor_charcoal"],
                         body_fontsize=9.5, line_step=1.7, wrap_width=64)

    draw_source(ax,
                 "Source: Socialstyrelsen Cancer Register, RCC, Folkhälsomyndigheten "
                 "Infectious Disease Surveillance, Kolada Heart Care Quality (2024-2025).")

    plt.savefig(out_path(d["region_short"], "R2_disease_burden"),
                facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_path(d['region_short'], 'R2_disease_burden')}")


if __name__ == "__main__":
    render_r2("Region Stockholm")
