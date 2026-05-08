# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
NT-rådet timing-impact analysis (descriptive event study).

Frames decision dates as overlays on monthly IQVIA Sell-In trajectories.
NOT a causal claim — pre/post slopes describe what happened around the decision
date but cannot rule out concurrent factors (launch dynamics, brand campaigns,
competitor moves, prescriber-level adoption curves).

Five products with NT-rådet decisions inside the IQVIA window (Apr 2023–Mar 2026):
  Abrysvo   — 2023-10-05 AWAIT (avvakta)
  Talzenna  — 2024-06-01 NATIONAL_AGREEMENT (no recommendation)
  Elrexfio  — 2024-06-14 NT_RECOMMENDATION (multipelt myelom)
  Tukysa    — 2025-05-01 NATIONAL_AGREEMENT (no recommendation)
  Vyndaqel  — 2025-09-02 ARCHIVED (NAG LOK transition)

Pre window = 6 months before decision; post = 6 months after.
Slope metric = % change in 6-mo total SEK vs the prior 6-mo total SEK.

Outputs:
  working/data/interim/nt_radet_timing_table.csv
  delivery/figures/F22_nt_radet_timing_overlay.png
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW = ROOT / "working" / "data" / "raw"
INTERIM = ROOT / "working" / "data" / "interim"
FIG = ROOT / "delivery" / "figures"

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.family": "DejaVu Sans",
    "font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

# Pfizer brand color
PFIZER_BLUE = "#0093D0"

# ---------------------------------------------------------------------------
# Product specifications
# ---------------------------------------------------------------------------
PRODUCTS = [
    {"name": "Abrysvo",  "decision": "2023-10-05",
     "status": "AWAIT (avvakta)",
     "file": "VitiScience_Vaccines_Apr-02-2026.xlsx",
     "sheet": "Sweden Sell-In",
     "product_col": "Product Name Incl PI",
     "value_prefix": "Sell In Value",
     "product_match": ["ABRYSVO"]},
    {"name": "Talzenna", "decision": "2024-06-01",
     "status": "NATIONAL_AGREEMENT",
     "file": "VitiScience Oncology_Apr-27-2026.xlsx",
     "sheet": "Talzenna",
     "product_col": "Product Name incl PI",
     "value_prefix": "Sell-In Value",
     "product_match": ["TALZENNA"]},
    {"name": "Elrexfio", "decision": "2024-06-14",
     "status": "NT_RECOMMENDATION",
     "file": "VitiScience Oncology_Apr-27-2026.xlsx",
     "sheet": "Elrexfio",
     "product_col": "Product Name incl PI",
     "value_prefix": "Sell-In Value",
     "product_match": ["ELREXFIO"]},
    {"name": "Tukysa",   "decision": "2025-05-01",
     "status": "NATIONAL_AGREEMENT",
     "file": "VitiScience Oncology_Apr-27-2026.xlsx",
     "sheet": "Tukysa L01EH",
     "product_col": "Product Name incl PI",
     "value_prefix": "Sell-In Value",
     "product_match": ["TUKYSA"]},
    {"name": "Vyndaqel", "decision": "2025-09-02",
     "status": "ARCHIVED (NAG LOK)",
     "file": "VitiScience RD_IM_Apr-27-2026.xlsx",
     "sheet": "ATTR",
     "product_col": "Product Name incl PI",
     "value_prefix": "Sell-In Value",
     "product_match": ["VYNDAQEL"]},
]

MONTHS_ALL = pd.date_range("2023-04-01", "2026-03-01", freq="MS")
MONTH_FORMAT = "%b %Y"


def get_monthly_series(spec):
    """Read the IQVIA file and return monthly Sweden Sell-In SEK series."""
    fpath = RAW / spec["file"]
    df = pd.read_excel(fpath, sheet_name=spec["sheet"])
    df = df[df[spec["product_col"]].isin(spec["product_match"])].copy()

    # Filter out Grand Total brick rows for oncology/RDIM files
    if "Brick" in df.columns:
        df = df[df["Brick"].notna() & (df["Brick"] != "Grand Total")]

    series = {}
    for d in MONTHS_ALL:
        col = f"{spec['value_prefix']}\n{d.strftime(MONTH_FORMAT)}"
        if col in df.columns:
            series[d] = df[col].sum()
        else:
            series[d] = np.nan
    s = pd.Series(series).sort_index()
    return s


def slope_pct(series, window_end_excl, n=6):
    """6-mo SEK total in window [end-2n+1 .. end] split into pre and post."""
    end = pd.Timestamp(window_end_excl)
    months = pd.date_range(end - pd.DateOffset(months=2*n-1), end, freq="MS")
    if len(months) < 2*n:
        return None
    pre = series.loc[months[:n]].sum()
    post = series.loc[months[n:]].sum()
    if pre <= 0:
        return None
    return (post - pre) / pre * 100


def event_study(spec):
    """Compute pre-6 SEK and post-6 SEK total around decision date.
    Returns dict with pre_total, post_total, pct_change, n_months_pre/post available."""
    series = get_monthly_series(spec)
    decision = pd.Timestamp(spec["decision"])
    decision_month = pd.Timestamp(decision.year, decision.month, 1)

    # Pre 6mo: months [decision_month-6, decision_month-1] inclusive
    pre_months = pd.date_range(decision_month - pd.DateOffset(months=6),
                                decision_month - pd.DateOffset(months=1), freq="MS")
    # Post 6mo: months [decision_month+1, decision_month+6] inclusive (skip decision month)
    post_months = pd.date_range(decision_month + pd.DateOffset(months=1),
                                 decision_month + pd.DateOffset(months=6), freq="MS")

    pre_avail = [m for m in pre_months if m in series.index and not pd.isna(series[m])]
    post_avail = [m for m in post_months if m in series.index and not pd.isna(series[m])]

    pre_sek = series.loc[pre_avail].sum() if pre_avail else 0
    post_sek = series.loc[post_avail].sum() if post_avail else 0
    pct_change = (post_sek - pre_sek) / pre_sek * 100 if pre_sek > 0 else np.nan

    return {
        "name": spec["name"],
        "decision": spec["decision"],
        "status": spec["status"],
        "pre_n_months": len(pre_avail),
        "post_n_months": len(post_avail),
        "pre_sek": pre_sek,
        "post_sek": post_sek,
        "pct_change": pct_change,
        "series": series,
    }


# ---------------------------------------------------------------------------
# Run event study
# ---------------------------------------------------------------------------
results = [event_study(p) for p in PRODUCTS]

# Output table
rows = []
for r in results:
    rows.append({
        "Product": r["name"],
        "NT-rådet decision": r["decision"],
        "NT-rådet status": r["status"],
        "Pre-6mo months observed": r["pre_n_months"],
        "Post-6mo months observed": r["post_n_months"],
        "Pre-6mo SEK total (M kr)": r["pre_sek"] / 1e6,
        "Post-6mo SEK total (M kr)": r["post_sek"] / 1e6,
        "Pre→Post % change": r["pct_change"],
    })
table = pd.DataFrame(rows)
INTERIM.mkdir(parents=True, exist_ok=True)
table.to_csv(INTERIM / "nt_radet_timing_table.csv", index=False, encoding="utf-8-sig")
print("Wrote", INTERIM / "nt_radet_timing_table.csv")
print()
print(table.to_string(index=False))

# ---------------------------------------------------------------------------
# F22 — 5-panel overlay figure
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.2))
axes = axes.flatten()

for i, r in enumerate(results):
    ax = axes[i]
    s = r["series"]
    decision = pd.Timestamp(r["decision"])

    # Plot monthly trajectory in M kr
    ax.plot(s.index, s.values / 1e6, color=PFIZER_BLUE, lw=1.6, marker="o", ms=2.5)
    ax.axvline(decision, color="black", ls="--", lw=1.2, alpha=0.7)

    # Shaded pre/post windows
    pre_start = pd.Timestamp(decision.year, decision.month, 1) - pd.DateOffset(months=6)
    pre_end = pd.Timestamp(decision.year, decision.month, 1)
    post_start = pre_end + pd.DateOffset(months=1)
    post_end = post_start + pd.DateOffset(months=6)
    ax.axvspan(pre_start, pre_end, alpha=0.10, color="gray")
    ax.axvspan(post_start, post_end, alpha=0.10, color=PFIZER_BLUE)

    # Annotate decision
    ymax = max(s.dropna().values) / 1e6 if len(s.dropna()) else 1
    ax.text(decision, ymax * 1.05, r["status"],
            ha="center", va="bottom", fontsize=7.5, color="black",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="gray", lw=0.5))

    # Pre/post slope label
    if not np.isnan(r["pct_change"]):
        sign = "+" if r["pct_change"] >= 0 else ""
        ax.text(0.02, 0.94, f"Pre6mo → Post6mo SEK: {sign}{r['pct_change']:.1f}%",
                transform=ax.transAxes, fontsize=8.5, fontweight="bold",
                va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray",
                          lw=0.5, alpha=0.9))

    ax.set_title(f"{r['name']} — NT-rådet {r['decision']}",
                 fontsize=10, loc="left", fontweight="bold")
    ax.set_ylabel("Sweden Sell-In SEK (M kr/mo)", fontsize=8.5)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.xaxis.set_major_formatter(DateFormatter("%b\n%Y"))

# Hide 6th panel; use it for explanatory legend
axes[5].axis("off")
axes[5].text(0.05, 0.92, "F22 — NT-rådet decision timing", fontsize=11, fontweight="bold",
             transform=axes[5].transAxes, va="top")
axes[5].text(0.05, 0.80,
             "Descriptive event study: monthly IQVIA Sweden Sell-In SEK\n"
             "with the NT-rådet decision date as a vertical reference.\n\n"
             "Pre/post 6-month SEK totals shown as % change. This is\n"
             "DESCRIPTIVE — concurrent factors (launch dynamics, competitor\n"
             "moves, brand campaigns) cannot be ruled out as alternative\n"
             "explanations for any inflection.\n\n"
             "Status legend:\n"
             "  AWAIT          — 'avvakta', regions decide independently\n"
             "  NT_RECOMMENDATION — formal national guidance to use\n"
             "  NATIONAL_AGREEMENT — price agreement, no clinical rec\n"
             "  ARCHIVED       — review handed to NAG LOK pathway\n\n"
             "Source: IQVIA Sell-In SEK monthly Apr 2023–Mar 2026 +\n"
             "samverkanlakemedel.se NT-rådet product pages (verified 2026-04-26).",
             fontsize=8, transform=axes[5].transAxes, va="top",
             linespacing=1.5)

plt.tight_layout()
out = FIG / "F22_nt_radet_timing_overlay.png"
plt.savefig(out, bbox_inches="tight")
print(f"\nWrote {out}")

# ---------------------------------------------------------------------------
# Summary readout
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("READOUT FOR FINDINGS MEMO")
print("="*70)
for r in results:
    sign = "+" if r["pct_change"] >= 0 else ""
    print(f"{r['name']:10s} ({r['status']:25s}, dec {r['decision']}): "
          f"pre {r['pre_sek']/1e6:5.1f}M kr → post {r['post_sek']/1e6:5.1f}M kr "
          f"= {sign}{r['pct_change']:.1f}%")
