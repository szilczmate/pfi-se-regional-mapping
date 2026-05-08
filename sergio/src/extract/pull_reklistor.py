# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Download regional drug formularies (REK-listor) and scan for Pfizer products.

Each region has its own formulary with a different URL pattern. This script:
  1. Downloads the PDFs we have direct URLs for
  2. For each, searches for Pfizer product names (brand + INN) to determine listing
  3. Builds a region × product matrix

Regions with direct PDF URLs (verified 2026-04-24):
  - Stockholm: Kloka listan 2026
  - Skåne: Skånelistan 2026
  - Blekinge: rekommenderade läkemedel 2026 (landing page, find PDF)

For others, we fall back to web-page scrape of the formulary landing page.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, re, json
from pathlib import Path
import pdfplumber

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw/reklistor")
OUT_RAW.mkdir(parents=True, exist_ok=True)
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

PFIZER_PRODUCTS = {
    "Ibrance": ["Ibrance", "palbociklib", "palbociclib"],
    "Vyndaqel": ["Vyndaqel", "tafamidis"],
    "Talzenna": ["Talzenna", "talazoparib"],
    "Tukysa": ["Tukysa", "tucatinib"],
    "Lorbrena": ["Lorbrena", "Lorviqua", "lorlatinib"],
    "Vydura": ["Vydura", "rimegepant"],
    "Paxlovid": ["Paxlovid", "nirmatrelvir"],
    "Prevenar 20": ["Prevenar 20", "Prevenar20", "PCV20"],
    "Abrysvo": ["Abrysvo"],
    "FSME-IMMUN": ["FSME-IMMUN", "FSME IMMUN"],
    "Elrexfio": ["Elrexfio", "elranatamab"],
    "Hympavzi": ["Hympavzi", "marstacimab"],
}

# Known REK-lista URLs
REKLISTOR = {
    "Stockholm": "https://klokalistan.se/download/18.35c7715f19b353dcac8bc0a/1766148745775/Kloka_Listan_2026.pdf",
    "Skåne": "https://vardgivare.skane.se/siteassets/1.-vardriktlinjer/lakemedel/skanelistans-bakgrundsmaterial/skanelistan-2026.pdf",
}

def fetch_and_scan(region, url):
    print(f"\n=== {region} ===  {url}")
    try:
        r = requests.get(url, timeout=120, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code != 200:
            print(f"  [FAIL] HTTP {r.status_code}")
            return None
        if not r.content.startswith(b"%PDF"):
            print(f"  [SKIP] Not PDF, first bytes={r.content[:20]}")
            return None
        safe = re.sub(r"[^\w\-]+", "_", region)
        dest = OUT_RAW / f"{safe}_reklista.pdf"
        dest.write_bytes(r.content)
        with pdfplumber.open(dest) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        (OUT_RAW / f"{safe}_reklista.txt").write_text(text, encoding="utf-8")
        print(f"  {len(pdf.pages)} pages, {len(text):,} chars")
        # Scan for each Pfizer product
        hits = {}
        for brand, synonyms in PFIZER_PRODUCTS.items():
            count = sum(len(re.findall(rf"\b{re.escape(syn)}\b", text, re.IGNORECASE)) for syn in synonyms)
            if count > 0:
                # Capture first context
                ctx = None
                for syn in synonyms:
                    m = re.search(rf"\b{re.escape(syn)}\b", text, re.IGNORECASE)
                    if m:
                        ctx = text[max(0, m.start()-80):m.start()+120].replace("\n", " ")
                        break
                hits[brand] = {"count": count, "context": ctx[:200] if ctx else None}
        return hits
    except Exception as e:
        print(f"  [ERR] {e}")
        return None

results = {}
for region, url in REKLISTOR.items():
    results[region] = fetch_and_scan(region, url)

# Summary table
print("\n=== Pfizer products in regional REK-listor ===")
brands = list(PFIZER_PRODUCTS.keys())
print(f"  {'Region':<18} | " + " | ".join(f"{b[:9]:>9}" for b in brands))
print("-" * 180)
for region, hits in results.items():
    if hits is None:
        print(f"  {region:<18} | {'(no data)':<180}")
        continue
    cells = []
    for brand in brands:
        if brand in hits:
            cells.append(f"{'★'+str(hits[brand]['count']):>9}")
        else:
            cells.append(f"{'—':>9}")
    print(f"  {region:<18} | " + " | ".join(cells))

# Show contexts for key products
print("\n=== Context snippets for key products (Stockholm, Skåne) ===")
for region, hits in results.items():
    if not hits: continue
    print(f"\n{region}:")
    for brand, data in hits.items():
        print(f"  {brand} (×{data['count']}): ...{data['context']}...")

# Save JSON
out = OUT_INT / "reklistor_pfizer_scan.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
