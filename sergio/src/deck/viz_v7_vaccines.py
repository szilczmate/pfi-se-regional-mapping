# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V7 — Pfizer adult vaccines: demographic tailwind (deck slide 8).

Three Pfizer adult vaccines benefit from Sweden's aging population:
  FSME-IMMUN (TBE) — mature, ~1.3B kr / 36 months, the cash anchor
  Abrysvo (RSV)    — launch trajectory under NT-rådet "avvakta"
  Prevenar 20      — launch trajectory, gradual ramp

Output: delivery/figures/deck/V7_vaccine_tailwind.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, style_axes,
                         add_title_block, add_source_line, add_accent_rule)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW = ROOT / "working" / "data" / "raw"
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

# ---------------------------------------------------------------------------
# Load + reshape
# ---------------------------------------------------------------------------
df = pd.read_excel(RAW / "VitiScience_Vaccines_Apr-02-2026.xlsx",
                    sheet_name="Sweden Sell-In")
df = df[df["Brick"].notna() & (df["Brick"] != "Grand Total")].copy()

months = pd.date_range("2023-04-01", "2026-03-01", freq="MS")
val_cols = {f"Sell In Value\n{m.strftime('%b %Y')}": m for m in months}

# Aggregate FSME-IMMUN VUXEN + JUNIOR into "FSME-IMMUN total"
df["product_grouped"] = df["Product Name Incl PI"].replace({
    "FSME-IMMUN VUXEN": "FSME-IMMUN", "FSME-IMMUN JUNIOR": "FSME-IMMUN"
})

products = ["FSME-IMMUN", "ABRYSVO", "PREVENAR 20"]
labels = {"FSME-IMMUN": "FSME-IMMUN  (TBE)",
          "ABRYSVO": "Abrysvo  (RSV)",
          "PREVENAR 20": "Prevenar 20  (pneumococcal)"}
descriptions = {
    "FSME-IMMUN": "Cash anchor",
    "ABRYSVO": "RSV launch · NT-rådet \"avvakta\"",
    "PREVENAR 20": "Pneumococcal launch · 65+ target",
}

monthly = []
for col, m in val_cols.items():
    if col in df.columns:
        for p in products:
            sek = df[df["product_grouped"] == p][col].sum()
            monthly.append({"month": m, "product": p, "sek": sek})
mdf = pd.DataFrame(monthly)
pivot = mdf.pivot(index="month", columns="product", values="sek").fillna(0)
print(pivot.tail())

# 3-month rolling for smoothing
roll = pivot.rolling(3, min_periods=1).mean()

# Totals across the 36 months
totals_36 = pivot.sum() / 1e6

# ---------------------------------------------------------------------------
# Figure: three panels in a row, big-number header per panel
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(13, 5.0),
                          gridspec_kw={"wspace": 0.32})
fig.subplots_adjust(left=0.06, right=0.96, top=0.56, bottom=0.13)

for ax, p in zip(axes, products):
    series_M = roll[p] / 1e6  # to M kr
    total_M = totals_36[p]

    # Trajectory area
    ax.fill_between(series_M.index, series_M.values, 0,
                     color=COLORS["pfizer_blue"], alpha=0.18)
    ax.plot(series_M.index, series_M.values,
             color=COLORS["pfizer_blue"], lw=2.5)

    # Big number above the chart
    if total_M >= 1000:
        big_str = f"{total_M/1000:.1f}B kr"
    else:
        big_str = f"{total_M:,.0f}M kr"
    ax.text(0.0, 1.46, big_str,
             transform=ax.transAxes, fontsize=24,
             color=COLORS["pfizer_blue"], fontweight="bold", va="bottom")
    ax.text(0.0, 1.38, "Sell-In SEK · 36 months",
             transform=ax.transAxes, fontsize=9,
             color=COLORS["viti_gray"], va="bottom")

    # Sub-header with product name + role
    ax.text(0.0, 1.22, labels[p],
             transform=ax.transAxes, fontsize=11.5,
             color=COLORS["viti_dark"], fontweight="semibold", va="bottom")
    ax.text(0.0, 1.13, descriptions[p],
             transform=ax.transAxes, fontsize=9,
             color=COLORS["viti_gray"], va="bottom")

    # Polish axes
    style_axes(ax, hide_x_grid=True)
    ax.set_ylim(bottom=0)
    ax.set_xlim(months[0] - pd.Timedelta(days=15),
                 months[-1] + pd.Timedelta(days=15))

    # Year ticks only
    year_ticks = pd.date_range("2024-01-01", "2026-01-01", freq="YS")
    ax.set_xticks(list(year_ticks))
    ax.set_xticklabels([d.strftime("%Y") for d in year_ticks], fontsize=9)
    ax.set_ylabel("M kr / month", fontsize=9, color=COLORS["viti_gray"])

# Title block
add_accent_rule(fig, x=0.06, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="P3 ADULT VACCINE PORTFOLIO · SWEDEN · APR 2023–MAR 2026",
    headline="Three Pfizer adult vaccines, three growth profiles.",
    takeaway="FSME-IMMUN is the established revenue base. Abrysvo and Prevenar 20 are launching into a 65+ population growing substantially through 2040.",
    x=0.06, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
)

add_source_line(fig,
                "Source: IQVIA Sweden Sell-In SEK monthly Apr 2023–Mar 2026, 3-month rolling average. "
                "FSME-IMMUN totals combine VUXEN + JUNIOR. Y-axes scaled independently.",
                x=0.06, y=0.04)

plt.savefig(OUT / "V7_vaccine_tailwind.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V7_vaccine_tailwind.png'}")
