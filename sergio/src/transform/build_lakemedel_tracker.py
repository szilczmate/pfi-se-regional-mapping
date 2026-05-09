# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build a tracker workbook for the manual Socialstyrelsen Läkemedelsregistret exports."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path

OUT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master")

ATC_TO_PULL = [
    # (ATC, Pfizer product, indication, priority, why_in_register)
    ("L01EF01", "Ibrance",   "HR+/HER2- BC, advanced",        "High",   "Oral, Rx-dispensed"),
    ("N07XX08", "Vyndaqel",  "ATTR-CM",                       "High",   "Oral, Rx-dispensed; NT-rådet relevant"),
    ("L01XK04", "Talzenna",  "BRCA-mut HER2- BC",             "Medium", "Oral, Rx-dispensed (PARP inhibitor class)"),
    ("L01ED04", "Lorbrena",  "ALK+ NSCLC, post-1L",           "Medium", "Oral, Rx-dispensed"),
    ("L01EH03", "Tukysa",    "HER2+ BC w/ brain mets",        "Medium", "Oral, Rx-dispensed"),
    ("N02CD06", "Vydura",    "Migraine, acute",               "Lower",  "Oral, Rx-dispensed"),
    ("J05AE30", "Paxlovid",  "COVID-19 outpatient",           "Lower",  "Oral, Rx-dispensed"),
]

NOT_IN_REGISTER = [
    ("(brand)",  "Hympavzi",  "Haemophilia A/B",   "Subcut, hospital-admin (rekvisition); NOT in Rx register; IQVIA or Concise needed"),
    ("L01FX25",  "Elrexfio",  "RRMM 4L+",          "Subcut, hospital-admin (rekvisition); NOT in Rx register; IQVIA or Concise needed"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Pull tracker"

hdr_fill = PatternFill("solid", fgColor="305496")
hdr_font = Font(bold=True, color="FFFFFF")

ws.append([
    "ATC code", "Pfizer product", "Indication", "Priority",
    "Why this is in the Rx register",
    "Pulled? (Yes/No)", "Pull date", "File saved as", "Analyst", "Notes"
])
for atc, prod, ind, prio, why in ATC_TO_PULL:
    ws.append([atc, prod, ind, prio, why, "No", "", f"sos_rx_{atc}_YYYYMMDD.xlsx", "", ""])

# Style header
for col in range(1, 11):
    c = ws.cell(row=1, column=col)
    c.fill = hdr_fill; c.font = hdr_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[1].height = 38

for i, w in enumerate([12, 14, 32, 10, 38, 14, 12, 30, 14, 30], start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "B2"

# Sheet 2: Out of scope (hospital-administered)
ws2 = wb.create_sheet("Not in Rx register")
ws2.append(["ATC", "Product", "Indication", "Why excluded"])
for atc, prod, ind, why in NOT_IN_REGISTER:
    ws2.append([atc, prod, ind, why])
for col in range(1, 5):
    c = ws2.cell(row=1, column=col); c.fill = hdr_fill; c.font = hdr_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
for i, w in enumerate([12, 14, 28, 80], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 38

# Sheet 3: Procedure
ws3 = wb.create_sheet("Manual export procedure")
proc = [
    ["Manual export from Socialstyrelsen Läkemedelsregistret"],
    [""],
    ["Why manual: Statistikdatabasen has no public API or stable URL pattern (form posts via JS)."],
    ["Time per export: 5-10 min. Total for 7 ATCs: ~1 hour."],
    [""],
    ["Steps:"],
    ["  1. Open https://sdb.socialstyrelsen.se/if_lak/val.aspx"],
    ["  2. Select Tabellinnehåll: tick 'Antal patienter', 'Antal expeditioner', 'DDD per 1000 inv/dag'"],
    ["  3. Select ATC-kod: enter the ATC for the product (e.g., L01EF01 for Ibrance)"],
    ["  4. Select Region: tick 'Alla län' (all 21 regions)"],
    ["  5. Select Ålder: 'Totalt'"],
    ["  6. Select Kön: 'Båda könen'"],
    ["  7. Select År: 2021, 2022, 2023, 2024 (latest 4 years)"],
    ["  8. Click 'Visa resultat'"],
    ["  9. Click Excel export icon at top of results table"],
    ["  10. Save as working/data/raw/sos_rx_<ATC>_<YYYYMMDD>.xlsx"],
    ["  11. Update this tracker: mark 'Pulled? Yes', add date and filename"],
    [""],
    ["Privacy / suppression note:"],
    ["  Small numbers (typically < 5 patients) are suppressed in SoS output."],
    ["  Expect suppression for rare indications and small regions in combination."],
    ["  Especially relevant for Lorbrena (ALK+ NSCLC) and Tukysa (HER2+ BC w/ brain mets)."],
    [""],
    ["Once exports arrive, run: python working/notebooks/parse_sos_rx_export.py"],
    ["(parser to be built when first file arrives — script template ready)"],
]
for row in proc:
    ws3.append(row)
ws3.column_dimensions["A"].width = 110
ws3.cell(row=1, column=1).font = Font(bold=True, size=14)

out_file = OUT / "lakemedelsregistret_pull_tracker.xlsx"
wb.save(out_file)
print(f"Saved: {out_file}")
print(f"Sheets: {wb.sheetnames}")
print(f"ATCs to pull: {len(ATC_TO_PULL)} (priority order)")
print(f"ATCs NOT pullable: {len(NOT_IN_REGISTER)} (hospital-administered)")
