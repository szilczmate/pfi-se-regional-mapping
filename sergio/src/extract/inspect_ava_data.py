# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Inspect the new AVA (Analysis Visualisation Apps) data delivered 2026-05-02.

Three product folders, each with one or two RDS files:
  Ibrance/    IncPrevData.RDS, IncPrevDataYear.RDS
  Vydura/     data_duot.RDS (IPD), region.RDS
  Vyndaquel/  tab12a.RDS, tab12b.RDS

Goal: surface schema (columns, dtypes, row counts), unique values for likely
filter columns (region, drug, year, analysis), and a head() preview of each
table so we can map them onto the existing master_workbook structure.
"""

from pathlib import Path
import pyreadr
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/AVA data for mapping 2026-05-02")

FILES = [
    ("Ibrance", "IncPrevData.RDS"),
    ("Ibrance", "IncPrevDataYear.RDS"),
    ("Vydura", "data_duot.RDS"),
    ("Vydura", "region.RDS"),
    ("Vyndaquel", "tab12a.RDS"),
    ("Vyndaquel", "tab12b.RDS"),
]

LIKELY_DIMS = {
    "region", "drug", "analysis", "edate", "date", "year", "indikation",
    "indication", "kon", "sex", "agegroup", "age_group", "alder",
    "atc", "produkt", "product",
}


def describe(label: str, df: pd.DataFrame) -> None:
    print("\n" + "=" * 90)
    print(f"FILE: {label}")
    print(f"  shape      : {df.shape[0]:,} rows x {df.shape[1]} cols")
    print(f"  columns    : {list(df.columns)}")
    print(f"  dtypes     :")
    for c in df.columns:
        print(f"    {c:<24} {str(df[c].dtype)}")
    print(f"  null counts:")
    nulls = df.isna().sum()
    for c in df.columns:
        if nulls[c]:
            print(f"    {c:<24} {nulls[c]:,} nulls")

    # Cardinality check for likely dimension columns
    for c in df.columns:
        cl = c.lower()
        if cl in LIKELY_DIMS or any(d in cl for d in LIKELY_DIMS):
            uniq = df[c].dropna().unique()
            print(f"  unique[{c}] ({len(uniq)}): {sorted(map(str, uniq))[:25]}"
                  + ("  ..." if len(uniq) > 25 else ""))

    print("  head(5):")
    print(df.head(5).to_string())
    print("  tail(3):")
    print(df.tail(3).to_string())


def main() -> None:
    for product, fname in FILES:
        path = ROOT / product / fname
        result = pyreadr.read_r(str(path))
        # pyreadr returns OrderedDict {name -> DataFrame}; .RDS files have one
        for key, df in result.items():
            label = f"{product}/{fname}  (R object name: {key or '<unnamed>'})"
            describe(label, df)


if __name__ == "__main__":
    main()
