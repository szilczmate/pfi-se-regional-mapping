# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB BRP (GRP) per region 2024."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/NR/NR0105/NR0105A/NR0105ENS2010T01A"

# Inspect metadata first
meta = requests.get(URL, timeout=30).json()
print("Variables in NR0105ENS2010T01A:")
for v in meta.get("variables", []):
    print(f"  {v['code']:<15} ({v['text'][:50]:<50}) — {len(v.get('values', []))} values")
    if v["code"] == "Region":
        print(f"    sample regions: {v['values'][:8]}")
    if v["code"] == "Tid":
        print(f"    years: {v['values'][0]} to {v['values'][-1]}")
    if v["code"] == "ContentsCode":
        for code, txt in zip(v["values"], v.get("valueTexts", v["values"])):
            print(f"    contents: {code} - {txt}")

# Identify län-level region codes (we want 21 regions only, not riksområde aggregates)
LANCODES = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]
# Latest year
year = meta["variables"][next(i for i,v in enumerate(meta["variables"]) if v["code"]=="Tid")]["values"][-1]
print(f"\nUsing latest year: {year}")

# Pick relevant ContentsCode: BRP and BRP per inhabitant
contents = next(v for v in meta["variables"] if v["code"]=="ContentsCode")
contents_codes = contents["values"]
contents_texts = contents.get("valueTexts", contents_codes)
# Normally: NR0105AB - BRP (mnkr), NR0105AC - BRP per inv (kr), depending on table version
print("\nContent codes available:", list(zip(contents_codes, contents_texts)))

# Build query: all relevant contents, all 21 län, latest year
query = {
    "query": [
        {"code": "Region", "selection": {"filter": "item", "values": LANCODES}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": contents_codes}},
        {"code": "Tid", "selection": {"filter": "item", "values": [year]}}
    ],
    "response": {"format": "json-stat2"}
}

r = requests.post(URL, json=query, timeout=120)
print(f"\nQuery status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500])
    sys.exit(1)

data = r.json()
(OUT_RAW / f"scb_grp_{year}_raw.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# Parse json-stat2
dims = data["dimension"]
dim_order = data["id"]
sizes = data["size"]
values = data["value"]

def get_cats(dim_name):
    d = dims[dim_name]
    cat = d["category"]
    idx = cat["index"]
    lbl = cat.get("label", {})
    codes_in_order = [None] * len(idx)
    for code, pos in idx.items():
        codes_in_order[pos] = code
    labels_in_order = [lbl.get(c, c) for c in codes_in_order]
    return codes_in_order, labels_in_order

cat_data = {d: get_cats(d) for d in dim_order}
strides = [1] * len(sizes)
for i in range(len(sizes)-2, -1, -1):
    strides[i] = strides[i+1] * sizes[i+1]

records = []
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords = []
    rem = flat_idx
    for s in strides:
        coords.append(rem // s); rem = rem % s
    rec = {}
    for di, dname in enumerate(dim_order):
        codes, labels = cat_data[dname]
        rec[dname + "_code"] = codes[coords[di]]
        rec[dname + "_label"] = labels[coords[di]]
    rec["value"] = val
    records.append(rec)

# Pivot to one row per region with all metrics as columns
from collections import defaultdict
per_region = defaultdict(dict)
for r in records:
    region_key = (r["Region_code"], r["Region_label"])
    metric = r["ContentsCode_label"]
    per_region[region_key][metric] = r["value"]

# Save
all_metrics = sorted({r["ContentsCode_label"] for r in records})
print(f"\nMetrics: {all_metrics}")

with open(OUT_INT / f"scb_grp_{year}_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code", "region", "year"] + all_metrics)
    for (code, label), metrics in sorted(per_region.items(), key=lambda x: x[0][0]):
        row = [code, label, year] + [metrics.get(m, "") for m in all_metrics]
        w.writerow(row)

print(f"Saved: {OUT_INT}/scb_grp_{year}_by_region.csv")
print(f"\nSummary — {year} BRP per region:")
print(f"  {'Region':<32}", " ".join(f"{m[:25]:>26}" for m in all_metrics))
for (code, label), metrics in sorted(per_region.items(), key=lambda x: -float(x[1].get(all_metrics[0], 0))):
    vals = " ".join(f"{metrics.get(m, 0):>26,.0f}" if isinstance(metrics.get(m), (int,float)) else f"{'-':>26}" for m in all_metrics)
    print(f"  {label[:32]:<32}", vals)
