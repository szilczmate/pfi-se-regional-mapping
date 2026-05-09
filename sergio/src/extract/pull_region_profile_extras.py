# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull more region profile data: Kolada vårdval, screening, more workforce, patient satisfaction.
Plus SCB education levels + foreign-born per region."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
REGION_CODES = ["0001","0003","0004","0005","0006","0007","0008","0009","0010","0012","0013","0014","0017","0018","0019","0020","0021","0022","0023","0024","0025"]

# Search Kolada for more KPIs
print("=== Searching Kolada for additional profile KPIs ===")
kpis = requests.get("https://api.kolada.se/v3/kpi", timeout=60).json().get("values", [])

SEARCH_TERMS = {
    "privatisation": ["privat utförare", "privata", "köp av"],
    "cancer_screening_detail": ["cervixcancer", "tjocktarm", "screen"],
    "patient_satisfaction": ["förtroende", "patienterfarenhet", "nöjdhet", "NPE"],
    "workforce_detail": ["sjuksköterskor", "specialistsjuksköterskor", "undersköterskor"],
    "diabetes_cardio_care": ["diabetes", "blodtryck", "stroke"],
    "primary_care_continuity": ["fast läkarkontakt", "kontinuitet"],
    "palliative": ["palliativ"],
    "vaccine_adult": ["influensavaccin", "pneumokock"],
}
candidates = {}
for cat, terms in SEARCH_TERMS.items():
    matched = []
    for k in kpis:
        t = k["title"].lower()
        if any(term in t for term in terms):
            matched.append(k)
    candidates[cat] = matched[:10]

# Verify top candidates
print("\nVerifying coverage for promising candidates...")
def test_kpi(kpi_id):
    for yr in [2024, 2023]:
        try:
            r = requests.get(f"https://api.kolada.se/v3/data/kpi/{kpi_id}/year/{yr}", timeout=15).json()
            n = sum(1 for v in r.get("values", []) if v.get("municipality") in REGION_CODES)
            if n >= 18:
                return (yr, n)
        except: continue
    return (None, 0)

TARGET_KPIS = {}
tested = set()
for cat, ks in candidates.items():
    print(f"\n  {cat}:")
    for k in ks[:5]:
        if k["id"] in tested: continue
        tested.add(k["id"])
        yr, n = test_kpi(k["id"])
        if yr:
            TARGET_KPIS[k["id"]] = (k["title"][:80], cat)
            print(f"    ✓ {k['id']:<10} {yr} {n}/21  {k['title'][:70]}")

# Pull data for confirmed KPIs
print(f"\n=== Pulling data for {len(TARGET_KPIS)} verified KPIs ===")
muni = requests.get("https://api.kolada.se/v3/municipality", timeout=60).json()
region_names = {x['id']: x['title'] for x in muni['values'] if x['type'] == 'L'}

all_rows = []
for kpi_id, (title, cat) in TARGET_KPIS.items():
    for yr in [2024, 2023]:
        r = requests.get(f"https://api.kolada.se/v3/data/kpi/{kpi_id}/year/{yr}", timeout=30).json()
        for entry in r.get("values", []):
            muni_id = entry.get("municipality")
            if muni_id not in REGION_CODES: continue
            for v in entry.get("values", []):
                if v.get("gender") == "T":
                    all_rows.append({
                        "category": cat, "kpi": kpi_id, "title": title,
                        "region_code": muni_id, "region": region_names.get(muni_id, "?"),
                        "year": yr, "value": v.get("value"),
                    })

with open(OUT_INT / "kolada_profile_extras.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["category","kpi","title","region_code","region","year","value"])
    w.writeheader(); w.writerows(all_rows)

latest = {}
for row in all_rows:
    if row["value"] is None: continue
    key = (row["kpi"], row["region_code"])
    if key not in latest or row["year"] > latest[key]["year"]:
        latest[key] = row
with open(OUT_INT / "kolada_profile_extras_latest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["category","kpi","title","region_code","region","year","value"])
    w.writeheader()
    for row in sorted(latest.values(), key=lambda x: (x["category"], x["kpi"], x["region_code"])):
        w.writerow(row)
print(f"Total rows: {len(all_rows)}; latest: {len(latest)}")
print(f"Saved: {OUT_INT / 'kolada_profile_extras_latest.csv'}")

# Summary
print("\nKPI verifications by category:")
for kpi, (title, cat) in TARGET_KPIS.items():
    yrs = sorted({r["year"] for r in all_rows if r["kpi"] == kpi and r["value"] is not None})
    if yrs:
        ly = max(yrs)
        vals = [r["value"] for r in all_rows if r["kpi"] == kpi and r["year"] == ly and r["value"] is not None]
        if vals:
            print(f"  {kpi} ({cat[:20]}): {title[:55]} — range {min(vals):.1f}-{max(vals):.1f} ({ly})")
