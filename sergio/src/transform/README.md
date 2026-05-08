# `src/transform/`

Analytical layers. Each script reads from `data/raw/` or `data/interim/` (or earlier transform outputs), applies one analytical operation, and writes to `data/master/`.

## AVA workstreams (Pfizer-provided patient-level data)

| Script | Workstream |
|---|---|
| `ava_w1_cdk46_analysis.py` | W1 — CDK4/6 class-naive starts, national |
| `ava_w1b_cdk46_per_region.py` | W1b — CDK4/6 per region cuts |
| `ava_w2_attr_analysis.py` | W2 — ATTR Vyndaqel patient counts per sjukvårdsregion |
| `ava_w2_attr_pn_drilldown.py` | W2 — ATTR-PN proxy index (Norra over-index calculation) |
| `ava_w3_migraine_analysis.py` | W3 — Vydura vs Atogepant migraine-class analysis |
| `ava_w3b_vydura_switching.py` | W3b — Vydura switching dynamics |
| `ava_audit.py` | Internal audit of AVA data integrity |
| `ava_audit_iqvia_crosscheck.py` | Cross-check AVA patient counts vs IQVIA Sell-In direction |
| `ava_audit_iqvia_explore.py` | Exploratory IQVIA-vs-AVA reconciliation |

## CDK4/6 share + brick analytics

| Script | Output |
|---|---|
| `f23_f24_cdk46_share_arc_persistence.py` | `data/master/share_arc.json` — rolling 6-month SEK share trajectory |
| `cdk46_brick_priority.py` | `data/master/brick_priority.json` — Recovery + Defense brick rankings |

## Quadrant + influence + opportunity

| Script | Output |
|---|---|
| `build_actionability_quadrant.py` | `data/master/quadrant_and_nt.json` — 231 cells classified into 4 quadrants |
| `build_opportunity_matrix.py` | Region × product opportunity SEK matrix |
| `build_pfizer_opportunity_score.py` | Composite opportunity score per cell |
| `build_stakeholder_influence.py` | Composite influence scores for stakeholder records |
| `build_engagement_angles.py` | Per-region engagement angles for stakeholder briefings |
| `build_scenario_sensitivity.py` | Sensitivity analysis on quadrant placements + recovery sizing |

## Stakeholder mapping

| Script | Purpose |
|---|---|
| `build_stakeholder_v10_email_inference.py` | Pattern-infer email contacts from regional standard formats |
| `build_stakeholder_v10_honest.py` | Conservative stakeholder build (no email inference) |
| `update_stakeholder_mapping_v2.py` | Refresh of stakeholder mapping from latest pulls |
| `update_ntradet_v2.py` | NT-rådet decision tracker refresh |
| `fix_stakeholders_v1.py` | Apply audit corrections to stakeholder data (Stockholm HSN, NSG roster, Pia Näsvall date) |

## NT-rådet + TLV + competitive

| Script | Purpose |
|---|---|
| `build_ntradet_findings.py` | NT-rådet decision pattern analysis per Pfizer product |
| `nt_radet_timing_analysis.py` | NT-rådet decision timing histograms |
| `build_tlv_findings.py` | TLV cost-effectiveness review status tracker |
| `build_competitive_intelligence.py` | Competitor product positioning per Pfizer class |
| `build_penetration_analyses.py` | Per-region penetration of Pfizer products vs class total |

## Master workbook + derived data

| Script | Purpose |
|---|---|
| `build_master_workbook_v13.py` | Compose 65-sheet master workbook from all extracts and transforms |
| `build_clean_workbook.py` | Clean-pass workbook with consistent naming |
| `build_derived_variables_index.py` | Index of all derived variables and their formulas |
| `build_evidence_ledger.py` | Per-claim evidence ledger linking each figure to source |
| `build_analytical_findings.py` | Synthesise top-level analytical findings across workstreams |
| `region_data.py` | Region-level data handler / API for downstream scripts |
| `region_dashboards.py` | Per-region dashboard data preparation |
| `rebuild_deck_model.py` | Compose `data/master/deck_model.json` from workbook outputs |

## Quality assurance

| Script | Purpose |
|---|---|
| `qa_data_robustness.py` | Cross-source consistency checks |
| `qa_master_workbook.py` | Workbook structural validation |
| `qc_delivery_pass.py` | Pre-delivery quality control |
