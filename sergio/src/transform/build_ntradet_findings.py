# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build structured CSV + workbook of NT-rådet status per Pfizer product.
Based on direct page fetches and search results 2026-04-24."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path
from datetime import date

OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
OUT_MASTER = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master")

today = date.today().isoformat()

# Status categories
# - "NT_RECOMMENDATION": formal NT-rådet recommendation issued
# - "NATIONAL_AGREEMENT": national pricing agreement, no formal recommendation, regional decisions
# - "REGIONAL_ASSESSMENT": NT-rådet decided regions assess on their own
# - "AWAIT": NT-rådet recommends regions await
# - "ARCHIVED": NT-rådet has handed off to NAG LOK or similar
# - "OUT_OF_SCOPE": product type not handled by NT-rådet (vaccines/COVID/etc.)
# - "UNKNOWN": no information found via WebFetch/WebSearch on 2026-04-24

findings = [
    {
        "pfizer_product": "Tukysa",
        "substance": "tucatinib",
        "atc": "L01EH03",
        "indication": "HER2+ metastatic breast cancer w/ brain mets, 3L+, in combo with trastuzumab + capecitabine",
        "nt_status": "NT_RECOMMENDATION",
        "decision_date": "2022-05-23",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "Found via web search. Direct samverkanlakemedel.se page not located via WebFetch; Tukysa likely under different URL slug. Manual verification recommended to confirm exact wording.",
        "gap_analysis_method": "Compute regional uptake from IQVIA (when oncology extract arrives) or Rx register (oral). Compare against expected eligible (C50 incidence x 20% HER2+ x 30% brain mets).",
    },
    {
        "pfizer_product": "Lorbrena",
        "substance": "lorlatinib",
        "atc": "L01ED04",
        "indication": "ALK+ NSCLC, post-1L",
        "nt_status": "UNKNOWN",
        "decision_date": "",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "Direct samverkanlakemedel.se page not located. Approved EU 2018; likely has had some NT-rådet review. Needs manual search by Sergio/Máté.",
        "gap_analysis_method": "Even without NT-rådet rec, regional variability via Rx register vs C34 incidence x ~5% ALK+ is informative.",
    },
    {
        "pfizer_product": "Elrexfio",
        "substance": "elranatamab",
        "atc": "L01FX25",
        "indication": "Multipelt myelom (RRMM 4L+)",
        "nt_status": "NATIONAL_AGREEMENT",
        "decision_date": "2024-06-14",
        "agreement_start": "2024-06-01",
        "agreement_end": "2027-01-31",
        "pdf_url": "https://samverkanlakemedel.se/download/18.165c6f351900ff10197e04/1718341468454/Elrexfio%20RRMM%202024-06-14.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/elrexfio-elranatamab",
        "notes": "Handled via requisition (rekvisition); not in Rx register. National agreement extension option through 2028-01-31.",
        "gap_analysis_method": "Hospital-administered. Need IQVIA (or Concise) for regional volumes. Compare against C90 incidence x ~50% reaching 4L.",
    },
    {
        "pfizer_product": "Ibrance",
        "substance": "palbociclib",
        "atc": "L01EF01",
        "indication": "HR+/HER2- advanced/metastatic breast cancer, in combo with endocrine therapy",
        "nt_status": "UNKNOWN",
        "decision_date": "",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "Direct page not located. Approved EU 2016; CDK4/6 inhibitor class likely had NT review. Manual verification needed.",
        "gap_analysis_method": "Oral, in Rx register. Regional variability vs C50 x ~70% HR+/HER2- x ~30% advanced is informative even without NT rec.",
    },
    {
        "pfizer_product": "Talzenna",
        "substance": "talazoparib",
        "atc": "L01XK04",
        "indication": "BRCA-mutated HER2-negative breast cancer",
        "nt_status": "NATIONAL_AGREEMENT",
        "decision_date": "2024-06-01",
        "agreement_start": "2024-06-01",
        "agreement_end": "2026-05-31",
        "pdf_url": "",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/talzenna-talazoparib",
        "notes": "NT-rådet explicitly will NOT issue recommendation. National agreement only. Extension option through 2027-05-31. Verbatim: 'NT-rådet kommer inte att ge en rekommendation till regionerna om läkemedlets användning.'",
        "gap_analysis_method": "Oral, in Rx register. Regional variability is the signal — no NT recommendation to compare against.",
    },
    {
        "pfizer_product": "Vyndaqel",
        "substance": "tafamidis",
        "atc": "N07XX08",
        "indication": "Wildtype or hereditary transthyretin amyloidosis (TTR-amyloidos) in adults with cardiomyopathy (ATTR-CM)",
        "nt_status": "ARCHIVED",
        "decision_date": "2025-09-02",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/vyndaqel-tafamidis",
        "notes": "NT-rådet ARCHIVED its recommendation 2025-09-02. NAG LOK (Nationell Arbetsgrupp Läkemedel och Onkologisk Klinikläkemedel) now handles. Sveriges läkemedelskommittéer issued recommendation 2025-10-15.",
        "gap_analysis_method": "Oral, in Rx register. Multi-source recommendations (NT-rådet historical + NAG LOK current + LK 2025-10-15) — frame as 'transitioning oversight regime'.",
    },
    {
        "pfizer_product": "Hympavzi",
        "substance": "marstacimab",
        "atc": "(no established ATC yet)",
        "indication": "Severe haemophilia A or B with inhibitors",
        "nt_status": "UNKNOWN",
        "decision_date": "",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "Newer product (EU approval ~2024). Not found on samverkanlakemedel.se. May not yet be under NT-rådet review.",
        "gap_analysis_method": "Hospital-administered (subcut). Regional volumes via IQVIA only (not in Rx register). Compare against population x rare-disease prevalence.",
    },
    {
        "pfizer_product": "Paxlovid",
        "substance": "nirmatrelvir + ritonavir",
        "atc": "J05AE30",
        "indication": "COVID-19 outpatient treatment, high-risk patients",
        "nt_status": "OUT_OF_SCOPE",
        "decision_date": "",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "COVID-19 treatments managed via Folkhälsomyndigheten / national pandemic governance, not standard NT-rådet pathway.",
        "gap_analysis_method": "Oral, in Rx register. Regional uptake variability is informative; declining as COVID phase ends.",
    },
    {
        "pfizer_product": "Vydura",
        "substance": "rimegepant",
        "atc": "N02CD06",
        "indication": "Migraine (acute and prophylactic)",
        "nt_status": "REGIONAL_ASSESSMENT",
        "decision_date": "2021-11-18",  # Date of early assessment report
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "https://samverkanlakemedel.se/download/18.25cdd0fd18e65a1a5d0379bf/1640084404393/Rimegepant-vid-migr%C3%A4n-tidig-bedomningsrapport-211118.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/vydura-rimegepant",
        "notes": "NT-rådet decided rimegepant 'kan bedömas regionalt' — no national recommendation. Regions assess independently.",
        "gap_analysis_method": "Oral, in Rx register. Regional decisions = regional variability is itself the signal.",
    },
    {
        "pfizer_product": "Prevenar 20",
        "substance": "20-valent pneumococcal conjugate vaccine",
        "atc": "J07AL02",
        "indication": "Pneumococcal disease prevention, adults 65+",
        "nt_status": "OUT_OF_SCOPE",
        "decision_date": "",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "",
        "notes": "Vaccines for adult prevention go through FHM / regional vaccination strategies, not standard NT-rådet pathway.",
        "gap_analysis_method": "Use IQVIA + FHM IPD epi + age 65+ pop denominator. Regional coverage variability is the signal.",
    },
    {
        "pfizer_product": "Abrysvo",
        "substance": "RSV vaccine",
        "atc": "J07BX05",
        "indication": "RSV vaccine for elderly (and pregnancy)",
        "nt_status": "AWAIT",
        "decision_date": "2023-10-05",
        "agreement_start": "",
        "agreement_end": "",
        "pdf_url": "https://samverkanlakemedel.se/download/18.25cdd0fd18e65a1a5d02c6d1/1696501601122/Avvakta%20Arexvy%20och%20Abrysvo%202023-10-05.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/abrysvo-rsv-vaccin",
        "notes": "NT-rådet recommendation: 'Avvakta' (await funding decision). TLV health-economic valuation received June 2024; supplementary analysis September 2025. Still under review as of Sep 2025.",
        "gap_analysis_method": "Use IQVIA. Per-region uptake DESPITE 'avvakta' recommendation = strong signal of regions making independent funding decisions. POLITICALLY INTERESTING for Pfizer.",
    },
]

# Save CSV
fields = ["pfizer_product","substance","atc","indication","nt_status","decision_date",
          "agreement_start","agreement_end","pdf_url","product_page_url","notes","gap_analysis_method"]
with open(OUT_INT / "ntradet_pfizer_status.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(findings)

# Status distribution
from collections import Counter
counts = Counter(f["nt_status"] for f in findings)
print(f"NT-rådet status distribution across 11 Pfizer products:")
for status, n in counts.most_common():
    print(f"  {status:<22} {n}")

# Build a workbook for human review
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "NT-rådet status"

hdr = ["Product","Substance","ATC","Indication","NT-rådet status",
       "Decision date","Agreement start","Agreement end","PDF","Product page",
       "Notes","Gap-analysis approach"]
ws.append(hdr)
for f in findings:
    ws.append([f[k] for k in fields])

# Style
header_fill = PatternFill("solid", fgColor="305496")
header_font = Font(bold=True, color="FFFFFF")
for col in range(1, len(hdr)+1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[1].height = 38

# Color code by status
status_colors = {
    "NT_RECOMMENDATION":   "C6EFCE",  # green
    "NATIONAL_AGREEMENT":  "DDEBF7",  # blue
    "REGIONAL_ASSESSMENT": "FFF2CC",  # yellow
    "AWAIT":               "FCE4D6",  # orange
    "ARCHIVED":            "EAD1DC",  # purple
    "OUT_OF_SCOPE":        "D9D9D9",  # grey
    "UNKNOWN":             "F4CCCC",  # red
}
for row in range(2, ws.max_row + 1):
    status = ws.cell(row=row, column=5).value
    color = status_colors.get(status, "FFFFFF")
    fill = PatternFill("solid", fgColor=color)
    ws.cell(row=row, column=5).fill = fill

widths = [14, 22, 12, 50, 22, 14, 14, 14, 50, 50, 50, 60]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "B2"
for r in range(2, ws.max_row+1):
    ws.row_dimensions[r].height = 60

# Add legend sheet
ws2 = wb.create_sheet("Status legend")
legend = [
    ["Status", "Meaning", "What it implies for Upgrade #1 (gap analysis)"],
    ["NT_RECOMMENDATION", "Formal NT-rådet yttrande issued", "Classic gap analysis: observed uptake vs expected eligible"],
    ["NATIONAL_AGREEMENT", "National pricing agreement; no formal NT recommendation", "Regions adopt at their own pace; variability IS the signal"],
    ["REGIONAL_ASSESSMENT", "NT-rådet declined; regions decide independently", "Variability across regions = the analytical question"],
    ["AWAIT", "NT-rådet says regions should await funding decision", "Regions buying despite 'avvakta' = political signal"],
    ["ARCHIVED", "NT-rådet has handed off to other body (NAG LOK, etc.)", "Multi-source recommendations; track transitions"],
    ["OUT_OF_SCOPE", "Product type not handled by NT-rådet (vaccines, COVID, etc.)", "Use parallel governance (FHM, etc.) for analysis"],
    ["UNKNOWN", "No information found via web search 2026-04-24", "Manual deeper search needed; treat as gap in our research"],
]
for row in legend:
    ws2.append(row)
for col in range(1, 4):
    c = ws2.cell(row=1, column=col); c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
for i, w in enumerate([22, 50, 60], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 38

# Add raw evidence sheet (for traceability)
ws3 = wb.create_sheet("Evidence trail")
ws3.append(["Product", "Source", "URL", "Date fetched", "Key quote / finding"])
evidence = [
    ("Tukysa", "Web search via Targeted Onc / Lakartidningen", "https://lakartidningen.se/aktuellt/nyheter/2024/02/nt-radet-ger-klartecken-for-bredare-anvandning-av-brostcancerterapi/", today, "NT-rådet recommendation for HER2+ BC documented from May 23, 2022"),
    ("Lorbrena", "samverkanlakemedel.se", "https://samverkanlakemedel.se/produktinfo/lorbrena-lorlatinib", today, "404 - URL pattern doesn't match for Lorbrena"),
    ("Elrexfio", "samverkanlakemedel.se direct page", "https://samverkanlakemedel.se/produktinfo/elrexfio-elranatamab", today, "Decision 2024-06-14, national agreement 2024-06-01 to 2027-01-31, indication 'multipelt myelom'"),
    ("Ibrance", "samverkanlakemedel.se", "https://samverkanlakemedel.se/produktinfo/ibrance-palbociclib", today, "404 - URL pattern doesn't match for Ibrance"),
    ("Talzenna", "samverkanlakemedel.se direct page", "https://samverkanlakemedel.se/produktinfo/talzenna-talazoparib", today, "Verbatim 'NT-rådet kommer inte att ge en rekommendation till regionerna om läkemedlets användning' Agreement 2024-06-01 to 2026-05-31"),
    ("Vyndaqel", "samverkanlakemedel.se direct page", "https://samverkanlakemedel.se/produktinfo/vyndaqel-tafamidis", today, "NT-rådet 'arkiverad rekommendationen 2025-09-02'. NAG LOK has assumed responsibility. Sveriges läkemedelskommittéer 2025-10-15"),
    ("Hympavzi", "samverkanlakemedel.se search", "(none found)", today, "No results on samverkanlakemedel.se"),
    ("Paxlovid", "samverkanlakemedel.se search", "(none found)", today, "Not on samverkanlakemedel.se — managed via FHM channel"),
    ("Vydura", "samverkanlakemedel.se direct page", "https://samverkanlakemedel.se/produktinfo/vydura-rimegepant", today, "'NT-rådet har beslutat att rimegepant kan bedömas regionalt'. Early assessment report 2021-11-18"),
    ("Prevenar 20", "samverkanlakemedel.se search", "(none found)", today, "Vaccine — managed via FHM channel"),
    ("Abrysvo", "samverkanlakemedel.se direct page", "https://samverkanlakemedel.se/produktinfo/abrysvo-rsv-vaccin", today, "'Rekommendation att avvakta' 2023-10-05. PDF: Avvakta Arexvy och Abrysvo. Under review as of Sep 2025"),
]
for e in evidence:
    ws3.append(e)
for col in range(1, 6):
    c = ws3.cell(row=1, column=col); c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
for i, w in enumerate([14, 32, 60, 14, 60], start=1):
    ws3.column_dimensions[get_column_letter(i)].width = w
ws3.row_dimensions[1].height = 38

out_file = OUT_MASTER / "ntradet_pfizer_status_v1.xlsx"
wb.save(out_file)
print(f"\nSaved CSV: {OUT_INT / 'ntradet_pfizer_status.csv'}")
print(f"Saved Excel: {out_file}")
