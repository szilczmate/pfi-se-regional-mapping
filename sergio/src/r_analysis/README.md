# `src/r_analysis/`

R analysis scripts — modelling, clustering, scenario sizing, and figure generation that complement the Python analytical pipeline.

## Setup

| Script | Purpose |
|---|---|
| `00_setup_v2.R` | Load packages, configure paths, set theme (run once at session start) |

## Core analytical scripts

| Script | What it does |
|---|---|
| `01_penetration_gap.R` | Per-region penetration gap analysis (Pfizer share vs class total) |
| `02_ibrance_forecast.R` | Ibrance trajectory forecast under three scenarios |
| `03_regression_drivers.R` | Regression of regional uptake on demographic + KPI predictors |
| `04_cluster_regions.R` | Hierarchical clustering of 21 regions on Pfizer-relevance features |
| `05_opportunity_sizing.R` | Region × product opportunity SEK sizing |
| `06_sweden_maps.R` | Sweden choropleth maps (per-region metrics) |
| `07_vaccine_competitive.R` | Vaccines competitive landscape (RSV, pneumococcal, TBE) |
| `08_priority_matrix.R` | Priority matrix scoring across the 231 region × product cells |

## Scenario / what-if scripts

| Script | What it does |
|---|---|
| `A_abrysvo_avvakta.R` | Abrysvo TLV avvakta-override scenario sensitivity |
| `B_budget_impact.R` | Budget impact analysis per Pfizer product |
| `C_implementation_latency.R` | NT-rådet decision → regional LK listing latency analysis |
| `D_kisqali_scenarios.R` | Kisqali class-naive share scenario modelling |

## Dependencies

Standard R 4.x with: `tidyverse`, `sf` (geographic), `cluster`, `forecast`, `ggplot2` extensions. Full list in `00_setup_v2.R`.
