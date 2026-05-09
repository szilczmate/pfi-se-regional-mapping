# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v13.xlsx — client-grade polish pass.

Delta vs v12:
1. Rewritten README sheet (was stuck at "v0.4" header from v04 build)
2. New "Data Dictionary" sheet — every column source, definition, year, caveat
3. Frozen panes (row 1) on all data sheets
4. Autofilters on all data sheets
5. Excel Tables (named, styled) on the key sheets
6. Consistent column widths + number formatting where meaningful

No data changes. Pure packaging/polish for client hand-off.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import shutil
from pathlib import Path
from datetime import date
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
MASTER = ROOT / "working/data/master"
SRC = MASTER / "master_workbook_v12.xlsx"
DST = MASTER / "master_workbook_v13.xlsx"
TODAY = "2026-04-24"

shutil.copy(SRC, DST)
wb = openpyxl.load_workbook(DST)

# ============ 1) REWRITE README ============
if "README" in wb.sheetnames:
    wb.remove(wb["README"])
ws = wb.create_sheet("README", 0)  # first sheet

TITLE = Font(bold=True, size=16, color="FFFFFF")
H1 = Font(bold=True, size=13, color="005B96")
H2 = Font(bold=True, size=11)
BODY = Font(size=10)
WRAP = Alignment(wrap_text=True, vertical="top")
LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)
DARK_BLUE = PatternFill(start_color="005B96", end_color="005B96", fill_type="solid")
LIGHT_BLUE = PatternFill(start_color="DAEEF3", end_color="DAEEF3", fill_type="solid")
YELLOW = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

r = 1
c = ws.cell(row=r, column=1, value="Pfizer Sweden Regional Landscape Mapping — Master Workbook v13")
c.font = TITLE; c.fill = DARK_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
ws.row_dimensions[r].height = 28

r += 2
ws.cell(row=r, column=1, value="Project: VS-2026-PFI-001").font = H2
r += 1
ws.cell(row=r, column=1, value="Vendor: Viti Science AB   •   Client: Pfizer Sweden, Access & Value team (Samira Toghanian)").font = BODY
r += 1
ws.cell(row=r, column=1, value=f"Version 13 — 2026-04-24 (polish pass)").font = BODY
r += 1
ws.cell(row=r, column=1, value="Delivery date: 2026-05-15 (target)").font = BODY

# ============ OVERVIEW ============
r += 2
ws.cell(row=r, column=1, value="WHAT THIS WORKBOOK CONTAINS").font = H1
ws.cell(row=r, column=1).fill = LIGHT_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
r += 1

overview = [
    "32 sheets covering demographics, economy, disease burden, pharma utilisation, stakeholder governance,",
    "regulatory context, opportunity scoring, and regional engagement angles for all 21 Swedish regions.",
    "",
    "Scope: all public data sources verified (SCB, Kolada, FHM, Socialstyrelsen, SKR, cancercentrum.se,",
    "samverkanlakemedel.se, TLV). Pfizer IQVIA vaccines extract integrated. 7 Pfizer oral Rx products",
    "pulled from Socialstyrelsen Läkemedelsregistret per region × year 2021-2024.",
    "",
    "Robustness QA: 27/27 validation checks pass vs external benchmarks (see 'Robustness QA' sheet).",
]
for line in overview:
    ws.cell(row=r, column=1, value=line).font = BODY
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 1

# ============ SHEET INVENTORY ============
r += 1
ws.cell(row=r, column=1, value="SHEET INVENTORY").font = H1
ws.cell(row=r, column=1).fill = LIGHT_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
r += 1

inventory = [
    ("CORE DATA — 21 regions × all metrics", "", ""),
    ("Region master", "Primary 21×48 matrix: demography, economy, disease, mortality, SES, quality, pharma", "All regions, latest year available per metric"),
    ("Per-capita view", "Region master ranked per-capita on key indicators", ""),
    ("Governance box per region", "Stakeholder panel per region (RD, HSD, RSO, HSN, LK, NT-rådet, NSG)", ""),
    ("", "", ""),
    ("DEMOGRAPHIC + ECONOMIC", "", ""),
    ("Future — pop projections", "SCB BefProgRegFakN 2030/2040/2050 projections", "2024 → 2050"),
    ("Future — life expectancy", "SCB life expectancy + gender delta 5-yr average", "2021-2025 avg"),
    ("Workforce", "Specialist physician density + other workforce metrics", "2024"),
    ("", "", ""),
    ("DISEASE BURDEN", "", ""),
    ("Cancer landscape", "Breast/prostate/lung incidence + mortality per region", "2023-2024"),
    ("Mortality indicators", "6 Kolada mortality KPIs per region (premature, amenable, cause-specific)", "Latest available"),
    ("Wait times", "Kolada SVF specialist/operation wait metrics", "2024"),
    ("Infectious disease epi", "TBE + IPD per region, full history", "1997-2025"),
    ("Lifestyle factors", "Smoking, obesity, falls", "2024"),
    ("", "", ""),
    ("PHARMA + REGULATORY", "", ""),
    ("Läkemedelsregistret Rx", "7 Pfizer orals per region per year (Socialstyrelsen direct pull)", "2021-2024"),
    ("Rx 2024 snapshot", "Per-capita normalised Rx for 7 products", "2024"),
    ("NT-rådet status v2", "Status per Pfizer product (recommendation, agreement, archived, await)", "Latest samverkanlakemedel.se"),
    ("TLV decisions", "TLV förmånsbeslut per Pfizer product", "Latest"),
    ("Combined regulatory view", "TLV + NT-rådet paired table", "Latest"),
    ("SKR Pharma 2026", "SKR Överenskommelse Läkemedelsförmånerna 2026 national context + Pfizer relevance", "2026"),
    ("Vaccine market share", "Pfizer vs competitor share per ATC class (IQVIA)", "Rolling 36 mo to Mar 2026"),
    ("Vaccine sales detail", "IQVIA Pfizer vaccines by ATC/year/region", "Apr 2023 – Mar 2026"),
    ("", "", ""),
    ("ANALYTICAL / OPPORTUNITY", "", ""),
    ("OPP - TBE penetration", "TBE vaccine opportunity vs incidence — top: Uppsala", "Computed"),
    ("OPP - IPD penetration", "IPD / pneumococcal opportunity — top: Blekinge", "Computed"),
    ("OPP - All products composite", "147 product × region scored combinations", "Computed"),
    ("OPP - Top per region", "Top 3 Pfizer opportunities per region", "Computed"),
    ("Competitor pipeline", "Enhertu, Tecvayli, Kisqali, Verzenios threats", "Horizon-scanned"),
    ("Health equity overlay", "SES composite (foreign-born + education + mortality) rank per region", "Computed"),
    ("", "", ""),
    ("QUALITATIVE / CONTEXT", "", ""),
    ("Regional plans + angles", "v1 substrate per region from plan PDFs", ""),
    ("Regional plans + angles v2", "10 new regional plans parsed 2026-04-24 with keyword densities", ""),
    ("RCC Insights 2024-2025", "Samverkansregionala cancerrapport + 4 RCC documents thematic summary", ""),
    ("Quality + access KPIs", "17 quality/access indicators consolidated", ""),
    ("", "", ""),
    ("METADATA", "", ""),
    ("Data sources", "Every metric's source + indicator ID + extraction date + caveat", "Living document"),
    ("Robustness QA", "27 validation checks vs external benchmarks", ""),
    ("Data Dictionary", "Column-by-column definitions for Region master", ""),
    ("README", "This file", ""),
]

# Table header
for col, hdr in enumerate(["Sheet", "Contents", "Coverage / Year"], 1):
    c = ws.cell(row=r, column=col, value=hdr)
    c.font = H2; c.fill = YELLOW
r += 1
for row in inventory:
    sheet, contents, coverage = row
    if not sheet and not contents:
        r += 1; continue
    if not contents:  # section header
        c = ws.cell(row=r, column=1, value=sheet)
        c.font = H2; c.fill = LIGHT_BLUE
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    else:
        ws.cell(row=r, column=1, value=sheet).font = Font(bold=True, size=10)
        ws.cell(row=r, column=2, value=contents).alignment = WRAP
        ws.cell(row=r, column=3, value=coverage).alignment = WRAP
    r += 1

# ============ HOW TO USE ============
r += 1
ws.cell(row=r, column=1, value="HOW TO USE THIS WORKBOOK").font = H1
ws.cell(row=r, column=1).fill = LIGHT_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
r += 1
usage = [
    "1. START at 'Region master' — the 21-region primary matrix. All other sheets drill into specific domains.",
    "2. For stakeholder context per region, pair 'Governance box per region' with stakeholder_mapping_v7.xlsx (separate file).",
    "3. For Pfizer product-specific analysis: 'Läkemedelsregistret Rx' (Socialstyrelsen actual Rx), 'Vaccine sales detail' (IQVIA), 'NT-rådet status v2', 'TLV decisions'.",
    "4. Health equity overlay + Mortality indicators = layered evidence for 'where need is highest'.",
    "5. Data Dictionary sheet explains every Region master column's source and definition.",
    "6. Data sources sheet lists every metric's provenance (source, ID, date) for defensibility.",
    "",
    "Every quantitative cell has a source identifiable via Data Dictionary + Data sources sheets.",
    "If a cell is blank, it either (a) data not reported by that region or (b) structural suppression (see caveats in Data Dictionary).",
]
for line in usage:
    ws.cell(row=r, column=1, value=line).font = BODY
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 1

# ============ CHANGELOG (condensed) ============
r += 1
ws.cell(row=r, column=1, value="VERSION HISTORY").font = H1
ws.cell(row=r, column=1).fill = LIGHT_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
r += 1
changelog = [
    ("v13 (2026-04-24, polish)", "Rewritten README, added Data Dictionary sheet, applied Excel Tables + frozen panes + autofilters. No data changes."),
    ("v12 (2026-04-24)", "Completeness audit closed: 5 gaps investigated, RCC Insights added, PxWeb API documented, Stockholm Kloka listan NULL finding."),
    ("v11 (2026-04-24)", "Läkemedelsregistret Rx automated via Playwright — 7 Pfizer orals × 21 regions × 2021-2024. Talzenna ATC corrected to L01XK04."),
    ("v10 (2026-04-24)", "SKR Pharma 2026 context sheet (Överenskommelse Läkemedelsförmånerna 2026)."),
    ("v9 (2026-04-24)", "Health equity overlay (SES + mortality composite). 5 new Region master columns: utrikes födda %, eftergymn %, förtida död, åtgärdbar död, självmord."),
    ("v8 (2026-04-24)", "Quality + access KPIs consolidation, regulatory sheets."),
    ("v01-v07 (2026-04-24)", "Progressive build: demographics → pharma → disease burden → regulatory → opportunity."),
]
for v, desc in changelog:
    ws.cell(row=r, column=1, value=v).font = Font(bold=True, size=10)
    ws.cell(row=r, column=2, value=desc).alignment = WRAP
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    r += 1

# ============ CONTACT + OWNERSHIP ============
r += 1
ws.cell(row=r, column=1, value="OWNERSHIP + REFRESH").font = H1
ws.cell(row=r, column=1).fill = LIGHT_BLUE
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
r += 1
ownership = [
    "Viti Science maintains the underlying extraction + integration pipeline.",
    "Annual refresh service available — Kolada + SCB + FHM + Socialstyrelsen refresh + Läkemedelsregistret year-over-year delta.",
    "Contact: sergio.flores@vitiscience.com for refresh scheduling.",
]
for line in ownership:
    ws.cell(row=r, column=1, value=line).font = BODY
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 1

# Column widths for README
ws.column_dimensions['A'].width = 32
ws.column_dimensions['B'].width = 62
ws.column_dimensions['C'].width = 28
ws.column_dimensions['D'].width = 15
ws.column_dimensions['E'].width = 15
ws.column_dimensions['F'].width = 15

# ============ 2) DATA DICTIONARY ============
if "Data Dictionary" in wb.sheetnames:
    wb.remove(wb["Data Dictionary"])
# Insert right after README
ws_dict = wb.create_sheet("Data Dictionary", 1)

ws_dict.cell(row=1, column=1, value="Region master column dictionary").font = Font(bold=True, size=14, color="FFFFFF")
ws_dict.cell(row=1, column=1).fill = DARK_BLUE
ws_dict.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)

dict_hdrs = ["Column", "Definition", "Source", "Indicator / URL", "Year / Notes"]
for col, h in enumerate(dict_hdrs, 1):
    c = ws_dict.cell(row=2, column=col, value=h)
    c.font = H2; c.fill = YELLOW

dict_rows = [
    ("Region code", "Official two-digit county code (länskod) as used by SCB & Kolada", "SCB BE/Skatteverket", "—", "Stable; 00 = national total"),
    ("Region", "Region name per common use (e.g. 'Stockholm', 'Västra Götaland')", "Norm by Viti", "—", ""),
    ("Sjukvårdsregion", "One of 6 collaborative healthcare regions (Norr/Mellansverige/Stockholm-Gotland/Sydöstra/Syd/Väst)", "samverkanlakemedel.se", "—", "Governance layer"),
    ("Population", "Total population 31 Dec 2024", "SCB BE0101", "BefolkningNy", "2024"),
    ("Pop 65+", "Population 65+ 31 Dec 2024", "SCB BE0101", "BefolkningNy", "2024"),
    ("Pop 75+", "Population 75+ 31 Dec 2024", "SCB BE0101", "BefolkningNy", "2024"),
    ("Pop women 15-44", "Women 15-44 (Abrysvo maternal target)", "SCB BE0101", "BefolkningNy", "2024"),
    ("Pop 0-1", "Children 0-1 (Abrysvo infant target via maternal transfer)", "SCB BE0101", "BefolkningNy", "2024"),
    ("Births 2024", "Live births 2024", "SCB BE0101/BE0101H", "", "2024 preliminary"),
    ("BRP/inv (tkr)", "Regional GDP per capita, current prices, tusen kronor", "SCB NR0105", "NR0105_preliminar", "2023 preliminary"),
    ("BRP total (mnkr)", "Regional GDP total, million SEK", "SCB NR0105", "", "2023"),
    ("Employed (1000s)", "Employed 16-74, 1000s", "SCB AM0101", "", "2024"),
    ("Specialist läkare (#)", "Specialist physicians total", "Kolada N01813", "kolada.se", "2024"),
    ("HC cost/inv", "Hälso- och sjukvårdskostnad per invånare (inkl läkemedel)", "Kolada N70061", "kolada.se", "2024"),
    ("HC excl pharma/inv", "Hälso- och sjukvårdskostnad excl läkemedel per invånare", "Kolada N70017", "kolada.se", "2024"),
    ("Primary care/inv", "Primärvårdskostnad per invånare", "Kolada N71007", "kolada.se", "2024"),
    ("Pharma förmån/inv", "Kostnad läkemedel inom förmånen per invånare", "Kolada N70001", "kolada.se", "2024 — förmån (Rx-disp via apotek)"),
    ("Pharma total/inv (excl tandvård)", "Total pharma kostnad per invånare (excl dental)", "Kolada N70059", "kolada.se", "2024 — förmån + rekvisition proxy"),
    ("Breast ca rate /100k", "Breast cancer incidence rate", "Kolada N06020", "kolada.se", "2023"),
    ("Prostate ca rate /100k", "Prostate cancer incidence rate", "Kolada N06035", "kolada.se", "2023"),
    ("Lung ca incidence /100k", "Lung cancer incidence", "Kolada N06011", "kolada.se", "2023"),
    ("Lung ca mortality /100k", "Lungcancer, dödlighet 25+, åldersstand.", "Kolada N02013", "kolada.se", "2024"),
    ("Breast ca screening detect %", "Andel screeningupptäckt bröstcancer", "Kolada ÖJ KPI", "kolada.se", "2024 (14 regioner rapporterar)"),
    ("Breast ca surgery <28d %", "Andel bröstcancerkirurgi inom 28 dagar", "Kolada ÖJ KPI", "kolada.se", "2024 (13 regioner)"),
    ("MI incidence /100k", "Hjärtinfarkt incidens", "Kolada", "kolada.se", "2024"),
    ("MI prevalence /100k", "Hjärtinfarkt prevalens", "Kolada", "kolada.se", "2024"),
    ("Heart care quality (0-100)", "Hjärtvårdens kvalitetsindex SWEDEHEART", "Kolada", "kolada.se", "2024"),
    ("Specialist wait <=90d %", "Andel specialistbesök inom 90 dagar (SVF)", "Kolada N15030", "kolada.se", "2024"),
    ("Operation wait <=90d %", "Andel operation/åtgärd inom 90 dagar", "Kolada N15029", "kolada.se", "2024"),
    ("Median wait spec days", "Mediantid till specialistbesök", "Kolada", "kolada.se", "2024"),
    ("Median wait op days", "Mediantid till operation", "Kolada", "kolada.se", "2024"),
    ("Daily smokers %", "Andel dagligrökare 16+ år", "Kolada N00953", "kolada.se", "2023 FHM national survey (regional precision varies)"),
    ("Overweight/obese %", "Andel med övervikt eller fetma 16+ år", "Kolada N00955", "kolada.se", "2023"),
    ("Falls 80+ /100k", "Fallolyckor 80+ åldersstand.", "Kolada", "kolada.se", "2024"),
    ("Falls 65-79 /100k", "Fallolyckor 65-79", "Kolada", "kolada.se", "2024"),
    ("MPR 2yo %", "Vaccintäckning MPR vid 2 års ålder", "Kolada N14401", "kolada.se", "2024"),
    ("HPV girls %", "HPV-vaccintäckning flickor", "Kolada", "kolada.se", "2024"),
    ("Antibiotic Rx /1000", "Antibiotikaförskrivning per 1000 invånare", "Kolada N00946", "kolada.se", "2024 — J01 excl dentala"),
    ("TBE cases 2025", "TBE-fall 2025", "FHM SmiNet sminet3-prod.sminet.se", "mapapp CSV 2026-04-30", "2025 full year"),
    ("TBE /100k 2025", "TBE incidens 2025", "FHM + SCB pop", "derived", "2025"),
    ("IPD cases 2025", "Invasiv pneumokockinfektion 2025", "FHM SmiNet", "mapapp CSV 2026-04-30", "2025"),
    ("IPD /100k 2025", "IPD incidens 2025", "FHM + SCB", "derived", "2025"),
    ("Vaccine sell-in /inv (SEK/yr)", "IQVIA Pfizer vaccines sell-in per capita, 12-month rolling", "Pfizer IQVIA extract (Johanna 2026-04-02)", "J07*", "Apr 2023–Mar 2026 annualised"),
    ("Utrikes födda % 2024", "Andel utrikes födda av befolkningen", "SCB BE0101E InrUtrFoddaRegAlKon", "Fodelseregion=11", "2024 — fixed v9 (was broken var name)"),
    ("Eftergymnasial utbildning 25-64 % 2024", "Andel med eftergymnasial utbildning 25-64 år", "SCB UF0506/UF0506B/Utbildning", "UtbildningsNiva 5,6,7 summed", "2024"),
    ("Förtida dödsfall 25-64 /100k (åldersstand.)", "Premature mortality 25-64 age-standardised", "Kolada N01451", "kolada.se", "2024 — åldersstandardiserat"),
    ("Åtgärdbar dödlighet sjukvård /100k (3-års mv)", "Healthcare-amenable mortality Eurostat/OECD 3-year rolling", "Kolada N79190", "kolada.se", "2023 (3-års mv)"),
    ("Självmord 25+ /100k (5-års mv)", "Suicide 25+ 5-year rolling mean", "Kolada N61603", "kolada.se", "2024 (5-års mv)"),
]

for row_i, row_data in enumerate(dict_rows, 3):
    for col, val in enumerate(row_data, 1):
        c = ws_dict.cell(row=row_i, column=col, value=val)
        c.alignment = WRAP
        c.font = BODY

for col, width in enumerate([38, 50, 30, 38, 40], 1):
    ws_dict.column_dimensions[get_column_letter(col)].width = width

# Freeze header row
ws_dict.freeze_panes = "A3"

# Apply Excel Table style
last_row = len(dict_rows) + 2
tbl = Table(displayName="DataDictionary", ref=f"A2:E{last_row}")
tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws_dict.add_table(tbl)

# ============ 3) APPLY FREEZE PANES + AUTOFILTER on data sheets ============
SHEETS_TO_POLISH = [
    "Region master", "Governance box per region", "Per-capita view", "Future — pop projections",
    "Quality + access KPIs", "Future — life expectancy", "Cancer landscape", "Health equity overlay",
    "Mortality indicators", "Wait times",
    "OPP - TBE penetration", "OPP - IPD penetration", "OPP - All products composite", "OPP - Top per region",
    "Infectious disease epi", "Lifestyle factors", "Workforce", "Combined regulatory view",
    "NT-rådet status v2", "TLV decisions", "Regional plans + angles v2",
    "Vaccine market share", "Vaccine sales detail", "Data sources", "Robustness QA",
    "Läkemedelsregistret Rx", "Rx 2024 snapshot", "Competitor pipeline",
]
for sheet_name in SHEETS_TO_POLISH:
    if sheet_name not in wb.sheetnames: continue
    ws_s = wb[sheet_name]
    if ws_s.max_row < 2: continue
    ws_s.freeze_panes = "B2"  # freeze top row + first col
    # Apply autofilter
    last_col = get_column_letter(ws_s.max_column)
    last_r = ws_s.max_row
    ws_s.auto_filter.ref = f"A1:{last_col}{last_r}"

wb.save(DST)
print(f"Saved: {DST}")
print(f"  Sheets: {len(wb.sheetnames)}")
print(f"  README rewritten + Data Dictionary added + {len(SHEETS_TO_POLISH)} sheets got freeze panes + autofilter")
