# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Self-audit pass on the AVA workstreams.

Checks:
  A. Did we use all 6 RDS files? (Ibrance yearly + Vyndaqel YTD weren't used in analysis)
  B. Internal consistency — yearly vs monthly Ibrance; YTD vs rolling Vyndaqel
  C. Cross-validation — AVA patient counts vs IQVIA Sell-In SEK (RD-IM + Oncology sheets)
  D. Sjukvårdsregion population back-calculation — does AVA's regional grouping match standard Swedish sjukvårdsregioner?
  E. Factual error sweep — F9 chart text, memo numbers vs CSV exports
  F. Under-exploited dimensions — Vydura switching/persistence from IPD
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import numpy as np
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
WB = ROOT / "delivery" / "06_master_workbook_v29.xlsx"


def banner(s: str) -> None:
    print("\n" + "=" * 90 + f"\n{s}\n" + "=" * 90)


# ---------------------------------------------------------------------------
banner("A. Did we use all 6 files?")
# IbranceyearlyAVA — added to v29 but not used in W1 analysis
# VyndaqelYTD — added to v29 but not used in W2 analysis
# Sanity: compare yearly aggregation of monthly to the yearly file
ibr_m = list(pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevData.RDS")).values())[0]
ibr_y = list(pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevDataYear.RDS")).values())[0]
ibr_m["date"] = pd.to_datetime(ibr_m["date"].astype(str))
ibr_m["year"] = ibr_m["date"].dt.year
ibr_y["year"] = ibr_y["year"].astype(int)

# For "New CDK4/6 user" specifically (incident metric — sum across months should equal yearly)
m_yr = (ibr_m[ibr_m["analysis"] == "New CDK4/6 user"]
        .groupby(["year", "drug", "region"])["n"].sum().reset_index()
        .rename(columns={"n": "n_from_monthly"}))
y_only = (ibr_y[ibr_y["analysis"] == "New CDK4/6 user"]
          [["year", "drug", "region", "n"]].rename(columns={"n": "n_yearly"}))
merge = m_yr.merge(y_only, on=["year", "drug", "region"], how="outer")
merge["match"] = merge["n_from_monthly"] == merge["n_yearly"]
print(f"  'New CDK4/6 user' year-from-monthly vs yearly file: "
      f"{merge['match'].sum()}/{len(merge)} match")
mism = merge[~merge["match"]].head(8)
if len(mism):
    print("  Mismatches (top 8):")
    print(mism.to_string(index=False))


# ---------------------------------------------------------------------------
banner("B. Vyndaqel rolling-3mo vs YTD internal consistency")
vqa_a = list(pyreadr.read_r(str(AVA / "Vyndaquel" / "tab12a.RDS")).values())[0]
vqa_b = list(pyreadr.read_r(str(AVA / "Vyndaquel" / "tab12b.RDS")).values())[0]
vqa_a["date"] = pd.to_datetime(vqa_a["date"].astype(str))
vqa_b["date"] = pd.to_datetime(vqa_b["date"].astype(str))
print(f"  tab12a (rolling 3mo) date range: {vqa_a['date'].min().date()} → {vqa_a['date'].max().date()}")
print(f"  tab12b (budget år)   date range: {vqa_b['date'].min().date()} → {vqa_b['date'].max().date()}")
print(f"  tab12a unique analyses: {sorted(vqa_a['analysis'].unique())}")
print(f"  tab12b unique analyses: {sorted(vqa_b['analysis'].unique())}")

# YTD should equal cumulative sum within each calendar year — but it's "budget år"
# which is a pharmaceutical-specific accumulation. Spot-check: latest month YTD value
# for Vyndaqel × DG3 × Sweden should be close to the rolling-3mo prevalens × ratio
# More useful: just confirm the two tables share the same regional and grupp schema
print(f"\n  tab12a regions: {sorted(vqa_a['region'].unique())}")
print(f"  tab12b regions: {sorted(vqa_b['region'].unique())}")
print(f"  tab12a grupp:   {sorted(vqa_a['grupp'].unique())}")
print(f"  tab12b grupp:   {sorted(vqa_b['grupp'].unique())}")

# Last-month value comparison: tab12a Mar 2026 prevalens (rolling 3mo of Jan/Feb/Mar) vs
# tab12b Mar 2026 (budget år, year-to-date through Mar)
last_a = vqa_a[(vqa_a["date"] == "2026-03-15") &
                (vqa_a["drug"] == "Vyndaqel") &
                (vqa_a["region"] == "Sweden") &
                (vqa_a["grupp"] == "Diagnosgrupp 3") &
                (vqa_a["analysis"].str.startswith("Prevalens rullande"))]
last_b = vqa_b[(vqa_b["date"] == "2026-03-15") &
                (vqa_b["drug"] == "Vyndaqel") &
                (vqa_b["region"] == "Sweden") &
                (vqa_b["grupp"] == "Diagnosgrupp 3") &
                (vqa_b["analysis"].str.startswith("Prevalens budget"))]
print(f"\n  Mar 2026 Vyndaqel × DG3 × Sweden:")
print(f"    rolling 3mo prevalens: {last_a['n'].iloc[0] if len(last_a) else 'n/a'}")
print(f"    budget-år prevalens  : {last_b['n'].iloc[0] if len(last_b) else 'n/a'}")


# ---------------------------------------------------------------------------
banner("C. Cross-validate AVA patient counts vs IQVIA Sell-In")
# IQVIA sheets: RD-IM IQVIA detail (Migraine + ATTR among others), Oncology IQVIA detail (CDK4/6)
wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)

# C1. CDK4/6: AVA Sweden last-6mo PWD vs IQVIA Sell-In units last-6mo
# Read Oncology IQVIA detail sheet
print("\n--- C1: CDK4/6 cross-check (AVA PWD vs IQVIA units) ---")
ws = wb["Oncology IQVIA detail"]
oncol_rows = []
for row in ws.iter_rows(min_row=1, max_row=2, values_only=True):
    print(f"  header sample: {row[:8]}")
    break
# Read full sheet
data = list(ws.values)
hdr = data[0]
df_iqvia_onc = pd.DataFrame(data[1:], columns=hdr)
print(f"  Oncology IQVIA shape: {df_iqvia_onc.shape}")
print(f"  Oncology IQVIA columns: {list(df_iqvia_onc.columns)}")
print(f"  Oncology IQVIA unique products (first 12): {sorted(df_iqvia_onc.iloc[:, 0].dropna().unique())[:12] if df_iqvia_onc.shape[1] else 'n/a'}")

# C2. Migraine: AVA Vydura/Atogepant vs IQVIA RD-IM Migraine sheet
print("\n--- C2: Migraine cross-check (AVA Vydura PWD vs IQVIA RD-IM units) ---")
ws = wb["RD-IM IQVIA detail"]
data = list(ws.values)
hdr = data[0]
df_iqvia_rdim = pd.DataFrame(data[1:], columns=hdr)
print(f"  RD-IM IQVIA shape: {df_iqvia_rdim.shape}")
print(f"  RD-IM IQVIA columns: {list(df_iqvia_rdim.columns)[:12]}")
# Look for migraine-specific rows
sample = df_iqvia_rdim.iloc[0:3].to_dict("records")
for s in sample:
    print(f"  sample row: {dict(list(s.items())[:8])}")

wb.close()


# ---------------------------------------------------------------------------
banner("D. Sjukvårdsregion population back-calculation")
# From AVA, prev_count and prev_per100k let us back out the implied population
sub = vqa_a[(vqa_a["drug"] == "Vyndaqel") &
             (vqa_a["grupp"] == "Diagnosgrupp 3") &
             (vqa_a["analysis"] == "Prevalens rullande 3 månader")]
p100k_sub = vqa_a[(vqa_a["drug"] == "Vyndaqel") &
                   (vqa_a["grupp"] == "Diagnosgrupp 3") &
                   (vqa_a["analysis"] == "Prevalens per 100k rullande 3 månader")]
merged = sub[["date", "region", "n"]].rename(columns={"n": "count"}).merge(
    p100k_sub[["date", "region", "n"]].rename(columns={"n": "per100k"}),
    on=["date", "region"])
merged["implied_pop"] = merged["count"] / merged["per100k"] * 100_000
implied = (merged.groupby("region")["implied_pop"].mean().round(0).astype(int)
           .reset_index().rename(columns={"implied_pop": "implied_pop_avg"}))
print("\n  Implied population per AVA region (mean of monthly back-calculations):")
print(implied.to_string(index=False))
total_excl_swe = implied[implied["region"] != "Sweden"]["implied_pop_avg"].sum()
swe = implied[implied["region"] == "Sweden"]["implied_pop_avg"].iloc[0] if "Sweden" in implied["region"].values else 0
print(f"\n  Sum of regional pops (excl Sweden, excl '99'): {total_excl_swe:,}")
print(f"  Sweden:                                          {swe:,}")
print(f"  Sum/Sweden ratio: {total_excl_swe/swe:.3f}")


# ---------------------------------------------------------------------------
banner("E. F9 chart text vs script numbers — factual error sweep")
# F9's suptitle says 'Apr–Sep 2025 (prev 6) vs Aug 2025–Jan 2026 (last 6)'
# Script computes: PREV6 = 2025-02-15 to 2025-07-15, LAST6 = 2025-08-15 to 2026-01-15
# So suptitle should say 'Feb–Jul 2025 (prev 6)' not 'Apr–Sep 2025'
# This is a CONFIRMED factual error.

slope_csv = pd.read_csv(ROOT / "working" / "data" / "interim" / "ava_w1_cdk46_slope_national.csv")
print(f"\n  W1 slope CSV (national):")
print(slope_csv.to_string(index=False, float_format="%.1f"))

# Verify the prev6/last6 windows
ibr_swe = ibr_m[(ibr_m["region"] == "Sweden") & (ibr_m["drug"] == "Ibrance")]
LAST6_END = ibr_swe["date"].max()
LAST6_START = LAST6_END - pd.DateOffset(months=5)
PREV6_END = LAST6_START - pd.DateOffset(months=1)
PREV6_START = PREV6_END - pd.DateOffset(months=5)
print(f"\n  Verified date windows:")
print(f"    PREV6: {PREV6_START.date()} → {PREV6_END.date()}  (months: "
      f"{', '.join(pd.date_range(PREV6_START, PREV6_END, freq='MS').strftime('%b %Y'))})")
print(f"    LAST6: {LAST6_START.date()} → {LAST6_END.date()}  (months: "
      f"{', '.join(pd.date_range(LAST6_START, LAST6_END, freq='MS').strftime('%b %Y'))})")
print(f"  → F9 suptitle currently says 'Apr–Sep 2025 (prev 6)' — INCORRECT, should be 'Feb–Jul 2025'.")


# ---------------------------------------------------------------------------
banner("F. Under-exploited: Vydura IPD switching/persistence")
duot = list(pyreadr.read_r(str(AVA / "Vydura" / "data_duot.RDS")).values())[0]
duot["edate"] = pd.to_datetime(duot["edate"].astype(str))

# Patients who appear with both drugs at some point
patients_per_drug = duot.groupby(["lopnr", "drug"]).size().reset_index(name="n_dispensations")
pivot = patients_per_drug.pivot_table(index="lopnr", columns="drug", values="n_dispensations", fill_value=0)
both = pivot[(pivot["Vydura"] > 0) & (pivot["Atogepant"] > 0)]
only_vyd = pivot[(pivot["Vydura"] > 0) & (pivot["Atogepant"] == 0)]
only_ato = pivot[(pivot["Vydura"] == 0) & (pivot["Atogepant"] > 0)]
print(f"\n  Total unique patients in IPD: {len(pivot):,}")
print(f"    Only Vydura ever  : {len(only_vyd):,}")
print(f"    Only Atogepant ever: {len(only_ato):,}")
print(f"    Both at some point: {len(both):,}  ({len(both)/len(pivot)*100:.1f}% of cohort)")

# Persistence: avg # dispensations per patient
print(f"\n  Mean dispensations per patient:")
print(f"    Vydura users  : {pivot[pivot['Vydura']>0]['Vydura'].mean():.2f}")
print(f"    Atogepant users: {pivot[pivot['Atogepant']>0]['Atogepant'].mean():.2f}")

# Switch direction: for "both" patients, did Vydura come first or Atogepant?
both_lopnrs = both.index.tolist()
first_drug = (duot[duot["lopnr"].isin(both_lopnrs)]
              .sort_values(["lopnr", "edate"])
              .drop_duplicates("lopnr", keep="first")[["lopnr", "drug"]])
switch_dir = first_drug["drug"].value_counts()
print(f"\n  For patients on BOTH drugs over time, FIRST drug seen:")
for d, n in switch_dir.items():
    print(f"    {d:<12} {n:>4} patients ({n/len(both_lopnrs)*100:.1f}%)")


# ---------------------------------------------------------------------------
banner("G. Yearly file regional check — does it match monthly aggregation for ALL analyses?")
all_analyses = ibr_m["analysis"].unique()
print(f"  Monthly file analyses: {sorted(all_analyses)}")
print(f"  Yearly file analyses : {sorted(ibr_y['analysis'].unique())}")
# Note: 'Patients on treatment' is in monthly only (we knew this)
# Aggregating monthly stock metrics (PWD, PoT) to yearly is meaningful as an avg, not sum.
# 'New drug user' and 'New CDK4/6 user' are flow metrics — sum of monthly = yearly count.

print("\n  'New drug user' year-from-monthly vs yearly file (Sweden only, last 5 years):")
m_swe = ibr_m[(ibr_m["region"] == "Sweden") & (ibr_m["analysis"] == "New drug user")]
m_y_swe = m_swe.groupby(["year", "drug"])["n"].sum().reset_index().rename(columns={"n": "from_monthly"})
y_swe = ibr_y[(ibr_y["region"] == "Sweden") & (ibr_y["analysis"] == "New drug user")][["year", "drug", "n"]].rename(columns={"n": "yearly_file"})
m_y_swe = m_y_swe.merge(y_swe, on=["year", "drug"])
m_y_swe["delta"] = m_y_swe["from_monthly"] - m_y_swe["yearly_file"]
print(m_y_swe.tail(15).to_string(index=False))
print(f"\n  Total mismatches: {(m_y_swe['delta'] != 0).sum()}/{len(m_y_swe)}")

print("\nDone.")
