# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Clean and update the master workbook for client delivery.

Reads master_workbook_v22.xlsx, applies:
- English translations for Swedish column headers
- Sheet name normalisation (drop "v2" suffixes, clarify some)
- Drop legacy duplicate sheets
- Logical sheet ordering
- Rebuild README with public-facing intro and a Swedish institutional glossary

Output: master_workbook_v23.xlsx (working source) + 06_master_workbook_v23.xlsx (delivery)
"""
from __future__ import annotations
import sys
import shutil
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v22.xlsx"
DST_WORK = ROOT / "working/data/master/master_workbook_v23.xlsx"
DST_DELIVERY = ROOT / "delivery/06_master_workbook_v23.xlsx"


# ============================================================================
# TRANSLATION DICTIONARY — Swedish to English
# ============================================================================
# Rule: keep institutional proper nouns in Swedish (NT-rådet, NSG, Sjukvårdsregion,
# Läkemedelskommitté, Region Stockholm, etc.). Translate descriptive headers and
# common phrases. Where institutional context matters, English first with Swedish
# in parentheses.
TRANSLATIONS = {
    # Common region structure
    "Sjukvårdsregion": "Healthcare region",
    "Region master — column-level confidence tags": "Region master — column-level confidence tags",

    # Demographics / economics
    "BRP/inv (tkr)": "GRP per capita (kSEK)",
    "BRP total (mnkr)": "GRP total (mSEK)",
    "Employed (1000s)": "Employed (1,000s)",
    "Specialist läkare (#)": "Specialist physicians (#)",
    "Spec läkare per 1000 inv": "Specialist physicians per 1,000 inhabitants",
    "Spec läkare årsarbetare": "Specialist physicians (FTE)",

    # Healthcare cost columns
    "HC cost/inv": "Healthcare cost per capita (SEK)",
    "HC excl pharma/inv": "Healthcare cost excl. pharma per capita (SEK)",
    "HC/inv": "Healthcare cost per capita (SEK)",
    "Primary care/inv": "Primary care cost per capita (SEK)",
    "Pharma förmån/inv": "Pharma reimbursement per capita (SEK)",
    "Pharma total/inv": "Pharma total cost per capita (SEK)",
    "Pharma % of HC": "Pharma as % of healthcare cost",
    "Vaccine sell-in /inv (SEK/yr)": "Vaccine sell-in per capita (SEK/year)",
    "Vaccine /inv/yr": "Vaccine sell-in per capita (SEK/year)",

    # Equity / SES
    "Utrikes födda %": "Foreign-born %",
    "Utrikes födda % 2024": "Foreign-born % (2024)",
    "Eftergymn. 25-64 %": "Post-secondary education 25–64 %",
    "Eftergymnasial utbildning 25-64 % 2024": "Post-secondary education 25–64 % (2024)",

    # Mortality
    "Förtida död 25-64 /100k": "Premature mortality 25–64 /100k",
    "Förtida dödsfall 25-64 /100k (åldersstand.)": "Premature mortality 25–64 /100k (age-std)",
    "Åtgärdbar död sjukvård /100k": "Healthcare-amenable mortality /100k",
    "Åtgärdbar dödlighet sjukvård /100k (3-års mv)": "Healthcare-amenable mortality /100k (3-yr MA)",
    "Självmord 25+ /100k (5-års mv)": "Suicide 25+ /100k (5-yr MA)",
    "Förtida död 25-64 (N01451)": "Premature mortality 25–64 (Kolada N01451)",
    "Lungcancer död 25+ (N02013)": "Lung cancer mortality 25+ (Kolada N02013)",
    "Självmord 25+ (N61603)": "Suicide 25+ (Kolada N61603)",
    "Åtgärdbar död sjukvård (N79190)": "Healthcare-amenable mortality (Kolada N79190)",
    "Åtgärdbar död hälsopolitik (N79191)": "Health-policy-amenable mortality (Kolada N79191)",
    "Stroke död 3 mån (N72461)": "Stroke mortality 3-month (Kolada N72461)",
    "år": "Year",

    # Quality + access
    "Förtroende kommunpolitiker %": "Trust in municipal politicians %",
    "Förtroende riksdagspolitiker %": "Trust in parliamentary politicians %",
    "Stroke incidens /100k": "Stroke incidence /100k",
    "Diabetes kvalitetsindex (max 100)": "Diabetes quality index (0–100)",
    "Stroke kvalitetsindex (max 100)": "Stroke quality index (0–100)",
    "Palliativ vård kvalitetsindex (max 100)": "Palliative care quality index (0–100)",
    "Patientupplevd kontinuitet primärvård %": "Patient-perceived primary care continuity %",
    "Tjocktarmscancer kvinnor /100k": "Colorectal cancer (women) /100k",
    "Tjocktarmscancer män /100k": "Colorectal cancer (men) /100k",
    "Bröstcancerfall via screening %": "Breast cancer cases via screening %",
    "Bröstcanceroperation <28 dagar %": "Breast cancer surgery <28 days %",

    # Penetration + market columns
    "Pneumokock market total SEK": "Pneumococcal market total (SEK)",

    # Regional plan keyword columns
    "Äldre": "Elderly",
    "Kronisk": "Chronic disease",
    "Tillgänglig": "Accessibility",
    "Nära vård": "Close care (nära vård)",
    "Jämlik": "Equity",
    "Primärvård": "Primary care",
    "Forskning": "Research",

    # Misc
    "Daily smoke %": "Daily smokers %",
    "Overweight %": "Overweight/obese %",
    "Antibiotic /1000": "Antibiotic Rx per 1,000",

    # Stakeholder column shortenings (already English-ish but expand)
    "RD": "Regional director (RD)",
    "RD conf": "Regional director confidence",
    "HSD": "Healthcare director (HSD)",
    "HSD conf": "HSD confidence",
    "RS ordf": "Regional council chair (RS ordförande)",
    "RS conf": "RS chair confidence",
    "HSN ordf": "Healthcare board chair (HSN ordförande)",
    "HSN conf": "HSN chair confidence",
    "LK ordf": "Drug committee chair (LK ordförande)",
    "LK conf": "LK chair confidence",
    "NT-rådet rep": "NT-rådet representative",
    "NSG rep": "NSG representative",

    # Penetration sheet headers (per capita suffixes)
    "Pfizer FSME-IMMUN /inv": "Pfizer FSME-IMMUN per capita",
    "Pfizer Prevenar /inv": "Pfizer Prevenar per capita",

    # Data dictionary descriptive cells
    "Pharma total/inv (excl tandvård)": "Pharma total cost per capita (excl. dental)",
    "Lungcancer, dödlighet 25+, åldersstand.": "Lung cancer, mortality 25+, age-standardised",
    "Hjärtvårdens kvalitetsindex SWEDEHEART": "Cardiac care quality index (SWEDEHEART)",
    "Fallolyckor 80+ åldersstand.": "Fall accidents 80+ age-standardised",
    "2024 — åldersstandardiserat": "2024 — age-standardised",
    "Pharma förmån/inv (excl tandvård)": "Pharma reimbursement per capita (excl. dental)",

    # Data sources descriptive cells
    "Folkmängd 31 dec": "Population 31 December",
    "Specialist läkare per region": "Specialist physicians per region",
    "Kolada förtida dödsfall 25-64": "Kolada premature mortality 25-64",

    # Robustness QA cells
    "Avg HC/inv 32-42k SEK": "Avg healthcare cost per capita 32-42k SEK",
}


# ============================================================================
# SUBSTRING TRANSLATIONS — applied after full-string pass for surviving fragments
# ============================================================================
# Word-boundary safe substring replacements for common Swedish fragments that
# appear inside longer English/Swedish-mixed cells.
SUBSTRING_TRANSLATIONS = [
    # (Swedish, English) — order matters: longer/more-specific first
    ("Pharma förmån/inv", "Pharma reimbursement per capita"),
    ("Förmån/rekvisition split not separable", "Reimbursement vs hospital procurement split not separable"),
    ("Förmån/rekvisition split", "Reimbursement vs hospital procurement split"),
    ("RSV-vaccin (allmän kategori)", "RSV vaccine (general category)"),
    ("Kostnad ≥ 30 SEK/inv över riksgenomsnittet (betydande cost above national average)",
     "Cost ≥ 30 SEK per capita above national average (substantial deviation)"),
    ("Fallolyckor 65-79", "Fall accidents 65-79"),
    ("(åldersstandardiserat)", "(age-standardised)"),
    ("åldersstandardiserat", "age-standardised"),
    ("(åldersstand.)", "(age-std)"),
    (" åldersstand.", " age-std"),
    ("(3-års mv)", "(3-year MA)"),
    ("(5-års mv)", "(5-year MA)"),
    (" /inv ", " per capita "),
    (" /inv\n", " per capita\n"),
    (" tandvård", " dental care"),
    (" Folkmängd ", " Population "),
    (" Folkmängd", " Population"),
    (" dödlighet ", " mortality "),
    (" dödsfall ", " deaths "),
    (" förtida ", " premature "),
    (" Lungcancer", " Lung cancer"),
    (" Bröstcancer", " Breast cancer"),
    (" Tjocktarmscancer", " Colorectal cancer"),
    (" kvinnor ", " (women) "),
    (" män ", " (men) "),
    (" kvinnor)", " (women))"),
    (" män)", " (men))"),
    (" Hjärtvårdens", " Cardiac care"),
    (" Fallolyckor", " Fall accidents"),
    (" årsarbetare", " full-time equivalent"),
    (" Specialist läkare", " Specialist physicians"),
    (" Förtroende ", " Trust in "),
    (" kommunpolitiker", " municipal politicians"),
    (" riksdagspolitiker", " parliamentary politicians"),
]


def apply_substring_translations(value):
    """Apply substring replacements to a string."""
    if not isinstance(value, str):
        return value
    for sv, en in SUBSTRING_TRANSLATIONS:
        if sv in value:
            value = value.replace(sv, en)
    return value


# ============================================================================
# SHEET RENAMES — drop "v2" suffixes, clarify
# ============================================================================
SHEET_RENAMES = {
    # Constraints: Excel sheet names ≤31 chars, no / : ? * [ ] characters.
    "Future — pop projections": "Population projections",
    "Future — life expectancy": "Life expectancy",
    "Quality + access KPIs": "Quality and access KPIs",
    "Health equity overlay": "Equity composite",
    "Cancer landscape": "Cancer burden",
    "Mortality indicators": "Mortality KPIs",
    "Infectious disease epi": "Infectious disease epi",
    "Lifestyle factors": "Lifestyle risk factors",
    "Workforce": "Healthcare workforce",
    "Wait times": "Specialist wait times",
    "Per-capita view": "Per-capita rankings",
    "Governance box per region": "Regional governance",
    "Läkemedelsregistret Rx": "Drug register Rx",
    "Rx 2024 snapshot": "Pfizer Rx footprint 2024",
    "Vaccine market share": "Vaccine market share",
    "Vaccine sales detail": "Vaccine sales detail",
    "NT-rådet status v2": "NT-rådet decisions",
    "TLV decisions": "TLV decisions",
    "Combined regulatory view": "Combined regulatory",
    "Regional plans + angles v2": "Regional plans signals",
    "Competitor pipeline": "Competitor pipeline",
    "SKR Pharma 2026": "SKR pharma 2026",
    "RCC Insights 2024-2025": "RCC insights 2024-2025",
    "Region master — confidence": "Region master confidence",
    "OPP - All products composite": "Burden x share composite",
    "OPP - Region x Product matrix": "Region x product matrix",
    "OPP - Actionability inputs": "Actionability inputs",
    "OPP - Quadrant summary": "Quadrant summary",
    "OPP - Regional archetypes": "Regional archetypes",
    "OPP - Archetype playbooks": "Archetype playbooks",
    "OPP - Portfolio plays": "Five plays",
    "OPP - Plays detail": "Plays detail",
    "OPP - Stakeholder influence": "Stakeholder influence",
    "OPP - Named individuals": "Named individuals",
    "OPP - Validation queue": "Validation queue",
    "OPP - Engagement priorities": "Engagement priorities",
    "OPP - Top per region": "Top product per region",
    "OPP - TBE penetration": "TBE penetration",
    "OPP - IPD penetration": "IPD penetration",
    "Product-Role Relevance": "Product-Role table",
    "Pfizer validation gates": "Pfizer validation gates",
    "Scenario sensitivity": "Scenario sensitivity",
    "Ibrance trajectory scenarios": "Ibrance trajectory",
    "Assumptions ledger": "Assumptions ledger",
    "Evidence ledger": "Evidence ledger",
    "Derived variables": "Derived variables",
    "Data sources": "Data sources",
    "Data Dictionary": "Data dictionary",
    "Robustness QA": "Robustness QA",
    "Region master": "Region master",
}

# Sheets to drop (legacy duplicates)
SHEETS_TO_DROP = {
    "Regional plans + angles",  # superseded by v2
}

# Logical sheet order (using NEW names after rename)
SHEET_ORDER = [
    # Reference (8)
    "README",
    "Data dictionary",
    "Data sources",
    "Robustness QA",
    "Evidence ledger",
    "Derived variables",
    "Region master confidence",
    "Assumptions ledger",
    # Region foundation (5)
    "Region master",
    "Per-capita rankings",
    "Population projections",
    "Life expectancy",
    "Healthcare workforce",
    # Disease burden + clinical (6)
    "Cancer burden",
    "Mortality KPIs",
    "Specialist wait times",
    "Quality and access KPIs",
    "Lifestyle risk factors",
    "Infectious disease epi",
    # Equity (1)
    "Equity composite",
    # Pfizer footprint (4)
    "Drug register Rx",
    "Pfizer Rx footprint 2024",
    "Vaccine market share",
    "Vaccine sales detail",
    # Regulatory (6)
    "NT-rådet decisions",
    "TLV decisions",
    "Combined regulatory",
    "Competitor pipeline",
    "SKR pharma 2026",
    "RCC insights 2024-2025",
    # Regional plans (1)
    "Regional plans signals",
    # Stakeholder layer (4)
    "Regional governance",
    "Stakeholder influence",
    "Named individuals",
    "Validation queue",
    # Strategy synthesis (13)
    "Burden x share composite",
    "TBE penetration",
    "IPD penetration",
    "Region x product matrix",
    "Actionability inputs",
    "Quadrant summary",
    "Regional archetypes",
    "Archetype playbooks",
    "Five plays",
    "Plays detail",
    "Top product per region",
    "Product-Role table",
    "Engagement priorities",
    # Scenarios (2)
    "Scenario sensitivity",
    "Ibrance trajectory",
    # Validation tracking (1)
    "Pfizer validation gates",
]


# ============================================================================
# README CONTENT
# ============================================================================
README_ROWS = [
    ("Pfizer Sweden — Regional Landscape Mapping (master workbook v23)", "title"),
    ("", None),
    ("Project: VS-2026-PFI-001", None),
    ("Vendor: Viti Science AB · Client: Pfizer Sweden, Access & Value", None),
    ("Version 23 · 2026-04-26 · client-facing release", None),
    ("", None),
    ("Purpose of this workbook", "h1"),
    ("This is the data spine of the regional landscape mapping. Fifty-one sheets covering "
     "demographics, economy, disease burden, regulatory status, governance, Pfizer's current "
     "footprint, and the analytical synthesis layer (region × product opportunity matrix, "
     "regional archetypes, five plays, stakeholder influence). Every quantitative claim in the "
     "client-facing report traces back to one of these sheets via Claim IDs in the Evidence "
     "ledger.", None),
    ("", None),
    ("How to read this workbook", "h1"),
    ("Sheets are grouped into eight sections, in the order they appear:", None),
    ("1. Reference (this README, data dictionary, data sources, robustness QA, evidence ledger, "
     "derived variables index, assumptions ledger).", None),
    ("2. Region foundation (region master with 48 demographic and economic columns, per-capita "
     "rankings, population projections to 2050, life expectancy, healthcare workforce).", None),
    ("3. Disease burden and clinical landscape (cancer burden, mortality KPIs, specialist wait "
     "times, quality and access KPIs, lifestyle risk factors, infectious disease "
     "epidemiology).", None),
    ("4. Equity (a four-component composite of unmet need across the 21 regions).", None),
    ("5. Pfizer footprint (drug register prescribing per region per product 2021–2024, "
     "vaccine market share from IQVIA, the 2024 Pfizer footprint snapshot).", None),
    ("6. Regulatory (NT-rådet decisions, TLV decisions, combined regulatory positioning, "
     "competitor pipeline, SKR pharma agreement, RCC insights, regional plan priority "
     "signals).", None),
    ("7. Stakeholder layer (regional governance, stakeholder influence scores, named "
     "individuals ranked, validation queue for stakeholders not yet at HIGH confidence).", None),
    ("8. Strategy synthesis (the 231-cell region × product opportunity matrix, archetype "
     "tagging, four-quadrant view, five plays with detail, scenario sensitivity).", None),
    ("", None),
    ("All sheets are in English for column headers. Swedish institutional names "
     "(NT-rådet, sjukvårdsregion, Läkemedelskommitté, etc.) are kept as-is because they are "
     "proper names with no equivalent English term; a glossary follows below.", None),
    ("", None),
    ("Glossary of Swedish institutional terms", "h1"),
    ("Term", "header"),  # special — header row
    # Term, Meaning, Notes
    ("Sjukvårdsregion", "Healthcare region", "One of six collaborative regions that coordinate "
     "specialist care between member regions"),
    ("NT-rådet", "National Therapeutic Council", "National advisory body issuing recommendations "
     "on new pharmaceuticals; non-binding but strongly observed"),
    ("NSG Läkemedel", "National Strategic Group for Pharmaceuticals", "National coordination "
     "body for pharma access between regions"),
    ("Läkemedelskommitté (LK)", "Drug committee", "Regional formulary committee deciding what "
     "is on regional recommendation"),
    ("LK ordförande", "Drug committee chair", "Chair of the regional drug committee"),
    ("Regiondirektör (RD)", "Regional director", "Top executive of a region"),
    ("HSD (Hälso- och sjukvårdsdirektör)", "Healthcare director", "Top healthcare executive in "
     "a region"),
    ("RS ordförande", "Regional council chair", "Political chair of the regional council"),
    ("HSN ordförande", "Healthcare board chair", "Political chair of the healthcare board"),
    ("RCC (Regionalt cancercentrum)", "Regional Cancer Centre", "Regional centre coordinating "
     "cancer care across multiple regions"),
    ("TLV", "Dental and Pharmaceutical Benefits Agency", "National authority for cost-"
     "effectiveness assessment and reimbursement"),
    ("SKR", "Swedish Association of Local Authorities and Regions", "National membership "
     "organisation for the 21 regions and 290 municipalities"),
    ("FHM (Folkhälsomyndigheten)", "Public Health Agency", "National public health authority"),
    ("SCB (Statistikmyndigheten)", "Statistics Sweden", "National statistics authority"),
    ("Kolada", "Council and Region Open Data", "Open database of regional and municipal KPIs"),
    ("Socialstyrelsen", "National Board of Health and Welfare", "National health regulator; "
     "publishes the Drug Register (Läkemedelsregistret) and Patient Register"),
    ("Läkemedelsregistret", "Prescribed Drug Register", "National prescription drug register "
     "covering all dispensed prescriptions"),
    ("Avvakta", "Await", "NT-rådet status meaning a recommendation is pending further analysis"),
    ("Rekommendation", "Recommendation", "NT-rådet positive recommendation status"),
    ("Nationellt avtal", "National agreement", "NT-rådet status indicating a managed entry "
     "agreement is in place"),
    ("BRP (Bruttoregionalprodukt)", "Gross Regional Product (GRP)", "Region-level equivalent "
     "of GDP"),
    ("", None),
    ("Confidence framework", "h1"),
    ("Every quantitative claim in this workbook carries one of four confidence tags:", None),
    ("• Observed: directly from a primary source (SCB, Kolada, IQVIA, Socialstyrelsen, etc.) "
     "with no transformation beyond aggregation.", None),
    ("• Modeled: calculated using one or more author-chosen assumptions (a weight, threshold, "
     "proxy, projection). Composites and ranks fall here.", None),
    ("• Hypothesis: a causal or strategic interpretation of a pattern, not directly tested.", None),
    ("• Needs Pfizer validation: depends on Pfizer-internal data; combined with one of the "
     "other three.", None),
    ("", None),
    ("The Evidence ledger sheet records 51 specific claims with Claim IDs. The Derived "
     "variables index documents every score, rank, and composite construction. The "
     "Assumptions ledger records every modelling assumption with its impact on outputs.", None),
    ("", None),
    ("Data freshness", "h1"),
    ("Demographics, economy, mortality: SCB and Kolada 2024 (latest available).", None),
    ("Pfizer Rx footprint: Socialstyrelsen Läkemedelsregistret 2021–2024.", None),
    ("Vaccine market share: IQVIA April 2026 extract.", None),
    ("Regulatory status (NT-rådet, TLV): refreshed against samverkanlakemedel.se on "
     "2026-04-25.", None),
    ("Stakeholders: regional websites and samverkanlakemedel.se, fact-checked on 2026-04-25 "
     "(87 of 105 leadership slots at HIGH confidence; the remainder are in the validation "
     "queue and are not used as named priority contacts in any client-facing material).", None),
    ("", None),
    ("Annual refresh", "h1"),
    ("The data pipeline is automated where possible: Playwright headless browser for the Drug "
     "register, PxWeb and JSON APIs for SCB and Kolada, programmatic PDF parsing for regional "
     "plans, web fetch for stakeholder verification. The same methodology re-run a year from "
     "now produces year-over-year deltas that mean what they appear to mean.", None),
    ("", None),
    ("Contact", "h1"),
    ("For questions about a specific number, claim, or recommendation, reference the relevant "
     "Claim ID from the Evidence ledger. The full client report (02_REGIONAL_MAPPING_REPORT) "
     "is the narrative companion to this workbook.", None),
]


# ============================================================================
# CORE TRANSFORMATION
# ============================================================================
def translate_cell_value(value):
    """Apply translation dictionary to a cell value if it's a string."""
    if not isinstance(value, str):
        return value
    # Direct full-string match
    if value in TRANSLATIONS:
        return TRANSLATIONS[value]
    # Try stripped match
    stripped = value.strip()
    if stripped in TRANSLATIONS:
        return TRANSLATIONS[stripped]
    return value


def translate_sheet(ws):
    """Apply translations to all string cells in a sheet (full-match then substring)."""
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                # Full-string match first
                new = translate_cell_value(cell.value)
                # Then substring fragments
                new = apply_substring_translations(new)
                if new != cell.value:
                    cell.value = new


def rebuild_readme(wb):
    """Replace the README sheet content entirely with the new public-facing version."""
    if "README" in wb.sheetnames:
        del wb["README"]
    ws = wb.create_sheet("README", 0)

    # Styles
    title_font = Font(name="Calibri", size=18, bold=True, color="003F7F")
    h1_font = Font(name="Calibri", size=12, bold=True, color="003F7F")
    body_font = Font(name="Calibri", size=11)
    table_header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    table_header_fill = PatternFill(start_color="003F7F", end_color="003F7F", fill_type="solid")
    table_body_font = Font(name="Calibri", size=10)
    wrap = Alignment(wrap_text=True, vertical="top")
    border_thin = Border(
        left=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF"),
        top=Side(style="thin", color="BFBFBF"),
        bottom=Side(style="thin", color="BFBFBF"),
    )

    # Column widths
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 70

    # Build the rows
    in_glossary = False
    for row_data in README_ROWS:
        text, kind = row_data if len(row_data) == 2 else (row_data[0], None)

        if kind == "title":
            ws.append([text])
            cell = ws.cell(row=ws.max_row, column=1)
            cell.font = title_font
            ws.row_dimensions[ws.max_row].height = 28
        elif kind == "h1":
            ws.append([text])
            cell = ws.cell(row=ws.max_row, column=1)
            cell.font = h1_font
            ws.row_dimensions[ws.max_row].height = 22
        elif kind == "header":
            # Glossary table header — three columns
            ws.append(["Swedish term", "English equivalent", "Notes"])
            for col in range(1, 4):
                c = ws.cell(row=ws.max_row, column=col)
                c.font = table_header_font
                c.fill = table_header_fill
                c.alignment = wrap
                c.border = border_thin
            in_glossary = True
        elif in_glossary and isinstance(row_data, tuple) and len(row_data) >= 3:
            # Glossary row
            term, meaning, notes = row_data[0], row_data[1], row_data[2] if len(row_data) > 2 else ""
            ws.append([term, meaning, notes])
            for col in range(1, 4):
                c = ws.cell(row=ws.max_row, column=col)
                c.font = table_body_font
                c.alignment = wrap
                c.border = border_thin
        else:
            ws.append([text])
            cell = ws.cell(row=ws.max_row, column=1)
            cell.font = body_font
            cell.alignment = wrap
            if text == "":
                in_glossary = False  # blank row exits glossary
            elif text and len(text) > 80:
                # Long body paragraph — span and wrap
                ws.merge_cells(start_row=ws.max_row, start_column=1,
                               end_row=ws.max_row, end_column=3)
                ws.row_dimensions[ws.max_row].height = max(15, len(text) // 12)


# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"Loading {SRC.name}...")
    wb = openpyxl.load_workbook(SRC)
    print(f"  {len(wb.sheetnames)} sheets loaded")

    # 1. Drop legacy sheets
    for name in SHEETS_TO_DROP:
        if name in wb.sheetnames:
            del wb[name]
            print(f"  dropped: {name}")

    # 2. Translate every string cell across every sheet
    print("Translating Swedish content...")
    for sheet_name in wb.sheetnames:
        translate_sheet(wb[sheet_name])

    # 3. Rename sheets — two-pass via temp names to avoid case-insensitive conflicts.
    # openpyxl treats sheet names case-insensitively for uniqueness, so renaming
    # "Data Dictionary" -> "Data dictionary" would otherwise auto-suffix as "Data dictionary1".
    print("Renaming sheets...")
    pending = [(old, new) for old, new in SHEET_RENAMES.items()
               if old in wb.sheetnames and old != new]
    for i, (old, _) in enumerate(pending):
        wb[old].title = f"__TMP_{i}__"
    for i, (_, new) in enumerate(pending):
        wb[f"__TMP_{i}__"].title = new

    # 4. Rebuild README
    print("Rebuilding README...")
    rebuild_readme(wb)

    # 5. Reorder sheets
    print("Reordering sheets...")
    ordered = []
    for name in SHEET_ORDER:
        if name in wb.sheetnames:
            ordered.append(name)
    # Append any sheets not in the order list at the end
    for name in wb.sheetnames:
        if name not in ordered:
            ordered.append(name)
            print(f"  warning: sheet '{name}' not in expected order; appended at end")
    wb._sheets = [wb[name] for name in ordered]

    # 6. Save
    print(f"\nSaving {DST_WORK.name}...")
    wb.save(DST_WORK)
    size_mb = DST_WORK.stat().st_size / (1024 * 1024)
    print(f"  {DST_WORK} ({size_mb:.2f} MB)")

    print(f"Copying to delivery...")
    shutil.copy2(DST_WORK, DST_DELIVERY)
    print(f"  {DST_DELIVERY}")

    # 7. Final inventory
    print(f"\nFinal sheet inventory ({len(wb.sheetnames)} sheets):")
    for i, name in enumerate(wb.sheetnames, 1):
        print(f"  {i:3d}. {name}")


if __name__ == "__main__":
    main()
