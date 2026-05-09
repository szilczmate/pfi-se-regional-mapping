# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Inspect IQVIA vaccines file: products, regions, Unknown rows, totals."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import openpyxl
from pathlib import Path
import csv

src = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/VitiScience_Vaccines_Apr-02-2026.xlsx")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
ws = wb["Sweden Sell-In"]

rows = list(ws.iter_rows(values_only=True))
header = rows[0]
data = rows[1:]
print("Total data rows:", len(data))
print("Total columns:", len(header))

col_idx = {h: i for i, h in enumerate(header)}
ATC_C = col_idx["ATC WHO Level 5"]
PROD_C = col_idx["Product Name Incl PI"]
PI_C = col_idx["PI/Non PI"]
COUNTY_C = col_idx["County Council"]
BRICK_C = col_idx["Brick"]

products = sorted({r[PROD_C] for r in data if r[PROD_C]})
print("\nUnique products (", len(products), "):", sep="")
for p in products: print(" ", p)

atcs = sorted({r[ATC_C] for r in data if r[ATC_C]})
print("\nUnique ATCs (", len(atcs), "):", sep="")
for a in atcs: print(" ", a)

counties = sorted({r[COUNTY_C] for r in data if r[COUNTY_C]})
print("\nUnique counties (", len(counties), "):", sep="")
for c in counties: print(" ", c)

pi_count = sum(1 for r in data if r[PI_C] == "P.I.")
non_pi = sum(1 for r in data if r[PI_C] == "Non P.I.")
print("\nPI rows:", pi_count, " Non-PI rows:", non_pi)

unknown_county = sum(1 for r in data if r[COUNTY_C] and "Unknown" in str(r[COUNTY_C]))
unknown_brick = sum(1 for r in data if r[BRICK_C] and "Unknown" in str(r[BRICK_C]))
print("\nRows with Unknown county:", unknown_county)
print("Rows with Unknown brick:", unknown_brick)

val_cols = [(i, h) for i, h in enumerate(header) if h and h.startswith("Sell In Value")]
unit_cols = [(i, h) for i, h in enumerate(header) if h and h.startswith("Units")]
print("\nValue columns:", len(val_cols), " Unit columns:", len(unit_cols))

totals = {}
for r in data:
    p = r[PROD_C]
    if not p: continue
    if p not in totals: totals[p] = {"value": 0, "units": 0, "rows": 0}
    for ci, _ in val_cols:
        v = r[ci]
        if isinstance(v, (int, float)):
            totals[p]["value"] += v
    for ci, _ in unit_cols:
        u = r[ci]
        if isinstance(u, (int, float)):
            totals[p]["units"] += u
    totals[p]["rows"] += 1

print("\nTotals per product (Apr 2023 - Mar 2026, all geographies):")
print("  {:<28} {:>6} {:>16} {:>20}".format("Product", "Rows", "Total Units", "Total Value SEK"))
for p, t in sorted(totals.items(), key=lambda x: -x[1]["value"]):
    print("  {:<28} {:>6} {:>16,.0f} {:>20,.0f}".format(p, t["rows"], t["units"], t["value"]))

with open(OUT_INT / "iqvia_vaccines_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["product", "atc", "rows", "total_units_apr2023_mar2026", "total_value_sek"])
    for p, t in sorted(totals.items()):
        atc = next((r[ATC_C] for r in data if r[PROD_C] == p and r[ATC_C]), "")
        w.writerow([p, atc, t["rows"], t["units"], t["value"]])
print("\nSaved:", OUT_INT / "iqvia_vaccines_summary.csv")

# Per-county totals (which counties dominate? how big is Unknown?)
print("\nTotal Sell-In Value by county (top 25):")
county_tot = {}
for r in data:
    c = r[COUNTY_C]
    if not c: continue
    s = sum(r[ci] for ci, _ in val_cols if isinstance(r[ci], (int, float)))
    county_tot[c] = county_tot.get(c, 0) + s
for c, v in sorted(county_tot.items(), key=lambda x: -x[1])[:25]:
    print("  {:<35} {:>20,.0f} SEK".format(c, v))
