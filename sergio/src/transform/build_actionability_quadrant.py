# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v16.xlsx — Actionability axis + 4-quadrant assignment.

Roadmap work item #3 (audit #2). Adds a second axis to the Opportunity Matrix
so we can distinguish "high-opportunity-but-locked" cells from "high-opportunity-immediately-actionable" cells.

Actionability composite (0-100, higher = easier for Pfizer to move the needle):
  1. Governance reachability  (40%) — HIGH-conf stakeholder count + national rep + sjukvårdsregion cornerstone
  2. Pfizer footprint         (35%) — existing Rx /100k breadth + vaccine sell-in /inv
  3. Policy permissiveness    (25%) — regional plan tier + keyword density on relevant themes
Plus per-product modifier (hospital-admin -10, etc.) — capped to [0, 100].

Quadrant assignment (thresholds: 50 on both axes):
  - HH: high opportunity + high actionability  → "Priority focus"
  - HL: high opp  + low  action                → "Engagement build needed"
  - LH: low  opp  + high action                → "Quick win territory"
  - LL: low  opp  + low  action                → "Deprioritize"

Inputs:  master_workbook_v15.xlsx + stakeholder_mapping_v8.xlsx
Outputs: master_workbook_v16.xlsx (replaces matrix sheet with extended cols + adds
                                   Actionability inputs sheet + Quadrant summary sheet)
         working/data/master/opportunity_matrix_v2.csv
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
SRC = ROOT / "working/data/master/master_workbook_v15.xlsx"
STAKE = ROOT / "working/data/master/stakeholder_mapping_v8.xlsx"
DST = ROOT / "working/data/master/master_workbook_v16.xlsx"
CSV_OUT = ROOT / "working/data/master/opportunity_matrix_v2.csv"

PF_NAVY = "003F7F"
PF_GREY = "4B5563"
TAG_HIGH = "C6EFCE"
TAG_MEDIUM = "FFEB9C"
TAG_LOW = "FFC7CE"
HEAT_DARK = "1F4E79"
HEAT_MID = "9CC2E5"
HEAT_LIGHT = "DEEBF7"

# Quadrant fills
Q_HH = "8FD19E"   # green — Priority focus
Q_HL = "FFC78A"   # amber — Engagement build needed
Q_LH = "BDD7EE"   # blue  — Quick win territory
Q_LL = "D9D9D9"   # grey  — Deprioritize

# Confidence tag fills (carried from v15)
C_OBS = "C6EFCE"; C_MOD = "FFEB9C"; C_HYP = "FFC7CE"; C_NPV = "D9D2E9"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

WEIGHTS = dict(governance=0.40, footprint=0.35, policy=0.25)

# Per-product Actionability modifier (added on top of regional base)
PRODUCT_ACTION_MOD = {
    "Tukysa": 0,
    "Lorbrena/Lorviqua": 0,
    "Elrexfio": -12,         # hospital-admin, no Rx-register visibility = harder to act
    "Ibrance": 0,
    "Talzenna": 0,
    "Vyndaqel": 0,
    "Hympavzi": -12,         # hospital-admin
    "Paxlovid": -3,          # OUT_OF_SCOPE NT pathway, separate FHM channel
    "Vydura": 0,
    "Prevenar 20": 0,
    "Abrysvo": -8,           # AVVAKTA — moves are politically constrained
}

# Sjukvårdsregion-level cornerstone bumps (post v8 corrections)
SJ_CORNERSTONE_REACH = {
    "Stockholm-Gotland": 5,
    "Mellansverige": 6,
    "Sydöstra": 7,            # Lindström + Ekelund cornerstone
    "Västra": 4,
    "Sydsvenska": 4,
    "Norra": 7,               # Näsvall + Bergström + ATTR-CM relevance
}


# ============================================================================
# DATA LOADERS
# ============================================================================
def load_v15_matrix(wb):
    """Returns list of dicts from existing OPP - Region x Product matrix sheet."""
    ws = wb["OPP - Region x Product matrix"]
    headers = [ws.cell(5, c).value for c in range(1, ws.max_column + 1)]
    rows = []
    for r in range(6, ws.max_row + 1):
        row = {h: ws.cell(r, i + 1).value for i, h in enumerate(headers) if h}
        if row.get("Region"):
            rows.append(row)
    return rows, headers


def load_stakeholder_v8(wb_st):
    """Returns dict[region] -> {high_count, has_natrep, sjukvardsregion}."""
    ws = wb_st["Stakeholders"]
    headers = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1) if ws.cell(1, c).value}
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, headers["Region"]).value
        if not region:
            continue
        sj = ws.cell(r, headers["Sjukvårdsregion"]).value or ""
        high = 0
        for cf in ["RD conf", "HSD conf", "RS conf", "HSN conf", "LK conf"]:
            v = ws.cell(r, headers[cf]).value
            if v and "HIGH" in str(v).upper():
                high += 1
        nt = ws.cell(r, headers["NT-rådet rep (SVR)"]).value
        nsg = ws.cell(r, headers["NSG rep (SVR)"]).value
        has_nat = bool((nt and str(nt).strip()) or (nsg and str(nsg).strip()))
        out[region] = dict(sj=sj, high_count=high, has_natrep=has_nat)
    return out


def load_pfizer_footprint(wb15):
    """Returns dict[region_name] -> dict(rx_total_per100k, vaccine_sellin)."""
    out = {}
    # Rx from 'Rx 2024 snapshot'
    ws = wb15["Rx 2024 snapshot"]
    for r in range(2, ws.max_row + 1):
        region_short = ws.cell(r, 1).value
        if not region_short:
            continue
        # Sum patient-per-100k cells (every 'X /100k' col)
        total = 0
        for c in range(4, ws.max_column + 1, 2):
            v = ws.cell(r, c).value
            try:
                total += float(v) if v else 0
            except (TypeError, ValueError):
                pass
        # Reconcile to canonical region name
        canonical = region_short if region_short.startswith("Region") or region_short == "Västra Götaland" else f"Region {region_short}"
        if region_short == "Västra Götaland":
            canonical = "Västra Götalandsregionen"
        if region_short == "Jämtland Härjedalen":
            canonical = "Region Jämtland Härjedalen"
        if region_short == "Sörmland":
            canonical = "Region Sörmland"
        if region_short == "Jönköping":
            canonical = "Region Jönköpings län"
        if region_short == "Kalmar":
            canonical = "Region Kalmar"
        if region_short == "Örebro":
            canonical = "Region Örebro län"
        out.setdefault(canonical, {})["rx_total_per100k"] = total

    # Vaccine sell-in from Region master
    ws2 = wb15["Region master"]
    hd = {ws2.cell(1, c).value: c for c in range(1, ws2.max_column + 1) if ws2.cell(1, c).value}
    for r in range(2, ws2.max_row + 1):
        region = ws2.cell(r, hd["Region"]).value
        v = ws2.cell(r, hd["Vaccine sell-in /inv (SEK/yr)"]).value
        try:
            sellin = float(v) if v else 0
        except (TypeError, ValueError):
            sellin = 0
        out.setdefault(region, {})["vaccine_sellin"] = sellin
    return out


def load_regional_plans(wb15):
    """Returns dict[region_short] -> {tier, kw_total}."""
    ws = wb15["Regional plans + angles v2"]
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 1).value
        if not region:
            continue
        try:
            kw_total = sum(int(ws.cell(r, c).value or 0) for c in range(4, 14))
        except (TypeError, ValueError):
            kw_total = 0
        tier = ws.cell(r, 15).value if ws.max_column >= 15 else None
        out[region] = dict(tier=(tier or "MEDIUM"), kw_total=kw_total)
    return out


# ============================================================================
# ACTIONABILITY SUB-SCORE COMPUTATION
# ============================================================================
def normalize(values):
    if not values:
        return []
    lo = min(values); hi = max(values)
    if hi - lo < 1e-9:
        return [50.0] * len(values)
    return [(v - lo) / (hi - lo) * 100 for v in values]


def compute_governance_reach(stake_data, region):
    """0-100 governance reachability score."""
    s = stake_data.get(region, {})
    if not s:
        return 50
    base = (s["high_count"] / 5) * 70  # up to 70 from HIGH count
    if s["has_natrep"]:
        base += 15  # +15 if has NT-rådet or NSG representation (national-tier access)
    base += SJ_CORNERSTONE_REACH.get(s["sj"], 3)
    return min(100, max(0, base))


def compute_footprint(footprint_data, region, rx_norm_lookup, vac_norm_lookup):
    """0-100 Pfizer footprint score (Rx breadth + vaccine sell-in)."""
    f = footprint_data.get(region, {})
    rx_score = rx_norm_lookup.get(region, 0)
    vac_score = vac_norm_lookup.get(region, 0)
    return (rx_score + vac_score) / 2  # equal weight


def compute_policy_permissive(plans_data, region_short):
    """0-100 policy permissiveness from regional plan engagement signal."""
    plan = plans_data.get(region_short)
    if plan is None:
        # No parsed plan — neutral
        return 45
    tier_map = {"HIGH": 80, "MEDIUM": 55, "LOW": 30}
    base = tier_map.get((plan["tier"] or "").upper(), 45)
    # Keyword-density bonus (cap +15)
    bonus = min(15, plan["kw_total"] / 8)
    return min(100, base + bonus)


# ============================================================================
# QUADRANT ASSIGNMENT
# ============================================================================
QUADRANT_LABELS = {
    "HH": ("Priority focus", "High opportunity + high actionability — concentrate Pfizer effort here"),
    "HL": ("Engagement build", "High opportunity but low actionability — invest in stakeholder/footprint before commercial push"),
    "LH": ("Quick win", "Lower absolute opportunity but actionable — tactical low-cost engagement"),
    "LL": ("Deprioritize", "Low opportunity + low actionability — minimal effort"),
}

# Median-based thresholds — calibrated to actual distribution after first run:
#   Opportunity median ≈ 43, Actionability median ≈ 60.
# Using 45 / 60 gives a balanced quadrant split honest to data shape.
OPP_THRESHOLD = 45
ACT_THRESHOLD = 60


def assign_quadrant(opp, act):
    h_opp = opp >= OPP_THRESHOLD
    h_act = act >= ACT_THRESHOLD
    if h_opp and h_act: return "HH"
    if h_opp and not h_act: return "HL"
    if not h_opp and h_act: return "LH"
    return "LL"


# ============================================================================
# CONFIDENCE / QUADRANT FILL HELPERS
# ============================================================================
def conf_fill(tag):
    s = (tag or "").lower()
    if "needs pfizer validation" in s: return PatternFill("solid", fgColor=C_NPV)
    if "hypothesis" in s: return PatternFill("solid", fgColor=C_HYP)
    if "modeled" in s: return PatternFill("solid", fgColor=C_MOD)
    if "observed" in s: return PatternFill("solid", fgColor=C_OBS)
    return None


def quadrant_fill(q):
    return PatternFill("solid", fgColor={
        "HH": Q_HH, "HL": Q_HL, "LH": Q_LH, "LL": Q_LL
    }.get(q, "FFFFFF"))


def heat_fill(score):
    if score is None: return None
    if score >= 67: return PatternFill("solid", fgColor=HEAT_DARK)
    if score >= 33: return PatternFill("solid", fgColor=HEAT_MID)
    return PatternFill("solid", fgColor=HEAT_LIGHT)


def make_header_cell(cell, text, bg=PF_NAVY, fg="FFFFFF", size=10):
    cell.value = text
    cell.font = Font(name="Calibri", size=size, bold=True, color=fg)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = BORDER


# ============================================================================
# WORKBOOK BUILD
# ============================================================================
def build():
    print(f"Loading {SRC.name} + {STAKE.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    wb_st = openpyxl.load_workbook(STAKE, data_only=True)

    print(f"Initial sheet count: {len(wb.sheetnames)}")

    # Data
    rows, _ = load_v15_matrix(wb)
    stake_data = load_stakeholder_v8(wb_st)
    footprint_data = load_pfizer_footprint(wb)
    plans_data = load_regional_plans(wb)

    # Per-region Actionability sub-scores
    print("Computing per-region Actionability sub-scores ...")
    regions = sorted({r["Region"] for r in rows})

    # First normalize footprint inputs across regions
    rx_vals = {region: footprint_data.get(region, {}).get("rx_total_per100k", 0) for region in regions}
    vac_vals = {region: footprint_data.get(region, {}).get("vaccine_sellin", 0) for region in regions}
    rx_normed = dict(zip(rx_vals.keys(), normalize(list(rx_vals.values()))))
    vac_normed = dict(zip(vac_vals.keys(), normalize(list(vac_vals.values()))))

    region_actionability = {}
    for region in regions:
        gov = compute_governance_reach(stake_data, region)
        fp = compute_footprint(footprint_data, region, rx_normed, vac_normed)
        # Plan key matching — sheet uses short names
        short = region.replace("Region ", "")
        if short == "Västra Götalandsregionen": short = "Västra Götaland"
        pol = compute_policy_permissive(plans_data, short)
        composite = gov * WEIGHTS["governance"] + fp * WEIGHTS["footprint"] + pol * WEIGHTS["policy"]
        region_actionability[region] = dict(
            governance=round(gov, 1),
            footprint=round(fp, 1),
            policy=round(pol, 1),
            composite=round(composite, 1),
        )

    # Per-cell Actionability + Quadrant
    print("Assigning per-cell Actionability + Quadrant ...")
    for r in rows:
        base = region_actionability[r["Region"]]["composite"]
        modifier = PRODUCT_ACTION_MOD.get(r["Product"], 0)
        actionability = max(0, min(100, base + modifier))
        opportunity = float(r["Composite"])
        q = assign_quadrant(opportunity, actionability)
        r["_governance"] = region_actionability[r["Region"]]["governance"]
        r["_footprint"] = region_actionability[r["Region"]]["footprint"]
        r["_policy_perm"] = region_actionability[r["Region"]]["policy"]
        r["_action_modifier"] = modifier
        r["_actionability"] = round(actionability, 1)
        r["_quadrant"] = q
        r["_quadrant_label"] = QUADRANT_LABELS[q][0]

    # Sort by actionability desc within HH, then by composite desc
    rows.sort(key=lambda x: (
        -1 if x["_quadrant"] == "HH" else (-2 if x["_quadrant"] == "HL" else (-3 if x["_quadrant"] == "LH" else -4)),
        -float(x["Composite"]),
    ), reverse=False)
    # Wait — that sort is upside down. Let me redo:
    rows.sort(key=lambda x: (
        {"HH": 0, "HL": 1, "LH": 2, "LL": 3}[x["_quadrant"]],
        -float(x["Composite"]),
    ))

    # Replace the matrix sheet entirely with the extended version
    print("Rewriting OPP - Region x Product matrix sheet (extended) ...")
    if "OPP - Region x Product matrix" in wb.sheetnames:
        del wb["OPP - Region x Product matrix"]

    # Place new sheet right after OPP - All products composite
    insert_idx = wb.sheetnames.index("OPP - All products composite") + 1
    ws = wb.create_sheet("OPP - Region x Product matrix", index=insert_idx)

    # Title
    ws.cell(row=1, column=1, value="Product × Region Opportunity Matrix v2 — with Actionability axis + Quadrant")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=22)

    ws.cell(row=2, column=1, value=(
        "Adds Actionability axis to v1 matrix. Quadrant = HH (Priority focus) / HL (Engagement build) / "
        "LH (Quick win) / LL (Deprioritize). Thresholds: 50 on both axes. Actionability = "
        "0.40·Governance + 0.35·Footprint + 0.25·Policy permissiveness, with per-product modifiers "
        "(hospital-admin -12, Abrysvo -8, Paxlovid -3). Stakeholder data from v8 fact-checked file."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=22)

    weight_str = "  ".join(f"{k}:{int(v*100)}%" for k, v in WEIGHTS.items())
    ws.cell(row=3, column=1, value=f"Actionability weights — {weight_str}    Quadrant thresholds — Opp:{OPP_THRESHOLD}, Act:{ACT_THRESHOLD} (data median-aligned)")
    ws.cell(row=3, column=1).font = Font(name="Calibri", size=9, italic=True, color=PF_GREY)
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=22)

    # Headers
    headers = [
        "Region", "Sjukvårdsregion", "Product", "Category", "Indication",
        "Epi", "Uptake", "Growth", "Access", "Stake", "Compet", "Policy",
        "Opportunity", "Governance", "Footprint", "PolicyPerm", "Actionability",
        "Quadrant", "Q label", "Action", "Action text", "Confidence"
    ]
    for i, h in enumerate(headers, start=1):
        make_header_cell(ws.cell(row=5, column=i), h)

    # Body
    for ri, row in enumerate(rows, start=6):
        ordered = [
            row["Region"], row["Sjukvårdsregion"], row["Product"], row["Category"], row["Indication"],
            row["Epi fit"], row["Uptake"], row["Growth"], row["Access"], row["Stakeholder"],
            row["Competitive"], row["Policy"], row["Composite"],
            row["_governance"], row["_footprint"], row["_policy_perm"], row["_actionability"],
            row["_quadrant"], row["_quadrant_label"],
            row["Action"], row["Action text"], row["Confidence"]
        ]
        for ci, val in enumerate(ordered, start=1):
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.font = Font(name="Calibri", size=9)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            # Heat for opportunity sub-scores (cols 6-13)
            if 6 <= ci <= 13 and isinstance(val, (int, float)):
                cell.fill = heat_fill(val)
                cell.font = Font(name="Calibri", size=9,
                                  color=("FFFFFF" if val >= 67 else "000000"),
                                  bold=True)
            # Heat for actionability sub-scores (cols 14-17)
            if 14 <= ci <= 17 and isinstance(val, (int, float)):
                cell.fill = heat_fill(val)
                cell.font = Font(name="Calibri", size=9,
                                  color=("FFFFFF" if val >= 67 else "000000"),
                                  bold=True)
            # Quadrant col (18)
            if ci == 18:
                cell.fill = quadrant_fill(val)
                cell.font = Font(name="Calibri", size=9, bold=True)
            # Action keyword (20)
            if ci == 20:
                cell.font = Font(name="Calibri", size=9, bold=True)
            # Confidence (22)
            if ci == 22:
                cell.fill = conf_fill(val) or PatternFill()
                cell.font = Font(name="Calibri", size=9, bold=True)

    # Widths
    widths = [22, 22, 18, 14, 28, 6, 6, 6, 6, 6, 6, 6, 10,
              10, 10, 10, 11, 9, 18, 11, 50, 24]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "F6"
    ws.auto_filter.ref = f"A5:V{5 + len(rows)}"

    # ========== Sheet 2: Actionability inputs (per region) ==========
    print("Adding 'OPP - Actionability inputs' sheet ...")
    ws2 = wb.create_sheet("OPP - Actionability inputs", index=insert_idx + 1)
    ws2.cell(row=1, column=1, value="Per-region Actionability sub-scores (the regional baseline before per-product modifiers)")
    ws2.cell(row=1, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    h2 = ["Region", "Sjukvårdsregion", "Governance reach", "Pfizer footprint",
          "Policy permissiveness", "Actionability composite", "HIGH-conf governance roles", "Has national rep"]
    for i, h in enumerate(h2, start=1):
        make_header_cell(ws2.cell(row=3, column=i), h)

    for ri, region in enumerate(sorted(regions, key=lambda r: -region_actionability[r]["composite"]),
                                 start=4):
        sd = stake_data.get(region, {})
        a = region_actionability[region]
        vals = [region, sd.get("sj", ""), a["governance"], a["footprint"], a["policy"], a["composite"],
                f"{sd.get('high_count', 0)}/5", "Yes" if sd.get("has_natrep") else "No"]
        for ci, v in enumerate(vals, start=1):
            cell = ws2.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if 3 <= ci <= 6 and isinstance(v, (int, float)):
                cell.fill = heat_fill(v)
                cell.font = Font(name="Calibri", size=10,
                                  color=("FFFFFF" if v >= 67 else "000000"),
                                  bold=True)

    widths2 = [22, 22, 14, 14, 14, 16, 16, 12]
    for i, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A4"

    # ========== Sheet 3: Quadrant summary ==========
    print("Adding 'OPP - Quadrant summary' sheet ...")
    ws3 = wb.create_sheet("OPP - Quadrant summary", index=insert_idx + 2)
    ws3.cell(row=1, column=1, value="Quadrant distribution: Opportunity × Actionability")
    ws3.cell(row=1, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

    # Summary by product
    products = sorted({r["Product"] for r in rows})
    h3 = ["Product", "HH (Priority focus)", "HL (Engagement build)", "LH (Quick win)", "LL (Deprioritize)", "Total"]
    for i, h in enumerate(h3, start=1):
        make_header_cell(ws3.cell(row=3, column=i), h)

    summary_row = 4
    for product in products:
        prod_rows = [r for r in rows if r["Product"] == product]
        counts = {q: sum(1 for r in prod_rows if r["_quadrant"] == q) for q in ["HH", "HL", "LH", "LL"]}
        ws3.cell(summary_row, 1, product).font = Font(bold=True, size=10)
        for ci, q in enumerate(["HH", "HL", "LH", "LL"], start=2):
            cell = ws3.cell(summary_row, ci, counts[q])
            cell.font = Font(size=10)
            cell.alignment = Alignment(horizontal="center")
            cell.fill = quadrant_fill(q) if counts[q] > 0 else PatternFill()
            cell.border = BORDER
        ws3.cell(summary_row, 6, sum(counts.values())).alignment = Alignment(horizontal="center")
        ws3.cell(summary_row, 6).font = Font(bold=True, size=10)
        ws3.cell(summary_row, 6).border = BORDER
        summary_row += 1

    # Total row
    summary_row += 1
    ws3.cell(summary_row, 1, "TOTAL").font = Font(bold=True, size=10)
    total_counts = {q: sum(1 for r in rows if r["_quadrant"] == q) for q in ["HH", "HL", "LH", "LL"]}
    for ci, q in enumerate(["HH", "HL", "LH", "LL"], start=2):
        cell = ws3.cell(summary_row, ci, total_counts[q])
        cell.font = Font(bold=True, size=10)
        cell.alignment = Alignment(horizontal="center")
        cell.fill = quadrant_fill(q)
        cell.border = BORDER
    ws3.cell(summary_row, 6, sum(total_counts.values())).font = Font(bold=True, size=10)
    ws3.cell(summary_row, 6).alignment = Alignment(horizontal="center")
    ws3.cell(summary_row, 6).border = BORDER

    # Quadrant legend
    summary_row += 3
    for q, (label, desc) in QUADRANT_LABELS.items():
        c = ws3.cell(summary_row, 1, q + " — " + label)
        c.font = Font(bold=True, size=10)
        c.fill = quadrant_fill(q)
        c.border = BORDER
        d = ws3.cell(summary_row, 2, desc)
        d.font = Font(size=10, italic=True)
        d.alignment = Alignment(wrap_text=True, vertical="top")
        ws3.merge_cells(start_row=summary_row, start_column=2, end_row=summary_row, end_column=6)
        summary_row += 1

    widths3 = [24, 18, 18, 18, 18, 10]
    for i, w in enumerate(widths3, start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # Update README
    print("Updating README ...")
    rd = wb["README"]
    r = rd.max_row + 2
    rd.cell(row=r, column=1, value="ACTIONABILITY AXIS + QUADRANT (v16, 2026-04-25)")
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    rd.cell(row=r, column=1, value=(
        "Matrix sheet now extended with Actionability axis (Governance reach + Pfizer footprint + Policy "
        "permissiveness) + 4-quadrant assignment (HH Priority focus / HL Engagement build / LH Quick win "
        "/ LL Deprioritize). New 'OPP - Actionability inputs' sheet shows the regional baseline. New "
        "'OPP - Quadrant summary' sheet shows per-product quadrant distribution."
    ))
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    rd.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

    # Save
    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    # CSV
    fields = [
        "region", "sjukvardsregion", "product", "category", "indication",
        "epi", "uptake", "growth", "access", "stake", "compet", "policy",
        "opportunity", "governance", "footprint", "policy_perm", "actionability",
        "quadrant", "quadrant_label", "action", "action_text", "confidence"
    ]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(dict(
                region=row["Region"], sjukvardsregion=row["Sjukvårdsregion"],
                product=row["Product"], category=row["Category"], indication=row["Indication"],
                epi=row["Epi fit"], uptake=row["Uptake"], growth=row["Growth"], access=row["Access"],
                stake=row["Stakeholder"], compet=row["Competitive"], policy=row["Policy"],
                opportunity=row["Composite"],
                governance=row["_governance"], footprint=row["_footprint"], policy_perm=row["_policy_perm"],
                actionability=row["_actionability"],
                quadrant=row["_quadrant"], quadrant_label=row["_quadrant_label"],
                action=row["Action"], action_text=row["Action text"], confidence=row["Confidence"],
            ))
    print(f"Wrote {CSV_OUT.name}")

    # Print summary
    print()
    print("Quadrant distribution (overall):")
    for q in ["HH", "HL", "LH", "LL"]:
        n = total_counts[q]
        print(f"  {q} ({QUADRANT_LABELS[q][0]:<22}): {n}")
    print()
    print("Top 10 HH (Priority focus) cells:")
    hh_rows = [r for r in rows if r["_quadrant"] == "HH"][:10]
    for r in hh_rows:
        print(f"  Opp:{float(r['Composite']):>5.1f} Act:{r['_actionability']:>5.1f}  "
              f"{r['Region'][:24]:<24} | {r['Product']:<18} [{r['Action']}]")
    print()
    print("All HL (Engagement build needed) cells — high opportunity locked behind low actionability:")
    hl_rows = [r for r in rows if r["_quadrant"] == "HL"]
    for r in hl_rows:
        print(f"  Opp:{float(r['Composite']):>5.1f} Act:{r['_actionability']:>5.1f}  "
              f"{r['Region'][:24]:<24} | {r['Product']:<18} [{r['Action']}]")

    return rows, region_actionability


if __name__ == "__main__":
    build()
