# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Round 4 — Västerbotten regionplan 2026. Gävleborg remains TBD."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, re, json
from pathlib import Path
import pdfplumber

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw/regional_plans")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

PDFS = {
    "Västerbotten (Regionplan 2026)": {
        "url": "https://www.regionvasterbotten.se/VLL/Filer/Regionplan%202026.pdf",
        "title": "Regionplan 2026",
    },
}

def parse(text):
    focus = re.findall(r"(?:Fokusområde|Prioritering|Strategiska? mål|Målområde|Strategiskt område|Utvecklingsområde|Inriktningsmål|Effektmål)\s*\d*[:\s]+([^\n]+)", text)
    sections = re.findall(r"^\s*(\d+\.?\s+[A-ZÅÄÖ][A-ZÅÄÖa-zåäö][^\n]+)$", text, re.MULTILINE)
    kws = {k: len(re.findall(rf"\b{p}", text, re.IGNORECASE))
           for k, p in [("cancer","cancer"), ("vaccin","vaccin"), ("äldre","äldre"),
                        ("kronisk","kronisk"), ("tillgänglig","tillgänglig"),
                        ("digital","digital"), ("nära vård",r"nära\s+vård"),
                        ("prevent",r"prevent|profylax"), ("jämlik","jämlik"),
                        ("primärvård","primärvård"), ("forskning","forskning"), ("infektion","infektion")]}
    return {"focus_areas": focus[:10], "sections": sections[:15], "keywords": kws}

results = {}
for region, info in PDFS.items():
    print(f"\n=== {region} ===")
    try:
        r = requests.get(info["url"], timeout=90, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code != 200:
            print(f"  [SKIP] HTTP {r.status_code}"); continue
        if not r.content.startswith(b"%PDF"):
            print(f"  [SKIP] Not PDF"); continue
        safe = re.sub(r"[^\w\-]+","_", region)
        dest = OUT_RAW / f"{safe}.pdf"
        dest.write_bytes(r.content)
        with pdfplumber.open(dest) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        (OUT_RAW / f"{safe}.txt").write_text(text, encoding="utf-8")
        parsed = parse(text); parsed["title"]=info["title"]; parsed["pages"]=len(pdf.pages); parsed["chars"]=len(text)
        results[region] = parsed
        print(f"  [OK] {len(r.content):,} bytes, {parsed['pages']} pages")
        print(f"       Keywords: {', '.join(f'{k}={v}' for k,v in parsed['keywords'].items() if v>0)}")
    except Exception as e:
        print(f"  [ERROR] {e}")

existing = json.loads((OUT_INT/"regional_plans_pdf_extraction_v3.json").read_text(encoding="utf-8"))
merged = {**existing, **results}
out = OUT_INT / "regional_plans_pdf_extraction_v4.json"
out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nTotal regions with parsed plan: {len(merged)}")
print(f"Saved: {out}")
