# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
WORKSTREAM 1 — CDK4/6 patient-level analysis from AVA data.

Goal: refresh the v5 Plays brief P2 narrative ("Kisqali +15.7% growing /
Ibrance −3% / Verzenios −0.1%") with patient-level data instead of IQVIA
Sell-In SEK. Specifically answer:

  Q1. Is the Sell-In growth real at the patient level? (PWD trajectory)
  Q2. Where is Kisqali growth coming from — class-naive starts or
      switches from Ibrance/Verzenios?
  Q3. How does the picture differ across the three biggest regions
      (Stockholm, Västra Götaland, Skåne)?

The AVA file's four metrics let us decompose:
  - "New CDK4/6 user" = class-naive incident (first ever CDK4/6 inhibitor)
  - "New drug user"   = drug-naive incident (first time on THIS drug, may
    have been on another CDK4/6)
  - "Patients with dispensations" (PWD) = monthly flow stock
  - "Patients on treatment" (PoT) = dispensation + 3-month grace stock

  Implied within-class switches = NDU - New CDK4/6 user
  (i.e. patients new to this drug but not new to the class)

OUTPUT (all under delivery/figures/):
  F9_cdk46_growth_source_decomposition.png
  F10_cdk46_long_arc_2017_2026.png
  F11_cdk46_top3_regions.png

Plus prints summary tables to stdout — captured into the findings memo manually.
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
FIG = ROOT / "delivery" / "figures"
DOCS = ROOT / "working" / "docs"

# Pfizer brand colours (consistent with v4-v5 figure set)
COLOR = {
    "Ibrance":   "#0093D0",   # Pfizer blue
    "Kisqali":   "#E03C31",   # Novartis red
    "Verzenios": "#7B2D8E",   # Lilly purple
}

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


# ---------------------------------------------------------------------------
# Load + reshape
# ---------------------------------------------------------------------------
print("Loading AVA CDK4/6 monthly file…")
result = pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevData.RDS"))
df = list(result.values())[0]
df["date"] = pd.to_datetime(df["date"].astype(str))

# Pivot to wide so each metric is a column
wide = (df.pivot_table(index=["date", "region", "drug"], columns="analysis",
                       values="n", aggfunc="sum", fill_value=0)
        .reset_index())
wide.columns.name = None

# Implied switch share
wide["switches_in"] = wide["New drug user"] - wide["New CDK4/6 user"]
# Sanity: switches_in should be >= 0 in steady state. Exception: data noise
# can produce small negatives in low-volume regions. Clip for plotting only.
print(f"  rows: {len(wide):,}")
print(f"  switch_in negative count: {(wide['switches_in'] < 0).sum()} "
      f"(min={wide['switches_in'].min()})")


# ---------------------------------------------------------------------------
# Q1. National PWD trajectory + last-6 vs prev-6 slope per drug
# ---------------------------------------------------------------------------
print("\n=== Q1: National PWD trajectory and slope ===")
nat = wide[wide["region"] == "Sweden"].copy()
nat = nat.sort_values(["drug", "date"]).reset_index(drop=True)

LAST6_END = nat["date"].max()  # 2026-01-15
LAST6_START = LAST6_END - pd.DateOffset(months=5)
PREV6_END = LAST6_START - pd.DateOffset(months=1)
PREV6_START = PREV6_END - pd.DateOffset(months=5)
print(f"  Last 6:  {LAST6_START.date()} → {LAST6_END.date()}")
print(f"  Prev 6:  {PREV6_START.date()} → {PREV6_END.date()}")

slope_rows = []
for drug in ["Ibrance", "Kisqali", "Verzenios"]:
    sub = nat[nat["drug"] == drug]
    last6 = sub[(sub["date"] >= LAST6_START) & (sub["date"] <= LAST6_END)]
    prev6 = sub[(sub["date"] >= PREV6_START) & (sub["date"] <= PREV6_END)]
    last_avg = last6["Patients with dispensations"].mean()
    prev_avg = prev6["Patients with dispensations"].mean()
    pct_change = (last_avg - prev_avg) / prev_avg * 100 if prev_avg else np.nan
    last_pot = last6["Patients on treatment"].mean()
    prev_pot = prev6["Patients on treatment"].mean()
    pot_pct = (last_pot - prev_pot) / prev_pot * 100 if prev_pot else np.nan
    slope_rows.append({
        "drug": drug,
        "PWD_prev6": prev_avg,
        "PWD_last6": last_avg,
        "PWD_pct": pct_change,
        "PoT_prev6": prev_pot,
        "PoT_last6": last_pot,
        "PoT_pct": pot_pct,
    })
slope_df = pd.DataFrame(slope_rows)
print("\n  PWD slope (monthly avg, prev-6 vs last-6):")
print(slope_df.to_string(index=False, float_format="%.1f"))


# ---------------------------------------------------------------------------
# Q2. Decomposition of Kisqali growth — class-naive starts vs within-class switches
# ---------------------------------------------------------------------------
print("\n=== Q2: Growth source decomposition (national, last 6 mo) ===")
decomp = []
for drug in ["Ibrance", "Kisqali", "Verzenios"]:
    sub_last = nat[(nat["drug"] == drug) &
                   (nat["date"] >= LAST6_START) & (nat["date"] <= LAST6_END)]
    sub_prev = nat[(nat["drug"] == drug) &
                   (nat["date"] >= PREV6_START) & (nat["date"] <= PREV6_END)]
    decomp.append({
        "drug": drug,
        "class_naive_starts_last6": sub_last["New CDK4/6 user"].sum(),
        "class_naive_starts_prev6": sub_prev["New CDK4/6 user"].sum(),
        "drug_naive_starts_last6": sub_last["New drug user"].sum(),
        "drug_naive_starts_prev6": sub_prev["New drug user"].sum(),
        "implied_switches_in_last6": sub_last["switches_in"].sum(),
        "implied_switches_in_prev6": sub_prev["switches_in"].sum(),
    })
dec = pd.DataFrame(decomp)
dec["class_naive_change_pct"] = (dec["class_naive_starts_last6"] -
                                  dec["class_naive_starts_prev6"]) / dec["class_naive_starts_prev6"] * 100
dec["switches_in_change_pct"] = (dec["implied_switches_in_last6"] -
                                  dec["implied_switches_in_prev6"]) / dec["implied_switches_in_prev6"] * 100
print(dec.to_string(index=False, float_format="%.1f"))

# Class-share of new starts (last 6)
class_naive_total_last = dec["class_naive_starts_last6"].sum()
print("\n  Share of CLASS-NAIVE starts captured (last 6mo):")
for _, r in dec.iterrows():
    print(f"    {r['drug']:<10} {r['class_naive_starts_last6']:>4} / "
          f"{class_naive_total_last:>4}  ({r['class_naive_starts_last6']/class_naive_total_last*100:>5.1f}%)")


# ---------------------------------------------------------------------------
# Q3. Top-3 regions: Stockholm, Västra Götaland, Skåne
# ---------------------------------------------------------------------------
print("\n=== Q3: Top 3 regions (Stockholm, Västra Götaland, Skåne) ===")
top3 = ["Stockholm", "Västra Götaland", "Skåne"]
reg_rows = []
for region in top3:
    for drug in ["Ibrance", "Kisqali", "Verzenios"]:
        sub_last = wide[(wide["region"] == region) & (wide["drug"] == drug) &
                        (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
        sub_prev = wide[(wide["region"] == region) & (wide["drug"] == drug) &
                        (wide["date"] >= PREV6_START) & (wide["date"] <= PREV6_END)]
        last_pwd = sub_last["Patients with dispensations"].mean()
        prev_pwd = sub_prev["Patients with dispensations"].mean()
        pct = (last_pwd - prev_pwd) / prev_pwd * 100 if prev_pwd else np.nan
        reg_rows.append({"region": region, "drug": drug,
                          "PWD_prev6": prev_pwd, "PWD_last6": last_pwd,
                          "PWD_pct": pct})
reg_df = pd.DataFrame(reg_rows)
print("\n  PWD slope per top-3 region:")
print(reg_df.to_string(index=False, float_format="%.1f"))

# Class-share per region (PWD basis, last 6mo) — three-way race depth
print("\n  Last-6mo PWD share per region (the three-way race):")
share_rows = []
for region in top3 + ["Sweden"]:
    sub = wide[(wide["region"] == region) &
               (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
    totals = sub.groupby("drug")["Patients with dispensations"].sum()
    grand = totals.sum()
    row = {"region": region, "total_PWD_6mo": grand}
    for drug in ["Ibrance", "Kisqali", "Verzenios"]:
        row[f"{drug}_share"] = totals.get(drug, 0) / grand * 100 if grand else 0
    share_rows.append(row)
share_df = pd.DataFrame(share_rows)
print(share_df.to_string(index=False, float_format="%.1f"))


# ---------------------------------------------------------------------------
# FIGURE F9 — growth source decomposition (Kisqali story)
# ---------------------------------------------------------------------------
print("\nRendering F9 (growth source decomposition)…")
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

# Subplot A — class-naive starts per drug, prev-6 vs last-6
x = np.arange(3)
width = 0.35
for ax_idx, (col_prev, col_last, title, ylabel) in enumerate([
    ("class_naive_starts_prev6", "class_naive_starts_last6",
     "Class-naive starts (first-ever CDK4/6)", "Patients (6-month total)"),
    ("implied_switches_in_prev6", "implied_switches_in_last6",
     "Within-class switches in (NDU − class-naive)", "Patients (6-month total)"),
]):
    ax = axes[ax_idx]
    drugs = dec["drug"].tolist()
    prev_vals = dec[col_prev].values
    last_vals = dec[col_last].values
    bars1 = ax.bar(x - width/2, prev_vals, width, label=f"Prev 6mo ({PREV6_START:%b %Y}–{PREV6_END:%b %Y})",
                    color="lightgray", edgecolor="dimgray")
    bars2 = ax.bar(x + width/2, last_vals, width, label=f"Last 6mo ({LAST6_START:%b %Y}–{LAST6_END:%b %Y})",
                    color=[COLOR[d] for d in drugs])
    for bar, v in zip(bars1, prev_vals):
        ax.text(bar.get_x() + bar.get_width()/2, v, f"{int(v)}", ha="center", va="bottom", fontsize=8, color="dimgray")
    for bar, v in zip(bars2, last_vals):
        ax.text(bar.get_x() + bar.get_width()/2, v, f"{int(v)}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(drugs)
    ax.set_title(title)
    if ax_idx == 0:
        ax.set_ylabel(ylabel)
    ax.legend(loc="upper left", fontsize=8, frameon=False)

fig.suptitle(f"F9 — CDK4/6 growth source: class-naive starts vs within-class switches\n"
             f"Sweden, {PREV6_START:%b %Y}–{PREV6_END:%b %Y} (prev 6) vs {LAST6_START:%b %Y}–{LAST6_END:%b %Y} (last 6) (AVA patient counts)",
             fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "F9_cdk46_growth_source_decomposition.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F9_cdk46_growth_source_decomposition.png'}")


# ---------------------------------------------------------------------------
# FIGURE F10 — long arc 2017-2026 PWD per drug, Sweden
# ---------------------------------------------------------------------------
print("Rendering F10 (long arc 2017-2026)…")
fig, ax = plt.subplots(figsize=(11, 5.5))
for drug in ["Ibrance", "Kisqali", "Verzenios"]:
    sub = nat[nat["drug"] == drug].sort_values("date")
    ax.plot(sub["date"], sub["Patients with dispensations"],
            label=drug, color=COLOR[drug], linewidth=2)

# Annotate key inflection points
ax.axvspan(LAST6_START, LAST6_END, alpha=0.15, color="gold",
           label=f"Last 6mo (slope window)")
ax.set_title("F10 — CDK4/6 class long arc: monthly PWD, Sweden, 2017–2026\n"
              "AVA patient counts (Patients with dispensations, monthly)",
              fontsize=11, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Patients with dispensations (national, monthly)")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(loc="upper left", fontsize=10, frameon=True)
fig.tight_layout()
fig.savefig(FIG / "F10_cdk46_long_arc_2017_2026.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F10_cdk46_long_arc_2017_2026.png'}")


# ---------------------------------------------------------------------------
# FIGURE F11 — top-3 regions trajectory (last 24 months) + share table inset
# ---------------------------------------------------------------------------
print("Rendering F11 (top-3 regions)…")
fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
window_start = LAST6_END - pd.DateOffset(months=23)

for ax, region in zip(axes, top3):
    for drug in ["Ibrance", "Kisqali", "Verzenios"]:
        sub = wide[(wide["region"] == region) & (wide["drug"] == drug) &
                   (wide["date"] >= window_start) & (wide["date"] <= LAST6_END)]
        sub = sub.sort_values("date")
        ax.plot(sub["date"], sub["Patients with dispensations"],
                label=drug, color=COLOR[drug], linewidth=1.8)
    # Inset share annotation
    sh = next(r for r in share_rows if r["region"] == region)
    txt = (f"Last 6mo share:\n"
           f"  Ibrance:   {sh['Ibrance_share']:.0f}%\n"
           f"  Kisqali:   {sh['Kisqali_share']:.0f}%\n"
           f"  Verzenios: {sh['Verzenios_share']:.0f}%")
    ax.text(0.03, 0.97, txt, transform=ax.transAxes, fontsize=8,
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="lightgray"))
    ax.set_title(region)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=8)

axes[0].set_ylabel("Patients with dispensations (monthly)")
axes[0].legend(loc="lower left", fontsize=9)
fig.suptitle("F11 — CDK4/6 in the three biggest regions: monthly PWD trajectory + last-6mo share\n"
              "Stockholm / Västra Götaland / Skåne, Feb 2024 – Jan 2026 (AVA patient counts)",
              fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "F11_cdk46_top3_regions.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F11_cdk46_top3_regions.png'}")


# ---------------------------------------------------------------------------
# Persist tables for the findings memo
# ---------------------------------------------------------------------------
out = ROOT / "working" / "data" / "interim"
out.mkdir(parents=True, exist_ok=True)
slope_df.to_csv(out / "ava_w1_cdk46_slope_national.csv", index=False)
dec.to_csv(out / "ava_w1_cdk46_decomposition.csv", index=False)
reg_df.to_csv(out / "ava_w1_cdk46_top3_slope.csv", index=False)
share_df.to_csv(out / "ava_w1_cdk46_top3_share.csv", index=False)
print(f"\n  Tables written to {out}/ava_w1_*.csv")

print("\nDone.")
