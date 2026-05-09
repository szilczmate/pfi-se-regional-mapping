# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Region data accessor.

Pulls all fields needed for the 6-slide regional profile from workbook v30
+ stakeholder mapping v10. Returns a single dict per region.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v30.xlsx"
SH = ROOT / "delivery" / "07_stakeholder_mapping_v10.xlsx"


def _load_sheet(name):
    return pd.read_excel(WB, sheet_name=name)


def get_region(region_full_name):
    """Return a dict of all fields for a single region (e.g. 'Region Stockholm')."""
    rm = _load_sheet("Region master")
    le = _load_sheet("Life expectancy")
    pp = _load_sheet("Population projections")
    pf = _load_sheet("Pfizer total footprint")
    vm = _load_sheet("Vaccine market share")
    cdk = _load_sheet("CDK4-6 competitive landscape")
    tp = _load_sheet("Top product per region")

    row = rm[rm["Region"] == region_full_name].iloc[0]
    le_row = le[le["Region"] == region_full_name].iloc[0]
    pp_row = pp[pp["Region"] == region_full_name].iloc[0]
    pf_row = pf[pf["Region"] == region_full_name].iloc[0]
    vm_row = vm[vm["Region"] == region_full_name].iloc[0]
    cdk_row = cdk[cdk["Region"] == region_full_name].iloc[0]
    tp_row = tp[tp["Region"] == region_full_name].iloc[0]

    pharma_pct_hc = (row["Pharma total cost per capita (SEK)"] /
                     row["Healthcare cost per capita (SEK)"]) * 100

    pop_65_share = row["Pop 65+"] / row["Population"] * 100

    return {
        "region": region_full_name,
        "region_short": region_full_name.replace("Region ", ""),
        "healthcare_region": row["Healthcare region"],

        # Demographics
        "population": row["Population"],
        "pop_65_share": pop_65_share,
        "grp_per_capita_ksek": row["GRP per capita (kSEK)"],
        "growth_65_to_2040": pp_row["65+ growth % 2024→2040"],
        "life_expectancy_avg": le_row["Average"],
        "foreign_born_pct": row["Foreign-born % (2024)"],

        # Healthcare Budget
        "hc_cost_per_capita": row["Healthcare cost per capita (SEK)"],
        "pharma_per_capita": row["Pharma total cost per capita (SEK)"],
        "primary_care_per_capita": row["Primary care cost per capita (SEK)"],
        "pharma_pct_hc": pharma_pct_hc,
        "vaccine_sellin_per_capita": row["Vaccine sell-in per capita (SEK/year)"],
        "specialists": row["Specialist physicians (#)"],

        # Population Projections
        "pop_2040": pp_row["Pop 2040"],
        "pop_65_2040": pp_row["65+ 2040"],
        "pop_2050": pp_row["Pop 2050"],
        "births_2024": row["Births 2024"],
        "pop_women_15_44": row["Pop women 15-44"],
        "pop_0_1": row["Pop 0-1"],

        # Health Equity Indicators
        "premature_mortality_25_64": row["Premature mortality 25–64 /100k (age-std)"],
        "hc_amenable_mortality": row["Healthcare-amenable mortality /100k (3-yr MA)"],
        "suicide_25plus": row["Suicide 25+ /100k (5-yr MA)"],
        "post_secondary_pct": row["Post-secondary education 25–64 % (2024)"],
        "daily_smokers_pct": row["Daily smokers %"],
        "overweight_obese_pct": row["Overweight/obese %"],

        # Disease burden (slide 2)
        "breast_ca_rate": row["Breast ca rate /100k"],
        "prostate_ca_rate": row["Prostate ca rate /100k"],
        "lung_ca_incidence": row["Lung ca incidence /100k"],
        "lung_ca_mortality": row["Lung ca mortality /100k"],
        "breast_screening_pct": row["Breast ca screening detect %"],
        "breast_surg_28d_pct": row["Breast ca surgery <28d %"],
        "mi_incidence": row["MI incidence /100k"],
        "mi_prevalence": row["MI prevalence /100k"],
        "heart_care_quality": row["Heart care quality (0-100)"],
        "tbe_cases_2025": row.get("TBE cases 2025"),
        "tbe_per100k_2025": row.get("TBE /100k 2025"),
        "ipd_cases_2025": row.get("IPD cases 2025"),
        "ipd_per100k_2025": row.get("IPD /100k 2025"),
        "antibiotic_rx_per1000": row["Antibiotic Rx /1000"],
        "mpr_2yo_pct": row["MPR 2yo %"],
        "hpv_girls_pct": row["HPV girls %"],

        # Implied case counts (rate × population / 100k)
        "breast_implied_cases": row["Breast ca rate /100k"] * row["Population"] / 100000,
        "prostate_implied_cases": row["Prostate ca rate /100k"] * row["Population"] / 100000,
        "lung_implied_cases": row["Lung ca incidence /100k"] * row["Population"] / 100000,

        # Pfizer footprint (3-year SEK totals)
        "pfizer_total_3yr": pf_row["Total Pfizer SEK"],
        "pfizer_vaccines_3yr": pf_row["Vaccines SEK"],
        "pfizer_rdim_3yr": pf_row["RD/IM SEK"],
        "pfizer_oncology_3yr": pf_row["Oncology SEK"],
        "pfizer_rank": pf_row["Pfizer SEK rank"],
        "abrysvo_3yr": pf_row["ABRYSVO SEK (3yr)"],
        "prevenar20_3yr": pf_row["PREVENAR 20 SEK (3yr)"],
        "fsme_vuxen_3yr": pf_row["FSME-IMMUN VUXEN SEK (3yr)"],
        "fsme_junior_3yr": pf_row["FSME-IMMUN JUNIOR SEK (3yr)"],
        "vyndaqel_3yr": pf_row["VYNDAQEL SEK (3yr)"],
        "vydura_3yr": pf_row["VYDURA SEK (3yr)"],
        "ibrance_3yr": pf_row["IBRANCE SEK (3yr)"],
        "tukysa_3yr": pf_row["TUKYSA SEK (3yr)"],
        "talzenna_3yr": pf_row["TALZENNA SEK (3yr)"],
        "lorviqua_3yr": pf_row["LORVIQUA SEK (3yr)"],
        "elrexfio_3yr": pf_row["ELREXFIO SEK (3yr)"],
        "xtandi_3yr": pf_row["XTANDI SEK (3yr)"],
        "benefix_3yr": pf_row["BENEFIX SEK (3yr)"],
        "refacto_3yr": pf_row["REFACTO AF SEK (3yr)"],

        # Vaccine market shares (Pfizer share of class)
        "rsv_market_total": vm_row["RSV total"],
        "rsv_pfizer_sek": vm_row["Pfizer Abrysvo"],
        "rsv_pfizer_share": vm_row["Share %"],
        "pneu_market_total": vm_row["Pneu total"],
        "pneu_pfizer_sek": vm_row["Pfizer Prevenar"],
        "pneu_pfizer_share": vm_row["Share %.1"],
        "tbe_market_total": vm_row["TBE total"],
        "tbe_pfizer_sek": vm_row["Pfizer FSME"],
        "tbe_pfizer_share": vm_row["Share %.2"],

        # CDK4/6 competitive
        "ibrance_units": cdk_row["IBRANCE units"],
        "ibrance_sek": cdk_row["IBRANCE SEK"],
        "ibrance_delta_18m": cdk_row["Ibrance Δ% (1H vs 2H)"],
        "verzenios_units": cdk_row["VERZENIOS units"],
        "verzenios_sek": cdk_row["VERZENIOS SEK"],
        "verzenios_delta_18m": cdk_row["Verzenios Δ%"],
        "kisqali_units": cdk_row["KISQALI units"],
        "kisqali_sek": cdk_row["KISQALI SEK"],
        "kisqali_delta_18m": cdk_row["Kisqali Δ%"],
        "cdk_class_units": cdk_row["Class total units"],
        "cdk_pfizer_units_share": cdk_row["Pfizer share % (units)"],
        "cdk_pfizer_sek_share": cdk_row["Pfizer share % (SEK)"],
        "cdk_substitution_direction": cdk_row["Substitution direction"],

        # Top product priorities
        "top_product_1": tp_row["Top Pfizer product"],
        "top_product_1_score": tp_row["Score"],
        "top_product_2": tp_row["2nd priority"],
        "top_product_2_score": tp_row["Score.1"],
        "top_product_3": tp_row["3rd priority"],
        "top_product_3_score": tp_row["Score.2"],
    }


def get_stakeholders(region_full_name):
    """Return a dict of governance role names + influence scores for a region."""
    sk = pd.read_excel(SH, sheet_name="Stakeholders")
    row = sk[sk["Region"] == region_full_name].iloc[0]
    return {
        "regiondirektor":   row["Regiondirektör"],
        "hsd":              row["HSD"],
        "rs_ordf":          row["RS ordf"],
        "hsn_ordf":         row["HSN ordf"],
        "lk_ordf":          row["LK ordf"],
        "nt_radet_rep":     row["NT-rådet rep (SVR)"],
        "nsg_rep":          row["NSG rep (SVR)"],
    }


# Curated narratives per region (hand-written, not programmatic)
NARRATIVES = {
    "Region Stockholm": {
        "pipeline_areas": (
            "Largest patient pool nationally — 2.5M, 24% of Sweden — drives volume across every category.",
            "Breast cancer 208/100k (~5,140 cases) anchors Tukysa and CDK4/6 demand.",
            "Prostate cancer 185/100k (~4,580 cases) — Talzenna BRCA scales with volume.",
            "65+ growth +35% to 2040 — strongest Abrysvo + Prevenar 20 tailwind in Sweden.",
        ),
        "cv_rare_disease": (
            "MI incidence 207/100k, prevalence 193/100k — large cardiovascular base.",
            "Heart care quality 92.6/100 — highest in Sweden; clinical infrastructure is the differentiator.",
            "ATTR-CM: per-100k below the national mean (Södra leads). Vyndaqel "
            "share holds at scale rather than concentration.",
            "Largest haemophilia market by SEK — natural Hympavzi launch site "
            "(BeneFIX 40.6M kr + Refacto AF over 3 years).",
        ),
        "competitor_threats": [
            ("Enhertu (AstraZeneca/Daiichi)",
             "HR+/HER2-low post-endokrin breast cancer 2L. Threat to Tukysa positioning."),
            ("Verzenios (Eli Lilly)",
             "CDK4/6 inhibitor, HR+/HER2- 2L+ and adjuvant. Already eroding Ibrance share — Stockholm hardest hit."),
            ("Tecvayli (Janssen)",
             "Multipelt myelom 2L combination with daratumumab. Threat to Elrexfio launch trajectory."),
        ],
        "archetype": "Academic specialist · large-volume reference centre",
        "strategic_summary": [
            "Largest patient pool nationally (2.5M, 24% of Sweden).",
            "Lowest CDK4/6 Pfizer share among major regions — defend Ibrance position via Mats Ek and Stockholm LK.",
            "Vyndaqel SEK leader at 283M kr (3yr) — scale rather than per-capita concentration.",
            "Largest haemophilia market by SEK — primary Hympavzi launch site.",
            "TBE endemic with 78.6% Pfizer share — maintain leadership.",
            "Low Prevenar 20 share at 12.4% — clear gap opportunity for the 65+ cohort.",
        ],
        "grp_pharma_note": (
            "Stockholm has the highest GRP per capita in Sweden (833 kSEK) yet "
            "pharma cost per capita (3,104 SEK) sits below the national mean. "
            "This indicates room for higher pharmaceutical utilisation relative "
            "to the region's economic capacity, particularly in adult vaccines "
            "(85 SEK sell-in/cap, modest for the largest market) and high-value "
            "specialty oncology."
        ),
    },
    "Region Västerbotten": {
        "pipeline_areas": (
            "ATTR-PN founder cluster (V30M, Skellefteå) drives rare-disease specialty caseload.",
            "Highest MI incidence in Sweden (264/100k) — large cardiovascular burden.",
            "Overweight/obese 52.7% above the national mean — cardiometabolic addressable.",
            "65+ growth +9.8% to 2040 — RSV/pneumococcal demand stable, not expanding.",
        ),
        "cv_rare_disease": (
            "MI incidence 264/100k (highest nationally); prevalence 254/100k.",
            "Heart care quality 45.5/100 — significantly below the national "
            "mean; clinical capacity gap.",
            "ATTR-PN: 25.0 patients per 100k (8.1× the Sweden mean) — V30M "
            "founder cluster is a once-in-a-portfolio rare-disease anchor.",
            "Norrlands universitetssjukhus Umeå is the Swedish reference centre for the V30M founder cluster — "
            "natural carry-into for Hympavzi (haemophilia) and Elrexfio "
            "(myeloma) rare-disease specialty infrastructure.",
        ),
        "competitor_threats": [
            ("Amvuttra (Alnylam)",
             "siRNA TTR silencer for ATTR-PN. Direct threat to Vyndaqel in the founder-cluster population."),
            ("Beyonttra (BridgeBio)",
             "Acoramidis TTR stabiliser, same mechanism as tafamidis. ATTR-CM only — flank threat."),
            ("Verzenios (Eli Lilly)",
             "CDK4/6 inhibitor +91% — Ibrance share erosion at small volumes but high growth rate."),
        ],
        "archetype": "Rare-disease specialty centre · founder-cluster anchor",
        "strategic_summary": [
            "Vyndaqel 214M kr (74% of Pfizer footprint) — ATTR-PN founder cluster anchor.",
            "Norrlands universitetssjukhus Umeå — natural site for Hympavzi + Elrexfio carry-in.",
            "Highest MI incidence + lowest heart-care quality — cardiovascular pipeline opportunity.",
            "TBE endemic with 61.9% FSME share — maintain against ENCEPUR.",
            "Pia Näsvall (NSG Chair + HSD) — highest-leverage stakeholder per Pfizer SEK.",
            "Anders Bergström (NT-rådet Vice Chair, Norrbotten) — Norra access influence.",
        ],
        "grp_pharma_note": (
            "Västerbotten has below-average GRP per capita (548 kSEK vs Stockholm's 833) "
            "yet healthcare cost per capita (37,900 SEK) is above the national mean. "
            "The region carries clinical complexity (rare disease, cardiovascular) "
            "that drives spend rather than economic capacity. Pfizer SEK per 100k is "
            "2× higher here than in Stockholm — a function of the Vyndaqel "
            "concentration."
        ),
    },
    "Region Gotland": {
        "pipeline_areas": (
            "Smallest region nationally (61k pop, 27.5% 65+) — high aging share, modest absolute volume.",
            "FSME-IMMUN dominates Pfizer footprint at 79.9% TBE share — TBE-endemic island context.",
            "Top product Abrysvo — 45.8% RSV share suggests room above 60% national benchmark.",
            "Combined kommun+region structure is a structural exception — single-stop governance.",
        ),
        "cv_rare_disease": (
            "MI incidence 274/100k — above national mean.",
            "Heart care quality data not reported (zero in workbook); structural data gap.",
            "Vyndaqel 7M kr (3-yr) — small but present; sjukvårdsregion view via Stockholm-Gotland.",
            "Hympavzi opportunity routes via Karolinska reference (Gotland clinically integrates with Stockholm-Gotland sjukvårdsregion).",
        ),
        "competitor_threats": [
            ("Kisqali (Novartis)",
             "Strongest CDK4/6 growth at +133% over 18 months — at small volumes (170 units) any switch is decisive."),
            ("Verzenios (Eli Lilly)",
             "264 CDK4/6 units — already class-leader by volume; Ibrance held at 28% share via Stockholm-Gotland anchor."),
            ("ENCEPUR (Bavarian Nordic)",
             "TBE competitor — Pfizer holds 79.9% TBE share; ENCEPUR is the residual challenger."),
        ],
        "archetype": "Small island specialty · TBE-endemic + Stockholm-Gotland dependent",
        "strategic_summary": [
            "Pfizer total 3-yr footprint: 44M kr (rank 21 — smallest by absolute scale).",
            "FSME-IMMUN 6.6M kr (TBE) is the largest single product — 79.9% Pfizer TBE share.",
            "Abrysvo at 45.8% RSV share — room to grow toward national 64.5% benchmark.",
            "CDK4/6 share holds at 28.5% via Ibrance + Stockholm-Gotland sjukvårdsregion influence.",
            "Meit Fohlin (RS ordf, S) + Stefan Hollmark (RD) — both verified HIGH confidence.",
            "Sjukvårdsregion routing via Stockholm — engagement coordinated with Mats Ek + Johan Bratt + Rickard Malmström triumvirate.",
        ],
        "grp_pharma_note": (
            "Gotland has a modest GRP per capita (453 kSEK) and elevated pharma cost per "
            "capita (4,314 SEK) — above national mean despite small scale. The aging "
            "demographic (27.5% 65+) and TBE-endemic geography drive structurally higher "
            "per-capita pharmaceutical spend. Vaccine sell-in per capita (69 SEK) is "
            "modest — Abrysvo + Prevenar 20 represent the demographic-tailwind upside."
        ),
    },
    "Region Uppsala": {
        "pipeline_areas": (
            "Akademiska sjukhuset Uppsala — national academic referral centre across precision oncology + rare disease.",
            "65+ growth +26.4% to 2040 — substantial Abrysvo + Prevenar 20 demographic tailwind.",
            "Vydura is top Pfizer product — but Uppsala is the P6 structural anomaly (Atogepant first-line at 56%).",
            "Lorviqua #3 priority — ALK+ NSCLC academic specialist demand at Akademiska.",
        ),
        "cv_rare_disease": (
            "MI incidence 218/100k — slightly above national mean; heart care quality 78.4/100.",
            "Vyndaqel 32M kr (3yr) — moderate ATTR concentration; Akademiska handles complex amyloid referrals.",
            "Mellansverige sjukvårdsregion routes Hympavzi launch through Akademiska as a secondary site to Norrlands universitetssjukhus.",
            "TBE endemic with 14.6/100k cases (2025) — but Pfizer FSME share only 47.6% (ENCEPUR challenge).",
        ),
        "competitor_threats": [
            ("Atogepant/Aquipta (AbbVie)",
             "Migraine first-line at 56% (Akademiska prescribing-preference structural anomaly). The single most important Vydura defence target nationally."),
            ("Kisqali (Novartis)",
             "+116% CDK4/6 18-month growth at 1,119 units — Akademiska oncology drives volume."),
            ("ENCEPUR (Bavarian Nordic)",
             "FSME-IMMUN share only 47.6% in TBE-endemic geography — competitive vulnerability."),
        ],
        "archetype": "Academic specialist · Mellansverige reference centre · P6 anomaly",
        "strategic_summary": [
            "Akademiska sjukhuset = Mellansverige reference centre (population 408k, GRP 574 kSEK).",
            "P6 (Migraine) Tier-1 engagement target — Atogepant first-line at 56% (national Vydura first-line is 75%).",
            "Pfizer 3-yr footprint 189M kr (rank 8); Vydura, FSME-IMMUN, Lorviqua = top-3.",
            "Jan Melin (LK Uppsala + NT-rådet Mellansverige rep, rank 1 by aggregate influence 179.5).",
            "Helena Proos (RS ordf) verified HIGH; Johan von Knorring (RD) verified HIGH.",
            "Structural HSN exception — Sjukhusstyrelsen + Vårdstyrelsen split (no single HSN ordförande).",
        ],
        "grp_pharma_note": (
            "Uppsala has above-average GRP per capita (574 kSEK) and below-average pharma "
            "cost per capita (3,476 SEK) — economic capacity exceeds clinical "
            "consumption. Vaccine sell-in per capita (119 SEK) is among the highest in "
            "Sweden — TBE endemicity + adult vaccination uptake. Akademiska sjukhuset's "
            "academic referral function means several Pfizer specialty SEK streams "
            "(Lorviqua, Tukysa, Vydura) flow through Uppsala on behalf of patients "
            "registered elsewhere."
        ),
    },
    "Region Sörmland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 144M kr (rank 11) — mid-tier with strong ATTR + vaccines mix.",
            "65+ growth +18.9% to 2040 — Abrysvo + Prevenar 20 demographic tailwind moderate.",
            "Top product FSME-IMMUN — TBE-endemic with 84% RSV Pfizer share (above national mean).",
            "Equity composite #1 (highest need) — premature mortality, healthcare-amenable mortality both elevated.",
        ),
        "cv_rare_disease": (
            "MI incidence 276/100k (above national); heart care quality 79.8/100 (mid-pack).",
            "Vyndaqel 22M kr (3yr) — modest ATTR concentration via Mellansverige sjukvårdsregion.",
            "Hympavzi opportunity routes via Akademiska Uppsala (Mellansverige reference).",
            "Cancer burden moderate — breast 131/100k (low end), prostate 204/100k (high end).",
        ),
        "competitor_threats": [
            ("Kisqali (Novartis)",
             "+66% CDK4/6 18-month growth — ahead of Verzenios in this region (Verzenios -30% which is unusual)."),
            ("ENCEPUR (Bavarian Nordic)",
             "FSME-IMMUN share only 45.6% in TBE-endemic geography."),
            ("Vaxneuvance (MSD)",
             "Pneumococcal class — Pfizer Prevenar 20 share only 9.9%; significant gap."),
        ],
        "archetype": "Mid-tier · highest equity need · Mellansverige integrated",
        "strategic_summary": [
            "Pfizer total 3-yr 144M kr (rank 11); FSME-IMMUN, Prevenar 20, Vyndaqel = top-3.",
            "Equity composite #1 nationally — premature mortality + healthcare-amenable mortality both elevated.",
            "Mellansverige sjukvårdsregion via Jan Melin (rank 1 aggregate influence) — engagement leverage.",
            "RS acts as HSN — Christoffer Öqvist (RS ordf, M) is the de-facto HSN authority (structural exception).",
            "Magnus Johansson (RD) verified HIGH; Lars Steen (LK ordf) verified HIGH.",
            "P3 (Vaccines) Tier-2 target — Prevenar 20 9.9% leaves clear MSD competitive gap.",
        ],
        "grp_pharma_note": (
            "Sörmland has below-average GRP per capita (438 kSEK) and slightly above-mean "
            "pharma cost per capita (3,638 SEK) — economically modest with elevated "
            "clinical consumption. The equity composite #1 ranking flags multiple "
            "amenable-mortality dimensions; Pfizer's adult vaccine portfolio (Abrysvo, "
            "Prevenar 20) aligns well with the demographic + equity narrative."
        ),
    },
    "Region Västmanland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 118M kr (rank 16) — mid-tier; Tukysa is top product priority.",
            "65+ growth +17.3% to 2040 — Abrysvo + Prevenar 20 demographic tailwind moderate.",
            "Vyndaqel 29M kr largest single product — Mellansverige ATTR concentration.",
            "Heart care quality 86.6/100 — second-highest in Sweden after Stockholm.",
        ),
        "cv_rare_disease": (
            "MI incidence 236/100k (slightly above national); heart care quality 86.6/100 (second-best nationally).",
            "Vyndaqel 28.9M kr (3yr) — moderate concentration; Mellansverige sjukvårdsregion routing.",
            "Lung cancer incidence 30/100k — among the lowest nationally; lung-specific oncology focus less acute.",
            "TBE endemic but FSME share only 24.3% — substantial ENCEPUR penetration; unusual for endemic geography.",
        ),
        "competitor_threats": [
            ("Kisqali (Novartis)",
             "+98% CDK4/6 18-month growth — and Ibrance at -67% in this region (steepest collapse)."),
            ("Verzenios (Eli Lilly)",
             "+61% CDK4/6 18-month growth at 575 units — class-leader by volume here."),
            ("ENCEPUR (Bavarian Nordic)",
             "FSME-IMMUN share only 24.3% in TBE-endemic geography — major competitive deficit."),
        ],
        "archetype": "Mid-tier · best heart-care quality · Mellansverige integrated",
        "strategic_summary": [
            "Pfizer total 3-yr 118M kr (rank 16); Tukysa, FSME-IMMUN, Prevenar 20 = top-3 priority.",
            "Heart care quality 86.6/100 — second-highest in Sweden (after Stockholm 92.6).",
            "Ibrance share collapse most extreme: -67% over 18 months (vs national -23%).",
            "FSME-IMMUN 24.3% TBE share is the lowest in any TBE-endemic region — recovery target.",
            "Mikael Andersson Elfgren (RS ordf, M) verified HIGH; Lars Almroth (HSD) being replaced by Jonas Cederberg (tf. from 2026-05-04).",
            "P2 (CDK4/6) Tier-2 defence — Ibrance at 22% units share, half of national mean.",
        ],
        "grp_pharma_note": (
            "Västmanland has GRP per capita 457 kSEK (mid-pack) and pharma cost per "
            "capita 3,386 SEK (below national mean). Vaccine sell-in per capita 87 SEK — "
            "moderate. The TBE FSME share at 24.3% in an endemic geography is the most "
            "striking competitive feature: Pfizer is losing systematically to ENCEPUR "
            "here in a way not seen elsewhere; investigation warranted."
        ),
    },
    "Region Örebro län": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 121M kr (rank 15); Vydura is top product priority.",
            "65+ growth +15.2% to 2040 — Abrysvo + Prevenar 20 demographic tailwind moderate.",
            "Universitetssjukhuset Örebro — secondary academic centre in Mellansverige.",
            "Equity composite Top-5 nationally — elevated need across multiple dimensions.",
        ),
        "cv_rare_disease": (
            "MI incidence 271/100k (above national); heart care quality 39.6/100 (low — clinical capacity gap).",
            "Vyndaqel only 0.9M kr (3yr) — minimal ATTR concentration here despite Mellansverige routing.",
            "Lung cancer mortality 51.5/100k — elevated (national mean 47/100k); P4 Lorviqua relevance.",
            "Vydura 0.4M kr — Mellansverige migraine market routes more through Uppsala (Akademiska anomaly + Vydura preference).",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+57% CDK4/6 18-month growth at 870 units — class-leader by volume; Ibrance at 21% units share."),
            ("Kisqali (Novartis)",
             "+72% CDK4/6 18-month growth at 575 units — second-fastest CDK4/6 growth alongside Verzenios."),
            ("ENCEPUR (Bavarian Nordic)",
             "FSME-IMMUN share only 23.9% — second-lowest TBE share among TBE-endemic regions."),
        ],
        "archetype": "Mid-tier secondary academic · Mellansverige · brick recovery target",
        "strategic_summary": [
            "Pfizer total 3-yr 121M kr (rank 15); Vydura, FSME-IMMUN, Lorviqua = top-3 priority.",
            "Brick #4 nationally for CDK4/6 Recovery (0.52M kr opportunity at 8.0% Ibrance share).",
            "Heart care quality 39.6 — clinical capacity gap; cardiovascular pipeline opportunity.",
            "Universitetssjukhuset Örebro — secondary Mellansverige academic centre.",
            "Jenny Steen (RS ordf, S) verified HIGH; Maria Palmetun Ekbäck (LK ordf) verified HIGH.",
            "Behcet Barsom (HSN ordf) MEDIUM confidence — verification needed.",
        ],
        "grp_pharma_note": (
            "Örebro län has GRP per capita 522 kSEK (slightly above mean) and pharma cost "
            "per capita 3,454 SEK (slightly below mean). Vaccine sell-in per capita 108 "
            "SEK is the highest in Mellansverige outside Uppsala. The 39.6 heart-care "
            "quality score is the most actionable clinical-capacity finding — flags both "
            "an unmet-need narrative and a pipeline-development opportunity for Pfizer's "
            "cardiovascular portfolio."
        ),
    },
    "Region Dalarna": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 157M kr (rank 10) — Vyndaqel + FSME-IMMUN heavy.",
            "65+ growth only +7.1% to 2040 — vaccine demographic tailwind weakest in Mellansverige.",
            "Top product Vyndaqel (ATTR) — concentration via Mellansverige Hospital amyloid network.",
            "FSME-IMMUN 38M kr — Pfizer 89.2% TBE share (highest in Mellansverige).",
        ),
        "cv_rare_disease": (
            "MI incidence 294/100k (top-tier nationally); heart care quality 61.8/100 (mid-pack).",
            "Vyndaqel 27.4M kr — ATTR-CM caseload via Mellansverige amyloid referral network.",
            "Hympavzi opportunity via Akademiska Uppsala (Mellansverige routing).",
            "Lung cancer 45/100k — elevated; P4 Lorviqua + Talzenna relevance via Falun/Borlänge.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+93% CDK4/6 18-month growth — among the steepest in Sweden."),
            ("Kisqali (Novartis)",
             "+106% CDK4/6 18-month growth at 578 units — class race fully active."),
            ("Amvuttra (Alnylam)",
             "ATTR-PN siRNA — secondary threat to Vyndaqel ATTR-CM concentration."),
        ],
        "archetype": "Mellansverige rural · FSME-IMMUN dominant · ATTR mid-tier",
        "strategic_summary": [
            "Pfizer total 3-yr 157M kr (rank 10); Vyndaqel, Lorviqua, Abrysvo = top-3 priority.",
            "FSME-IMMUN 89.2% TBE share — strongest Pfizer TBE position in Sweden.",
            "Brick #8 nationally for CDK4/6 Recovery (0.34M kr at 7.7% Ibrance share).",
            "65+ growth only +7.1% — weakest demographic tailwind; Abrysvo growth assumption modest.",
            "Elin Norén (RS ordf, S) verified HIGH; Sofia Jarl (HSN ordf) verified HIGH.",
            "Mellansverige routing via Jan Melin (rank 1 aggregate influence).",
        ],
        "grp_pharma_note": (
            "Dalarna has GRP per capita 456 kSEK (mid-pack) and pharma cost per capita "
            "3,647 SEK (slightly above mean). Vaccine sell-in per capita 76 SEK reflects "
            "TBE endemicity + adult Abrysvo uptake. The 89.2% FSME share is structurally "
            "the strongest Pfizer TBE position in Sweden — a defence anchor, not an "
            "opportunity, for P3 vaccines play."
        ),
    },
    "Region Gävleborg": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 113M kr (rank 17) — Vyndaqel-heavy with weak Ibrance.",
            "65+ growth only +8.9% to 2040 — vaccine demographic tailwind moderate.",
            "Top product Abrysvo — RSV Pfizer share 52% (below national mean of 64.5%).",
            "Equity composite Top-5 nationally — Sörmland #1, Gävleborg in same tier.",
        ),
        "cv_rare_disease": (
            "MI incidence 258/100k (above national); heart care quality 51.2/100 (low end).",
            "Vyndaqel 26M kr — moderate ATTR concentration via Mellansverige routing.",
            "Lung cancer 52/100k — second-highest nationally; significant P4 + tobacco-related cluster.",
            "First Swedish region with corporatized public primary care (RD Göran Angergård dual role as acting CEO).",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+25% CDK4/6 18-month growth at 976 units — clear class-leader; Ibrance only 6.5% share."),
            ("Kisqali (Novartis)",
             "+63% CDK4/6 18-month growth at 730 units — second-largest CDK4/6 player."),
            ("Vaxneuvance (MSD)",
             "Pneumococcal — Prevenar 20 only 11.5% share (large MSD majority)."),
        ],
        "archetype": "Mellansverige rural · CDK4/6 lowest Pfizer share · structural innovator",
        "strategic_summary": [
            "Pfizer total 3-yr 113M kr (rank 17); Abrysvo, Lorviqua, Vyndaqel = top-3 priority.",
            "CDK4/6 Pfizer share only 6.5% units — lowest in Sweden among major regions.",
            "Brick #2 nationally for CDK4/6 Recovery (0.58M kr at 0.0% Ibrance share — virtual zero).",
            "Lung cancer 52/100k second-highest nationally — P4 Talzenna + Lorviqua relevance.",
            "Patrik Stenvard (RS ordf, M) verified HIGH; Göran Angergård (RD/CEO dual role).",
            "First Swedish region to corporatize public primary care via wholly-owned aktiebolag.",
        ],
        "grp_pharma_note": (
            "Gävleborg has GRP per capita 434 kSEK (low) and pharma cost per capita 3,553 "
            "SEK (mid-pack). Vaccine sell-in per capita 68 SEK is modest. The 6.5% CDK4/6 "
            "Pfizer share is the headline — Ibrance has virtually exited this market. "
            "Brick-level recovery targeting (Gävle = #2 brick nationally) is the P2 "
            "play here. The corporatized primary care structure may offer different "
            "engagement leverage points than other Mellansverige regions."
        ),
    },
    "Region Värmland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 102M kr (rank 18); FSME-IMMUN top product priority.",
            "65+ growth only +9.4% to 2040 — vaccine demographic tailwind weak.",
            "Top product FSME-IMMUN, Abrysvo, Vyndaqel = top-3 priority.",
            "Norway border geography — TBE pressure + demographic ageing both pronounced.",
        ),
        "cv_rare_disease": (
            "MI incidence 272/100k; heart care quality 83.4/100 (above mean).",
            "Vyndaqel 22.6M kr — moderate ATTR concentration.",
            "Pneumococcal Prevenar 20 share 20.6% — among the highest in Mellansverige.",
            "Lung cancer 39/100k — at national mean.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+122% CDK4/6 18-month growth — among the steepest in Sweden; Ibrance 12% share."),
            ("Kisqali (Novartis)",
             "+64% CDK4/6 18-month growth at 539 units."),
            ("Aquipta (AbbVie)",
             "Migraine class growth — Vydura 0.55M kr at moderate within-class share."),
        ],
        "archetype": "Mellansverige rural · TBE-vaccine anchor · CDK4/6 collapsed",
        "strategic_summary": [
            "Pfizer total 3-yr 102M kr (rank 18); FSME-IMMUN, Abrysvo, Vyndaqel = top-3.",
            "Pneumococcal Prevenar 20 share 20.6% — second-highest in Mellansverige (after Uppsala).",
            "CDK4/6 Pfizer share 12% units — well below national mean; Verzenios dominant.",
            "65+ growth +9.4% — weak demographic tailwind for Abrysvo/Prevenar 20.",
            "Åsa Johansson (RS ordf, S) verified HIGH; Malgorzata Antoniewicz (LK ordf) verified HIGH.",
            "Mellansverige routing via Jan Melin (rank 1 aggregate influence).",
        ],
        "grp_pharma_note": (
            "Värmland has GRP per capita 475 kSEK (mid-pack) and pharma cost per capita "
            "3,790 SEK (above mean). Vaccine sell-in per capita 107 SEK is among the "
            "highest in Mellansverige — TBE-endemic + Norway-border population dynamics. "
            "Pneumococcal share 20.6% is a quiet strength worth defending; CDK4/6 12% "
            "is the recovery work."
        ),
    },
    "Region Östergötland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 239M kr (rank 6) — Universitetssjukhuset Linköping anchors Sydöstra sjukvårdsregion.",
            "65+ growth +17.5% to 2040 — solid Abrysvo + Prevenar 20 demographic tailwind.",
            "Vydura top product — strong migraine class position (Linköping neurology).",
            "Tukysa #2 priority — HER2+ breast cancer at 207/100k breast cancer incidence (mid-tier).",
        ),
        "cv_rare_disease": (
            "MI incidence 256/100k (above national); heart care quality 49.4/100 (low — clinical capacity gap).",
            "Vyndaqel 40M kr — strongest ATTR concentration in Sydöstra sjukvårdsregion.",
            "Hympavzi opportunity via Linköping (Sydöstra reference centre); secondary to Norrlands universitetssjukhus.",
            "Lung cancer mortality 44/100k — at national mean.",
        ),
        "competitor_threats": [
            ("Kisqali (Novartis)",
             "+201% CDK4/6 18-month growth — among the steepest in Sweden at 677 units."),
            ("Verzenios (Eli Lilly)",
             "+153% CDK4/6 18-month growth at 924 units — class race fully active."),
            ("Aquipta (AbbVie)",
             "Migraine — Vydura is top product but Atogepant trajectory worth monitoring."),
        ],
        "archetype": "Sydöstra reference · academic specialist · brick Defense candidate",
        "strategic_summary": [
            "Pfizer total 3-yr 239M kr (rank 6); Vydura, Tukysa, Lorviqua = top-3 priority.",
            "Universitetssjukhuset Linköping = Sydöstra sjukvårdsregion academic centre.",
            "CDK4/6 Pfizer share 36.5% SEK — above national mean; Linköping brick = Defense target.",
            "Mårten Lindström engagement (NT-rådet Chair, Sydöstra rep) covers this region directly.",
            "Marie Morell (RS ordf, M) verified HIGH; Karl Landergren (HSD) recently in transition.",
            "Christina Fischer (LK ordf) verified HIGH.",
        ],
        "grp_pharma_note": (
            "Östergötland has GRP per capita 553 kSEK (above mean) and pharma cost per "
            "capita 3,294 SEK (below mean). Vaccine sell-in per capita 75 SEK is "
            "moderate. The 40M kr Vyndaqel concentration is the second-largest in "
            "Sydöstra (after Skåne); Linköping's academic referral function pulls "
            "ATTR-CM cases beyond local population denominator."
        ),
    },
    "Region Jönköpings län": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 163M kr (rank 9) — Tukysa is top product priority.",
            "65+ growth +16.0% to 2040 — solid Abrysvo + Prevenar 20 demographic tailwind.",
            "Triple-leverage governance cluster — Mårten Lindström + Maria Ekelund + Bojestig successor.",
            "Breast cancer 221/100k — second-highest nationally; Tukysa demand elevated.",
        ),
        "cv_rare_disease": (
            "MI incidence 272/100k (above national); heart care quality 74.9/100 (above mean).",
            "Vyndaqel 23M kr — moderate ATTR concentration via Sydöstra routing.",
            "Hympavzi opportunity via Sydöstra (Linköping reference); engagement coordinated through Lindström + Ekelund.",
            "FSME-IMMUN 87.2% TBE share — strong Pfizer position.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+76% CDK4/6 18-month growth at 1,483 units — class-leader by wide margin; Ibrance only 14.3% share."),
            ("Kisqali (Novartis)",
             "+31% CDK4/6 18-month growth at 817 units — second-largest CDK4/6 player."),
            ("Vaxneuvance (MSD)",
             "Pneumococcal — Prevenar 20 11.8% share (large MSD majority)."),
        ],
        "archetype": "Sydöstra Triple-leverage governance · CDK4/6 collapsed · Tukysa anchor",
        "strategic_summary": [
            "Pfizer total 3-yr 163M kr (rank 9); Tukysa, Vydura, Prevenar 20 = top-3 priority.",
            "Triple-leverage governance cluster: Mårten Lindström (NT-rådet Chair) + Maria Ekelund (LK + Sydöstra) + Bojestig successor (Q3 2026 watch).",
            "CDK4/6 Pfizer share 14.3% units — well below national mean; Verzenios fully dominant.",
            "Breast cancer 221/100k — second-highest nationally (after Kronoberg); Tukysa anchor.",
            "Rachel De Basso (RS ordf, S) verified HIGH; Maria Ekelund (LK ordf) verified HIGH.",
            "Thomas Gustafsson (HSN ordf) — Folkhälsa och sjukvård nämnd, NOT Katarina Nyberg-Finn (Jämtland H. only).",
        ],
        "grp_pharma_note": (
            "Jönköping has GRP per capita 508 kSEK (mid-pack) and pharma cost per capita "
            "3,311 SEK (below mean). Vaccine sell-in per capita 85 SEK is moderate. The "
            "Sydöstra triple-leverage governance is the most concentrated access "
            "geography Pfizer has — three named individuals routing across NT-rådet "
            "(Lindström), LK formulary (Ekelund), and HSD (Bojestig successor) in one "
            "region."
        ),
    },
    "Region Kalmar": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 133M kr (rank 13); Abrysvo top product priority.",
            "65+ growth +10.3% to 2040 — moderate vaccine demographic tailwind.",
            "Vyndaqel 41M kr (3yr) — large ATTR concentration via Sydöstra Linköping referral.",
            "Heart care quality 32.2/100 — among the lowest nationally; clinical capacity gap.",
        ),
        "cv_rare_disease": (
            "MI incidence 259/100k (above national); heart care quality 32.2/100 (low — clinical capacity gap).",
            "Vyndaqel 41M kr — second-largest single-product Pfizer SEK in Sydöstra (after Östergötland).",
            "Hympavzi opportunity via Linköping (Sydöstra reference); engagement via Lindström + Ekelund cluster.",
            "FSME-IMMUN 75.4% TBE share — Pfizer strongly positioned.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+285% CDK4/6 18-month growth — among the steepest growth rates in Sweden at 330 units."),
            ("Kisqali (Novartis)",
             "+37% CDK4/6 18-month growth at 642 units — class-leader by volume."),
            ("Aquipta (AbbVie)",
             "Migraine — Vydura 0.7M kr at moderate within-class share."),
        ],
        "archetype": "Sydöstra · ATTR concentration · CDK4/6 collapsed (Ibrance -69%)",
        "strategic_summary": [
            "Pfizer total 3-yr 133M kr (rank 13); Abrysvo, Vyndaqel, Prevenar 20 = top-3 priority.",
            "Ibrance -69% over 18 months — second-steepest collapse nationally (after Västmanland).",
            "Vyndaqel 41M kr — second-largest in Sydöstra; Sydöstra triple-leverage cluster engagement applies.",
            "Heart care quality 32.2 — among the lowest nationally; cardiovascular pipeline opportunity.",
            "Angelica Katsanidou (RS ordf, S) verified HIGH; Magdalena Bosson (RD, installed Jan 2026 after Eriksson resignation).",
            "Fredrik Hagerman (LK ordf) verified HIGH.",
        ],
        "grp_pharma_note": (
            "Kalmar has GRP per capita 448 kSEK (low) and pharma cost per capita 3,442 "
            "SEK (mid-pack). Vaccine sell-in per capita 67 SEK is modest. The Vyndaqel "
            "41M kr concentration is unusually large for a region of this scale — "
            "Linköping referral pattern explains some, but Pfizer Medical Affairs may "
            "want to validate the underlying ATTR caseload (related to the Örebro "
            "Vyndaqel anomaly question already logged for follow-up)."
        ),
    },
    "Region Skåne": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 675M kr (rank 3) — Lund + Malmö academic anchor of Södra sjukvårdsregion.",
            "65+ growth +24% to 2040 — strong Abrysvo + Prevenar 20 demographic tailwind.",
            "Breast cancer 253/100k — highest nationally; Tukysa demand at scale.",
            "Vyndaqel 179M kr (3yr) — largest in Södra sjukvårdsregion; Södra leads ATTR-CM per-100k (idx 156).",
        ),
        "cv_rare_disease": (
            "MI incidence 270/100k; heart care quality 48.3/100 (low end).",
            "Vyndaqel 179M kr — Södra sjukvårdsregion is the actual ATTR-CM per-100k leader (not Norra).",
            "Lund University Hospital — academic referral routes for rare oncology + cardiology.",
            "Hympavzi opportunity via Lund (Södra reference); Skåne is largest haemophilia market in Södra.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+192% CDK4/6 18-month growth at 3,771 units — class-leader by volume; Ibrance at 36% share."),
            ("Kisqali (Novartis)",
             "+49% CDK4/6 18-month growth at 2,643 units — third-place but growing steadily."),
            ("Atogepant (AbbVie)",
             "Migraine — Vydura 9.2M kr (third-largest nationally); within-class defence relevant."),
        ],
        "archetype": "Södra sjukvårdsregion academic anchor · ATTR-CM per-100k leader · large-volume reference centre",
        "strategic_summary": [
            "Pfizer total 3-yr 675M kr (rank 3); Tukysa, Vydura, Prevenar 20 = top-3 priority.",
            "Vyndaqel 179M kr — Södra sjukvårdsregion is the actual ATTR-CM per-100k leader (idx 156, surpasses Norra).",
            "Lund University Hospital + SUS Malmö = Södra reference centres for P4 precision oncology.",
            "Breast cancer 253/100k — highest nationally; Tukysa demand at scale.",
            "Carl Johan Sonesson (RS ordf, M) verified HIGH; Stefan Nilsson (LK ordf) verified HIGH.",
            "Jonna Myrebris (RD, post-2025-12 transition); Anna Mannfalk (HSN ordf, M).",
        ],
        "grp_pharma_note": (
            "Skåne has GRP per capita 515 kSEK (mid-pack) and pharma cost per capita "
            "3,277 SEK (below mean). Vaccine sell-in per capita 62 SEK is modest "
            "considering scale (1.4M population). The 179M kr Vyndaqel concentration is "
            "the second-largest in Sweden after Stockholm — and on per-100k basis Södra "
            "leads ATTR-CM, a finding that re-frames the historical 'Norrland Cornerstone' "
            "narrative (Norrland is ATTR-PN per AVA W2)."
        ),
    },
    "Region Blekinge": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 60M kr (rank 20) — small region but high per-capita pharma intensity.",
            "65+ growth only +9.9% to 2040 — vaccine demographic tailwind weak.",
            "Top product Prevenar 20 — uncommon for a small region; Blekinge IPD penetration opportunity (top in workbook OPP sheet).",
            "Heart care quality 100/100 — best-in-class nationally (small N caveat).",
        ),
        "cv_rare_disease": (
            "MI incidence 323/100k (third-highest nationally after Norrbotten + Västernorrland).",
            "Vyndaqel 14.8M kr — moderate ATTR concentration via Södra routing.",
            "Heart care quality 100/100 — best score nationally; small reporting denominator caveat.",
            "Lung cancer 52/100k — high (tied with Gävleborg); P4 Talzenna + Lorviqua relevance.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+1,285% CDK4/6 18-month growth — anomalous figure (small base effect at 297 units)."),
            ("Kisqali (Novartis)",
             "+28% CDK4/6 18-month growth at 466 units — class-leader by volume."),
            ("Vaxneuvance (MSD)",
             "Pneumococcal — Prevenar 20 only 8.3% share (large MSD majority despite Prevenar 20 being Pfizer top product here)."),
        ],
        "archetype": "Södra small · IPD penetration top opportunity · CV burden elevated",
        "strategic_summary": [
            "Pfizer total 3-yr 60M kr (rank 20); Prevenar 20, Abrysvo, Lorviqua = top-3 priority.",
            "IPD penetration top opportunity nationally (workbook OPP sheet) — Prevenar 20 lead role.",
            "MI incidence 323/100k — third-highest nationally; cardiovascular pipeline opportunity.",
            "Heart care quality 100/100 — best-in-class (small N caveat); paradoxical with high MI burden.",
            "Björn Tenland Nurhadi (RS ordf, M) verified HIGH; Helena Ringborn (LK ordf) verified HIGH.",
            "Caroline Nilsson (HSD, post-2025-07 transition).",
        ],
        "grp_pharma_note": (
            "Blekinge has GRP per capita 521 kSEK (slightly above mean) and pharma cost "
            "per capita 3,905 SEK (above mean). Vaccine sell-in per capita 49 SEK is "
            "the lowest in Södra. The IPD penetration top-opportunity ranking + Prevenar "
            "20 already being top product priority makes this a tight P3 vaccines focus "
            "candidate."
        ),
    },
    "Region Halland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 202M kr (rank 7) — coastal Södra region with strong CDK4/6 share.",
            "65+ growth +25.5% to 2040 — strong Abrysvo + Prevenar 20 demographic tailwind.",
            "CDK4/6 Pfizer share 51.2% units — HIGHEST in Sweden (Pfizer-leading reference case).",
            "Vyndaqel 79M kr — third-largest single-product SEK in Södra after Skåne + Stockholm.",
        ),
        "cv_rare_disease": (
            "MI incidence 250/100k (slightly above national); heart care quality 70.6/100 (above mean).",
            "Vyndaqel 79M kr — substantial ATTR concentration; Halmstad + Varberg + Kungsbacka clinical network.",
            "Hympavzi opportunity via Lund (Södra reference); secondary haemophilia market.",
            "Tukysa is top product priority — HER2+ breast cancer at 204/100k breast cancer rate.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+196% CDK4/6 18-month growth — but Ibrance still leads at 51.2% share (the only region where Ibrance is lead)."),
            ("Kisqali (Novartis)",
             "+22% CDK4/6 18-month growth at 511 units — third place."),
            ("Aquipta (AbbVie)",
             "Migraine — Vydura 1.5M kr at moderate within-class share."),
        ],
        "archetype": "Södra coastal · CDK4/6 reference case · Pfizer-leading position",
        "strategic_summary": [
            "Pfizer total 3-yr 202M kr (rank 7); Tukysa, Lorviqua, Abrysvo = top-3 priority.",
            "CDK4/6 Pfizer share 51.2% units — HIGHEST in Sweden; the P2 reference case for share defence.",
            "Vyndaqel 79M kr — substantial ATTR concentration in Södra.",
            "65+ growth +25.5% — strong Abrysvo + Prevenar 20 demographic tailwind.",
            "Mikaela Waltersson (RS ordf, M) verified HIGH 2026-04-24; Tamara Adem (LK ordf) verified HIGH.",
            "Structural HSN exception — local municipal HSNs + HSU (no single region-tier HSN ordförande).",
        ],
        "grp_pharma_note": (
            "Halland has GRP per capita 457 kSEK (mid-pack) and pharma cost per capita "
            "4,043 SEK (above mean). Vaccine sell-in per capita 56 SEK is modest. The "
            "51.2% CDK4/6 Pfizer share is the most actionable single number — P2 plays "
            "brief uses Halland as the reference case for what 'good' looks like; the "
            "question is what Halland clinicians know that other regions don't."
        ),
    },
    "Region Kronoberg": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 138M kr (rank 12); Tukysa top product priority.",
            "65+ growth +13.5% to 2040 — moderate Abrysvo + Prevenar 20 demographic tailwind.",
            "Breast cancer 223/100k — first or second highest nationally (alongside Jönköping).",
            "Vyndaqel 62M kr — substantial ATTR concentration in Södra (Växjö + Ljungby).",
        ),
        "cv_rare_disease": (
            "MI incidence 285/100k (above national); heart care quality 0/100 — data gap (likely not reported).",
            "Vyndaqel 62M kr — fourth-largest single-product Pfizer SEK in Södra.",
            "Hympavzi opportunity via Lund (Södra reference) + secondary Växjö amyloid clinic.",
            "Lung cancer 30/100k — among the lowest nationally; lung-specific oncology focus less acute.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+117% CDK4/6 18-month growth at 577 units — class-leader by margin."),
            ("Kisqali (Novartis)",
             "+72% CDK4/6 18-month growth at 701 units — second-place."),
            ("Aquipta (AbbVie)",
             "Migraine — Vydura 0.4M kr at moderate within-class share."),
        ],
        "archetype": "Södra · breast cancer high · ATTR mid-tier · CDK4/6 stable",
        "strategic_summary": [
            "Pfizer total 3-yr 138M kr (rank 12); Tukysa, Vyndaqel, Prevenar 20 = top-3 priority.",
            "Breast cancer 223/100k — among the highest nationally; Tukysa demand pressure.",
            "Ibrance share -1.2% (essentially flat) — unusual stability vs national -23%.",
            "Vyndaqel 62M kr — substantial ATTR concentration via Växjö amyloid clinic.",
            "Henrietta Modig Serrate (RS ordf, S) verified HIGH; Fredrik Schön (LK ordf) verified HIGH.",
            "Andreas Liljenrud (RD); Ida Eriksson (HSN ordf) MEDIUM confidence.",
        ],
        "grp_pharma_note": (
            "Kronoberg has GRP per capita 571 kSEK (above mean) and pharma cost per "
            "capita 3,408 SEK (mid-pack). Vaccine sell-in per capita 79 SEK is moderate. "
            "Heart care quality reported at 0 — this is a data gap (likely under-"
            "reporting), not a true zero; flag for verification with Region Kronoberg."
        ),
    },
    "Västra Götalandsregionen": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 781M kr (rank 2) — second-largest after Stockholm.",
            "65+ growth +20.6% to 2040 — strong Abrysvo + Prevenar 20 demographic tailwind.",
            "Sahlgrenska Universitetssjukhuset = Västra sjukvårdsregion academic anchor.",
            "Vydura is top product priority — strong migraine class position.",
        ),
        "cv_rare_disease": (
            "MI incidence 249/100k (slightly below national); heart care quality 67/100 (mid-pack).",
            "Vyndaqel 168M kr — third-largest single-product Pfizer SEK in Sweden (after Stockholm + Skåne).",
            "Hympavzi opportunity via Sahlgrenska — third-largest haemophilia market by SEK after Stockholm + Skåne.",
            "Vydura 12M kr — second-largest migraine SEK nationally (after Skåne).",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+128% CDK4/6 18-month growth at 4,639 units — class-leader by volume; Ibrance 35% share."),
            ("Kisqali (Novartis)",
             "+51% CDK4/6 18-month growth at 2,738 units — third-place but growing."),
            ("Atogepant (AbbVie)",
             "Migraine — Vydura is top product but Atogepant trajectory worth monitoring."),
        ],
        "archetype": "Västra sjukvårdsregion sole-region · Sahlgrenska academic anchor · second-largest scale",
        "strategic_summary": [
            "Pfizer total 3-yr 781M kr (rank 2); Vydura, Lorviqua, FSME-IMMUN = top-3 priority.",
            "Sahlgrenska Universitetssjukhuset = Västra sjukvårdsregion academic anchor (sole-region structure).",
            "VGR P2 biggest recovery target nationally — 140 class-naive starts last 6mo, only 3.6% Ibrance capture (vs 7.3% national).",
            "Vyndaqel 168M kr — third-largest in Sweden.",
            "Helén Eliasson (RS ordf, S) verified HIGH 2026-04-24 (helen.m.eliasson@vgregion.se).",
            "Jonas Claesson (HSD, post-2025-10 transition) — also NSG Mellansverige rep (rank 2 aggregate influence 163.5).",
        ],
        "grp_pharma_note": (
            "VGR has GRP per capita 603 kSEK (above mean) and pharma cost per capita "
            "2,800 SEK — the LOWEST per-capita pharma in Sweden. Vaccine sell-in per "
            "capita 84 SEK is moderate. The pharma per-capita underspend at high GRP "
            "is the headline finding; suggests room for higher pharmaceutical "
            "utilisation across the portfolio. P2 (CDK4/6) recovery is the headline "
            "VGR-specific finding from AVA W1b — biggest recovery target nationally."
        ),
    },
    "Region Västernorrland": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 132M kr (rank 14); Abrysvo top product priority.",
            "65+ growth only +4.1% to 2040 — vaccine demographic tailwind weakest in Norra (after Norrbotten).",
            "MI incidence 316/100k — second-highest nationally after Norrbotten.",
            "P2 (CDK4/6) class-naive capture: Västernorrland leads nationally at 25%.",
        ),
        "cv_rare_disease": (
            "MI incidence 316/100k (second-highest nationally); heart care quality 65.5/100 (mid-pack).",
            "Vyndaqel 25M kr — moderate ATTR concentration; ATTR-PN cluster geography (Norra sjukvårdsregion).",
            "Hympavzi opportunity via Norrlands universitetssjukhus Umeå (Norra reference).",
            "FSME-IMMUN 79.4% TBE share — Pfizer strongly positioned; Sundsvall brick = CDK4/6 Defense target.",
        ),
        "competitor_threats": [
            ("Kisqali (Novartis)",
             "+21% CDK4/6 18-month growth at 558 units — class-leader by margin."),
            ("Verzenios (Eli Lilly)",
             "+18% CDK4/6 18-month growth at 417 units — second-place."),
            ("Amvuttra (Alnylam)",
             "ATTR-PN siRNA — direct threat to Vyndaqel via Norra sjukvårdsregion's PN founder cluster."),
        ],
        "archetype": "Norra · CDK4/6 class-naive leader (25%) · Sundsvall brick Defense",
        "strategic_summary": [
            "Pfizer total 3-yr 132M kr (rank 14); Abrysvo, Vyndaqel, Prevenar 20 = top-3 priority.",
            "P2 (CDK4/6) class-naive capture 25% — HIGHEST nationally (vs national 7%).",
            "Sundsvall brick = CDK4/6 Defense target (Pfizer above-mean share + Kisqali growing >10%).",
            "MI incidence 316/100k — second-highest nationally; cardiovascular pipeline opportunity.",
            "Sara Nylund (RS ordf, S) verified HIGH 2026-04-24; Roger Westerlund (HSD) verified HIGH 2026-04-24.",
            "Åsa Bellander (RD) verified HIGH 2026-04-24; Norra routing via Pia Näsvall + Anders Bergström.",
        ],
        "grp_pharma_note": (
            "Västernorrland has GRP per capita 567 kSEK (above mean) and pharma cost per "
            "capita 3,632 SEK (slightly above mean). Vaccine sell-in per capita 67 SEK "
            "is modest. The 25% class-naive CDK4/6 capture rate is the single most "
            "interesting Pfizer-favourable finding nationally — the Pfizer practice "
            "pattern here is what other regions should learn from."
        ),
    },
    "Region Jämtland Härjedalen": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 68M kr (rank 19) — small region in Norra sjukvårdsregion.",
            "65+ growth only +7.9% to 2040 — vaccine demographic tailwind weak.",
            "Tukysa top product priority — breast cancer 236/100k (third-highest nationally).",
            "Vyndaqel 29M kr — substantial ATTR concentration despite small population.",
        ),
        "cv_rare_disease": (
            "MI incidence 257/100k (above national); heart care quality 83.6/100 (above mean).",
            "Vyndaqel 29M kr — substantial relative concentration; Norra ATTR-PN cluster geography.",
            "Hympavzi opportunity via Norrlands universitetssjukhus Umeå (Norra reference).",
            "Lung cancer mortality 35/100k — lowest in Norra sjukvårdsregion.",
        ),
        "competitor_threats": [
            ("Verzenios (Eli Lilly)",
             "+109% CDK4/6 18-month growth at 297 units — class-leader by margin."),
            ("Kisqali (Novartis)",
             "+8% CDK4/6 18-month growth at 156 units — modest growth."),
            ("Amvuttra (Alnylam)",
             "ATTR-PN siRNA — Norra cluster threat to Vyndaqel."),
        ],
        "archetype": "Norra small · Tukysa top product · ATTR concentration outsize for population",
        "strategic_summary": [
            "Pfizer total 3-yr 68M kr (rank 19); Tukysa, Prevenar 20, Lorviqua = top-3 priority.",
            "Breast cancer 236/100k — third-highest nationally; Tukysa demand pressure.",
            "Vyndaqel 29M kr — outsize for 133k population; Norra ATTR-PN cluster.",
            "Heart care quality 83.6/100 — above mean despite small scale.",
            "Bengt Bergqvist (RS ordf, S) verified HIGH; Kristina Seling (LK ordf) verified HIGH.",
            "Katarina Nyberg-Finn (HSN ordf) — JÄMTLAND H. ONLY (not Jönköping; common confusion).",
        ],
        "grp_pharma_note": (
            "Jämtland Härjedalen has GRP per capita 471 kSEK (mid-pack) and pharma cost "
            "per capita 3,493 SEK (mid-pack). Vaccine sell-in per capita 46 SEK is the "
            "lowest in Sweden — opportunity for Abrysvo + Prevenar 20 demographic uplift "
            "even at modest population scale."
        ),
    },
    "Region Norrbotten": {
        "pipeline_areas": (
            "Pfizer 3-yr footprint 304M kr (rank 4) — Vyndaqel-dominant via V30M founder cluster.",
            "65+ growth only +2.8% to 2040 — vaccine demographic tailwind weakest in Sweden.",
            "Vyndaqel 256M kr (84% of Pfizer footprint) — ATTR-PN founder cluster paired with Västerbotten.",
            "MI incidence 383/100k — HIGHEST nationally; heart care quality 31.2/100 (low — clinical capacity gap).",
        ),
        "cv_rare_disease": (
            "MI incidence 383/100k (HIGHEST nationally); heart care quality 31.2/100 (low end).",
            "Vyndaqel 256M kr — ATTR-PN founder cluster (V30M, Skellefteå area; spans Norrbotten + Västerbotten border).",
            "Norrlands universitetssjukhus Umeå is the Nordic ATTR-PN reference centre — Norrbotten patients route there.",
            "Hympavzi launch site — Norra sjukvårdsregion via Umeå reference.",
        ),
        "competitor_threats": [
            ("Amvuttra (Alnylam)",
             "siRNA TTR silencer for ATTR-PN — direct threat to Vyndaqel in V30M founder population."),
            ("Beyonttra (BridgeBio)",
             "Acoramidis TTR stabiliser — ATTR-CM only; flank threat."),
            ("Verzenios (Eli Lilly)",
             "+184% CDK4/6 18-month growth — class-leader by volume; Ibrance only 7.7% units share."),
        ],
        "archetype": "Norra · ATTR-PN co-cluster (with Västerbotten) · MI highest nationally",
        "strategic_summary": [
            "Pfizer total 3-yr 304M kr (rank 4); Vyndaqel, Prevenar 20, Abrysvo = top-3 priority.",
            "Vyndaqel 256M kr — 84% of Pfizer footprint; ATTR-PN V30M founder cluster.",
            "MI incidence 383/100k — HIGHEST nationally; cardiovascular pipeline opportunity.",
            "Brick #3 nationally for CDK4/6 Recovery (0.53M kr at 3.2% Ibrance share — Luleå/Boden).",
            "Anders Öberg (RS ordf, S) verified HIGH; Linda Grahn (LK ordf) verified HIGH.",
            "Anna Alm Andersson (RD, post-Thörnqvist tf.); Maria Joelsson (tf. HSD post-Näsvall transfer to Västerbotten).",
        ],
        "grp_pharma_note": (
            "Norrbotten has GRP per capita 615 kSEK (above mean) and pharma cost per "
            "capita 4,095 SEK (above mean) — both elevated. Vaccine sell-in per capita "
            "38 SEK is the lowest in Sweden. The 84% Vyndaqel concentration is the most "
            "extreme single-product dependence in any Swedish region — V30M founder "
            "cluster makes Norrbotten + Västerbotten a once-in-a-portfolio rare-disease "
            "asset, but also a highly concentrated AMVUTTRA risk surface."
        ),
    },
}


def get_narratives(region_full_name):
    return NARRATIVES.get(region_full_name, {})


# ---------------------------------------------------------------------------
# Region-rank computation: where does this region sit on each KPI vs the 21?
# ---------------------------------------------------------------------------
# (column, direction) — direction "high" = higher value is "more"; "low" = lower
# value is "more" (e.g., wait times — fewer days is better). We rank such that
# rank=1 means "this region has the largest value" for "high"-direction metrics.
RANKABLE = {
    "Population":                                  "high",
    "Pop 65+":                                     "high",
    "GRP per capita (kSEK)":                       "high",
    "Healthcare cost per capita (SEK)":            "high",
    "Pharma total cost per capita (SEK)":          "high",
    "Specialist physicians (#)":                   "high",
    "Vaccine sell-in per capita (SEK/year)":       "high",
    "Foreign-born % (2024)":                       "high",
    "Post-secondary education 25–64 % (2024)":     "high",
    "Premature mortality 25–64 /100k (age-std)":   "high",
    "Healthcare-amenable mortality /100k (3-yr MA)":"high",
    "Daily smokers %":                             "high",
    "Overweight/obese %":                          "high",
    "Breast ca rate /100k":                        "high",
    "Prostate ca rate /100k":                      "high",
    "Lung ca incidence /100k":                     "high",
    "MI incidence /100k":                          "high",
    "Heart care quality (0-100)":                  "high",
}


def get_region_ranks(region_full_name):
    """For each KPI in RANKABLE, return rank of this region among the 21.
    rank 1 = highest value (or 'most' on this dimension)."""
    rm = _load_sheet("Region master")
    pp = _load_sheet("Population projections")
    pf = _load_sheet("Pfizer total footprint")
    pf = pf.dropna(subset=["Region"])
    pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
    le = _load_sheet("Life expectancy")

    rm_target = rm[rm["Region"] == region_full_name].iloc[0]
    pp_target = pp[pp["Region"] == region_full_name].iloc[0]
    pf_target = pf[pf["Region"] == region_full_name].iloc[0]
    le_target = le[le["Region"] == region_full_name].iloc[0]

    ranks = {}
    for col, direction in RANKABLE.items():
        if col not in rm.columns:
            continue
        s = rm[col].dropna()
        ascending = (direction == "low")
        ranked = s.rank(ascending=ascending, method="min")
        target_val = rm_target[col]
        if pd.isna(target_val):
            ranks[col] = None
        else:
            ranks[col] = int(ranked[rm_target.name]) if rm_target.name in ranked.index else None

    # Population projections — 65+ growth %
    s = pp["65+ growth % 2024→2040"].dropna()
    ranked = s.rank(ascending=False, method="min")
    ranks["65+ growth % 2024→2040"] = int(ranked[pp_target.name]) if pp_target.name in ranked.index else None

    # Life expectancy — higher is better, rank 1 = highest
    s = le["Average"].dropna()
    ranked = s.rank(ascending=False, method="min")
    ranks["Life exp avg"] = int(ranked[le_target.name]) if le_target.name in ranked.index else None

    # Pfizer total footprint — rank 1 = largest
    s = pf["Total Pfizer SEK"].dropna()
    ranked = s.rank(ascending=False, method="min")
    ranks["Total Pfizer SEK"] = int(ranked[pf_target.name]) if pf_target.name in ranked.index else None

    # 65+ share (computed)
    rm["pop_65_share"] = rm["Pop 65+"] / rm["Population"] * 100
    s = rm["pop_65_share"].dropna()
    ranked = s.rank(ascending=False, method="min")
    ranks["pop_65_share"] = int(ranked[rm_target.name]) if rm_target.name in ranked.index else None

    # Equity composite (rank 1 = highest need; comes already sorted)
    eq = _load_sheet("Equity composite")
    eq_target = eq[eq["Region"] == region_full_name]
    if len(eq_target):
        ranks["Equity rank"] = int(eq_target.iloc[0]["SES composite rank (1=highest need)"])

    return ranks


def compute_fingerprint(region_full_name):
    """Return a list of (label, percentile, value_str) tuples for the
    'fingerprint strip' at the top of R-A. Percentile is 0-100 where 100 =
    'most' on the dimension."""
    rm = _load_sheet("Region master")
    pp = _load_sheet("Population projections")
    pf = _load_sheet("Pfizer total footprint")
    pf = pf.dropna(subset=["Region"])
    pf = pf[~pf["Region"].astype(str).str.contains("TOTAL|Sweden", case=False, na=False)]
    eq = _load_sheet("Equity composite")

    rm_target = rm[rm["Region"] == region_full_name].iloc[0]
    pp_target = pp[pp["Region"] == region_full_name].iloc[0]
    pf_target = pf[pf["Region"] == region_full_name].iloc[0]
    eq_target = eq[eq["Region"] == region_full_name].iloc[0]

    def percentile(s, val, ascending=False):
        if pd.isna(val):
            return None, "—"
        rank = s.rank(ascending=ascending, pct=True, method="min")
        target_idx = s[s == val].index[0]
        return rank.loc[target_idx] * 100, f"{val:.0f}"

    out = []

    # Population (scale)
    pct, _ = percentile(rm["Population"], rm_target["Population"], ascending=True)
    rank_pop = int((rm["Population"].rank(ascending=False, method="min")[rm_target.name]))
    out.append(("Population scale", pct, f"#{rank_pop} of 21"))

    # Aging pressure (65+ growth to 2040)
    growth = pp_target["65+ growth % 2024→2040"]
    pct, _ = percentile(pp["65+ growth % 2024→2040"], growth, ascending=True)
    rank_age = int(pp["65+ growth % 2024→2040"].rank(ascending=False, method="min")[pp_target.name])
    out.append(("Aging pressure (+65 by 2040)", pct, f"+{growth:.0f}%  ·  #{rank_age}"))

    # Equity need (1=highest need is 100%ile)
    eq_rank = int(eq_target["SES composite rank (1=highest need)"])
    pct = (22 - eq_rank) / 21 * 100  # invert: rank 1 = 100%ile-needy
    # We display "low need" interpretation: high pct = low need = best equity
    eq_pct_display = (eq_rank - 1) / 20 * 100   # 1=0%ile, 21=100%ile
    out.append(("Equity (low need)", eq_pct_display, f"#{eq_rank}"))

    # Disease burden composite (mean of cancer + MI ranks)
    burden_cols = ["Breast ca rate /100k", "Prostate ca rate /100k",
                    "Lung ca incidence /100k", "MI incidence /100k"]
    burden_pct = []
    for c in burden_cols:
        rk = rm[c].rank(ascending=True, pct=True, method="min")
        if rm_target.name in rk.index:
            burden_pct.append(rk.loc[rm_target.name] * 100)
    if burden_pct:
        avg_burden = sum(burden_pct) / len(burden_pct)
        burden_rank = int(rm[burden_cols].mean(axis=1).rank(ascending=False, method="min")[rm_target.name])
        out.append(("Disease burden (per-capita)", avg_burden, f"#{burden_rank}"))

    # Pfizer footprint
    pct, _ = percentile(pf["Total Pfizer SEK"], pf_target["Total Pfizer SEK"], ascending=True)
    rank_pf = int(pf["Total Pfizer SEK"].rank(ascending=False, method="min")[pf_target.name])
    out.append(("Pfizer footprint (3-yr SEK)", pct, f"#{rank_pf}"))

    return out


# Quick test
if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    for r in ["Region Stockholm", "Region Västerbotten"]:
        print(f"\n{'='*60}\n{r}\n{'='*60}")
        d = get_region(r)
        for k, v in d.items():
            if isinstance(v, float):
                print(f"  {k}: {v:,.2f}" if v == v else f"  {k}: NaN")
            else:
                print(f"  {k}: {v}")
