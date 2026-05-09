# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Search Kolada for additional indicators relevant to Pfizer regional mapping.
Focus: vaccine coverage, primary care access, oncology access, prescribing patterns,
elderly care quality. Save shortlist of candidates for review."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests
import csv
from pathlib import Path

OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

# Pull full KPI list
print("Fetching Kolada KPI list (5000+ indicators)...")
kpis = requests.get("https://api.kolada.se/v3/kpi", timeout=60).json().get("values", [])
print(f"Total KPIs: {len(kpis)}")

# Categories to search for
SEARCH_TERMS = {
    "vaccine_coverage": ["vaccin"],
    "elderly_care": ["aldreomsorg", "äldre", "demens"],
    "primary_care_access": ["vardcentral", "vårdcentral", "tillganglig", "tillgänglig"],
    "wait_times": ["väntetid", "vantetid", "väntan"],
    "oncology": ["cancer", "onkolog"],
    "respiratory": ["kol ", "astma", "luftvags"],
    "cardiovascular": ["hjart", "hjärt", "kardio"],
    "rare_disease_general": ["sallsynt", "sällsynt"],
    "rx_prescribing_patterns": ["förskrivning", "forskrivning", "rekvisition"],
    "infectious_disease": ["smittsam", "infektion", "antibiotik"],
}

# Filter to region-level indicators (filtered later) — for now collect by keyword
results = {}
for cat, terms in SEARCH_TERMS.items():
    matched = []
    for k in kpis:
        title_lc = k["title"].lower()
        if any(t in title_lc for t in terms):
            matched.append(k)
    results[cat] = matched
    print(f"\n{cat}: {len(matched)} matches (showing top 10):")
    for k in matched[:10]:
        # Show only those marked as relevant for L (region)
        op_areas = k.get("operating_area") or k.get("operating_area_2") or "?"
        print(f"  {k['id']:<10} {k['title'][:90]}")

# Save shortlist
all_matched = []
for cat, ks in results.items():
    for k in ks:
        all_matched.append({
            "category": cat,
            "kpi_id": k["id"],
            "title": k["title"],
            "operating_area": k.get("operating_area", ""),
            "perspective": k.get("perspective", ""),
        })

with open(OUT_INT / "kolada_kpi_shortlist.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["category","kpi_id","title","operating_area","perspective"])
    w.writeheader()
    w.writerows(all_matched)
print(f"\nSaved shortlist: {OUT_INT / 'kolada_kpi_shortlist.csv'}")
print(f"Total candidate KPIs: {len(all_matched)}")

# Now test each candidate KPI for region-level data availability (year 2023, fast)
print("\nTesting top 5 per category for actual region-level data availability for 2024 or 2023...")
REGION_CODES = ["0001","0003","0004","0005","0006","0007","0008","0009","0010",
                "0012","0013","0014","0017","0018","0019","0020","0021","0022",
                "0023","0024","0025"]

def test_kpi(kpi_id):
    for yr in [2024, 2023, 2022]:
        try:
            r = requests.get(f"https://api.kolada.se/v3/data/kpi/{kpi_id}/year/{yr}", timeout=20).json()
            n_regions = sum(1 for v in r.get("values", []) if v.get("municipality") in REGION_CODES)
            if n_regions >= 18:
                return (yr, n_regions)
        except Exception:
            continue
    return (None, 0)

verified = []
seen = set()
for cat, ks in results.items():
    for k in ks[:5]:
        if k["id"] in seen: continue
        seen.add(k["id"])
        yr, n = test_kpi(k["id"])
        if yr:
            verified.append((cat, k["id"], k["title"][:80], yr, n))

print("\nVerified region-level KPIs (>=18/21 regions, latest year):")
print(f"  {'Category':<25} {'KPI':<10} {'Year':<6} {'N':<4} {'Title':<80}")
for cat, kpi, title, yr, n in verified:
    print(f"  {cat:<25} {kpi:<10} {yr:<6} {n:<4} {title}")

with open(OUT_INT / "kolada_kpi_verified_extras.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category","kpi_id","title","year","regions_with_data"])
    for row in verified:
        w.writerow(row)
print(f"\nSaved verified: {OUT_INT / 'kolada_kpi_verified_extras.csv'}")
