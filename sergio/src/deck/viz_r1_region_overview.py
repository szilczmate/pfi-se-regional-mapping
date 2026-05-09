# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
R1 — Region Overview dashboard (regional profile slide 1 of 6).

Replicates the reference Stockholm slide-7 layout in Viti polished style:
  4 cards in a 2×2 grid, each with 6 KPI tiles.

Output: delivery/figures/region_profiles/<region>/R1_overview.png
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS, add_source_line, add_accent_rule
from region_data import get_region

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")

apply_viti_theme()


def fmt_int(v):
    if v is None or v != v:
        return "—"
    return f"{int(v):,}"


def fmt_pct(v, dp=1):
    if v is None or v != v:
        return "—"
    return f"{v:.{dp}f}%"


def fmt_sek(v):
    if v is None or v != v:
        return "—"
    return f"{int(v):,} SEK"


def fmt_signed_pct(v):
    if v is None or v != v:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.0f}%"


def draw_card(ax, x, y, w, h, title, kpis,
               accent_color=None, fill_color=None):
    """Draw one card with title + 6 KPI tiles in a 2x3 grid.
    kpis: list of (value_str, label_str)
    """
    accent = accent_color or COLORS["pfizer_blue"]
    fill = fill_color or "#FFFFFF"

    # Card background
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor=fill, zorder=1,
    ))

    # Left accent strip
    ax.add_patch(Rectangle((x, y), 0.5, h,
                              facecolor=accent, linewidth=0,
                              zorder=2))

    # Title
    ax.text(x + 1.5, y + h - 1.6, title,
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top", ha="left", zorder=3)

    # KPI tiles in 2 rows × 3 cols
    pad_left = 1.5
    pad_top = 4.5
    tile_w = (w - pad_left - 1.0) / 3
    tile_h = (h - pad_top - 1.0) / 2

    for idx, (val, lbl) in enumerate(kpis):
        col = idx % 3
        row = idx // 3
        tx = x + pad_left + col * tile_w
        ty = y + h - pad_top - row * tile_h

        # Big value
        ax.text(tx, ty, str(val),
                 fontsize=15, color=COLORS["viti_dark"],
                 fontweight="bold", va="top", ha="left", zorder=3)
        # Label below
        ax.text(tx, ty - 1.7, lbl,
                 fontsize=9, color=COLORS["viti_gray"],
                 va="top", ha="left", zorder=3)


def render_r1(region_full_name):
    d = get_region(region_full_name)

    fig = plt.figure(figsize=(13.33, 7.5))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56.25)  # 16:9 ratio (100 / 16 * 9 = 56.25)
    ax.axis("off")

    # Top accent bar (full width)
    ax.add_patch(Rectangle((0, 56.0), 100, 0.25,
                              facecolor=COLORS["pfizer_blue"],
                              linewidth=0, zorder=2))

    # Eyebrow + Title + Subtitle
    ax.text(5.5, 53.0, "REGION PROFILE  ·  PART B",
             fontsize=10, color=COLORS["viti_blue"],
             fontweight="semibold", va="top")
    ax.text(5.5, 51.5, d["region_short"],
             fontsize=26, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(5.5, 47.0, f"Healthcare region: {d['healthcare_region']}",
             fontsize=11, color=COLORS["viti_gray"],
             va="top")

    # Card layout
    card_w = 43.0
    card_h = 17.0
    left_x = 5.0
    right_x = 52.0
    top_y = 27.0
    bot_y = 8.5

    # Demographics (top-left)
    draw_card(ax, left_x, top_y, card_w, card_h,
               "Demographics",
               [
                   (fmt_int(d["population"]), "Population"),
                   (fmt_pct(d["pop_65_share"]), "65+ share"),
                   (f"{int(d['grp_per_capita_ksek']):,} kSEK", "GRP/capita"),
                   (fmt_signed_pct(d["growth_65_to_2040"]), "65+ by 2040"),
                   (f"{d['life_expectancy_avg']:.1f} yrs", "Life expectancy"),
                   (fmt_pct(d["foreign_born_pct"]), "Foreign-born"),
               ])

    # Healthcare Budget (bottom-left)
    draw_card(ax, left_x, bot_y, card_w, card_h,
               "Healthcare Budget",
               [
                   (fmt_sek(d["hc_cost_per_capita"]), "HC cost/capita"),
                   (fmt_sek(d["pharma_per_capita"]), "Pharma/capita"),
                   (fmt_sek(d["primary_care_per_capita"]), "Primary care/cap"),
                   (fmt_pct(d["pharma_pct_hc"]), "Pharma % of HC"),
                   (fmt_sek(d["vaccine_sellin_per_capita"]), "Vaccine sell-in/cap"),
                   (fmt_int(d["specialists"]), "Specialists"),
               ])

    # Population Projections (top-right) — slightly different accent (Brand Dark)
    draw_card(ax, right_x, top_y, card_w, card_h,
               "Population Projections",
               [
                   (fmt_int(d["pop_2040"]), "Pop 2040"),
                   (fmt_int(d["pop_65_2040"]), "65+ in 2040"),
                   (fmt_int(d["pop_2050"]), "Pop 2050"),
                   (fmt_int(d["births_2024"]), "Births 2024"),
                   (fmt_int(d["pop_women_15_44"]), "Women 15–44"),
                   (fmt_int(d["pop_0_1"]), "Infants 0–1"),
               ],
               accent_color=COLORS["competitor_charcoal"])

    # Health Equity Indicators (bottom-right)
    draw_card(ax, right_x, bot_y, card_w, card_h,
               "Health Equity Indicators",
               [
                   (f"{d['premature_mortality_25_64']:.1f}/100k", "Premature mort. 25–64"),
                   (f"{d['hc_amenable_mortality']:.1f}/100k", "HC-amenable mort."),
                   (f"{d['suicide_25plus']:.1f}/100k", "Suicide 25+"),
                   (fmt_pct(d["post_secondary_pct"]), "Post-secondary edu"),
                   (fmt_pct(d["daily_smokers_pct"]), "Daily smokers"),
                   (fmt_pct(d["overweight_obese_pct"]), "Overweight/obese"),
               ],
               accent_color=COLORS["competitor_charcoal"])

    # Source line bottom-left
    ax.text(5.0, 2.5,
             "Source: SCB Population Projections (2024–2050), Kolada Healthcare Indicators (2024), "
             "Folkhälsomyndigheten Lifestyle Risk Factors (2024).",
             fontsize=8.5, color=COLORS["viti_gray"], va="bottom")

    # Save
    region_slug = d["region_short"].replace(" ", "_").replace("ö", "o").replace("ä", "a").replace("å", "a")
    out_dir = ROOT / "delivery" / "figures" / "region_profiles" / region_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "R1_overview.png"
    plt.savefig(out_path, facecolor="#FFFFFF", dpi=200, bbox_inches=None)
    plt.close()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    render_r1("Region Stockholm")
