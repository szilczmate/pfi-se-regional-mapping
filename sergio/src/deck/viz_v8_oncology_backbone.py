# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V8 — Precision oncology backbone (deck slide 9).

Three Pfizer precision-medicine oncology products dependent on molecular
testing infrastructure:
  Tukysa    (HER2+ breast cancer brain mets)
  Talzenna  (BRCA-mutated mCRPC)
  Lorviqua  (ALK+ NSCLC)

Output: delivery/figures/deck/V8_oncology_backbone.png
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

PRODUCTS = [
    {"name": "Tukysa", "sheet": "Tukysa L01EH", "match": "TUKYSA",
     "label": "Tukysa  (HER2+ brain mets)",
     "biomarker": "HER2 amplification · brain mets"},
    {"name": "Talzenna", "sheet": "Talzenna", "match": "TALZENNA",
     "label": "Talzenna  (BRCA mCRPC)",
     "biomarker": "BRCA1/2 mutation · prostate"},
    {"name": "Lorviqua", "sheet": "Lorviqua L01ED", "match": "LORVIQUA",
     "label": "Lorviqua  (ALK+ NSCLC)",
     "biomarker": "ALK rearrangement · lung"},
]

months = pd.date_range("2023-04-01", "2026-03-01", freq="MS")
val_cols = {f"Sell-In Value\n{m.strftime('%b %Y')}": m for m in months}

monthly = []
totals_36 = {}
for p in PRODUCTS:
    df = pd.read_excel(RAW / "VitiScience Oncology_Apr-27-2026.xlsx",
                        sheet_name=p["sheet"])
    df = df[df["Product Name incl PI"] == p["match"]].copy()
    df = df[df["Brick"].notna() & (df["Brick"] != "Grand Total")].copy()
    series_data = {}
    for col, m in val_cols.items():
        series_data[m] = df[col].sum() if col in df.columns else 0
    series = pd.Series(series_data).sort_index()
    totals_36[p["name"]] = series.sum() / 1e6
    for m, sek in series.items():
        monthly.append({"month": m, "product": p["name"], "sek": sek})

mdf = pd.DataFrame(monthly)
pivot = mdf.pivot(index="month", columns="product", values="sek").fillna(0)
roll = pivot.rolling(3, min_periods=1).mean()
print(pivot.tail())
print("\n36-month totals:")
print(pd.Series(totals_36))

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(13, 5.0),
                          gridspec_kw={"wspace": 0.32})
fig.subplots_adjust(left=0.06, right=0.96, top=0.56, bottom=0.13)

for ax, p in zip(axes, PRODUCTS):
    series_M = roll[p["name"]] / 1e6
    total_M = totals_36[p["name"]]

    ax.fill_between(series_M.index, series_M.values, 0,
                     color=COLORS["pfizer_blue"], alpha=0.18)
    ax.plot(series_M.index, series_M.values,
             color=COLORS["pfizer_blue"], lw=2.5)

    big_str = f"{total_M:,.0f}M kr"
    ax.text(0.0, 1.46, big_str,
             transform=ax.transAxes, fontsize=24,
             color=COLORS["pfizer_blue"], fontweight="bold", va="bottom")
    ax.text(0.0, 1.38, "Sell-In SEK · 36 months",
             transform=ax.transAxes, fontsize=9,
             color=COLORS["viti_gray"], va="bottom")

    ax.text(0.0, 1.22, p["label"],
             transform=ax.transAxes, fontsize=11.5,
             color=COLORS["viti_dark"], fontweight="semibold", va="bottom")
    ax.text(0.0, 1.13, p["biomarker"],
             transform=ax.transAxes, fontsize=9,
             color=COLORS["viti_gray"], va="bottom")

    style_axes(ax, hide_x_grid=True)
    ax.set_ylim(bottom=0)
    ax.set_xlim(months[0] - pd.Timedelta(days=15),
                 months[-1] + pd.Timedelta(days=15))
    year_ticks = pd.date_range("2024-01-01", "2026-01-01", freq="YS")
    ax.set_xticks(list(year_ticks))
    ax.set_xticklabels([d.strftime("%Y") for d in year_ticks], fontsize=9)
    ax.set_ylabel("M kr / month", fontsize=9, color=COLORS["viti_gray"])

add_accent_rule(fig, x=0.06, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="P4 PRECISION ONCOLOGY · SWEDEN · APR 2023–MAR 2026",
    headline="Three molecular-testing-dependent products. Three demand profiles.",
    takeaway="Eligible-patient identification depends on biomarker testing infrastructure — HER2 amplification, BRCA1/2 mutation, ALK rearrangement.",
    x=0.06, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
)

add_source_line(fig,
                "Source: IQVIA Oncology Sweden Sell-In SEK monthly Apr 2023–Mar 2026, 3-month rolling average. "
                "Y-axes scaled independently. Brick-level coverage from the IQVIA Oncology extract delivered 2026-04-27.",
                x=0.06, y=0.04)

plt.savefig(OUT / "V8_oncology_backbone.png", facecolor="#FFFFFF")
print(f"\nWrote {OUT / 'V8_oncology_backbone.png'}")
