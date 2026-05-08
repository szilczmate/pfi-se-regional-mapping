# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v22.xlsx — adds transparency layer for derived variables.

Two new sheets:
  1. "Derived variables" — single index of every score, rank, composite, and
     classification we built. Each row gives: variable, sheet location, formula,
     inputs, author choices, confidence tag, where explained in the client docs.
  2. "Product-Role Relevance" — the 11×7 author-judgment table used in the
     Stakeholder Influence × Product engagement-priority calculation. Currently
     this 77-cell table only exists in Python source; this sheet exposes it.

Plus:
  - Restores the 7-dimension Opportunity weights into the matrix sheet header
    (currently only the Actionability weights are visible).
"""
import sys
from pathlib import Path
import shutil

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v21.xlsx"
DST = ROOT / "working/data/master/master_workbook_v22.xlsx"

PF_NAVY = "003F7F"; PF_GREY = "4B5563"; PF_RED = "E4002B"
C_OBS = "C6EFCE"; C_MOD = "FFEB9C"; C_HYP = "FFC7CE"; C_NPV = "D9D2E9"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ============================================================================
# THE DERIVED-VARIABLES INDEX (every score, rank, composite, classification)
# ============================================================================
DERIVED = [
    # ---------- Scores in OPP - Region x Product matrix (231 cells) ----------
    {
        "id": "DV-01",
        "variable": "Epi fit score",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Epi",
        "formula": "Per-product epidemiological denominator (e.g. for Tukysa: breast_ca_per_100k × pop × 0.20 HER2+ × 0.30 brain mets), normalised across 21 regions to 0–100 (highest region = 100)",
        "inputs": "Regional cancer rates (RCC), pop demographics (SCB), per-product clinical-fraction proxies (literature)",
        "author_choices": "Per-product clinical fractions (HER2+, BRCA, ALK+, etc.) — see DV-19 product config",
        "confidence": "Modeled (Pfizer epi-validation closes this — see Validation Gate 5)",
        "explained_in": "Report Part III §10 + Methodology Pt 2 worked examples",
    },
    {
        "id": "DV-02",
        "variable": "Uptake score",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Uptake",
        "formula": "Region's observed Pfizer presence per product. For oral Rx: patients/100k from Rx 2024 snapshot. For vaccines: Pfizer market share %. For hospital-admin (Elrexfio, Hympavzi): set to 50 (neutral) and tagged Needs Pfizer validation. Then normalised 0–100.",
        "inputs": "Rx 2024 snapshot, Vaccine market share",
        "author_choices": "Hospital-admin neutral default = 50",
        "confidence": "Observed → Modeled (the normalisation is Modeled)",
        "explained_in": "Report Part III §9 + Methodology",
    },
    {
        "id": "DV-03",
        "variable": "Growth score",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Growth",
        "formula": "Demographic tailwind. For age-driven products (Vyndaqel, Abrysvo, Prevenar 20, Paxlovid, Elrexfio): 65+ growth % 2024→2040 from SCB projections. For breast cancer products (Ibrance, Talzenna, Tukysa): pop-women 50+ growth proxy. For lung (Lorbrena): general pop growth. For migraine (Vydura): women 15-44 growth. Normalised 0–100.",
        "inputs": "SCB projections (Future — pop projections sheet)",
        "author_choices": "Per-product demographic mapping rule",
        "confidence": "Modeled (SCB projections are themselves Modeled)",
        "explained_in": "Report Part I §2",
    },
    {
        "id": "DV-04",
        "variable": "Access score (inverted friction)",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Access",
        "formula": "Composite of (a) inverted median specialist wait, (b) per-capita pharma budget, (c) specialist density. Higher = lower friction = better. Normalised 0–100.",
        "inputs": "Wait times sheet, Region master columns (Pharma förmån/inv, Specialist läkare)",
        "author_choices": "Equal weighting of 3 sub-components",
        "confidence": "Modeled",
        "explained_in": "Report Part II §8",
    },
    {
        "id": "DV-05",
        "variable": "Stakeholder leverage score",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Stake",
        "formula": "Sjukvårdsregion-level cornerstone bump (Sydöstra: 100 — Lindström+Ekelund+Nyberg Finn; Norra: 90; Stockholm-Gotland: 80; Mellansverige: 80; Västra: 70; Sydsvenska: 60), then per-region adjustment for HIGH-confidence stakeholder count.",
        "inputs": "Stakeholder mapping v8, governance box per region",
        "author_choices": "Sjukvårdsregion-level cornerstone scores; weighting against per-region HIGH-conf count",
        "confidence": "Modeled (over Observed names)",
        "explained_in": "Report Part IV §16 (stakeholder influence)",
    },
    {
        "id": "DV-06",
        "variable": "Competitive score (inverted threat)",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Compet",
        "formula": "Inverted competitor threat. Per-product national threat baseline (HIGH=80, MEDIUM=50, LOW=20) inverted to 100−threat. Then regional modifier — e.g. Stockholm + VGR Ibrance: threat bumped to 95 (Kisqali) → score 5.",
        "inputs": "Per-product competitor profile (NT-rådet status v2, Competitor pipeline sheet)",
        "author_choices": "Threat baselines per product (DV-19); regional modifier rules",
        "confidence": "Modeled + Hypothesis (Stockholm/VGR Ibrance modifier rests on Kisqali substitution hypothesis)",
        "explained_in": "Report Part III §11.2",
    },
    {
        "id": "DV-07",
        "variable": "Policy relevance score",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Policy",
        "formula": "Per-product NT-rådet status base score: NT_RECOMMENDATION=90, NATIONAL_AGREEMENT=70, REGIONAL_CANCER_CENTRE=60, REGIONAL_ASSESSMENT=40, ARCHIVED=50, AWAIT/AVVAKTA=25, TOO_NEW=30, OUT_OF_SCOPE=50. Plus regional modifier by regional plan tier (HIGH +10, LOW −10).",
        "inputs": "NT-rådet status v2, Regional plans + angles v2",
        "author_choices": "NT-status to score mapping; regional plan tier bonus",
        "confidence": "Observed (NT status) → Modeled (mapping)",
        "explained_in": "Report Part II §6",
    },
    {
        "id": "DV-08",
        "variable": "Opportunity composite",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Opportunity",
        "formula": "0.25·Epi + 0.10·Uptake + 0.15·Growth + 0.10·Access + 0.15·Stakeholder + 0.15·Competitive + 0.10·Policy. Sum of weights = 1.00.",
        "inputs": "DV-01 through DV-07",
        "author_choices": "The 7 weights (epi-fit weighted highest at 25% because no patients = no opportunity)",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §14 + this index",
    },

    # ---------- Actionability axis ----------
    {
        "id": "DV-09",
        "variable": "Governance reach score",
        "type": "Score 0–100",
        "sheet": "OPP - Actionability inputs",
        "column": "Governance reach",
        "formula": "(HIGH-confidence governance role count / 5) × 70 + 15 if has-national-rep + sjukvårdsregion cornerstone bonus (Stockholm-Gotland +5, Mellansverige +6, Sydöstra +7, Västra +4, Sydsvenska +4, Norra +7).",
        "inputs": "stakeholder_mapping_v8.xlsx",
        "author_choices": "70-15-X structure; SVR cornerstone bonuses",
        "confidence": "Modeled (over Observed inputs)",
        "explained_in": "Report Part IV §15",
    },
    {
        "id": "DV-10",
        "variable": "Pfizer footprint score",
        "type": "Score 0–100",
        "sheet": "OPP - Actionability inputs",
        "column": "Pfizer footprint",
        "formula": "Mean of two normalised inputs: (a) sum of patients/100k across 7 oral Pfizer products, (b) vaccine sell-in /inv (SEK/yr). Each normalised across 21 regions to 0–100, then averaged with equal weight.",
        "inputs": "Rx 2024 snapshot, Region master Vaccine sell-in",
        "author_choices": "Equal weighting of Rx breadth and vaccine sell-in",
        "confidence": "Observed → Modeled (composite)",
        "explained_in": "Report Part IV §15",
    },
    {
        "id": "DV-11",
        "variable": "Policy permissiveness score",
        "type": "Score 0–100",
        "sheet": "OPP - Actionability inputs",
        "column": "Policy permissiveness",
        "formula": "Regional plan tier base (HIGH=80, MEDIUM=55, LOW=30, no plan=45) + min(15, keyword density / 8). Keyword density = sum of cancer + vaccine + äldre + kronisk + tillgänglig + digital + nära vård + prevention + jämlik + primärvård + forskning counts in regional plan PDF.",
        "inputs": "Regional plans + angles v2",
        "author_choices": "Tier→base mapping; keyword density bonus formula (+15 cap, /8 divisor)",
        "confidence": "Modeled (Observed plan tier + Modeled bonus)",
        "explained_in": "Report Part II §7",
    },
    {
        "id": "DV-12",
        "variable": "Actionability composite",
        "type": "Score 0–100",
        "sheet": "OPP - Region x Product matrix",
        "column": "Actionability",
        "formula": "0.40·Governance + 0.35·Footprint + 0.25·Policy permissiveness + per-product modifier (Elrexfio/Hympavzi −12, Abrysvo −8, Paxlovid −3, others 0). Clamped to [0, 100].",
        "inputs": "DV-09, DV-10, DV-11, per-product modifier",
        "author_choices": "Weights 40/35/25; per-product penalties",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §15",
    },
    {
        "id": "DV-13",
        "variable": "Quadrant assignment",
        "type": "Categorical (HH/HL/LH/LL)",
        "sheet": "OPP - Region x Product matrix",
        "column": "Quadrant",
        "formula": "Opp ≥ 45 AND Act ≥ 60 → HH (Priority Focus). Opp ≥ 45 AND Act < 60 → HL (Engagement Build). Opp < 45 AND Act ≥ 60 → LH (Quick Win). Otherwise LL (Deprioritise).",
        "inputs": "DV-08 + DV-12",
        "author_choices": "Thresholds 45 and 60. These are data-median-aligned (chose after first run with 50/50 yielded 0 HL cells).",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §15",
    },
    {
        "id": "DV-14",
        "variable": "Recommended action keyword",
        "type": "Categorical (Build/Defend/Cornerstone/Position/Watch/Maintain)",
        "sheet": "OPP - Region x Product matrix",
        "column": "Action",
        "formula": "Rule engine: if epi>60 + uptake<30 → Build. If uptake>70 + competitive<30 → Defend. If epi>80 + stakeholder>70 → Cornerstone. If access friction high (access<30) → Watch. If growth>70 + uptake<50 → Position. Else → Maintain.",
        "inputs": "DV-01 through DV-07",
        "author_choices": "Rule thresholds (60/30/70/80/50)",
        "confidence": "Modeled (deterministic rules)",
        "explained_in": "Report Part IV §14",
    },

    # ---------- Regional archetypes ----------
    {
        "id": "DV-15",
        "variable": "Regional archetype tags (6 categorical)",
        "type": "Multi-tag categorical",
        "sheet": "OPP - Regional archetypes",
        "column": "All tags",
        "formula": "Each region tested against 6 trigger rules. Multi-tag allowed. Rules: Academic specialist = region hosts university hospital + RCC. Aging vaccine-growth = pop 65+ ≥ 22% OR 65+ growth ≥ 25%. Rare-disease hotspot = Vyndaqel rate ≥ 5/100k OR known hereditary cluster. Equity/access-friction = top-5 SES need rank OR specialist wait ≥ 65 days. High-governance = listed cornerstone-stakeholder concentration regions. Competitive defense = listed regions with significant Pfizer footprint + active competitive pressure.",
        "inputs": "Region master, Rx 2024 snapshot, Health equity overlay, Wait times",
        "author_choices": "All 6 trigger rule thresholds. Threshold choices documented in OPP - Archetype playbooks sheet.",
        "confidence": "Modeled (rule-based)",
        "explained_in": "Report Part IV §13 + OPP - Archetype playbooks sheet",
    },

    # ---------- Health equity ----------
    {
        "id": "DV-16",
        "variable": "Viti health-equity composite rank",
        "type": "Rank 1–21",
        "sheet": "Health equity overlay",
        "column": "SES composite rank (1=highest need)",
        "formula": "For each region, rank on each of 4 components (foreign-born % DESC, eftergymnasial % ASC i.e. low edu = high need, premature mortality DESC, healthcare-amenable mortality DESC). 4 ranks averaged with equal weights. Composite mean re-sorted to give final 1–21 rank where 1 = highest need.",
        "inputs": "SCB BE0101 + UF0506 + Kolada N79190 + Kolada N72461",
        "author_choices": "Equal weighting of 4 components. Choice of these 4 components.",
        "confidence": "Modeled (over Observed inputs)",
        "explained_in": "Report Part I §3 + Methodology Pt 1 dedicated section",
    },

    # ---------- Stakeholder layer ----------
    {
        "id": "DV-17",
        "variable": "Stakeholder Influence Score",
        "type": "Score 0–~120",
        "sheet": "OPP - Stakeholder influence",
        "column": "Influence score",
        "formula": "Role Power × Confidence Multiplier × SVR Bonus (only for SVR-spanning roles like NT-rådet rep + NSG rep). Role Power: NT-rådet rep=95, NSG rep=85, LK ordf=75, HSD=70, RD=65, HSN ordf=55, RS ordf=50. Confidence Multiplier: HIGH=1.00, MEDIUM=0.70, LOW=0.40, VERIFY=0.20. SVR Bonus: 1.00–1.20 by sjukvårdsregion size.",
        "inputs": "stakeholder_mapping_v8.xlsx",
        "author_choices": "Role power weights (95/85/75/70/65/55/50). Confidence multipliers. SVR bonus range.",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §16 + Methodology Pt 1 layer 7",
    },
    {
        "id": "DV-18",
        "variable": "Aggregate Influence (per named individual)",
        "type": "Sum of distinct role scores",
        "sheet": "OPP - Named individuals",
        "column": "Aggregate score",
        "formula": "For each unique person, sum of Influence Scores across distinct roles they hold. SVR-spanning roles (NT-rådet rep + NSG rep) counted once per person, not once per region in the SVR (de-duplication fix applied 2026-04-25).",
        "inputs": "DV-17",
        "author_choices": "De-duplication rule: one (name, role) pair scored once",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §16",
    },
    {
        "id": "DV-19",
        "variable": "Engagement Priority (per product per stakeholder)",
        "type": "Score",
        "sheet": "OPP - Engagement priorities",
        "column": "Engagement priority",
        "formula": "Influence Score (DV-17) × Product-Role Relevance. Product-Role Relevance is the 11×7 author-judgment table — see new \"Product-Role Relevance\" sheet in this workbook for the full 77 cells.",
        "inputs": "DV-17 + Product-Role Relevance table",
        "author_choices": "All 77 cells of the Product-Role Relevance table are author judgment",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §16 + Product-Role Relevance sheet (this workbook)",
    },

    # ---------- Scenario sensitivity ----------
    {
        "id": "DV-20",
        "variable": "Net revenue scenario multipliers",
        "type": "3 fixed multipliers",
        "sheet": "Scenario sensitivity",
        "column": "Net Conservative / Net Base / Net Upside",
        "formula": "Per Pfizer oral Rx product: Gross = patients × TLV list × 12 months. Net Conservative = Gross × 0.60 (rebate 30% + regional discount 15%). Net Base = Gross × 0.80 (rebate 15% + regional discount 5%). Net Upside = Gross × 0.95 (rebate 5%, no regional discount).",
        "inputs": "Rx 2024 patient counts, TLV list prices",
        "author_choices": "All three multipliers (0.60/0.80/0.95) are illustrative. Validation Gate 1 collapses these to Pfizer-confirmed values.",
        "confidence": "Modeled + Needs Pfizer validation",
        "explained_in": "Report Part VII §27 + Methodology + Assumptions Ledger ASM-01 to ASM-07",
    },

    # ---------- Penetration gap ----------
    {
        "id": "DV-21",
        "variable": "Penetration gap (per region per product)",
        "type": "Number (signed integer + %)",
        "sheet": "n/a (R analysis 1, figure source)",
        "column": "n/a — see analysis1_penetration_gap.csv",
        "formula": "Gap (count) = observed patients − expected. Expected = national rate per 100k × regional population / 1e5. Gap (%) = (observed − expected) / max(expected, 1) × 100.",
        "inputs": "Rx 2024 + Region master populations",
        "author_choices": "\"Expected\" baseline uses national rate × regional population — Modeled benchmark. A more refined benchmark would use sub-population denominators (HER2+, BRCA-mut, etc.).",
        "confidence": "Modeled",
        "explained_in": "Report Part III §10 + Figure 10.1 caption",
    },

    # ---------- Cluster + regression ----------
    {
        "id": "DV-22",
        "variable": "Region cluster assignment (k=2)",
        "type": "Categorical",
        "sheet": "n/a (R analysis 4)",
        "column": "see analysis4_cluster_assignments.csv",
        "formula": "Hierarchical clustering, Ward's method, Euclidean distance on 14 normalised features (pct_65, log_pop, utrikes_fodda_pct, eftergymn_pct, premature_mort, breast_ca_rate, median_wait_spec, plus 7 Rx rates per product). k=2 chosen by silhouette score.",
        "inputs": "Region master + Rx 2024 + Health equity",
        "author_choices": "14 feature selection. Ward linkage. Euclidean distance. Silhouette-optimum k.",
        "confidence": "Modeled",
        "explained_in": "Report Part IV §13 (clusters background to archetypes)",
    },

    # ---------- Confidence framework ----------
    {
        "id": "DV-23",
        "variable": "Confidence tags (Observed/Modeled/Hypothesis/Needs Pfizer validation)",
        "type": "4-tag categorical taxonomy",
        "sheet": "Evidence ledger",
        "column": "Confidence",
        "formula": "Decision rule per tag, see Methodology Part 2. Combined tags allowed (e.g. \"Modeled + Needs Pfizer validation\"). Display: green/yellow/red/purple light fill, prioritising the most cautious tag visually.",
        "inputs": "Author judgment per claim, applied through the workbook",
        "author_choices": "The 4-tag taxonomy itself, the decision rules per tag, and the per-claim assignment",
        "confidence": "(Meta-framework, not itself tagged)",
        "explained_in": "Methodology Part 2 (full taxonomy + worked examples)",
    },
]


# ============================================================================
# PRODUCT-ROLE RELEVANCE TABLE (the 11 × 7 = 77 author-judgment cells)
# ============================================================================
PRODUCT_ROLE_RELEVANCE = {
    # Oral oncology
    "Tukysa":            {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Talzenna":          {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Lorbrena/Lorviqua": {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.90, "NSG rep": 0.70, "Regiondirektör": 0.50, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Ibrance":           {"LK ordförande": 1.00, "HSD": 0.85, "NT-rådet rep": 0.85, "NSG rep": 0.65, "Regiondirektör": 0.55, "HSN ordförande": 0.35, "RS ordförande": 0.25},
    # Rare disease
    "Vyndaqel":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.85, "NSG rep": 0.85, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Hympavzi":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.80, "NSG rep": 0.80, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Elrexfio":          {"LK ordförande": 0.90, "HSD": 1.00, "NT-rådet rep": 0.85, "NSG rep": 0.85, "Regiondirektör": 0.60, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    # Vaccines
    "Abrysvo":           {"LK ordförande": 0.50, "HSD": 1.00, "NT-rådet rep": 0.40, "NSG rep": 0.50, "Regiondirektör": 0.85, "HSN ordförande": 0.55, "RS ordförande": 0.45},
    "Prevenar 20":       {"LK ordförande": 0.55, "HSD": 1.00, "NT-rådet rep": 0.40, "NSG rep": 0.50, "Regiondirektör": 0.85, "HSN ordförande": 0.55, "RS ordförande": 0.45},
    # Migraine, antiviral
    "Vydura":            {"LK ordförande": 1.00, "HSD": 0.75, "NT-rådet rep": 0.45, "NSG rep": 0.40, "Regiondirektör": 0.55, "HSN ordförande": 0.30, "RS ordförande": 0.20},
    "Paxlovid":          {"LK ordförande": 0.55, "HSD": 0.85, "NT-rådet rep": 0.30, "NSG rep": 0.35, "Regiondirektör": 0.80, "HSN ordförande": 0.45, "RS ordförande": 0.40},
}

ROLES_ORDER = ["LK ordförande", "HSD", "NT-rådet rep", "NSG rep",
               "Regiondirektör", "HSN ordförande", "RS ordförande"]


# ============================================================================
# WORKBOOK BUILD
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


def relevance_fill(value):
    """Heat-fill for product-role relevance (0-1 scale)."""
    if value >= 0.85: return PatternFill("solid", fgColor="1F4E79")
    if value >= 0.70: return PatternFill("solid", fgColor="9CC2E5")
    if value >= 0.50: return PatternFill("solid", fgColor="DEEBF7")
    return PatternFill("solid", fgColor="F8FAFC")


def relevance_text_color(value):
    return "FFFFFF" if value >= 0.85 else "000000"


def build():
    print(f"Loading {SRC.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    print(f"Initial sheet count: {len(wb.sheetnames)}")

    # ============================================================================
    # SHEET 1: Derived variables index
    # ============================================================================
    print("Writing 'Derived variables' index sheet ...")
    insert_idx = wb.sheetnames.index("Evidence ledger") + 1
    if "Derived variables" in wb.sheetnames:
        del wb["Derived variables"]
    ws = wb.create_sheet("Derived variables", index=insert_idx)

    ws.cell(row=1, column=1, value="Derived variables — single index of every score, rank, composite, and classification we built")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    ws.cell(row=2, column=1, value=(
        "For each derived variable: where it lives in the workbook, the formula, the inputs, the author choices, "
        "the confidence tag, and where the construction is explained in the client-facing documents. This sheet "
        "is the transparency single-source-of-truth — if you can't find a formula here, please flag it."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)

    headers = ["ID", "Variable", "Type", "Sheet · Column", "Formula",
               "Inputs", "Author choices", "Confidence", "Explained in"]
    for i, h in enumerate(headers, start=1):
        make_header(ws.cell(row=4, column=i), h)

    for ri, dv in enumerate(DERIVED, start=5):
        loc = f"{dv['sheet']}\n  → col: {dv['column']}"
        vals = [dv["id"], dv["variable"], dv["type"], loc, dv["formula"],
                dv["inputs"], dv["author_choices"], dv["confidence"], dv["explained_in"]]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=9.5)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 1:
                cell.font = Font(name="Calibri", size=10, bold=True, color=PF_NAVY)
            if ci == 2:
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 8:
                cell.fill = conf_fill(v) or PatternFill()
                cell.font = Font(name="Calibri", size=9, bold=True)
        ws.row_dimensions[ri].height = 95

    widths = [8, 24, 18, 22, 60, 28, 32, 22, 30]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{4 + len(DERIVED)}"

    # ============================================================================
    # SHEET 2: Product-Role Relevance (11 × 7)
    # ============================================================================
    print("Writing 'Product-Role Relevance' sheet ...")
    insert_idx_2 = wb.sheetnames.index("OPP - Engagement priorities") + 1
    if "Product-Role Relevance" in wb.sheetnames:
        del wb["Product-Role Relevance"]
    ws2 = wb.create_sheet("Product-Role Relevance", index=insert_idx_2)

    ws2.cell(row=1, column=1, value="Product-Role Relevance table — author-judgment weights (11 products × 7 roles = 77 cells)")
    ws2.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    ws2.cell(row=2, column=1, value=(
        "Used in the Engagement Priority calculation (DV-19): Engagement priority = Stakeholder Influence × this cell's weight. "
        "Weights are 0–1 scale (1.00 = role most directly drives access to this product). All 77 cells are author judgment. "
        "Pfizer can replace with field-team-validated values without any data refresh — the framework is parameterised."
    ))
    ws2.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws2.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws2.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)

    # Header row: roles
    make_header(ws2.cell(row=4, column=1), "Product")
    for ci, role in enumerate(ROLES_ORDER, start=2):
        make_header(ws2.cell(row=4, column=ci), role)

    # Body
    for ri, (product, weights) in enumerate(PRODUCT_ROLE_RELEVANCE.items(), start=5):
        c0 = ws2.cell(row=ri, column=1, value=product)
        c0.font = Font(name="Calibri", size=10, bold=True, color=PF_NAVY)
        c0.alignment = Alignment(vertical="center", wrap_text=True)
        c0.border = BORDER
        for ci, role in enumerate(ROLES_ORDER, start=2):
            v = weights.get(role, 0.5)
            cell = ws2.cell(row=ri, column=ci, value=f"{v:.2f}")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = BORDER
            cell.fill = relevance_fill(v)
            cell.font = Font(name="Calibri", size=10, bold=True,
                              color=relevance_text_color(v))

    widths2 = [22, 16, 14, 14, 14, 18, 16, 14]
    for i, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "B5"

    # Legend row
    legend_row = 5 + len(PRODUCT_ROLE_RELEVANCE) + 2
    ws2.cell(legend_row, 1, "Legend").font = Font(bold=True, size=10, color=PF_NAVY)
    legend_items = [(0.95, "0.85+ — primary"), (0.75, "0.70–0.85 — strong"),
                    (0.60, "0.50–0.70 — moderate"), (0.30, "<0.50 — peripheral")]
    for i, (val, label) in enumerate(legend_items):
        c = ws2.cell(legend_row + 1 + i, 1, "")
        c.fill = relevance_fill(val)
        d = ws2.cell(legend_row + 1 + i, 2, label)
        d.font = Font(size=10)

    # ============================================================================
    # FIX: Restore 7-dimension Opportunity weights into matrix sheet header
    # ============================================================================
    print("Restoring 7-dimension Opportunity weights to matrix sheet header ...")
    ws_m = wb["OPP - Region x Product matrix"]
    # Add a new line below row 3 with the opportunity weights
    # Insert above row 4 (between row 3 actionability and row 4 something)
    # Actually we'll just append into row 3's text since the text cell is merged
    current_r3 = ws_m.cell(row=3, column=1).value or ""
    new_r3 = (current_r3 + "    Opportunity weights — epi:25%  uptake:10%  growth:15%  "
                          "access:10%  stakeholder:15%  competitive:15%  policy:10%")
    ws_m.cell(row=3, column=1).value = new_r3
    ws_m.cell(row=3, column=1).font = Font(name="Calibri", size=9, italic=True, color=PF_GREY)
    ws_m.cell(row=3, column=1).alignment = Alignment(wrap_text=True)

    # ============================================================================
    # Update README
    # ============================================================================
    print("Updating README ...")
    rd = wb["README"]
    r = rd.max_row + 2
    rd.cell(row=r, column=1, value="DERIVED VARIABLES INDEX (v22, 2026-04-25)")
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    rd.cell(row=r, column=1, value=(
        "New 'Derived variables' sheet documents every score, rank, composite, and classification we "
        "built — formula, inputs, author choices, confidence tag, and where each is explained in the "
        "client docs. Twenty-three derived variables indexed (DV-01 to DV-23). New 'Product-Role "
        "Relevance' sheet exposes the 11×7 author-judgment table previously embedded only in Python "
        "source. Matrix sheet header now also documents the 7-dimension Opportunity weights "
        "(previously only Actionability weights were visible)."
    ))
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    rd.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    # Summary
    print()
    print(f"Total derived variables documented: {len(DERIVED)}")
    print(f"Product-Role Relevance cells exposed: {len(PRODUCT_ROLE_RELEVANCE)} products × {len(ROLES_ORDER)} roles = {len(PRODUCT_ROLE_RELEVANCE) * len(ROLES_ORDER)}")


if __name__ == "__main__":
    build()
