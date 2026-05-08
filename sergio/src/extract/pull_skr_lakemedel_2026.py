# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SKR pharma agreement + cirkulär documents for 2026.

Finding (2026-04-24 session 2): NEXT_STEPS.md originally said "cirkulär 26:5" but that
number isn't publicly listed. The actual documents are:
  1. Cirkulär 26:16 — LPIK 2026 läkemedelsindex (price/cost index methodology)
  2. Överenskommelse Läkemedelsförmånerna 2026 — full state-region pharma agreement with per-region allocation

Both contain the förmån vs rekvisition split context. Download and extract.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests
from pathlib import Path
import re

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw/skr")
OUT_RAW.mkdir(parents=True, exist_ok=True)
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

DOCS = {
    "Cirkulär_26-16_LPIK": "https://extra.skr.se/download/18.45e45e1119d24f88d0623c36/1774869548784/Cirkular_26-16.pdf",
    "Överenskommelse_Läkemedelsförmånerna_2026": "https://skr.se/download/18.7b047ebc19c2c45974b24140/1770364435824/Overenskommalse-Lakemedelsformanerna-2026.pdf",
    # Previously identified related docs
    "Ställningstagande_Läkemedel": "https://extra.skr.se/download/18.7b71856719c47c8ac3e2a244/1771250979076/Ställningstagande Läkemedel.pdf",
    "Cirkulär_26-8": "https://extra.skr.se/download/18.65f6f1b419c47a6784d31fad/1771341757492/CIRKULÄR 26-8 .pdf",
}

downloaded = {}
for name, url in DOCS.items():
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent":"Mozilla/5.0"})
        print(f"{name}: HTTP {r.status_code}, {len(r.content):,} bytes")
        if r.status_code != 200:
            continue
        if not r.content.startswith(b"%PDF"):
            print(f"  Not PDF: first 30={r.content[:30]}"); continue
        dest = OUT_RAW / f"{name}.pdf"
        dest.write_bytes(r.content)
        downloaded[name] = dest
    except Exception as e:
        print(f"{name}: {e}")

# Parse each PDF
try:
    import pdfplumber
except ImportError:
    print("pdfplumber missing"); sys.exit(1)

for name, path in downloaded.items():
    print(f"\n=== {name} ===")
    with pdfplumber.open(path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    (OUT_RAW / f"{name}.txt").write_text(text, encoding="utf-8")
    print(f"  {len(pdf.pages)} pages, {len(text):,} chars")

    # Look for per-region allocation table
    # Pattern: region name followed by large SEK number
    region_hits = re.findall(
        r"(Stockholm|Uppsala|Södermanland|Östergötland|Jönköping|Kronoberg|Kalmar|Gotland|Blekinge|Skåne|Halland|Västra Götaland|Värmland|Örebro|Västmanland|Dalarna|Gävleborg|Västernorrland|Jämtland|Västerbotten|Norrbotten)\s+([\d\s ]{5,})",
        text)
    if region_hits:
        print(f"  Region-value hits: {len(region_hits)} (first 5):")
        for r_, v_ in region_hits[:5]:
            print(f"    {r_:<20} {v_.strip()[:30]}")

    # Look for keywords
    kws = {
        "förmån": len(re.findall(r"förmån", text, re.IGNORECASE)),
        "rekvisition": len(re.findall(r"rekvisition", text, re.IGNORECASE)),
        "per region": len(re.findall(r"per\s+region", text, re.IGNORECASE)),
        "fördelning": len(re.findall(r"fördelning", text, re.IGNORECASE)),
        "bidrag": len(re.findall(r"bidrag", text, re.IGNORECASE)),
        "LPIK": len(re.findall(r"LPIK", text, re.IGNORECASE)),
        "behovsmodell": len(re.findall(r"behovsmodell", text, re.IGNORECASE)),
    }
    print(f"  Keywords: {kws}")

print(f"\nRaw files: {OUT_RAW}")
print("Done.")
