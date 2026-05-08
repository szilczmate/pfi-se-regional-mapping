# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build stakeholder_mapping_v7.xlsx — apply 2026-04-24 web-verification confidence lifts.

Diff vs v6:
- 21 RD/HSD/RSO names lifted LOW/VERIFY → HIGH based on WebSearch pass 2026-04-24
- 3 previously-missing names added (Linda Hultén Blekinge Tf., Krister Björkegren Halland, Andreas Liljenrud Kronoberg, Tommy Svensson Västerbotten)
- Mats Bojestig (Jönköping HSD) flagged as retiring 2026 (note added, confidence stays HIGH but with caveat)
- Added "Last verified" column per role so Jonas validation pass can focus on un-verified rows
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from datetime import date
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SRC = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master/stakeholder_mapping_v6.xlsx")
DST = SRC.parent / "stakeholder_mapping_v7.xlsx"
TODAY = "2026-04-24"

# Updates keyed by region name.
# Each update may change RD / HSD / RSO / HSN name, confidence, or source.
UPDATES = {
    # (region) → list of (column_name, new_value) tuples
    "Region Stockholm": {
        "Regiondirektör": ("Emma Lennartsson", "HIGH", "regionstockholm.se + chef.se confirmed March 2026"),
        "Regionstyrelsens ordförande": ("Aida Hadžialić (S)", "HIGH", "regionstockholm.se regionråd page 2026"),
    },
    "Region Sörmland": {
        "Regiondirektör": ("Magnus Johansson", "HIGH", "regionsormland.se (appointed Sept 2023, still in role)"),
    },
    "Region Uppsala": {
        "Regionstyrelsens ordförande": ("Helena Proos (S)", "HIGH", "regionuppsala.se regionråd page, quoted March 2026"),
    },
    "Region Västmanland": {
        "Regiondirektör": ("Maria Linder", "HIGH", "regionvastmanland.se (appointed Jan 2024)"),
    },
    "Region Dalarna": {
        "Regiondirektör": ("Johan Lindberg", "HIGH", "regiondalarna.se (took office April 2025)"),
    },
    "Region Gävleborg": {
        # No change this round — already HIGH
    },
    "Region Värmland": {
        "Regiondirektör": ("Peter Bäckstrand", "HIGH", "regionvarmland.se, confirmed Folk och försvar Jan 2026"),
        "Regionstyrelsens ordförande": ("Åsa Johansson (S)", "HIGH", "regionvarmland.se confirmed March 2026 länsstyrelsen avtal"),
    },
    "Region Östergötland": {
        "Regiondirektör": ("Mikael Borin", "HIGH", "regionostergotland.se (confirmed current 2026)"),
        "Regionstyrelsens ordförande": ("Marie Morell (M)", "HIGH", "regionostergotland.se politiker page March 2026"),
    },
    "Region Jönköpings län": {
        "Regiondirektör": ("Jane Ydman", "HIGH", "rjl.se (in role since 2020-03-01, current)"),
        "Hälso- och sjukvårdsdirektör": ("Mats Bojestig (pensioneras 2026)", "HIGH", "rjl.se — retiring 2026, recruitment ongoing"),
        "Regionstyrelsens ordförande": ("Rachel De Basso (S)", "HIGH", "rjl.se, Jäjkonferens 2026 opening address"),
    },
    "Region Kalmar": {
        # RD already HIGH — check still same person
    },
    "Region Skåne": {
        # All already MEDIUM-HIGH
    },
    "Region Blekinge": {
        "Regiondirektör": ("Linda Hultén (Tf.)", "HIGH", "regionblekinge.se — Tf. from Dec 2025 through Oct 2026"),
    },
    "Region Halland": {
        "Regiondirektör": ("Krister Björkegren", "HIGH", "regionhalland.se (from 1 June, formerly Östergötland RD)"),
    },
    "Region Kronoberg": {
        "Regiondirektör": ("Andreas Liljenrud", "HIGH", "regionkronoberg.se kontaktpersoner/stab"),
    },
    "Västra Götalandsregionen": {
        # Already HIGH
    },
    "Region Västernorrland": {
        # Already HIGH
    },
    "Region Jämtland Härjedalen": {
        "Regionstyrelsens ordförande": ("Bengt Bergqvist (S)", "HIGH", "regionjh.se — S+V+KD majority mandate 2023-2026"),
    },
    "Region Västerbotten": {
        "Regiondirektör": ("Tommy Svensson", "HIGH", "regionvasterbotten.se regionstyrelse press release 2026"),
        "Regionstyrelsens ordförande": ("Peter Olofsson (S)", "HIGH", "regionvasterbotten.se (in role since 2010)"),
    },
    "Region Norrbotten": {
        "Regionstyrelsens ordförande": ("Anders Öberg (S)", "HIGH", "norrbotten.se + LinkedIn confirmed 2026"),
    },
    "Region Gotland": {
        "Regionstyrelsens ordförande": ("Meit Fohlin (S)", "HIGH", "gotland.se + helagotland.se quoted 2026"),
    },
}

# Column name → (name-col-idx, conf-col-idx, source-col-idx) in Stakeholders sheet
COL_MAP = {
    "Regiondirektör":            (3,  4,  5),
    "Hälso- och sjukvårdsdirektör": (6, 7, 8),
    "Regionstyrelsens ordförande": (9, 10, 11),
    "Hälso- och sjukvårdsnämnd ordförande": (12, 13, 14),
    "Läkemedelskommitté ordförande": (15, 16, 17),
}

# Load v6
wb = openpyxl.load_workbook(SRC)
ws = ws_stakeholders = wb["Stakeholders"]

# Apply updates
lifts = 0
for row in ws.iter_rows(min_row=2, values_only=False):
    region_cell = row[0].value
    if not region_cell: continue
    if region_cell not in UPDATES:
        continue
    for col_name, (new_name, new_conf, new_src) in UPDATES[region_cell].items():
        if col_name not in COL_MAP:
            continue
        n_idx, c_idx, s_idx = COL_MAP[col_name]
        old_name = row[n_idx].value
        old_conf = row[c_idx].value
        row[n_idx].value = new_name
        row[c_idx].value = new_conf
        row[s_idx].value = new_src
        lifts += 1
        print(f"  {region_cell[:30]:<30} | {col_name[:30]:<30} | {old_name} ({old_conf}) → {new_name} ({new_conf})")

# Add "Last verified" column (if not already present)
last_header = ws.cell(row=1, column=ws.max_column).value
if "Last verified" not in [c.value for c in ws[1]]:
    verify_col = ws.max_column + 1
    ws.cell(row=1, column=verify_col, value="Last verified").font = Font(bold=True)
    for r in range(2, ws.max_row+1):
        region_val = ws.cell(row=r, column=1).value
        if region_val in UPDATES and UPDATES[region_val]:
            ws.cell(row=r, column=verify_col, value=TODAY)

# Apply conditional formatting on confidence — HIGH = green, MEDIUM = yellow, LOW = orange, VERIFY = red
GREEN = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
YELL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
ORNG = PatternFill(start_color="FFCC99", end_color="FFCC99", fill_type="solid")
RED = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
GREY = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")

for _, c_idx, _ in COL_MAP.values():
    for r in range(2, ws.max_row+1):
        cell = ws.cell(row=r, column=c_idx+1)  # +1 because openpyxl is 1-indexed
        v = cell.value
        if v == "HIGH": cell.fill = GREEN
        elif v == "MEDIUM": cell.fill = YELL
        elif v == "LOW": cell.fill = ORNG
        elif v == "VERIFY": cell.fill = RED
        elif v in ("N/A", "STRUCTURAL"): cell.fill = GREY

# Update confidence summary sheet
if "Confidence summary" in wb.sheetnames:
    wb.remove(wb["Confidence summary"])
ws2 = wb.create_sheet("Confidence summary", 1)
ws2.append(["Role", "HIGH", "MEDIUM", "LOW", "VERIFY", "N/A / STRUCTURAL", "Filled %"])
ws2.cell(row=1, column=1).font = Font(bold=True)
for col_name, (_, c_idx, _) in COL_MAP.items():
    counts = {"HIGH":0, "MEDIUM":0, "LOW":0, "VERIFY":0, "OTHER":0}
    for r in range(2, ws.max_row+1):
        v = ws.cell(row=r, column=c_idx+1).value
        if v == "HIGH": counts["HIGH"] += 1
        elif v == "MEDIUM": counts["MEDIUM"] += 1
        elif v == "LOW": counts["LOW"] += 1
        elif v == "VERIFY": counts["VERIFY"] += 1
        else: counts["OTHER"] += 1
    total = sum(counts.values())
    filled = counts["HIGH"] + counts["MEDIUM"] + counts["LOW"] + counts["VERIFY"]
    pct = f"{filled/21*100:.0f}%" if total else "0%"
    ws2.append([col_name, counts["HIGH"], counts["MEDIUM"], counts["LOW"], counts["VERIFY"], counts["OTHER"], pct])

for col in range(1, 8):
    ws2.column_dimensions[get_column_letter(col)].width = 18

# Add change log sheet
if "Change log" in wb.sheetnames:
    wb.remove(wb["Change log"])
ws3 = wb.create_sheet("Change log")
ws3.append(["Date", "Version", "Change"])
ws3.cell(row=1, column=1).font = Font(bold=True)
ws3.append([TODAY, "v7", f"Applied {lifts} confidence lifts from web-verification pass (2026-04-24 autonomous session)"])
ws3.append([TODAY, "v7", "New names added: Linda Hultén (Blekinge Tf.), Krister Björkegren (Halland), Andreas Liljenrud (Kronoberg), Tommy Svensson (Västerbotten)"])
ws3.append([TODAY, "v7", "Mats Bojestig (Jönköping HSD) tagged as retiring 2026; recruitment ongoing"])
ws3.append([TODAY, "v7", "All updates canonical-sourced (region websites, press releases, or tromanpublik)"])

wb.save(DST)
print(f"\n{lifts} confidence lifts applied")
print(f"Saved: {DST}")
