# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB foreign-born population per region 2024 (v2 — fixed variable names).

Fix notes (2026-04-24):
- Prior v1 used wrong variable names (InrUtrFodd / Alder=tot). Real API exposes:
  Fodelseregion (09=fodd i Sverige, 11=utrikes fodd) and Alder (individual years 0..100+).
- Query all ages per region and sum. Output per region: inrikes, utrikes, total, %-utrikes.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, csv
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
OUT_RAW.mkdir(parents=True, exist_ok=True)
OUT_INT.mkdir(parents=True, exist_ok=True)

REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]
REGION_NAMES = {
    "01":"Stockholm","03":"Uppsala","04":"Sörmland","05":"Östergötland","06":"Jönköping",
    "07":"Kronoberg","08":"Kalmar","09":"Gotland","10":"Blekinge","12":"Skåne",
    "13":"Halland","14":"Västra Götaland","17":"Värmland","18":"Örebro","19":"Västmanland",
    "20":"Dalarna","21":"Gävleborg","22":"Västernorrland","23":"Jämtland Härjedalen",
    "24":"Västerbotten","25":"Norrbotten"
}

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101E/InrUtrFoddaRegAlKon"
meta = requests.get(URL, timeout=30).json()
alder_values = [v["code"] for v in meta["variables"] if v["code"]=="Alder"][0] if False else \
    next(v["values"] for v in meta["variables"] if v["code"]=="Alder")

print(f"Alder: {len(alder_values)} values, Fodelseregion: 2 values")

query = {
    "query": [
        {"code":"Region","selection":{"filter":"item","values":REGIONS}},
        {"code":"Alder","selection":{"filter":"item","values":alder_values}},
        {"code":"Kon","selection":{"filter":"item","values":["1","2"]}},
        {"code":"Fodelseregion","selection":{"filter":"item","values":["09","11"]}},
        {"code":"ContentsCode","selection":{"filter":"item","values":["000001NS"]}},
        {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
    ],
    "response":{"format":"json-stat2"}
}
r = requests.post(URL, json=query, timeout=120)
print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500]); sys.exit(1)

data = r.json()
# Save raw
import json as _j
(OUT_RAW/"scb_inr_utr_fodda_2024.json").write_text(_j.dumps(data, ensure_ascii=False), encoding="utf-8")

dims = data["dimension"]; dim_order = data["id"]; sizes = data["size"]; values = data["value"]

def get_cats(dn):
    cat = dims[dn]["category"]; idx = cat["index"]
    codes = [None]*len(idx)
    for code, pos in idx.items(): codes[pos]=code
    return codes
cats = {d: get_cats(d) for d in dim_order}
strides = [1]*len(sizes)
for i in range(len(sizes)-2,-1,-1): strides[i]=strides[i+1]*sizes[i+1]

# Aggregate by (region, fodelseregion)
agg = defaultdict(int)
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords=[]; rem=flat_idx
    for s in strides:
        coords.append(rem//s); rem%=s
    rec = {dn: cats[dn][coords[di]] for di, dn in enumerate(dim_order)}
    agg[(rec["Region"], rec["Fodelseregion"])] += int(val)

rows = []
for code in REGIONS:
    inr = agg.get((code,"09"), 0)
    utr = agg.get((code,"11"), 0)
    total = inr + utr
    pct = (utr/total*100) if total else 0
    rows.append({"region_code":code, "region":REGION_NAMES[code],
                 "inrikes_fodda":inr, "utrikes_fodda":utr, "totalt":total,
                 "andel_utrikes_fodda_pct": round(pct,2)})

with open(OUT_INT/"scb_inr_utr_fodda_by_region_2024.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for row in rows: w.writerow(row)

print("\nForeign-born share by region 2024:")
print(f"  {'Region':<25} {'Inrikes':>12} {'Utrikes':>12} {'%utrikes':>10}")
for row in sorted(rows, key=lambda x: -x["andel_utrikes_fodda_pct"]):
    print(f"  {row['region']:<25} {row['inrikes_fodda']:>12,} {row['utrikes_fodda']:>12,} {row['andel_utrikes_fodda_pct']:>9.1f}%")

print(f"\nSaved: {OUT_INT/'scb_inr_utr_fodda_by_region_2024.csv'}")
