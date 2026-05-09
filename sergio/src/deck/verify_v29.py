# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Verify v29 workbook integrity:
  1. All 65 v28 sheets present in v29 with same shapes (no inadvertent overwrites).
  2. 8 new AVA sheets present with expected row counts.
  3. Spot-check: Methods notes header + Sweden total in a derived sheet.
"""

from pathlib import Path
import sys
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB28 = ROOT / "delivery" / "06_master_workbook_v28.xlsx"
WB29 = ROOT / "delivery" / "06_master_workbook_v29.xlsx"

EXPECTED_AVA_SHEETS = [
    "AVA — Methods notes",
    "AVA — CDK4-6 monthly patients",
    "AVA — CDK4-6 yearly patients",
    "AVA — Migraine prevalence (pre)",
    "AVA — Migraine PWD (derived)",
    "AVA — Migraine NDU (derived)",
    "AVA — ATTR class rolling 3mo",
    "AVA — ATTR class YTD",
]

EXPECTED_DATA_ROWS = {
    "AVA — CDK4-6 monthly patients": 17_667,
    "AVA — CDK4-6 yearly patients": 1_635,
    "AVA — Migraine prevalence (pre)": 1_327,
    "AVA — Migraine PWD (derived)": 1_271,
    "AVA — Migraine NDU (derived)": 970,
    "AVA — ATTR class rolling 3mo": 10_778,
    "AVA — ATTR class YTD": 7_386,
}

print("Loading v28 + v29…")
wb28 = openpyxl.load_workbook(WB28, read_only=True, data_only=True)
wb29 = openpyxl.load_workbook(WB29, read_only=True, data_only=True)

# ----- Check 1: all v28 sheets present in v29 with same shapes ---------------
print("\n--- Check 1: v28 sheets preserved in v29 ---")
errors = []
for s in wb28.sheetnames:
    if s not in wb29.sheetnames:
        errors.append(f"MISSING: '{s}'")
        continue
    a, b = wb28[s], wb29[s]
    if a.max_row != b.max_row or a.max_column != b.max_column:
        # Methods notes is expected to grow by 3 rows: a spacer plus the v29
        # pointer header/detail rows.
        if s == "Methods notes":
            if b.max_row == a.max_row + 3 and a.max_column == b.max_column:
                print(f"  ✓ '{s}': {a.max_row}x{a.max_column} → {b.max_row}x{b.max_column} (expected +3 rows)")
                continue
        if s == "Build pipeline":
            if b.max_row == a.max_row + 1 and a.max_column == b.max_column:
                print(f"  ✓ '{s}': {a.max_row}x{a.max_column} → {b.max_row}x{b.max_column} (expected +1 v29 row)")
                continue
        errors.append(f"SHAPE CHANGED: '{s}' {a.max_row}x{a.max_column} → {b.max_row}x{b.max_column}")
    else:
        pass  # silent
print(f"  v28 sheets in v29: {sum(1 for s in wb28.sheetnames if s in wb29.sheetnames)}/{len(wb28.sheetnames)}")
if errors:
    print("  ERRORS:")
    for e in errors:
        print(f"    {e}")
else:
    print("  ✓ All v28 sheets preserved")

# ----- Check 2: AVA sheets present with expected shape -----------------------
print("\n--- Check 2: AVA sheets present + row counts ---")
for s in EXPECTED_AVA_SHEETS:
    if s not in wb29.sheetnames:
        print(f"  ✗ MISSING: '{s}'")
        continue
    ws = wb29[s]
    if s in EXPECTED_DATA_ROWS:
        # Account for: title row, preamble lines, blank row, header, data
        # Approximate check: max_row should be > expected_data_rows
        expected = EXPECTED_DATA_ROWS[s]
        if ws.max_row >= expected:
            print(f"  ✓ '{s}': max_row={ws.max_row} (≥ {expected} data rows expected)")
        else:
            print(f"  ✗ '{s}': max_row={ws.max_row}, expected ≥ {expected}")
    else:
        print(f"  ✓ '{s}': max_row={ws.max_row}")

# ----- Check 3: spot-check content -------------------------------------------
print("\n--- Check 3: spot-check content ---")

# 3a. AVA — Methods notes header
ws = wb29["AVA — Methods notes"]
print(f"\n  'AVA — Methods notes' first 5 rows:")
for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
    truncated = [str(v)[:60] + ("…" if v and len(str(v)) > 60 else "") if v else "" for v in row]
    print(f"    {truncated}")

# 3b. Sweden total in Migraine PWD (derived) — pick a known month
ws = wb29["AVA — Migraine PWD (derived)"]
# Need to find a Sweden row. Header is at row title+preamble+blank+header. Let's
# scan the sheet to find Sweden×Vydura×2026-03-15.
print("\n  Sweden / Vydura / 2026-03-15 in 'AVA — Migraine PWD (derived)':")
header_row = None
for r in range(1, 12):
    row_vals = [c.value for c in ws[r]]
    if row_vals and "date" in [str(v).lower() if v else "" for v in row_vals]:
        header_row = r
        break
print(f"    header_row found at: {header_row}")
if header_row:
    headers = [c.value for c in ws[header_row]]
    print(f"    headers: {headers}")
    # Read all data rows, find target
    for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row, values_only=True):
        if row[0] == "2026-03-15" and row[1] == "Vydura" and row[2] == "Sweden":
            print(f"    target row: {row} (expected n_pwd ≈ 1548)")
            break

# 3c. Methods notes pointer at the end of v28's original Methods notes sheet
ws = wb29["Methods notes"]
print(f"\n  'Methods notes' (extended) last 4 rows:")
for r in range(max(1, ws.max_row - 3), ws.max_row + 1):
    row = [c.value for c in ws[r]]
    print(f"    row {r}: {row}")

wb28.close()
wb29.close()

print("\nVerification complete.")
if errors:
    sys.exit(1)
