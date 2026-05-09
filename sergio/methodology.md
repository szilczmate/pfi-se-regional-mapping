# Methodology

Six analytical layers applied to the source data. Each layer is documented with its inputs, formula, thresholds, and the master JSON file it produces.

## Layer 01 — Data foundations

**Inputs**
- IQVIA Sell-In: Vaccines extract (Apr 2026), RD/IM extract (Apr 2026), Oncology extract (Apr 2026). 36 months brick-level monthly data, Sell-In SEK and units.
- AVA: Patient-level data for Vyndaqel, Ibrance, Vydura. Supersedes Socialstyrelsen open data for these specific products.
- Public registries: SCB (population, demographics, GRP), Socialstyrelsen (Läkemedelsregistret, Cancerregistret, patient register), Folkhälsomyndigheten (vaccine coverage, infectious disease), Kolada (standardised KPIs), RCC (cancer-care signals), samverkansläkemedel.se (NT-rådet, NSG, regional LK).

**Conventions**
- IQVIA is **Sell-In** (wholesale invoice to region or central buyer), pack count, not patient days.
- Per-100k normalisation everywhere comparison is across regions of differing sizes.
- SEK figures are gross (pre-rebate). Net Pfizer revenue is not visible in IQVIA.
- All data current to 2026-04-27 freeze with stakeholder verification pass May 2026.

## Layer 02 — Trajectory verdicts

**Method.** For each product, sum monthly Sell-In units across all bricks for the most recent 6 months (last-6) and the prior 6 months (prev-6). Compute percent change.

**Verdict bands**
| % change | Verdict |
|---|---|
| > +15% | Growing |
| +5% to +15% | Stable up |
| −5% to +5% | Plateau |
| −5% to −15% | Stable down |
| < −15% | Declining |

**Window sensitivity.** All verdicts also computed at 12-month and 18-month windows; the 6-month "live window" is the operational standard. Kisqali and Vyndaqel verdicts are window-robust; the Verzenios verdict is window-sensitive (Plateau at 6 months, Growing at 18 months) and is flagged as such.

## Layer 03 — Region × product quadrant

**231 cells** (21 Swedish regions × 11 Pfizer products). Each cell scored on two axes:

**Opportunity (vertical)** — SEK gap between current Pfizer position and a defensible target position in that cell.
- Recovery products: (target share − current share) × class-naive volume × forward run-rate × pack price
- Defend products: current SEK at risk if competitor entrant share grew at observed rate over 12 months
- Engage products: (addressable patient pool − current treated population) × treatment cost

**Actionability (horizontal)** — composite of three measurable inputs, each scored 1–5, normalised:
1. NT-rådet recommendation state (Recommended / Open / Restricted / Not recommended)
2. Regional LK alignment (formulary listed / bedside list / restricted / not stocked)
3. Stakeholder engagement depth (cornerstone present / mid-tier present / no named contact)

**Quadrants** are formed by median-of-axis splits:
- Top-right (Priority Focus): high opportunity AND high actionability — ~70 cells, the working list for plays
- Top-left (Engagement Build): high opportunity, low actionability — ~50 cells
- Bottom-right (Quick Win): low opportunity, high actionability — ~40 cells
- Bottom-left (Deprioritise): low on both — ~70 cells

**Output:** `data/master/quadrant_and_nt.json`

## Layer 04 — Influence scoring (cornerstones)

**Composite score** for each of ~135 stakeholder-role records (covering ~103 distinct named individuals):

```
score = formal_authority_weight + dual_role_bonus + regional_reach + cross_play_applicability
```

**Formal authority weights** (illustrative): NT-rådet ordförande +75, NT-rådet member +60, NSG ordförande +60, NSG member +50, regional LK ordförande +30, regiondirektör +20, HSD +15.

**Dual-role bonus.** A person holding two governance roles (e.g., NT-rådet member AND regional LK chair) scores higher because a single Pfizer touchpoint reaches two governance bodies.

**Regional reach.** Stockholm and VGR get a small bonus for decision-volume concentration; sjukvårdsregion-coordinating roles get a bonus for multi-region span.

**Cross-play applicability.** People who matter on three or more strategic plays score higher than people who matter on one.

**Cornerstone cut.** Composite scores normalised to 0–200. Natural break in the distribution at score ≥140 yields 8 cornerstones; 22 high-value tier (100–139); rest standard tier. Sensitivity-tested to ±10% perturbation of weights — top 8 stable.

**Output:** `data/master/stakeholder_data.json`

## Layer 05 — Brick priority

**~78 IQVIA bricks** in Sweden. Bricks roll cleanly to region; finer than region, coarser than postcode. Each brick has 36 months of monthly Sell-In per product.

**Recovery brick criteria:** brick CDK4/6 volume above the median AND Ibrance share below 12.5% (i.e., 5 percentage points below the 17.5% national mean — the meaningful gap that justifies field-team time).

**Recovery formula:**
```
recovery_sek = (17.5% national_mean − current_brick_ibrance_share) × brick_total_CDK46_SEK_last_6_months
```

Conservative target — recovery to the empirical national mean, not to a normative ambition. Alternative target (recovery to 25% in bricks below 15%) yields ≈17.25M kr Sweden-wide vs the 9.303M kr base case at the national-mean target.

**Defense brick criteria:** Ibrance share above 30% AND competitor (Verzenios or Kisqali) growth velocity above threshold AND brick volume above median.

**Output:** `data/master/brick_priority.json`. Top-15 raw recovery opportunities cover ~6M kr of the 9.303M kr Sweden-wide opportunity. 11 bricks meet formal Recovery criteria today. 3 Defense bricks (Eskilstuna, Kristianstad, Sundsvall).

## Layer 06 — Confidence framework

Every quantitative claim in the analysis is tagged with one of four confidence tiers:

| Tier | Definition | Example |
|---|---|---|
| **Observed** | Direct from a public registry or the AVA / IQVIA extracts | Vyndaqel last-6 vs prev-6 +3.4% |
| **Modelled** | Derived from observed data via a documented method | 9.303M kr Sweden-wide Recovery opportunity |
| **Hypothesis** | Directional reading consistent with data but unprovable from public sources | "Stockholm Karolinska clinical preference is the likely driver of the Abrysvo minority position" |
| **Needs Pfizer Validation** | Claim requires Pfizer-internal data to verify | "Pfizer field team has limited engagement with Mats Ek today" |

The tier is encoded in the master workbook for every cell. The deck does not display tags on every figure (would crowd the slides) but all sourcing conventions are consistent and auditable.

## Cross-validation

Where two independent data sources cover the same metric, both are computed and the directional verdict is confirmed:

| Metric | Source A (primary) | Source B (cross-check) | Status |
|---|---|---|---|
| CDK4/6 SEK share trajectory | IQVIA Oncology extract | AVA class-naive starts | Directional agreement; magnitudes differ (different denominators) |
| Vyndaqel volume trajectory | IQVIA RD/IM extract | AVA Vyndaqel patient counts | Directional agreement |
| ATTR-PN concentration in Norra | AVA Vyndaqel proxy prevalence | Published clinical literature (Suhr 1992, Hellman 2008) | Range 5×–10× depending on methodology; AVA central estimate 7.6× |
| NSG roster | samverkansläkemedel.se | Region-website press releases + Region Stockholm politiker register | All seats verified May 2026 |

## Open validation gates

Four Pfizer-side inputs that would deepen the analysis if provided:

1. **Net revenue per oral Rx product.** Today reported at gross sell-in; net Pfizer revenue requires Pfizer-internal access to confidential rebate structures.
2. **Field-team perspective on the 8 cornerstones.** Cold / aware / engaged / partner status, internal owner, last meaningful contact.
3. **TLV Abrysvo cost-effectiveness review status.** September 2025 supplementary analysis — within or outside cost-effectiveness corridor.
4. **Swedish epidemiology for three oncology subtypes.** HER2+ with brain mets (Tukysa), BRCA-mutated breast/HRR-mutated mCRPC (Talzenna), ALK+ NSCLC (Lorviqua) — per-region.
