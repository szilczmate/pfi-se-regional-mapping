# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Deep-dive on the five open questions about the AVA data, using only file
contents (no external sources):

  Q1. What is region "99" in Vyndaqel? — distribution, magnitude, drugs/atc/grupp involved
  Q2. What does `grupp` map to per ATC? — full unique list + ATC×grupp cross-tab
  Q3. "Patients on treatment" definition (Ibrance monthly) — compare to
       "Patients with dispensations" head-to-head
  Q4. Is Vydura `region.RDS::prevalens` derivable from IPD via Sergio's R code?
       Re-derive both "New drug users" and "Patients with dispensations" from
       data_duot and compare to region.RDS prevalens
  Q5. Does Vydura IPD sum across 21 regions match region.RDS Sweden row?

Also look for any R attributes (labels, comments) that pyreadr exposes.
"""

from pathlib import Path
import pyreadr
import pandas as pd
import sys

# Force UTF-8 stdout (Windows default cp1252 mangles Swedish letters when piped)
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/AVA data for mapping 2026-05-02")


def load(folder: str, fname: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(ROOT / folder / fname))
    df = list(result.values())[0]
    return df


def banner(s: str) -> None:
    print("\n" + "=" * 90 + f"\n{s}\n" + "=" * 90)


# ----------------------------------------------------------------------------
banner("Q1.  Vyndaqel region '99' — what is it?")
tab12a = load("Vyndaquel", "tab12a.RDS")
tab12b = load("Vyndaquel", "tab12b.RDS")

for name, df in [("tab12a", tab12a), ("tab12b", tab12b)]:
    print(f"\n--- {name} ---")
    print(f"All unique regions: {sorted(df['region'].unique())}")
    sub = df[df["region"] == "99"]
    print(f"Rows where region == '99': {len(sub):,}")
    if len(sub):
        print(f"  Drugs   : {sorted(sub['drug'].unique())}")
        print(f"  ATC     : {sorted(sub['atc'].unique())}")
        print(f"  Grupp   : {sorted(sub['grupp'].unique())}")
        print(f"  Analyses: {sorted(sub['analysis'].unique())}")
        print(f"  Date range: {sub['date'].min()} → {sub['date'].max()}")
        print(f"  n stats: min={sub['n'].min()}, max={sub['n'].max()}, mean={sub['n'].mean():.2f}")
        print(f"  Sample rows:")
        print(sub.head(10).to_string())

# Compare magnitude: '99' vs Sweden vs single sjukvårdsregion
print("\n--- Aggregate per region (tab12a, raw counts only) ---")
mask = tab12a["analysis"] == "Incidens rullande 3 månader"
agg = (tab12a[mask].groupby("region")["n"].agg(["sum", "mean", "count"])
       .sort_values("sum", ascending=False))
print(agg.to_string())


# ----------------------------------------------------------------------------
banner("Q2.  `grupp` mapping — full unique values + ATC × grupp cross-tab")
print(f"\nAll unique grupp (tab12a): {sorted(tab12a['grupp'].unique())}")
print(f"All unique grupp (tab12b): {sorted(tab12b['grupp'].unique())}")

print("\nATC × grupp cross-tab (tab12a, count of rows):")
print(pd.crosstab(tab12a["atc"], tab12a["grupp"]).to_string())

print("\nDrug × grupp cross-tab (tab12a):")
print(pd.crosstab(tab12a["drug"], tab12a["grupp"]).to_string())

print("\nDrug × ATC cross-tab (tab12a):")
print(pd.crosstab(tab12a["drug"], tab12a["atc"]).to_string())


# ----------------------------------------------------------------------------
banner("Q3.  Ibrance: 'Patients on treatment' vs 'Patients with dispensations'")
ibrance = load("Ibrance", "IncPrevData.RDS")

# Pivot the four analyses for Ibrance×Sweden, look at the same months
swe_ibr = ibrance[(ibrance["region"] == "Sweden") & (ibrance["drug"] == "Ibrance")]
pivot = (swe_ibr.pivot_table(index="date", columns="analysis", values="n", aggfunc="sum")
         .sort_index())
print("\nIbrance × Sweden, last 18 months (head, all four analyses side-by-side):")
print(pivot.tail(18).to_string())

print("\nRatio 'Patients on treatment' / 'Patients with dispensations' over time (Ibrance×Sweden):")
if "Patients on treatment" in pivot and "Patients with dispensations" in pivot:
    r = pivot["Patients on treatment"] / pivot["Patients with dispensations"]
    print(f"  min={r.min():.3f}, mean={r.mean():.3f}, max={r.max():.3f}, median={r.median():.3f}")

# Same for Kisqali (cross-check)
swe_kis = ibrance[(ibrance["region"] == "Sweden") & (ibrance["drug"] == "Kisqali")]
piv_k = (swe_kis.pivot_table(index="date", columns="analysis", values="n", aggfunc="sum")
         .sort_index())
print("\nKisqali × Sweden, last 6 months:")
print(piv_k.tail(6).to_string())


# ----------------------------------------------------------------------------
banner("Q4 + Q5.  Vydura: re-derive prevalens from IPD and compare to region.RDS")
duot = load("Vydura", "data_duot.RDS")
region_pre = load("Vydura", "region.RDS")

# Sergio's "Patients with dispensations" definition: distinct lopnr×drug×edate per
# (edate, drug, region), counted as n.
pwd_region = (duot
              .drop_duplicates(["lopnr", "drug", "edate", "region"])
              .groupby(["edate", "drug", "region"])
              .size().rename("n_pwd_region").reset_index())

# Sergio's "New drug users" definition: row_number()==1 per lopnr (first appearance
# of that lopnr in the data), then count per (edate, drug, region).
ndu_region = (duot
              .sort_values(["lopnr", "edate"])
              .groupby("lopnr").head(1)
              .groupby(["edate", "drug", "region"])
              .size().rename("n_ndu_region").reset_index())

# Sergio's same code with mutate(region = "Sweden"): Sweden-rolled distinct-lopnr.
pwd_sweden = (duot
              .drop_duplicates(["lopnr", "drug", "edate"])
              .groupby(["edate", "drug"])
              .size().rename("n_pwd_sweden").reset_index())

ndu_sweden = (duot
              .sort_values(["lopnr", "edate"])
              .groupby("lopnr").head(1)
              .groupby(["edate", "drug"])
              .size().rename("n_ndu_sweden").reset_index())

# Pre-computed region.RDS values
print("\nregion.RDS schema sample:")
print(region_pre.head(3).to_string())

# Compare Sweden row in region_pre to our derivations
swe_pre = (region_pre[region_pre["region"] == "Sweden"]
           .rename(columns={"month": "edate", "prevalens": "prevalens_pre"})
           [["edate", "drug", "prevalens_pre"]])

cmp_swe = (swe_pre
           .merge(pwd_sweden, on=["edate", "drug"], how="left")
           .merge(ndu_sweden, on=["edate", "drug"], how="left"))
cmp_swe["match_pwd"] = cmp_swe["prevalens_pre"] == cmp_swe["n_pwd_sweden"]
cmp_swe["match_ndu"] = cmp_swe["prevalens_pre"] == cmp_swe["n_ndu_sweden"]

print("\nSweden: region.RDS prevalens vs derived 'Patients with dispensations' / 'New drug users':")
print(f"  Total rows compared: {len(cmp_swe)}")
print(f"  Matches PWD (distinct lopnr×drug×edate): {cmp_swe['match_pwd'].sum()} / {len(cmp_swe)}")
print(f"  Matches NDU (first row per lopnr)     : {cmp_swe['match_ndu'].sum()} / {len(cmp_swe)}")
print("\nFirst 8 Sweden rows side-by-side:")
print(cmp_swe.head(8).to_string())
print("\nLast 5 Sweden rows side-by-side:")
print(cmp_swe.tail(5).to_string())

# Also check the per-region match
nonswe_pre = (region_pre[region_pre["region"] != "Sweden"]
              .rename(columns={"month": "edate", "prevalens": "prevalens_pre"}))
cmp_reg = (nonswe_pre
           .merge(pwd_region.rename(columns={"n_pwd_region": "n_pwd"}),
                  on=["edate", "drug", "region"], how="left")
           .merge(ndu_region.rename(columns={"n_ndu_region": "n_ndu"}),
                  on=["edate", "drug", "region"], how="left"))
cmp_reg["match_pwd"] = cmp_reg["prevalens_pre"] == cmp_reg["n_pwd"]
cmp_reg["match_ndu"] = cmp_reg["prevalens_pre"] == cmp_reg["n_ndu"]
print(f"\nPer-region (21 regions) comparison rows: {len(cmp_reg)}")
print(f"  Matches PWD: {cmp_reg['match_pwd'].sum()} / {len(cmp_reg)}")
print(f"  Matches NDU: {cmp_reg['match_ndu'].sum()} / {len(cmp_reg)}")

# Mismatches
mism = cmp_reg[~cmp_reg["match_pwd"] & ~cmp_reg["match_ndu"]]
print(f"\nMismatch rows (neither matches): {len(mism)}")
if len(mism):
    print(mism.head(10).to_string())


# ----------------------------------------------------------------------------
banner("Q5 specific: Vydura — sum of 21 regions vs Sweden row in region.RDS")
# Sweden total = sum of region rows? OR distinct-lopnr-Sweden (which would be
# strictly ≤ sum because patients can move regions)?
sum_per_month = (region_pre[region_pre["region"] != "Sweden"]
                 .groupby(["month", "drug"])["prevalens"].sum()
                 .rename("sum_21regions").reset_index())
sweden_pre = (region_pre[region_pre["region"] == "Sweden"]
              .rename(columns={"prevalens": "prevalens_sweden"})
              [["month", "drug", "prevalens_sweden"]])
cmp = sum_per_month.merge(sweden_pre, on=["month", "drug"], how="outer")
cmp["delta"] = cmp["prevalens_sweden"] - cmp["sum_21regions"]
print("\nFirst 12 months, side-by-side:")
print(cmp.head(12).to_string())
print(f"\nDelta stats (Sweden - sum_of_21_regions):")
print(f"  exactly equal     : {(cmp['delta'] == 0).sum()} / {len(cmp)}")
print(f"  Sweden < sum      : {(cmp['delta'] < 0).sum()} / {len(cmp)}")
print(f"  Sweden > sum      : {(cmp['delta'] > 0).sum()} / {len(cmp)}")
print(f"  delta describe   :\n{cmp['delta'].describe()}")


# ----------------------------------------------------------------------------
banner("BONUS: pyreadr metadata — does R store any attributes/labels we missed?")
# pyreadr exposes column-level attributes only sometimes; print what's there.
for folder, fname in [("Ibrance", "IncPrevData.RDS"),
                      ("Ibrance", "IncPrevDataYear.RDS"),
                      ("Vydura", "data_duot.RDS"),
                      ("Vydura", "region.RDS"),
                      ("Vyndaquel", "tab12a.RDS"),
                      ("Vyndaquel", "tab12b.RDS")]:
    result = pyreadr.read_r(str(ROOT / folder / fname))
    print(f"\n{folder}/{fname}: keys={list(result.keys())}")
    for k, df in result.items():
        # pyreadr stores column metadata in df.attrs sometimes
        if hasattr(df, "attrs") and df.attrs:
            print(f"  attrs: {df.attrs}")
        # Check column-level metadata
        for col in df.columns:
            if hasattr(df[col], "attrs") and df[col].attrs:
                print(f"  col[{col}].attrs: {df[col].attrs}")
        # Pandas Categorical → check categories order (might encode labels)
        for col in df.columns:
            if pd.api.types.is_categorical_dtype(df[col]):
                cats = df[col].cat.categories.tolist()
                print(f"  col[{col}] is Categorical with {len(cats)} cats: {cats[:10]}{'...' if len(cats)>10 else ''}")
