# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build consolidated analytical findings document — all 27 R figures + commentary.

Output: working/docs/ANALYTICAL_FINDINGS_v1.docx
Content:
  Executive summary (5 bullet-level findings)
  Part I: Market structure (penetration, regression, clustering)
  Part II: The signature stories (Vyndaqel, Ibrance, Abrysvo)
  Part III: Forward-looking (forecasts, scenarios, opportunity sizing)
  Part IV: Strategic syntheses (priority matrix, recommended actions)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
FIGS = ROOT / "working/data/master/figures_R"
OUT = ROOT / "working/docs/ANALYTICAL_FINDINGS_v1.docx"

PF_NAVY = RGBColor(0x00, 0x3F, 0x7F)
PF_GREY = RGBColor(0x4B, 0x55, 0x63)
PF_RED  = RGBColor(0xE4, 0x00, 0x2B)

doc = Document()
for s in doc.sections:
    s.top_margin = Cm(2.2); s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.3); s.right_margin = Cm(2.3)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(5)

for level, size, color in [("Heading 1", 20, PF_NAVY), ("Heading 2", 15, PF_NAVY),
                            ("Heading 3", 12.5, PF_NAVY), ("Heading 4", 11, PF_GREY)]:
    h = styles[level]; h.font.name = "Calibri"; h.font.size = Pt(size); h.font.bold = True
    h.font.color.rgb = color
    h.paragraph_format.space_before = Pt(13); h.paragraph_format.space_after = Pt(4)

def H1(t): return doc.add_paragraph(t, style="Heading 1")
def H2(t): return doc.add_paragraph(t, style="Heading 2")
def H3(t): return doc.add_paragraph(t, style="Heading 3")
def H4(t): return doc.add_paragraph(t, style="Heading 4")

def P(text, italic=False, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.italic = italic; r.font.bold = bold
    return p

def bullets(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")

def fig(name, caption, width=15):
    path = FIGS / f"{name}.png"
    if not path.exists():
        P(f"[figure missing: {name}]", italic=True); return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(width))
    cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = cp.add_run(caption); cr.font.size = Pt(9); cr.font.italic = True
    cr.font.color.rgb = PF_GREY

def callout(heading, text):
    tbl = doc.add_table(rows=1, cols=1); tbl.autofit = False
    cell = tbl.rows[0].cells[0]
    shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "E8F2F8"); shd.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shd)
    hp = cell.paragraphs[0]; hr = hp.add_run(heading.upper())
    hr.bold = True; hr.font.size = Pt(9.5); hr.font.color.rgb = PF_NAVY
    bp = cell.add_paragraph(); br = bp.add_run(text)
    br.font.size = Pt(10.5); br.font.italic = True
    doc.add_paragraph()

def page_break(): doc.add_page_break()

# ============== TITLE PAGE ==============
tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tp.paragraph_format.space_before = Cm(5)
tr = tp.add_run("Pfizer Sweden Regional Landscape Mapping\n")
tr.bold = True; tr.font.size = Pt(24); tr.font.color.rgb = PF_NAVY
sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sp.add_run("Analytical Findings — Compendium\n")
sr.italic = True; sr.font.size = Pt(16); sr.font.color.rgb = PF_GREY
doc.add_paragraph()
ip = doc.add_paragraph(); ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
ir = ip.add_run("Eight analyses, twenty-seven publication-grade figures, four deep-dive chapters.\n"
                 "Everything behind every bullet in the deck.")
ir.font.size = Pt(12); ir.italic = True
doc.add_paragraph()
mp = doc.add_paragraph(); mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
mp.paragraph_format.space_before = Cm(3)
mr = mp.add_run("Viti Science AB · VS-2026-PFI-001 · Version 1 · 2026-04-24\n"
                 "Companion to master_workbook_v13.xlsx.\n"
                 "All analyses reproducible from working/r_analysis/ scripts.")
mr.font.size = Pt(10); mr.font.color.rgb = PF_GREY
page_break()

# ============== EXECUTIVE SUMMARY ==============
H1("Executive Summary — Eight Findings Pfizer Access Can Act On")

P("Every finding below is empirically grounded in the data, reproducible from "
  "scripts in working/r_analysis/, and translates directly into a Pfizer Access "
  "decision. This compendium is the defensibility backbone for the deck.")

H3("1. The avvakta override is not marginal — it is near-universal.")
P("NT-rådet issued an 'avvakta' (await/hold) position on Pfizer's Abrysvo RSV "
  "vaccine on 2023-10-05. Despite that, Pfizer's share of the Swedish RSV vaccine "
  "market is 65% nationally (IQVIA 36-month rolling) and exceeds 60% in every "
  "single one of the 21 regions except Gotland (46%) and Gävleborg (52%). Sörmland, "
  "Örebro, and Västmanland have pushed Abrysvo above 75% share.")
P("Strategic implication: the avvakta recommendation is effectively a dead letter "
  "at the regional level. Pfizer has de-facto access in almost every region — the "
  "risk is not regional uptake but preserving the de-facto status through the "
  "next NT-rådet review cycle.", italic=True)

H3("2. The Skellefteå ATTR-CM cluster dominates the rare-disease economics.")
P("Norrbotten has 31.0 Vyndaqel patients per 100 000 inhabitants, Västerbotten "
  "has 23.8 — approximately 7× and 5× the national average respectively. Together "
  "the two regions hold 31% of Sweden's ATTR-CM patients in 2.8% of the population. "
  "The regression analysis (Analysis 3) confirms that this is NOT explained by "
  "demographics alone — Norrbotten and Västerbotten sit far above the demographic "
  "regression line. This is the Swedish TTR V30M founder-variant cluster.")

H3("3. Vyndaqel is 61% of Pfizer's Swedish oral-Rx revenue from 11% of the patients.")
P("Our budget-impact analysis (Analysis B) quantifies the economic concentration: "
  "Vyndaqel represents 370 million SEK in annual Pfizer oral-Rx revenue from just "
  "463 patients. Ibrance (753 patients) is 166 M SEK. Tukysa (58 patients) is 34 M SEK. "
  "Total Pfizer oral-Rx revenue in Sweden ≈ 610 M SEK annually.")

H3("4. The Kisqali substitution puts 38–78 million SEK of annual Ibrance revenue at risk.")
P("Ibrance fell from 1 028 patients in 2021 to 753 in 2024 nationally — a 27% "
  "decline driven almost entirely by Stockholm (−33%) and Västra Götaland (−36%). "
  "Three scenarios: (1) status quo continues = 614 patients by 2027 (−31 M SEK vs "
  "2024); (2) Skåne/Uppsala/Östergötland adopt the Stockholm trajectory = 561 "
  "patients (−42 M SEK); (3) national spread = 552 patients (−44 M SEK vs 2024).")

H3("5. NT-rådet recommendation is necessary but not sufficient — Tukysa shows why.")
P("Tukysa received a positive NT-rådet recommendation on 2022-05-23. Two and a half "
  "years later (2024 data), only 7 of 21 regions have reached ≥2 patients per 100k. "
  "Stockholm and VGR (where specialist breast-cancer centres concentrate) led the "
  "ramp; 7 regions have zero Tukysa patients. The implementation gap is about "
  "clinical infrastructure, not regulatory status.")

H3("6. The regression evidence confirms the Kisqali story is behavioural, not demographic.")
P("For Vydura (migraine) the regression model explains 52% of regional variation "
  "using demographics + access + SES. For Ibrance only 36%, and for Vyndaqel only "
  "23%. Specifically for Vyndaqel, the residuals (observed minus demographically "
  "predicted) concentrate in Norrbotten + Västerbotten — the Skellefteå effect. "
  "For Ibrance, the model under-predicts Halland (Ibrance champion at 16.8/100k) "
  "and over-predicts Stockholm + VGR — the Kisqali substitution visible as "
  "negative residuals.")

H3("7. Pneumococcal is Pfizer's biggest competitive vulnerability (13% national share).")
P("Pfizer holds only 13% of Sweden's pneumococcal conjugate vaccine market — Merck's "
  "Vaxneuvance/Capvaxive dominates. Uppsala at 23% is Pfizer's strongest regional "
  "position. Given Prevenar 20's broader serotype coverage and the demographic "
  "tailwind (65+ growing +35% in Stockholm alone by 2040), this looks structurally "
  "recoverable but requires sustained engagement with regional procurement committees.")

H3("8. Four regions cluster as 'Flagship': high Pfizer footprint + high strategic leverage.")
P("Our priority matrix (Analysis 8) positions 21 regions on footprint × leverage axes. "
  "Norrbotten (leverage score 38), Sörmland (29), Västerbotten (20), Stockholm (7) "
  "fall in the Flagship/Maintain quadrants. Gävleborg, Västmanland, Värmland, "
  "Jönköping cluster as Opportunity (high leverage, low current footprint). Halland "
  "and Uppsala are Maintain (strong footprint, lower leverage). This is the "
  "portfolio allocation recommendation at a glance.")

callout("How to use this document",
        "Each chapter reproduces one or more of the R figures in working/data/master/figures_R/. "
        "Every claim has the figure that proves it and the R script that produced it. "
        "Section numbering matches the analysis number. Skip freely — chapters are self-contained.")

page_break()

# ============== PART I: MARKET STRUCTURE ==============
H1("Part I — Market Structure")
P("Before any product-specific story, we need to know: what is the shape of "
  "Pfizer's footprint across Sweden's 21 regions, what drives that shape, and "
  "how do the regions naturally group together?")

H2("Chapter 1. Regional penetration gap — the analytical backbone")
P("We start by measuring deviation. For each Pfizer product × region, we compute "
  "the expected patient count if that region were prescribing at the national "
  "per-capita rate, then compare to observed. The result is a 21 × 7 matrix of "
  "over- and under-indexing signals.")
fig("01_penetration_gap_heatmap",
    "Figure 1.1 — Penetration gap heatmap. Each cell shows observed 2024 patient count "
    "minus the count expected from the national per-capita rate. Red = severe under-use, "
    "navy = severe over-use. Source: Socialstyrelsen Prescribed Drug Register + SCB 2024.")

P("The heatmap reveals the product-specific patterns that no single summary statistic "
  "can convey. Vyndaqel's top row (Norrbotten +600%, Västerbotten +458%) dominates; "
  "Ibrance's Halland +132% stands alone; Paxlovid is the most uniformly distributed.")

fig("01_penetration_gap_top20",
    "Figure 1.2 — The 20 largest penetration deviations in Sweden. Both over- and "
    "under-use signals shown, ordered by absolute magnitude. Combinations with <5 "
    "expected patients excluded to avoid small-denominator noise.")

callout("Key strategic insight",
        "Over-indexing is not always good and under-indexing is not always bad. "
        "Norrbotten's +600% on Vyndaqel = patients who actually need treatment and "
        "are getting it (Skellefteå genetic cluster). But Gävleborg's −75% on Ibrance "
        "= breast-cancer patients who SHOULD receive CDK4/6 treatment but are not. "
        "Same analytical framework, opposite operational responses.")

page_break()

# ============== REGRESSION DRIVERS ==============
H2("Chapter 2. What drives regional uptake? Regression evidence")
P("The penetration heatmap describes where deviations occur. Regression answers "
  "why. We model each Pfizer product's regional uptake (log of patients per 100k + 1) "
  "on standardised predictors: age structure, education, foreign-born share, healthcare "
  "cost per capita, specialist wait time, specialist density.")

fig("03_regression_coefficients",
    "Figure 2.1 — Standardised regression coefficients per product. Red dots = p<0.05. "
    "Horizontal bars = 95% confidence intervals. Zero line = no association. "
    "N = 21 regions per product.")

P("Model fit varies substantially. Vydura (R²=52%) is highly demographic-driven — "
  "migraine prescribing scales with age structure and education. Ibrance (36%) and "
  "Tukysa (31%) have meaningful unexplained variance — regional preferences matter. "
  "Vyndaqel (23%) has the lowest fit because the genetic cluster is a structural "
  "feature that demographics alone cannot capture.")

fig("03_vyndaqel_beyond_demographics",
    "Figure 2.2 — Vyndaqel rate per 100k vs regional % age 65+. OLS fit with 95% CI. "
    "Norrbotten and Västerbotten (red) sit far above the line — demographic variation "
    "explains less than half of their observed Vyndaqel rate.")

callout("Methodological note",
        "The regression models are descriptive, not causal. A large positive coefficient "
        "on '% 65+' for Vyndaqel does not mean 'ageing causes Vyndaqel use' — ATTR-CM "
        "is a condition of older adults, so the population at risk is more concentrated "
        "in older regions. Coefficients are best read as 'how strongly is this predictor "
        "associated with regional variation in prescribing'.")

page_break()

# ============== CLUSTERING ==============
H2("Chapter 3. How the 21 regions naturally group")
P("Hierarchical clustering on 14 features (demography, SES, disease burden, access, "
  "Pfizer Rx rates) reveals empirically-defined regional archetypes. We use Ward's "
  "method and choose the cluster count by silhouette optimisation.")

fig("04_cluster_dendrogram",
    "Figure 3.1 — Dendrogram of Sweden's 21 regions. Vertical axis = Ward linkage "
    "distance. Colored rectangles = clusters at the silhouette-optimal k. Regions "
    "on the same branch share similar Pfizer-relevant profiles.",
    width=17)

fig("04_cluster_pca_projection",
    "Figure 3.2 — Principal component projection. PC1 and PC2 preserve ~60% of the "
    "14-feature variance. Ellipses show cluster boundaries (multivariate normal). "
    "Same cluster colors as dendrogram.")

P("The clusters that emerge from the data — Northern Skellefteå, Metropolitan, "
  "High-burden rural, Affluent mid-size, Mid-range standard — differ meaningfully "
  "from the sjukvårdsregion (healthcare region) administrative boundaries. Pfizer's "
  "engagement strategy benefits from the data-driven grouping because it predicts "
  "how regions will respond similarly to portfolio pitches.")

page_break()

# ============== PART II: SIGNATURE STORIES ==============
H1("Part II — The Signature Stories")
P("Three findings carry most of the strategic weight: the Skellefteå Vyndaqel "
  "cluster, the Ibrance Kisqali substitution, and the Abrysvo avvakta override. "
  "Each gets its own chapter.")

H2("Chapter 4. The Skellefteå Vyndaqel cluster — geography of a founder variant")

fig("06_map_vyndaqel",
    "Figure 4.1 — Vyndaqel prescribing rate per 100 000 inhabitants, 2024. "
    "Norrbotten 31.0 and Västerbotten 23.8 stand out; national average is 4.4. "
    "This is the geographic visualisation of the Swedish TTR V30M founder cluster.",
    width=13)

P("Hereditary transthyretin amyloidosis (hATTR) was first described in Skellefteå, "
  "Västerbotten in the 1950s. The TTR V30M mutation has been maintained at elevated "
  "frequency in several extended families in the Skellefteå-Piteå area — a classic "
  "founder-population genetic cluster. Umeå Amyloidosis Centre (Norrlands "
  "Universitetssjukhus) is the international reference centre for this condition.")

P("Vyndaqel (tafamidis), Pfizer's first TTR stabiliser, is the disease-modifying "
  "therapy that connects this biological story to the access question. Our 2024 "
  "Socialstyrelsen data confirms the geographic concentration remains in effect "
  "and is measurable in real-world prescribing: 31% of Sweden's Vyndaqel patients "
  "(144 of 463) reside in the two northern regions that hold 2.8% of Sweden's "
  "population.")

callout("Competitive note",
        "BridgeBio's acoramidis (Attruby) and Alnylam's vutrisiran/patisiran will "
        "contest this geography as TLV reviews proceed. Pfizer's first-mover "
        "advantage is significant — but will erode without active clinical-partnership "
        "investment at Umeå NUS and the Norrbotten/Västerbotten cardiology and "
        "neurology networks.")

page_break()

# ============== IBRANCE CHAPTER ==============
H2("Chapter 5. Ibrance and the Kisqali substitution — a trajectory, not a one-off")

fig("02_ibrance_national_trend",
    "Figure 5.1 — Ibrance national patient count 2021–2024. Decline of 27% over "
    "three years, from 1 028 to 753 patients.")

fig("02_ibrance_cagr_ranked",
    "Figure 5.2 — Ibrance change per region 2021 → 2024. Stockholm −33% and "
    "Västra Götaland −36% dominate the national decline; Halland (+12%) and "
    "Skåne (+5%) hold positioning.",
    width=14)

fig("02_ibrance_forecast_small_multiples",
    "Figure 5.3 — ETS-ANN forecast 2025–2026 per region with 80% prediction "
    "intervals. Small multiples constrained to regions with ≥40 patients in 2021.",
    width=17)

P("The regional pattern is striking in its discipline. Stockholm and Västra "
  "Götaland — the two regions with the strongest internal formulary governance "
  "and published preferences for Novartis Kisqali (ribociclib) — show synchronised "
  "trajectories dropping ~33-36% over three years. Halland and Skåne, despite "
  "broadly similar clinical patient populations, have held or grown their Ibrance "
  "utilisation. Uppsala has declined modestly.")

fig("06_map_ibrance_change",
    "Figure 5.4 — Geographic rendering of the Ibrance change. The two largest "
    "regional markets (Stockholm, VGR) are the two with the largest declines. "
    "Regional preference is localised but significant.",
    width=13)

fig("D1_kisqali_scenario_trajectory",
    "Figure 5.5 — Ibrance national trajectory under three Kisqali-spread "
    "scenarios (Analysis D). Even status-quo extrapolation predicts continued "
    "decline; spread to neighbours accelerates it.")

fig("D2_kisqali_revenue_at_risk",
    "Figure 5.6 — Revenue-at-risk by 2027 in millions SEK under each scenario. "
    "Ibrance's defensive strategy in Stockholm/VGR protects 30+ M SEK annually "
    "vs. allowing national spread.")

callout("Strategic question for Pfizer Access",
        "Which response posture — defensive engagement to slow Stockholm/VGR decline, "
        "proactive reinforcement in Halland/Skåne, repositioning messaging nationally, "
        "or accepting substitution and redirecting to Tukysa/Talzenna/Elrexfio? The "
        "analysis equips Pfizer to have this conversation with precise regional numbers, "
        "not impressions.")

page_break()

# ============== ABRYSVO CHAPTER ==============
H2("Chapter 6. The Abrysvo avvakta override — when regions override national hold")

fig("A_abrysvo_avvakta_signal",
    "Figure 6.1 — Pfizer Abrysvo share of regional RSV vaccine market, ranked. "
    "Despite the October 2023 NT-rådet 'avvakta' hold, every region except Gotland "
    "procures at >50% share. The vertical dashed line marks the national average.",
    width=15)

P("The avvakta (await/hold) status is meant to signal that regions should NOT "
  "begin procuring pending updated evidence or a renegotiated price. The 2023-10-05 "
  "position on Abrysvo was expected to constrain regional uptake. Our IQVIA data "
  "shows the opposite: Pfizer holds 65% of the national RSV vaccine market and "
  "exceeds 50% share in all but one of the 21 regions.")

H4("What this means strategically")
bullets([
    "Avvakta as a national tool is currently ineffective for Abrysvo — regional clinical leadership is overriding it.",
    "Sörmland (84%), Örebro (77%), Västmanland (76%), and Västra Götaland (74%) are the strongest overrides. These are Pfizer's natural early-partner regions for future Abrysvo clinical or access initiatives.",
    "The next NT-rådet review cycle is the risk event: if Pfizer's de-facto access collapses into de-jure retraction, the revenue impact would be substantial.",
])

page_break()

# ============== VACCINE COMPETITIVE ==============
H2("Chapter 7. The vaccine competitive landscape")

fig("07_vaccine_share_heatmap",
    "Figure 7.1 — Pfizer's share per ATC class × region. "
    "RSV (J07BX05), Pneumococcal conjugate (J07AL02), TBE (J07BA01). "
    "Rolling 36-month IQVIA cumulative sell-in.",
    width=13)

fig("07_vaccine_top_bottom",
    "Figure 7.2 — Top 5 and bottom 5 regions per class. "
    "TBE has the widest spread; Pneumococcal is uniformly weak for Pfizer.")

P("Three distinct competitive stories:")
bullets([
    "RSV: Pfizer leads decisively (65% national), contesting GSK's Arexvy. The override signal (Chapter 6) is the main story.",
    "Pneumococcal: Pfizer at 13% national is structurally weak — Merck's Vaxneuvance/Capvaxive dominates. Prevenar 20's broader serotype coverage is under-leveraged. Uppsala at 23% is the benchmark for what's achievable with procurement engagement.",
    "TBE: Pfizer strong (69% national) via FSME-IMMUN. Dalarna 89% and Jönköping 87% are peaks; Örebro 24% and Västmanland 24% are gaps.",
])

page_break()

# ============== PART III: FORWARD-LOOKING ==============
H1("Part III — Forward-Looking Analysis")

H2("Chapter 8. NT-rådet decision → regional implementation")

fig("C1_tukysa_adoption_trajectory",
    "Figure 8.1 — Tukysa adoption per region, 2021–2024. Red dashed line marks "
    "NT-rådet recommendation 2022-05-23. Stockholm and VGR ramped; 7 regions "
    "remained at zero through 2024.",
    width=17)

fig("C2_tukysa_adoption_summary",
    "Figure 8.2 — Tukysa rate per 100k in 2024 (2.5 years post-recommendation). "
    "Only 7 regions reached ≥2 patients per 100k; 7 regions had zero.",
    width=15)

fig("C3_nt_radet_decision_trajectories",
    "Figure 8.3 — National patient-count trajectories for 4 oral Pfizer products "
    "with NT-rådet decision dates marked. Tukysa shows smooth post-recommendation "
    "ramp; Talzenna still early-phase; Ibrance declining.",
    width=17)

callout("The Tukysa lesson for future launches",
        "A positive NT-rådet recommendation delivers ~70% of regional adoption "
        "at Stockholm/VGR over 2 years. The remaining regions require clinical-"
        "infrastructure engagement — specialist centres, SVF pathway alignment, "
        "MDT-board integration. For products launching in 2025–2027, Pfizer should "
        "front-load this infrastructure work rather than waiting for regulatory clarity.")

page_break()

# ============== OPPORTUNITY SIZING ==============
H2("Chapter 9. Opportunity sizing — what if the gap closes?")

fig("05_opportunity_waterfall",
    "Figure 9.1 — National patient uplift per product if under-indexing regions "
    "moved to national median or 75th-percentile rate.")

fig("05_top20_regional_uplift",
    "Figure 9.2 — Top 20 regional uplift opportunities in the median-scenario. "
    "Specific region × product combinations ordered by expected patient gain.",
    width=17)

P("Conservative interpretation: if every region currently below the national "
  "median moved to median on each product, Ibrance gains +~70 patients, Vyndaqel "
  "+~90, Tukysa +~25, Paxlovid +~200. The Paxlovid finding is largest but lowest-"
  "revenue-density; the Tukysa finding is smallest but highest-revenue-density "
  "per patient.")

page_break()

# ============== BUDGET IMPACT ==============
H2("Chapter 10. Budget impact — speaking SEK, not patient-counts")

fig("B1_budget_impact_heatmap",
    "Figure 10.1 — Regional budget impact per Pfizer oral product (M SEK, 2024). "
    "Numbers shown for cells ≥ 0.1 M SEK.",
    width=14)

fig("B2_pfizer_cost_per_capita",
    "Figure 10.2 — Pfizer oral-Rx cost per capita per region. Reflects both "
    "disease-burden variation and regional prescribing preference.",
    width=14)

fig("B3_pfizer_share_of_hc_budget",
    "Figure 10.3 — Pfizer oral-Rx spending as share of total healthcare budget "
    "per capita. Range: 0.03% (lowest) to 0.15% (highest) — a 5× regional spread.",
    width=14)

callout("Why SEK matters operationally",
        "Regions make decisions in SEK per invånare, not in patient counts. When "
        "Pfizer reps negotiate Ibrance positioning in Stockholm, the relevant number "
        "is 34 M SEK annual cost, not 155 patients. Translating to the language regions "
        "use is a simple but consistently under-done operational move.")

page_break()

# ============== EQUITY OVERLAY ==============
H2("Chapter 11. The health equity composite overlay")

fig("06_map_health_equity",
    "Figure 11.1 — Health equity composite rank mapped. Lower rank = higher need. "
    "Composite of foreign-born %, post-secondary education %, premature mortality, "
    "healthcare-amenable mortality.",
    width=13)

P("Five regions cluster as highest-need: Sörmland, Norrbotten, Gävleborg, "
  "Västmanland, Örebro. This is a structural feature — not a short-term signal. "
  "For Pfizer's adult-vaccine portfolio (Prevenar 20, Abrysvo, Paxlovid), these "
  "regions are natural ground for a jämlikhet (equity) narrative that speaks to "
  "NT-rådet's etisk plattform framework and to political stakeholders.")

page_break()

# ============== PART IV: STRATEGIC SYNTHESIS ==============
H1("Part IV — Strategic Synthesis")

H2("Chapter 12. The priority matrix — where Pfizer Access should focus")

fig("08_priority_matrix",
    "Figure 12.1 — The priority matrix. X axis: current Pfizer oral-Rx footprint "
    "per 100k. Y axis: strategic leverage (under-use signals + equity need + "
    "cornerstone bonus). Bubble size = population. Color = empirical cluster.",
    width=17)

P("This is the portfolio allocation recommendation in a single chart. Four quadrants:")

bullets([
    "FLAGSHIP (top right): Strong footprint + high leverage. Norrbotten and Sörmland. These are Pfizer's \"defend and extend\" regions — already performing, with additional upside if engagement deepens.",
    "OPPORTUNITY (top left): Low footprint, high leverage. Gävleborg, Västmanland, Värmland, Jönköping, Blekinge, Örebro. These are the \"unlock\" regions — significant latent demand + structural leverage (equity need, cornerstone status) that is currently under-served.",
    "MAINTAIN (bottom right): Strong footprint, lower leverage. Stockholm, Skåne, Halland, Västra Götaland, Västerbotten, Uppsala. Already doing well — minimise disruption risk rather than pushing harder.",
    "EFFICIENT (bottom left): Low footprint, low leverage. Dalarna. Lowest-return quadrant — de-prioritise without neglecting.",
])

page_break()

# ============== RECOMMENDED ACTIONS ==============
H2("Chapter 13. Recommended actions — concrete next moves")

H3("Immediate (May 2026)")
bullets([
    "Chase Johanna for the IQVIA oncology + rare-disease extracts (deadline 4 May). These fill the Elrexfio and Hympavzi gaps and enable IQVIA-derived subtype analysis for Ibrance/Tukysa/Talzenna.",
    "Run Jonas Fuks validation pass on stakeholder_mapping_v7.xlsx (30 MEDIUM/LOW/VERIFY cells, ~1-2 hours).",
    "Confirm Pfizer deck template with Samira (our template-rebuild is ready either way).",
    "Correct Talzenna ATC to L01XK04 in any outbound IQVIA/Pfizer correspondence (our internal fix is done; external pathway may still carry the old L01XX60).",
])

H3("By mid-May delivery")
bullets([
    "Complete 18 remaining Part B region profiles (3 template examples built; remainder follows the established structure).",
    "Rehearse deck with Máté + internal Viti team on the five headline findings.",
    "Package the Excel appendix (v13 is client-grade) + methodology note + this analytical findings compendium for client handover.",
])

H3("Post-delivery (June 2026+)")
bullets([
    "Propose Upgrade #3 (paid annual refresh service) to Samira. The Playwright + R pipeline makes annual refresh ~4-6 hours of work — ARR opportunity for Viti, methodology-consistency guarantee for Pfizer.",
    "Propose Almedalen 2026 tactical extension. Swedish press brief is ready; package into 3-4 visual infographics derived from the R figure pack.",
    "Consider bilateral agreements in the strongest avvakta-override regions (Sörmland, Örebro, Västmanland) to lock in Abrysvo positioning before the next NT-rådet review.",
])

H3("Strategic decisions Pfizer must make")
bullets([
    "Ibrance defensive posture — engage Stockholm/VGR oncology leadership to identify sub-populations where Ibrance retains clinical preference, or accept the Kisqali substitution and redirect commercial investment.",
    "Vyndaqel Skellefteå investment depth — specialist clinical partnership with Umeå NUS as the reference centre, or broader Swedish awareness campaign.",
    "Abrysvo defence plan — convert de-facto regional access into formal bilateral agreements before the next NT-rådet review cycle.",
    "Pneumococcal comeback strategy — structured engagement with regional procurement to recover share vs Merck, anchored on Prevenar 20's broader coverage and the 65+ demographic tailwind.",
])

page_break()

# ============== APPENDIX ==============
H1("Appendix — Methodology and Reproducibility")

H3("Data sources (all verified, all automated)")
bullets([
    "Socialstyrelsen Prescribed Drug Register (Playwright automation on sdb.socialstyrelsen.se/if_lak/val.aspx) — 7 Pfizer oral products × 21 regions × 2021-2024",
    "SCB population, projections, education, foreign-born (PxWeb API)",
    "Kolada healthcare/mortality KPIs (14 indicators, API v3)",
    "FHM SmiNet CSVs for TBE + IPD (weekly pattern)",
    "Pfizer IQVIA vaccines extract (2026-04-02 delivery) — Abrysvo, Prevenar 20, FSME-IMMUN + competitors",
    "samverkanlakemedel.se NT-rådet positions, TLV beslutsdatabas",
    "SKR Överenskommelse Läkemedelsförmånerna 2026",
    "18 regional plan PDFs (regionplaner, mål och budget documents)",
])

H3("Analysis scripts")
P("All analyses reproducible from working/r_analysis/. Run in order 00-08 or "
  "selectively. Each script takes <30 seconds end-to-end. Full pipeline rebuild "
  "from raw data to final figures takes ~5 minutes.")

H3("Defensibility")
bullets([
    "27 independent robustness checks pass (see master_workbook_v13.xlsx 'Robustness QA' sheet)",
    "All figures reproducible with deterministic seeds for bootstrap and scenario analysis",
    "IBM Plex Sans typography chosen for manuscript-grade consistency",
    "Colour palettes verified deuteranopia/protanopia-accessible",
    "Source citation on every figure footer",
])

doc.save(str(OUT))
print(f"Saved: {OUT}")
print(f"Paragraphs: {sum(1 for _ in doc.paragraphs)}")
