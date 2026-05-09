# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
W2 drill-down: where does Norrland actually over-index? PN per-100k by
sjukvårdsregion, plus the Skellefteå founder variant context.

The v5 thesis "Northern ATTR-CM Cornerstone — Vyndaqel anchor at Norrlands
universitetssjukhus Umeå" implicitly conflates two things:
  - V30M Skellefteå founder variant → ATTR-PN (hereditary polyneuropathy)
  - ATTR-CM (cardiomyopathy, mostly wild-type or non-V30M variants)

Norrland over-indexes on the founder variant historically; the CM picture
is different. Let me check both per-100k.
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"

result = pyreadr.read_r(str(AVA / "Vyndaquel" / "tab12a.RDS"))
df = list(result.values())[0]
df["date"] = pd.to_datetime(df["date"].astype(str))
df = df[df["region"] != "99"].copy()
df["n"] = pd.to_numeric(df["n"], errors="coerce")
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

LAST6_END = wide["date"].max()
LAST6_START = LAST6_END - pd.DateOffset(months=5)

print(f"Last 6mo window: {LAST6_START.date()} → {LAST6_END.date()}\n")

# Helper: per-region prevalens per-100k by drug × grupp (last 6mo mean)
def regional_per100k(drug: str, grupp_label: str, grupp_filter):
    sub = wide[(wide["drug"] == drug) & grupp_filter(wide) &
               (wide["region"] != "Sweden") &
               (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
    if grupp_label == "DG1+DG2":
        # Combine
        sub = sub.groupby(["date", "region", "drug"], as_index=False)[
            ["prevalens_per100k", "prevalens_count", "incidens_per100k", "incidens_count"]].sum()
    out = (sub.groupby("region")
              .agg(prev_per100k=("prevalens_per100k", "mean"),
                   prev_count=("prevalens_count", "mean"),
                   inc_per100k=("incidens_per100k", "mean"),
                   inc_count=("incidens_count", "mean"))
              .reset_index().sort_values("prev_per100k", ascending=False))

    # Sweden reference
    swe_sub = wide[(wide["drug"] == drug) & grupp_filter(wide) &
                   (wide["region"] == "Sweden") &
                   (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
    if grupp_label == "DG1+DG2":
        swe_sub = swe_sub.groupby(["date", "drug"], as_index=False)[
            ["prevalens_per100k", "prevalens_count"]].sum()
    swe_per100k = swe_sub["prevalens_per100k"].mean()
    swe_count = swe_sub["prevalens_count"].mean()
    out["index_vs_sweden"] = out["prev_per100k"] / swe_per100k * 100

    print(f"\n=== {drug} × {grupp_label} per-100k (last 6mo) ===")
    print(out.to_string(index=False, float_format="%.2f"))
    print(f"  Sweden: prev_per100k={swe_per100k:.2f}, prev_count={swe_count:.1f}")
    return out, swe_per100k

# Vyndaqel × ATTR-CM (DG3)
regional_per100k("Vyndaqel", "DG3 (ATTR-CM)",
                  lambda w: w["grupp"] == "Diagnosgrupp 3")

# Vyndaqel × ATTR-PN (DG1+DG2 combined)
regional_per100k("Vyndaqel", "DG1+DG2",
                  lambda w: w["grupp"].isin(["Diagnosgrupp 1", "Diagnosgrupp 2"]))

# Vyndaqel × DG1 alone
regional_per100k("Vyndaqel", "DG1",
                  lambda w: w["grupp"] == "Diagnosgrupp 1")

# Vyndaqel × DG2 alone
regional_per100k("Vyndaqel", "DG2",
                  lambda w: w["grupp"] == "Diagnosgrupp 2")

# Amvuttra × DG1+DG2 — competitive picture in PN
regional_per100k("Amvuttra", "DG1+DG2",
                  lambda w: w["grupp"].isin(["Diagnosgrupp 1", "Diagnosgrupp 2"]))

# All ATTR drugs combined × DG3 (full ATTR-CM market per-100k by region)
print("\n=== ATTR-CM total (all drugs combined) × DG3 per-100k ===")
all_cm = wide[(wide["grupp"] == "Diagnosgrupp 3") &
              (wide["region"] != "Sweden") &
              (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
all_cm_total = (all_cm.groupby(["date", "region"], as_index=False)[
                  ["prevalens_per100k", "prevalens_count"]].sum())
agg_cm = (all_cm_total.groupby("region")
            .agg(prev_per100k=("prevalens_per100k", "mean"),
                 prev_count=("prevalens_count", "mean"))
            .reset_index().sort_values("prev_per100k", ascending=False))
print(agg_cm.to_string(index=False, float_format="%.2f"))

# Same for PN
print("\n=== ATTR-PN total (all drugs combined) × DG1+DG2 per-100k ===")
all_pn = wide[(wide["grupp"].isin(["Diagnosgrupp 1", "Diagnosgrupp 2"])) &
              (wide["region"] != "Sweden") &
              (wide["date"] >= LAST6_START) & (wide["date"] <= LAST6_END)]
all_pn_total = (all_pn.groupby(["date", "region"], as_index=False)[
                  ["prevalens_per100k", "prevalens_count"]].sum())
agg_pn = (all_pn_total.groupby("region")
            .agg(prev_per100k=("prevalens_per100k", "mean"),
                 prev_count=("prevalens_count", "mean"))
            .reset_index().sort_values("prev_per100k", ascending=False))
print(agg_pn.to_string(index=False, float_format="%.2f"))

print("\nDone.")
