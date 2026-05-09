# Data

## `master/`

Canonical JSON outputs of the analytical pipeline. These files are consumed directly by the deck and by any downstream tool.

| File | Schema | Source script |
|---|---|---|
| `deck_data.json` | List of 21 region records, each with ~80 fields covering demographics, healthcare budget, equity indicators, Pfizer footprint per product (Vyndaqel, Ibrance, Tukysa, Talzenna, Lorviqua, Xtandi, Xalkori, Elrexfio, Vydura, Abrysvo, Prevenar 20, FSME-IMMUN), vaccine market share, ATTR signals | `src/transform/build_master_workbook_v13.py` → `src/transform/rebuild_deck_model.py` |
| `share_arc.json` | Monthly time series Apr 2023 – Mar 2026, rolling 6-month CDK4/6 SEK share for Ibrance / Verzenios / Kisqali (Sweden national) | `src/transform/f23_f24_cdk46_share_arc_persistence.py` |
| `brick_priority.json` | `top_recovery` (top 15 bricks ranked by recovery_sek), `defense` (3 bricks above 30% Ibrance with competitor velocity threat), `totals` summary | `src/transform/cdk46_brick_priority.py` |
| `attr_pn_cm.json` | ATTR-PN and ATTR-CM proxy prevalence per sjukvårdsregion (per 100k and indexed to Sweden=100) — Norra, Stockholm-Sörmland, Mellansverige, Sydöstra, Södra, VGR | `src/transform/ava_w2_attr_pn_drilldown.py` |
| `quadrant_and_nt.json` | Region × product opportunity-actionability quadrant placements + NT-rådet recommendation status per Pfizer product | `src/transform/build_actionability_quadrant.py` |
| `stakeholder_data.json` | 21-region grid with named decision-makers (RD, HSD, RS ordf, HSN ordf, LK ordf) per region, NT-rådet and NSG sjukvårdsregion reps, named individuals with composite influence scores, critical intel observations | `src/transform/build_stakeholder_v10_email_inference.py` + `src/transform/fix_stakeholders_v1.py` |
| `deck_model.json` | Composite model state used by deck for cross-slide consistency (TLDR anchors, play-level synthesis) | `src/transform/rebuild_deck_model.py` |

## `reference/`

Lookup tables (region codes, IQVIA brick → region mapping, product → indication map, sjukvårdsregion membership). Currently empty — reference data is embedded in the relevant `src/transform/` scripts. Future refactors should externalise these here.

## Raw data (excluded from git)

Raw IQVIA Sell-In extracts (Vaccines, RD/IM, Oncology), AVA RDS files (Ibrance, Vyndaqel, Vydura), and SCB / Socialstyrelsen / Folkhälsomyndigheten / Kolada pulls live in `data/raw/` and `data/interim/` locally. These are excluded from the repository via `.gitignore` because the IQVIA and AVA extracts are confidential.

To rebuild the master JSON outputs from raw data, see the rebuild instructions in the root [`README.md`](../README.md#how-to-rebuild).
