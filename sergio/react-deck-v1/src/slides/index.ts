import type { ComponentType, ReactElement } from 'react'
import type { SlideProps } from '../types'

// The region-template components are plain function components that also accept a
// `region` prop; this callable type lets us invoke them directly in the generator.
type RegionSlideComp = (props: SlideProps & { region?: string }) => ReactElement

import { SectionDivider } from '../components/SectionDivider'

// Open
import { Slide01_Cover } from './Slide01_Cover'
import { Slide_Scope } from './Slide_Scope'
import { Slide02_Objectives } from './Slide02_Objectives'
import { Slide03_Methodology } from './Slide03_Methodology'

// National mapping
import { Slide05_FourTracks } from './Slide05_FourTracks'
import { Slide06_HealthEquityIndicators } from './Slide06_HealthEquityIndicators'
import { Slide_GovernanceRemits } from './Slide_GovernanceRemits'
import { Slide07_GovernanceBodies } from './Slide07_GovernanceBodies'
import { Slide_QuestionOwnership } from './Slide_QuestionOwnership'
import { Slide08_DMM } from './Slide08_DMM'
import { Slide09_AntiPatterns } from './Slide09_AntiPatterns'
import { Slide11_ReformCalendar } from './Slide11_ReformCalendar'
import { Slide_ReformCalendarFull } from './Slide_ReformCalendarFull'
import { Slide_NumbersInUse } from './Slide_NumbersInUse'
import { Slide_CostDriver } from './Slide_CostDriver'

// Region deep-dive — the Stockholm components are the shared template, reused for every
// region via a `region` prop. The 2026-06 rollout applies them to all 21 regions.
import { Slide12_StakeholderPriorities } from './Slide12_StakeholderPriorities'
import { Stockholm01_Overview } from './Stockholm01_Overview'
import { Stockholm_Benchmark } from './Stockholm_Benchmark'
import { Stockholm_Budget } from './Stockholm_Budget'
import { Stockholm_LakemedelBudget } from './Stockholm_LakemedelBudget'

// Close
import { Slide14_Closing } from './Slide14_Closing'

// ─────────────────────────────────────────────────────────────────────────
// PARKED for the app (removed from the deck per Samira feedback 2026-05-31).
// Files kept intentionally — these become the product/commercial layer of the
// live app. Do not delete.
//   import { Slide10_ProductTracks } from './Slide10_ProductTracks'
//   import { Stockholm03_Portfolio } from './Stockholm03_Portfolio'
//   import { Stockholm04_Vaccines } from './Stockholm04_Vaccines'
//   import { Stockholm05_PositioningQuadrant } from './Stockholm05_PositioningQuadrant'
//   import { Stockholm06_Synthesis } from './Stockholm06_Synthesis'
//   import { Stockholm02_DiseaseBurden } from './Stockholm02_DiseaseBurden'  // Samira 2026-06-16 (Bild 23): "disease burden" removed from the deck (all regions)
//   import { Slide04_FindingsPreview } from './Slide04_FindingsPreview'
//   import { Analysis_BrickRecovery } from './Analysis_BrickRecovery'
//   import { Analysis_ATTRConcentration } from './Analysis_ATTRConcentration'
//   import { Analysis_VaccineTrends } from './Analysis_VaccineTrends'
// ─────────────────────────────────────────────────────────────────────────

const shortName = (r: string) =>
  r.replace('Region ', '').replace('Västra Götalandsregionen', 'VGR')

// ── The 21 regions, grouped by sjukvårdsregion (SVR) ───────────────────────
// NT-rådet and NSG operate at SVR level (and their reps are shared within a
// group), so grouping the region deep-dives this way mirrors the governance
// spine laid out in the national section. Region strings MUST match the
// `region` field in data.json / stakeholderpriorities.json exactly.
interface RegionGroup { svr: string; regions: string[] }
const REGION_GROUPS: RegionGroup[] = [
  { svr: 'Stockholm-Gotland', regions: ['Region Stockholm', 'Region Gotland'] },
  { svr: 'Södra', regions: ['Region Skåne', 'Region Halland', 'Region Kronoberg', 'Region Blekinge'] },
  { svr: 'Västra', regions: ['Västra Götalandsregionen'] },
  { svr: 'Sydöstra', regions: ['Region Östergötland', 'Region Jönköpings län', 'Region Kalmar'] },
  { svr: 'Mellansverige', regions: ['Region Uppsala', 'Region Örebro län', 'Region Sörmland', 'Region Dalarna', 'Region Gävleborg', 'Region Värmland', 'Region Västmanland'] },
  { svr: 'Norra', regions: ['Region Västerbotten', 'Region Norrbotten', 'Region Västernorrland', 'Region Jämtland Härjedalen'] },
]

// The five-slide template applied to each region (title suffix kept in sync with the array).
const REGION_TEMPLATE: { Comp: RegionSlideComp; titleSuffix: string }[] = [
  { Comp: Slide12_StakeholderPriorities, titleSuffix: 'decision-maker priorities' },
  { Comp: Stockholm01_Overview,          titleSuffix: 'region overview' },
  { Comp: Stockholm_Benchmark,           titleSuffix: 'national benchmark' },
  { Comp: Stockholm_Budget,              titleSuffix: 'regional budget' },
  { Comp: Stockholm_LakemedelBudget,     titleSuffix: 'medicines budget' },
]

// ── Fixed front matter ─────────────────────────────────────────────────────
const OPEN: ComponentType<SlideProps>[] = [Slide01_Cover, Slide02_Objectives, Slide_Scope, Slide03_Methodology]
const OPEN_TITLES = ['Cover', 'Objectives', 'Scope of the work', 'Methodology']

const Section1Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '1', title: 'National mapping' })

const NATIONAL: ComponentType<SlideProps>[] = [
  Section1Divider,
  Slide05_FourTracks,
  Slide06_HealthEquityIndicators,
  Slide_NumbersInUse, // Samira 2026-06-16 (Bild 15): framed up front, before the governance detail
  Slide_GovernanceRemits,
  Slide07_GovernanceBodies,
  Slide_QuestionOwnership,
  Slide08_DMM,
  Slide09_AntiPatterns,
  Slide11_ReformCalendar,
  Slide_ReformCalendarFull,
  Slide_CostDriver,
]
const NATIONAL_TITLES = [
  'Section 1 · National mapping',
  'Four-track architecture',
  'Health equity indicators',
  'Indicators and decisions', // Samira 2026-06-16 (Bild 15): moved earlier
  'Governance remits (NT-rådet · NSG · LK)',
  'Governance bodies and named seats',
  'Question ownership (5 roles)',
  'Decision-maker matrix (21 regions × 5 roles)',
  'Engagement routing',
  'Reform calendar 2026–2027',
  'Full reform calendar 2025–2027',
  'Where spend growth concentrates',
]

// ── Generate the region sections: 6 SVR dividers + 21 region deep-dives ─────
const REGION_SLIDES: ComponentType<SlideProps>[] = []
const REGION_TITLES: string[] = []
REGION_GROUPS.forEach((group, i) => {
  const sectionNo = String(i + 2) // section 1 = national mapping; region groups are 2..7
  REGION_SLIDES.push((props: SlideProps) =>
    SectionDivider({ ...props, number: sectionNo, title: `Sjukvårdsregion ${group.svr}` }))
  REGION_TITLES.push(`Section ${sectionNo} · Sjukvårdsregion ${group.svr}`)
  for (const region of group.regions) {
    const short = shortName(region)
    for (const { Comp, titleSuffix } of REGION_TEMPLATE) {
      REGION_SLIDES.push((props: SlideProps) => Comp({ ...props, region }))
      REGION_TITLES.push(`${short}: ${titleSuffix}`)
    }
  }
})

const CLOSE_NO = String(REGION_GROUPS.length + 2) // section after the region groups
const CloseDivider = (props: SlideProps) =>
  SectionDivider({ ...props, number: CLOSE_NO, title: 'Where this could go next' })

export const ALL_SLIDES: ComponentType<SlideProps>[] = [
  ...OPEN,
  ...NATIONAL,
  ...REGION_SLIDES,
  CloseDivider,
  Slide14_Closing,
]

export const SLIDE_TITLES: string[] = [
  ...OPEN_TITLES,
  ...NATIONAL_TITLES,
  ...REGION_TITLES,
  `Section ${CLOSE_NO} · Where this could go next`,
  'From a deck to a live dashboard',
]
