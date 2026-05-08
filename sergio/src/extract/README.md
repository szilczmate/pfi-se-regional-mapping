# `src/extract/`

Raw → typed data ingestion. Each script pulls from one source, normalises, and writes to `data/raw/` or `data/interim/`. Outputs feed `src/transform/`.

## Public Swedish registries

| Script | Source | Output |
|---|---|---|
| `pull_scb_population.py` | SCB PxWeb API | Population per region/age/sex 2024 |
| `pull_scb_projections.py` | SCB PxWeb | Population projections to 2040, 2050 |
| `pull_scb_life_expectancy.py` | SCB PxWeb | Life expectancy per region |
| `pull_scb_foreign_born.py` | SCB PxWeb | Foreign-born share per region |
| `pull_scb_births.py` | SCB PxWeb | Annual births per region |
| `pull_scb_education.py` | SCB PxWeb | Education attainment per region |
| `pull_scb_grp.py` | SCB PxWeb | Gross regional product per capita |
| `pull_scb_sub_demographics.py` | SCB PxWeb | Sub-regional demographic breakdowns |
| `pull_kolada_extras_v2_data.py` | Kolada open API | Standardised regional KPIs |
| `pull_mortality_kolada.py` | Kolada open API | Premature mortality, healthcare-amenable mortality |
| `pull_lakemedelsregistret_v2.py` | Socialstyrelsen Statistikdatabas | Prescription counts by ATC code per region |
| `parse_lakemedelsregistret.py` | Local Läkemedelsregistret extract | Aggregate per Pfizer product per region |
| `pull_fhm_epi.py` | Folkhälsomyndigheten | Infectious disease epidemiology (TBE, IPD) |
| `pull_fhm_rsv.py` | Folkhälsomyndigheten | RSV epidemiology + vaccine coverage |
| `pull_rcc_reports.py` | Regionala cancercentrum (RCC) | Cancer-care signals per region |
| `pull_reklistor.py` | Regional reklistor PDFs | Regional formulary recommendations |
| `pull_skr_lakemedel_2026.py` | samverkansläkemedel.se | NT-rådet decisions, NSG roster |
| `pull_region_profile_extras.py` | Region websites | Verksamhetsplaner, governance pages |
| `download_parse_regional_pdfs_v4.py` | Region websites | Annual plans (PDFs) → text |
| `explore_kolada_extras.py` | Kolada open API | Exploratory KPI lookups |

## IQVIA + AVA inspection

| Script | Purpose |
|---|---|
| `inspect_iqvia_vaccines.py` | Schema inspection of IQVIA Vaccines extract |
| `inspect_ava_data.py` | Schema inspection of AVA RDS files |
| `inspect_ava_data_deep.py` | Deeper AVA structure analysis |
| `inspect_v28_for_ava_insert.py` | Pre-merge inspection for AVA→workbook integration |
