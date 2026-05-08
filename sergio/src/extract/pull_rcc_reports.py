# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull RCC (Regionalt cancercentrum) annual reports + samverkan reports.

Strategy: only RCC Syd publishes at a clean /download/ URL pattern. Other RCCs are more
opaque. Instead, pull:
  1. RCC Syd årsredovisning 2025 (most recent)
  2. RCC Syd årsredovisning 2024 (for comparison)
  3. "Samverkansregionala insatser årsrapport 2024" — covers all 6 RCCs centrally (more
     useful for Pfizer's cross-region comparison needs than 6 separate reports)
  4. RCC Norr cancerplan uppföljning 2025 (found)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, re, json
from pathlib import Path
import pdfplumber

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw/rcc")
OUT_RAW.mkdir(parents=True, exist_ok=True)
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

DOCS = {
    "RCC_Syd_Årsredovisning_2025": "https://cancercentrum.se/download/18.d4630df19c479448b93c33/1770812762563/Årsredovisning RCC Syd 2025.pdf",
    "RCC_Syd_Årsredovisning_2024": "https://cancercentrum.se/download/18.5eaa54d31967c2e29e4140/1745841406237/arsredovisning-rcc-syd-2024.pdf",
    "RCC_Samverkan_Årsrapport_2024": "https://cancercentrum.se/download/18.7df1d5341961de0462c34e2/1744380903612/bilaga-1-samverkansregionala-insatser_arsapport-2024.pdf",
    "RCC_Norr_Cancerplan_Uppföljning_2025": "https://cancercentrum.se/download/18.3d2e08671967cb4ebd71c61/1745937416673/uppfoljningsrapport-kvalitetsregister-cancerplan-rcc-norr-20250426.pdf",
    "RCC_Samverkan_Cancerrapport_Delrapport_2025": "https://cancercentrum.se/download/18.7bc6fce31993221716f6b7b3/1759229761944/Delrapport 2025 Överenskommelse Jämlik och effektiv cancervård.pdf",
}

def fetch_parse(name, url):
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=90, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code != 200:
            print(f"  [FAIL] HTTP {r.status_code}"); return None
        if not r.content.startswith(b"%PDF"):
            print(f"  [SKIP] Not PDF"); return None
        dest = OUT_RAW / f"{name}.pdf"
        dest.write_bytes(r.content)
        with pdfplumber.open(dest) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        (OUT_RAW / f"{name}.txt").write_text(text, encoding="utf-8")
        print(f"  [OK] {len(r.content):,} bytes, {len(pdf.pages)} pages, {len(text):,} chars")
        # Scan for Pfizer-relevant themes
        terms = {
            "bröstcancer": len(re.findall(r"bröstcancer", text, re.IGNORECASE)),
            "lungcancer": len(re.findall(r"lungcancer", text, re.IGNORECASE)),
            "HER2": len(re.findall(r"\bHER2\b", text)),
            "ALK": len(re.findall(r"\bALK\b(?:\s+pos|-pos|\+)?", text)),
            "BRCA": len(re.findall(r"\bBRCA", text)),
            "myelom": len(re.findall(r"myelom", text, re.IGNORECASE)),
            "amyloid": len(re.findall(r"amyloid", text, re.IGNORECASE)),
            "hereditär": len(re.findall(r"hereditär", text, re.IGNORECASE)),
            "palbociklib": len(re.findall(r"palbocik", text, re.IGNORECASE)),
            "ventetid": len(re.findall(r"\bv[äa]nte(?:tid|tider)\b", text, re.IGNORECASE)),
            "molekylär": len(re.findall(r"molekyl", text, re.IGNORECASE)),
            "prevention": len(re.findall(r"prevention", text, re.IGNORECASE)),
            "screening": len(re.findall(r"screening", text, re.IGNORECASE)),
        }
        # Show top hits
        nonzero = {k:v for k,v in terms.items() if v > 0}
        print(f"  Key themes: {nonzero}")
        return {"pages": len(pdf.pages), "chars": len(text), "themes": terms}
    except Exception as e:
        print(f"  [ERR] {e}")
        return None

results = {}
for name, url in DOCS.items():
    results[name] = fetch_parse(name, url)

out = OUT_INT / "rcc_reports_summary.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
