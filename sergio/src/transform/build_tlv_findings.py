# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build TLV decisions structured workbook for Pfizer products."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import openpyxl
import csv
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path
from datetime import date

OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
OUT_MASTER = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master")
today = date.today().isoformat()

findings = [
    {
        "product": "Tukysa", "substance": "tucatinib",
        "tlv_status": "INCLUDED_REASONABLE",
        "tlv_decision_date": "2022-04-28",
        "subvention_type": "Generell subvention (högkostnadsskydd)",
        "indication_text": "HER2-positiv lokalt avancerad eller metastaserad bröstcancer, efter ≥2 tidigare anti-HER2-behandlingar",
        "tlv_assessment": "Reasonable cost vs benefit. Long-term effect uncertainty noted.",
        "regional_agreement": "Ja — sidoavtal mellan TLV, regioner och företag minskar behandlingskostnaden",
        "tlv_url": "https://www.tlv.se/beslut/beslut-lakemedel/generell-subvention/arkiv/2022-04-28-tukysa-ingar-i-hogkostnadsskyddet.html",
    },
    {
        "product": "Lorbrena (Lorviqua)", "substance": "lorlatinib",
        "tlv_status": "INCLUDED_GENERELL_2022",
        "tlv_decision_date": "2022-03-28 (utvidgning från 2019-09-30 begränsad)",
        "subvention_type": "Generell subvention (utvidgad från begränsad)",
        "indication_text": "ALK-positiv avancerad NSCLC; numera även för patienter som inte tidigare behandlats med ALK-hämmare",
        "tlv_assessment": "Rimlig kostnad. Kostnad per QALY 730k-980k SEK (2020 bedömning).",
        "regional_agreement": "Inte specificerat",
        "tlv_url": "https://www.tlv.se/beslut/beslut-lakemedel/generell-subvention/arkiv/2022-03-28-lorviqua-ingar-i-hogkostnadsskyddet-med-generell-subvention.html",
    },
    {
        "product": "Ibrance", "substance": "palbociclib",
        "tlv_status": "INCLUDED_REASONABLE",
        "tlv_decision_date": "(äldre beslut, ej fångat exakt datum)",
        "subvention_type": "Högkostnadsskydd",
        "indication_text": "HR+/HER2- avancerad bröstcancer, kombination med aromatashämmare eller fulvestrant",
        "tlv_assessment": "Rimlig kostnad i båda kombinationerna",
        "regional_agreement": "OBS: Region Stockholm rekommenderar konkurrent Kisqali (ribociclib, Novartis) över palbociclib av kostnadsskäl trots TLV-godkännande",
        "tlv_url": "https://www.tlv.se/lakemedel/kliniklakemedelsuppdraget/avslutade-halsoekonomiska-bedomningar.html",
    },
    {
        "product": "Talzenna", "substance": "talazoparib",
        "tlv_status": "ASSESSED",
        "tlv_decision_date": "2024 (nationellt avtal samma år)",
        "subvention_type": "Nationellt avtal (sidoavtal); NT-rådet ger ej rekommendation",
        "indication_text": "BRCA-muterad HER2- bröstcancer; även mCRPC bedömd som svår sjukdom",
        "tlv_assessment": "mCRPC bedömd som mycket allvarlig (botemedel saknas, kortare livslängd)",
        "regional_agreement": "Ja — nationellt avtal 2024-06-01 till 2026-05-31 (förlängningsalternativ till 2027-05-31)",
        "tlv_url": "https://www.tlv.se/lakemedel/kliniklakemedelsuppdraget/avslutade-halsoekonomiska-bedomningar.html",
    },
    {
        "product": "Vyndaqel", "substance": "tafamidis",
        "tlv_status": "INCLUDED_LIMITED",
        "tlv_decision_date": "2021-09-01",
        "subvention_type": "Begränsad subvention",
        "indication_text": "TTR-amyloidos med kardiomyopati (ATTRwt eller ATTRv) UTAN signifikanta amyloidos-symtom från andra organ än hjärtat",
        "tlv_assessment": "Bäst effekt vid tidiga sjukdomsstadier (NYHA klass I-II). NYHA klass III mer osäker, NYHA IV evidens saknas.",
        "regional_agreement": "Bestämmelse: endast vid hjärtsvikt-historik",
        "tlv_url": "https://www.tlv.se/download/18.4aae5b7817b8881a5ca546c6/1630501167542/bes210901_vyndaqel.pdf",
    },
    {
        "product": "Vydura", "substance": "rimegepant",
        "tlv_status": "INCLUDED_LIMITED",
        "tlv_decision_date": "2023-12-15",
        "subvention_type": "Begränsad subvention",
        "indication_text": "Akut migrän",
        "tlv_assessment": "Endast för patienter med ≥2 migränattacker per månad och som efter optimerad behandling inte fått effekt av eller inte tolererat ≥2 olika migränläkemedel (triptaner)",
        "regional_agreement": "—",
        "tlv_url": "https://www.tlv.se/beslut/beslut-lakemedel/begransad-subvention/arkiv/2023-12-15-vydura-ingar-i-hogkostnadsskyddet-med-begransning.html",
    },
    {
        "product": "Paxlovid", "substance": "nirmatrelvir + ritonavir",
        "tlv_status": "INCLUDED_GENERELL",
        "tlv_decision_date": "2022-11-21",
        "subvention_type": "Generell subvention",
        "indication_text": "COVID-19 utomhus (poliklinisk behandling) hos högriskpatienter",
        "tlv_assessment": "Hälsoekonomisk bedömning publicerad sept 2022",
        "regional_agreement": "—",
        "tlv_url": "https://www.tlv.se/beslut/beslut-lakemedel/generell-subvention/arkiv/2022-11-21-paxlovid-ingar-i-hogkostnadsskyddet.html",
    },
    {
        "product": "Abrysvo", "substance": "RSV-vaccin (prefusion-F)",
        "tlv_status": "ASSESSED_PENDING",
        "tlv_decision_date": "2024-06-18 + tilläggsanalyser 2025-09-01",
        "subvention_type": "Bedömning klar; finansiering avvaktar (FHM-process)",
        "indication_text": "RSV-vaccin för 60+ vuxna (samt graviditet)",
        "tlv_assessment": "Bedömning enligt FHM rekommendation 60+; tilläggsanalyser 2025 efter NT-rådets 'avvakta'",
        "regional_agreement": "—",
        "tlv_url": "https://www.tlv.se/lakemedelsforetag/halsoekonomiska-bedomningar-och-rapporter-kliniklakemedel/arkiv-avslutade-halsoekonomiska-bedomningar/2025-09-01-tillaggsanalyser-av-abrysvo-for-vaccinering-mot-luftvagsviruset-rsv.html",
    },
    {
        "product": "Elrexfio", "substance": "elranatamab",
        "tlv_status": "REFERENCED_NOT_DIRECT",
        "tlv_decision_date": "—",
        "subvention_type": "Nationellt avtal via NT-rådet (rekvisition)",
        "indication_text": "RRMM (4L+) — multipelt myelom",
        "tlv_assessment": "Inte separat TLV-bedömning hittad; nämnt i kontext för Sarclisa (isatuximab) som behandlingsalternativ för RRMM",
        "regional_agreement": "Ja — NT-rådets nationella avtal 2024-06-14 (2024-06-01 till 2027-01-31)",
        "tlv_url": "—",
    },
    {
        "product": "Hympavzi", "substance": "marstacimab",
        "tlv_status": "TOO_NEW",
        "tlv_decision_date": "—",
        "subvention_type": "—",
        "indication_text": "Profylax vid hemofili A/B utan inhibitorer (12+ år)",
        "tlv_assessment": "Inte ännu bedömt av TLV. FDA-godkännande 2024-10-11.",
        "regional_agreement": "—",
        "tlv_url": "—",
    },
    {
        "product": "Prevenar 20", "substance": "20-valent pneumokockvaccin",
        "tlv_status": "OUT_OF_SCOPE_FHM",
        "tlv_decision_date": "—",
        "subvention_type": "—",
        "indication_text": "Pneumokocksjukdom-prevention vuxna 65+",
        "tlv_assessment": "Vacciner för vuxenbruk hanteras via FHM-rekommendationer och regionala upphandlingar, inte via TLV-subvention",
        "regional_agreement": "—",
        "tlv_url": "—",
    },
]

fields = list(findings[0].keys())
with open(OUT_INT / "tlv_decisions_pfizer.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(findings)

# Build workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "TLV decisions"

hdr = ["Product", "Substance", "TLV Status", "Decision date", "Subvention type",
       "Indication", "TLV assessment", "Regional/national agreement", "TLV URL"]
ws.append(hdr)

header_fill = PatternFill("solid", fgColor="305496")
header_font = Font(bold=True, color="FFFFFF")
for col in range(1, len(hdr)+1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[1].height = 38

status_colors = {
    "INCLUDED_REASONABLE":   "C6EFCE",
    "INCLUDED_GENERELL":     "C6EFCE",
    "INCLUDED_GENERELL_2022":"C6EFCE",
    "INCLUDED_LIMITED":      "FFF2CC",
    "ASSESSED_PENDING":      "FCE4D6",
    "ASSESSED":              "DDEBF7",
    "REFERENCED_NOT_DIRECT": "EAD1DC",
    "TOO_NEW":               "BDD7EE",
    "OUT_OF_SCOPE_FHM":      "D9D9D9",
}
for f in findings:
    ws.append([f[k] for k in fields])

for row in range(2, ws.max_row+1):
    status = ws.cell(row=row, column=3).value
    color = status_colors.get(status, "FFFFFF")
    ws.cell(row=row, column=3).fill = PatternFill("solid", fgColor=color)

widths = [22, 22, 22, 28, 32, 50, 50, 50, 60]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "B2"
for r in range(2, ws.max_row+1):
    ws.row_dimensions[r].height = 80

# Status legend
ws2 = wb.create_sheet("Status legend")
legend = [
    ["Status", "Meaning"],
    ["INCLUDED_REASONABLE", "TLV bedömt rimlig kostnad; inkluderad i högkostnadsskydd"],
    ["INCLUDED_GENERELL", "Generell subvention (alla godkända indikationer)"],
    ["INCLUDED_GENERELL_2022", "Utvidgad till generell subvention (tidigare begränsad)"],
    ["INCLUDED_LIMITED", "Begränsad subvention (specifika patientkriterier)"],
    ["ASSESSED_PENDING", "TLV-bedömning klar men finansieringsbeslut väntar"],
    ["ASSESSED", "Bedömt med specifik observation (t.ex. svårhetsgrad)"],
    ["REFERENCED_NOT_DIRECT", "Inte direkt TLV-bedömt; refererat i andra bedömningar"],
    ["TOO_NEW", "För nytt — inte ännu hanterat av TLV"],
    ["OUT_OF_SCOPE_FHM", "Hanteras via FHM-rekommendationer, inte TLV"],
]
for row in legend: ws2.append(row)
for col in range(1, 3):
    c = ws2.cell(row=1, column=col); c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
for i,w in enumerate([24, 80], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w

# Combined NT-rådet + TLV view
ws3 = wb.create_sheet("Combined regulatory view")
ws3.append(["Product", "TLV status", "TLV date", "NT-rådet status", "Regional agreement", "Combined positioning"])
nt_lookup = {}  # Build from existing data
nt_csv = OUT_INT / "ntradet_pfizer_status.csv"
if nt_csv.exists():
    for r in csv.DictReader(open(nt_csv, encoding="utf-8")):
        # Simplify product name match
        key = r["pfizer_product"].split(" (")[0].strip()
        nt_lookup[key] = r

for f in findings:
    pname = f["product"].split(" (")[0].strip()
    nt = nt_lookup.get(pname, {})
    ws3.append([
        f["product"], f["tlv_status"], f["tlv_decision_date"],
        nt.get("nt_status", "?"),
        f["regional_agreement"][:80] if f["regional_agreement"] else "",
        f"TLV {f['tlv_status']} + NT {nt.get('nt_status','?')}",
    ])
for col in range(1, 7):
    c = ws3.cell(row=1, column=col); c.fill = header_fill; c.font = header_font
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws3.row_dimensions[1].height = 38
for i,w in enumerate([22, 22, 28, 24, 50, 40], start=1):
    ws3.column_dimensions[get_column_letter(i)].width = w
ws3.freeze_panes = "B2"

out_file = OUT_MASTER / "tlv_decisions_pfizer_v1.xlsx"
wb.save(out_file)

print(f"Saved: {out_file}")
print(f"Sheets: {wb.sheetnames}")
print()
print("TLV status distribution:")
from collections import Counter
counts = Counter(f["tlv_status"] for f in findings)
for status, n in counts.most_common():
    print(f"  {status:<25} {n}")
