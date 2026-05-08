# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Parse downloaded Läkemedelsregistret CSVs into consolidated per-region × ATC × year table."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv, json
from pathlib import Path

RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

ATCS = {
    "L01EF01": "Ibrance (palbociklib) — HR+/HER2- BC",
    "N07XX08": "Vyndaqel (tafamidis) — ATTR-CM",
    "L01XK04": "Talzenna (talazoparib) — BRCA-mut HER2- BC",
    "L01ED04": "Lorbrena/Lorviqua (lorlatinib) — ALK+ NSCLC",
    "L01EH03": "Tukysa (tucatinib) — HER2+ BC + brain mets",
    "N02CD06": "Vydura (rimegepant) — acute migraine",
    "J05AE30": "Paxlovid (nirmatrelvir/ritonavir) — COVID-19",
}

REGION_MAP = {
    "Stockholms län": ("01", "Stockholm"),
    "Uppsala län": ("03", "Uppsala"),
    "Södermanlands län": ("04", "Sörmland"),
    "Östergötlands län": ("05", "Östergötland"),
    "Jönköpings län": ("06", "Jönköping"),
    "Kronobergs län": ("07", "Kronoberg"),
    "Kalmar län": ("08", "Kalmar"),
    "Gotlands län": ("09", "Gotland"),
    "Blekinge län": ("10", "Blekinge"),
    "Skåne län": ("12", "Skåne"),
    "Hallands län": ("13", "Halland"),
    "Västra Götalands län": ("14", "Västra Götaland"),
    "Värmlands län": ("17", "Värmland"),
    "Örebro län": ("18", "Örebro"),
    "Västmanlands län": ("19", "Västmanland"),
    "Dalarnas län": ("20", "Dalarna"),
    "Gävleborgs län": ("21", "Gävleborg"),
    "Västernorrlands län": ("22", "Västernorrland"),
    "Jämtlands län": ("23", "Jämtland Härjedalen"),
    "Västerbottens län": ("24", "Västerbotten"),
    "Norrbottens län": ("25", "Norrbotten"),
}

all_data = {}  # atc → region_code → {year: count}
for atc in ATCS:
    csv_path = RAW / f"sos_rx_{atc}_20260424.csv"
    if not csv_path.exists():
        print(f"[MISSING] {atc}")
        continue
    text = csv_path.read_text(encoding="utf-8-sig")  # handle BOM
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("Socialstyrelsens") and not l.startswith("Läkemedelsstatistik")]
    reader = csv.reader(lines, delimiter=";")
    hdr = next(reader)
    # Expected: ['Mått', 'Läkemedel', 'Region', 'Kön', 'Ålder', '2021', '2022', '2023', '2024']
    year_cols = [c for c in hdr if c.isdigit()]
    data_per_region = {}
    for row in reader:
        if len(row) < len(hdr): continue
        region_raw = row[2]
        if region_raw not in REGION_MAP: continue
        code, name = REGION_MAP[region_raw]
        vals = {}
        for i, yr in enumerate(year_cols):
            v = row[5 + i].strip()
            # Suppressed values appear as ".." or similar
            try:
                vals[yr] = int(v) if v.isdigit() else 0
            except:
                vals[yr] = None
        data_per_region[code] = {"region_name": name, **vals}
    all_data[atc] = data_per_region
    total_24 = sum(d.get("2024", 0) or 0 for d in data_per_region.values())
    print(f"[{atc}] {ATCS[atc]}: total patients 2024 = {total_24}")

# Save consolidated JSON
out_json = INT / "lakemedelsregistret_parsed.json"
out_json.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSaved: {out_json}")

# Build wide CSV: region × (product × year)
wide_rows = []
sorted_codes = sorted({c for atc_data in all_data.values() for c in atc_data})
for code in sorted_codes:
    row = {"region_code": code}
    # region_name from first available ATC data
    for atc, atc_data in all_data.items():
        if code in atc_data:
            row["region"] = atc_data[code]["region_name"]
            break
    for atc in ATCS:
        for yr in ["2021","2022","2023","2024"]:
            v = (all_data.get(atc, {}).get(code, {}).get(yr))
            row[f"{atc}_{yr}"] = v
    wide_rows.append(row)

out_csv = INT / "lakemedelsregistret_patients_by_region_2021_2024.csv"
headers = ["region_code", "region"] + [f"{atc}_{yr}" for atc in ATCS for yr in ["2021","2022","2023","2024"]]
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader()
    for row in wide_rows: w.writerow(row)
print(f"Saved wide CSV: {out_csv}")

# Quick-look summary table — 2024 patients per region per product
print("\n=== 2024 Patient counts per region per Pfizer product ===")
print(f"  {'Region':<22} | " + " | ".join(f'{atc[:8]:>8}' for atc in ATCS))
print("-"*180)
for code in sorted_codes:
    region_name = next((d[code]["region_name"] for d in all_data.values() if code in d), "?")
    vals = [all_data.get(atc, {}).get(code, {}).get("2024") for atc in ATCS]
    cells = [f'{v:>8}' if v is not None else f'{"-":>8}' for v in vals]
    print(f"  {region_name:<22} | " + " | ".join(cells))
