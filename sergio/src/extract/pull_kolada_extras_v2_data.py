# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull selected high-value Kolada KPIs from v2 candidates: specialist density, breast cancer
screening + surgery wait, lifestyle (smoking, obesity), elderly falls."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

INDICATORS = {
    # Workforce / capacity
    "N70015": ("Regional specialistkompetenta läkare, antal", "workforce"),
    "N70034": ("Regional specialistläkare årsarbetare, antal", "workforce"),
    # Cancer screening + surgery
    "N70605": ("Bröstcancer upptäckt via screening, andel (%)", "oncology_quality"),
    "N70601": ("Bröstcanceroperation inom 28 dagar, andel (%)", "oncology_quality"),
    "N70603": ("Bröstbevarande operation vid små tumörer, andel (%)", "oncology_quality"),
    # Lifestyle (relevant for Pfizer products)
    "U01402": ("Invånare 16-84 som röker dagligen, andel (%)", "lifestyle_smoking"),  # lung cancer (Lorbrena) context
    "U01760": ("Invånare med övervikt eller fetma, andel (%)", "lifestyle_obesity"),  # pipeline obesity context
    # Elderly falls (RSV / Prevenar / fall prevention angle)
    "N20402": ("Fallskador 80+ slutenvård, antal/100k", "elderly_falls"),
    "N20410": ("Fallskador 65-79 vårdtillfällen, antal/100k", "elderly_falls"),
}

REGION_CODES = ["0001","0003","0004","0005","0006","0007","0008","0009","0010",
                "0012","0013","0014","0017","0018","0019","0020","0021","0022",
                "0023","0024","0025"]

muni = requests.get("https://api.kolada.se/v3/municipality", timeout=60).json()
region_names = {x['id']: x['title'] for x in muni['values'] if x['type'] == 'L'}

all_rows = []
YEARS = [2024, 2023, 2022]
for kpi, (title, cat) in INDICATORS.items():
    for yr in YEARS:
        r = requests.get(f"https://api.kolada.se/v3/data/kpi/{kpi}/year/{yr}", timeout=30).json()
        for entry in r.get("values", []):
            muni_id = entry.get("municipality")
            if muni_id not in REGION_CODES: continue
            for v in entry.get("values", []):
                if v.get("gender") == "T":
                    all_rows.append({
                        "category": cat, "kpi": kpi, "title": title,
                        "region_code": muni_id, "region": region_names.get(muni_id, "?"),
                        "year": yr, "value": v.get("value"),
                    })

fields = ["category","kpi","title","region_code","region","year","value"]
with open(OUT_INT / "kolada_extras_v2_data.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(all_rows)

# Latest year per (kpi, region)
latest = {}
for row in all_rows:
    if row["value"] is None: continue
    key = (row["kpi"], row["region_code"])
    if key not in latest or row["year"] > latest[key]["year"]:
        latest[key] = row

with open(OUT_INT / "kolada_extras_v2_latest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in sorted(latest.values(), key=lambda x: (x["kpi"], x["region_code"])):
        w.writerow(r)

print(f"Total rows: {len(all_rows)}")
print(f"\nCoverage per indicator:")
for kpi, (title, cat) in INDICATORS.items():
    yrs = [r["year"] for r in all_rows if r["kpi"] == kpi and r["value"] is not None]
    if yrs:
        ly = max(yrs)
        n = sum(1 for r in all_rows if r["kpi"] == kpi and r["year"] == ly and r["value"] is not None)
        # spread
        vals = [r["value"] for r in all_rows if r["kpi"] == kpi and r["year"] == ly and r["value"] is not None]
        print(f"  {kpi:<8} {ly}  {n}/21  range {min(vals):>7.1f}-{max(vals):>7.1f}  {title[:55]}")

print(f"\nFiles:")
print(f"  {OUT_INT / 'kolada_extras_v2_data.csv'}")
print(f"  {OUT_INT / 'kolada_extras_v2_latest.csv'}")

# Show extreme regions for the most narrative-relevant indicators
print(f"\nSmoking %: top 3 highest, top 3 lowest (latest year)")
smk = sorted([r for r in latest.values() if r["kpi"]=="U01402"], key=lambda x: -(x["value"] or 0))
for r in smk[:3]: print(f"  HIGH  {r['region']:<30} {r['value']:.1f}%  ({r['year']})")
for r in smk[-3:]: print(f"  LOW   {r['region']:<30} {r['value']:.1f}%  ({r['year']})")

print(f"\nFalls 80+ slutenvård: top 3 highest")
fal = sorted([r for r in latest.values() if r["kpi"]=="N20402"], key=lambda x: -(x["value"] or 0))
for r in fal[:3]: print(f"  HIGH  {r['region']:<30} {r['value']:.0f}/100k  ({r['year']})")
for r in fal[-3:]: print(f"  LOW   {r['region']:<30} {r['value']:.0f}/100k  ({r['year']})")
