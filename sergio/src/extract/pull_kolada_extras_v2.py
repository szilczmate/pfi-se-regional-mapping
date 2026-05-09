# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull additional Kolada KPIs: specialist density, cancer screening, lifestyle, primary care quality."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

REGION_CODES = ["0001","0003","0004","0005","0006","0007","0008","0009","0010",
                "0012","0013","0014","0017","0018","0019","0020","0021","0022",
                "0023","0024","0025"]

# First, search for relevant indicator candidates
print("Searching Kolada for additional relevant KPIs...")
kpis = requests.get("https://api.kolada.se/v3/kpi", timeout=60).json().get("values", [])
print(f"Total KPIs: {len(kpis)}")

# Categories to add
SEARCH_TERMS = {
    "specialist_density":  ["specialist", "läkare per", "lakare per"],
    "cancer_screening":    ["mammografi", "screening", "screen"],
    "lifestyle_smoking":   ["röker", "tobak", "snusar"],
    "lifestyle_obesity":   ["fetma", "övervikt", "BMI"],
    "lifestyle_alcohol":   ["alkohol"],
    "primary_care_qual":   ["fast läkarkontakt", "kontinuitet", "vårdcentral"],
    "elderly_falls":       ["fallolyckor", "fallskador"],
    "covid_vacc":          ["covid", "covid-19"],
    "rehabilitation":      ["rehab"],
    "operations_volume":   ["operation", "ingrepp"],
}

candidates = {}
for cat, terms in SEARCH_TERMS.items():
    matched = []
    for k in kpis:
        title_lc = k["title"].lower()
        if any(t in title_lc for t in terms):
            matched.append(k)
    candidates[cat] = matched

# Test a sample for each category — find ones with >=18 region coverage
print("\nVerifying region-level coverage for top candidates...")
def test_kpi(kpi_id):
    for yr in [2024, 2023, 2022]:
        try:
            r = requests.get(f"https://api.kolada.se/v3/data/kpi/{kpi_id}/year/{yr}", timeout=20).json()
            n = sum(1 for v in r.get("values", []) if v.get("municipality") in REGION_CODES)
            if n >= 18:
                return (yr, n)
        except: continue
    return (None, 0)

verified = []
seen = set()
for cat, ks in candidates.items():
    for k in ks[:8]:  # test top 8 per category
        if k["id"] in seen: continue
        seen.add(k["id"])
        yr, n = test_kpi(k["id"])
        if yr:
            verified.append((cat, k["id"], k["title"][:90], yr, n))

print(f"\nVerified region-level KPIs: {len(verified)}")
print(f"  {'Category':<22} {'KPI':<10} {'Year':<6} {'N':<4} {'Title':<90}")
for cat, kpi, title, yr, n in verified[:40]:
    print(f"  {cat:<22} {kpi:<10} {yr:<6} {n:<4} {title}")

with open(OUT_INT / "kolada_extras_v2_candidates.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category","kpi","title","year","regions_with_data"])
    for row in verified: w.writerow(row)
print(f"\nSaved candidate list: {OUT_INT / 'kolada_extras_v2_candidates.csv'}")
