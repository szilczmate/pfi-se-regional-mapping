# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Save NT-rådet 'under beredning' pipeline as competitor intelligence for Pfizer."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
from pathlib import Path
from datetime import date

OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
today = date.today().isoformat()

# Captured from samverkanlakemedel.se 'under beredning' page 2026-04-24
competitors = [
    # (substance, brand, manufacturer, indication, NT-rådet decision_date_or_status, Pfizer product affected, threat_level, notes)
    ("trastuzumab deruxtekan", "Enhertu", "AstraZeneca/Daiichi", "HR+ HER2-låg/ultralåg breast cancer, 2L post-endokrin", "2025-01-15 (decision)", "Tukysa", "HIGH", "DIRECT competitor in HER2 breast cancer expanded indication. Pfizer's Tukysa is HER2+ 3L+; Enhertu's HER2-low extends competitor market significantly."),
    ("trastuzumab deruxtekan", "Enhertu", "AstraZeneca/Daiichi", "HER2+ gastrointestinal cancers", "2022-12-21 (decision)", "Tukysa (adjacent)", "MEDIUM", "Enhertu in GI HER2+ — different anatomy than Tukysa breast, but Enhertu pan-tumor positioning is competitive narrative"),
    ("teklistamab", "Tecvayli", "Janssen/J&J", "Multipelt myelom 2L kombination med daratumumab", "2026-02-25 (decision)", "Elrexfio", "HIGH", "DIRECT competitor — bispecific antibody MM. Tecvayli moves to 2L (earlier line); Elrexfio is 4L+. Long-term threat to Elrexfio market expansion"),
    ("isatuximab", "Sarclisa", "Sanofi", "Multipelt myelom 1L behandling", "2024-01-11 (decision)", "Elrexfio (adjacent)", "MEDIUM", "MM 1L — different line than Elrexfio (4L+), but reduces patient flow into later lines"),
    ("RSV-vaccin (allmän kategori)", "Abrysvo + Arexvy", "Pfizer + GSK", "Vaccin mot RS-virus, äldre", "2023-09-27 (decision)", "Abrysvo", "PFIZER OWN", "NT-rådet decision affects Pfizer's Abrysvo. Per our other findings: 'Avvakta' rec still active 2025-09. Tracking funding."),
    ("amivantamab", "Rybrevant", "Janssen/J&J", "EGFR-muterad NSCLC, 1:a linjen", "2024-09-12 (decision)", "Lorviqua (adjacent)", "LOW", "EGFR-muterad ≠ ALK+. Different molecular subtypes. But broader NSCLC competitive landscape developing."),
    ("exagamglogen autotemcel", "Casgevy", "Vertex/CRISPR", "CAR-T gene editing (sickle cell, beta-thalassemia)", "2023-12-20 (decision)", "Hympavzi (different MoA)", "LOW", "Different therapeutic area but landmark gene-editing approval signals shift in payer mindset for high-cost therapies"),
    ("lifileucel", "Amtagvi", "Iovance Biotherapeutics", "TIL therapy (melanoma)", "Withdrawn from EMA July 2025", "—", "NONE", "Withdrawn — no longer competitive concern"),
    ("pembrolizumab + enfortumab vedotin", "Keytruda + Padcev", "Merck + Astellas/Seagen", "Urotelial cancer kombinationsbehandling", "2026-02-11 (decision)", "—", "NONE", "Bladder cancer — outside Pfizer portfolio; broader Pfizer-Seagen relevance"),
]

fields = ["substance","brand","manufacturer","indication","nt_status_or_date","pfizer_product_affected","threat_level","notes"]
with open(OUT_INT / "nt_radet_competitor_pipeline.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for c in competitors:
        w.writerow(dict(zip(fields, c)))

print(f"Saved: {OUT_INT / 'nt_radet_competitor_pipeline.csv'}")
print(f"\n{len(competitors)} NT-rådet pipeline products affecting Pfizer:")
print()
print(f"  {'Threat':<8} {'Substance':<32} {'Brand':<22} {'Affects Pfizer':<24}")
threat_order = {"HIGH":0, "MEDIUM":1, "PFIZER OWN":2, "LOW":3, "NONE":4}
for c in sorted(competitors, key=lambda x: threat_order.get(x[6], 5)):
    print(f"  {c[6]:<8} {c[0][:30]:<32} {c[1]:<22} {c[5]:<24}")

# Also build a Pfizer "threat summary" — for each Pfizer product, which competitors are in pipeline
print(f"\n\nPER PFIZER PRODUCT — COMPETITIVE PIPELINE THREATS:")
from collections import defaultdict
by_pfizer = defaultdict(list)
for c in competitors:
    pfizer_prod = c[5]
    if pfizer_prod and pfizer_prod not in ("—", "PFIZER OWN"):
        by_pfizer[pfizer_prod.split(" ")[0]].append(c)

for product in ["Tukysa", "Lorviqua", "Elrexfio", "Hympavzi", "Vyndaqel", "Ibrance", "Talzenna", "Vydura", "Paxlovid", "Abrysvo", "Prevenar"]:
    threats = by_pfizer.get(product, [])
    if threats:
        print(f"\n  {product}:")
        for c in threats:
            print(f"    [{c[6]:<7}] {c[1]} ({c[0]}) — {c[3][:60]}")
    else:
        print(f"\n  {product}: no pipeline threats identified currently")
