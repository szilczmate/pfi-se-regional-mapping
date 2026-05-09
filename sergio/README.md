# Pfizer Sweden Regional Mapping — Analysis

Brick-level, region-by-region analysis of Pfizer's commercial position across the 21 Swedish regions, integrating IQVIA Sell-In, AVA patient-level data, and public Swedish registries (SCB, Socialstyrelsen, Folkhälsomyndigheten, Kolada, samverkansläkemedel.se).

The repository contains the analytical pipeline (raw data → master JSON outputs) and the HTML presentation deck that consumes those outputs. Author: **Sergio Flores · Viti Science · VS-2026-PFI-001**.

## Repository structure

```
pfizer-sweden-mapping-analysis/
├── data/
│   ├── master/              # Canonical JSON outputs consumed by the deck
│   └── reference/           # Lookup tables (region codes, brick→region map)
├── src/
│   ├── extract/             # Raw → typed ingestion (IQVIA, AVA, SCB, Socialstyrelsen, …)
│   ├── transform/           # Analytical layers (trajectory, brick priority, ATTR, influence, quadrant)
│   ├── deck/                # HTML deck build pipeline + visualisations
│   └── utils/               # Shared helpers
└── deliverables/
    └── deck.html            # The final HTML presentation deck
```

## Master JSON outputs

| File | What it is | Consumed by |
|---|---|---|
| `data/master/deck_data.json` | Per-region scorecard — population, demographics, healthcare budget, equity indicators, Pfizer footprint per product | All deck slides |
| `data/master/share_arc.json` | Monthly CDK4/6 SEK share trajectory (Ibrance / Verzenios / Kisqali), Apr 2023 – Mar 2026, rolling 6-month windows | Slide 26 (share arc) |
| `data/master/brick_priority.json` | IQVIA brick-level Recovery and Defense rankings (CDK4/6) with recovery_sek per brick | Slide 28 (plays + brick) |
| `data/master/attr_pn_cm.json` | ATTR-PN and ATTR-CM proxy prevalence per sjukvårdsregion (from AVA Vyndaqel data) | Slide 27 (ATTR) |
| `data/master/quadrant_and_nt.json` | Region × product opportunity-actionability quadrant placements + NT-rådet status | Slide 14 (quadrant), slide 6 (M4) |
| `data/master/stakeholder_data.json` | 21-region stakeholder grid + critical intel + named individuals + influence ranking | Slide 16 (cornerstones), slide 17 (intel), slide 24 (Stockholm governance) |
| `data/master/deck_model.json` | Composite model state used by the deck for cross-slide consistency | Multiple slides |

## Data sources

| Source | Coverage | Pull script |
|---|---|---|
| IQVIA Sell-In (Pfizer-provided) | 36-month brick-level monthly data, three extracts (Vaccines, RD/IM, Oncology) | Manual extracts; processed via `src/transform/build_master_workbook_v13.py` |
| AVA (Pfizer-provided) | Patient-level data for Vyndaqel, Ibrance, Vydura | `src/transform/ava_w*.py` workstreams |
| SCB | Population, demographics, GRP, projections to 2040/2050 | `src/extract/pull_scb_*.py` |
| Socialstyrelsen | Patient register, Läkemedelsregistret prescription counts, Cancerregistret incidence | `src/extract/pull_lakemedelsregistret_v2.py`, `parse_lakemedelsregistret.py` |
| Folkhälsomyndigheten | Vaccine coverage, infectious disease epidemiology (RSV, TBE, IPD) | `src/extract/pull_fhm_*.py` |
| Kolada | Standardised regional KPIs (quality and access metrics) | `src/extract/pull_kolada_*.py`, `pull_mortality_kolada.py` |
| RCC | Regional cancer-care signals | `src/extract/pull_rcc_reports.py` |
| samverkansläkemedel.se | NT-rådet decisions, NSG roster, regional LK chairs | `src/extract/pull_skr_lakemedel_2026.py`, `pull_reklistor.py` |
| Region websites + Reklistor | Verksamhetsplaner, regional formulary documents | `src/extract/download_parse_regional_pdfs_v4.py` |

## How to rebuild

The pipeline runs in three sequential phases.

### 1. Extract — pull raw data

Each `src/extract/pull_*.py` script is independent. Run the relevant ones based on what data needs refreshing:

```bash
python src/extract/pull_scb_population.py
python src/extract/pull_kolada_extras_v2_data.py
python src/extract/pull_skr_lakemedel_2026.py
# … etc
```

### 2. Transform — compute analytical layers

```bash
# AVA workstreams (CDK4/6, ATTR, migraine)
python src/transform/ava_w1_cdk46_analysis.py
python src/transform/ava_w2_attr_analysis.py
python src/transform/ava_w3_migraine_analysis.py

# Master workbook with all derived variables
python src/transform/build_master_workbook_v13.py

# Brick priority + share arc + quadrant + influence
python src/transform/cdk46_brick_priority.py
python src/transform/f23_f24_cdk46_share_arc_persistence.py
python src/transform/build_actionability_quadrant.py
python src/transform/build_stakeholder_influence.py
```

### 3. Build the deck

```bash
# Generate chart assets
python src/deck/generate_deck_charts_v2.py

# Compose the deck HTML
python src/deck/build_deck_v5.py

# Inject latest master JSON into deck
python src/deck/reinject_data_v2.py
python src/deck/reinject_stakeholders_v3.py

# Final polish pass
python src/deck/polish_deck_v6.py
```

The output is `deliverables/deck.html` — open in any modern browser.

## Methodology

See [`methodology.md`](methodology.md) for the six analytical layers (data foundations, trajectory verdicts, region × product quadrant, influence scoring, brick priority, confidence framework) and the formulas behind each.

## Dependencies

Python 3.11+. See [`requirements.txt`](requirements.txt).

## Confidentiality

Internal use only. Do not redistribute without explicit Pfizer Sweden Access & Value approval.
