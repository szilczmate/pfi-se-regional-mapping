# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build composite Pfizer regional opportunity score per region.
Methodology:
  Score = weighted combination of:
    - Disease burden (relative to national avg) — higher burden = higher opportunity
    - Pfizer market share gap (relative to product class) — lower share = higher opportunity
    - Wait time / access pressure — higher pressure = higher opportunity for Pfizer prevention
    - Aging population (65+) — higher = higher opportunity for vaccines/Vyndaqel
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
from collections import defaultdict
from pathlib import Path
from datetime import date

INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
SRC = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
today = date.today().isoformat()

def load_csv(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))

pop = {r["region_code"]: r for r in load_csv(INT / "scb_population_2024_by_region.csv")}
extras = defaultdict(dict)
for r in load_csv(INT / "kolada_extras_latest.csv"):
    extras[r["region_code"][2:]][r["kpi"]] = float(r["value"]) if r["value"] else None
extras_v2 = defaultdict(dict)
for r in load_csv(INT / "kolada_extras_v2_latest.csv"):
    extras_v2[r["region_code"][2:]][r["kpi"]] = float(r["value"]) if r["value"] else None
fhm = defaultdict(dict)
for r in load_csv(INT / "fhm_epi_long.csv"):
    if r["region_code"] in ("?", "00"): continue
    if int(r["year"]) >= 2024:
        key = f"{r['disease']}_{r['metric']}_{r['year']}"
        fhm[r["region_code"]][key] = float(r["value"])

# IQVIA aggregated
import openpyxl as xl
wb_iq = xl.load_workbook(SRC / "VitiScience_Vaccines_Apr-02-2026.xlsx", data_only=True, read_only=True)
ws_iq = wb_iq["Sweden Sell-In"]
rows_iq = list(ws_iq.iter_rows(values_only=True))
hdr_iq = rows_iq[0]; data_iq = rows_iq[1:]
COL = {h: i for i, h in enumerate(hdr_iq)}
val_cols = [(i, h) for i, h in enumerate(hdr_iq) if h and h.startswith("Sell In Value")]
COUNTY_MAP = {"01 - Stockholms län":"01","03 - Uppsala län":"03","04 - Södermanlands län":"04","05 - Östergötlands län":"05","06 - Jönköpings län":"06","07 - Kronobergs län":"07","08 - Kalmar län":"08","09 - Gotlands län":"09","10 - Blekinge län":"10","12 - Skåne län":"12","13 - Hallands län":"13","14 - Västra Götalands län":"14","17 - Värmlands län":"17","18 - Örebro län":"18","19 - Västmanlands län":"19","20 - Dalarnas län":"20","21 - Gävleborgs län":"21","22 - Västernorrlands län":"22","23 - Jämtlands län":"23","24 - Västerbottens län":"24","25 - Norrbottens län":"25"}
iq = defaultdict(lambda: defaultdict(lambda: {"value":0.0}))
for r in data_iq:
    code = COUNTY_MAP.get(r[COL["County Council"]])
    product = r[COL["Product Name Incl PI"]]
    if not code or not product: continue
    iq[code][product]["value"] += sum(r[i] for i,_ in val_cols if isinstance(r[i],(int,float)))

REGIONS = [
    ("01","Region Stockholm","Stockholm-Gotland"),("09","Region Gotland","Stockholm-Gotland"),
    ("03","Region Uppsala","Mellansverige"),("04","Region Sörmland","Mellansverige"),
    ("19","Region Västmanland","Mellansverige"),("18","Region Örebro län","Mellansverige"),
    ("20","Region Dalarna","Mellansverige"),("21","Region Gävleborg","Mellansverige"),
    ("17","Region Värmland","Mellansverige"),("05","Region Östergötland","Sydöstra"),
    ("06","Region Jönköpings län","Sydöstra"),("08","Region Kalmar","Sydöstra"),
    ("12","Region Skåne","Södra"),("10","Region Blekinge","Södra"),
    ("13","Region Halland","Södra"),("07","Region Kronoberg","Södra"),
    ("14","Västra Götalandsregionen","Västra"),("22","Region Västernorrland","Norra"),
    ("23","Region Jämtland Härjedalen","Norra"),("24","Region Västerbotten","Norra"),
    ("25","Region Norrbotten","Norra"),
]

def percentile_rank(values_dict, reverse=False):
    """Return code → 0-100 rank. reverse=True means high values rank low (worst=0)."""
    items = [(c, v) for c, v in values_dict.items() if v is not None]
    items.sort(key=lambda x: x[1], reverse=reverse)
    n = len(items)
    return {c: round(i / (n-1) * 100, 1) for i, (c, _) in enumerate(items)} if n > 1 else {}

# Build per-product opportunity scores
products = {
    "Prevenar 20 (pneumokock 65+)": {
        "burden_metric": ("ipd_2025", lambda code: fhm.get(code,{}).get("ipd_incidence_per_100k_2025")),
        "share_metric": ("pneu_share", lambda code: compute_pneu_share(code)),
        "demographic_metric": ("pop_65plus_pct", lambda code: int(pop.get(code,{}).get("age_65plus",0) or 0) / int(pop.get(code,{}).get("total",1) or 1) * 100),
        "weight_burden": 0.4, "weight_share_gap": 0.4, "weight_demo": 0.2,
    },
    "Abrysvo (RSV adult)": {
        "burden_metric": ("ipd_2025_proxy", lambda code: fhm.get(code,{}).get("ipd_incidence_per_100k_2025")),  # using IPD as proxy for respiratory burden
        "share_metric": ("rsv_share", lambda code: compute_rsv_share(code)),
        "demographic_metric": ("pop_75plus_pct", lambda code: int(pop.get(code,{}).get("age_75plus",0) or 0) / int(pop.get(code,{}).get("total",1) or 1) * 100),
        "weight_burden": 0.2, "weight_share_gap": 0.4, "weight_demo": 0.4,
    },
    "FSME-IMMUN (TBE)": {
        "burden_metric": ("tbe_2025", lambda code: fhm.get(code,{}).get("tbe_incidence_per_100k_2025")),
        "share_metric": ("tbe_share", lambda code: compute_tbe_share(code)),
        "demographic_metric": ("pop_total", lambda code: int(pop.get(code,{}).get("total",0) or 0)),
        "weight_burden": 0.5, "weight_share_gap": 0.3, "weight_demo": 0.2,
    },
    "Tukysa (HER2+ BC)": {
        "burden_metric": ("breast_rate", lambda code: extras.get(code,{}).get("N70345")),
        "share_metric": ("breast_surgery_wait", lambda code: extras_v2.get(code,{}).get("N70601")),  # higher = better access (already pfizer adjacent)
        "demographic_metric": ("pop_women_15_44", lambda code: int(pop.get(code,{}).get("women_15_44",0) or 0) / int(pop.get(code,{}).get("total",1) or 1) * 100),
        "weight_burden": 0.5, "weight_share_gap": 0.3, "weight_demo": 0.2,
    },
    "Lorviqua (ALK+ NSCLC)": {
        "burden_metric": ("lung_inc", lambda code: extras.get(code,{}).get("N60912")),
        "share_metric": ("smoking_pct", lambda code: extras_v2.get(code,{}).get("U01402")),  # smoking is risk factor, higher = more lung cancer
        "demographic_metric": ("pop_total", lambda code: int(pop.get(code,{}).get("total",0) or 0)),
        "weight_burden": 0.5, "weight_share_gap": 0.3, "weight_demo": 0.2,
    },
    "Vyndaqel (ATTR-CM)": {
        "burden_metric": ("mi_inc", lambda code: extras.get(code,{}).get("N01439")),  # MI as cardiac context
        "share_metric": ("heart_quality", lambda code: extras.get(code,{}).get("N70539")),
        "demographic_metric": ("pop_75plus_pct", lambda code: int(pop.get(code,{}).get("age_75plus",0) or 0) / int(pop.get(code,{}).get("total",1) or 1) * 100),
        "weight_burden": 0.3, "weight_share_gap": 0.3, "weight_demo": 0.4,
    },
    "Vydura (migraine)": {
        "burden_metric": ("women_pop", lambda code: int(pop.get(code,{}).get("women_15_44",0) or 0) / int(pop.get(code,{}).get("total",1) or 1) * 100),
        "share_metric": ("antibiotic_usage", lambda code: extras.get(code,{}).get("N00404")),  # neutral; not direct
        "demographic_metric": ("pop_total", lambda code: int(pop.get(code,{}).get("total",0) or 0)),
        "weight_burden": 0.5, "weight_share_gap": 0.2, "weight_demo": 0.3,
    },
}

def compute_pneu_share(code):
    rq = iq.get(code, {})
    pfi = rq.get("PREVENAR 13",{}).get("value",0) + rq.get("PREVENAR 20",{}).get("value",0)
    tot = pfi + rq.get("VAXNEUVANCE",{}).get("value",0) + rq.get("CAPVAXIVE",{}).get("value",0)
    return (pfi/tot*100) if tot > 0 else 0

def compute_rsv_share(code):
    rq = iq.get(code, {})
    pfi = rq.get("ABRYSVO",{}).get("value",0)
    tot = pfi + rq.get("AREXVY",{}).get("value",0)
    return (pfi/tot*100) if tot > 0 else 0

def compute_tbe_share(code):
    rq = iq.get(code, {})
    pfi = rq.get("FSME-IMMUN VUXEN",{}).get("value",0) + rq.get("FSME-IMMUN JUNIOR",{}).get("value",0)
    tot = pfi + rq.get("ENCEPUR",{}).get("value",0) + rq.get("ENCEPUR BARN",{}).get("value",0)
    return (pfi/tot*100) if tot > 0 else 0

# Compute scores
all_scores = []
for product_name, spec in products.items():
    # Build values dict for each metric
    burden_vals = {code: spec["burden_metric"][1](code) for code, _, _ in REGIONS}
    share_vals = {code: spec["share_metric"][1](code) for code, _, _ in REGIONS}
    demo_vals = {code: spec["demographic_metric"][1](code) for code, _, _ in REGIONS}

    # Filter Nones
    burden_vals = {c: v for c, v in burden_vals.items() if v is not None}
    share_vals = {c: v for c, v in share_vals.items() if v is not None}
    demo_vals = {c: v for c, v in demo_vals.items() if v is not None}

    # Rank: burden=high opportunity, share=low opportunity (gap), demo=high opportunity
    burden_rank = percentile_rank(burden_vals, reverse=False)
    share_rank = percentile_rank(share_vals, reverse=True)  # low share = high rank
    demo_rank = percentile_rank(demo_vals, reverse=False)

    for code, name, svr in REGIONS:
        burden_score = burden_rank.get(code, 50)
        share_score = share_rank.get(code, 50)
        demo_score = demo_rank.get(code, 50)
        composite = (
            spec["weight_burden"] * burden_score +
            spec["weight_share_gap"] * share_score +
            spec["weight_demo"] * demo_score
        )
        all_scores.append({
            "product": product_name,
            "region_code": code,
            "region": name,
            "sjukvardsregion": svr,
            "burden_metric": spec["burden_metric"][0],
            "burden_value": round(burden_vals.get(code, 0) or 0, 2),
            "burden_score": burden_score,
            "share_metric": spec["share_metric"][0],
            "share_value": round(share_vals.get(code, 0) or 0, 2),
            "share_score": share_score,
            "demo_metric": spec["demographic_metric"][0],
            "demo_value": round(demo_vals.get(code, 0) or 0, 2),
            "demo_score": demo_score,
            "composite_opportunity_score": round(composite, 1),
        })

# Save full long
fields = list(all_scores[0].keys())
with open(INT / "pfizer_regional_opportunity_scores.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(all_scores)

# Top 5 opportunities per product
print("\nTOP 5 REGIONAL OPPORTUNITIES PER PFIZER PRODUCT (composite score):")
print("=" * 80)
from collections import defaultdict
by_product = defaultdict(list)
for s in all_scores:
    by_product[s["product"]].append(s)

for product, scores in by_product.items():
    print(f"\n  {product}")
    print(f"  {'Region':<28} {'Burden':>8} {'Share gap':>10} {'Demo':>6} {'Composite':>10}")
    for s in sorted(scores, key=lambda x: -x["composite_opportunity_score"])[:5]:
        print(f"  {s['region']:<28} {s['burden_score']:>8.1f} {s['share_score']:>10.1f} {s['demo_score']:>6.1f} {s['composite_opportunity_score']:>10.1f}")

# Per-region "biggest single opportunity"
print("\n\nPER-REGION BIGGEST SINGLE PFIZER OPPORTUNITY:")
print("=" * 80)
print(f"  {'Region':<28} {'Top product':<32} {'Score':>6}")
by_region = defaultdict(list)
for s in all_scores:
    by_region[s["region"]].append(s)
for region in sorted(by_region.keys()):
    top = max(by_region[region], key=lambda x: x["composite_opportunity_score"])
    print(f"  {region:<28} {top['product']:<32} {top['composite_opportunity_score']:>6.1f}")

print(f"\nFile saved: {INT / 'pfizer_regional_opportunity_scores.csv'}")
