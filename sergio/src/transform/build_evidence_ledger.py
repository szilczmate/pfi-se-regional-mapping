# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v14.xlsx — adds the Evidence Confidence Layer.

Retrofits v13 with:
  1. New "Evidence ledger" sheet — canonical truth-table of ~50 major claims tagged
     with Observed / Modeled / Hypothesis / Needs Pfizer validation
  2. Confidence + Confidence rule columns on "OPP - All products composite"
  3. Confidence column on "NT-rådet status v2"
  4. Confidence column on "Robustness QA"
  5. New "Region master — confidence" sheet documenting per-column confidence on the
     Region master (since within-column the tag is uniform)
  6. README updated to describe the new framework

No data is mutated; only metadata is added.

Schema for Evidence ledger:
  claim_id | domain | source_artefact | section | claim_short | confidence
    | decision_rule | evidence_trail | what_would_upgrade
"""
import sys
from pathlib import Path
from copy import copy
import shutil

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v13.xlsx"
DST = ROOT / "working/data/master/master_workbook_v14.xlsx"

# Pfizer palette (consistent with charts_v2)
PF_NAVY = "003F7F"
PF_LIGHT_BLUE = "DAEEF3"
PF_GREY = "4B5563"
PF_LIGHT_GREY = "F3F4F6"
TAG_OBSERVED = "C6EFCE"      # light green
TAG_MODELED = "FFEB9C"       # light yellow
TAG_HYPOTHESIS = "FFC7CE"    # light red
TAG_NEEDS_VALIDATION = "D9D2E9"  # light purple

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ============================================================================
# EVIDENCE LEDGER ROWS — the canonical truth-table
# ============================================================================
# Schema: claim_id, domain, source_artefact, section, claim_short, confidence,
#         decision_rule, evidence_trail, what_would_upgrade
LEDGER = [
    # ========== EXECUTIVE SUMMARY (ANALYTICAL_FINDINGS_v1.docx) ==========
    ("EX-01", "Market access", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §1",
     "Avvakta override on Abrysvo: 65% national IQVIA share + >60% in 19/21 regions despite NT-rådet hold (2023-10-05).",
     "Observed + Hypothesis",
     "The shares are Observed (IQVIA 36-month rolling). The framing 'override' is Hypothesis — regions may be buying for risk-group indications without consciously challenging the hold.",
     "IQVIA market-share table + samverkanlakemedel.se NT-rådet status",
     "Hypothesis → Modeled if regional procurement records show explicit override decisions; or downgrade language to 'regional uptake despite national financing hold'."),

    ("EX-02", "Rare disease", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §2",
     "Norrbotten 31.0/100k + Västerbotten 23.8/100k Vyndaqel patients = 31% of Sweden's ATTR-CM in 2.8% of population.",
     "Observed",
     "Direct counts from Socialstyrelsen Läkemedelsregistret 2024 ÷ SCB 2024 region population.",
     "Läkemedelsregistret Rx sheet, Region master Pop column",
     "Stable Observed — refreshes when Socialstyrelsen publishes 2025 figures."),

    ("EX-03", "Commercial", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §3",
     "Vyndaqel = 61% of Pfizer's Swedish oral-Rx revenue (370M SEK / 610M SEK total).",
     "Modeled + Needs Pfizer validation",
     "Gross therapy-cost proxy = patient count × public list price × 12 months. Pfizer net revenue (rebates, regional discounts, tender losses) is unknown to us.",
     "Läkemedelsregistret patient counts × TLV public list prices",
     "Modeled → Observed if Pfizer shares net per-patient revenue figures. Always retain 'gross therapy-cost proxy' label."),

    ("EX-04", "Commercial", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §4",
     "Kisqali substitution puts 38-78M SEK of annual Ibrance revenue at risk under three scenarios.",
     "Modeled + Needs Pfizer validation",
     "Linear extrapolation of 2021-2024 Ibrance trajectory × gross therapy-cost proxy. Three scenarios (status quo / regional spread / national spread).",
     "Läkemedelsregistret Ibrance trajectory + scenario assumptions in analysis D",
     "Needs IQVIA Kisqali volume to validate substitution channel; needs Pfizer net pricing for SEK figures."),

    ("EX-05", "Market access", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §5",
     "NT-rådet recommendation is necessary but not sufficient — Tukysa shows variable regional adoption despite formal NT rec.",
     "Hypothesis",
     "Pattern interpretation: even with NT recommendation, regional uptake varies. We have not tested causes (eligible-population denominator, regional formulary timing, oncologist preferences).",
     "Tukysa adoption trajectory analysis C + NT-rådet status v2 sheet",
     "Hypothesis → Modeled with proper denominator (HER2+ breast cancer with brain mets per region) and time-to-first-prescription per region."),

    ("EX-06", "Behavioural", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §6",
     "Regression confirms Kisqali substitution story is behavioural, not demographic — Stockholm/VGR sit far below the demographic regression line.",
     "Modeled",
     "OLS regression of regional Ibrance uptake on demographic predictors (Pop women 15-44, breast ca rate, breast ca surgery wait). Stockholm/VGR are negative outliers.",
     "Analysis 3 regression coefficients + residuals plot",
     "Modeled → stronger Modeled with longitudinal panel (region × year fixed effects) once 2025 data lands."),

    ("EX-07", "Vaccines", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §7",
     "Pneumococcal is Pfizer's biggest competitive vulnerability — 13% national share (Prevenar 20) vs MSD competitors.",
     "Observed",
     "IQVIA 36-month rolling vaccine market-share data, ATC J07AL.",
     "Vaccine market share sheet, Vaccine sales detail sheet",
     "Stable Observed — refreshes with next IQVIA pull."),

    ("EX-08", "Strategic", "ANALYTICAL_FINDINGS_v1.docx", "Exec summary §8",
     "Four regions cluster as 'Flagship': high Pfizer footprint × high strategic leverage.",
     "Modeled",
     "Hierarchical clustering on Pfizer-relevant features (vaccine sell-in, oral-Rx penetration, governance density). Cluster boundary depends on linkage method.",
     "Analysis 4 cluster_assignments + dendrogram",
     "Modeled → robust Modeled if cluster stability is tested across linkage methods (Ward, complete, average) + bootstrap."),

    # ========== CHAPTER-LEVEL CLAIMS (ANALYTICAL_FINDINGS Part I-IV) ==========
    ("CH-01", "Market structure", "ANALYTICAL_FINDINGS_v1.docx", "Ch 1 — Penetration gap",
     "Penetration gap heatmap quantifies Pfizer-share variability across 21 × 11 = 231 cells.",
     "Modeled",
     "Gap = potential (national rate × region pop) − observed (region count). Potential is itself a Modeled benchmark.",
     "Analysis 1 penetration_gap_heatmap.png + analysis1_penetration_gap.csv",
     "Modeled → stronger if 'potential' uses sub-region clinical denominators (e.g. HER2+ patients) rather than population-rate scaling."),

    ("CH-02", "Drivers", "ANALYTICAL_FINDINGS_v1.docx", "Ch 2 — Regression drivers",
     "Demographic + access predictors explain 40-65% of regional uptake variance per product.",
     "Modeled",
     "OLS coefficients with R² values per product. Linear-additive specification chosen.",
     "Analysis 3 regression_table.html + analysis3_r2_summary.csv",
     "Modeled → robust Modeled with non-linear specification (random forest feature importance) for products where R² < 0.5."),

    ("CH-03", "Clusters", "ANALYTICAL_FINDINGS_v1.docx", "Ch 3 — Region clusters",
     "21 regions naturally group into 4 clusters on Pfizer-relevance features.",
     "Modeled",
     "Hierarchical clustering, Ward linkage, k=4 chosen by dendrogram inspection.",
     "Analysis 4 cluster_dendrogram.png + cluster_pca_projection.png",
     "Modeled → robust Modeled with silhouette score test + bootstrap stability."),

    ("CH-04", "Rare disease", "ANALYTICAL_FINDINGS_v1.docx", "Ch 4 — Skellefteå cluster",
     "Skellefteå founder TTR V30M variant explains the Norrbotten + Västerbotten Vyndaqel concentration.",
     "Hypothesis",
     "Cluster geography is Observed; founder-variant causation is plausible from published genetics literature but not measured in this analysis.",
     "Läkemedelsregistret + ATTR-CM founder variant references",
     "Hypothesis → Modeled if region-level genetic prevalence data sourced; otherwise frame as 'consistent with literature'."),

    ("CH-05", "CDK4/6", "ANALYTICAL_FINDINGS_v1.docx", "Ch 5 — Ibrance trajectory",
     "Ibrance national decline 2021-2024 = 27% (1028 → 753 patients), driven by Stockholm (-33%) + VGR (-36%).",
     "Observed",
     "Direct counts from Socialstyrelsen Läkemedelsregistret per region per year.",
     "Läkemedelsregistret Rx sheet + analysis2_ibrance_cagr.csv",
     "Stable Observed."),

    ("CH-06", "Vaccines", "ANALYTICAL_FINDINGS_v1.docx", "Ch 6 — Abrysvo override",
     "Regions buy Abrysvo at 60-90% Pfizer share despite NT-rådet avvakta.",
     "Observed + Hypothesis",
     "Shares are Observed (IQVIA). 'Override' framing is Hypothesis — alternatives include risk-group buying (FHM 75+ rec) without challenging the hold.",
     "IQVIA vaccine market share + samverkanlakemedel.se NT-rådet status",
     "Reframe deck text to 'regional uptake despite national financing hold' — keeps the data, drops the loaded interpretation."),

    ("CH-07", "Vaccines", "ANALYTICAL_FINDINGS_v1.docx", "Ch 7 — Vaccine competition",
     "Across 4 vaccine ATCs (J07AL, J07BC, J07BX, J07BA), Pfizer share ranges 13-65% nationally.",
     "Observed",
     "IQVIA 36-month rolling, by ATC class.",
     "Vaccine market share sheet",
     "Stable Observed."),

    ("CH-08", "Implementation", "ANALYTICAL_FINDINGS_v1.docx", "Ch 8 — NT decision → regional",
     "Time from NT-rådet recommendation to regional uptake varies from <6 months to >24 months.",
     "Modeled",
     "First-prescription month derived from Läkemedelsregistret pull. Censored regions handled by simple right-censor at 2024-12.",
     "Analysis C tukysa_adoption_trajectory.png + analysis_C_tukysa_adoption.csv",
     "Modeled → robust with formal time-to-event analysis (Kaplan-Meier) on multiple products, not just Tukysa."),

    ("CH-09", "Opportunity sizing", "ANALYTICAL_FINDINGS_v1.docx", "Ch 9 — Opportunity if gap closes",
     "Closing penetration gaps to top-quartile regional rate would lift national patient counts by X% per product.",
     "Modeled",
     "Counterfactual: each region × product = top-quartile rate × region population. Top-quartile is itself derived.",
     "Analysis 5 opportunity_waterfall.png",
     "Modeled → strong Modeled with sensitivity over top-decile vs top-quartile vs top-tercile benchmarks."),

    ("CH-10", "Commercial", "ANALYTICAL_FINDINGS_v1.docx", "Ch 10 — Budget impact in SEK",
     "Pfizer Sweden gross oral-Rx therapy-cost = ~610M SEK annually (Vyndaqel 370M, Ibrance 166M, Tukysa 34M, others ~40M).",
     "Modeled + Needs Pfizer validation",
     "Patient count × TLV public list price × 12 months. Excludes hospital-administered (Elrexfio, Hympavzi).",
     "Analysis B B1_budget_impact_heatmap.png + analysis_B_budget_impact.csv",
     "Pfizer net revenue substantially differs from gross. Always retain 'modeled gross therapy-cost proxy' label."),

    ("CH-11", "Equity", "ANALYTICAL_FINDINGS_v1.docx", "Ch 11 — Health equity overlay",
     "Top-5 highest-need regions (composite SES + mortality): Sörmland, Norrbotten, Gävleborg, Västmanland, Örebro.",
     "Modeled",
     "Composite ranking on 5 SES/mortality components. Component weights are author-chosen.",
     "Health equity overlay sheet + analysis 06 map_health_equity.png",
     "Modeled → stronger with sensitivity over alternate component weights."),

    ("CH-12", "Strategic", "ANALYTICAL_FINDINGS_v1.docx", "Ch 12 — Priority matrix",
     "Region × product priority matrix identifies top 10 cells for Pfizer Access focus.",
     "Modeled",
     "Composite of opportunity score × strategic-leverage score. Author-chosen weighting.",
     "Analysis 8 priority_matrix.png + analysis8_priority_matrix.csv",
     "Modeled → upgrade with Codex-recommended Actionability axis (work item #3 in roadmap)."),

    ("CH-13", "Strategic", "ANALYTICAL_FINDINGS_v1.docx", "Ch 13 — Recommended actions",
     "10 immediate / mid-May / post-delivery action items for Pfizer Access.",
     "Hypothesis",
     "Strategic recommendations based on combined evidence. Dependent on Pfizer's own internal priority weighting.",
     "Synthesis across all chapters",
     "Pfizer field/access leadership review."),

    # ========== R ANALYTICAL LAYER ==========
    ("AN-01", "Methodology", "Analysis 01 (R)", "01_penetration_gap.R",
     "Penetration gap heatmap — Pfizer-share variability across 21 regions × 11 products.",
     "Modeled",
     "Gap = expected (population × national rate) − observed.",
     "01_penetration_gap_heatmap.png + 01_penetration_gap_summary_table.html",
     "See CH-01."),

    ("AN-02", "Methodology", "Analysis 02 (R)", "02_ibrance_forecast.R",
     "Ibrance national + regional forecast 2024 → 2027 under three scenarios.",
     "Modeled",
     "Linear regression on 2021-2024 patient counts; three scenarios (status quo, regional spread, national spread).",
     "02_ibrance_forecast_small_multiples.png + 02_ibrance_cagr_ranked.png",
     "Modeled → with 2025 data point + ARIMA / state-space alternative."),

    ("AN-03", "Methodology", "Analysis 03 (R)", "03_regression_drivers.R",
     "OLS regression of regional uptake on demographic + access predictors.",
     "Modeled",
     "Linear-additive specification, R² 0.40-0.65 depending on product.",
     "03_regression_coefficients.png + 03_regression_table.html",
     "See CH-02."),

    ("AN-04", "Methodology", "Analysis 04 (R)", "04_cluster_regions.R",
     "Hierarchical clustering of 21 regions on Pfizer-relevance feature vector.",
     "Modeled",
     "Ward linkage, k=4 by dendrogram. PCA projection for visualization.",
     "04_cluster_dendrogram.png + 04_cluster_pca_projection.png",
     "See CH-03."),

    ("AN-05", "Methodology", "Analysis 05 (R)", "05_opportunity_sizing.R",
     "Counterfactual opportunity sizing: gap-close to top-quartile rate.",
     "Modeled",
     "Top-quartile benchmarking. Sensitivity to benchmark choice not yet tested.",
     "05_opportunity_waterfall.png + 05_top20_regional_uplift.png",
     "See CH-09."),

    ("AN-06", "Methodology", "Analysis 06 (R)", "06_sweden_maps.R",
     "Sweden choropleth maps for health equity, Ibrance change, Vyndaqel rate.",
     "Observed",
     "Direct rendering of Observed values onto NUTS-3 region polygons.",
     "06_map_health_equity.png + 06_map_ibrance_change.png + 06_map_vyndaqel.png",
     "Stable Observed."),

    ("AN-07", "Methodology", "Analysis 07 (R)", "07_vaccine_competitive.R",
     "Vaccine competitive landscape (heatmap + top/bottom regions).",
     "Observed",
     "Direct rendering of IQVIA 36-month rolling shares.",
     "07_vaccine_share_heatmap.png + 07_vaccine_top_bottom.png",
     "Stable Observed."),

    ("AN-08", "Methodology", "Analysis 08 (R)", "08_priority_matrix.R",
     "Region × product priority matrix combining opportunity + strategic-leverage scores.",
     "Modeled",
     "Composite scoring; author-chosen weights for opportunity vs leverage.",
     "08_priority_matrix.png + analysis8_priority_matrix.csv",
     "See CH-12."),

    ("AN-A", "Methodology", "Analysis A (R)", "A_abrysvo_avvakta.R",
     "Quantifies regional uptake-vs-national-hold gap for Abrysvo.",
     "Observed + Hypothesis",
     "Uptake gap is Observed; 'override signal' framing is Hypothesis.",
     "A_abrysvo_avvakta_signal.png + analysis_A_abrysvo_signal.csv",
     "See CH-06."),

    ("AN-B", "Methodology", "Analysis B (R)", "B_budget_impact.R",
     "Budget-impact heatmap: gross therapy-cost proxy in SEK per region per product.",
     "Modeled + Needs Pfizer validation",
     "Patient count × TLV list price × 12 months. Pfizer net unknown.",
     "B1_budget_impact_heatmap.png + analysis_B_budget_impact.csv",
     "See CH-10."),

    ("AN-C", "Methodology", "Analysis C (R)", "C_implementation_latency.R",
     "Time-to-first-prescription for Tukysa post NT-rådet rec, per region.",
     "Modeled",
     "Right-censored at 2024-12 for non-adopting regions. Simple time-to-event.",
     "C1_tukysa_adoption_trajectory.png + analysis_C_tukysa_adoption.csv",
     "See CH-08."),

    ("AN-D", "Methodology", "Analysis D (R)", "D_kisqali_scenarios.R",
     "Three Ibrance trajectory scenarios with associated revenue-at-risk SEK.",
     "Modeled + Needs Pfizer validation",
     "Linear extrapolation × gross therapy-cost proxy. See CH-04 caveats.",
     "D1_kisqali_scenario_trajectory.png + D2_kisqali_revenue_at_risk.png",
     "See EX-04."),

    # ========== STRATEGIC / NARRATIVE CLAIMS ==========
    ("ST-01", "Competitive", "Memory + REGION_INTELLIGENCE_BRIEFS_v2.md", "Stockholm regional brief",
     "Region Stockholm prefers Novartis Kisqali over Pfizer Ibrance for cost reasons.",
     "Hypothesis + Needs Pfizer validation",
     "Decline pattern is consistent with cost-driven substitution; explicit cost-preference is interpretation, not measured.",
     "Ibrance trajectory + IQVIA Kisqali volume (not in our extract)",
     "IQVIA Kisqali volume + Pfizer field intel + region procurement records."),

    ("ST-02", "Competitive", "REGION_INTELLIGENCE_BRIEFS_v2.md", "Tukysa + Elrexfio threat",
     "Enhertu + Tecvayli pose HIGH threat to Tukysa + Elrexfio (NT-rådet pipeline).",
     "Hypothesis",
     "Pattern interpretation from NT-rådet review docket dates + label-expansion expectations.",
     "samverkanlakemedel.se pipeline reviews",
     "Quantify with eligible-population shift modeling once new indications confirmed."),

    ("ST-03", "Naming", "Memory", "Lorbrena = Lorviqua",
     "Lorbrena (US name) = Lorviqua (EU/Swedish brand name) for the same molecule.",
     "Observed",
     "FASS + EMA records.",
     "FASS substance lookup",
     "Stable Observed."),

    ("ST-04", "Pharmacology", "PROJECT_PLAN.md + memory", "Talzenna ATC",
     "Talzenna ATC = L01XK04 (PARP inhibitor class), corrected from earlier L01XX60.",
     "Observed",
     "FASS authoritative.",
     "FASS + WHO ATC index",
     "Stable Observed."),

    ("ST-05", "Stakeholder", "stakeholder_mapping_v7.xlsx", "Pia Näsvall",
     "Pia Näsvall (NSG Chair) moved from Norrbotten to Västerbotten in 2024.",
     "Observed",
     "Region Västerbotten official site + tromanpublik.",
     "Region Västerbotten politiker register",
     "Stable Observed; recheck annually."),

    ("ST-06", "Stakeholder", "stakeholder_mapping_v7.xlsx", "Jönköping triple-leverage",
     "Jönköping = triple-leverage cornerstone via Mårten Lindström (NT-rådet) + Maria Ekelund (LK + NT-rådet Sydöstra) + Katarina Nyberg Finn (HSN).",
     "Observed + Hypothesis + Needs Pfizer validation",
     "Names/roles Observed (samverkanlakemedel.se primary). 'Triple-leverage' is Hypothesis. Katarina Nyberg Finn name disputed (also attributed to Jämtland — likely two persons).",
     "samverkanlakemedel.se + STAKEHOLDER_VERIFICATION_PROMPT.md line 37",
     "Jonas Fuks pass to disambiguate Nyberg Finn; Pfizer field validation of strategic value."),

    ("ST-07", "Operations", "Region Jönköping public", "HSD Bojestig retiring",
     "Mats Bojestig (Jönköping HSD) retiring 2026; recruitment ongoing.",
     "Observed",
     "Region Jönköping personnel announcement; web-verified.",
     "Region Jönköping site",
     "Recheck Q3 2026 for replacement."),

    ("ST-08", "Wait times", "Master workbook 'Wait times'", "Wait time spread",
     "Specialist wait spread Stockholm (24.5 days) → Norrbotten (113 days) = 4.6x.",
     "Observed",
     "Kolada KPIs N06304 / N06305.",
     "Wait times sheet",
     "Stable Observed."),

    ("ST-09", "Wait times", "Master workbook 'Wait times'", "Breast cancer surgery",
     "Breast cancer surgery within 28 days: 9.7% (worst) → 91.4% (best) across 13 reporting regions.",
     "Observed",
     "RCC + Kolada SVF KPI.",
     "Wait times sheet + Cancer landscape sheet",
     "Stable Observed."),

    ("ST-10", "Demographics", "Master workbook 'Future — pop projections'", "Stockholm 65+ growth",
     "Stockholm 65+ population grows +35% by 2040 (+146 000 people).",
     "Modeled",
     "SCB demographic projection — assumes fertility/mortality/migration trajectory holds.",
     "Future — pop projections sheet",
     "Modeled by definition; refresh with each SCB projection cycle."),

    ("ST-11", "Coverage gap", "findings_iqvia_vaccines.md", "IQVIA scope",
     "Only 1 of 11 Pfizer products (Tukysa) has classic NT-rådet recommendation.",
     "Observed",
     "samverkanlakemedel.se scan.",
     "NT-rådet status v2 sheet",
     "Stable Observed; recheck per pipeline cycle."),

    ("ST-12", "Pipeline", "ntradet_pfizer_status_v2.xlsx", "NT-rådet status mix",
     "Pfizer 11-product NT status: 1 NT_RECOMMENDATION (Tukysa), 2 NATIONAL_AGREEMENT, 1 REGIONAL_ASSESSMENT, 1 AWAIT (Abrysvo), 1 ARCHIVED (Vyndaqel), 2 OUT_OF_SCOPE, 3 UNKNOWN.",
     "Observed",
     "samverkanlakemedel.se scan, audit trail in findings_ntradet.md.",
     "NT-rådet status v2 sheet",
     "UNKNOWN rows = Needs validation; recheck quarterly."),

    # ========== STRUCTURAL CAVEATS ==========
    ("DT-01", "Methodology", "METHODOLOGY.md + Data Dictionary", "Subtype invisibility",
     "Cancer molecular subtypes (HER2+, ALK+, BRCA, HR+/HER2-) are not in any Swedish public register.",
     "Observed",
     "Confirmed via Socialstyrelsen + RCC documentation review.",
     "METHODOLOGY.md structural caveats",
     "Stable structural limit; would change only via IQVIA proxy or Pfizer-internal data."),

    ("DT-02", "Methodology", "METHODOLOGY.md", "Förmån/rekvisition split",
     "Förmån vs rekvisition pharma split is not derivable per region from Kolada.",
     "Observed",
     "SKR + Kolada documentation review; SKR cirkulär 26:5 needed for proxy.",
     "findings_skr_lakemedel_2026.md",
     "SKR cirkulär 26:5 manual download (~15 min)."),

    ("DT-03", "Methodology", "METHODOLOGY.md", "RSV regional",
     "RSV regional surveillance is not published by FHM at region level.",
     "Observed",
     "FHM sminet3 pattern tested across slugs/dates; structural absence.",
     "pull_fhm_rsv.py output",
     "Stable structural limit; would need Socialstyrelsen Patientregistret J21.0 manual pull."),

    ("DT-04", "Methodology", "METHODOLOGY.md", "Hospital-administered",
     "Hospital-administered Pfizer products (Elrexfio, Hympavzi) are not in Läkemedelsregistret (which covers Rx only).",
     "Observed",
     "Socialstyrelsen scope documentation.",
     "findings_lakemedelsregistret_v2.md",
     "Concise (clinic-administered register) needed; awaiting IQVIA."),

    # ========== ROBUSTNESS / DATA QUALITY ==========
    ("DT-05", "QA", "Robustness QA sheet", "Sweden pop within range",
     "Sweden total population: 10,587,710 (within 10.5-10.7M expected band, 0.24% diff).",
     "Observed",
     "SCB primary record vs published official total.",
     "Robustness QA sheet",
     "Stable Observed."),

    ("DT-06", "QA", "Robustness QA sheet", "27/27 robustness checks pass",
     "All 27 robustness checks pass with 0 critical issues, 0 warnings (Codex audit confirmation).",
     "Observed",
     "Direct cell-by-cell run; results in Robustness QA sheet.",
     "Robustness QA sheet",
     "Recheck after each data refresh."),
]


def make_header_cell(cell, text, bg=PF_NAVY, fg="FFFFFF", size=10):
    cell.value = text
    cell.font = Font(name="Calibri", size=size, bold=True, color=fg)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = BORDER


def confidence_fill(tag_text):
    """Return appropriate fill color based on the confidence tag."""
    if not tag_text:
        return None
    s = tag_text.lower()
    # Combined tags: pick the most cautious color (purple wins, then red, then yellow, then green)
    if "needs pfizer validation" in s or "needs validation" in s:
        return PatternFill("solid", fgColor=TAG_NEEDS_VALIDATION)
    if "hypothesis" in s:
        return PatternFill("solid", fgColor=TAG_HYPOTHESIS)
    if "modeled" in s:
        return PatternFill("solid", fgColor=TAG_MODELED)
    if "observed" in s:
        return PatternFill("solid", fgColor=TAG_OBSERVED)
    return None


def append_evidence_ledger(wb):
    """Add new 'Evidence ledger' sheet."""
    ws = wb.create_sheet("Evidence ledger", index=2)  # right after Data Dictionary

    # Title row
    ws.cell(row=1, column=1, value="Evidence Ledger — Confidence Layer v1")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=9)

    ws.cell(row=2, column=1, value=(
        "Canonical truth-table of major analytical claims, each tagged Observed / Modeled / "
        "Hypothesis / Needs Pfizer validation. See EVIDENCE_CONFIDENCE_FRAMEWORK.md for taxonomy."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)

    # Color legend
    legend_row = 3
    ws.cell(row=legend_row, column=1, value="Legend:").font = Font(bold=True, size=9)
    legend_items = [
        ("Observed", TAG_OBSERVED),
        ("Modeled", TAG_MODELED),
        ("Hypothesis", TAG_HYPOTHESIS),
        ("Needs Pfizer validation", TAG_NEEDS_VALIDATION),
    ]
    for i, (label, fill) in enumerate(legend_items):
        c = ws.cell(row=legend_row, column=2 + i*2, value=label)
        c.fill = PatternFill("solid", fgColor=fill)
        c.font = Font(size=9, bold=True)
        c.alignment = Alignment(horizontal="center")
        c.border = BORDER

    # Header row
    headers = ["Claim ID", "Domain", "Source artefact", "Section", "Claim (short)",
               "Confidence", "Decision rule", "Evidence trail", "What would upgrade this"]
    for i, h in enumerate(headers, start=1):
        make_header_cell(ws.cell(row=5, column=i), h)

    # Body
    for r, row_data in enumerate(LEDGER, start=6):
        for c, value in enumerate(row_data, start=1):
            cell = ws.cell(row=r, column=c, value=value)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if c == 6:  # confidence column
                fill = confidence_fill(value)
                if fill:
                    cell.fill = fill
                cell.font = Font(name="Calibri", size=10, bold=True)

    # Column widths
    widths = [10, 14, 28, 28, 50, 22, 50, 36, 50]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Row heights — generous for wrap_text
    for r in range(6, 6 + len(LEDGER)):
        ws.row_dimensions[r].height = 90

    # Freeze header row
    ws.freeze_panes = "A6"

    # Autofilter on data range
    ws.auto_filter.ref = f"A5:I{5 + len(LEDGER)}"

    return ws


def add_confidence_to_opp_composite(wb):
    """Add Confidence + Confidence rule columns to OPP - All products composite."""
    ws = wb["OPP - All products composite"]
    last_col = ws.max_column

    # Add headers
    make_header_cell(ws.cell(row=1, column=last_col + 1), "Confidence")
    make_header_cell(ws.cell(row=1, column=last_col + 2), "Decision rule")

    # All composite rows are Modeled by definition
    for r in range(2, ws.max_row + 1):
        c1 = ws.cell(row=r, column=last_col + 1, value="Modeled")
        c1.font = Font(name="Calibri", size=10, bold=True)
        c1.fill = PatternFill("solid", fgColor=TAG_MODELED)
        c1.alignment = Alignment(vertical="top")
        c1.border = BORDER

        c2 = ws.cell(row=r, column=last_col + 2,
                     value="Composite of 3 sub-scores (burden, share-gap, demo) with author-chosen weights")
        c2.font = Font(name="Calibri", size=9)
        c2.alignment = Alignment(vertical="top", wrap_text=True)
        c2.border = BORDER

    ws.column_dimensions[get_column_letter(last_col + 1)].width = 14
    ws.column_dimensions[get_column_letter(last_col + 2)].width = 50


def add_confidence_to_ntradet(wb):
    """Add Confidence column to NT-rådet status v2 sheet."""
    ws = wb["NT-rådet status v2"]
    last_col = ws.max_column

    make_header_cell(ws.cell(row=1, column=last_col + 1), "Confidence")

    # Read existing status and decide tag
    status_col_idx = None
    for c in range(1, last_col + 1):
        if ws.cell(row=1, column=c).value == "NT-rådet status":
            status_col_idx = c
            break

    for r in range(2, ws.max_row + 1):
        status = ws.cell(row=r, column=status_col_idx).value if status_col_idx else None
        if status and "UNKNOWN" in str(status).upper():
            tag = "Observed + Needs Pfizer validation"
        elif status:
            tag = "Observed"
        else:
            tag = "Needs Pfizer validation"

        c1 = ws.cell(row=r, column=last_col + 1, value=tag)
        c1.font = Font(name="Calibri", size=10, bold=True)
        c1.fill = confidence_fill(tag)
        c1.alignment = Alignment(vertical="top")
        c1.border = BORDER

    ws.column_dimensions[get_column_letter(last_col + 1)].width = 28


def add_confidence_to_robustness(wb):
    """Add Confidence column to Robustness QA — all rows Observed by definition."""
    ws = wb["Robustness QA"]
    last_col = ws.max_column

    make_header_cell(ws.cell(row=1, column=last_col + 1), "Confidence")

    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=1).value:  # only rows with content
            c1 = ws.cell(row=r, column=last_col + 1, value="Observed")
            c1.font = Font(name="Calibri", size=10, bold=True)
            c1.fill = PatternFill("solid", fgColor=TAG_OBSERVED)
            c1.alignment = Alignment(vertical="top")
            c1.border = BORDER

    ws.column_dimensions[get_column_letter(last_col + 1)].width = 14


def add_region_master_confidence_sheet(wb):
    """Add a 'Region master — confidence' sheet documenting per-column tags."""
    region_master = wb["Region master"]
    headers = [c.value for c in region_master[1]]

    ws = wb.create_sheet("Region master — confidence")

    ws.cell(row=1, column=1, value="Region master — column-level confidence tags")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)

    ws.cell(row=2, column=1, value=(
        "Within each Region master column, the confidence tag is uniform — primary-source "
        "registers (SCB, Kolada, Socialstyrelsen, IQVIA) yield Observed; derived ratios with "
        "implicit denominator assumptions can shift to Modeled."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=4)

    for i, h in enumerate(["Column", "Source", "Confidence", "Note"], start=1):
        make_header_cell(ws.cell(row=4, column=i), h)

    # Per-column source mapping (Observed unless noted otherwise)
    col_specs = {
        "Region code": ("SCB region codes", "Observed", "Stable identifier"),
        "Region": ("SCB", "Observed", ""),
        "Sjukvårdsregion": ("Sveriges Sjukhusägares Förening", "Observed", ""),
        "Population": ("SCB BefolkningKod", "Observed", "2024 reference year"),
        "Pop 65+": ("SCB BefolkningKod", "Observed", ""),
        "Pop 75+": ("SCB BefolkningKod", "Observed", ""),
        "Pop women 15-44": ("SCB BefolkningKod", "Observed", ""),
        "Pop 0-1": ("SCB BefolkningKod", "Observed", ""),
        "Births 2024": ("SCB BE0101", "Observed", ""),
        "BRP/inv (tkr)": ("SCB regional accounts", "Observed", ""),
        "BRP total (mnkr)": ("SCB regional accounts", "Observed", ""),
        "Employed (1000s)": ("SCB AKU", "Observed", ""),
        "Specialist läkare (#)": ("Socialstyrelsen HSL", "Observed", ""),
        "HC cost/inv": ("Kolada N00945 / SKR", "Observed", ""),
        "HC excl pharma/inv": ("Kolada", "Observed", ""),
        "Primary care/inv": ("Kolada", "Observed", ""),
        "Pharma förmån/inv": ("Kolada N00992", "Observed", ""),
        "Pharma total/inv": ("Kolada N00992 (förmån only — see DT-02)", "Observed", "Förmån/rekvisition split not separable per DT-02"),
        "Breast ca rate /100k": ("RCC + SCB", "Observed", "Age-standardized incidence"),
        "Prostate ca rate /100k": ("RCC + SCB", "Observed", ""),
        "Lung ca incidence /100k": ("RCC + SCB", "Observed", ""),
        "Lung ca mortality /100k": ("Socialstyrelsen Dödsorsaksregistret", "Observed", ""),
        "Breast ca screening detect %": ("RCC INCA", "Observed", ""),
        "Breast ca surgery <28d %": ("RCC SVF + Kolada", "Observed", ""),
        "MI incidence /100k": ("Socialstyrelsen Patientregistret", "Observed", ""),
        "MI prevalence /100k": ("Socialstyrelsen Patientregistret", "Observed", ""),
        "Heart care quality (0-100)": ("RCC + national registers composite", "Modeled", "Composite quality index"),
        "Specialist wait <=90d %": ("Kolada SKL5544", "Observed", ""),
        "Operation wait <=90d %": ("Kolada SKL5545", "Observed", ""),
        "Median wait spec days": ("Kolada", "Observed", ""),
        "Median wait op days": ("Kolada", "Observed", ""),
        "Daily smokers %": ("FHM survey", "Observed", "Self-reported"),
        "Overweight/obese %": ("FHM survey", "Observed", "Self-reported BMI"),
        "Falls 80+ /100k": ("Socialstyrelsen Patientregistret", "Observed", ""),
        "Falls 65-79 /100k": ("Socialstyrelsen Patientregistret", "Observed", ""),
        "MPR 2yo %": ("FHM vaccine register", "Observed", ""),
        "HPV girls %": ("FHM vaccine register", "Observed", ""),
        "Antibiotic Rx /1000": ("Socialstyrelsen Läkemedelsregistret", "Observed", ""),
        "TBE cases 2025": ("FHM SmiNet", "Observed", ""),
        "TBE /100k 2025": ("FHM SmiNet ÷ SCB pop", "Observed", "Simple ratio of two Observed values"),
        "IPD cases 2025": ("FHM SmiNet", "Observed", ""),
        "IPD /100k 2025": ("FHM SmiNet ÷ SCB pop", "Observed", ""),
        "Vaccine sell-in /inv (SEK/yr)": ("IQVIA vaccines extract", "Observed", "From signed IQVIA delivery"),
        "Utrikes födda % 2024": ("SCB BE0101 Födelseregion", "Observed", ""),
        "Eftergymnasial utbildning 25-64 % 2024": ("SCB UF0506", "Observed", ""),
        "Förtida dödsfall 25-64 /100k (åldersstand.)": ("Kolada N79190", "Observed", ""),
        "Åtgärdbar dödlighet sjukvård /100k (3-års mv)": ("Kolada N79191", "Observed", ""),
        "Självmord 25+ /100k (5-års mv)": ("Kolada N72461", "Observed", ""),
    }

    r = 5
    for header in headers:
        if header is None:
            continue
        spec = col_specs.get(header, ("?", "Observed", ""))
        ws.cell(row=r, column=1, value=header).font = Font(name="Calibri", size=10)
        ws.cell(row=r, column=2, value=spec[0]).font = Font(name="Calibri", size=10)
        c3 = ws.cell(row=r, column=3, value=spec[1])
        c3.font = Font(name="Calibri", size=10, bold=True)
        c3.fill = confidence_fill(spec[1])
        ws.cell(row=r, column=4, value=spec[2]).font = Font(name="Calibri", size=10, italic=True)
        for col in range(1, 5):
            ws.cell(row=r, column=col).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=r, column=col).border = BORDER
        r += 1

    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 38
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 50
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:D{r-1}"


def update_readme(wb):
    """Append a section to the README sheet about the Confidence Layer."""
    ws = wb["README"]
    # Find next empty row
    r = ws.max_row + 2

    ws.cell(row=r, column=1, value="EVIDENCE CONFIDENCE LAYER (v14, 2026-04-25)")
    ws.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    ws.cell(row=r, column=1, value=(
        "Every major analytical claim is now tagged with one of four confidence levels: "
        "Observed (directly in primary-source data), Modeled (calculated from assumptions), "
        "Hypothesis (causal/strategic interpretation), Needs Pfizer validation (depends on "
        "Pfizer-internal data or pending external follow-up). See 'Evidence ledger' sheet for "
        "the canonical truth-table and EVIDENCE_CONFIDENCE_FRAMEWORK.md (working/docs) for "
        "taxonomy + decision rules."
    ))
    ws.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")


def main():
    print(f"Loading {SRC.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)

    print(f"Initial sheet count: {len(wb.sheetnames)}")
    print(f"Adding Evidence Ledger sheet ({len(LEDGER)} claim rows) ...")
    append_evidence_ledger(wb)

    print("Adding Confidence + Decision rule columns to OPP - All products composite ...")
    add_confidence_to_opp_composite(wb)

    print("Adding Confidence column to NT-rådet status v2 ...")
    add_confidence_to_ntradet(wb)

    print("Adding Confidence column to Robustness QA ...")
    add_confidence_to_robustness(wb)

    print("Adding Region master — confidence sheet ...")
    add_region_master_confidence_sheet(wb)

    print("Updating README ...")
    update_readme(wb)

    print(f"Final sheet count: {len(wb.sheetnames)}")
    print(f"Saving to {DST.name} ...")
    wb.save(DST)
    print("Done.")

    # Distribution summary
    tag_counts = {}
    for row in LEDGER:
        tag = row[5]
        for sub in [t.strip() for t in tag.split("+")]:
            tag_counts[sub] = tag_counts.get(sub, 0) + 1
    print("\nTag distribution across Evidence Ledger:")
    for tag, n in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {n}")
    print(f"\nTotal ledger rows: {len(LEDGER)}")


if __name__ == "__main__":
    main()
