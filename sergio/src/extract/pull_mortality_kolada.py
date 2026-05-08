# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull regional mortality indicators from Kolada API v3.

SCB HS0301 mortality-by-cause table ends 1996 in the modern API; newer cause-of-death
data lives either in Socialstyrelsen's Dödsorsaksregistret (scraper-required) or Kolada's
curated KPIs. Kolada is already our canonical aggregator for regional KPIs, so use it.

KPIs pulled (latest available year per KPI per region):
  - N01451: Premature mortality 25-64 (age-standardised, all causes) per 100k
  - N02013: Lung cancer mortality 25+ per 100k
  - N61603: Suicide 25+ (5-year rolling mean) per 100k
  - N79190: Healthcare-amenable mortality (Eurostat/OECD, 3-yr mean) per 100k
  - N79191: Health-policy-amenable mortality (Eurostat/OECD) per 100k
  - N72455: Deaths within 28 days of MI (count) — paired with MI cases for case-fatality
  - N72461: Stroke mortality within 3 months per 10k
  - U71438: CV mortality in diabetics per 100k
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, csv, json
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

# Kolada uses 4-digit region IDs (0001=Stockholm, 0003=Uppsala, etc.)
REGIONS = ["0001","0003","0004","0005","0006","0007","0008","0009","0010","0012","0013","0014",
           "0017","0018","0019","0020","0021","0022","0023","0024","0025"]
REGION_NAMES = {"0001":"Stockholm","0003":"Uppsala","0004":"Sörmland","0005":"Östergötland","0006":"Jönköping",
    "0007":"Kronoberg","0008":"Kalmar","0009":"Gotland","0010":"Blekinge","0012":"Skåne","0013":"Halland",
    "0014":"Västra Götaland","0017":"Värmland","0018":"Örebro","0019":"Västmanland","0020":"Dalarna",
    "0021":"Gävleborg","0022":"Västernorrland","0023":"Jämtland Härjedalen","0024":"Västerbotten","0025":"Norrbotten"}

KPIS = {
    "N01451":"Förtida dödsfall 25-64 (åldersstand.) /100k",
    "N02013":"Lungcancer dödlighet 25+ /100k",
    "N61603":"Självmord 25+ (5-års mv) /100k",
    "N79190":"Åtgärdbar dödlighet sjukvård (3-års mv) /100k",
    "N79191":"Åtgärdbar dödlighet hälsopolitik /100k",
    "N72461":"Stroke dödlighet 3 mån /10k",
    "U71438":"Hjärt-kärl dödlighet diabetiker /100k",
}
# Regional municipality codes in Kolada use the 2-digit county code:
# Kolada uses "L" prefix for region level, but the data endpoint takes the code directly.
# Actually Kolada region_code convention is the 2-digit with no prefix for region level entity.
# Format of municipality_id in Kolada: e.g., '0114' for Upplands Väsby; regions are '01', '03' etc.

def pull_kpi(kpi_id, years=(2024,2023,2022,2021)):
    """Pull KPI per region. Try recent years, keep latest non-null per region."""
    out = {}  # region_code -> (year, value)
    for yr in years:
        url = f"https://api.kolada.se/v3/data/kpi/{kpi_id}/year/{yr}"
        try:
            r = requests.get(url, timeout=30).json()
        except Exception as e:
            continue
        for rec in r.get("values", []):
            muni = rec.get("municipality")
            if muni not in REGION_NAMES: continue
            for v in rec.get("values", []):
                if v.get("gender") == "T" and v.get("value") is not None:
                    if muni not in out:  # keep first (most recent year) non-null
                        out[muni] = (yr, float(v["value"]))
    return out

all_data = {}
for kpi_id, label in KPIS.items():
    print(f"Pulling {kpi_id} — {label}")
    vals = pull_kpi(kpi_id)
    all_data[kpi_id] = vals
    if vals:
        samples = sorted(vals.items())[:3]
        print(f"  Got {len(vals)}/21 regions. Samples: {samples}")

# Write CSV: wide format with one row per region
headers = ["region_code","region"]
for kid in KPIS:
    headers += [f"{kid}_year", f"{kid}_value"]

rows = []
for code in REGIONS:
    row = {"region_code":code, "region":REGION_NAMES[code]}
    for kid in KPIS:
        y, v = all_data[kid].get(code, (None, None))
        row[f"{kid}_year"] = y
        row[f"{kid}_value"] = v
    rows.append(row)

csv_path = OUT_INT / "kolada_mortality_by_region.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader()
    for r in rows: w.writerow(r)

# Save raw
(OUT_RAW/"kolada_mortality_by_region.json").write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")

# Summary — rank by premature mortality + amenable mortality
print("\n== Premature mortality 25-64 (N01451), latest year ==")
sorted_rows = sorted(rows, key=lambda r: (r.get("N01451_value") or 0), reverse=True)
for r in sorted_rows:
    v = r["N01451_value"]; y = r["N01451_year"]
    if v is not None:
        print(f"  {r['region']:<25} {v:>6.1f}/100k  ({y})")

print("\n== Healthcare-amenable mortality (N79190, Eurostat), latest year ==")
sorted_rows2 = sorted(rows, key=lambda r: (r.get("N79190_value") or 0), reverse=True)
for r in sorted_rows2:
    v = r["N79190_value"]; y = r["N79190_year"]
    if v is not None:
        print(f"  {r['region']:<25} {v:>6.1f}/100k  ({y})")

print(f"\nSaved: {csv_path}")
