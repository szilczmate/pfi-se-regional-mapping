# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB population by region/age/sex for 2024 via PxWeb API. Save raw + aggregated."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests
import json
import csv
from pathlib import Path

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkningNy"

# 21 region codes (län-level 2-char)
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14",
           "17","18","19","20","21","22","23","24","25"]

# Get metadata to confirm Alder & Civilstand values
meta = requests.get(URL, timeout=30).json()
alder_var = next(v for v in meta["variables"] if v["code"] == "Alder")
civ_var = next(v for v in meta["variables"] if v["code"] == "Civilstand")
print("Civilstand values:", civ_var["values"])
print("Alder sample (first 5):", alder_var["values"][:5])
print("Alder sample (last 5):", alder_var["values"][-5:])
print("Alder N:", len(alder_var["values"]))

# Build query: all ages, both sexes, all civil states, 2024, 21 regions
query = {
    "query": [
        {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
        {"code": "Civilstand", "selection": {"filter": "item", "values": civ_var["values"]}},
        {"code": "Alder", "selection": {"filter": "item", "values": alder_var["values"]}},
        {"code": "Kon", "selection": {"filter": "item", "values": ["1","2"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BE0101N1"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": ["2024"]}}
    ],
    "response": {"format": "json-stat2"}
}

print("\nPosting query...")
r = requests.post(URL, json=query, timeout=120)
print("Status:", r.status_code)
if r.status_code != 200:
    print("Error body:", r.text[:500])
    sys.exit(1)
data = r.json()

# Save raw
(OUT_RAW / "scb_population_2024_raw.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Saved raw:", OUT_RAW / "scb_population_2024_raw.json")

# json-stat2 parsing
# Dimensions appear in 'dimension' with index orders
dims = data["dimension"]
dim_order = data["id"]  # order of dims in 'value' flat array
sizes = data["size"]
values = data["value"]

print("\nDim order:", dim_order)
print("Sizes:", sizes)

# Get category labels per dim
def get_cats(dim_name):
    d = dims[dim_name]
    cat = d["category"]
    # 'index' maps code -> position; 'label' maps code -> human label
    idx = cat["index"]
    lbl = cat.get("label", {})
    # Sort codes by their index
    codes_in_order = [None] * len(idx)
    for code, pos in idx.items():
        codes_in_order[pos] = code
    labels_in_order = [lbl.get(c, c) for c in codes_in_order]
    return codes_in_order, labels_in_order

cat_data = {d: get_cats(d) for d in dim_order}
for d in dim_order:
    codes, labels = cat_data[d]
    print(f"  {d}: {len(codes)} categories")

# Iterate flat array. Index = sum_i (idx_i * stride_i), where stride_i is product of sizes after i
strides = [1] * len(sizes)
for i in range(len(sizes) - 2, -1, -1):
    strides[i] = strides[i+1] * sizes[i+1]

# Aggregate to per-region rows
import itertools
records = []
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords = []
    rem = flat_idx
    for s in strides:
        coords.append(rem // s)
        rem = rem % s
    rec = {}
    for di, dname in enumerate(dim_order):
        codes, labels = cat_data[dname]
        rec[dname + "_code"] = codes[coords[di]]
        rec[dname + "_label"] = labels[coords[di]]
    rec["value"] = val
    records.append(rec)

print(f"\nTotal non-null records: {len(records)}")

# Save full long-format
fields = list(records[0].keys()) if records else []
with open(OUT_INT / "scb_population_2024_long.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(records)
print("Saved long format:", OUT_INT / "scb_population_2024_long.csv")

# Aggregate: total population per region (sum across age, sex, civilstand)
from collections import defaultdict
total_per_region = defaultdict(int)
for r in records:
    total_per_region[(r["Region_code"], r["Region_label"])] += int(r["value"])

# Aggregate: by key age groups
def age_bucket(age_code):
    """SCB Alder codes are like '0','1',...,'100','100+' or similar. Map to bucket."""
    # SCB ages are typically '0','1',...'99','100+' as strings, sometimes with '-' for ranges
    if age_code.endswith("+"):
        a = int(age_code[:-1])
    elif "-" in age_code:
        a = int(age_code.split("-")[0])
    else:
        try:
            a = int(age_code)
        except ValueError:
            return "unknown"
    return a

bucket_per_region = defaultdict(lambda: defaultdict(int))
for r in records:
    a = age_bucket(r["Alder_code"])
    if a == "unknown": continue
    sex = r["Kon_code"]  # '1' = men, '2' = women
    region_key = (r["Region_code"], r["Region_label"])
    val = int(r["value"])
    bucket_per_region[region_key]["total"] += val
    if a < 1: bucket_per_region[region_key]["age_0"] += val
    if a < 5: bucket_per_region[region_key]["age_0_4"] += val
    if 15 <= a <= 44 and sex == "2": bucket_per_region[region_key]["women_15_44"] += val
    if a >= 50: bucket_per_region[region_key]["age_50plus"] += val
    if a >= 60: bucket_per_region[region_key]["age_60plus"] += val
    if a >= 65: bucket_per_region[region_key]["age_65plus"] += val
    if a >= 75: bucket_per_region[region_key]["age_75plus"] += val

# Write per-region aggregates
buckets = ["total", "age_0", "age_0_4", "women_15_44", "age_50plus", "age_60plus", "age_65plus", "age_75plus"]
with open(OUT_INT / "scb_population_2024_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code", "region"] + buckets)
    for (code, label), bucks in sorted(bucket_per_region.items(), key=lambda x: x[0][0]):
        row = [code, label] + [bucks.get(b, 0) for b in buckets]
        w.writerow(row)

print("Saved per-region aggregates:", OUT_INT / "scb_population_2024_by_region.csv")

# Print summary
print("\n21 regions, 2024 population summary:")
print("  {:<30} {:>12} {:>10} {:>12} {:>12}".format("Region", "Total", "0yo", "65+", "75+"))
for (code, label), bucks in sorted(bucket_per_region.items(), key=lambda x: -x[1]["total"]):
    print("  {:<30} {:>12,} {:>10,} {:>12,} {:>12,}".format(
        label[:30], bucks["total"], bucks["age_0"], bucks["age_65plus"], bucks["age_75plus"]))

print("\nNational totals (sum):")
nat_total = sum(b["total"] for b in bucket_per_region.values())
nat_65 = sum(b["age_65plus"] for b in bucket_per_region.values())
nat_75 = sum(b["age_75plus"] for b in bucket_per_region.values())
print(f"  Total: {nat_total:>12,}  65+: {nat_65:>10,}  75+: {nat_75:>10,}")
