# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB population projections by region 2030, 2040, 2050."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0401/BE0401A/BefProgRegFakN"
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]

# Inspect metadata
meta = requests.get(URL, timeout=30).json()
print("Variables in BefProgRegFakN:")
for v in meta.get("variables", []):
    print(f"  {v['code']:<15} {len(v.get('values', []))} values")
    if v["code"] == "Tid":
        print(f"    years: {v['values'][0]} - {v['values'][-1]}")
    if v["code"] == "ContentsCode":
        for code, txt in zip(v["values"], v.get("valueTexts", v["values"])):
            print(f"    contents: {code} - {txt}")
    if v["code"] == "InrUtrFodd":
        print(f"    InrUtrFodd values: {v['values']}")
    if v["code"] == "Alder":
        print(f"    Alder samples: {v['values'][:3]} ... {v['values'][-3:]}")

# Pull selected target years and target age groups
contents = next(v for v in meta["variables"] if v["code"] == "ContentsCode")
alder_var = next(v for v in meta["variables"] if v["code"] == "Alder")
inrutr = next((v for v in meta["variables"] if v["code"] == "InrUtrFodd"), None)
target_years = ["2030", "2035", "2040", "2050"]

# Build query
query_parts = [
    {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
    {"code": "Alder", "selection": {"filter": "item", "values": alder_var["values"]}},
    {"code": "Kon", "selection": {"filter": "item", "values": ["1","2"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": contents["values"]}},
    {"code": "Tid", "selection": {"filter": "item", "values": target_years}}
]
if inrutr:
    query_parts.insert(1, {"code": "InrUtrFodd", "selection": {"filter": "item", "values": inrutr["values"]}})

query = {"query": query_parts, "response": {"format": "json-stat2"}}

print(f"\nPosting query for years {target_years}...")
r = requests.post(URL, json=query, timeout=120)
print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500]); sys.exit(1)

data = r.json()
(OUT_RAW / "scb_pop_projection_raw.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# Parse json-stat2
dims = data["dimension"]; dim_order = data["id"]; sizes = data["size"]; values = data["value"]
def get_cats(dim_name):
    d = dims[dim_name]; cat = d["category"]; idx = cat["index"]; lbl = cat.get("label", {})
    codes_in_order = [None] * len(idx)
    for code, pos in idx.items(): codes_in_order[pos] = code
    return codes_in_order, [lbl.get(c, c) for c in codes_in_order]
cat_data = {d: get_cats(d) for d in dim_order}
strides = [1] * len(sizes)
for i in range(len(sizes)-2, -1, -1): strides[i] = strides[i+1] * sizes[i+1]

# Aggregate to per-region per-year per-age-bucket
def age_bucket(age_code):
    if age_code.endswith("+"): a = int(age_code[:-1])
    elif "-" in age_code: a = int(age_code.split("-")[0])
    else:
        try: a = int(age_code)
        except: return None
    return a

agg = defaultdict(lambda: defaultdict(int))  # (code, name, year) -> {bucket: total}
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords = []; rem = flat_idx
    for s in strides: coords.append(rem // s); rem = rem % s
    rec = {dn: cat_data[dn][0][coords[di]] for di, dn in enumerate(dim_order)}
    a = age_bucket(rec["Alder"])
    if a is None: continue
    yr = rec["Tid"]
    region_code = rec["Region"]
    region_name = cat_data["Region"][1][cat_data["Region"][0].index(region_code)]
    key = (region_code, region_name, yr)
    agg[key]["total"] += int(val)
    if a < 1: agg[key]["age_0"] += int(val)
    if a >= 65: agg[key]["age_65plus"] += int(val)
    if a >= 75: agg[key]["age_75plus"] += int(val)
    if a >= 85: agg[key]["age_85plus"] += int(val)

# Save
buckets = ["total", "age_0", "age_65plus", "age_75plus", "age_85plus"]
with open(OUT_INT / "scb_pop_projection_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code", "region", "year"] + buckets)
    for (code, name, yr), bucks in sorted(agg.items()):
        w.writerow([code, name, yr] + [bucks.get(b, 0) for b in buckets])
print(f"\nSaved: {OUT_INT / 'scb_pop_projection_by_region.csv'}")

# Print summary — change 2024 → 2040 for 65+
print(f"\nProjected 65+ population growth 2024 → 2040 by region:")
# Load 2024 baseline
import csv as csvmod
with open(OUT_INT / "scb_population_2024_by_region.csv", encoding="utf-8") as f:
    base = {r["region_code"]: int(r["age_65plus"]) for r in csv.DictReader(f)}

for (code, name, yr), bucks in sorted(agg.items()):
    if yr == "2040":
        pop_2024 = base.get(code, 0)
        pop_2040 = bucks.get("age_65plus", 0)
        if pop_2024:
            pct = (pop_2040 - pop_2024) / pop_2024 * 100
            print(f"  {name:<32} {pop_2024:>8,} → {pop_2040:>8,}  ({pct:+5.1f}%)")
