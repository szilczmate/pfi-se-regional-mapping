# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
W3 EXTENSION — Vydura IPD switching and persistence analysis.

The audit found 14% of patients (1,047 of 7,664) are exposed to BOTH gepants
over the study window, and 71% of them started on Vydura. This script formalises
that into a switching/persistence analysis with figures.

Questions:
  Q1. Cohort breakdown — Vydura-only / Atogepant-only / Both
  Q2. First drug for "Both" cohort — does Vydura tend to be first-line?
  Q3. Time-to-switch distribution
  Q4. Persistence — for patients who started after Atogepant launch (Jan 2024)
      so both drugs were available, what % each drug retains over 12 months?
  Q5. Per-region switching pattern — Uppsala anomaly investigation

OUTPUT:
  delivery/figures/F18_vydura_switching_persistence.png
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
FIG = ROOT / "delivery" / "figures"
INTERIM = ROOT / "working" / "data" / "interim"

DRUG_COLOR = {"Vydura": "#0093D0", "Atogepant": "#7B2D8E"}

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.family": "DejaVu Sans",
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

duot = list(pyreadr.read_r(str(AVA / "Vydura" / "data_duot.RDS")).values())[0]
duot["edate"] = pd.to_datetime(duot["edate"].astype(str))


# ---------------------------------------------------------------------------
# Q1. Cohort breakdown
# ---------------------------------------------------------------------------
print("=== Q1: Cohort breakdown ===")
patients_per_drug = duot.groupby(["lopnr", "drug"]).size().reset_index(name="n_disp")
pivot = patients_per_drug.pivot_table(index="lopnr", columns="drug", values="n_disp", fill_value=0)
n_total = len(pivot)
n_vyd_only = ((pivot["Vydura"] > 0) & (pivot["Atogepant"] == 0)).sum()
n_ato_only = ((pivot["Vydura"] == 0) & (pivot["Atogepant"] > 0)).sum()
n_both = ((pivot["Vydura"] > 0) & (pivot["Atogepant"] > 0)).sum()
print(f"  Total: {n_total:,}")
print(f"  Vydura only:    {n_vyd_only:,} ({n_vyd_only/n_total*100:.1f}%)")
print(f"  Atogepant only: {n_ato_only:,} ({n_ato_only/n_total*100:.1f}%)")
print(f"  Both (any time): {n_both:,} ({n_both/n_total*100:.1f}%)")


# ---------------------------------------------------------------------------
# Q2. First drug for "Both" cohort
# ---------------------------------------------------------------------------
print("\n=== Q2: First drug seen ===")
first_per_lopnr = (duot.sort_values(["lopnr", "edate"])
                   .drop_duplicates("lopnr", keep="first")[["lopnr", "drug", "edate"]])
first_drug_overall = first_per_lopnr["drug"].value_counts()
print(f"  All patients (n={len(first_per_lopnr):,}) — first drug seen:")
for d, n in first_drug_overall.items():
    print(f"    {d:<10} {n:>5} ({n/len(first_per_lopnr)*100:.1f}%)")

# For both-cohort
both_lopnrs = pivot[(pivot["Vydura"] > 0) & (pivot["Atogepant"] > 0)].index.tolist()
both_first = first_per_lopnr[first_per_lopnr["lopnr"].isin(both_lopnrs)]
print(f"\n  Both-drug cohort (n={len(both_first):,}) — first drug seen:")
for d, n in both_first["drug"].value_counts().items():
    print(f"    {d:<10} {n:>5} ({n/len(both_first)*100:.1f}%)")


# ---------------------------------------------------------------------------
# Q3. Time-to-switch (days from first dispensation to first dispensation of OTHER drug)
# ---------------------------------------------------------------------------
print("\n=== Q3: Time-to-switch ===")
# For both-cohort: get first edate of each drug
both_full = duot[duot["lopnr"].isin(both_lopnrs)].sort_values(["lopnr", "edate"])
first_each_drug = (both_full.groupby(["lopnr", "drug"])["edate"].min()
                   .reset_index().pivot(index="lopnr", columns="drug", values="edate"))
first_each_drug["days_diff"] = (
    (first_each_drug["Atogepant"] - first_each_drug["Vydura"]).dt.days)
# Positive = Vydura first; negative = Atogepant first
print("  Days between first-Vydura and first-Atogepant (positive = Vydura first):")
print(first_each_drug["days_diff"].describe().to_string())

vyd_first = first_each_drug[first_each_drug["days_diff"] > 0]
ato_first = first_each_drug[first_each_drug["days_diff"] < 0]
same_month = first_each_drug[first_each_drug["days_diff"] == 0]
print(f"\n  Vydura first: {len(vyd_first):,} (median switch lag {vyd_first['days_diff'].median():.0f} days)")
print(f"  Atogepant first: {len(ato_first):,} (median switch lag {(-ato_first['days_diff']).median():.0f} days)")
print(f"  Same month: {len(same_month):,}")


# ---------------------------------------------------------------------------
# Q4. Persistence — patients who started after Atogepant launch (Jan 2024)
# ---------------------------------------------------------------------------
print("\n=== Q4: Persistence — post-Atogepant-launch starters ===")
# Atogepant first appears in late 2023/Jan 2024 in Sweden — pick Jan 2024 as start
LAUNCH_DATE = pd.Timestamp("2024-01-01")
post_starters = first_per_lopnr[first_per_lopnr["edate"] >= LAUNCH_DATE].copy()
print(f"  Patients starting after {LAUNCH_DATE.date()}: {len(post_starters):,}")
print(f"  Initial drug split:")
post_first_split = post_starters["drug"].value_counts()
for d, n in post_first_split.items():
    print(f"    {d:<10} {n:>5} ({n/len(post_starters)*100:.1f}%)")

# For each post-launch starter, compute # months over which they had any
# dispensation (very rough persistence proxy)
post_dur = (duot[duot["lopnr"].isin(post_starters["lopnr"])]
            .groupby("lopnr")["edate"].agg(["min", "max", "count"]))
post_dur["span_months"] = ((post_dur["max"] - post_dur["min"]).dt.days / 30.44).round(1)
post_dur = post_dur.merge(post_starters[["lopnr", "drug"]].set_index("lopnr"),
                            left_index=True, right_index=True)
print(f"\n  Persistence by initial drug (post-Jan 2024 starters):")
for drug in ["Vydura", "Atogepant"]:
    sub = post_dur[post_dur["drug"] == drug]
    print(f"    {drug:<10} median span {sub['span_months'].median():.1f} months "
          f"(mean {sub['span_months'].mean():.1f}, n={len(sub):,}); "
          f"median dispensations {sub['count'].median():.0f}")


# ---------------------------------------------------------------------------
# Q5. Per-region switching — Uppsala anomaly check
# ---------------------------------------------------------------------------
print("\n=== Q5: Per-region first-drug split ===")
# Use first observed region per patient (could be anywhere across the cohort)
first_region = (duot.sort_values(["lopnr", "edate"])
                .drop_duplicates("lopnr", keep="first")[["lopnr", "drug", "region"]])
reg_first = first_region.groupby(["region", "drug"]).size().unstack(fill_value=0)
reg_first["Total"] = reg_first.sum(axis=1)
reg_first["Vydura_first_pct"] = reg_first["Vydura"] / reg_first["Total"] * 100
reg_first = reg_first.sort_values("Total", ascending=False)
print("  First-drug split by region (top 8):")
print(reg_first.head(8).to_string(float_format="%.1f"))


# ---------------------------------------------------------------------------
# FIGURE F18 — Switching + persistence panel
# ---------------------------------------------------------------------------
print("\nRendering F18…")
fig, axes = plt.subplots(2, 2, figsize=(13, 8))

# Panel A — Cohort breakdown (donut + numbers)
ax = axes[0, 0]
labels = [f"Vydura only\n{n_vyd_only:,} ({n_vyd_only/n_total*100:.1f}%)",
          f"Atogepant only\n{n_ato_only:,} ({n_ato_only/n_total*100:.1f}%)",
          f"Both at some point\n{n_both:,} ({n_both/n_total*100:.1f}%)"]
sizes = [n_vyd_only, n_ato_only, n_both]
colors = [DRUG_COLOR["Vydura"], DRUG_COLOR["Atogepant"], "#FFA500"]
ax.pie(sizes, labels=labels, colors=colors, startangle=90,
       wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
ax.set_title(f"Patient cohort breakdown\nTotal {n_total:,} unique patients in IPD",
              fontsize=11)

# Panel B — First drug for both-cohort
ax = axes[0, 1]
both_split = both_first["drug"].value_counts()
bars = ax.bar(both_split.index, both_split.values,
              color=[DRUG_COLOR.get(d, "gray") for d in both_split.index],
              edgecolor="dimgray")
for bar, v in zip(bars, both_split.values):
    pct = v / both_split.sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2, v + 10, f"{v:,}\n({pct:.1f}%)",
            ha="center", fontsize=11, fontweight="bold")
ax.set_ylabel("Patients (n)")
ax.set_ylim(0, both_split.max() * 1.25)
ax.set_title(f"Patients on BOTH drugs (n={n_both:,}) — first drug seen\n"
              "Strongly favours Vydura as first-line", fontsize=11)

# Panel C — Time-to-switch histogram
ax = axes[1, 0]
days_data = first_each_drug["days_diff"].dropna()
bins = np.linspace(-800, 800, 41)
ax.hist(days_data[days_data > 0], bins=bins, color=DRUG_COLOR["Vydura"],
        alpha=0.7, label=f"Vydura first → switched ({len(vyd_first):,})")
ax.hist(days_data[days_data < 0], bins=bins, color=DRUG_COLOR["Atogepant"],
        alpha=0.7, label=f"Atogepant first → switched ({len(ato_first):,})")
ax.axvline(0, color="black", linewidth=1)
ax.set_xlabel("Days between first dispensation of each drug (positive = Vydura first)")
ax.set_ylabel("Patients")
ax.legend(loc="upper right", fontsize=9)
ax.set_title(f"Time-to-switch distribution\nMedian Vydura→Aquipta: {vyd_first['days_diff'].median():.0f} d; "
              f"Aquipta→Vydura: {(-ato_first['days_diff']).median():.0f} d", fontsize=11)

# Panel D — Per-region first-drug split (Uppsala anomaly)
ax = axes[1, 1]
top_reg = reg_first.head(8).copy()
top_reg = top_reg[::-1]  # reverse for horizontal bar reading top-down
y = np.arange(len(top_reg))
vyd_pct = top_reg["Vydura"] / top_reg["Total"] * 100
ato_pct = top_reg["Atogepant"] / top_reg["Total"] * 100
ax.barh(y, vyd_pct, color=DRUG_COLOR["Vydura"], label="Vydura first")
ax.barh(y, ato_pct, left=vyd_pct, color=DRUG_COLOR["Atogepant"], label="Atogepant first")
ax.set_yticks(y)
ax.set_yticklabels(top_reg.index)
ax.set_xlabel("% of patients in region (first drug)")
# Highlight Uppsala if in top-8
for i, region in enumerate(top_reg.index):
    if region == "Uppsala":
        ax.get_yticklabels()[i].set_color("red")
        ax.get_yticklabels()[i].set_fontweight("bold")
    pct_v = vyd_pct.iloc[i]
    ax.text(pct_v / 2, i, f"{pct_v:.0f}%", ha="center", va="center",
            fontsize=8, color="white", fontweight="bold")
    pct_a = ato_pct.iloc[i]
    if pct_a > 5:
        ax.text(vyd_pct.iloc[i] + pct_a / 2, i, f"{pct_a:.0f}%", ha="center", va="center",
                fontsize=8, color="white", fontweight="bold")
ax.legend(loc="lower right", fontsize=8)
ax.set_title("First drug seen by region — Uppsala anomaly\nUppsala uniquely starts patients on Atogepant",
              fontsize=11)
ax.set_xlim(0, 100)

fig.suptitle("F18 — Vydura IPD: switching, persistence, and first-drug patterns\n"
              "AVA Vydura/data_duot.RDS, 7,664 patients · Nov 2022 – Mar 2026",
              fontsize=12, fontweight="bold", y=1.005)
fig.tight_layout()
fig.savefig(FIG / "F18_vydura_switching_persistence.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F18_vydura_switching_persistence.png'}")

# Persist tables
reg_first.reset_index().to_csv(INTERIM / "ava_w3b_first_drug_by_region.csv", index=False)
post_dur.reset_index().to_csv(INTERIM / "ava_w3b_persistence_post_jan2024.csv", index=False)
print(f"\n  Tables: {INTERIM}/ava_w3b_*.csv")
print("\nDone.")
