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
import { Slide07_GovernanceBodies } from './Slide07_GovernanceBodies'
import { Slide08_DMM } from './Slide08_DMM'
import { Slide10_ProductTracks } from './Slide10_ProductTracks'
import { Slide11_ReformCalendar } from './Slide11_ReformCalendar'

// Stockholm
import { Stockholm01_Overview } from './Stockholm01_Overview'
import { Stockholm02_DiseaseBurden } from './Stockholm02_DiseaseBurden'
import { Stockholm03_Portfolio } from './Stockholm03_Portfolio'
import { Stockholm04_Vaccines } from './Stockholm04_Vaccines'
import { Stockholm05_PositioningQuadrant } from './Stockholm05_PositioningQuadrant'
import { Slide12_StakeholderPriorities } from './Slide12_StakeholderPriorities'
import { Stockholm06_Synthesis } from './Stockholm06_Synthesis'

// National analysis
import { Slide04_FindingsPreview } from './Slide04_FindingsPreview'
import { Analysis_BrickRecovery } from './Analysis_BrickRecovery'
import { Analysis_ATTRConcentration } from './Analysis_ATTRConcentration'
import { Analysis_VaccineTrends } from './Analysis_VaccineTrends'
import { Slide09_AntiPatterns } from './Slide09_AntiPatterns'

// Close
import { Slide14_Closing } from './Slide14_Closing'

const Section1Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '1', title: 'National mapping' })

const Section2Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '2', title: 'Stockholm' })

const Section3Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '3', title: 'National analysis' })

const Section4Divider = (props: SlideProps) =>
  SectionDivider({ ...props, number: '4', title: 'Where this could go next' })

export const ALL_SLIDES: ComponentType<SlideProps>[] = [
  // Open (4)
  Slide01_Cover,
  Slide_Scope,
  Slide02_Objectives,
  Slide03_Methodology,

  // Section 1 — National mapping (divider + 6)
  Section1Divider,
  Slide05_FourTracks,
  Slide06_HealthEquityIndicators,
  Slide07_GovernanceBodies,
  Slide08_DMM,
  Slide10_ProductTracks,
  Slide11_ReformCalendar,

  // Section 2 — Stockholm (divider + 7)
  Section2Divider,
  Stockholm01_Overview,
  Stockholm02_DiseaseBurden,
  Stockholm03_Portfolio,
  Stockholm04_Vaccines,
  Stockholm05_PositioningQuadrant,
  (props: SlideProps) => Slide12_StakeholderPriorities({ ...props, region: 'Region Stockholm' }),
  Stockholm06_Synthesis,

  // Section 3 — National analysis (divider + 5)
  Section3Divider,
  Slide04_FindingsPreview,
  Analysis_BrickRecovery,
  Analysis_ATTRConcentration,
  Analysis_VaccineTrends,
  Slide09_AntiPatterns,

  // Section 4 — Close (divider + 1)
  Section4Divider,
  Slide14_Closing,
]

export const SLIDE_TITLES: string[] = [
  'Cover',
  'What we have built',
  'Objectives',
  'Methodology',
  '— Section 1 — National mapping —',
  'Four-track architecture',
  'Health equity indicators',
  'Governance bodies (NT-rådet · NSG · LK)',
  'Decision-maker matrix (21 regions × 5 roles)',
  'Per-product mapping (12 products)',
  'Reform calendar 2025–2027',
  '— Section 2 — Stockholm —',
  'Stockholm — region overview',
  'Stockholm — disease burden',
  'Stockholm — Pfizer portfolio with trendlines',
  'Stockholm — vaccine landscape',
  'Stockholm — strategic positioning quadrant',
  'Stockholm — governance & stakeholder priorities',
  'Stockholm — strategic synthesis',
  '— Section 3 — National analysis —',
  'Five findings to anchor on',
  'CDK4/6 brick recovery (top 15)',
  'ATTR concentration in the V30M cluster',
  'National vaccine trajectories',
  'Engagement anti-patterns',
  '— Section 4 — Where this could go next —',
  'From a deck to a live dashboard',
]
