# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Update NT-rådet status workbook v2 with newly-found data on Lorbrena/Lorviqua, Ibrance, Hympavzi."""
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

# Updated findings (3 previously-UNKNOWN now resolved)
findings = [
    {
        "pfizer_product": "Tukysa", "substance": "tucatinib", "atc": "L01EH03",
        "indication": "HER2+ metastatic breast cancer w/ brain mets, 3L+, in combo with trastuzumab + capecitabine",
        "nt_status": "NT_RECOMMENDATION", "decision_date": "2022-05-23",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "", "product_page_url": "",
        "notes": "NT-rådet recommendation documented from 2022-05-23. Web search via Targeted Onc / Lakartidningen confirms.",
        "gap_analysis_method": "C50 incidence x 20% HER2+ x 30% brain mets",
    },
    {
        "pfizer_product": "Lorbrena (Lorviqua in Sweden)", "substance": "lorlatinib", "atc": "L01ED04",
        "indication": "ALK+ non-small cell lung cancer, post 1L",
        "nt_status": "REGIONAL_CANCER_CENTRE", "decision_date": "2020-03-23",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "https://cancercentrum.se/download/18.4b2c14a019545e36ca71f21e/1741945348869/utlatande-lorlatinib-vid-nsclc-200323.pdf",
        "product_page_url": "https://kunskapsbanken.cancercentrum.se/lakemedelsregimer/lungcancer/lorlatinib/",
        "notes": "CRITICAL: Sold as 'Lorviqua' in Sweden, not 'Lorbrena'. Regional Cancer Centre (RCC) statement 2020-03-23. TLV cost-per-QALY 730k-980k SEK deemed reasonable. ~50k SEK/month treatment cost. Older statement; verify if updated 2024-2025.",
        "gap_analysis_method": "C34 incidence x ~5% ALK+ x ~80% post-1L. Compare regional uptake from IQVIA when received.",
    },
    {
        "pfizer_product": "Elrexfio", "substance": "elranatamab", "atc": "L01FX25",
        "indication": "Multipelt myelom (RRMM 4L+)",
        "nt_status": "NATIONAL_AGREEMENT", "decision_date": "2024-06-14",
        "agreement_start": "2024-06-01", "agreement_end": "2027-01-31",
        "pdf_url": "https://samverkanlakemedel.se/download/18.165c6f351900ff10197e04/1718341468454/Elrexfio%20RRMM%202024-06-14.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/elrexfio-elranatamab",
        "notes": "Hospital-administered (rekvisition). Extension option through 2028-01-31.",
        "gap_analysis_method": "C90 incidence x ~50% reaching 4L. Need IQVIA (Concise) for hospital admin volumes.",
    },
    {
        "pfizer_product": "Ibrance", "substance": "palbociclib", "atc": "L01EF01",
        "indication": "HR+/HER2- advanced/metastatic breast cancer, in combo with endocrine therapy",
        "nt_status": "REGIONAL_DISADVANTAGE", "decision_date": "(varying per region)",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "",
        "product_page_url": "https://janusinfo.se/behandling/expertgruppsutlatanden/cancersjukdomar/cancersjukdomar/cdk46hammarevidbrostcancer.5.79a74aa1185055c07db24ef6.html",
        "notes": "COMPETITIVE INSIGHT: Region Stockholm's expert group + LK explicitly recommends RIBOCICLIB (Kisqali, Novartis) over palbociclib for cost reasons. CDK4/6 inhibitors deemed clinically comparable. This is potentially repeated across other regions — needs investigation. Significant Pfizer disadvantage.",
        "gap_analysis_method": "C50 x ~70% HR+/HER2- x ~30% advanced. CRITICAL to compare Pfizer Ibrance share vs Novartis Kisqali + Lilly Verzenios per region.",
    },
    {
        "pfizer_product": "Talzenna", "substance": "talazoparib", "atc": "L01XK04",
        "indication": "BRCA-mutated HER2-negative breast cancer",
        "nt_status": "NATIONAL_AGREEMENT", "decision_date": "2024-06-01",
        "agreement_start": "2024-06-01", "agreement_end": "2026-05-31",
        "pdf_url": "", "product_page_url": "https://samverkanlakemedel.se/produktinfo/talzenna-talazoparib",
        "notes": "NT-rådet explicitly will NOT issue recommendation. National agreement only. Extension option through 2027-05-31. Verbatim: 'NT-rådet kommer inte att ge en rekommendation till regionerna om läkemedlets användning.'",
        "gap_analysis_method": "Oral, in Rx register. Regional variability is the signal — no NT recommendation to compare against.",
    },
    {
        "pfizer_product": "Vyndaqel", "substance": "tafamidis", "atc": "N07XX08",
        "indication": "Wildtype/hereditary transthyretin amyloidosis (TTR-amyloidos) in adults with cardiomyopathy (ATTR-CM)",
        "nt_status": "ARCHIVED", "decision_date": "2025-09-02",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "", "product_page_url": "https://samverkanlakemedel.se/produktinfo/vyndaqel-tafamidis",
        "notes": "NT-rådet ARCHIVED 2025-09-02. NAG LOK now handles. Sveriges läkemedelskommittéer issued recommendation 2025-10-15. Live regulatory transition story.",
        "gap_analysis_method": "Oral, in Rx register. Multi-source recommendations across the transition window.",
    },
    {
        "pfizer_product": "Hympavzi", "substance": "marstacimab", "atc": "(no established ATC yet)",
        "indication": "Routine prophylaxis in haemophilia A or B (without inhibitors), age 12+",
        "nt_status": "TOO_NEW", "decision_date": "",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "", "product_page_url": "",
        "notes": "FDA approval 2024-10-11. EU approval timeline unclear. No Swedish recommendation yet — too new for NT-rådet review. First anti-TFPI for hemophilia. Hospital-administered (subcut, pre-filled pen).",
        "gap_analysis_method": "Insufficient data. Track regional uptake from IQVIA (when received) as early-adopter signal.",
    },
    {
        "pfizer_product": "Paxlovid", "substance": "nirmatrelvir + ritonavir", "atc": "J05AE30",
        "indication": "COVID-19 outpatient treatment, high-risk patients",
        "nt_status": "OUT_OF_SCOPE", "decision_date": "",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "", "product_page_url": "",
        "notes": "COVID-19 treatments managed via Folkhälsomyndigheten / national pandemic governance, not standard NT-rådet pathway.",
        "gap_analysis_method": "Oral, in Rx register. Regional uptake variability informative; declining as COVID phase ends.",
    },
    {
        "pfizer_product": "Vydura", "substance": "rimegepant", "atc": "N02CD06",
        "indication": "Migraine (acute and prophylactic)",
        "nt_status": "REGIONAL_ASSESSMENT", "decision_date": "2021-11-18",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "https://samverkanlakemedel.se/download/18.25cdd0fd18e65a1a5d0379bf/1640084404393/Rimegepant-vid-migr%C3%A4n-tidig-bedomningsrapport-211118.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/vydura-rimegepant",
        "notes": "NT-rådet 'kan bedömas regionalt' — no national recommendation. Regions assess independently.",
        "gap_analysis_method": "Oral, in Rx register. Regional decisions = regional variability is itself the signal.",
    },
    {
        "pfizer_product": "Prevenar 20", "substance": "20-valent pneumococcal conjugate vaccine", "atc": "J07AL02",
        "indication": "Pneumococcal disease prevention, adults 65+",
        "nt_status": "OUT_OF_SCOPE", "decision_date": "",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "", "product_page_url": "",
        "notes": "Vaccines for adult prevention go through FHM / regional vaccination strategies, not NT-rådet pathway.",
        "gap_analysis_method": "IQVIA + FHM IPD epi + age 65+ pop denominator. Regional coverage variability is the signal.",
    },
    {
        "pfizer_product": "Abrysvo", "substance": "RSV vaccine", "atc": "J07BX05",
        "indication": "RSV vaccine for elderly (and pregnancy)",
        "nt_status": "AWAIT", "decision_date": "2023-10-05",
        "agreement_start": "", "agreement_end": "",
        "pdf_url": "https://samverkanlakemedel.se/download/18.25cdd0fd18e65a1a5d02c6d1/1696501601122/Avvakta%20Arexvy%20och%20Abrysvo%202023-10-05.pdf",
        "product_page_url": "https://samverkanlakemedel.se/produktinfo/abrysvo-rsv-vaccin",
        "notes": "NT-rådet recommendation: 'Avvakta'. TLV health-economic valuation received June 2024; supplementary analysis September 2025. Still under review as of Sep 2025.",
        "gap_analysis_method": "IQVIA shows regions buying despite 'avvakta' — STRONGEST POLITICAL SIGNAL of the portfolio.",
    },
]

# Save updated CSV
fields = ["pfizer_product","substance","atc","indication","nt_status","decision_date",
          "agreement_start","agreement_end","pdf_url","product_page_url","notes","gap_analysis_method"]
with open(OUT_INT / "ntradet_pfizer_status.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(findings)

# Build updated workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "NT-rådet status v2"

hdr = ["Product","Substance","ATC","Indication","NT-rådet status",
       "Decision date","Agreement start","Agreement end","PDF","Product page",
       "Notes","Gap-analysis approach"]
ws.append(hdr)
for f in findings:
    ws.append([f[k] for k in fields])

header_fill = PatternFill("solid", fgColor="305496")
header_font = Font(bold=True, color="FFFFFF")
for col in range(1, len(hdr)+1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[1].height = 38

status_colors = {
    "NT_RECOMMENDATION":     "C6EFCE",
    "NATIONAL_AGREEMENT":    "DDEBF7",
    "REGIONAL_ASSESSMENT":   "FFF2CC",
    "REGIONAL_CANCER_CENTRE":"FFF2CC",
    "REGIONAL_DISADVANTAGE": "F4CCCC",
    "AWAIT":                 "FCE4D6",
    "ARCHIVED":              "EAD1DC",
    "OUT_OF_SCOPE":          "D9D9D9",
    "TOO_NEW":               "BDD7EE",
}
for row in range(2, ws.max_row+1):
    status = ws.cell(row=row, column=5).value
    color = status_colors.get(status, "FFFFFF")
    ws.cell(row=row, column=5).fill = PatternFill("solid", fgColor=color)

widths = [22, 22, 12, 50, 24, 14, 14, 14, 50, 50, 50, 60]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "B2"
for r in range(2, ws.max_row+1):
    ws.row_dimensions[r].height = 80

# Status legend updated
ws2 = wb.create_sheet("Status legend")
legend = [
    ["Status", "Meaning", "Implication for analysis"],
    ["NT_RECOMMENDATION", "Formal NT-rådet yttrande issued", "Classic gap analysis vs eligible population"],
    ["NATIONAL_AGREEMENT", "National pricing agreement; no formal NT recommendation", "Regions adopt at own pace; variability IS the signal"],
    ["REGIONAL_ASSESSMENT", "NT-rådet declined; regions decide independently", "Variability across regions is the analytical question"],
    ["REGIONAL_CANCER_CENTRE", "RCC statement issued (older Janusinfo channel)", "Verify if updated; pre-NT-rådet era recommendations"],
    ["REGIONAL_DISADVANTAGE", "Region(s) recommend competitor over Pfizer for cost reasons", "CRITICAL for Pfizer Access — competitive disadvantage to surface"],
    ["AWAIT", "NT-rådet says regions should await funding decision", "Regions buying despite 'avvakta' = political signal"],
    ["ARCHIVED", "NT-rådet has handed off to other body (NAG LOK, etc.)", "Multi-source recommendations; track transitions"],
    ["TOO_NEW", "Product newly approved; no Swedish recommendation yet", "Track early uptake as signal of regions watching the data"],
    ["OUT_OF_SCOPE", "Product type not handled by NT-rådet (vaccines, COVID)", "Use parallel governance (FHM) for analysis"],
]
for row in legend: ws2.append(row)
for col in range(1, 4):
    c = ws2.cell(row=1, column=col); c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
for i, w in enumerate([24, 50, 60], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 38

# Distribution
from collections import Counter
counts = Counter(f["nt_status"] for f in findings)
ws3 = wb.create_sheet("Status distribution")
ws3.append(["NT-rådet status", "# Pfizer products"])
for status, n in counts.most_common():
    ws3.append([status, n])
for col in range(1, 3):
    c = ws3.cell(row=1, column=col); c.fill = header_fill; c.font = header_font

out_file = OUT_MASTER / "ntradet_pfizer_status_v2.xlsx"
wb.save(out_file)

print(f"Saved: {out_file}")
print(f"Status distribution v2:")
for status, n in counts.most_common():
    print(f"  {status:<25} {n}")

print(f"\nKey changes from v1:")
print(f"  - Lorbrena: UNKNOWN → REGIONAL_CANCER_CENTRE (RCC 2020-03-23) — Swedish brand is 'Lorviqua'!")
print(f"  - Ibrance: UNKNOWN → REGIONAL_DISADVANTAGE (Stockholm prefers Kisqali/Novartis)")
print(f"  - Hympavzi: UNKNOWN → TOO_NEW (FDA Oct 2024)")
print(f"  - All 11 Pfizer products now have documented status")
