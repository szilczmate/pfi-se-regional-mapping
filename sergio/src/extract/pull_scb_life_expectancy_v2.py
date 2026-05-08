# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB life expectancy by region (correct table: Medellivsl)."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101I/Medellivsl"
meta = requests.get(URL, timeout=30).json()
print("Variables in Medellivsl:")
for v in meta.get("variables", []):
    print(f"  {v['code']:<15} {len(v.get('values', []))} values")
    if v["code"] == "Tid":
        print(f"    period samples: {v['values'][-3:]}")

contents = next(v for v in meta["variables"] if v["code"] == "ContentsCode")
years = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
latest_period = years[-1]

query = {
    "query": [
        {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
        {"code": "Kon", "selection": {"filter": "item", "values": ["1","2"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": contents["values"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [latest_period]}}
    ],
    "response": {"format": "json-stat2"}
}
r = requests.post(URL, json=query, timeout=60)
print(f"\nStatus: {r.status_code}")
data = r.json()

dims = data["dimension"]; dim_order = data["id"]; sizes = data["size"]; values = data["value"]
def get_cats(dn):
    cat = dims[dn]["category"]; idx = cat["index"]; lbl = cat.get("label", {})
    codes_in_order = [None] * len(idx)
    for code, pos in idx.items(): codes_in_order[pos] = code
    return codes_in_order, [lbl.get(c, c) for c in codes_in_order]
cat_data = {d: get_cats(d) for d in dim_order}
strides = [1] * len(sizes)
for i in range(len(sizes)-2, -1, -1): strides[i] = strides[i+1] * sizes[i+1]

from collections import defaultdict
pivot = defaultdict(dict)
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords = []; rem = flat_idx
    for s in strides: coords.append(rem // s); rem = rem % s
    rec = {dn: cat_data[dn][0][coords[di]] for di, dn in enumerate(dim_order)}
    region_code = rec["Region"]; region_name = cat_data["Region"][1][cat_data["Region"][0].index(region_code)]
    sex = "men" if rec["Kon"] == "1" else "women"
    pivot[(region_code, region_name)][f"life_expectancy_{sex}"] = val

with open(OUT_INT / "scb_life_expectancy_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code","region","period","life_expectancy_men","life_expectancy_women","life_expectancy_avg","life_expectancy_diff"])
    for (code, name), vals in sorted(pivot.items()):
        m = vals.get("life_expectancy_men", 0); wm = vals.get("life_expectancy_women", 0)
        avg = (m + wm) / 2 if m and wm else 0
        w.writerow([code, name, latest_period, m, wm, round(avg,2), round(wm-m,2)])

print(f"\nLife expectancy at birth ({latest_period}, regional 5-year average):")
print(f"  {'Region':<32} {'Men':>6} {'Women':>7} {'Avg':>6}")
for (code, name), vals in sorted(pivot.items(), key=lambda x: -((x[1].get("life_expectancy_men",0) + x[1].get("life_expectancy_women",0))/2)):
    m = vals.get("life_expectancy_men", 0); wm = vals.get("life_expectancy_women", 0)
    avg = (m + wm) / 2
    print(f"  {name:<32} {m:>6.2f} {wm:>7.2f} {avg:>6.2f}")

print(f"\nSaved: {OUT_INT / 'scb_life_expectancy_by_region.csv'}")
