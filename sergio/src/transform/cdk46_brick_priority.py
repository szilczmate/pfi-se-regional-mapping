# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Brick-level priority analysis for P2 (CDK4/6 defense).

Translates the W1b regional finding ("Pfizer captures 7% of class-naive CDK4/6
starts nationally; per-region range 0-25%") down to the IQVIA brick level (~78
bricks) so Pfizer field can deploy at the level they actually deploy at.

Two outputs:
  - Recovery list: bricks where Pfizer share < national, weighted by market SEK
  - Defense list:  bricks where Pfizer share is high AND Kisqali is gaining

Window: Oct 2025 - Mar 2026 (last 6 months, matches existing slope methodology).
Metric: Sell-In SEK (no brick-level patient data; AVA is region-level only).

Outputs:
  working/data/interim/cdk46_brick_priority.csv (full 78-brick table)
  working/data/interim/cdk46_brick_recovery_top50.csv
  working/data/interim/cdk46_brick_defense_top20.csv
  delivery/figures/F21_cdk46_brick_priority_quadrant.png
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 220)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW = ROOT / "working" / "data" / "raw" / "VitiScience Oncology_Apr-27-2026.xlsx"
INTERIM = ROOT / "working" / "data" / "interim"
FIG = ROOT / "delivery" / "figures"

COLOR = {"Ibrance": "#0093D0", "Kisqali": "#E03C31", "Verzenios": "#7B2D8E"}

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.family": "DejaVu Sans",
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

# ---------------------------------------------------------------------------
# Load and reshape: brick x product x month (long format)
# ---------------------------------------------------------------------------
df = pd.read_excel(RAW, sheet_name="Ibrance")
df = df[df["Product Name incl PI"].isin(["IBRANCE", "KISQALI", "VERZENIOS"])].copy()
df = df[df["Brick"].notna() & (df["Brick"] != "Grand Total")].copy()

PRODUCT_MAP = {"IBRANCE": "Ibrance", "KISQALI": "Kisqali", "VERZENIOS": "Verzenios"}
df["Product"] = df["Product Name incl PI"].map(PRODUCT_MAP)

LAST6_MONTHS = ["Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026"]
PREV6_MONTHS = ["Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025"]

last6_cols = [f"Sell-In Value\n{m}" for m in LAST6_MONTHS]
prev6_cols = [f"Sell-In Value\n{m}" for m in PREV6_MONTHS]

df["last6_sek"] = df[last6_cols].sum(axis=1)
df["prev6_sek"] = df[prev6_cols].sum(axis=1)

# Aggregate to brick x product
agg = df.groupby(["Brick", "County Council", "Product"], as_index=False).agg(
    last6_sek=("last6_sek", "sum"),
    prev6_sek=("prev6_sek", "sum"),
)

# Pivot to brick-level table
last6 = agg.pivot_table(index=["Brick", "County Council"], columns="Product",
                        values="last6_sek", aggfunc="sum", fill_value=0).reset_index()
prev6 = agg.pivot_table(index=["Brick", "County Council"], columns="Product",
                        values="prev6_sek", aggfunc="sum", fill_value=0).reset_index()

# Make sure all three product columns exist
for p in ["Ibrance", "Kisqali", "Verzenios"]:
    if p not in last6.columns:
        last6[p] = 0
    if p not in prev6.columns:
        prev6[p] = 0

last6["last6_total"] = last6[["Ibrance", "Kisqali", "Verzenios"]].sum(axis=1)
prev6["prev6_total"] = prev6[["Ibrance", "Kisqali", "Verzenios"]].sum(axis=1)
last6["Ibrance_share"] = np.where(last6["last6_total"] > 0,
                                   last6["Ibrance"] / last6["last6_total"] * 100, np.nan)
last6["Kisqali_share"] = np.where(last6["last6_total"] > 0,
                                   last6["Kisqali"] / last6["last6_total"] * 100, np.nan)
last6["Verzenios_share"] = np.where(last6["last6_total"] > 0,
                                     last6["Verzenios"] / last6["last6_total"] * 100, np.nan)

# Kisqali growth rate (last 6 vs prev 6, per brick)
merged = last6.merge(prev6[["Brick", "Kisqali"]].rename(
    columns={"Kisqali": "Kisqali_prev6"}), on="Brick", how="left")
merged["Kisqali_growth_pct"] = np.where(
    merged["Kisqali_prev6"] > 0,
    (merged["Kisqali"] - merged["Kisqali_prev6"]) / merged["Kisqali_prev6"] * 100,
    np.nan,
)

# ---------------------------------------------------------------------------
# National benchmarks
# ---------------------------------------------------------------------------
national_total = merged["last6_total"].sum()
national_ibrance = merged["Ibrance"].sum()
national_share = national_ibrance / national_total * 100
print(f"National CDK4/6 last-6mo SEK: {national_total/1e6:.1f}M kr")
print(f"National Ibrance share: {national_share:.1f}%")
print(f"National Kisqali share: {merged['Kisqali'].sum()/national_total*100:.1f}%")
print(f"National Verzenios share: {merged['Verzenios'].sum()/national_total*100:.1f}%")
print(f"Bricks with non-zero CDK4/6 sales: {(merged['last6_total']>0).sum()} of {len(merged)}")

# ---------------------------------------------------------------------------
# Score bricks
# ---------------------------------------------------------------------------
# Recovery: under-share bricks weighted by market size
# Recovery SEK = (national_share - brick_share) * brick_total / 100
# Positive = brick is under-penetrated relative to national average
# Multiplied by brick total -> bigger markets weight more
merged["recovery_sek_kr"] = np.where(
    merged["last6_total"] > 0,
    (national_share - merged["Ibrance_share"]) * merged["last6_total"] / 100,
    0,
)

# Defense: brick share above national AND Kisqali growing fast
# Defense risk = Kisqali_growth_pct * Ibrance_sek_at_risk
# Approximation: if Kisqali keeps growing at this rate, what's the threat to current Ibrance SEK?
merged["defense_risk_kr"] = np.where(
    (merged["Ibrance_share"] > national_share) & (merged["Kisqali_growth_pct"] > 0),
    merged["Kisqali_growth_pct"] / 100 * merged["Ibrance"],
    0,
)

# Quadrant assignment
def assign_quadrant(row):
    total_top = merged["last6_total"].quantile(0.5)
    if row["last6_total"] < total_top:
        return "Low priority (small market)"
    if row["Ibrance_share"] < national_share - 5:
        return "Recovery target"
    if row["Ibrance_share"] > national_share + 5 and row["Kisqali_growth_pct"] > 10:
        return "Defense target"
    if row["Ibrance_share"] > national_share + 5:
        return "Stronghold"
    return "Stable mid-tier"

merged["quadrant"] = merged.apply(assign_quadrant, axis=1)

# ---------------------------------------------------------------------------
# Output tables
# ---------------------------------------------------------------------------
INTERIM.mkdir(parents=True, exist_ok=True)

# Full brick table
out_cols = ["Brick", "County Council", "last6_total",
            "Ibrance", "Kisqali", "Verzenios",
            "Ibrance_share", "Kisqali_share", "Verzenios_share",
            "Kisqali_growth_pct", "recovery_sek_kr", "defense_risk_kr", "quadrant"]
full = merged[out_cols].copy()
full = full.rename(columns={
    "last6_total": "CDK4/6 total SEK (last 6mo)",
    "Ibrance": "Ibrance SEK",
    "Kisqali": "Kisqali SEK",
    "Verzenios": "Verzenios SEK",
    "Ibrance_share": "Ibrance share %",
    "Kisqali_share": "Kisqali share %",
    "Verzenios_share": "Verzenios share %",
    "Kisqali_growth_pct": "Kisqali last6 vs prev6 %",
    "recovery_sek_kr": "Recovery SEK (kr)",
    "defense_risk_kr": "Defense-risk SEK (kr)",
    "quadrant": "Priority quadrant",
})
full = full.sort_values("CDK4/6 total SEK (last 6mo)", ascending=False)
full.to_csv(INTERIM / "cdk46_brick_priority.csv", index=False, encoding="utf-8-sig")
print(f"\nWrote {INTERIM/'cdk46_brick_priority.csv'} ({len(full)} bricks)")

# Recovery top 50
recovery = full[full["Recovery SEK (kr)"] > 0].sort_values(
    "Recovery SEK (kr)", ascending=False).head(50).copy()
recovery.to_csv(INTERIM / "cdk46_brick_recovery_top50.csv", index=False, encoding="utf-8-sig")
print(f"Wrote {INTERIM/'cdk46_brick_recovery_top50.csv'} ({len(recovery)} bricks)")
print(f"  Total recovery SEK in top 50: {recovery['Recovery SEK (kr)'].sum()/1e6:.1f}M kr")
print(f"  Total recovery SEK Sweden:   {full[full['Recovery SEK (kr)']>0]['Recovery SEK (kr)'].sum()/1e6:.1f}M kr")
print(f"  Top 50 captures: {recovery['Recovery SEK (kr)'].sum()/full[full['Recovery SEK (kr)']>0]['Recovery SEK (kr)'].sum()*100:.0f}%")

# Defense top 20
defense = full[full["Defense-risk SEK (kr)"] > 0].sort_values(
    "Defense-risk SEK (kr)", ascending=False).head(20).copy()
defense.to_csv(INTERIM / "cdk46_brick_defense_top20.csv", index=False, encoding="utf-8-sig")
print(f"Wrote {INTERIM/'cdk46_brick_defense_top20.csv'} ({len(defense)} bricks)")

# ---------------------------------------------------------------------------
# F21 — quadrant figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7.5))

active = merged[merged["last6_total"] > 0].copy()

# Bubble size: market size
sizes = active["last6_total"] / active["last6_total"].max() * 800 + 30

# Color by quadrant
QCOLOR = {
    "Recovery target": "#E03C31",
    "Defense target": "#FF8C00",
    "Stronghold": "#0093D0",
    "Stable mid-tier": "#888888",
    "Low priority (small market)": "#CCCCCC",
}
colors = active["quadrant"].map(QCOLOR)

ax.scatter(active["last6_total"]/1e6, active["Ibrance_share"],
           s=sizes, c=colors, alpha=0.65, edgecolors="white", linewidth=0.6)

# National share line
ax.axhline(national_share, ls="--", lw=1, color="black", alpha=0.4)
ax.text(active["last6_total"].max()/1e6 * 0.98, national_share + 0.7,
        f"National Ibrance share = {national_share:.1f}%",
        ha="right", fontsize=8, color="black", alpha=0.7)

# Annotate top-10 bricks by market size
top10 = active.nlargest(10, "last6_total")
for _, r in top10.iterrows():
    label = r["Brick"].split(" - ", 1)[1] if " - " in r["Brick"] else r["Brick"]
    ax.annotate(label,
                xy=(r["last6_total"]/1e6, r["Ibrance_share"]),
                xytext=(5, 4), textcoords="offset points",
                fontsize=7.5, alpha=0.85)

ax.set_xlabel("Brick CDK4/6 market size, last 6 mo (M kr)")
ax.set_ylabel("Ibrance share of brick CDK4/6 SEK (%)")
ax.set_title("F21 — Brick-level CDK4/6 priority quadrant\n"
             f"{len(active)} bricks with sales · Oct 2025 - Mar 2026 · IQVIA Sell-In SEK",
             loc="left", fontsize=11, fontweight="bold")

# Legend
from matplotlib.lines import Line2D
legend = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                 markersize=10, label=q)
          for q, c in QCOLOR.items()]
ax.legend(handles=legend, loc="upper right", fontsize=8.5, frameon=False)

ax.set_xlim(left=-active["last6_total"].max()/1e6 * 0.02)
ax.set_ylim(0, 100)

plt.tight_layout()
out = FIG / "F21_cdk46_brick_priority_quadrant.png"
plt.savefig(out, bbox_inches="tight")
print(f"\nWrote {out}")

# ---------------------------------------------------------------------------
# Summary stats for findings memo
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("SUMMARY FOR FINDINGS MEMO")
print("="*70)
print(f"Total bricks: {len(full)} (with sales: {(full['CDK4/6 total SEK (last 6mo)']>0).sum()})")
print(f"\nQuadrant counts:")
print(full["Priority quadrant"].value_counts().to_string())
print(f"\nTop-5 recovery bricks by SEK opportunity:")
print(recovery.head(5)[["Brick", "County Council", "Ibrance share %",
                        "Recovery SEK (kr)"]].to_string(index=False))
print(f"\nTop-5 defense risk bricks:")
print(defense.head(5)[["Brick", "County Council", "Ibrance share %",
                       "Kisqali last6 vs prev6 %",
                       "Defense-risk SEK (kr)"]].to_string(index=False))
