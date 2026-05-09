# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull FHM disease statistics CSVs (TBE, IPD) and parse to clean per-region tables."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests
import csv
from pathlib import Path
from datetime import date

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

today = date.today().strftime("%Y%m%d")

# CSV URLs follow pattern: https://sminet3-prod.sminet.se/mapapp/{disease}_ySWE_ALL_{date}.csv
DISEASES = {
    "tbe": f"https://sminet3-prod.sminet.se/mapapp/tbe_ySWE_ALL_20260430.csv",
    "ipd": f"https://sminet3-prod.sminet.se/mapapp/invasivpneumokockinfektion_ySWE_ALL_20260430.csv",
}

# Try borrelia variations
BORRELIA_TRY = [
    "https://sminet3-prod.sminet.se/mapapp/borrelios_ySWE_ALL_20260430.csv",
    "https://sminet3-prod.sminet.se/mapapp/borrelia_ySWE_ALL_20260430.csv",
    "https://sminet3-prod.sminet.se/mapapp/borreliainfektion_ySWE_ALL_20260430.csv",
]

# Sweden regions canonical list (for matching against FHM region names)
REGION_MAP = {
    "Stockholm": "01", "Uppsala": "03", "Södermanland": "04", "Östergötland": "05",
    "Jönköping": "06", "Kronoberg": "07", "Kalmar": "08", "Gotland": "09",
    "Blekinge": "10", "Skåne": "12", "Halland": "13", "Västra Götaland": "14",
    "Värmland": "17", "Örebro": "18", "Västmanland": "19", "Dalarna": "20",
    "Gävleborg": "21", "Västernorrland": "22", "Jämtland": "23", "Västerbotten": "24",
    "Norrbotten": "25",
    # Variations
    "Stockholms län": "01", "Uppsala län": "03", "Södermanlands län": "04",
    "Östergötlands län": "05", "Jönköpings län": "06", "Kronobergs län": "07",
    "Kalmar län": "08", "Gotlands län": "09", "Blekinge län": "10", "Skåne län": "12",
    "Hallands län": "13", "Västra Götalands län": "14", "Värmlands län": "17",
    "Örebro län": "18", "Västmanlands län": "19", "Dalarnas län": "20",
    "Gävleborgs län": "21", "Västernorrlands län": "22", "Jämtlands län": "23",
    "Västerbottens län": "24", "Norrbottens län": "25",
}

def fetch_and_parse(disease, url):
    print(f"\n=== {disease.upper()} ===")
    r = requests.get(url, timeout=60)
    print(f"  Status: {r.status_code}, Length: {len(r.content)}")
    if r.status_code != 200:
        return None

    raw_path = OUT_RAW / f"fhm_{disease}_raw.csv"
    raw_path.write_bytes(r.content)

    text = r.text
    reader = csv.reader(text.splitlines(), skipinitialspace=True)
    rows = list(reader)
    if not rows:
        print("  Empty CSV")
        return None
    header = [h.strip() for h in rows[0]]
    data_rows = rows[1:]
    print(f"  Header (first 6): {header[:6]}...")
    print(f"  Data rows: {len(data_rows)}")

    # Header pattern: ['Landsting', '1997(tot)', '1997(inc/100.000)', '1998(tot)', ...]
    # Each year has 2 cols: tot and inc
    years = []
    for h in header[1:]:
        h = h.strip().strip('"').strip()
        if "(tot)" in h:
            year = h.split("(")[0].strip()
            try:
                years.append(int(year))
            except: pass
    years = sorted(set(years))
    if not years: return None
    latest_year = max(years)
    print(f"  Years available: {years[0]} - {years[-1]}, latest = {latest_year}")

    # Build records
    records = []
    for row in data_rows:
        if not row or not row[0].strip(): continue
        region_name_raw = row[0].strip().strip('"').strip()
        region_code = REGION_MAP.get(region_name_raw)
        if not region_code:
            # Try alternative match (e.g., 'Riket' for national)
            if region_name_raw.lower() == "riket":
                region_code = "00"
            else:
                # Print unmatched for debugging
                pass
        for i, val in enumerate(row[1:]):
            if i + 1 >= len(header): break
            col_name = header[i+1].strip().strip('"').strip()
            val = val.strip().strip('"').strip()
            if not val or val == "-": continue
            try:
                num = float(val.replace(",", "."))
            except:
                continue
            # Identify year + metric
            year = None; metric = None
            if "(tot)" in col_name:
                year = int(col_name.split("(")[0].strip())
                metric = "cases"
            elif "(inc/100.000)" in col_name or "(inc/100,000)" in col_name:
                year = int(col_name.split("(")[0].strip())
                metric = "incidence_per_100k"
            else:
                continue
            records.append({
                "disease": disease,
                "region_name": region_name_raw,
                "region_code": region_code or "?",
                "year": year,
                "metric": metric,
                "value": num,
            })
    return records, latest_year

all_records = []
results = {}
for disease, url in DISEASES.items():
    res = fetch_and_parse(disease, url)
    if res:
        records, latest = res
        all_records.extend(records)
        results[disease] = (records, latest)

# Try borrelia URLs
for url in BORRELIA_TRY:
    print(f"\nTrying borrelia URL: {url}")
    r = requests.head(url, timeout=15, allow_redirects=True)
    print(f"  HEAD status: {r.status_code}")
    if r.status_code == 200:
        res = fetch_and_parse("borrelia", url)
        if res:
            all_records.extend(res[0])
            results["borrelia"] = res
            break

# Save long-format CSV
if all_records:
    fields = ["disease", "region_name", "region_code", "year", "metric", "value"]
    with open(OUT_INT / "fhm_epi_long.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_records)
    print(f"\nSaved long format: {OUT_INT / 'fhm_epi_long.csv'} ({len(all_records)} rows)")

# Pivot to per-region per-disease for latest year
import collections
latest_table = collections.defaultdict(dict)  # (region_code, region_name) -> {disease_metric: value}
for disease, (records, latest_year) in results.items():
    for r in records:
        if r["year"] == latest_year:
            key = (r["region_code"], r["region_name"])
            latest_table[key][f"{disease}_{r['metric']}_{latest_year}"] = r["value"]

with open(OUT_INT / "fhm_epi_latest_by_region.csv", "w", newline="", encoding="utf-8") as f:
    all_metrics = sorted({k for d in latest_table.values() for k in d})
    w = csv.writer(f)
    w.writerow(["region_code", "region_name"] + all_metrics)
    for (code, name), vals in sorted(latest_table.items(), key=lambda x: x[0][0]):
        w.writerow([code, name] + [vals.get(m, "") for m in all_metrics])

print(f"Saved latest-year wide: {OUT_INT / 'fhm_epi_latest_by_region.csv'}")
print(f"\nLatest year by region (top 5 of each):")
for disease, (records, latest_year) in results.items():
    print(f"\n  {disease.upper()} {latest_year}:")
    region_cases = [(r["region_name"], r["value"]) for r in records
                    if r["year"] == latest_year and r["metric"] == "cases" and r["region_code"] != "?"]
    for name, cases in sorted(region_cases, key=lambda x: -x[1])[:5]:
        print(f"    {name:<25} {cases:>6.0f} cases")
    nat = next((r["value"] for r in records if r["year"] == latest_year and r["metric"] == "cases" and r["region_code"] == "00"), None)
    if nat:
        print(f"    {'(National total)':<25} {nat:>6.0f} cases")
