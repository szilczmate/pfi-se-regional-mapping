# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R-A — Region Context (compressed R1 + R2 in 4-slide format).

Layout:
  Header        eyebrow + title + 1-line takeaway
  Fingerprint   5 horizontal percentile bars (Pop / Aging / Equity / Burden / Pfizer)
  KPI grid      2×2 cards with rank-annotated KPIs
                  Demographics │ Healthcare Economy
                  Equity       │ Disease Burden

Output: delivery/figures/region_profiles/<region>/RA_region_context.png
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from region_dashboards import make_canvas, draw_header, draw_source, out_path
from region_data import get_region, get_region_ranks, compute_fingerprint
from viti_theme import COLORS

sys.stdout.reconfigure(encoding="utf-8")


def render_ra(region_full_name):
    d = get_region(region_full_name)
    ranks = get_region_ranks(region_full_name)
    fp = compute_fingerprint(region_full_name)

    fig, ax = make_canvas()

    # ---------- Header ----------
    ax.add_patch(Rectangle((0, 56.0), 100, 0.25,
                              facecolor=COLORS["pfizer_blue"], linewidth=0))
    ax.text(5.0, 53.5, f"REGION PROFILE  ·  {d['region_short'].upper()}  ·  CONTEXT",
             fontsize=10, color=COLORS["viti_blue"],
             fontweight="semibold", va="top")
    ax.text(5.0, 52.0, d["region_short"],
             fontsize=22, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(5.0, 47.5, f"Healthcare region: {d['healthcare_region']}  ·  Region context at-a-glance",
             fontsize=10.5, color=COLORS["viti_gray"], va="top")

    # ---------- Fingerprint strip — 5 horizontal cells ----------
    fp_y = 36.0
    fp_h = 9.5
    ax.add_patch(FancyBboxPatch(
        (5.0, fp_y), 90.0, fp_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((5.0, fp_y), 0.5, fp_h,
                              facecolor=COLORS["pfizer_blue"], linewidth=0))
    ax.text(6.5, fp_y + fp_h - 0.7,
             "REGIONAL FINGERPRINT  ·  Where this region sits among Sweden's 21",
             fontsize=8.5, color=COLORS["viti_blue"],
             fontweight="bold", va="top")

    # Short labels (the full ones overflowed when stacked vertically)
    SHORT_LABELS = {
        "Population scale": "Population",
        "Aging pressure (+65 by 2040)": "Aging pressure",
        "Equity (low need)": "Equity (low need)",
        "Disease burden (per-capita)": "Disease burden",
        "Pfizer footprint (3-yr SEK)": "Pfizer footprint",
    }

    n_dims = len(fp)
    cell_strip_left = 6.5
    cell_strip_right = 94.0
    cell_strip_w = cell_strip_right - cell_strip_left
    cell_gap = 0.8
    cell_w = (cell_strip_w - cell_gap * (n_dims - 1)) / n_dims
    cell_top_y = fp_y + fp_h - 2.5
    cell_bot_y = fp_y + 0.6

    for i, (label, pct, value_str) in enumerate(fp):
        cx = cell_strip_left + i * (cell_w + cell_gap)
        cy_centre_top = cell_top_y

        # Cell label (top)
        short = SHORT_LABELS.get(label, label)
        ax.text(cx + cell_w / 2, cy_centre_top, short,
                 ha="center", va="top",
                 fontsize=8.5, color=COLORS["viti_gray"],
                 fontweight="semibold")

        # Big rank/value (middle)
        ax.text(cx + cell_w / 2, cy_centre_top - 1.7, value_str,
                 ha="center", va="top",
                 fontsize=12, color=COLORS["viti_dark"],
                 fontweight="bold")

        # Bar (bottom)
        bar_y = cell_bot_y + 0.4
        bar_h_local = 0.55
        ax.add_patch(Rectangle((cx, bar_y), cell_w, bar_h_local,
                                  facecolor=COLORS["viti_light"],
                                  linewidth=0))
        if pct is not None:
            ax.add_patch(Rectangle((cx, bar_y), cell_w * pct / 100, bar_h_local,
                                      facecolor=COLORS["pfizer_blue"],
                                      linewidth=0))

    # ---------- KPI cards (2×2) ----------
    card_w = 43.0
    card_h = 16.5
    left_x = 5.0
    right_x = 52.0
    top_y = 18.5
    bot_y = 1.5

    def fmt_int(v):
        if v is None or v != v: return "—"
        return f"{int(v):,}"
    def fmt_pct(v, dp=1):
        if v is None or v != v: return "—"
        return f"{v:.{dp}f}%"
    def fmt_sek(v):
        if v is None or v != v: return "—"
        return f"{int(v):,} SEK"

    def rank_str(metric_key):
        r = ranks.get(metric_key)
        if r is None: return ""
        return f"#{r}"

    def draw_card(x, y, title, kpis, accent=None):
        ax.add_patch(FancyBboxPatch(
            (x, y), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=1.0",
            linewidth=0.6, edgecolor=COLORS["viti_medium"],
            facecolor="#FFFFFF", zorder=1,
        ))
        ax.add_patch(Rectangle((x, y), 0.5, card_h,
                                  facecolor=accent or COLORS["pfizer_blue"],
                                  linewidth=0))
        ax.text(x + 1.5, y + card_h - 1.5, title,
                 fontsize=12, color=COLORS["viti_dark"],
                 fontweight="bold", va="top")

        # KPI grid: 2 cols × N rows
        pad_top = 4.0
        n = len(kpis)
        n_cols = 2
        n_rows = (n + n_cols - 1) // n_cols
        tile_w = (card_w - 3.0) / n_cols
        tile_h = (card_h - pad_top - 1.0) / max(n_rows, 1)

        for i, (val, lbl, rk) in enumerate(kpis):
            col = i % n_cols
            row = i // n_cols
            tx = x + 1.5 + col * tile_w
            ty = y + card_h - pad_top - row * tile_h
            ax.text(tx, ty, str(val),
                     fontsize=14, color=COLORS["viti_dark"],
                     fontweight="bold", va="top")
            ax.text(tx, ty - 1.7, lbl,
                     fontsize=8.5, color=COLORS["viti_gray"], va="top")
            if rk:
                ax.text(tx + tile_w - 1.0, ty + 0.3, rk,
                         fontsize=8.5, color=COLORS["pfizer_blue"],
                         fontweight="semibold", va="top", ha="right")

    # Card 1: Demographics & projections
    demo_kpis = [
        (f"{d['population']/1e6:.2f}M",
         "Population", rank_str("Population")),
        (fmt_pct(d['pop_65_share']),
         "65+ share", rank_str("pop_65_share")),
        (f"+{d['growth_65_to_2040']:.0f}%",
         "65+ growth to 2040", rank_str("65+ growth % 2024→2040")),
        (f"{d['life_expectancy_avg']:.1f} yr",
         "Life expectancy", rank_str("Life exp avg")),
        (fmt_pct(d['foreign_born_pct']),
         "Foreign-born", rank_str("Foreign-born % (2024)")),
        (f"{int(d['births_2024']):,}",
         "Births 2024", ""),
    ]
    draw_card(left_x, top_y, "Demographics", demo_kpis,
               accent=COLORS["pfizer_blue"])

    # Card 2: Healthcare Economy
    econ_kpis = [
        (f"{int(d['grp_per_capita_ksek']):,} kSEK",
         "GRP / capita", rank_str("GRP per capita (kSEK)")),
        (f"{int(d['hc_cost_per_capita']/1000):,}k SEK",
         "HC cost / capita", rank_str("Healthcare cost per capita (SEK)")),
        (f"{int(d['pharma_per_capita']):,} SEK",
         "Pharma / capita", rank_str("Pharma total cost per capita (SEK)")),
        (f"{int(d['vaccine_sellin_per_capita'])} SEK",
         "Vaccine sell-in / cap", rank_str("Vaccine sell-in per capita (SEK/year)")),
        (fmt_pct(d['pharma_pct_hc']),
         "Pharma % of HC", ""),
        (f"{int(d['specialists']):,}",
         "Specialists", rank_str("Specialist physicians (#)")),
    ]
    draw_card(right_x, top_y, "Healthcare Economy", econ_kpis,
               accent=COLORS["pfizer_blue"])

    # Card 3: Equity & Lifestyle
    eq_kpis = [
        (f"#{ranks.get('Equity rank', '—')}",
         "Equity rank (1 = most need)", "of 21"),
        (f"{d['premature_mortality_25_64']:.0f}",
         "Premature mort. 25–64 /100k",
         rank_str("Premature mortality 25–64 /100k (age-std)")),
        (f"{d['hc_amenable_mortality']:.1f}",
         "HC-amenable mort. /100k",
         rank_str("Healthcare-amenable mortality /100k (3-yr MA)")),
        (fmt_pct(d['post_secondary_pct']),
         "Post-secondary education",
         rank_str("Post-secondary education 25–64 % (2024)")),
        (fmt_pct(d['daily_smokers_pct']),
         "Daily smokers",
         rank_str("Daily smokers %")),
        (fmt_pct(d['overweight_obese_pct']),
         "Overweight/obese",
         rank_str("Overweight/obese %")),
    ]
    draw_card(left_x, bot_y, "Equity & Lifestyle", eq_kpis,
               accent=COLORS["competitor_charcoal"])

    # Card 4: Disease Burden
    burden_kpis = [
        (f"{d['breast_ca_rate']:.0f}",
         "Breast cancer /100k", rank_str("Breast ca rate /100k")),
        (f"{d['prostate_ca_rate']:.0f}",
         "Prostate cancer /100k", rank_str("Prostate ca rate /100k")),
        (f"{d['lung_ca_incidence']:.0f}",
         "Lung cancer /100k", rank_str("Lung ca incidence /100k")),
        (f"{d['mi_incidence']:.0f}",
         "MI incidence /100k", rank_str("MI incidence /100k")),
        (f"{d['heart_care_quality']:.0f}",
         "Heart care quality 0-100", rank_str("Heart care quality (0-100)")),
        (f"{int(d['tbe_cases_2025']) if d['tbe_cases_2025'] == d['tbe_cases_2025'] else '—'}",
         "TBE cases 2025", ""),
    ]
    draw_card(right_x, bot_y, "Disease Burden", burden_kpis,
               accent=COLORS["competitor_charcoal"])

    # ---------- Source ----------
    ax.text(5.0, 0.5,
             "Source: SCB Population Projections (2024–2050), Kolada Healthcare Indicators (2024), "
             "Folkhälsomyndigheten Lifestyle + Vaccination Coverage (2024), Socialstyrelsen Cancer Register + Patientregister (2024–2025), "
             "Workbook v30 \"Region master\" + \"Equity composite\" + \"Pfizer total footprint\". Ranks computed across 21 regions.",
             fontsize=7.5, color=COLORS["viti_gray"], va="bottom")

    out_p = out_path(d["region_short"], "compact_1_region_context")
    plt.savefig(out_p, facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {out_p}")


if __name__ == "__main__":
    render_ra("Region Stockholm")
    render_ra("Region Västerbotten")
