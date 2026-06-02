import type { ComponentType } from 'react'
import type { SlideProps } from '../types'

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
import { Slide_NumbersInUse } from './Slide_NumbersInUse'
import { Slide_CostDriver } from './Slide_CostDriver'

// Region deep-dive (Stockholm as template)
import { Slide12_StakeholderPriorities } from './Slide12_StakeholderPriorities'
import { Stockholm01_Overview } from './Stockholm01_Overview'
import { Stockholm_Benchmark } from './Stockholm_Benchmark'
import { Stockholm_Budget } from './Stockholm_Budget'
import { Stockholm_LakemedelBudget } from './Stockholm_LakemedelBudget'
import { Stockholm02_DiseaseBurden } from './Stockholm02_DiseaseBurden'

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
//   import { Slide04_FindingsPreview } from './Slide04_FindingsPreview'
//   import { Analysis_BrickRecovery } from './Analysis_BrickRecovery'
//   import { Analysis_ATTRConcentration } from './Analysis_ATTRConcentration'
//   import { Analysis_VaccineTrends } from './Analysis_VaccineTrends'
// ─────────────────────────────────────────────────────────────────────────

const Section1Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '1', title: 'National mapping' })

const Section2Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '2', title: 'Region focus: Stockholm' })

const Section3Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '3', title: 'Region focus: Skåne' })

const Section4Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '4', title: 'Region focus: VGR' })

const Section5Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '5', title: 'Where this could go next' })

export const ALL_SLIDES: ComponentType<SlideProps>[] = [
  // Open (4)
  Slide01_Cover,
  Slide02_Objectives,
  Slide_Scope,
  Slide03_Methodology,

  // Section 1 — National mapping
  Section1Divider,
  Slide05_FourTracks,
  Slide06_HealthEquityIndicators,
  Slide_GovernanceRemits,
  Slide07_GovernanceBodies,
  Slide_QuestionOwnership,
  Slide08_DMM,
  Slide09_AntiPatterns,
  Slide11_ReformCalendar,
  Slide_NumbersInUse,
  Slide_CostDriver,

  // Section 2 — Region deep-dive · Stockholm (template for the 21-region rollout)
  Section2Divider,
  (props: SlideProps) => Slide12_StakeholderPriorities({ ...props, region: 'Region Stockholm' }),
  Stockholm01_Overview,
  Stockholm_Benchmark,
  Stockholm_Budget,
  Stockholm_LakemedelBudget,
  Stockholm02_DiseaseBurden,

  // Section 3 — Region focus · Skåne
  Section3Divider,
  (props: SlideProps) => Slide12_StakeholderPriorities({ ...props, region: 'Region Skåne' }),
  (props: SlideProps) => Stockholm01_Overview({ ...props, region: 'Region Skåne' }),
  (props: SlideProps) => Stockholm_Benchmark({ ...props, region: 'Region Skåne' }),
  (props: SlideProps) => Stockholm_Budget({ ...props, region: 'Region Skåne' }),
  (props: SlideProps) => Stockholm_LakemedelBudget({ ...props, region: 'Region Skåne' }),
  (props: SlideProps) => Stockholm02_DiseaseBurden({ ...props, region: 'Region Skåne' }),

  // Section 4 — Region focus · VGR
  Section4Divider,
  (props: SlideProps) => Slide12_StakeholderPriorities({ ...props, region: 'Västra Götalandsregionen' }),
  (props: SlideProps) => Stockholm01_Overview({ ...props, region: 'Västra Götalandsregionen' }),
  (props: SlideProps) => Stockholm_Benchmark({ ...props, region: 'Västra Götalandsregionen' }),
  (props: SlideProps) => Stockholm_Budget({ ...props, region: 'Västra Götalandsregionen' }),
  (props: SlideProps) => Stockholm_LakemedelBudget({ ...props, region: 'Västra Götalandsregionen' }),
  (props: SlideProps) => Stockholm02_DiseaseBurden({ ...props, region: 'Västra Götalandsregionen' }),

  // Section 5 — Close
  Section5Divider,
  Slide14_Closing,
]

export const SLIDE_TITLES: string[] = [
  'Cover',
  'Objectives',
  'Scope of the work',
  'Methodology',
  'Section 1 · National mapping',
  'Four-track architecture',
  'Health equity indicators',
  'Governance remits (NT-rådet · NSG · LK)',
  'Governance bodies and named seats',
  'Question ownership (5 roles)',
  'Decision-maker matrix (21 regions × 5 roles)',
  'Engagement routing',
  'Reform calendar 2026–2027',
  'Indicators and decisions',
  'Where spend growth concentrates',
  'Section 2 · Region focus: Stockholm',
  'Stockholm: decision-maker priorities',
  'Stockholm: region overview',
  'Stockholm: national benchmark',
  'Stockholm: regional budget',
  'Stockholm: medicines budget',
  'Stockholm: disease burden',
  'Section 3 · Region focus: Skåne',
  'Skåne: decision-maker priorities',
  'Skåne: region overview',
  'Skåne: national benchmark',
  'Skåne: regional budget',
  'Skåne: medicines budget',
  'Skåne: disease burden',
  'Section 4 · Region focus: VGR',
  'VGR: decision-maker priorities',
  'VGR: region overview',
  'VGR: national benchmark',
  'VGR: regional budget',
  'VGR: medicines budget',
  'VGR: disease burden',
  'Section 5 · Where this could go next',
  'From a deck to a live dashboard',
]
