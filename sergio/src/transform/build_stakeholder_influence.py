# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v20.xlsx — Stakeholder influence scoring layer (roadmap #7).

Adds an analytical layer over stakeholder_mapping_v8.xlsx WITHOUT touching name verification
(separate fact-check agent owns that lane). Computes:

  Stakeholder Influence Score = role_power × confidence_multiplier
  (with sjukvårdsregion-level bonus for NT-rådet + NSG reps who span multiple regions)

  Per-named-individual aggregate score = sum of scores across roles they hold
  (e.g. Maria Ekelund = LK ordf Jönköping + NT-rådet Sydöstra → summed influence)

Plus 4 derived views:
  1. OPP - Stakeholder influence — per-region/role rows with computed scores
  2. OPP - Named individuals — aggregated by person (named individuals with multi-role exposure)
  3. OPP - Validation queue — non-HIGH confidence stakeholders to verify next
  4. OPP - Engagement priorities — top stakeholders per Pfizer product

Outputs: v20.xlsx + stakeholder_influence.csv + findings doc
"""
import sys
from pathlib import Path
import shutil
import csv
from collections import defaultdict

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC_WB = ROOT / "working/data/master/master_workbook_v19.xlsx"
SRC_ST = ROOT / "working/data/master/stakeholder_mapping_v8.xlsx"
DST = ROOT / "working/data/master/master_workbook_v20.xlsx"
CSV_OUT = ROOT / "working/data/master/stakeholder_influence.csv"

PF_NAVY = "003F7F"; PF_GREY = "4B5563"; PF_RED = "E4002B"
C_OBS = "C6EFCE"; C_MOD = "FFEB9C"; C_HYP = "FFC7CE"; C_NPV = "D9D2E9"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ============================================================================
# SCORING PARAMETERS
# ============================================================================
# Role power (0-100, fixed) — based on actual Pfizer-access decision impact
ROLE_POWER = {
    "NT-rådet rep":   95,   # National-tier decision (NT-rådet ordf > vice > rep)
    "NSG rep":        85,   # National-tier coordination + sjukvårdsregion lead
    "LK ordförande":  75,   # Regional formulary decision-maker (most direct Pfizer touchpoint)
    "HSD":            70,   # Hälso- och sjukvårdsdirektör — clinical-administrative power
    "Regiondirektör": 65,   # Overall regional direction (political-administrative)
    "HSN ordförande": 55,   # Health committee chair (political)
    "RS ordförande":  50,   # Region-styrelse chair (political — agenda, not formulary)
}

# Confidence multipliers — penalises uncertain identifications
CONFIDENCE_MULTIPLIER = {
    "HIGH":   1.00,
    "MEDIUM": 0.70,
    "LOW":    0.40,
    "VERIFY": 0.20,
}

# Sjukvårdsregion size weight (population-derived; bonus for SVR-spanning roles)
SVR_BONUS = {
    "Stockholm-Gotland":  1.20,
    "Västra":             1.15,
    "Sydsvenska":         1.10,  # fact-check audit naming — matches Python convention
    "Södra":              1.10,  # R convention — accept both
    "Mellansverige":      1.10,
    "Sydöstra":           1.05,
    "Norra":              1.00,
}

# Product relevance per role (which roles influence which products)
# Score 0-1 where 1 = most relevant role for that product
PRODUCT_ROLE_RELEVANCE = {
    # Oral oncology — LK + HSD heavily influence; RD lighter
    "Tukysa":            {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Talzenna":          {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Lorbrena/Lorviqua": {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Ibrance":           {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.85, "NSG rep": 0.65, "Regiondirektör": 0.55, "HSN ordförande": 0.35, "RS ordförande": 0.25},
    # Rare disease — HSD + LK + cardiology/neurology specialty (we don't have those names so weight stays on HSD/LK)
    "Vyndaqel":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.85, "NSG rep": 0.85, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Hympavzi":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.80, "NSG rep": 0.80, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Elrexfio":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.85, "NSG rep": 0.85, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    # Vaccines — RD + HSD + primary care; LK less involved (vaccines are FHM channel not formulary)
    "Abrysvo":           {"LK ordförande": 0.50, "HSD": 1.00, "NT-rådet rep": 0.40, "NSG rep": 0.50, "Regiondirektör": 0.85, "HSN ordförande": 0.55, "RS ordförande": 0.45},
    "Prevenar 20":       {"LK ordförande": 0.55, "HSD": 1.00, "NT-rådet rep": 0.40, "NSG rep": 0.50, "Regiondirektör": 0.85, "HSN ordförande": 0.55, "RS ordförande": 0.45},
    # Migraine — LK + primary care; lower national-tier
    "Vydura":            {"LK ordförande": 1.00, "HSD": 0.75, "NT-rådet rep": 0.45, "NSG rep": 0.40, "Regiondirektör": 0.55, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    # COVID antiviral — separate FHM-led pathway; HSD + RD
    "Paxlovid":          {"LK ordförande": 0.55, "HSD": 0.85, "NT-rådet rep": 0.30, "NSG rep": 0.35, "Regiondirektör": 0.80, "HSN ordförande": 0.45, "RS ordförande": 0.40},
}


# ============================================================================
# DATA LOADING
# ============================================================================
def load_stakeholders():
    """Returns list of stakeholder records from v8 file."""
    wb = openpyxl.load_workbook(SRC_ST, data_only=True)
    ws = wb["Stakeholders"]
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    out = []

    for r in range(2, ws.max_row + 1):
        row = {h: ws.cell(r, i + 1).value for i, h in enumerate(headers)}
        if not row.get("Region"):
            continue

        # Each region produces up to 7 stakeholder records (5 region-level roles + NT-rådet rep + NSG rep)
        sj = row.get("Sjukvårdsregion") or ""

        role_pairs = [
            ("Regiondirektör", row.get("Regiondirektör"), row.get("RD conf"), False),
            ("HSD",            row.get("HSD"),            row.get("HSD conf"), False),
            ("RS ordförande",  row.get("RS ordf"),        row.get("RS conf"), False),
            ("HSN ordförande", row.get("HSN ordf"),       row.get("HSN conf"), False),
            ("LK ordförande",  row.get("LK ordf"),        row.get("LK conf"), False),
            # SVR-level entries — same person may show up across multiple regions in same SVR; tag with svr_role flag
            ("NT-rådet rep",   row.get("NT-rådet rep (SVR)"), "HIGH",          True),
            ("NSG rep",        row.get("NSG rep (SVR)"),     "HIGH",          True),
        ]

        for role, name, conf, is_svr_role in role_pairs:
            if not name:
                continue
            out.append({
                "region": row["Region"],
                "sjukvardsregion": sj,
                "role": role,
                "name": str(name).strip(),
                "confidence": (conf or "VERIFY").upper().split()[0],  # take first word
                "is_svr_role": is_svr_role,
            })

    return out


# ============================================================================
# SCORE COMPUTATION
# ============================================================================
def compute_influence_scores(stakeholders):
    """Returns list of dicts with scoring fields added."""
    out = []
    for s in stakeholders:
        role_power = ROLE_POWER.get(s["role"], 50)
        conf_mult = CONFIDENCE_MULTIPLIER.get(s["confidence"], 0.5)
        svr_bonus = SVR_BONUS.get(s["sjukvardsregion"], 1.0)

        # Base score
        base = role_power * conf_mult

        # SVR-spanning roles get the bonus (NT-rådet rep, NSG rep)
        if s["is_svr_role"]:
            score = base * svr_bonus
        else:
            score = base

        out.append({
            **s,
            "role_power": role_power,
            "confidence_multiplier": conf_mult,
            "svr_bonus": svr_bonus if s["is_svr_role"] else 1.0,
            "influence_score": round(score, 1),
        })
    return out


def aggregate_by_individual(scored):
    """Group by name across UNIQUE roles. SVR-level roles count once per person
    (not once per region in the SVR), since one person holds the role for the whole SVR.
    """
    # First, dedupe to one record per (name, role) pair — keeps highest-scoring instance
    by_name_role = {}
    for s in scored:
        name_clean = s["name"].split("(")[0].strip()
        if not name_clean or name_clean == "?":
            continue
        key = (name_clean, s["role"])
        if key not in by_name_role or s["influence_score"] > by_name_role[key]["influence_score"]:
            by_name_role[key] = s

    # Then aggregate by name — count distinct roles
    by_name = defaultdict(list)
    for (name, role), s in by_name_role.items():
        by_name[name].append(s)

    out = []
    for name, records in by_name.items():
        total_score = sum(r["influence_score"] for r in records)
        roles = sorted({r["role"] for r in records})
        # For SVR-level roles, list the SVR; for region-level, list the region
        role_descriptions = []
        regions_set = set()
        for r in records:
            if r["is_svr_role"]:
                role_descriptions.append(f'{r["role"]} ({r["sjukvardsregion"]})')
                # SVR coverage = all regions in that SVR (compute from scored, since records is deduped)
                svr_regions = sorted({s2["region"] for s2 in scored
                                       if s2["sjukvardsregion"] == r["sjukvardsregion"]})
                for reg in svr_regions:
                    regions_set.add(reg)
            else:
                role_descriptions.append(f'{r["role"]} ({r["region"].replace("Region ", "")})')
                regions_set.add(r["region"])
        confidences = sorted({r["confidence"] for r in records})
        out.append({
            "name": name,
            "n_roles": len(records),
            "roles": " · ".join(role_descriptions),
            "regions_covered": " · ".join(sorted(r.replace("Region ", "").replace("Västra Götalandsregionen", "VGR")
                                                  for r in regions_set)),
            "min_confidence": "HIGH" if all(c == "HIGH" for c in confidences) else
                              ("VERIFY" if "VERIFY" in confidences else
                               ("LOW" if "LOW" in confidences else "MEDIUM")),
            "aggregate_score": round(total_score, 1),
        })
    out.sort(key=lambda x: -x["aggregate_score"])
    return out


def per_product_priorities(scored, top_n=8):
    """Per Pfizer product, return top N stakeholders by (influence × product_relevance)."""
    by_product = {}
    for product, role_relevance in PRODUCT_ROLE_RELEVANCE.items():
        ranked = []
        for s in scored:
            relevance = role_relevance.get(s["role"], 0.5)
            engagement_priority = s["influence_score"] * relevance
            ranked.append({
                **s,
                "product": product,
                "product_relevance": relevance,
                "engagement_priority": round(engagement_priority, 1),
            })
        ranked.sort(key=lambda x: -x["engagement_priority"])
        # Deduplicate by name (keep highest)
        seen = set()
        deduped = []
        for r in ranked:
            n = r["name"].split("(")[0].strip()
            if n in seen:
                continue
            seen.add(n)
            deduped.append(r)
            if len(deduped) >= top_n:
                break
        by_product[product] = deduped
    return by_product


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
    s = (tag or "").upper()
    return PatternFill("solid", fgColor={
        "HIGH": C_OBS, "MEDIUM": C_MOD, "LOW": C_HYP, "VERIFY": C_NPV
    }.get(s, "FFFFFF"))


def heat_fill(score, scale_max=120):
    """3-step heat fill based on score."""
    norm = min(score, scale_max) / scale_max
    if norm >= 0.67: return PatternFill("solid", fgColor="1F4E79")
    if norm >= 0.33: return PatternFill("solid", fgColor="9CC2E5")
    return PatternFill("solid", fgColor="DEEBF7")


def build():
    print(f"Loading {SRC_WB.name} + {SRC_ST.name} ...")
    shutil.copy(SRC_WB, DST)
    wb = openpyxl.load_workbook(DST)

    print(f"Initial sheet count: {len(wb.sheetnames)}")

    # Load + score
    raw = load_stakeholders()
    print(f"Loaded {len(raw)} stakeholder records")

    scored = compute_influence_scores(raw)
    individuals = aggregate_by_individual(scored)
    products = per_product_priorities(scored)

    insert_idx = wb.sheetnames.index("Assumptions ledger") + 1

    # ============================================================================
    # SHEET 1: OPP - Stakeholder influence (per-region/role)
    # ============================================================================
    print("Writing 'OPP - Stakeholder influence' sheet ...")
    ws = wb.create_sheet("OPP - Stakeholder influence", index=insert_idx)
    ws.cell(row=1, column=1, value="Stakeholder influence scores — per-region × per-role")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=9)

    ws.cell(row=2, column=1, value=(
        "Influence Score = Role Power × Confidence Multiplier (× SVR Bonus for NT-rådet + NSG reps). "
        "Confidence: Modeled (rule-based scoring formula). Names + roles inherit Observed status from "
        "stakeholder_mapping_v8.xlsx. This sheet does NOT modify name verification."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)

    headers = ["Region", "Sjukvårdsregion", "Role", "Name", "Confidence",
               "Role power", "Conf. multiplier", "SVR bonus", "Influence score"]
    for i, h in enumerate(headers, start=1):
        make_header(ws.cell(row=4, column=i), h)

    sorted_scored = sorted(scored, key=lambda x: -x["influence_score"])
    for ri, s in enumerate(sorted_scored, start=5):
        vals = [
            s["region"], s["sjukvardsregion"], s["role"], s["name"],
            s["confidence"], s["role_power"],
            f"{s['confidence_multiplier']:.2f}",
            f"{s['svr_bonus']:.2f}",
            s["influence_score"],
        ]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 5:
                cell.fill = conf_fill(v)
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 9:
                cell.fill = heat_fill(s["influence_score"])
                cell.font = Font(name="Calibri", size=10, bold=True,
                                  color="FFFFFF" if s["influence_score"] >= 80 else "000000")

    widths = [22, 22, 18, 30, 12, 12, 14, 12, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{4 + len(sorted_scored)}"

    # ============================================================================
    # SHEET 2: OPP - Named individuals (aggregated by person)
    # ============================================================================
    print("Writing 'OPP - Named individuals' sheet ...")
    ws2 = wb.create_sheet("OPP - Named individuals", index=insert_idx + 1)
    ws2.cell(row=1, column=1, value="Named individuals ranked by aggregate influence (multi-role consolidation)")
    ws2.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

    ws2.cell(row=2, column=1, value=(
        "Same person counted once with summed score across all roles they hold. Cornerstone individuals "
        "(those with multi-role exposure or SVR-level reach) surface here. Confidence = lowest "
        "confidence across their roles."
    ))
    ws2.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws2.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)

    h2 = ["Rank", "Name", "Roles held", "Regions covered", "Min confidence", "Aggregate score"]
    for i, h in enumerate(h2, start=1):
        make_header(ws2.cell(row=4, column=i), h)

    for ri, ind in enumerate(individuals, start=5):
        vals = [ri - 4, ind["name"], ind["roles"], ind["regions_covered"],
                ind["min_confidence"], ind["aggregate_score"]]
        for ci, v in enumerate(vals, start=1):
            cell = ws2.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 2:
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 5:
                cell.fill = conf_fill(v)
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 6:
                cell.fill = heat_fill(ind["aggregate_score"], scale_max=200)
                cell.font = Font(name="Calibri", size=10, bold=True,
                                  color="FFFFFF" if ind["aggregate_score"] >= 130 else "000000")

    widths2 = [6, 30, 65, 50, 14, 14]
    for i, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A5"

    # ============================================================================
    # SHEET 3: OPP - Validation queue
    # ============================================================================
    print("Writing 'OPP - Validation queue' sheet ...")
    ws3 = wb.create_sheet("OPP - Validation queue", index=insert_idx + 2)
    ws3.cell(row=1, column=1, value="Stakeholders pending validation — DO NOT show as cornerstone in Pfizer-facing materials")
    ws3.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_RED)
    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

    ws3.cell(row=2, column=1, value=(
        "audit #2: 'Do not show unverified names as cornerstone stakeholders. Show them in a "
        "validation queue instead.' This sheet lists every stakeholder with confidence < HIGH for "
        "Jonas Fuks pass + Pfizer field-team validation."
    ))
    ws3.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws3.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)

    h3 = ["Region", "Role", "Name", "Confidence", "Influence (if HIGH-validated)", "Verification action"]
    for i, h in enumerate(h3, start=1):
        make_header(ws3.cell(row=4, column=i), h)

    queue = [s for s in sorted_scored if s["confidence"] != "HIGH"]
    for ri, s in enumerate(queue, start=5):
        # If this name had been HIGH-confidence, what would the score be?
        full_score = s["role_power"] * 1.0 * (s["svr_bonus"] if s["is_svr_role"] else 1.0)
        action_text = ""
        if s["confidence"] == "VERIFY":
            action_text = "Direct web check on region website + tromanpublik OR Jonas pass"
        elif s["confidence"] == "MEDIUM":
            action_text = "Single-source name; cross-check against second source OR Jonas pass"
        else:
            action_text = "LOW confidence — assume name unreliable until validated"

        vals = [s["region"], s["role"], s["name"], s["confidence"],
                f"{full_score:.1f} (currently {s['influence_score']})",
                action_text]
        for ci, v in enumerate(vals, start=1):
            cell = ws3.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 4:
                cell.fill = conf_fill(v)
                cell.font = Font(name="Calibri", size=10, bold=True)

    widths3 = [22, 18, 30, 12, 22, 50]
    for i, w in enumerate(widths3, start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w
    ws3.freeze_panes = "A5"

    # ============================================================================
    # SHEET 4: OPP - Engagement priorities (per product)
    # ============================================================================
    print("Writing 'OPP - Engagement priorities' sheet ...")
    ws4 = wb.create_sheet("OPP - Engagement priorities", index=insert_idx + 3)
    ws4.cell(row=1, column=1, value="Top 8 engagement targets per Pfizer product")
    ws4.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws4.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    ws4.cell(row=2, column=1, value=(
        "Engagement priority = stakeholder influence × product-role relevance. Per product, top 8 "
        "deduplicated by name (so Pia Näsvall doesn't appear twice for Vyndaqel even though she holds "
        "HSD + NSG rep). Use as the named-target list for portfolio plays + deck Part B."
    ))
    ws4.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws4.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)

    h4 = ["Product", "Rank", "Name", "Role", "Region", "Confidence", "Role relevance", "Engagement priority"]
    for i, h in enumerate(h4, start=1):
        make_header(ws4.cell(row=4, column=i), h)

    row = 5
    for product, top_list in products.items():
        for rank, p in enumerate(top_list, 1):
            vals = [product, rank, p["name"], p["role"], p["region"],
                    p["confidence"], f"{p['product_relevance']:.2f}", p["engagement_priority"]]
            for ci, v in enumerate(vals, start=1):
                cell = ws4.cell(row, ci, value=v)
                cell.font = Font(name="Calibri", size=10)
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = BORDER
                if ci == 1 and rank == 1:
                    cell.font = Font(name="Calibri", size=10, bold=True, color=PF_NAVY)
                if ci == 6:
                    cell.fill = conf_fill(v)
                    cell.font = Font(name="Calibri", size=10, bold=True)
                if ci == 8:
                    cell.fill = heat_fill(p["engagement_priority"])
                    cell.font = Font(name="Calibri", size=10, bold=True,
                                      color="FFFFFF" if p["engagement_priority"] >= 80 else "000000")
            row += 1
        row += 1  # blank row between products

    widths4 = [20, 6, 30, 18, 22, 12, 14, 14]
    for i, w in enumerate(widths4, start=1):
        ws4.column_dimensions[get_column_letter(i)].width = w
    ws4.freeze_panes = "A5"

    # ======== Update README ========
    rd = wb["README"]
    r = rd.max_row + 2
    rd.cell(row=r, column=1, value="STAKEHOLDER INFLUENCE SCORING (v20, 2026-04-25)")
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    rd.cell(row=r, column=1, value=(
        "Analytical layer over stakeholder_mapping_v8.xlsx. Influence Score = Role Power × Confidence "
        "Multiplier (× SVR Bonus for NT-rådet + NSG reps). 4 new sheets: 'OPP - Stakeholder influence' "
        "(per-region/role), 'OPP - Named individuals' (aggregated cornerstones), 'OPP - Validation "
        "queue' (non-HIGH confidence pending Jonas), 'OPP - Engagement priorities' (top 8 per product). "
        "Does NOT touch name verification — that's owned by the fact-check agent lane."
    ))
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    rd.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    # CSV
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "region", "sjukvardsregion", "role", "name", "confidence",
            "role_power", "confidence_multiplier", "svr_bonus", "influence_score"
        ])
        w.writeheader()
        for s in sorted_scored:
            w.writerow({k: s[k] for k in w.fieldnames})
    print(f"Wrote {CSV_OUT.name}")

    # Summary
    print()
    print(f"Total stakeholder records: {len(scored)}")
    print(f"Named individuals (deduped): {len(individuals)}")
    print(f"Validation queue: {len(queue)} (confidence < HIGH)")
    print()
    print("Top 10 named individuals by aggregate influence:")
    for i, ind in enumerate(individuals[:10], 1):
        print(f"  {i:>2}. {ind['name']:<28} | {ind['n_roles']} roles | min conf {ind['min_confidence']:<6} | score {ind['aggregate_score']:>6.1f}")
    print()
    print("Confidence breakdown of all stakeholder records:")
    conf_counts = defaultdict(int)
    for s in scored:
        conf_counts[s["confidence"]] += 1
    for c in ["HIGH", "MEDIUM", "LOW", "VERIFY"]:
        print(f"  {c:<8}: {conf_counts.get(c, 0)}")

    return scored, individuals, queue


if __name__ == "__main__":
    build()
