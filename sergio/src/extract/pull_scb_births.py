# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB births by region for Abrysvo maternal indication denominator."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

# SCB Levande födda by mother's region: BE/BE0101/BE0101H/FoddaK
URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101H/FoddaK"

REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14",
           "17","18","19","20","21","22","23","24","25"]

# Inspect metadata
meta = requests.get(URL, timeout=30).json()
print("Variables in FoddaK:")
for v in meta.get("variables", []):
    print(f"  {v['code']:<15} ({v['text'][:50]:<50}) — {len(v.get('values', []))} values")
    if v["code"] == "Tid":
        print(f"    years: {v['values'][0]} to {v['values'][-1]}")
    if v["code"] == "ContentsCode":
        print(f"    contents: {list(zip(v['values'], v.get('valueTexts', v['values'])))}")

# Latest 3 years
years_var = next(v for v in meta["variables"] if v["code"] == "Tid")
latest_years = years_var["values"][-3:]

# Identify ContentsCode values to use - typically "Födda" + maybe others
contents = next(v for v in meta["variables"] if v["code"] == "ContentsCode")

query = {
    "query": [
        {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
        {"code": "Kon", "selection": {"filter": "item", "values": ["1","2"]}} if any(v["code"]=="Kon" for v in meta["variables"]) else None,
        {"code": "ContentsCode", "selection": {"filter": "item", "values": contents["values"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": latest_years}}
    ],
    "response": {"format": "json-stat2"}
}
# Remove None entries
query["query"] = [q for q in query["query"] if q is not None]

r = requests.post(URL, json=query, timeout=120)
print(f"\nQuery status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500])
    sys.exit(1)
data = r.json()
(OUT_RAW / "scb_births_raw.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# Parse json-stat2
dims = data["dimension"]; dim_order = data["id"]; sizes = data["size"]; values = data["value"]

def get_cats(dim_name):
    d = dims[dim_name]; cat = d["category"]; idx = cat["index"]; lbl = cat.get("label", {})
    codes_in_order = [None] * len(idx)
    for code, pos in idx.items():
        codes_in_order[pos] = code
    return codes_in_order, [lbl.get(c, c) for c in codes_in_order]

cat_data = {d: get_cats(d) for d in dim_order}
strides = [1] * len(sizes)
for i in range(len(sizes)-2, -1, -1):
    strides[i] = strides[i+1] * sizes[i+1]

records = []
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords = []; rem = flat_idx
    for s in strides:
        coords.append(rem // s); rem = rem % s
    rec = {}
    for di, dname in enumerate(dim_order):
        codes, labels = cat_data[dname]
        rec[dname + "_code"] = codes[coords[di]]
        rec[dname + "_label"] = labels[coords[di]]
    rec["value"] = val
    records.append(rec)

# Aggregate births per region per year (sum across sex if Kon present)
agg = defaultdict(lambda: defaultdict(int))
for r in records:
    region_key = (r["Region_code"], r["Region_label"])
    year = r["Tid_code"]
    agg[region_key][year] += int(r["value"])

# Compute average annual births (latest 3 yr)
with open(OUT_INT / "scb_births_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    yr_cols = sorted({y for d in agg.values() for y in d})
    w.writerow(["region_code", "region"] + yr_cols + ["avg_3yr"])
    for (code, label), yrs in sorted(agg.items()):
        row_vals = [yrs.get(y, 0) for y in yr_cols]
        avg = sum(row_vals) / len(row_vals) if row_vals else 0
        w.writerow([code, label] + row_vals + [round(avg, 0)])

print(f"\nSaved: {OUT_INT}/scb_births_by_region.csv")
print(f"\nBirths by region (latest year, sorted):")
latest_yr = sorted({y for d in agg.values() for y in d})[-1]
for (code, label), yrs in sorted(agg.items(), key=lambda x: -x[1].get(latest_yr, 0)):
    print(f"  {label[:32]:<32} {yrs.get(latest_yr, 0):>8,} births ({latest_yr})")

national = sum(yrs.get(latest_yr, 0) for yrs in agg.values())
print(f"\nNational total {latest_yr}: {national:,} births")
