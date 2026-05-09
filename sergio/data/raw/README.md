# `data/raw/`

Public-registry data pulls — the inputs to the analytical pipeline. Every file here is reproducible by re-running the corresponding `src/extract/pull_*.py` script against the public source API or website.

## Contents

| Pattern | Source | Pull script |
|---|---|---|
| `kolada_*.json` | Kolada open API (kolada.se/api/v3) | `src/extract/pull_kolada_*.py` |
| `scb_*.json` | SCB PxWeb API (api.scb.se) | `src/extract/pull_scb_*.py` |
| `fhm_*.json` | Folkhälsomyndigheten data portal | `src/extract/pull_fhm_*.py` |
| `rcc/` | Regionala cancercentrum reports | `src/extract/pull_rcc_reports.py` |
| `reklistor/` | Regional Reklistor PDFs | `src/extract/pull_reklistor.py` |
| `regional_plans/` | Region websites — verksamhetsplaner (PDFs) | `src/extract/download_parse_regional_pdfs_v4.py` |
| `skr/` | samverkansläkemedel.se + SKR open documents | `src/extract/pull_skr_lakemedel_2026.py` |

## NOT included (confidential)

The following raw files are excluded by `.gitignore` and must be sourced separately:

- IQVIA Sell-In extracts (Vaccines, RD/IM, Oncology) — Pfizer-provided, contractually confidential
- AVA patient-level data (RDS files for Vyndaqel, Ibrance, Vydura) — Pfizer-provided, contractually confidential

## Refresh

To re-pull all public-registry data: run each `src/extract/pull_*.py` script in turn. The Kolada and SCB APIs are open and rate-limited but free. Allow ~30 minutes for a full refresh.
