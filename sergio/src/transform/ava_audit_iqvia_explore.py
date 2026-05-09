# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Explore the structure of RD-IM IQVIA detail to understand what migraine
and ATTR products are present, so the cross-validation can be built correctly."""
from pathlib import Path
import sys
import openpyxl
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 220)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v29.xlsx"

wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
ws = wb["RD-IM IQVIA detail"]
data = list(ws.values)
hdr = data[0]
df = pd.DataFrame(data[1:], columns=hdr)
wb.close()

print(f"Shape: {df.shape}")
print(f"Columns (first 12): {list(df.columns)[:12]}")
print(f"Columns (last 8): {list(df.columns)[-8:]}")

print("\nUnique therapy areas:")
print(df["Therapy area"].value_counts().to_string())

print("\nUnique products in Migraine area:")
mig = df[df["Therapy area"] == "Migraine"]
print(mig["Product"].value_counts().to_string())

print("\nUnique ATCs in Migraine area:")
print(mig["ATC"].value_counts().to_string())

print("\nUnique manufacturers in Migraine area:")
print(mig["Manufacturer"].value_counts().to_string())

print("\nUnique products in ATTR area:")
attr = df[df["Therapy area"] == "ATTR"]
if len(attr):
    print(attr["Product"].value_counts().to_string())
    print("\nATTR ATCs:")
    print(attr["ATC"].value_counts().to_string())
else:
    print("(no rows with Therapy area == 'ATTR' — check exact label)")
    print(f"\nAll therapy areas with 'attr' or 'transthy' or 'amyloid' in name:")
    for ta in df["Therapy area"].dropna().unique():
        if any(s in str(ta).lower() for s in ["attr", "amyloid", "transthy"]):
            print(f"  {ta}")

# Look for time-series columns
date_cols = [c for c in df.columns if "2025" in str(c) or "2026" in str(c)]
print(f"\nDate columns ({len(date_cols)}): {date_cols[:6]} ... {date_cols[-4:]}")

# Sample Vydura row
print("\n--- Sample Vydura row (Sweden) ---")
vyd = mig[(mig["Product"] == "VYDURA") & (mig["Region"].astype(str).str.contains("Sweden|Stockholm", case=False))]
if len(vyd):
    sample = vyd.iloc[0]
    print(f"  Product: {sample['Product']}")
    print(f"  Region:  {sample['Region']}")
    print(f"  ATC:     {sample['ATC']}")
    print(f"  Mfr:     {sample['Manufacturer']}")
    print(f"  Total Sell-In SEK: {sample['Total Sell-In SEK']}")
    print(f"  Total Units:       {sample['Total Units']}")
else:
    # Search more flexibly
    vyd_any = df[df["Product"].astype(str).str.contains("VYDURA", case=False, na=False)]
    print(f"  Total VYDURA rows: {len(vyd_any)}")
    if len(vyd_any):
        print(f"  Therapy areas containing VYDURA: {sorted(vyd_any['Therapy area'].unique())}")
        print(vyd_any[["Therapy area", "Region", "Product", "ATC", "Total Sell-In SEK"]].head(5).to_string())

# Atogepant
print("\n--- AQUIPTA / Atogepant rows ---")
ato = mig[mig["Product"].astype(str).str.contains("ATOGEP|AQUIPTA", case=False, na=False)]
if len(ato):
    print(f"  Found {len(ato)} rows")
    print(ato[["Region", "Product", "ATC", "Total Sell-In SEK", "Total Units"]].head(5).to_string())
else:
    ato_any = df[df["Product"].astype(str).str.contains("ATOGEP|AQUIPTA", case=False, na=False)]
    print(f"  Searched all therapy areas: {len(ato_any)} rows")
    if len(ato_any):
        print(ato_any[["Therapy area", "Region", "Product", "ATC", "Total Sell-In SEK"]].head(5).to_string())
