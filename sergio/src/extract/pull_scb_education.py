# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB educational attainment (UF0506/Utbildning) per region 2024.

Metric of interest: share of population 25-64 with eftergymnasial (post-secondary) education,
which is a standard SES correlate (health outcomes, healthcare uptake, vaccine hesitancy).

Uses UF0506A1 (Antal) aggregated over ages 25-64, all kön, by region × utbildningsnivå.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, csv, json
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]
REGION_NAMES = {"01":"Stockholm","03":"Uppsala","04":"Sörmland","05":"Östergötland","06":"Jönköping",
    "07":"Kronoberg","08":"Kalmar","09":"Gotland","10":"Blekinge","12":"Skåne","13":"Halland",
    "14":"Västra Götaland","17":"Värmland","18":"Örebro","19":"Västmanland","20":"Dalarna",
    "21":"Gävleborg","22":"Västernorrland","23":"Jämtland Härjedalen","24":"Västerbotten","25":"Norrbotten"}
# Utbildningsniva: 1,2,3,4=pre/secondary; 5,6=post-secondary; 7=doctoral; US=unknown
POSTSEC = {"5","6","7"}  # eftergymnasial

URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/UF/UF0506/UF0506B/Utbildning"
# Query ages 25-64 (all codes in '25'..'64' map by string), both sex, all education levels, 2024
ages = [str(a) for a in range(25, 65)]
query = {
    "query": [
        {"code":"Region","selection":{"filter":"item","values":REGIONS}},
        {"code":"Alder","selection":{"filter":"item","values":ages}},
        {"code":"UtbildningsNiva","selection":{"filter":"item","values":["1","2","3","4","5","6","7","US"]}},
        {"code":"Kon","selection":{"filter":"item","values":["1","2"]}},
        {"code":"ContentsCode","selection":{"filter":"item","values":["UF0506A1"]}},
        {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
    ],
    "response":{"format":"json-stat2"}
}
r = requests.post(URL, json=query, timeout=120)
print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500]); sys.exit(1)

data = r.json()
(OUT_RAW/"scb_education_25_64_2024.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

dims = data["dimension"]; dim_order = data["id"]; sizes = data["size"]; values = data["value"]
def get_cats(dn):
    cat = dims[dn]["category"]; idx = cat["index"]
    codes = [None]*len(idx)
    for code, pos in idx.items(): codes[pos]=code
    return codes
cats = {d: get_cats(d) for d in dim_order}
strides = [1]*len(sizes)
for i in range(len(sizes)-2,-1,-1): strides[i]=strides[i+1]*sizes[i+1]

agg = defaultdict(lambda: defaultdict(int))  # region → level_group → count
for flat_idx, val in enumerate(values):
    if val is None: continue
    coords=[]; rem=flat_idx
    for s in strides:
        coords.append(rem//s); rem%=s
    rec = {dn: cats[dn][coords[di]] for di, dn in enumerate(dim_order)}
    region = rec["Region"]; lvl = rec["UtbildningsNiva"]
    group = "postsec" if lvl in POSTSEC else ("unknown" if lvl=="US" else "presec")
    agg[region][group] += int(val)

rows = []
for code in REGIONS:
    d = agg[code]
    pre = d["presec"]; post = d["postsec"]; unk = d["unknown"]
    total = pre + post + unk
    pct_post = (post / (pre+post) * 100) if (pre+post) else 0  # exclude unknown from denominator
    rows.append({"region_code":code, "region":REGION_NAMES[code],
                 "pre_gymn_gymn":pre, "eftergymnasial":post, "uppgift_saknas":unk,
                 "totalt_25_64":total, "andel_eftergymn_pct": round(pct_post,2)})

with open(OUT_INT/"scb_education_by_region_2024.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for row in rows: w.writerow(row)

print("\nShare with post-secondary (eftergymnasial) education, 25-64 år, 2024:")
for row in sorted(rows, key=lambda x: -x["andel_eftergymn_pct"]):
    print(f"  {row['region']:<25} {row['andel_eftergymn_pct']:>6.1f}%  "
          f"(post: {row['eftergymnasial']:>8,} / total25-64: {row['totalt_25_64']:>9,})")

print(f"\nSaved: {OUT_INT/'scb_education_by_region_2024.csv'}")
