# `src/deck/`

HTML deck build pipeline + visualisation scripts. Produces `deliverables/deck.html` from the master JSON outputs.

## Build pipeline

| Script | Purpose |
|---|---|
| `build_deck_v5.py` | Compose the deck HTML from master JSON + chart assets |
| `build_deck_v2_pfizer_template.py` | Earlier template iteration (kept for reference) |
| `reinject_data_v2.py` | Re-inject `deck_data.json` into the deck HTML when data refreshes |
| `reinject_stakeholders_v3.py` | Re-inject `stakeholder_data.json` STAKEHOLDERS + INTEL arrays into the deck |
| `polish_deck_v6.py` | Final polish pass (fact-check fixes, wording cleanup) |
| `fix_deck_v5_figure_aspect_ratios.py` | Normalise figure aspect ratios across slides |
| `verify_v29.py` | Pre-publish deck verification |
| `viti_theme.py` | Brand theme constants (colours, typography) for chart generation |

## Chart generation — slide-level (`viz_v*`)

| Script | Slide |
|---|---|
| `viz_v1_tldr_scorecard.py` | Slide 2 — TLDR five-anchor card |
| `viz_v2_share_arc.py` | Slide 26 — CDK4/6 share arc |
| `viz_v3_class_naive.py` | Class-naive AVA visualisation |
| `viz_v4_attr_correction.py` | Slide 27 — ATTR over-index |
| `viz_v5_brick_quadrant.py` | Slide 8 — Brick priority quadrant |
| `viz_v6_persistence.py` | Persistence trajectory |
| `viz_v7_vaccines.py` | Slide 13 — Vaccines panel |
| `viz_v8_oncology_backbone.py` | Oncology backbone visualisation |
| `viz_v9_cornerstones_grid.py` | Slide 16 — Cornerstones grid |
| `viz_v10_migraine.py` | Migraine class panel |
| `viz_v11_stakeholder_quadrant.py` | Stakeholder influence × applicability |
| `viz_v12_cornerstones_tactical.py` | Cornerstone tactical brief layouts |
| `viz_v13_coverage.py` | Coverage and equity overlay |

## Chart generation — national-level (`viz_n*`)

| Script | View |
|---|---|
| `viz_n1_equity_composite.py` | National equity composite |
| `viz_n2_pfizer_heatmap.py` | Slide 12 — Pfizer position heatmap (21 regions × 11 products) |
| `viz_n3_stakeholder_governance.py` | Stakeholder governance density per region |
| `viz_n4_equity_dimensions.py` | Equity dimension breakdown |
| `viz_n5_demographic_pressure.py` | Demographic pressure index |
| `viz_n6_disease_burden.py` | Disease burden per region |
| `viz_n7_vaccination_matrix.py` | Vaccination coverage matrix |
| `viz_n8_pfizer_category_mix.py` | Pfizer category mix per region |
| `viz_n9_equity_solidarity.py` | Equity-solidarity overlay |

## Chart generation — region-level (`viz_r*`)

| Script | Output (per region) |
|---|---|
| `viz_r0_overview.py` | Region overview composite |
| `viz_r1_region_overview.py` | Region overview KPI panel |
| `viz_r2_disease_burden.py` | Region disease burden detail |
| `viz_r3_pfizer_portfolio.py` | Region Pfizer portfolio table |
| `viz_r4_vaccine_landscape.py` | Region vaccine landscape |
| `viz_r5_governance.py` | Region governance + cornerstones |
| `viz_r6_competitive.py` | Region competitive positioning |
| `viz_ra_region_context.py` | Region context strip |
| `viz_rb_pfizer_footprint.py` | Region Pfizer footprint summary |

## Other plotting

| Script | Purpose |
|---|---|
| `plot_actionability_quadrant.py` | Standalone quadrant plot |
| `plot_budget_impact_heatmap.py` | Budget-impact heatmap |
| `plot_deck_vaccine_figures.py` | Vaccine figure batch |
| `plot_oncology_figures.py` | Oncology figure batch |
| `plot_rdim_figures.py` | RD/IM figure batch |
| `plot_v28_figures.py` | Figure batch from workbook v28 |
| `plot_v4_figures.py` | Earlier figure batch |
| `plot_v5_doc_figures.py` | Document figure batch |
| `generate_deck_charts_v2.py` | Orchestrator — runs all viz scripts |
