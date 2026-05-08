# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build penetration analyses: TBE × FSME-IMMUN, IPD × Prevenar.
For each region: where is disease burden HIGH but Pfizer share LOW = opportunity."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
import openpyxl
from collections import defaultdict
from pathlib import Path
from datetime import date

INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
SRC = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT_INT = INT
today = date.today().isoformat()

def load_csv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# Load demographics for normalization
pop = {r["region_code"]: r for r in load_csv(INT / "scb_population_2024_by_region.csv")}

# FHM epi
fhm = defaultdict(dict)
for r in load_csv(INT / "fhm_epi_long.csv"):
    if r["region_code"] in ("?", "00"): continue
    if int(r["year"]) >= 2024:
        key = f"{r['disease']}_{r['metric']}_{r['year']}"
        fhm[r["region_code"]][key] = float(r["value"])

# IQVIA aggregated per region per product
import openpyxl as xl
wb_iq = xl.load_workbook(SRC / "VitiScience_Vaccines_Apr-02-2026.xlsx", data_only=True, read_only=True)
ws_iq = wb_iq["Sweden Sell-In"]
rows_iq = list(ws_iq.iter_rows(values_only=True))
hdr_iq = rows_iq[0]
data_iq = rows_iq[1:]
COL = {h: i for i, h in enumerate(hdr_iq)}
val_cols = [(i, h) for i, h in enumerate(hdr_iq) if h and h.startswith("Sell In Value")]
unit_cols = [(i, h) for i, h in enumerate(hdr_iq) if h and h.startswith("Units")]
COUNTY_MAP = {
    "01 - Stockholms län":"01","03 - Uppsala län":"03","04 - Södermanlands län":"04",
    "05 - Östergötlands län":"05","06 - Jönköpings län":"06","07 - Kronobergs län":"07",
    "08 - Kalmar län":"08","09 - Gotlands län":"09","10 - Blekinge län":"10",
    "12 - Skåne län":"12","13 - Hallands län":"13","14 - Västra Götalands län":"14",
    "17 - Värmlands län":"17","18 - Örebro län":"18","19 - Västmanlands län":"19",
    "20 - Dalarnas län":"20","21 - Gävleborgs län":"21","22 - Västernorrlands län":"22",
    "23 - Jämtlands län":"23","24 - Västerbottens län":"24","25 - Norrbottens län":"25",
}
iq = defaultdict(lambda: defaultdict(lambda: {"value":0.0, "units":0.0}))
for r in data_iq:
    county = r[COL["County Council"]]
    product = r[COL["Product Name Incl PI"]]
    if not product: continue
    region = COUNTY_MAP.get(county)
    if not region: continue
    v = sum(r[i] for i,_ in val_cols if isinstance(r[i],(int,float)))
    u = sum(r[i] for i,_ in unit_cols if isinstance(r[i],(int,float)))
    iq[region][product]["value"] += v
    iq[region][product]["units"] += u

REGIONS = [
    ("01","Region Stockholm","Stockholm-Gotland"),
    ("09","Region Gotland","Stockholm-Gotland"),
    ("03","Region Uppsala","Mellansverige"),
    ("04","Region Sörmland","Mellansverige"),
    ("19","Region Västmanland","Mellansverige"),
    ("18","Region Örebro län","Mellansverige"),
    ("20","Region Dalarna","Mellansverige"),
    ("21","Region Gävleborg","Mellansverige"),
    ("17","Region Värmland","Mellansverige"),
    ("05","Region Östergötland","Sydöstra"),
    ("06","Region Jönköpings län","Sydöstra"),
    ("08","Region Kalmar","Sydöstra"),
    ("12","Region Skåne","Södra"),
    ("10","Region Blekinge","Södra"),
    ("13","Region Halland","Södra"),
    ("07","Region Kronoberg","Södra"),
    ("14","Västra Götalandsregionen","Västra"),
    ("22","Region Västernorrland","Norra"),
    ("23","Region Jämtland Härjedalen","Norra"),
    ("24","Region Västerbotten","Norra"),
    ("25","Region Norrbotten","Norra"),
]

# === TBE PENETRATION ANALYSIS ===
# Hypothesis: regions with high TBE burden + LOW FSME-IMMUN per-capita uptake = opportunity
print("\n" + "=" * 80)
print("TBE × FSME-IMMUN PENETRATION ANALYSIS")
print("=" * 80)

tbe_records = []
for code, name, svr in REGIONS:
    p = pop.get(code, {})
    pop_total = int(p.get("total", 0) or 0)
    if not pop_total: continue
    fh = fhm.get(code, {})
    tbe_inc = fh.get("tbe_incidence_per_100k_2025") or 0
    region_iq = iq.get(code, {})
    # Pfizer FSME-IMMUN sell-in (vuxen + junior, 36 mo total)
    fsme_pfi = region_iq.get("FSME-IMMUN VUXEN", {}).get("value", 0) + region_iq.get("FSME-IMMUN JUNIOR", {}).get("value", 0)
    fsme_per_capita_yr = (fsme_pfi / pop_total / 3) if pop_total else 0  # /3 for 36 months annualized
    # Total TBE market (all products)
    tbe_total = fsme_pfi + region_iq.get("ENCEPUR", {}).get("value", 0) + region_iq.get("ENCEPUR BARN", {}).get("value", 0)
    pfizer_share = (fsme_pfi / tbe_total * 100) if tbe_total > 0 else 0
    tbe_records.append({
        "region_code": code, "region": name, "sjukvardsregion": svr,
        "tbe_incidence_2025": tbe_inc,
        "fsme_pfi_sek_36mo": round(fsme_pfi, 0),
        "fsme_pfi_sek_per_capita_yr": round(fsme_per_capita_yr, 2),
        "tbe_market_total_sek": round(tbe_total, 0),
        "pfizer_share_pct": round(pfizer_share, 1),
    })

# Score: opportunity = (TBE incidence rank) + (low Pfizer share rank — inverted)
# Normalize each to 0-100
def normalize_rank(records, key, reverse=False):
    """Return dict of region_code → percentile (0=worst, 100=best)."""
    vals = [(r["region_code"], r[key] or 0) for r in records]
    vals.sort(key=lambda x: x[1], reverse=reverse)
    n = len(vals)
    return {code: round(i / (n-1) * 100, 1) for i, (code, _) in enumerate(vals)}

# High TBE = high opportunity (rank ascending so high values = high opportunity score)
tbe_burden_score = normalize_rank(tbe_records, "tbe_incidence_2025", reverse=False)
# Low Pfizer share = high opportunity (rank ascending so low share = high opportunity score)
share_gap_score = normalize_rank(tbe_records, "pfizer_share_pct", reverse=True)

for r in tbe_records:
    burden = tbe_burden_score.get(r["region_code"], 50)
    gap = share_gap_score.get(r["region_code"], 50)
    # Opportunity = average of burden and gap (high burden + low share = high opportunity)
    r["opportunity_score"] = round((burden + gap) / 2, 1)
    r["burden_score"] = burden
    r["gap_score"] = gap

# Save TBE analysis
fields = ["region_code","region","sjukvardsregion","tbe_incidence_2025","fsme_pfi_sek_36mo",
          "fsme_pfi_sek_per_capita_yr","tbe_market_total_sek","pfizer_share_pct",
          "burden_score","gap_score","opportunity_score"]
with open(OUT_INT / "penetration_tbe.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in sorted(tbe_records, key=lambda x: -x["opportunity_score"]):
        w.writerow(r)

print(f"\nTop 5 OPPORTUNITY regions (high TBE burden + low Pfizer share):")
print(f"  {'Region':<28} {'TBE/100k':>9} {'Pfi share %':>12} {'Opp score':>10}")
for r in sorted(tbe_records, key=lambda x: -x["opportunity_score"])[:5]:
    print(f"  {r['region']:<28} {r['tbe_incidence_2025']:>9.2f} {r['pfizer_share_pct']:>12.1f} {r['opportunity_score']:>10.1f}")

# === IPD × PREVENAR PENETRATION ANALYSIS ===
print("\n" + "=" * 80)
print("IPD × PREVENAR PENETRATION ANALYSIS")
print("=" * 80)

ipd_records = []
for code, name, svr in REGIONS:
    p = pop.get(code, {})
    pop_total = int(p.get("total", 0) or 0)
    pop_65 = int(p.get("age_65plus", 0) or 0)
    if not pop_total: continue
    fh = fhm.get(code, {})
    ipd_inc = fh.get("ipd_incidence_per_100k_2025") or 0
    region_iq = iq.get(code, {})
    prev_pfi = region_iq.get("PREVENAR 13", {}).get("value", 0) + region_iq.get("PREVENAR 20", {}).get("value", 0)
    # Per 65+ adult (target population for adult vaccination)
    prev_per_65_yr = (prev_pfi / pop_65 / 3) if pop_65 else 0
    pneu_total = prev_pfi + region_iq.get("VAXNEUVANCE", {}).get("value", 0) + region_iq.get("CAPVAXIVE", {}).get("value", 0)
    pfizer_share = (prev_pfi / pneu_total * 100) if pneu_total > 0 else 0
    ipd_records.append({
        "region_code": code, "region": name, "sjukvardsregion": svr,
        "ipd_incidence_2025": ipd_inc,
        "pop_65plus": pop_65,
        "prev_pfi_sek_36mo": round(prev_pfi, 0),
        "prev_pfi_sek_per_65_yr": round(prev_per_65_yr, 2),
        "pneu_market_total_sek": round(pneu_total, 0),
        "pfizer_share_pct": round(pfizer_share, 1),
    })

ipd_burden_score = normalize_rank(ipd_records, "ipd_incidence_2025", reverse=False)
ipd_share_gap_score = normalize_rank(ipd_records, "pfizer_share_pct", reverse=True)

for r in ipd_records:
    burden = ipd_burden_score.get(r["region_code"], 50)
    gap = ipd_share_gap_score.get(r["region_code"], 50)
    r["opportunity_score"] = round((burden + gap) / 2, 1)
    r["burden_score"] = burden
    r["gap_score"] = gap

fields = ["region_code","region","sjukvardsregion","ipd_incidence_2025","pop_65plus",
          "prev_pfi_sek_36mo","prev_pfi_sek_per_65_yr","pneu_market_total_sek","pfizer_share_pct",
          "burden_score","gap_score","opportunity_score"]
with open(OUT_INT / "penetration_ipd.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in sorted(ipd_records, key=lambda x: -x["opportunity_score"]):
        w.writerow(r)

print(f"\nTop 5 OPPORTUNITY regions (high IPD burden + low Pfizer pneumokock share):")
print(f"  {'Region':<28} {'IPD/100k':>9} {'Pfi share %':>12} {'Opp score':>10}")
for r in sorted(ipd_records, key=lambda x: -x["opportunity_score"])[:5]:
    print(f"  {r['region']:<28} {r['ipd_incidence_2025']:>9.2f} {r['pfizer_share_pct']:>12.1f} {r['opportunity_score']:>10.1f}")

print(f"\nFiles saved:")
print(f"  {OUT_INT / 'penetration_tbe.csv'}")
print(f"  {OUT_INT / 'penetration_ipd.csv'}")
