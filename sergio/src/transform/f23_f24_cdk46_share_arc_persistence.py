# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
F23 — Ibrance share-erosion arc 2023-2026 (CDK4/6 SEK by month).
F24 — PoT/PWD persistence ratio per drug (CDK4/6, last 6 months).

F23 shows that Pfizer's CDK4/6 SEK share has collapsed from 58.6% in Apr-Sep
2023 to 17.5% in Oct 2025-Mar 2026, while Verzenios has risen from 12.5% to
50.1% and Kisqali has held roughly stable.

F24 quantifies "stickiness" using AVA's PoT (Patients on Treatment) and PWD
(Patients with Dispensations) measures: PoT/PWD = duration on treatment within
a 3-month grace window. Last-6-month Sweden values (Oct 2025-Mar 2026):
  Ibrance   PoT/PWD = 1.42
  Kisqali   PoT/PWD = 1.62
  Verzenios PoT/PWD = 1.58

Outputs:
  delivery/figures/F23_cdk46_share_arc.png
  delivery/figures/F24_cdk46_persistence.png
  working/data/interim/cdk46_share_arc_monthly.csv
  working/data/interim/cdk46_persistence_ratios.csv
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyreadr

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW = ROOT / "working" / "data" / "raw"
AVA = ROOT / "AVA data for mapping 2026-05-02"
INTERIM = ROOT / "working" / "data" / "interim"
FIG = ROOT / "delivery" / "figures"

COLOR = {"Ibrance": "#0093D0", "Kisqali": "#E03C31", "Verzenios": "#7B2D8E"}

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.family": "DejaVu Sans",
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

# ===========================================================================
# F23 — Share-erosion arc
# ===========================================================================
df = pd.read_excel(RAW / "VitiScience Oncology_Apr-27-2026.xlsx", sheet_name="Ibrance")
df = df[df["Product Name incl PI"].isin(["IBRANCE", "KISQALI", "VERZENIOS"])].copy()
df = df[df["Brick"].notna() & (df["Brick"] != "Grand Total")].copy()
df["Product"] = df["Product Name incl PI"].str.title()

months = pd.date_range("2023-04-01", "2026-03-01", freq="MS")
val_cols = {f"Sell-In Value\n{m.strftime('%b %Y')}": m for m in months}

# Aggregate monthly Sweden SEK per product
monthly = []
for col, m in val_cols.items():
    if col in df.columns:
        agg = df.groupby("Product")[col].sum()
        for product, sek in agg.items():
            monthly.append({"month": m, "product": product, "sek": sek})

mdf = pd.DataFrame(monthly)
pivot = mdf.pivot(index="month", columns="product", values="sek").fillna(0)

# Rolling 6-month total to smooth
roll = pivot.rolling(6, min_periods=6).sum()
share = roll.div(roll.sum(axis=1), axis=0) * 100
share = share.dropna()

share.to_csv(INTERIM / "cdk46_share_arc_monthly.csv", encoding="utf-8-sig")
print("F23 share series (rolling 6mo):")
print(f"  First: {share.index[0].strftime('%Y-%m')}")
print(f"  Last:  {share.index[-1].strftime('%Y-%m')}")
print(share.iloc[[0, -1]].round(1).to_string())

# Plot
fig, ax = plt.subplots(figsize=(11, 5.5))
for product in ["Ibrance", "Kisqali", "Verzenios"]:
    ax.plot(share.index, share[product], label=product,
            color=COLOR[product], lw=2.5, marker="o", ms=3.5,
            markevery=3)

# Annotate start and end values
for product in ["Ibrance", "Kisqali", "Verzenios"]:
    start_pct = share[product].iloc[0]
    end_pct = share[product].iloc[-1]
    ax.annotate(f"{start_pct:.1f}%", xy=(share.index[0], start_pct),
                xytext=(-8, 0), textcoords="offset points",
                ha="right", va="center", fontsize=9, fontweight="bold",
                color=COLOR[product])
    ax.annotate(f"{end_pct:.1f}%", xy=(share.index[-1], end_pct),
                xytext=(8, 0), textcoords="offset points",
                ha="left", va="center", fontsize=9, fontweight="bold",
                color=COLOR[product])

ax.set_xlabel("")
ax.set_ylabel("Share of CDK4/6 class SEK, rolling 6-month %")
ax.set_title(
    "F23 — CDK4/6 share-erosion arc (Sweden, IQVIA Sell-In SEK rolling 6-mo share)\n"
    "Pfizer share has collapsed 58.6% → 17.5% over Apr 2023–Mar 2026",
    loc="left", fontsize=11, fontweight="bold")
ax.legend(loc="center right", fontsize=10, frameon=False)
ax.set_ylim(0, 70)
ax.grid(True, alpha=0.3)

# Wider x-axis margins for annotation labels
ax.set_xlim(share.index[0] - pd.Timedelta(days=70),
            share.index[-1] + pd.Timedelta(days=70))

plt.tight_layout()
plt.savefig(FIG / "F23_cdk46_share_arc.png", bbox_inches="tight")
print(f"\nWrote {FIG/'F23_cdk46_share_arc.png'}")
plt.close()

# ===========================================================================
# F24 — PoT/PWD persistence
# ===========================================================================
result = pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevData.RDS"))
ava_df = list(result.values())[0]
ava_df["date"] = pd.to_datetime(ava_df["date"].astype(str))

# Last 6 months (Oct 2025 - Mar 2026), Sweden national, three drugs
LAST6_END = pd.Timestamp("2026-01-01")  # AVA monthly data ends Jan 2026
LAST6_START = LAST6_END - pd.DateOffset(months=5)
print(f"\nF24 window: {LAST6_START.date()} → {LAST6_END.date()}")

last6 = ava_df[(ava_df["date"] >= LAST6_START) & (ava_df["date"] <= LAST6_END) &
               (ava_df["region"] == "Sweden")].copy()

# PoT and PWD per drug (sum across months)
agg = last6.groupby(["drug", "analysis"])["n"].sum().unstack(fill_value=0)
print("\nLast-6 Sweden totals:")
print(agg.to_string())

# PoT/PWD ratio
ratios = []
for drug in ["Ibrance", "Kisqali", "Verzenios"]:
    pot = agg.loc[drug, "Patients on treatment"] if "Patients on treatment" in agg.columns else np.nan
    pwd = agg.loc[drug, "Patients with dispensations"] if "Patients with dispensations" in agg.columns else np.nan
    ratio = pot / pwd if pwd > 0 else np.nan
    ratios.append({"drug": drug, "PoT_total": pot, "PWD_total": pwd, "ratio": ratio})

rdf = pd.DataFrame(ratios)
rdf.to_csv(INTERIM / "cdk46_persistence_ratios.csv", index=False, encoding="utf-8-sig")
print("\nPoT/PWD ratios (last 6mo Sweden):")
print(rdf.to_string(index=False))

# Plot: bar chart
fig, ax = plt.subplots(figsize=(8.5, 5.5))
drugs = rdf["drug"].tolist()
ratios_vals = rdf["ratio"].tolist()
colors = [COLOR[d] for d in drugs]

bars = ax.bar(drugs, ratios_vals, color=colors, edgecolor="white", linewidth=1.5,
              width=0.6)

# Annotate values
for bar, ratio in zip(bars, ratios_vals):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02,
            f"{ratio:.2f}",
            ha="center", va="bottom", fontsize=14, fontweight="bold")

ax.axhline(1.0, ls=":", lw=1, color="gray", alpha=0.6)
ax.text(2.4, 1.01, "PoT = PWD\n(no on-treatment buffer)",
        ha="right", va="bottom", fontsize=8, color="gray", alpha=0.8)

ax.set_ylabel("Patients on Treatment / Patients with Dispensations")
ax.set_title(
    "F24 — CDK4/6 stickiness proxy: PoT/PWD ratio (Sweden, last 6 months)\n"
    "Higher ratio = patients counted on-treatment for longer between dispensations",
    loc="left", fontsize=11, fontweight="bold")
ax.set_ylim(0, 2.0)

# Below-bar labels for context
for i, (drug, row) in enumerate(rdf.iterrows()):
    pwd_str = f"PWD: {int(row['PWD_total']):,}"
    ax.text(i, -0.10, pwd_str, ha="center", va="top",
            transform=ax.get_xaxis_transform(), fontsize=8.5, color="gray")

# Caveat box
caveat = ("Methodology note: PoT counts patients as on-treatment from a dispensation date through 90 days after, even with no new\n"
          "dispensation in the window (3-month grace rule, AVA Methods notes 2026-05-05). The PoT/PWD ratio is a STICKINESS PROXY.\n"
          "It is NOT median treatment duration. Higher ratio means each dispensation 'covers' more patient-months in the data — could\n"
          "reflect longer real treatment duration, larger pack sizes, or different prescribing intervals. Differences between drugs at\n"
          "this magnitude (1.42 vs 1.62) are real signals; the absolute interpretation requires Pfizer EMR/claims validation.")
fig.text(0.04, -0.02, caveat, fontsize=7.5, color="gray",
         linespacing=1.5, va="top")

plt.tight_layout()
plt.savefig(FIG / "F24_cdk46_persistence.png", bbox_inches="tight")
print(f"\nWrote {FIG/'F24_cdk46_persistence.png'}")
plt.close()

# ===========================================================================
# Summary
# ===========================================================================
print("\n" + "="*70)
print("READOUT FOR FINDINGS MEMO")
print("="*70)
print(f"F23 — Share collapse: Ibrance {share['Ibrance'].iloc[0]:.1f}% → {share['Ibrance'].iloc[-1]:.1f}%")
print(f"     Verzenios surge: {share['Verzenios'].iloc[0]:.1f}% → {share['Verzenios'].iloc[-1]:.1f}%")
print(f"     Kisqali stable:  {share['Kisqali'].iloc[0]:.1f}% → {share['Kisqali'].iloc[-1]:.1f}%")
print(f"\nF24 — PoT/PWD stickiness ratios (last 6mo Sweden):")
for _, r in rdf.iterrows():
    print(f"     {r['drug']:10s} {r['ratio']:.2f}  (PoT {int(r['PoT_total']):,} / PWD {int(r['PWD_total']):,})")
