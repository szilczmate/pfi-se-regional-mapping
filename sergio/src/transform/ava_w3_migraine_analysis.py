# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
WORKSTREAM 3 — Migraine class analysis from AVA Vydura data.

Context: v4 doc says "Vydura at 5% structurally small" (versus the full
migraine market including injectable CGRP mAbs). AVA gives us a head-to-head
comparison within the ORAL CGRP-receptor antagonist (gepant) niche:
  Vydura     = rimegepant (Pfizer, oral PRN + preventive)
  Atogepant  = atogepant (AbbVie/Allergan, branded as Aquipta in EU; oral preventive)

Both are ORAL gepants — direct head-to-head competitors within the niche.

Decision question: should Vydura become a 6th portfolio play?

Tests for "go" verdict:
  T1. Total class is growing fast at the patient level → defensible play
  T2. Vydura share is stable or growing vs Atogepant → defensible play
  T3. Vydura regional concentration where Pfizer has stakeholder leverage → focused play
  T4. Class growth absolute (NDU) is meaningful (>1000/year) → has commercial mass

Tests for "no-go" verdict:
  T1'. Class growing slowly or Vydura declining → low priority
  T2'. Vydura ceding share to Atogepant → defensive only, low impact
  T3'. No regional concentration → no anchor for engagement
  T4'. NDU volumes <500/year → too small to justify a play

OUTPUT:
  delivery/figures/F15_migraine_class_trajectory.png
  delivery/figures/F16_migraine_per_region.png
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
FIG = ROOT / "delivery" / "figures"
INTERIM = ROOT / "working" / "data" / "interim"

DRUG_COLOR = {
    "Vydura":     "#0093D0",   # Pfizer blue
    "Atogepant":  "#7B2D8E",   # AbbVie purple-ish (Aquipta brand colour)
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
# Load
# ---------------------------------------------------------------------------
print("Loading Vydura RDS files…")
duot = list(pyreadr.read_r(str(AVA / "Vydura" / "data_duot.RDS")).values())[0]
region_pre = list(pyreadr.read_r(str(AVA / "Vydura" / "region.RDS")).values())[0]

duot["edate"] = pd.to_datetime(duot["edate"].astype(str))
region_pre["month"] = pd.to_datetime(region_pre["month"].astype(str))

print(f"  IPD rows: {len(duot):,}; unique patients: {duot['lopnr'].nunique():,}")
print(f"  Pre-computed prevalence rows: {len(region_pre):,}")


# ---------------------------------------------------------------------------
# Q1. Sweden-level PWD + NDU trajectory
# ---------------------------------------------------------------------------
print("\n=== Q1: Sweden-level trajectory ===")
swe_pwd = (region_pre[region_pre["region"] == "Sweden"]
           .rename(columns={"month": "date", "prevalens": "n_pwd"}))

# Re-derive Sweden NDU from IPD per Sergio's R logic
first_per_lopnr = (duot.sort_values(["lopnr", "edate"])
                   .drop_duplicates("lopnr", keep="first"))
swe_ndu = (first_per_lopnr.groupby(["edate", "drug"], as_index=False).size()
           .rename(columns={"size": "n_ndu", "edate": "date"}))

LAST6_END = swe_pwd["date"].max()  # 2026-03-15
LAST6_START = LAST6_END - pd.DateOffset(months=5)
PREV6_END = LAST6_START - pd.DateOffset(months=1)
PREV6_START = PREV6_END - pd.DateOffset(months=5)

print(f"  Slope windows: prev6 {PREV6_START.date()}–{PREV6_END.date()}, "
      f"last6 {LAST6_START.date()}–{LAST6_END.date()}")

slope_rows = []
for drug in ["Vydura", "Atogepant"]:
    pwd_sub = swe_pwd[swe_pwd["drug"] == drug]
    last6_pwd = pwd_sub[(pwd_sub["date"] >= LAST6_START) & (pwd_sub["date"] <= LAST6_END)]["n_pwd"].mean()
    prev6_pwd = pwd_sub[(pwd_sub["date"] >= PREV6_START) & (pwd_sub["date"] <= PREV6_END)]["n_pwd"].mean()

    ndu_sub = swe_ndu[swe_ndu["drug"] == drug]
    last6_ndu = ndu_sub[(ndu_sub["date"] >= LAST6_START) & (ndu_sub["date"] <= LAST6_END)]["n_ndu"].sum()
    prev6_ndu = ndu_sub[(ndu_sub["date"] >= PREV6_START) & (ndu_sub["date"] <= PREV6_END)]["n_ndu"].sum()

    slope_rows.append({
        "drug": drug,
        "PWD_prev6_avg": prev6_pwd,
        "PWD_last6_avg": last6_pwd,
        "PWD_pct": (last6_pwd - prev6_pwd) / prev6_pwd * 100 if prev6_pwd else np.nan,
        "NDU_prev6_total": prev6_ndu,
        "NDU_last6_total": last6_ndu,
        "NDU_pct": (last6_ndu - prev6_ndu) / prev6_ndu * 100 if prev6_ndu else np.nan,
    })
slope_df = pd.DataFrame(slope_rows)
print("\n  Sweden slope (monthly avg PWD; total NDU per 6mo):")
print(slope_df.to_string(index=False, float_format="%.1f"))

# Class growth and Vydura share
total_pwd_last6 = slope_df["PWD_last6_avg"].sum()
total_pwd_prev6 = slope_df["PWD_prev6_avg"].sum()
class_pwd_pct = (total_pwd_last6 - total_pwd_prev6) / total_pwd_prev6 * 100

vyd_share_last6 = slope_df.loc[slope_df["drug"] == "Vydura", "PWD_last6_avg"].iloc[0] / total_pwd_last6 * 100
vyd_share_prev6 = slope_df.loc[slope_df["drug"] == "Vydura", "PWD_prev6_avg"].iloc[0] / total_pwd_prev6 * 100

print(f"\n  Class total PWD slope: prev6 {total_pwd_prev6:.0f} → last6 {total_pwd_last6:.0f} "
      f"({class_pwd_pct:+.1f}%)")
print(f"  Vydura share of class PWD: prev6 {vyd_share_prev6:.1f}% → last6 {vyd_share_last6:.1f}% "
      f"({vyd_share_last6 - vyd_share_prev6:+.1f}pp)")

# Total NDU (total class growth) — annualised
total_ndu_last6 = slope_df["NDU_last6_total"].sum()
total_ndu_prev6 = slope_df["NDU_prev6_total"].sum()
print(f"\n  Class total NDU (incident): prev6 {total_ndu_prev6:.0f} → last6 {total_ndu_last6:.0f} "
      f"({(total_ndu_last6 - total_ndu_prev6) / total_ndu_prev6 * 100:+.1f}%)")
print(f"  Annualised NDU = {total_ndu_last6 * 2:.0f} new patients/year nationwide")

# NDU share
vyd_ndu_share_last = slope_df.loc[slope_df["drug"] == "Vydura", "NDU_last6_total"].iloc[0] / total_ndu_last6 * 100
print(f"  Vydura share of NDU (last 6mo): {vyd_ndu_share_last:.1f}%")


# ---------------------------------------------------------------------------
# Q2. Per-region pattern — where is Vydura strong vs Atogepant?
# ---------------------------------------------------------------------------
print("\n=== Q2: Per-region pattern (last 6mo PWD share) ===")
reg_last6 = (region_pre[(region_pre["region"] != "Sweden") &
                         (region_pre["month"] >= LAST6_START) &
                         (region_pre["month"] <= LAST6_END)]
             .groupby(["region", "drug"], as_index=False)["prevalens"]
             .sum())
reg_pivot = (reg_last6.pivot(index="region", columns="drug", values="prevalens")
             .fillna(0))
reg_pivot["Total"] = reg_pivot.sum(axis=1)
reg_pivot["Vydura_share"] = reg_pivot["Vydura"] / reg_pivot["Total"] * 100
reg_pivot = reg_pivot.sort_values("Total", ascending=False)
print("\n  Per-region last-6mo PWD totals (suppressed cells excluded):")
print(reg_pivot.to_string(float_format="%.0f"))


# ---------------------------------------------------------------------------
# Q3. Verdict synthesis
# ---------------------------------------------------------------------------
print("\n=== Q3: Verdict synthesis ===")
verdict = {
    "T1_class_growth": class_pwd_pct,
    "T2_vydura_share_pp_change": vyd_share_last6 - vyd_share_prev6,
    "T3_top_region_volume": reg_pivot["Vydura"].max(),
    "T4_annualised_NDU": total_ndu_last6 * 2,
}
for k, v in verdict.items():
    print(f"  {k:<35} {v:>10.1f}")


# ---------------------------------------------------------------------------
# FIGURE F15 — Class trajectory (Sweden): PWD + NDU + share
# ---------------------------------------------------------------------------
print("\nRendering F15 (Sweden trajectory)…")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A — PWD trajectory
ax = axes[0]
for drug in ["Vydura", "Atogepant"]:
    sub = swe_pwd[swe_pwd["drug"] == drug].sort_values("date")
    ax.plot(sub["date"], sub["n_pwd"], label=drug,
            color=DRUG_COLOR[drug], linewidth=2)
ax.axvspan(LAST6_START, LAST6_END, alpha=0.15, color="gold", label="Last 6mo")
ax.set_title("Patients with dispensations (PWD)\nSweden monthly")
ax.set_xlabel("Month")
ax.set_ylabel("Patients (monthly)")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(loc="upper left", fontsize=9)

# Panel B — NDU trajectory
ax = axes[1]
for drug in ["Vydura", "Atogepant"]:
    sub = swe_ndu[swe_ndu["drug"] == drug].sort_values("date")
    ax.plot(sub["date"], sub["n_ndu"], label=drug,
            color=DRUG_COLOR[drug], linewidth=2)
ax.set_title("New drug users (NDU) — incident\nSweden monthly")
ax.set_xlabel("Month")
ax.set_ylabel("New starts (monthly)")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(loc="upper left", fontsize=9)

# Panel C — share trajectory
ax = axes[2]
share_traj = (swe_pwd.pivot(index="date", columns="drug", values="n_pwd")
              .fillna(0))
share_traj["Total"] = share_traj.sum(axis=1)
share_traj["Vydura_share"] = share_traj["Vydura"] / share_traj["Total"] * 100
share_traj["Atogepant_share"] = share_traj["Atogepant"] / share_traj["Total"] * 100
ax.plot(share_traj.index, share_traj["Vydura_share"], label="Vydura share %",
        color=DRUG_COLOR["Vydura"], linewidth=2)
ax.plot(share_traj.index, share_traj["Atogepant_share"], label="Atogepant share %",
        color=DRUG_COLOR["Atogepant"], linewidth=2)
ax.set_title("Vydura share of oral CGRP-receptor\nantagonist class (PWD basis)")
ax.set_xlabel("Month")
ax.set_ylabel("Share (%)")
ax.set_ylim(0, 100)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(loc="lower right", fontsize=9)

fig.suptitle("F15 — Migraine class (oral CGRP gepants) at Sweden level\n"
              "Vydura (rimegepant, Pfizer) vs Atogepant (atogepant, AbbVie); "
              "AVA patient counts, Oct 2022 – Mar 2026",
              fontsize=11, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F15_migraine_class_trajectory.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F15_migraine_class_trajectory.png'}")


# ---------------------------------------------------------------------------
# FIGURE F16 — Per-region landscape
# ---------------------------------------------------------------------------
print("Rendering F16 (per-region)…")
top_regions = reg_pivot.head(8).index.tolist()  # top-8 by total volume

fig, axes = plt.subplots(2, 4, figsize=(15.5, 7), sharex=True)
axes = axes.flatten()
window_start = LAST6_END - pd.DateOffset(months=23)

for i, region in enumerate(top_regions):
    ax = axes[i]
    for drug in ["Vydura", "Atogepant"]:
        sub = region_pre[(region_pre["region"] == region) & (region_pre["drug"] == drug) &
                          (region_pre["month"] >= window_start) &
                          (region_pre["month"] <= LAST6_END)].sort_values("month")
        if not len(sub):
            continue
        ax.plot(sub["month"], sub["prevalens"], label=drug,
                color=DRUG_COLOR[drug], linewidth=1.8)
    # Vydura share annotation
    if region in reg_pivot.index:
        share = reg_pivot.loc[region, "Vydura_share"]
        ax.text(0.03, 0.97, f"Vydura share: {share:.0f}%",
                transform=ax.transAxes, fontsize=8, va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           alpha=0.9, edgecolor="lightgray"))
    ax.set_title(region, fontsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=7)
    if i == 0:
        ax.legend(loc="lower left", fontsize=8)

axes[0].set_ylabel("Patients (PWD monthly)")
axes[4].set_ylabel("Patients (PWD monthly)")
fig.suptitle("F16 — Migraine class (oral gepants) by region: top 8 regions by total volume\n"
              "Vydura (Pfizer) vs Atogepant (AbbVie); pre-computed PWD with regional <5 suppression",
              fontsize=11, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F16_migraine_per_region.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F16_migraine_per_region.png'}")


# Persist
slope_df.to_csv(INTERIM / "ava_w3_migraine_sweden_slope.csv", index=False)
reg_pivot.to_csv(INTERIM / "ava_w3_migraine_per_region.csv")
print(f"\n  Tables: {INTERIM}/ava_w3_*.csv")
print("\nDone.")
