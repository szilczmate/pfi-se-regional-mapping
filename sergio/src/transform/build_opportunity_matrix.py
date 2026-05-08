# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v15.xlsx — Product × Region Opportunity Matrix v1.

Roadmap work item #2 (Codex audit #2). Produces the centerpiece artefact:
  - 21 regions × 11 Pfizer products = 231 rows
  - 7 scored dimensions per row (each 0-100, higher = more favorable for Pfizer):
      1. Epi fit              — regional disease burden support
      2. Current uptake       — observed Pfizer presence (Rx patients/100k or vaccine share)
      3. Growth pressure      — demographic tailwind (mostly 65+ growth)
      4. Access score         — INVERTED friction (waits, budget, specialists)
      5. Stakeholder leverage — Pfizer-relevant stakeholder density per sjukvårdsregion
      6. Competitive score    — INVERTED threat (alternatives in market)
      7. Policy relevance     — NT-rådet/TLV/regional-plan alignment
  - Composite opportunity score = weighted avg
  - Recommended action keyword (Build / Defend / Cornerstone / Watch / Position / Maintain)
  - Confidence tag per row (mostly Modeled; hospital-admin = Modeled + Needs Pfizer validation)

Inputs:  master_workbook_v14.xlsx  (Confidence Layer applied)
Outputs: master_workbook_v15.xlsx  (with new "OPP - Region x Product matrix" sheet)
         working/data/master/opportunity_matrix_v1.csv  (standalone client artefact)

NOTE: All composite scores are MODELED (author-chosen dimension weights).
      Pfizer net revenue is not derivable from this layer — gross therapy-cost
      proxies remain in Analysis B. This matrix is strategic prioritization, not
      financial forecasting.
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
SRC = ROOT / "working/data/master/master_workbook_v14.xlsx"
DST = ROOT / "working/data/master/master_workbook_v15.xlsx"
CSV_OUT = ROOT / "working/data/master/opportunity_matrix_v1.csv"

# ============================================================================
# STYLE TOKENS
# ============================================================================
PF_NAVY = "003F7F"
PF_GREY = "4B5563"
PF_LIGHT_GREY = "F3F4F6"
TAG_OBSERVED = "C6EFCE"
TAG_MODELED = "FFEB9C"
TAG_HYPOTHESIS = "FFC7CE"
TAG_NEEDS_VALIDATION = "D9D2E9"

HEAT_DARK = "1F4E79"     # high score
HEAT_MID = "9CC2E5"
HEAT_LIGHT = "DEEBF7"    # low score

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# ============================================================================
# PRODUCT CONFIG — canonical 11-product list with epi rules + competitor profile
# ============================================================================
# Each product has:
#   substance       — INN
#   atc             — Anatomical Therapeutic Chemical code
#   indication      — short clinical description
#   category        — Oncology oral / Hospital admin / Vaccine / Antiviral / Migraine / Rare disease
#   epi_rule        — function name to compute regional epi-fit denominator
#   epi_basis       — short description of epi computation
#   nt_score        — base policy score (0-100)
#   competitor      — main alternative (str)
#   threat_base     — national threat 0-100 (HIGH=80, MEDIUM=50, LOW=20)
#   uptake_source   — 'rx' or 'vaccine' or 'na' (hospital-admin)
PRODUCTS = [
    dict(name="Tukysa", substance="tucatinib", atc="L01EH03",
         indication="HER2+ breast cancer with brain metastases",
         category="Oncology oral",
         epi_rule="breast_her2_brain_mets", epi_basis="breast_ca_per_100k × pop × 0.20 (HER2+) × 0.30 (brain mets)",
         nt_score=90, competitor="Enhertu (AZ/Daiichi)", threat_base=55,
         uptake_source="rx"),
    dict(name="Lorbrena/Lorviqua", substance="lorlatinib", atc="L01ED04",
         indication="ALK+ NSCLC",
         category="Oncology oral",
         epi_rule="lung_alk", epi_basis="lung_ca_per_100k × pop × 0.05 (ALK+ fraction)",
         nt_score=60, competitor="Alecensa (Roche)", threat_base=55,
         uptake_source="rx"),
    dict(name="Elrexfio", substance="elranatamab", atc="L01XC42",
         indication="Relapsed/refractory multiple myeloma",
         category="Hospital admin",
         epi_rule="mm_proxy", epi_basis="lymphoid cancer rate proxy × pop (national MM ≈ 6/100k)",
         nt_score=70, competitor="Tecvayli (J&J)", threat_base=80,
         uptake_source="na"),
    dict(name="Ibrance", substance="palbociclib", atc="L01EF01",
         indication="HR+/HER2- advanced/metastatic breast cancer",
         category="Oncology oral",
         epi_rule="breast_hr_her2neg", epi_basis="breast_ca_per_100k × pop × 0.70 (HR+/HER2-)",
         nt_score=35, competitor="Kisqali (Novartis ribociclib)", threat_base=70,
         uptake_source="rx",
         regional_threat_modifiers={"Stockholm": 25, "Västra Götalandsregionen": 25}),  # bump threat in Stockholm/VGR
    dict(name="Talzenna", substance="talazoparib", atc="L01XK04",
         indication="BRCA-mutated HER2- metastatic breast cancer",
         category="Oncology oral",
         epi_rule="breast_brca", epi_basis="breast_ca_per_100k × pop × 0.05 (BRCA prev)",
         nt_score=70, competitor="Lynparza (AZ olaparib)", threat_base=55,
         uptake_source="rx"),
    dict(name="Vyndaqel", substance="tafamidis", atc="N07XX08",
         indication="ATTR cardiomyopathy (wild-type and hereditary)",
         category="Rare disease oral",
         epi_rule="attr_cm", epi_basis="pop_75+ × 0.4% prevalence + Skellefteå hereditary multiplier",
         nt_score=50, competitor="Acoramidis (BridgeBio, EU pipeline)", threat_base=20,
         uptake_source="rx",
         hereditary_cluster={"Norrbotten": 5.0, "Västerbotten": 4.0}),  # multiplier on epi_fit
    dict(name="Hympavzi", substance="marstacimab", atc="B02BX10",
         indication="Hemophilia A and B without inhibitors",
         category="Hospital admin",
         epi_rule="hemophilia_proxy", epi_basis="national hemophilia prevalence ~10/100k × pop",
         nt_score=30, competitor="Hemlibra (Roche emicizumab)", threat_base=80,
         uptake_source="na"),
    dict(name="Paxlovid", substance="nirmatrelvir/ritonavir", atc="J05AE30",
         indication="Mild-to-moderate COVID-19 in high-risk patients",
         category="Antiviral",
         epi_rule="covid_risk", epi_basis="pop_65+ + comorbidity proxy (smoking + obesity)",
         nt_score=50, competitor="Lagevrio (MSD molnupiravir)", threat_base=20,
         uptake_source="rx"),
    dict(name="Vydura", substance="rimegepant", atc="N02CD06",
         indication="Acute and preventive migraine",
         category="Migraine",
         epi_rule="migraine_women", epi_basis="women 15-44 × 18% migraine prevalence",
         nt_score=40, competitor="Aimovig/Ajovy/Emgality (CGRP class)", threat_base=55,
         uptake_source="rx"),
    dict(name="Prevenar 20", substance="20-valent pneumococcal", atc="J07AL02",
         indication="Adult pneumococcal vaccination",
         category="Vaccine",
         epi_rule="ipd_burden", epi_basis="pop_65+ × IPD/100k regional rate",
         nt_score=50, competitor="Vaxneuvance / Capvaxive (MSD)", threat_base=80,
         uptake_source="vaccine_pneu"),
    dict(name="Abrysvo", substance="RSV bivalent", atc="J07BX05",
         indication="RSV prevention in adults 60+ and maternal",
         category="Vaccine",
         epi_rule="rsv_proxy", epi_basis="pop_60+ + pop 75+ (FHM target groups)",
         nt_score=25, competitor="Arexvy (GSK), mRESVIA (Moderna)", threat_base=55,
         uptake_source="vaccine_rsv"),
]


# ============================================================================
# DATA LOADERS
# ============================================================================
def load_region_master(wb):
    """Returns dict[region_name] -> dict of column-name → value."""
    ws = wb["Region master"]
    headers = [c.value for c in ws[1]]
    out = {}
    for r in range(2, ws.max_row + 1):
        row = {h: ws.cell(r, i + 1).value for i, h in enumerate(headers)}
        if row.get("Region"):
            out[row["Region"]] = row
    return out


def load_rx_snapshot(wb):
    """Returns dict[region_name] -> dict[product_short] -> patients/100k float."""
    ws = wb["Rx 2024 snapshot"]
    headers = [c.value for c in ws[1]]
    out = {}
    # Build column-name index
    col_per_100k = {}
    for i, h in enumerate(headers):
        if h and "/100k" in str(h):
            # strip product short
            short = h.split("/100k")[0].strip()
            col_per_100k[short] = i
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 1).value
        if not region:
            continue
        # Region master uses "Region X"; snapshot uses just "Stockholm"; reconcile by suffix match
        region_full = region if region.startswith("Region") else f"Region {region}"
        if region == "Västra Götaland":
            region_full = "Västra Götalandsregionen"
        if region == "Jämtland Härjedalen":
            region_full = "Region Jämtland Härjedalen"
        if region == "Sörmland":
            region_full = "Region Sörmland"
        out[region_full] = {}
        for short, col_idx in col_per_100k.items():
            v = ws.cell(r, col_idx + 1).value
            try:
                out[region_full][short] = float(v) if v is not None else 0.0
            except (TypeError, ValueError):
                out[region_full][short] = 0.0
    return out


def load_vaccine_share(wb):
    """Returns dict[region_name] -> dict with rsv_share, pneu_share, tbe_share (%)."""
    ws = wb["Vaccine market share"]
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 2).value
        if not region:
            continue
        try:
            out[region] = dict(
                rsv_share=float(ws.cell(r, 5).value or 0),
                pneu_share=float(ws.cell(r, 8).value or 0),
                tbe_share=float(ws.cell(r, 11).value or 0),
            )
        except (TypeError, ValueError):
            out[region] = dict(rsv_share=0, pneu_share=0, tbe_share=0)
    return out


def load_pop_projections(wb):
    """Returns dict[region_name] -> {65+ growth %, pop 2024, 65+ 2024, 65+ 2040}."""
    ws = wb["Future — pop projections"]
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 2).value
        if not region:
            continue
        try:
            out[region] = dict(
                pop_2024=float(ws.cell(r, 4).value or 0),
                p65_2024=float(ws.cell(r, 5).value or 0),
                p65_2040=float(ws.cell(r, 7).value or 0),
                p75_2040=float(ws.cell(r, 8).value or 0),
                p65_growth_pct=float(ws.cell(r, 12).value or 0),
            )
        except (TypeError, ValueError):
            out[region] = dict(pop_2024=0, p65_2024=0, p65_2040=0, p75_2040=0, p65_growth_pct=0)
    return out


def load_governance(wb):
    """Returns dict[region_name] -> {sjukvardsregion, NT_rep, NSG_rep, HIGH_count}."""
    ws = wb["Governance box per region"]
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 1).value
        if not region:
            continue
        sj = ws.cell(r, 2).value
        nt_rep = ws.cell(r, 13).value
        nsg_rep = ws.cell(r, 14).value
        # HIGH-confidence count across the 5 governance roles (cols 4, 6, 8, 10, 12 are confidence cols)
        high_count = 0
        for conf_col in [4, 6, 8, 10, 12]:
            v = ws.cell(r, conf_col).value
            if v and "HIGH" in str(v).upper():
                high_count += 1
        out[region] = dict(sjukvardsregion=sj, nt_rep=nt_rep, nsg_rep=nsg_rep, high_count=high_count)
    return out


def load_regional_plans(wb):
    """Returns dict[region_short_name] -> {pfizer_relevance_tier, vaccine_kw, cancer_kw, aldre_kw}."""
    ws = wb["Regional plans + angles v2"]
    out = {}
    for r in range(2, ws.max_row + 1):
        region = ws.cell(r, 1).value
        if not region:
            continue
        try:
            out[region] = dict(
                cancer_kw=int(ws.cell(r, 4).value or 0),
                vaccine_kw=int(ws.cell(r, 5).value or 0),
                aldre_kw=int(ws.cell(r, 6).value or 0),
                tier=ws.cell(r, 15).value,
            )
        except (TypeError, ValueError):
            out[region] = dict(cancer_kw=0, vaccine_kw=0, aldre_kw=0, tier="MEDIUM")
    return out


# ============================================================================
# EPI-FIT COMPUTATION (per product per region)
# ============================================================================
def compute_epi_fit(product, region, region_master, pop_proj):
    """Returns raw epi-fit value (eligible patient pool estimate).
    Final score is normalized 0-100 across regions in caller.
    """
    rule = product["epi_rule"]
    rm = region_master.get(region, {})
    pp = pop_proj.get(region, {})
    pop = rm.get("Population") or pp.get("pop_2024") or 0
    p65 = rm.get("Pop 65+") or 0
    p75 = rm.get("Pop 75+") or 0
    breast_rate = rm.get("Breast ca rate /100k") or 0
    lung_rate = rm.get("Lung ca incidence /100k") or 0
    ipd_rate = rm.get("IPD /100k 2025") or 0
    smokers = rm.get("Daily smokers %") or 0
    obese = rm.get("Overweight/obese %") or 0
    women_15_44 = rm.get("Pop women 15-44") or 0

    if rule == "breast_her2_brain_mets":
        return (breast_rate / 1e5) * pop * 0.20 * 0.30
    if rule == "breast_brca":
        return (breast_rate / 1e5) * pop * 0.05
    if rule == "breast_hr_her2neg":
        return (breast_rate / 1e5) * pop * 0.70
    if rule == "lung_alk":
        return (lung_rate / 1e5) * pop * 0.05
    if rule == "attr_cm":
        base = p75 * 0.004  # 0.4% prevalence
        # Hereditary cluster modifier — only Norrbotten/Västerbotten elevated
        cluster = product.get("hereditary_cluster", {})
        for cluster_region, mult in cluster.items():
            if cluster_region.lower() in region.lower():
                base *= mult
        return base
    if rule == "mm_proxy":
        return pop * 6 / 1e5  # national MM incidence approx 6/100k
    if rule == "hemophilia_proxy":
        return pop * 10 / 1e5  # ~10/100k
    if rule == "covid_risk":
        # 65+ + comorbidity proxy (smoking + obesity contribute)
        return p65 + (pop * (smokers + obese) / 100 * 0.05)
    if rule == "migraine_women":
        return women_15_44 * 0.18  # ~18% prevalence in women aged 15-44
    if rule == "ipd_burden":
        return p65 * (ipd_rate / 1e5)  # eligible cases/year approximation
    if rule == "rsv_proxy":
        return p65 * 1.0  # 60+ proxy via 65+ (no 60-64 column)
    return pop  # fallback


# ============================================================================
# SCORING UTILITIES (normalize 0-100 across a list)
# ============================================================================
def normalize_scores(values, invert=False):
    """Map a list of values to 0-100. Highest = 100 (or 0 if invert=True)."""
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi - lo < 1e-9:
        return [50.0] * len(values)
    out = [(v - lo) / (hi - lo) * 100 for v in values]
    if invert:
        out = [100 - v for v in out]
    return out


# ============================================================================
# DIMENSION 4: ACCESS SCORE (inverted friction)
# ============================================================================
def compute_access_score(region_master, region):
    """Higher = lower friction = better for Pfizer access. 0-100."""
    rm = region_master.get(region, {})
    wait_spec = rm.get("Median wait spec days") or 60
    wait_op = rm.get("Median wait op days") or 60
    pharma_per_inv = rm.get("Pharma förmån/inv") or 2500
    spec_count = rm.get("Specialist läkare (#)") or 1000
    pop = rm.get("Population") or 1
    spec_density = spec_count / pop * 1000  # specialists per 1000 pop

    # Heuristic friction (each component 0-100, higher = more friction):
    f_wait_spec = min(100, max(0, (wait_spec - 20) / 100 * 100))  # 20d good, 120d bad
    f_wait_op = min(100, max(0, (wait_op - 20) / 100 * 100))
    f_budget = max(0, min(100, (3500 - pharma_per_inv) / 1500 * 100))  # higher budget = lower friction
    f_spec = max(0, min(100, (3 - spec_density) / 3 * 100))  # 3+ specialists/1k = good

    friction = (f_wait_spec + f_wait_op + f_budget + f_spec) / 4
    return 100 - friction


# ============================================================================
# DIMENSION 5: STAKEHOLDER LEVERAGE per region
# ============================================================================
# Sjukvårdsregion-level cornerstone scores — calibrated post-2026-04-25 fact-check
# (stakeholder_mapping_v8.xlsx). Earlier "Sydöstra triple-leverage" framing was
# corrected: Katarina Nyberg-Finn is Jämtland H. (Norra), NOT Jönköping (Sydöstra).
# Sydöstra remains strong via dual-leverage Lindström + Ekelund.
SJ_CORNERSTONE_BASE = {
    # Stockholm-Gotland: Lennartsson + Hadžialić (Finansregionråd/RS ordf) + Talla Alkurdi (HSN) + Bratt (NSG) + Mats Ek (LK)
    "Stockholm-Gotland": 75,
    # Mellansverige: Jan Melin (Uppsala LK + NT-rådet rep) + Helena Proos (RS Uppsala) + several RDs
    "Mellansverige": 80,
    # Sydöstra: Mårten Lindström (NT-rådet tf. ordf, Jönköping) + Maria Ekelund (LK Jönköping + NT-rådet Sydöstra) — dual cornerstone
    "Sydöstra": 88,
    # Västra (VGR): Järnström + Claesson + Eliasson + Olsson/Alnebratt (split HSN) + Sandelin (LK)
    "Västra": 72,
    # Sydsvenska: Skåne lead Myrebris + Engström + Sonesson + Mannfalk + Stefan Nilsson (LK)
    "Sydsvenska": 65,
    # Norra: Näsvall (HSD VB + NSG) + Bergström (NT-rådet vice ordf NB) + Anna Alm Andersson (RD NB) + Joelsson (tf. HSD NB)
    # + Bo Sundqvist (LK VB) + Linda Grahn (LK NB) — esp ATTR-CM relevant
    "Norra": 90,
    # variants
    "Sjukvårdsregion Stockholm-Gotland": 75,
    "Sjukvårdsregion Mellansverige": 80,
    "Sjukvårdsregion Sydöstra": 88,
    "Sjukvårdsregion Västra": 72,
    "Sjukvårdsregion Sydsvenska": 65,
    "Sjukvårdsregion Norra": 90,
}

# Per-product sjukvårdsregion modifiers — where a region has product-specific strength
PRODUCT_SJ_MODIFIER = {
    "Vyndaqel": {"Norra": 10, "Sjukvårdsregion Norra": 10},  # Skellefteå cluster expertise
    "Tukysa": {"Sydöstra": 5, "Sjukvårdsregion Sydöstra": 5},  # NT-rådet chair (Lindström)
    "Talzenna": {"Sydöstra": 4, "Sjukvårdsregion Sydöstra": 4},
    "Elrexfio": {"Sydöstra": 4, "Sjukvårdsregion Sydöstra": 4},
}


def compute_stakeholder_leverage(governance, region, product_name):
    """Returns 0-100 stakeholder leverage score for a region × product."""
    g = governance.get(region, {})
    sj = g.get("sjukvardsregion") or ""
    base = SJ_CORNERSTONE_BASE.get(sj, 50)
    high_bonus = g.get("high_count", 0) * 4  # up to +20 if all 5 roles HIGH
    # Per-product modifier for sjukvårdsregion
    mod_table = PRODUCT_SJ_MODIFIER.get(product_name, {})
    mod = mod_table.get(sj, 0)
    return min(100, base + high_bonus + mod)


# ============================================================================
# DIMENSION 6: COMPETITIVE SCORE (inverted threat)
# ============================================================================
def compute_competitive_score(product, region):
    """Higher = lower competitive threat = better for Pfizer."""
    threat = product["threat_base"]
    mods = product.get("regional_threat_modifiers", {})
    # Match region to modifier (loose containment)
    for mod_region, bump in mods.items():
        if mod_region.lower() in region.lower():
            threat += bump
            break
    threat = min(100, threat)
    return 100 - threat


# ============================================================================
# DIMENSION 7: POLICY RELEVANCE (with regional plan modifier)
# ============================================================================
def compute_policy_relevance(product, region_short_name, regional_plans):
    """Returns 0-100 policy relevance score."""
    base = product["nt_score"]
    plan = regional_plans.get(region_short_name) or regional_plans.get(region_short_name.replace("Region ", "")) or {}
    tier = (plan.get("tier") or "").upper()
    if tier == "HIGH":
        base += 8
    elif tier == "LOW" or tier == "":
        base -= 4
    # Vaccine product: vaccine keyword density helps
    if product["category"] == "Vaccine" and plan.get("vaccine_kw", 0) > 5:
        base += 5
    if product["category"] == "Oncology oral" and plan.get("cancer_kw", 0) > 3:
        base += 4
    return max(0, min(100, base))


# ============================================================================
# RECOMMENDED ACTION RULE ENGINE
# ============================================================================
def recommended_action(scores, product):
    """Returns (action_keyword, one_line_text)."""
    epi = scores["epi_fit"]
    uptake = scores["uptake"]
    growth = scores["growth"]
    access = scores["access"]
    stakeholder = scores["stakeholder"]
    competitive = scores["competitive"]
    policy = scores["policy"]
    composite = scores["composite"]

    # Hospital-admin without uptake data: special label
    if product["uptake_source"] == "na":
        if epi > 70 and stakeholder > 70:
            return ("Position", "High disease burden + strong stakeholders; uptake unknown — pull IQVIA Concise to validate")
        return ("Position", "Hospital-administered; no Rx-register uptake — needs IQVIA Concise extract for visibility")

    # Cornerstone — anchor region for the product
    if epi > 75 and stakeholder > 80 and composite > 65:
        return ("Cornerstone", "Anchor region for this product — concentrate effort here; pilot for portfolio play")

    # Defend — established footprint under threat
    if uptake > 70 and competitive < 40:
        return ("Defend", "Strong footprint under direct competitive pressure — commercial defense priority")

    # Build — undeveloped opportunity with epi support
    if epi > 60 and uptake < 35:
        if access < 40:
            return ("Watch", "Epi support but high access friction — monitor; act when wait times / budget shift")
        return ("Build", "Underpenetrated despite epidemiological support — first-mover engagement opportunity")

    # Position — emerging demographic demand
    if growth > 70 and uptake < 50:
        return ("Position", "Demographic tailwind — build presence ahead of demand inflection")

    # Watch — unfavorable mix
    if access < 35 or composite < 35:
        return ("Watch", "Multiple unfavorable signals — deprioritize until conditions shift")

    # Maintain — steady state
    return ("Maintain", "Balanced signals — sustain current engagement intensity")


# ============================================================================
# CONFIDENCE TAG PER ROW
# ============================================================================
def assign_confidence(product, region):
    """Returns confidence string based on data availability + interpretive content."""
    tags = ["Modeled"]  # composite scoring is always Modeled
    if product["uptake_source"] == "na":
        tags.append("Needs Pfizer validation")
    # Ibrance Stockholm/VGR carries Hypothesis on Kisqali substitution narrative
    if product["name"] == "Ibrance" and any(s.lower() in region.lower() for s in ["Stockholm", "Västra"]):
        tags.append("Hypothesis")
    # Rare-disease cluster — founder-variant explanation is Hypothesis layer
    if product["name"] == "Vyndaqel" and any(s.lower() in region.lower() for s in ["Norrbotten", "Västerbotten"]):
        tags.append("Hypothesis")
    return " + ".join(tags)


# ============================================================================
# MAIN MATRIX BUILD
# ============================================================================
WEIGHTS = dict(
    epi_fit=0.25,
    uptake=0.10,
    growth=0.15,
    access=0.10,
    stakeholder=0.15,
    competitive=0.15,
    policy=0.10,
)


def build_matrix(wb):
    region_master = load_region_master(wb)
    rx_snap = load_rx_snapshot(wb)
    vac_share = load_vaccine_share(wb)
    pop_proj = load_pop_projections(wb)
    governance = load_governance(wb)
    regional_plans = load_regional_plans(wb)

    regions = list(region_master.keys())
    print(f"Loaded {len(regions)} regions × {len(PRODUCTS)} products = {len(regions) * len(PRODUCTS)} cells")

    # Stage 1: compute raw values per cell, then normalize per product
    raw = []
    for product in PRODUCTS:
        for region in regions:
            epi_raw = compute_epi_fit(product, region, region_master, pop_proj)
            # Uptake: from rx_snap or vac_share
            if product["uptake_source"] == "rx":
                # Find matching key in rx_snap (e.g., "Ibrance patients 2024" not present, "Ibrance" via /100k)
                rx_keys = rx_snap.get(region, {})
                # match by product name short
                short_name = product["name"].split("/")[0].split(" ")[0]
                uptake_raw = rx_keys.get(f"{short_name} patients 2024",
                                          rx_keys.get(short_name, 0)) or 0
                if uptake_raw == 0:
                    # try fuzzy match
                    for k, v in rx_keys.items():
                        if short_name.lower() in k.lower():
                            uptake_raw = v
                            break
            elif product["uptake_source"] == "vaccine_rsv":
                uptake_raw = vac_share.get(region, {}).get("rsv_share", 0)
            elif product["uptake_source"] == "vaccine_pneu":
                uptake_raw = vac_share.get(region, {}).get("pneu_share", 0)
            else:  # na
                uptake_raw = None

            # Growth: 65+ growth pct for age-driven products; pop growth proxy for others
            pp = pop_proj.get(region, {})
            growth_raw = pp.get("p65_growth_pct", 0)

            access_raw = compute_access_score(region_master, region)
            short_region = region.replace("Region ", "")
            stake_raw = compute_stakeholder_leverage(governance, region, product["name"])
            comp_raw = compute_competitive_score(product, region)
            policy_raw = compute_policy_relevance(product, short_region, regional_plans)

            raw.append(dict(
                region=region,
                product=product,
                epi_raw=epi_raw,
                uptake_raw=uptake_raw,
                growth_raw=growth_raw,
                access_raw=access_raw,
                stake_raw=stake_raw,
                comp_raw=comp_raw,
                policy_raw=policy_raw,
            ))

    # Stage 2: normalize per product across regions for epi_fit + uptake
    rows = []
    for product in PRODUCTS:
        cells = [r for r in raw if r["product"] is product]
        epi_vals = [c["epi_raw"] for c in cells]
        epi_scores = normalize_scores(epi_vals)

        uptake_vals = [c["uptake_raw"] if c["uptake_raw"] is not None else 0 for c in cells]
        uptake_scores = normalize_scores(uptake_vals)
        # If uptake_source is na, set uptake score to 50 (neutral)
        if product["uptake_source"] == "na":
            uptake_scores = [50.0] * len(cells)

        growth_vals = [c["growth_raw"] for c in cells]
        growth_scores = normalize_scores(growth_vals)

        for i, c in enumerate(cells):
            scores = dict(
                epi_fit=round(epi_scores[i], 1),
                uptake=round(uptake_scores[i], 1),
                growth=round(growth_scores[i], 1),
                access=round(c["access_raw"], 1),
                stakeholder=round(c["stake_raw"], 1),
                competitive=round(c["comp_raw"], 1),
                policy=round(c["policy_raw"], 1),
            )
            composite = (
                scores["epi_fit"] * WEIGHTS["epi_fit"] +
                scores["uptake"] * WEIGHTS["uptake"] +
                scores["growth"] * WEIGHTS["growth"] +
                scores["access"] * WEIGHTS["access"] +
                scores["stakeholder"] * WEIGHTS["stakeholder"] +
                scores["competitive"] * WEIGHTS["competitive"] +
                scores["policy"] * WEIGHTS["policy"]
            )
            scores["composite"] = round(composite, 1)
            action_kw, action_text = recommended_action(scores, c["product"])
            confidence = assign_confidence(c["product"], c["region"])

            rows.append(dict(
                region=c["region"],
                sjukvardsregion=governance.get(c["region"], {}).get("sjukvardsregion", ""),
                product=product["name"],
                category=product["category"],
                indication=product["indication"],
                **scores,
                action=action_kw,
                action_text=action_text,
                confidence=confidence,
                competitor=product["competitor"],
                nt_status=product.get("nt_score", ""),
                epi_basis=product["epi_basis"],
            ))

    # Sort by composite descending — gives ranked client-ready output
    rows.sort(key=lambda x: -x["composite"])
    return rows


# ============================================================================
# WORKBOOK + CSV WRITERS
# ============================================================================
def heat_fill(score):
    """Map 0-100 score to a 3-stop heatmap color."""
    if score is None:
        return None
    if score >= 67:
        return PatternFill("solid", fgColor=HEAT_DARK)
    if score >= 33:
        return PatternFill("solid", fgColor=HEAT_MID)
    return PatternFill("solid", fgColor=HEAT_LIGHT)


def confidence_fill(tag):
    if not tag:
        return None
    s = tag.lower()
    if "needs pfizer validation" in s:
        return PatternFill("solid", fgColor=TAG_NEEDS_VALIDATION)
    if "hypothesis" in s:
        return PatternFill("solid", fgColor=TAG_HYPOTHESIS)
    if "modeled" in s:
        return PatternFill("solid", fgColor=TAG_MODELED)
    return PatternFill("solid", fgColor=TAG_OBSERVED)


def make_header_cell(cell, text, bg=PF_NAVY, fg="FFFFFF", size=10):
    cell.value = text
    cell.font = Font(name="Calibri", size=size, bold=True, color=fg)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = BORDER


def write_matrix_sheet(wb, rows):
    ws = wb.create_sheet("OPP - Region x Product matrix",
                         index=wb.sheetnames.index("OPP - All products composite") + 1)

    # Title block
    ws.cell(row=1, column=1, value="Product × Region Opportunity Matrix v1")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=15)

    ws.cell(row=2, column=1, value=(
        "21 regions × 11 Pfizer products = 231 cells, scored on 7 dimensions (0-100, higher = "
        "more favorable for Pfizer engagement). Composite = weighted average. Recommended action "
        "from rule engine. All composite scores tagged Modeled — see EVIDENCE_CONFIDENCE_FRAMEWORK. "
        "Stakeholder leverage layer uses stakeholder_mapping_v8 (post-2026-04-25 external fact-check)."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)

    weight_str = "  ".join(f"{k}: {int(v*100)}%" for k, v in WEIGHTS.items())
    ws.cell(row=3, column=1, value=f"Weights — {weight_str}")
    ws.cell(row=3, column=1).font = Font(name="Calibri", size=9, italic=True, color=PF_GREY)
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=15)

    # Headers
    headers = [
        "Region", "Sjukvårdsregion", "Product", "Category", "Indication",
        "Epi fit", "Uptake", "Growth", "Access", "Stakeholder", "Competitive", "Policy",
        "Composite", "Action", "Action text", "Confidence", "Competitor", "Epi basis"
    ]
    for i, h in enumerate(headers, start=1):
        make_header_cell(ws.cell(row=5, column=i), h)

    # Body
    for ri, row in enumerate(rows, start=6):
        ordered = [
            row["region"], row["sjukvardsregion"], row["product"], row["category"], row["indication"],
            row["epi_fit"], row["uptake"], row["growth"], row["access"], row["stakeholder"],
            row["competitive"], row["policy"], row["composite"],
            row["action"], row["action_text"], row["confidence"], row["competitor"], row["epi_basis"]
        ]
        for ci, val in enumerate(ordered, start=1):
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.font = Font(name="Calibri", size=9)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            # Heat-color for score columns (cols 6-13)
            if 6 <= ci <= 13 and isinstance(val, (int, float)):
                cell.fill = heat_fill(val)
                # white text on dark fill for readability
                if val >= 67:
                    cell.font = Font(name="Calibri", size=9, color="FFFFFF", bold=True)
                else:
                    cell.font = Font(name="Calibri", size=9, bold=True)
            # Confidence column (16)
            if ci == 16:
                cell.fill = confidence_fill(val)
                cell.font = Font(name="Calibri", size=9, bold=True)
            # Action column (14) — bold
            if ci == 14:
                cell.font = Font(name="Calibri", size=9, bold=True)

    # Column widths
    widths = [22, 22, 18, 16, 32, 8, 8, 8, 8, 12, 12, 8, 11, 12, 50, 24, 28, 50]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "F6"
    ws.auto_filter.ref = f"A5:R{5 + len(rows)}"


def write_csv(rows):
    fields = [
        "region", "sjukvardsregion", "product", "category", "indication",
        "epi_fit", "uptake", "growth", "access", "stakeholder", "competitive", "policy",
        "composite", "action", "action_text", "confidence", "competitor", "epi_basis"
    ]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def update_readme(wb):
    ws = wb["README"]
    r = ws.max_row + 2
    ws.cell(row=r, column=1, value="OPPORTUNITY MATRIX (v15, 2026-04-25)")
    ws.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    ws.cell(row=r, column=1, value=(
        "New 'OPP - Region x Product matrix' sheet — 21 regions × 11 Pfizer products on 7 "
        "scored dimensions (epi fit, uptake, growth, access, stakeholder leverage, competitive, "
        "policy) + composite score + recommended Pfizer action. Standalone CSV at "
        "working/data/master/opportunity_matrix_v1.csv. All composite scores are Modeled — see "
        "EVIDENCE_CONFIDENCE_FRAMEWORK.md for taxonomy."
    ))
    ws.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")


def main():
    print(f"Loading {SRC.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    print(f"Initial sheet count: {len(wb.sheetnames)}")

    rows = build_matrix(wb)
    print(f"Built {len(rows)} matrix rows")

    write_matrix_sheet(wb, rows)
    print("Wrote OPP - Region x Product matrix sheet")

    update_readme(wb)
    print("Updated README")

    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    write_csv(rows)
    print(f"Wrote {CSV_OUT.name}")

    # Distribution summary
    actions = {}
    for r in rows:
        actions[r["action"]] = actions.get(r["action"], 0) + 1
    print("\nAction distribution:")
    for a, n in sorted(actions.items(), key=lambda x: -x[1]):
        print(f"  {a}: {n}")

    print("\nTop 10 cells by composite:")
    for r in rows[:10]:
        print(f"  {r['composite']:>5.1f}  {r['region'][:26]:<26}  {r['product']:<20}  {r['action']}")

    print("\nBottom 5 cells by composite:")
    for r in rows[-5:]:
        print(f"  {r['composite']:>5.1f}  {r['region'][:26]:<26}  {r['product']:<20}  {r['action']}")


if __name__ == "__main__":
    main()
