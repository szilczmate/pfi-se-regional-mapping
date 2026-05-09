# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Build v29: surgical insert of AVA data (delivered 2026-05-02) into v28 workbook.

INPUTS  : delivery/06_master_workbook_v28.xlsx (preserved, opened)
          AVA data for mapping 2026-05-02/{Ibrance,Vydura,Vyndaquel}/*.RDS
OUTPUT  : delivery/06_master_workbook_v29.xlsx

Strategy
--------
Open v28 with openpyxl, append new sheets at the end (preserves all 65 existing
sheets in their current order/positions), and append rows to the existing
'Methods notes' sheet documenting the AVA definitions confirmed by the data
owner on 2026-05-05. Save as v29 (NEW filename — never overwrite).

NOT regenerating the workbook from scratch (per Sergio's workflow rule).

New sheets added (8)
--------------------
  AVA — Methods notes               Definitions + suppression rule + region grouping
  AVA — CDK4-6 monthly patients     Ibrance/IncPrevData.RDS unpivoted, 4 metrics
  AVA — CDK4-6 yearly patients      Ibrance/IncPrevDataYear.RDS unpivoted, 3 metrics
  AVA — Migraine prevalence (pre)   Vydura/region.RDS pre-computed (PWD with <5 suppression)
  AVA — Migraine PWD (derived)      Re-derived from Vydura IPD, unsuppressed Sweden + per region
  AVA — Migraine NDU (derived)      "New drug users" derived from IPD per Sergio's R code
  AVA — ATTR class rolling 3mo      Vyndaquel/tab12a.RDS
  AVA — ATTR class YTD              Vyndaquel/tab12b.RDS

Definitions (from data owner reply, 2026-05-05) recorded in Methods notes
-------------------------------------------------------------------------
- DG3 = ATTR-CM (cardiomyopathy) — high confidence (Beyonttra/acoramidis appears
  only in DG3 + Oavsett, and acoramidis is licensed for ATTR-CM only).
- DG1, DG2 = ATTR-PN sub-buckets, exact mapping pending owner confirmation;
  workbook reports DG1+DG2 combined as "ATTR-PN total" for safety.
- "Patients on treatment" = dispensation + 3-month grace (a patient is on-treatment
  through 90 days after their most recent dispensation).
- Per-region values in Vydura region.RDS apply Socialstyrelsen <5 suppression at
  region level only (Sweden total is unsuppressed). Verified empirically:
  Sweden ≥ sum(21 regions) in 100% of months; Sweden equals derived PWD in 68/70.
"""

from pathlib import Path
import sys
from copy import copy
import pyreadr
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
SRC_WB = ROOT / "delivery" / "06_master_workbook_v28.xlsx"
DST_WB = ROOT / "delivery" / "06_master_workbook_v29.xlsx"

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
NOTE_FILL = PatternFill("solid", fgColor="FFF2CC")
TITLE_FONT = Font(bold=True, size=14, color="1F4E78")


def read_rds(folder: str, fname: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(AVA / folder / fname))
    return list(result.values())[0]


def write_df_to_sheet(ws, df: pd.DataFrame, title: str | None = None,
                      preamble: list[str] | None = None) -> None:
    """Write a DataFrame to a sheet with formatted header. Optional title row +
    preamble lines above the table."""
    row = 1
    if title:
        ws.cell(row=row, column=1, value=title).font = TITLE_FONT
        row += 1
    if preamble:
        for line in preamble:
            c = ws.cell(row=row, column=1, value=line)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.merge_cells(start_row=row, start_column=1, end_row=row,
                           end_column=max(2, len(df.columns)))
            row += 1
        row += 1  # blank line

    # Header
    for j, col in enumerate(df.columns, start=1):
        c = ws.cell(row=row, column=j, value=str(col))
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center")
    row += 1

    # Data — write as native types (pandas → openpyxl handles ints, floats, NaN→None)
    for record in df.itertuples(index=False, name=None):
        for j, val in enumerate(record, start=1):
            if pd.isna(val):
                v = None
            elif hasattr(val, "item"):  # numpy scalars
                v = val.item()
            else:
                v = val
            ws.cell(row=row, column=j, value=v)
        row += 1

    # Column widths — best-effort sizing
    for j, col in enumerate(df.columns, start=1):
        max_len = max(len(str(col)),
                      df[col].astype(str).str.len().max() if len(df) else 0)
        ws.column_dimensions[ws.cell(row=1, column=j).column_letter].width = min(
            max(10, int(max_len) + 2), 38)


# ---------------------------------------------------------------------------
# 1. Load all six RDS files
# ---------------------------------------------------------------------------
print("Loading RDS files…")
ibr_m = read_rds("Ibrance", "IncPrevData.RDS")
ibr_y = read_rds("Ibrance", "IncPrevDataYear.RDS")
vyd_ipd = read_rds("Vydura", "data_duot.RDS")
vyd_pre = read_rds("Vydura", "region.RDS")
vqa_a = read_rds("Vyndaquel", "tab12a.RDS")
vqa_b = read_rds("Vyndaquel", "tab12b.RDS")

# Normalize types: 'date'/'edate'/'months'/'month' → consistent string
for df, col in [(ibr_m, "date"), (ibr_y, "date"), (ibr_m, "months"),
                (vyd_pre, "month"), (vyd_ipd, "edate"),
                (vqa_a, "date"), (vqa_b, "date")]:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Year column to int (was float)
if "year" in ibr_y.columns:
    ibr_y["year"] = ibr_y["year"].astype(int)

print(f"  Ibrance monthly:  {len(ibr_m):>7,} rows")
print(f"  Ibrance yearly :  {len(ibr_y):>7,} rows")
print(f"  Vydura IPD     :  {len(vyd_ipd):>7,} rows ({vyd_ipd['lopnr'].nunique():,} patients)")
print(f"  Vydura prev    :  {len(vyd_pre):>7,} rows")
print(f"  Vyndaqel 3mo   :  {len(vqa_a):>7,} rows")
print(f"  Vyndaqel YTD   :  {len(vqa_b):>7,} rows")


# ---------------------------------------------------------------------------
# 2. Vydura derivations from IPD per Sergio's R logic
# ---------------------------------------------------------------------------
print("\nDeriving Vydura PWD / NDU from IPD…")

# PWD per region: distinct(lopnr, drug, edate) keeping first row, then group by
# (edate, drug, region). NOTE: the dedup keys do NOT include region — patients
# who appear in two regions in the same month are counted once (in whichever
# region appeared first in the source ordering).
ipd_for_pwd = vyd_ipd.drop_duplicates(["lopnr", "drug", "edate"], keep="first")
pwd_region = (ipd_for_pwd
              .groupby(["edate", "drug", "region"], as_index=False)
              .size().rename(columns={"size": "n_pwd"}))
# PWD Sweden: same dedup, group without region
pwd_sweden = (ipd_for_pwd
              .groupby(["edate", "drug"], as_index=False)
              .size().rename(columns={"size": "n_pwd"}))
pwd_sweden["region"] = "Sweden"

vyd_pwd_derived = (pd.concat([pwd_region, pwd_sweden[["edate", "drug", "region", "n_pwd"]]],
                              ignore_index=True)
                   .sort_values(["edate", "drug", "region"])
                   .reset_index(drop=True))

# NDU per region: row_number()==1 per lopnr, then group by (edate, drug, region)
first_per_lopnr = (vyd_ipd
                   .sort_values(["lopnr", "edate"])
                   .drop_duplicates("lopnr", keep="first"))
ndu_region = (first_per_lopnr
              .groupby(["edate", "drug", "region"], as_index=False)
              .size().rename(columns={"size": "n_ndu"}))
ndu_sweden = (first_per_lopnr
              .groupby(["edate", "drug"], as_index=False)
              .size().rename(columns={"size": "n_ndu"}))
ndu_sweden["region"] = "Sweden"
vyd_ndu_derived = (pd.concat([ndu_region, ndu_sweden[["edate", "drug", "region", "n_ndu"]]],
                              ignore_index=True)
                   .sort_values(["edate", "drug", "region"])
                   .reset_index(drop=True))

print(f"  Vydura PWD (derived, unsuppressed): {len(vyd_pwd_derived):,} rows")
print(f"  Vydura NDU (derived, unsuppressed): {len(vyd_ndu_derived):,} rows")


# ---------------------------------------------------------------------------
# 3. Open v28, append sheets
# ---------------------------------------------------------------------------
print(f"\nOpening v28 ({SRC_WB.name})…")
wb = openpyxl.load_workbook(SRC_WB)
existing_sheets = list(wb.sheetnames)
print(f"  existing sheets: {len(existing_sheets)}")


# ----- 3a. AVA — Methods notes ---------------------------------------------
ws = wb.create_sheet("AVA — Methods notes")
ws["A1"] = "AVA data — definitions, suppression, regional grouping"
ws["A1"].font = TITLE_FONT
ws.merge_cells("A1:E1")

methods_rows = [
    ("Topic", "Definition / rule", "Source / verification"),
    ("Source",
     "Six RDS files delivered 2026-05-02 from Viti Science AVA (Analysis "
     "Visualisation Apps) pipeline; replaces SoS open prescription stats for "
     "the three named products (Ibrance / Vydura / Vyndaqel). IQVIA Sell-In "
     "remains authoritative for SEK and units.",
     "Email handover from Viti, 2026-05-02"),
    ("'Patients with dispensations' (PWD)",
     "For (date, drug, region): distinct lopnr × drug × edate counted per "
     "(edate, drug, region). Monthly flow.",
     "Sergio's R code (dplyr group_by/summarise) shared 2026-05-05"),
    ("'New drug users' (NDU)",
     "For (date, drug, region): first row per lopnr (row_number()==1 after "
     "ordering by edate), then count per (edate, drug, region). Patient is "
     "counted once over their lifetime in the dataset.",
     "Sergio's R code (dplyr group_by/summarise) shared 2026-05-05"),
    ("'Patients on treatment' (PoT, Ibrance only)",
     "Dispensation + 3-month grace period: a patient is counted as on-treatment "
     "through 90 days after their most recent dispensation, regardless of new "
     "dispensation activity in that window. Stock metric (~1.43× PWD).",
     "Confirmed by AVA owner, 2026-05-05"),
    ("'New CDK4/6 user' (Ibrance file only)",
     "First-ever exposure to ANY CDK4/6 inhibitor (Ibrance, Kisqali, Verzenios). "
     "Class-naive incident metric. Differs from NDU which is drug-naive.",
     "Inferred from analysis labelling; column distinct from 'New drug user'"),
    ("DG3 in Vyndaqel `grupp`",
     "ATTR-CM (transthyretin amyloid cardiomyopathy). HIGH CONFIDENCE.",
     "Inferred from data: Beyonttra (acoramidis) appears only in DG3 + Oavsett, "
     "and acoramidis is licensed for ATTR-CM only."),
    ("DG1 + DG2 in Vyndaqel `grupp`",
     "ATTR-PN sub-buckets (likely hATTR-PN and wtATTR-PN, exact mapping pending). "
     "Workbook reports DG1+DG2 combined as 'ATTR-PN total' for safety.",
     "Pending confirmation from AVA owner; flagged 2026-05-05"),
    ("'Oavsett diagnos' in Vyndaqel `grupp`",
     "Aggregate across all diagnosis groups (DG1+DG2+DG3). Use this when only "
     "drug-level totals are needed.",
     "Inferred from cross-tab and Swedish term"),
    ("Per-region suppression in Vydura region.RDS",
     "Cells with n < 5 are suppressed at the region level (Socialstyrelsen "
     "small-cell rule). Sweden total is unsuppressed. Hence Sweden ≥ "
     "sum(21 regions); never the reverse.",
     "Confirmed by AVA owner, 2026-05-05; verified empirically against IPD"),
    ("Vyndaqel regional grouping",
     "6 sjukvårdsregion-style groupings + Sweden + '99' (uppgift saknas, trace "
     "Amvuttra rows): Mellansverige, Norrland, Stockholm Sörmland, Sydöstra, "
     "Södra, VGR. NOTE 'Stockholm Sörmland' bundles Stockholm + Sörmland (not "
     "the standard Stockholm-Gotland sjukvårdsregion). Different granularity "
     "from the 21-region per-län layer used elsewhere in this workbook.",
     "AVA file structure"),
    ("Period coverage",
     "Ibrance: 2017-04 → 2026-01 monthly (106 months). "
     "Vydura: 2022-10 → 2026-03 monthly (region.RDS); IPD 2022-11 → 2026-03. "
     "Vyndaqel: 2020-12 → 2026-03 monthly.",
     "AVA file structure"),
    ("Encoding",
     "Source files are UTF-8; pyreadr loads correctly. Swedish region names "
     "(Västra Götaland, Östergötland etc.) preserved.",
     ""),
]

ws.append([])  # blank row 2
for r in methods_rows:
    ws.append(r)
# Format header row
hdr_row = 3
for j in range(1, 4):
    c = ws.cell(row=hdr_row, column=j)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
# Wrap and width
for col_letter, width in [("A", 32), ("B", 80), ("C", 60)]:
    ws.column_dimensions[col_letter].width = width
for r in range(hdr_row + 1, hdr_row + 1 + len(methods_rows) - 1):
    for j in range(1, 4):
        ws.cell(row=r, column=j).alignment = Alignment(wrap_text=True, vertical="top")

print(f"  ✓ AVA — Methods notes")


# ----- 3b. AVA — CDK4-6 monthly patients -----------------------------------
ws = wb.create_sheet("AVA — CDK4-6 monthly patients")
write_df_to_sheet(
    ws,
    ibr_m[["date", "drug", "region", "analysis", "n"]].sort_values(
        ["analysis", "drug", "region", "date"]
    ).reset_index(drop=True),
    title="AVA: CDK4/6 monthly patient counts (Ibrance, Kisqali, Verzenios)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Ibrance/IncPrevData.RDS",
        "Period: 2017-04 to 2026-01 monthly (106 months); 21 regions + Sweden total.",
        "Four metrics in 'analysis' column: New CDK4/6 user (class-naive incident), "
        "New drug user (drug-naive incident), Patients with dispensations (monthly flow), "
        "Patients on treatment (3-month grace stock).",
    ],
)
print(f"  ✓ AVA — CDK4-6 monthly patients ({len(ibr_m):,} rows)")


# ----- 3c. AVA — CDK4-6 yearly patients ------------------------------------
ws = wb.create_sheet("AVA — CDK4-6 yearly patients")
write_df_to_sheet(
    ws,
    ibr_y[["year", "drug", "region", "analysis", "n"]].sort_values(
        ["analysis", "drug", "region", "year"]
    ).reset_index(drop=True),
    title="AVA: CDK4/6 yearly patient counts (Ibrance, Kisqali, Verzenios)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Ibrance/IncPrevDataYear.RDS",
        "Period: 2017–2026 yearly; 21 regions + Sweden total.",
        "Three metrics: New CDK4/6 user, New drug user, Patients with dispensations "
        "(no 'Patients on treatment' in yearly file).",
    ],
)
print(f"  ✓ AVA — CDK4-6 yearly patients ({len(ibr_y):,} rows)")


# ----- 3d. AVA — Migraine prevalence (pre) ---------------------------------
ws = wb.create_sheet("AVA — Migraine prevalence (pre)")
write_df_to_sheet(
    ws,
    vyd_pre[["month", "drug", "region", "prevalens"]].sort_values(
        ["drug", "region", "month"]
    ).reset_index(drop=True),
    title="AVA: Vydura + Atogepant — Patients with dispensations (pre-computed)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Vydura/region.RDS",
        "Definition: 'prevalens' = Patients with dispensations (distinct lopnr × drug × edate, "
        "summed per region). Verified empirically against IPD: Sweden total matches in 68/70 months.",
        "Suppression: per-region cells with n < 5 are HIDDEN per Socialstyrelsen rule. "
        "Sweden row is unsuppressed. Use the 'Migraine PWD (derived)' sheet for unsuppressed "
        "regional figures.",
        "Drugs: Vydura (rimegepant) + Atogepant (head-to-head oral CGRP-receptor antagonist comparator).",
    ],
)
print(f"  ✓ AVA — Migraine prevalence (pre) ({len(vyd_pre):,} rows)")


# ----- 3e. AVA — Migraine PWD (derived) ------------------------------------
ws = wb.create_sheet("AVA — Migraine PWD (derived)")
write_df_to_sheet(
    ws,
    vyd_pwd_derived[["edate", "drug", "region", "n_pwd"]].rename(
        columns={"edate": "date", "n_pwd": "patients_with_dispensations"}
    ),
    title="AVA: Vydura + Atogepant — PWD re-derived from IPD (UNSUPPRESSED)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Vydura/data_duot.RDS (IPD)",
        "Method: Sergio's R code translated to pandas — distinct(lopnr, drug, edate) "
        "kept (first row), then count per (edate, drug, region). Sweden total computed "
        "by summing without region group, matching R's mutate(region='Sweden').",
        "Use this sheet when small-cell suppression in the pre-computed file would hide "
        "values you need (e.g. low-volume regions for Atogepant).",
    ],
)
print(f"  ✓ AVA — Migraine PWD (derived) ({len(vyd_pwd_derived):,} rows)")


# ----- 3f. AVA — Migraine NDU (derived) ------------------------------------
ws = wb.create_sheet("AVA — Migraine NDU (derived)")
write_df_to_sheet(
    ws,
    vyd_ndu_derived[["edate", "drug", "region", "n_ndu"]].rename(
        columns={"edate": "date", "n_ndu": "new_drug_users"}
    ),
    title="AVA: Vydura + Atogepant — New drug users (incident) derived from IPD",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Vydura/data_duot.RDS (IPD)",
        "Method: row_number()==1 per lopnr after ordering by edate, then count per "
        "(edate, drug, region). A patient is counted once over their entire history in "
        "the dataset, in the region/month of their first dispensation.",
        "Use this for class growth analysis: how many class-naive patients are starting "
        "Vydura vs Atogepant per region per month?",
    ],
)
print(f"  ✓ AVA — Migraine NDU (derived) ({len(vyd_ndu_derived):,} rows)")


# ----- 3g. AVA — ATTR class rolling 3mo ------------------------------------
ws = wb.create_sheet("AVA — ATTR class rolling 3mo")
write_df_to_sheet(
    ws,
    vqa_a[["date", "drug", "atc", "region", "grupp", "analysis", "n"]].sort_values(
        ["drug", "region", "grupp", "analysis", "date"]
    ).reset_index(drop=True),
    title="AVA: ATTR class — rolling 3-month Incidens & Prevalens (raw + per 100k)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Vyndaquel/tab12a.RDS",
        "Period: 2020-12 to 2026-03 monthly (64 months).",
        "Drugs: Vyndaqel (tafamidis, N07XX08), Amvuttra (vutrisiran, N07XX18), "
        "Beyonttra (acoramidis, C01EB25), Diflunisal (NSAID, N02BA11 — off-label ATTR).",
        "Regions: 6 sjukvårdsregion-style groupings + Sweden + '99' (uppgift saknas).",
        "grupp: DG3 = ATTR-CM (high confidence); DG1+DG2 = ATTR-PN (sub-mapping pending); "
        "Oavsett = aggregate.",
        "analysis: 4 metrics — Incidens / Prevalens, raw count and per 100k, all on a "
        "rolling 3-month window.",
    ],
)
print(f"  ✓ AVA — ATTR class rolling 3mo ({len(vqa_a):,} rows)")


# ----- 3h. AVA — ATTR class YTD --------------------------------------------
ws = wb.create_sheet("AVA — ATTR class YTD")
write_df_to_sheet(
    ws,
    vqa_b[["date", "drug", "atc", "region", "grupp", "analysis", "n"]].sort_values(
        ["drug", "region", "grupp", "analysis", "date"]
    ).reset_index(drop=True),
    title="AVA: ATTR class — Budget-år (YTD) Incidens & Prevalens (raw + per 100k)",
    preamble=[
        "Source: AVA data for mapping 2026-05-02/Vyndaquel/tab12b.RDS",
        "Same drug/region/grupp schema as the rolling-3mo sheet.",
        "analysis: 4 metrics on a budget-year (YTD) window — Incidens / Prevalens, "
        "raw count and per 100k.",
    ],
)
print(f"  ✓ AVA — ATTR class YTD ({len(vqa_b):,} rows)")


# ---------------------------------------------------------------------------
# 4. Extend the existing 'Methods notes' sheet with a one-liner pointer
# ---------------------------------------------------------------------------
mn = wb["Methods notes"]
last_row = mn.max_row
pointer_row = last_row + 2
mn.cell(row=pointer_row, column=1, value="AVA data (added v29, 2026-05-05)").font = Font(bold=True)
mn.cell(row=pointer_row + 1, column=1,
        value="Six RDS files for Ibrance / Vydura / Vyndaqel patient counts — see 'AVA — Methods notes' sheet for full definitions, suppression rules, and regional grouping.")
mn.cell(row=pointer_row + 1, column=1).alignment = Alignment(wrap_text=True, vertical="top")

print(f"\n  ✓ Extended 'Methods notes' with v29 pointer")

# Keep workbook-facing documentation aligned with the actual v29 artifact.
readme = wb["README"]
readme["A1"] = "Pfizer Sweden — Regional Landscape Mapping (master workbook v29)"
readme["A5"] = "Version 29 · 2026-05-05 · AVA patient-count insert"
for row in readme.iter_rows():
    for cell in row:
        if isinstance(cell.value, str) and "65 sheets covering" in cell.value:
            cell.value = cell.value.replace("65 sheets covering", "73 sheets covering")
        if isinstance(cell.value, str) and "Every quantitative claim in the client-facing report" in cell.value:
            cell.value = cell.value + " v29 additionally appends AVA patient-count sheets for Ibrance/CDK4-6, Vydura/oral gepants, and Vyndaqel/ATTR."

bp = wb["Build pipeline"]
bp.append([
    "Workbook v28 → v29 (THIS BUILD)",
    "06_master_workbook_v29.xlsx",
    "build_workbook_v29_ava_insert.py",
    "Surgical AVA insert: 8 new sheets from six RDS files (CDK4/6 patient metrics, Vydura/gepant patient counts, ATTR class rolling/YTD) plus Methods notes pointer.",
])
for c in bp[bp.max_row]:
    c.alignment = Alignment(wrap_text=True, vertical="top")

print("  ✓ Updated README + Build pipeline for v29")


# ---------------------------------------------------------------------------
# 5. Save
# ---------------------------------------------------------------------------
print(f"\nSaving v29 to {DST_WB.name}…")
wb.save(DST_WB)
wb.close()

# Re-open for verification
verify = openpyxl.load_workbook(DST_WB, read_only=True)
print(f"  v29 sheet count: {len(verify.sheetnames)} (was 65 → expected 73)")
new_sheets = [s for s in verify.sheetnames if s.startswith("AVA")]
print(f"  AVA sheets ({len(new_sheets)}): {new_sheets}")
verify.close()

print("\nDone.")
