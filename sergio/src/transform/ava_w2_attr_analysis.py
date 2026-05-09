# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
WORKSTREAM 2 — ATTR class analysis from AVA Vyndaqel data at sjukvårdsregion level.

Goal: refresh the v5 Plays brief P1 ("Northern ATTR-CM Cornerstone — Vyndaqel
anchor at Norrlands universitetssjukhus Umeå") with patient-level data at
sjukvårdsregion granularity (the NT-rådet samverkansmodell layer).

Confirmed mapping (2026-05-05):
  DG3        = ATTR-CM (cardiomyopathy)            HIGH CONFIDENCE
  DG1 + DG2  = ATTR-PN sub-buckets (exact pending) → reported COMBINED
  Oavsett    = aggregate across all diagnosis groups

Drugs:
  Vyndaqel    (tafamidis, Pfizer)        N07XX08 — covers all subtypes
  Amvuttra    (vutrisiran, Alnylam)      N07XX18 — primarily PN in window
  Beyonttra   (acoramidis, BridgeBio)    C01EB25 — ATTR-CM only
  Diflunisal  (NSAID, off-label)         N02BA11 — all subtypes

Sjukvårdsregioner: Norrland, Mellansverige, Stockholm Sörmland, Sydöstra,
                   Södra, VGR (+ Sweden, drop '99' uppgift saknas).

Questions:
  Q1. ATTR-CM (DG3) competitive landscape — is Vyndaqel still dominant or is
      Beyonttra cutting in? Per sjukvårdsregion incidence + prevalence.
  Q2. ATTR-PN total (DG1+DG2) — Vyndaqel vs Amvuttra share trajectory.
  Q3. Northern cornerstone validation — does Norrland still over-index for
      Vyndaqel ATTR-CM on a per-100k basis? How big is the gap to other regions?
  Q4. Beyonttra launch curve — when did it appear? Where first?

OUTPUT:
  delivery/figures/F12_attr_cm_competitive_landscape.png
  delivery/figures/F13_attr_pn_competitive_landscape.png
  delivery/figures/F14_northern_cornerstone_validation.png
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
INTERIM.mkdir(parents=True, exist_ok=True)

DRUG_COLOR = {
    "Vyndaqel":   "#0093D0",   # Pfizer blue
    "Amvuttra":   "#7B2D8E",   # Alnylam purple
    "Beyonttra":  "#E03C31",   # BridgeBio red
    "Diflunisal": "#888888",   # generic grey
}

# Sjukvårdsregioner with population (2024 SCB) — used for per-100k validation
# of the AVA per-100k column. Source: SCB regional totals summed.
# Approximate populations (2024):
SVR_POP = {
    "Stockholm Sörmland":  2_775_000,    # Stockholm + Sörmland (note AVA grouping)
    "Norrland":            894_000,      # Norrbotten + Västerbotten + Västernorrland + Jämtland
    "Mellansverige":       2_245_000,    # Uppsala + Örebro + Värmland + Västmanland + Dalarna + Gävleborg
    "Sydöstra":            1_088_000,    # Östergötland + Jönköping + Kalmar
    "Södra":               1_870_000,    # Skåne + Blekinge + Kronoberg + (Halland?)
    "VGR":                 1_780_000,    # Västra Götaland (sometimes inc. Halland)
    "Sweden":             10_650_000,
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
# Load + prep
# ---------------------------------------------------------------------------
print("Loading Vyndaquel/tab12a (rolling 3mo)…")
result = pyreadr.read_r(str(AVA / "Vyndaquel" / "tab12a.RDS"))
df = list(result.values())[0]
df["date"] = pd.to_datetime(df["date"].astype(str))

# Drop trace '99' rows
df = df[df["region"] != "99"].copy()

# Drop NaN n (small-cell suppression at this point becomes 0 for plotting)
df["n"] = pd.to_numeric(df["n"], errors="coerce")

print(f"  rows after dropping '99': {len(df):,}")
print(f"  drugs: {sorted(df['drug'].unique())}")
print(f"  regions: {sorted(df['region'].unique())}")
print(f"  grupp: {sorted(df['grupp'].unique())}")
print(f"  analyses: {sorted(df['analysis'].unique())}")

# Build a clean wide structure: index by date, region, drug, grupp; columns = analysis
df["analysis_key"] = df["analysis"].map({
    "Incidens rullande 3 månader": "incidens_count",
    "Incidens per 100k rullande 3 månader": "incidens_per100k",
    "Prevalens rullande 3 månader": "prevalens_count",
    "Prevalens per 100k rullande 3 månader": "prevalens_per100k",
})
wide = (df.pivot_table(index=["date", "region", "drug", "grupp"],
                       columns="analysis_key", values="n", aggfunc="sum")
        .reset_index())
wide.columns.name = None

# Slope windows
LAST6_END = wide["date"].max()
LAST6_START = LAST6_END - pd.DateOffset(months=5)
PREV6_END = LAST6_START - pd.DateOffset(months=1)
PREV6_START = PREV6_END - pd.DateOffset(months=5)
print(f"  Slope windows: prev6 {PREV6_START.date()}–{PREV6_END.date()}, "
      f"last6 {LAST6_START.date()}–{LAST6_END.date()}")


# ---------------------------------------------------------------------------
# Q1. ATTR-CM (DG3) competitive landscape per sjukvårdsregion
# ---------------------------------------------------------------------------
print("\n=== Q1: ATTR-CM (DG3) competitive landscape ===")
cm = wide[wide["grupp"] == "Diagnosgrupp 3"].copy()
print(f"  DG3 rows: {len(cm)}, drugs present: {sorted(cm['drug'].unique())}")

# Last-6 vs prev-6 slope per drug at Sweden level (prevalens — stock metric)
print("\n  ATTR-CM Sweden — drug PWD (prevalens count) prev-6 vs last-6:")
cm_swe = cm[cm["region"] == "Sweden"]
cm_slope_rows = []
for drug in sorted(cm_swe["drug"].unique()):
    sub = cm_swe[cm_swe["drug"] == drug]
    last_avg = sub[(sub["date"] >= LAST6_START) & (sub["date"] <= LAST6_END)]["prevalens_count"].mean()
    prev_avg = sub[(sub["date"] >= PREV6_START) & (sub["date"] <= PREV6_END)]["prevalens_count"].mean()
    last_inc = sub[(sub["date"] >= LAST6_START) & (sub["date"] <= LAST6_END)]["incidens_count"].mean()
    prev_inc = sub[(sub["date"] >= PREV6_START) & (sub["date"] <= PREV6_END)]["incidens_count"].mean()
    pct_p = (last_avg - prev_avg) / prev_avg * 100 if prev_avg else np.nan
    pct_i = (last_inc - prev_inc) / prev_inc * 100 if prev_inc else np.nan
    cm_slope_rows.append({"drug": drug, "prev_prev_avg": prev_avg,
                           "prev_last_avg": last_avg, "prev_pct": pct_p,
                           "inc_prev_avg": prev_inc, "inc_last_avg": last_inc, "inc_pct": pct_i})
cm_slope = pd.DataFrame(cm_slope_rows)
print(cm_slope.to_string(index=False, float_format="%.1f"))

# Share at Sweden level (prevalens, last-6 mean)
print("\n  ATTR-CM Sweden — last-6mo prevalens share:")
totals = cm_swe[(cm_swe["date"] >= LAST6_START) & (cm_swe["date"] <= LAST6_END)] \
    .groupby("drug")["prevalens_count"].sum()
grand = totals.sum()
for drug, val in totals.sort_values(ascending=False).items():
    pct = val / grand * 100 if grand else 0
    print(f"    {drug:<12} {val:>6.1f}  ({pct:>5.1f}%)")


# ---------------------------------------------------------------------------
# Q2. ATTR-PN total (DG1+DG2) per sjukvårdsregion
# ---------------------------------------------------------------------------
print("\n=== Q2: ATTR-PN total (DG1+DG2 combined) ===")
pn = wide[wide["grupp"].isin(["Diagnosgrupp 1", "Diagnosgrupp 2"])].copy()
# Combine DG1+DG2 into a single PN total
pn_combined = (pn.groupby(["date", "region", "drug"], as_index=False)
                  [["incidens_count", "incidens_per100k", "prevalens_count", "prevalens_per100k"]]
                  .sum())
print(f"  DG1+DG2 combined rows: {len(pn_combined)}")
print(f"  Drugs in PN: {sorted(pn_combined['drug'].unique())}")

# Sweden PN slope per drug
pn_swe = pn_combined[pn_combined["region"] == "Sweden"]
pn_slope_rows = []
for drug in sorted(pn_swe["drug"].unique()):
    sub = pn_swe[pn_swe["drug"] == drug]
    last_avg = sub[(sub["date"] >= LAST6_START) & (sub["date"] <= LAST6_END)]["prevalens_count"].mean()
    prev_avg = sub[(sub["date"] >= PREV6_START) & (sub["date"] <= PREV6_END)]["prevalens_count"].mean()
    pct_p = (last_avg - prev_avg) / prev_avg * 100 if prev_avg else np.nan
    pn_slope_rows.append({"drug": drug, "prev_avg": prev_avg, "last_avg": last_avg, "pct": pct_p})
pn_slope = pd.DataFrame(pn_slope_rows)
print("\n  ATTR-PN Sweden (DG1+DG2 combined) — prevalens slope:")
print(pn_slope.to_string(index=False, float_format="%.1f"))

# PN share Sweden last-6
totals_pn = pn_swe[(pn_swe["date"] >= LAST6_START) & (pn_swe["date"] <= LAST6_END)] \
    .groupby("drug")["prevalens_count"].sum()
grand_pn = totals_pn.sum()
print(f"\n  ATTR-PN Sweden — last-6mo prevalens share:")
for drug, val in totals_pn.sort_values(ascending=False).items():
    pct = val / grand_pn * 100 if grand_pn else 0
    print(f"    {drug:<12} {val:>6.1f}  ({pct:>5.1f}%)")


# ---------------------------------------------------------------------------
# Q3. Northern cornerstone validation — Vyndaqel ATTR-CM per-100k by sjukvårdsregion
# ---------------------------------------------------------------------------
print("\n=== Q3: Northern cornerstone — Vyndaqel ATTR-CM per-100k by sjukvårdsregion ===")
cm_vyn = cm[(cm["drug"] == "Vyndaqel") & (cm["region"] != "Sweden")].copy()
last6_vyn = cm_vyn[(cm_vyn["date"] >= LAST6_START) & (cm_vyn["date"] <= LAST6_END)]

# Mean per-100k over last 6 months per region
cornerstone = (last6_vyn.groupby("region")
                .agg(prev_per100k=("prevalens_per100k", "mean"),
                     inc_per100k=("incidens_per100k", "mean"),
                     prev_count=("prevalens_count", "mean"),
                     inc_count=("incidens_count", "mean"))
                .reset_index()
                .sort_values("prev_per100k", ascending=False))
# Compare to Sweden
swe = cm[(cm["drug"] == "Vyndaqel") & (cm["region"] == "Sweden") &
         (cm["date"] >= LAST6_START) & (cm["date"] <= LAST6_END)]
swe_per100k = swe["prevalens_per100k"].mean()
swe_count = swe["prevalens_count"].mean()
cornerstone["index_vs_sweden"] = cornerstone["prev_per100k"] / swe_per100k * 100
print(cornerstone.to_string(index=False, float_format="%.2f"))
print(f"  Sweden mean prevalens per 100k: {swe_per100k:.2f}")
print(f"  Sweden mean prevalens count:    {swe_count:.1f}")


# ---------------------------------------------------------------------------
# Q4. Beyonttra launch curve
# ---------------------------------------------------------------------------
print("\n=== Q4: Beyonttra launch curve (ATTR-CM) ===")
bey = cm[(cm["drug"] == "Beyonttra") & (cm["region"] == "Sweden")].sort_values("date")
print(f"  First non-zero month: {bey[bey['incidens_count'] > 0]['date'].min()}")
print(f"  Latest month     : {bey['date'].max()}")
print(f"  Latest prevalens : {bey['prevalens_count'].iloc[-1] if len(bey) else 'n/a'}")

# Per-region first appearance
bey_reg = cm[(cm["drug"] == "Beyonttra") & (cm["region"] != "Sweden") &
             (cm["incidens_count"] > 0)]
first_by_region = bey_reg.groupby("region")["date"].min().sort_values()
print(f"\n  Beyonttra first appearance by sjukvårdsregion:")
for region, dt in first_by_region.items():
    print(f"    {region:<22} {dt.date()}")


# ---------------------------------------------------------------------------
# FIGURE F12 — ATTR-CM competitive landscape (Sweden + 6 sjukvårdsregioner)
# ---------------------------------------------------------------------------
print("\nRendering F12 (ATTR-CM competitive landscape)…")
fig, axes = plt.subplots(2, 4, figsize=(15.5, 7), sharex=True)
axes = axes.flatten()
regions_to_plot = ["Sweden", "Norrland", "Mellansverige", "Stockholm Sörmland",
                   "Sydöstra", "Södra", "VGR"]
window_start = LAST6_END - pd.DateOffset(months=23)

for i, region in enumerate(regions_to_plot):
    ax = axes[i]
    for drug in ["Vyndaqel", "Beyonttra", "Diflunisal"]:
        sub = cm[(cm["region"] == region) & (cm["drug"] == drug) &
                 (cm["date"] >= window_start) & (cm["date"] <= LAST6_END)]
        sub = sub.sort_values("date")
        if not len(sub):
            continue
        ax.plot(sub["date"], sub["prevalens_count"], label=drug,
                color=DRUG_COLOR.get(drug, "black"), linewidth=1.8)
    ax.set_title(region, fontsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=7)
    if i == 0:
        ax.legend(loc="upper left", fontsize=8)

# Hide unused 8th panel
axes[7].axis("off")

axes[0].set_ylabel("Patients (rolling 3-month prevalens)")
axes[4].set_ylabel("Patients (rolling 3-month prevalens)")
fig.suptitle("F12 — ATTR-CM (Diagnosgrupp 3): drug-level prevalens by sjukvårdsregion\n"
              "Vyndaqel (tafamidis, Pfizer) · Beyonttra (acoramidis, BridgeBio, NEW) · "
              "Diflunisal (off-label NSAID); rolling 3mo, Apr 2024–Mar 2026",
              fontsize=11, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F12_attr_cm_competitive_landscape.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F12_attr_cm_competitive_landscape.png'}")


# ---------------------------------------------------------------------------
# FIGURE F13 — ATTR-PN total (DG1+DG2) competitive landscape
# ---------------------------------------------------------------------------
print("Rendering F13 (ATTR-PN competitive landscape)…")
fig, axes = plt.subplots(2, 4, figsize=(15.5, 7), sharex=True)
axes = axes.flatten()

for i, region in enumerate(regions_to_plot):
    ax = axes[i]
    for drug in ["Vyndaqel", "Amvuttra", "Diflunisal"]:
        sub = pn_combined[(pn_combined["region"] == region) & (pn_combined["drug"] == drug) &
                          (pn_combined["date"] >= window_start) & (pn_combined["date"] <= LAST6_END)]
        sub = sub.sort_values("date")
        if not len(sub):
            continue
        ax.plot(sub["date"], sub["prevalens_count"], label=drug,
                color=DRUG_COLOR.get(drug, "black"), linewidth=1.8)
    ax.set_title(region, fontsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=7)
    if i == 0:
        ax.legend(loc="upper left", fontsize=8)

axes[7].axis("off")
axes[0].set_ylabel("Patients (rolling 3-month prevalens, DG1+DG2)")
axes[4].set_ylabel("Patients (rolling 3-month prevalens, DG1+DG2)")
fig.suptitle("F13 — ATTR-PN total (Diagnosgrupp 1 + 2): drug-level prevalens by sjukvårdsregion\n"
              "Vyndaqel (tafamidis, Pfizer) · Amvuttra (vutrisiran, Alnylam) · Diflunisal (off-label); "
              "rolling 3mo, Apr 2024–Mar 2026",
              fontsize=11, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F13_attr_pn_competitive_landscape.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F13_attr_pn_competitive_landscape.png'}")


# ---------------------------------------------------------------------------
# FIGURE F14 — Northern cornerstone validation: CM vs PN side-by-side
# (Reframes v5 narrative: Norrland over-indexes on PN, not CM.)
# ---------------------------------------------------------------------------
print("Rendering F14 (Northern cornerstone — CM vs PN)…")

# Build the same regional-per100k tables for both diagnosis groups
def per100k_by_region(grupp_filter):
    sub = wide[(wide["drug"] == "Vyndaqel") & grupp_filter(wide) &
               (wide["region"] != "Sweden") &
               (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
    if "DG1+DG2" in grupp_filter.__doc__:
        sub = sub.groupby(["date", "region", "drug"], as_index=False)[
            ["prevalens_per100k", "prevalens_count"]].sum()
    out = (sub.groupby("region")
              .agg(prev_per100k=("prevalens_per100k", "mean"),
                   prev_count=("prevalens_count", "mean"))
              .reset_index().sort_values("prev_per100k", ascending=False))
    swe_sub = wide[(wide["drug"] == "Vyndaqel") & grupp_filter(wide) &
                   (wide["region"] == "Sweden") &
                   (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
    if "DG1+DG2" in grupp_filter.__doc__:
        swe_sub = swe_sub.groupby(["date", "drug"], as_index=False)[
            ["prevalens_per100k", "prevalens_count"]].sum()
    swe_p = swe_sub["prevalens_per100k"].mean()
    out["index_vs_sweden"] = out["prev_per100k"] / swe_p * 100
    return out, swe_p

def f_cm(w):
    """ATTR-CM (DG3)"""
    return w["grupp"] == "Diagnosgrupp 3"
def f_pn(w):
    """ATTR-PN total (DG1+DG2)"""
    return w["grupp"].isin(["Diagnosgrupp 1", "Diagnosgrupp 2"])

cs_cm, swe_cm = per100k_by_region(f_cm)
cs_pn, swe_pn = per100k_by_region(f_pn)

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=False)

# Panel A — ATTR-CM (DG3) per-100k by sjukvårdsregion
ax = axes[0]
colors_cm = ["#0093D0" if r == "Norrland" else "lightgray" for r in cs_cm["region"]]
ax.barh(cs_cm["region"], cs_cm["prev_per100k"], color=colors_cm, edgecolor="dimgray")
for i, (region, val, idx) in enumerate(zip(cs_cm["region"], cs_cm["prev_per100k"],
                                            cs_cm["index_vs_sweden"])):
    ax.text(val + 0.05, i, f"{val:.2f}  (idx {idx:.0f})", va="center", fontsize=9,
            fontweight="bold" if region == "Norrland" else "normal",
            color="#0093D0" if region == "Norrland" else "black")
ax.axvline(swe_cm, color="red", linestyle="--", linewidth=1.2,
           label=f"Sweden mean ({swe_cm:.2f})")
ax.set_xlabel("Prevalens per 100k (last 6mo mean)")
ax.set_title("ATTR-CM (Diagnosgrupp 3)\n"
              "Norrland is BELOW Sweden (idx 89) — Södra leads (idx 156)",
              fontsize=10)
ax.legend(loc="lower right", fontsize=9)

# Panel B — ATTR-PN total (DG1+DG2) per-100k by sjukvårdsregion
ax = axes[1]
colors_pn = ["#0093D0" if r == "Norrland" else "lightgray" for r in cs_pn["region"]]
ax.barh(cs_pn["region"], cs_pn["prev_per100k"], color=colors_pn, edgecolor="dimgray")
for i, (region, val, idx) in enumerate(zip(cs_pn["region"], cs_pn["prev_per100k"],
                                            cs_pn["index_vs_sweden"])):
    ax.text(val + 0.2, i, f"{val:.2f}  (idx {idx:.0f})", va="center", fontsize=9,
            fontweight="bold" if region == "Norrland" else "normal",
            color="#0093D0" if region == "Norrland" else "black")
ax.axvline(swe_pn, color="red", linestyle="--", linewidth=1.2,
           label=f"Sweden mean ({swe_pn:.2f})")
ax.set_xlabel("Prevalens per 100k (last 6mo mean)")
ax.set_title("ATTR-PN total (Diagnosgrupp 1 + 2)\n"
              "Norrland 7.6× Sweden (idx 758) — V30M Skellefteå founder cluster",
              fontsize=10)
ax.legend(loc="lower right", fontsize=9)

fig.suptitle("F14 — Northern cornerstone is for ATTR-PN (founder variant), NOT ATTR-CM\n"
              "Vyndaqel (tafamidis) prevalens per 100k by sjukvårdsregion, last 6mo (Oct 2025–Mar 2026)",
              fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F14_northern_cornerstone_validation.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F14_northern_cornerstone_validation.png'}")


# ---------------------------------------------------------------------------
# Persist tables
# ---------------------------------------------------------------------------
cm_slope.to_csv(INTERIM / "ava_w2_attr_cm_sweden_slope.csv", index=False)
pn_slope.to_csv(INTERIM / "ava_w2_attr_pn_sweden_slope.csv", index=False)
cornerstone.to_csv(INTERIM / "ava_w2_northern_cornerstone.csv", index=False)
print(f"\n  Tables: {INTERIM}/ava_w2_*.csv")
print("\nDone.")
