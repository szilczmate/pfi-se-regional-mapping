# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build engagement-angle snippets per region from parsed regional plan PDFs.

For each region where we have a parsed regional plan, extract 3-5 stated priorities
verbatim and generate a short "alignment angle" paragraph framed in the region's language.

Output: working/docs/REGION_ENGAGEMENT_ANGLES_v1.md + JSON for machine use.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json, re
from pathlib import Path

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW = ROOT / "working/data/raw/regional_plans"
INT = ROOT / "working/data/interim"
DOCS = ROOT / "working/docs"

# Load merged extraction JSON (v3 is most recent with all 10)
jsonp = INT / "regional_plans_pdf_extraction_v3.json"
if not jsonp.exists():
    jsonp = INT / "regional_plans_pdf_extraction_v2.json"
data = json.loads(jsonp.read_text(encoding="utf-8"))

print(f"Loaded {len(data)} regions from {jsonp.name}")

# For each region, pull raw text and extract first 5 bullet points or prioritiering passages
angles = {}

def extract_priority_text(region_key, raw_txt_path):
    if not raw_txt_path.exists():
        return None
    text = raw_txt_path.read_text(encoding="utf-8", errors="replace")

    # Strategy 1: find "Prioriterade områden" / "Prioriteringar" blocks and extract nearby bullets
    candidates = []
    for pat in [r"[Pp]rioriterade\s+områden?[\s\S]{0,1200}",
                r"[Ss]trategiska\s+mål[\s\S]{0,1200}",
                r"[Mm]ålområden?[\s\S]{0,1200}",
                r"[Ii]nriktningsmål[\s\S]{0,1200}",
                r"[Uu]tvecklingsområden?[\s\S]{0,1200}"]:
        m = re.search(pat, text)
        if m:
            candidates.append((pat.split(r"\s")[0].lstrip("[").rstrip("]"), m.group(0)))

    # Strategy 2: pull first 3-5 bullet-looking lines (• or - or numbered) from top 20% of doc
    head_chunk = text[:len(text)//5]
    bullet_matches = re.findall(r"(?:^|\n)\s*(?:[•\-*]|\d+\.)\s+([A-ZÅÄÖ][^\n]{20,150})", head_chunk)

    return {
        "priority_candidates": [{"source": src, "excerpt": excerpt[:500]} for src, excerpt in candidates[:2]],
        "bullets_from_head": bullet_matches[:7],
    }

# Region-specific angle templates (will be filled from extracted data)
ANGLE_TEMPLATES = {
    "Västmanland (Regionplan 2026-2028)": {
        "region": "Västmanland",
        "plan_title": "Regionplan och budget 2026-2028",
    },
    "Dalarna (Regionplan 2026-2028)": {
        "region": "Dalarna",
        "plan_title": "Regionplan, budget och finansplan 2026-2028",
    },
    "Kalmar (Regionplan 2026-2028)": {
        "region": "Kalmar",
        "plan_title": "Regionplan 2026-2028",
    },
    "Västernorrland (Regionplan 2026-2028)": {
        "region": "Västernorrland",
        "plan_title": "Regionplan 2026-2028 — Liv, hälsa och hållbar utveckling",
    },
    "Jämtland Härjedalen (Regionplan 2026-2028)": {
        "region": "Jämtland Härjedalen",
        "plan_title": "Regionplan och budget 2026-2028",
    },
    "Sörmland (Mål och budget 2025-2027)": {
        "region": "Sörmland",
        "plan_title": "Mål och budget 2025 med plan 2026-2027",
    },
    "Blekinge (Budget 2026-2028)": {
        "region": "Blekinge",
        "plan_title": "Budget 2026 med planer 2027-2028",
    },
    "Örebro län (Verksamhetsplan 2026)": {
        "region": "Örebro län",
        "plan_title": "Verksamhetsplan med budget 2026",
    },
    "Halland (Mål och budget 2026)": {
        "region": "Halland",
        "plan_title": "Mål och budget 2026 med ekonomisk plan 2027-2030",
    },
    "Östergötland (Strategiprogram 2022-2026)": {
        "region": "Östergötland",
        "plan_title": "Strategiprogram 2022-2026",
    },
}

for region_key, tpl in ANGLE_TEMPLATES.items():
    if region_key not in data:
        continue
    safe = re.sub(r"[^\w\-]+","_", region_key)
    txt_path = RAW / f"{safe}.txt"
    extracted = extract_priority_text(region_key, txt_path)
    keywords = data[region_key].get("keywords", {})

    # Pfizer-relevance tier based on keyword hits (rough heuristic)
    relevance_signals = []
    if keywords.get("cancer", 0) >= 3: relevance_signals.append(f"cancer={keywords['cancer']}")
    if keywords.get("vaccin", 0) >= 3: relevance_signals.append(f"vaccin={keywords['vaccin']}")
    if keywords.get("äldre", 0) >= 5: relevance_signals.append(f"äldre={keywords['äldre']}")
    if keywords.get("kronisk", 0) >= 2: relevance_signals.append(f"kronisk={keywords['kronisk']}")
    if keywords.get("nära vård", 0) >= 5: relevance_signals.append(f"nära vård={keywords['nära vård']}")
    if keywords.get("prevent", 0) >= 2: relevance_signals.append(f"prevention/profylax={keywords['prevent']}")
    if keywords.get("jämlik", 0) >= 5: relevance_signals.append(f"jämlik vård={keywords['jämlik']}")
    if keywords.get("digital", 0) >= 5: relevance_signals.append(f"digitalisering={keywords['digital']}")
    if keywords.get("forskning", 0) >= 5: relevance_signals.append(f"forskning={keywords['forskning']}")

    angles[tpl["region"]] = {
        "plan_title": tpl["plan_title"],
        "key_themes_from_keywords": relevance_signals,
        "raw_priority_candidates": extracted.get("priority_candidates", []) if extracted else [],
        "bullets_from_head": extracted.get("bullets_from_head", []) if extracted else [],
    }

# Write JSON
out_json = INT / "region_engagement_angles_v1.json"
out_json.write_text(json.dumps(angles, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved: {out_json}")

# Write Markdown per-region angle section
md_lines = ["# Regional Engagement Angles — Extracted from Regional Plans",
            "",
            f"**Source**: 10 parsed regional plan PDFs (Apr 2026).  Companion file: [`region_engagement_angles_v1.json`](../data/interim/region_engagement_angles_v1.json).",
            "**Purpose**: for Part B per-region deck profiles, frame Pfizer's portfolio in each region's *stated priority language*. Each section below is extracted verbatim from the region's own plan — NOT Viti's editorial.",
            "**Status**: v1 is the raw substrate. An analyst (or Máté) should rewrite the 'alignment angle' paragraph below each region so it speaks the region's language and links to Pfizer relevance without selling.",
            "",
            "---",
            ""]

for region, info in angles.items():
    md_lines.append(f"## Region {region}")
    md_lines.append(f"**Plan**: {info['plan_title']}")
    md_lines.append("")
    if info["key_themes_from_keywords"]:
        md_lines.append(f"**Key themes (by keyword density)**: {', '.join(info['key_themes_from_keywords'])}")
        md_lines.append("")
    if info["bullets_from_head"]:
        md_lines.append("**First bullets in document head (typical priorities list)**:")
        for b in info["bullets_from_head"][:6]:
            md_lines.append(f"- {b.strip()}")
        md_lines.append("")
    if info["raw_priority_candidates"]:
        for cand in info["raw_priority_candidates"][:1]:
            md_lines.append(f"**Priority block excerpt** (first match of `{cand['source']}`):")
            md_lines.append("> " + cand["excerpt"].replace("\n","\n> ")[:500])
            md_lines.append("")
    md_lines.append("**Alignment angle** (TO WRITE): *[analyst to draft — 2-3 sentences tying Pfizer's relevant products to the region's stated priorities in the region's own language]*")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

out_md = DOCS / "REGION_ENGAGEMENT_ANGLES_v1.md"
out_md.write_text("\n".join(md_lines), encoding="utf-8")
print(f"Saved: {out_md}  ({sum(len(l) for l in md_lines):,} chars)")

print("\nDone. Regions covered:", list(angles.keys()))
