# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v19.xlsx — Scenario sensitivity rebuild (roadmap #6).

Replaces point-estimate revenue / budget claims with Conservative / Base / Upside
ranges, explicit assumption blocks, and "what Pfizer must validate" callouts.

Rebuilds two specific claims flagged in Codex audit #1:
  - Vyndaqel "61% of Pfizer Swedish oral-Rx revenue" (370M SEK gross)
  - Ibrance "38-78M SEK at risk" trajectory loss

Key uncertainty: Pfizer NET revenue per patient = list × (1 − rebate%) × (1 − regional discount%).
Rebate + discount percentages are unknown to us. We model 3 cases:

  Net multiplier vs gross (TLV list) — illustrative, not Pfizer-confirmed:
    Conservative  ~0.60  (rebate 30%, regional discount 15%)
    Base          ~0.80  (rebate 15%, regional discount 5%)
    Upside        ~0.95  (rebate 5%, no regional discount)

Outputs:
  master_workbook_v19.xlsx
    + new sheet: Scenario sensitivity — per-product 3-scenario gross + net ranges
    + new sheet: Ibrance trajectory scenarios — 3 trajectory × 3 net cases = 9 cells
    + new sheet: Assumptions ledger — every assumption used + Pfizer validation needed
  working/data/master/scenario_sensitivity.csv (long form)
  working/docs/findings_scenario_sensitivity.md
"""
import sys
from pathlib import Path
import shutil
import csv

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v18.xlsx"
DST = ROOT / "working/data/master/master_workbook_v19.xlsx"
CSV_OUT = ROOT / "working/data/master/scenario_sensitivity.csv"

PF_NAVY = "003F7F"; PF_GREY = "4B5563"; PF_RED = "E4002B"

# Confidence fill colours
C_OBS = "C6EFCE"; C_MOD = "FFEB9C"; C_HYP = "FFC7CE"; C_NPV = "D9D2E9"

# Scenario fills
S_CONS = "F4CCCC"; S_BASE = "FFF2CC"; S_UP = "DEEBF7"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ============================================================================
# CORE SCENARIO PARAMETERS
# ============================================================================
# Net-revenue multiplier vs gross TLV list price — ILLUSTRATIVE.
# Pfizer net depends on actual rebate negotiation + regional discounts; numbers below
# are modeling placeholders the audit flagged as needing Pfizer validation.
NET_MULTIPLIERS = {
    "Conservative": {
        "value": 0.60,
        "rebate_pct": 30,
        "regional_discount_pct": 15,
        "rationale": "High rebate (TLV/SKR pressure on rare-disease orals) + meaningful regional discount in larger procurement regions",
    },
    "Base": {
        "value": 0.80,
        "rebate_pct": 15,
        "regional_discount_pct": 5,
        "rationale": "Mid-range rebate (typical for branded orals with active competitor) + small regional differentiation",
    },
    "Upside": {
        "value": 0.95,
        "rebate_pct": 5,
        "regional_discount_pct": 0,
        "rationale": "Minimal rebate (no direct competitor or product holds clinical preference) + no regional discount",
    },
}

# Pfizer 7 oral Rx products with current 2024 patient counts + TLV list price
# (Hospital-administered Elrexfio + Hympavzi excluded — not in Läkemedelsregistret)
ORAL_RX = [
    # (name, atc, 2024 patients national, TLV list price annual SEK)
    ("Ibrance",            "L01EF01", 753, 220_000),
    ("Vyndaqel",           "N07XX08", 463, 800_000),
    ("Talzenna",           "L01XK04",  31, 320_000),
    ("Lorbrena/Lorviqua",  "L01ED04",  72, 350_000),
    ("Tukysa",             "L01EH03",  58, 580_000),
    ("Vydura",             "N02CD06", 1837,  2_500),  # high-volume migraine
    ("Paxlovid",           "J05AE30",  693,  5_400),
]

# Ibrance trajectory scenarios (from analysis D) — 2024 baseline → 2027 patient counts
IBRANCE_TRAJECTORY = {
    "Status quo": {
        "p2024": 753,
        "p2027": 614,
        "rationale": "Stockholm + VGR continue declining at observed 2021-2024 trajectory; other regions stay flat",
        "confidence": "Modeled (linear extrapolation of 2021-2024 trend)",
    },
    "Regional spread": {
        "p2024": 753,
        "p2027": 561,
        "rationale": "Skåne + Uppsala + Östergötland adopt Stockholm trajectory (Kisqali substitution spreads to next-adopter regions)",
        "confidence": "Modeled + Hypothesis (substitution-spread mechanism)",
    },
    "National spread": {
        "p2024": 753,
        "p2027": 552,
        "rationale": "Substitution becomes general — even small + rural regions follow Kisqali preference",
        "confidence": "Modeled + Hypothesis (mechanism + national diffusion assumption)",
    },
}

# Vyndaqel base for the audit-flagged "61% of revenue" claim
VYNDAQEL_PATIENTS_2024 = 463
ORAL_RX_2024_GROSS_SEK = sum(p * c for _, _, p, c in ORAL_RX)  # SUM OF GROSS — denominator
VYNDAQEL_GROSS_SEK = 463 * 800_000


# ============================================================================
# WORKBOOK BUILDERS
# ============================================================================
def make_header(cell, text, bg=PF_NAVY, size=10):
    cell.value = text
    cell.font = Font(name="Calibri", size=size, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = BORDER


def conf_fill(tag):
    s = (tag or "").lower()
    if "needs pfizer validation" in s: return PatternFill("solid", fgColor=C_NPV)
    if "hypothesis" in s: return PatternFill("solid", fgColor=C_HYP)
    if "modeled" in s: return PatternFill("solid", fgColor=C_MOD)
    if "observed" in s: return PatternFill("solid", fgColor=C_OBS)
    return None


def scenario_fill(label):
    return PatternFill("solid", fgColor={"Conservative": S_CONS, "Base": S_BASE, "Upside": S_UP}.get(label, "FFFFFF"))


def m_sek(value):
    """Format SEK value in M for display."""
    return f"{value / 1_000_000:.1f} M SEK"


def build():
    print(f"Loading {SRC.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    print(f"Initial sheet count: {len(wb.sheetnames)}")

    insert_idx = wb.sheetnames.index("OPP - Plays detail") + 1

    # ============================================================================
    # SHEET 1: Scenario sensitivity (per-product)
    # ============================================================================
    print("Writing 'Scenario sensitivity' sheet ...")
    ws = wb.create_sheet("Scenario sensitivity", index=insert_idx)
    ws.cell(row=1, column=1, value="Per-product gross + net revenue scenarios (audit-rebuilt 2026-04-25)")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)

    ws.cell(row=2, column=1, value=(
        "Replaces audit-flagged point estimates (Vyndaqel '61%' / Ibrance '38-78M SEK') with explicit "
        "Conservative / Base / Upside ranges. Net multipliers are ILLUSTRATIVE; Pfizer must validate "
        "actual rebate + regional discount per product. Confidence: Modeled + Needs Pfizer validation."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)

    ws.cell(row=3, column=1, value=(
        f"Net multiplier scenarios:  Conservative {NET_MULTIPLIERS['Conservative']['value']:.2f}  ·  "
        f"Base {NET_MULTIPLIERS['Base']['value']:.2f}  ·  Upside {NET_MULTIPLIERS['Upside']['value']:.2f}  "
        f"of TLV list price.  See Assumptions ledger for rebate + regional discount detail per scenario."
    ))
    ws.cell(row=3, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_NAVY)
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=10)

    headers = ["Product", "ATC", "Patients 2024", "TLV list (SEK/yr)",
               "Gross 2024 (M SEK)",
               "Net Conservative (M SEK)", "Net Base (M SEK)", "Net Upside (M SEK)",
               "Confidence", "Pfizer validation needed"]
    for i, h in enumerate(headers, start=1):
        make_header(ws.cell(row=5, column=i), h)

    # Per-product totals (for Vyndaqel % calculation)
    per_product_net = {scn: {} for scn in NET_MULTIPLIERS}

    for ri, (name, atc, patients, list_price) in enumerate(ORAL_RX, start=6):
        gross = patients * list_price
        cons_net = gross * NET_MULTIPLIERS["Conservative"]["value"]
        base_net = gross * NET_MULTIPLIERS["Base"]["value"]
        up_net = gross * NET_MULTIPLIERS["Upside"]["value"]
        per_product_net["Conservative"][name] = cons_net
        per_product_net["Base"][name] = base_net
        per_product_net["Upside"][name] = up_net

        valid_text = (
            "Net per-patient revenue (after rebate + regional discount). Pfizer Sweden has the actual "
            "figure — current modeling is gross therapy-cost proxy at TLV list × 12 months."
        )

        vals = [
            name, atc, patients, f"{list_price:,}".replace(",", " "),
            f"{gross / 1e6:.1f}",
            f"{cons_net / 1e6:.1f}", f"{base_net / 1e6:.1f}", f"{up_net / 1e6:.1f}",
            "Modeled + Needs Pfizer validation",
            valid_text,
        ]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 6:
                cell.fill = scenario_fill("Conservative")
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 7:
                cell.fill = scenario_fill("Base")
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 8:
                cell.fill = scenario_fill("Upside")
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 9:
                cell.fill = conf_fill(v) or PatternFill()
                cell.font = Font(name="Calibri", size=9, bold=True)

    # Totals row + Vyndaqel %
    total_row = 6 + len(ORAL_RX)
    cons_total = sum(per_product_net["Conservative"].values())
    base_total = sum(per_product_net["Base"].values())
    up_total = sum(per_product_net["Upside"].values())
    gross_total = sum(p * c for _, _, p, c in ORAL_RX)

    ws.cell(total_row, 1, "TOTAL (7 oral Rx)").font = Font(name="Calibri", size=10, bold=True)
    ws.cell(total_row, 5, f"{gross_total / 1e6:.1f}").font = Font(bold=True)
    ws.cell(total_row, 6, f"{cons_total / 1e6:.1f}").font = Font(bold=True)
    ws.cell(total_row, 7, f"{base_total / 1e6:.1f}").font = Font(bold=True)
    ws.cell(total_row, 8, f"{up_total / 1e6:.1f}").font = Font(bold=True)
    for ci in [5, 6, 7, 8]:
        ws.cell(total_row, ci).alignment = Alignment(vertical="top", horizontal="left")
        ws.cell(total_row, ci).border = BORDER

    # Vyndaqel % row
    vyn_row = total_row + 2
    ws.cell(vyn_row, 1, "Vyndaqel % of total").font = Font(bold=True, color=PF_NAVY)
    vyn_g = VYNDAQEL_GROSS_SEK
    ws.cell(vyn_row, 5, f"{vyn_g / gross_total * 100:.0f}%").font = Font(bold=True)
    for scn, total_v in [("Conservative", cons_total), ("Base", base_total), ("Upside", up_total)]:
        col = {"Conservative": 6, "Base": 7, "Upside": 8}[scn]
        vyn_n = per_product_net[scn]["Vyndaqel"]
        ws.cell(vyn_row, col, f"{vyn_n / total_v * 100:.0f}%").font = Font(bold=True)
        ws.cell(vyn_row, col).fill = scenario_fill(scn)
    ws.cell(vyn_row, 9, "Modeled — same multiplier per product is itself an assumption (rebates may differ rare-disease vs oncology)").font = Font(size=9, italic=True)

    widths = [22, 10, 12, 16, 14, 18, 14, 14, 28, 50]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A6"

    # ============================================================================
    # SHEET 2: Ibrance trajectory scenarios (3 traj × 3 net = 9 cells)
    # ============================================================================
    print("Writing 'Ibrance trajectory scenarios' sheet ...")
    ws2 = wb.create_sheet("Ibrance trajectory scenarios", index=insert_idx + 1)
    ws2.cell(row=1, column=1, value="Ibrance 2024→2027 — trajectory × net-revenue scenario sensitivity")
    ws2.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    ws2.cell(row=2, column=1, value=(
        "Replaces the audit-flagged '38-78M SEK at risk' single number with the full 3 trajectory × 3 net-multiplier "
        "matrix. Trajectory scenarios from R analysis D; net multipliers per scenario above."
    ))
    ws2.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws2.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)

    h2 = ["Trajectory scenario", "p2024", "p2027", "Δ patients",
          "Gross loss 2027 vs 2024 (M SEK)",
          "Net loss Conservative", "Net loss Base", "Net loss Upside"]
    for i, h in enumerate(h2, start=1):
        make_header(ws2.cell(row=4, column=i), h)

    for ri, (scn, d) in enumerate(IBRANCE_TRAJECTORY.items(), start=5):
        delta = d["p2024"] - d["p2027"]
        gross_loss = delta * 220_000
        c_loss = gross_loss * NET_MULTIPLIERS["Conservative"]["value"]
        b_loss = gross_loss * NET_MULTIPLIERS["Base"]["value"]
        u_loss = gross_loss * NET_MULTIPLIERS["Upside"]["value"]

        vals = [scn, d["p2024"], d["p2027"], -delta,
                f"{-gross_loss / 1e6:.1f}",
                f"{-c_loss / 1e6:.1f}",
                f"{-b_loss / 1e6:.1f}",
                f"{-u_loss / 1e6:.1f}"]
        for ci, v in enumerate(vals, start=1):
            cell = ws2.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 1:
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 6:
                cell.fill = scenario_fill("Conservative")
            if ci == 7:
                cell.fill = scenario_fill("Base")
            if ci == 8:
                cell.fill = scenario_fill("Upside")

    # Range summary row
    range_row = 5 + len(IBRANCE_TRAJECTORY) + 2
    cell = ws2.cell(range_row, 1, "Audit-rebuilt range")
    cell.font = Font(bold=True, color=PF_NAVY)
    losses_g = [(d["p2024"] - d["p2027"]) * 220_000 for d in IBRANCE_TRAJECTORY.values()]
    losses_n_min = min(losses_g) * NET_MULTIPLIERS["Conservative"]["value"]
    losses_n_max = max(losses_g) * NET_MULTIPLIERS["Upside"]["value"]
    ws2.cell(range_row, 5, f"−{min(losses_g) / 1e6:.0f} to −{max(losses_g) / 1e6:.0f} M SEK gross").font = Font(bold=True)
    ws2.cell(range_row, 6, f"−{losses_n_min / 1e6:.0f} M SEK net (Conservative trajectory × Conservative net)").font = Font(bold=True)
    ws2.cell(range_row, 8, f"−{losses_n_max / 1e6:.0f} M SEK net (National spread × Upside net)").font = Font(bold=True)

    ws2.cell(range_row + 1, 1, "Original audit-flagged claim").font = Font(bold=True, color=PF_RED)
    ws2.cell(range_row + 1, 5, "'-38 to -78 M SEK at risk' — the rebuilt range above is much narrower").font = Font(italic=True, color=PF_RED)
    ws2.merge_cells(start_row=range_row + 1, start_column=5, end_row=range_row + 1, end_column=8)

    widths2 = [22, 10, 10, 12, 30, 22, 22, 22]
    for i, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A5"

    # ============================================================================
    # SHEET 3: Assumptions ledger
    # ============================================================================
    print("Writing 'Assumptions ledger' sheet ...")
    ws3 = wb.create_sheet("Assumptions ledger", index=insert_idx + 2)
    ws3.cell(row=1, column=1, value="Assumptions ledger — every modeling parameter used in scenario sensitivity")
    ws3.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

    ws3.cell(row=2, column=1, value=(
        "Every assumption in the scenario sensitivity work is listed here with current value, source / rationale, "
        "and what Pfizer would need to validate or replace it. Each row carries a confidence tag."
    ))
    ws3.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws3.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)

    h3 = ["Assumption ID", "Parameter", "Value", "Source / rationale",
          "Pfizer validation needed", "Confidence"]
    for i, h in enumerate(h3, start=1):
        make_header(ws3.cell(row=4, column=i), h)

    assumptions = [
        ("ASM-01", "Net revenue multiplier (Conservative)", "0.60 (rebate 30% + regional discount 15%)",
         "Illustrative — high-pressure rebate environment for rare-disease/oncology orals",
         "Actual Pfizer rebate negotiation per product; regional discount practice", "Modeled + Needs Pfizer validation"),
        ("ASM-02", "Net revenue multiplier (Base)", "0.80 (rebate 15% + regional discount 5%)",
         "Illustrative — typical for branded oncology with active competitor",
         "Actual Pfizer rebate per product", "Modeled + Needs Pfizer validation"),
        ("ASM-03", "Net revenue multiplier (Upside)", "0.95 (rebate 5% + no regional discount)",
         "Illustrative — minimal rebate where Pfizer holds clinical preference and no direct competitor",
         "Actual Pfizer rebate per product; whether ANY product is at near-list pricing", "Modeled + Needs Pfizer validation"),
        ("ASM-04", "TLV list price (Ibrance)", "220 000 SEK / patient / year",
         "TLV public list price benchmark, from R PFIZER_PRODUCTS table",
         "Confirm against current TLV listing + any 2025 price update", "Observed (gross)"),
        ("ASM-05", "TLV list price (Vyndaqel)", "800 000 SEK / patient / year",
         "TLV public list price benchmark; rare-disease pricing band",
         "Confirm; rare-disease pricing typically has higher rebate negotiation", "Observed (gross)"),
        ("ASM-06", "TLV list price (Talzenna, Lorbrena, Tukysa)", "320k / 350k / 580k SEK",
         "TLV public list price benchmarks per product",
         "Confirm against TLV", "Observed (gross)"),
        ("ASM-07", "Same net multiplier across all 7 products", "Single multiplier applied uniformly",
         "Simplification — actual rebates likely differ between rare-disease (higher rebate) vs oncology (varies) vs migraine vs antiviral",
         "Per-product Pfizer net pricing — would replace single multiplier with 7 product-specific multipliers", "Modeled (simplification)"),
        ("ASM-08", "Ibrance trajectory: status quo 2027", "614 patients (linear extrapolation of 2021-2024)",
         "Linear regression of 2021-2024 patient counts (analysis D)",
         "Validate against Pfizer's own internal Ibrance forecast; whether linear extrapolation is appropriate", "Modeled"),
        ("ASM-09", "Ibrance trajectory: regional spread 2027", "561 patients",
         "Stockholm trajectory applied to Skåne + Uppsala + Östergötland from 2024",
         "Whether regional spread of Kisqali substitution is the correct mechanism + correct next-adopters", "Modeled + Hypothesis"),
        ("ASM-10", "Ibrance trajectory: national spread 2027", "552 patients",
         "Universal substitution diffusion",
         "Whether national-scale Kisqali adoption is even feasible (Halland resists; Norra not adopting)", "Hypothesis"),
        ("ASM-11", "Vyndaqel patient count 2024", "463 nationally",
         "Socialstyrelsen Läkemedelsregistret 2024 (Observed)",
         "Refresh annually with new Socialstyrelsen pull", "Observed"),
        ("ASM-12", "Hospital-administered products excluded", "Elrexfio + Hympavzi not in scope",
         "Not visible in Läkemedelsregistret — would need IQVIA Concise extract for hospital channel",
         "IQVIA Concise extract for hospital-administered Pfizer products", "Observed (structural limit)"),
    ]

    for ri, asm in enumerate(assumptions, start=5):
        for ci, v in enumerate(asm, start=1):
            cell = ws3.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 1:
                cell.font = Font(name="Calibri", size=10, bold=True, color=PF_NAVY)
            if ci == 6:
                cell.fill = conf_fill(v) or PatternFill()
                cell.font = Font(name="Calibri", size=9, bold=True)
        ws3.row_dimensions[ri].height = 60

    widths3 = [10, 30, 30, 50, 40, 22]
    for i, w in enumerate(widths3, start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w
    ws3.freeze_panes = "A5"

    # ======== Update README ========
    rd = wb["README"]
    r = rd.max_row + 2
    rd.cell(row=r, column=1, value="SCENARIO SENSITIVITY (v19, 2026-04-25)")
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    rd.cell(row=r, column=1, value=(
        "Replaces audit-flagged point-estimate revenue claims with explicit Conservative/Base/Upside "
        "ranges. New 'Scenario sensitivity' sheet has per-product gross + 3 net-multiplier scenarios; "
        "'Ibrance trajectory scenarios' sheet has 3 trajectory × 3 net = 9-cell sensitivity matrix; "
        "'Assumptions ledger' sheet documents every modeling parameter used + what Pfizer must validate. "
        "Net multipliers are illustrative — actual Pfizer net pricing is the #1 validation gate."
    ))
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    rd.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    # CSV
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["product", "atc", "patients_2024", "tlv_list_sek",
                    "gross_2024_msek",
                    "net_conservative_msek", "net_base_msek", "net_upside_msek",
                    "confidence"])
        for name, atc, patients, list_price in ORAL_RX:
            gross = patients * list_price
            w.writerow([
                name, atc, patients, list_price,
                round(gross / 1e6, 2),
                round(gross * NET_MULTIPLIERS["Conservative"]["value"] / 1e6, 2),
                round(gross * NET_MULTIPLIERS["Base"]["value"] / 1e6, 2),
                round(gross * NET_MULTIPLIERS["Upside"]["value"] / 1e6, 2),
                "Modeled + Needs Pfizer validation",
            ])
    print(f"Wrote {CSV_OUT.name}")

    # Summary
    print()
    print("Vyndaqel % of Pfizer Sweden oral-Rx revenue (audit-rebuilt):")
    print(f"  Gross (TLV list):       {VYNDAQEL_GROSS_SEK / gross_total * 100:.0f}%")
    print(f"  Conservative net:       {per_product_net['Conservative']['Vyndaqel'] / cons_total * 100:.0f}%  (note: same % because uniform multiplier)")
    print(f"  Base net:               {per_product_net['Base']['Vyndaqel'] / base_total * 100:.0f}%")
    print(f"  Upside net:             {per_product_net['Upside']['Vyndaqel'] / up_total * 100:.0f}%")
    print()
    print("Ibrance loss 2024→2027 across trajectory × net scenarios:")
    for scn, d in IBRANCE_TRAJECTORY.items():
        delta = d["p2024"] - d["p2027"]
        gross_loss = delta * 220_000
        print(f"  {scn:<20}: gross −{gross_loss/1e6:.0f} M | "
              f"net Conservative −{gross_loss * 0.60 / 1e6:.0f} | "
              f"net Base −{gross_loss * 0.80 / 1e6:.0f} | "
              f"net Upside −{gross_loss * 0.95 / 1e6:.0f}")


if __name__ == "__main__":
    build()
