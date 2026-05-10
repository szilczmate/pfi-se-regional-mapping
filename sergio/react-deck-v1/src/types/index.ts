export interface SlideProps {
  isActive: boolean
  isPrev?: boolean
  goSlide?: (n: number) => void
}

export interface RegionStakeholder {
  Region: string
  Sjukvårdsregion: string
  Website?: string
  Regiondirektör?: string
  HSD?: string
  'RS ordf'?: string
  'HSN ordf'?: string
  'LK ordf'?: string
  'NT-rådet rep (SVR)'?: string
  'NSG rep (SVR)'?: string
  [key: string]: string | undefined
}

export interface NamedIndividual {
  name: string
  roles: string
}

export interface BrickRow {
  brick: string
  county: string
  total_sek: number
  ibrance_share: number
  kisqali_share: number
  verzenios_share: number
  kisqali_growth: number
  recovery_sek: number
  quadrant: string
}

export interface CriticalIntel {
  cat: string
  label: string
  title: string
  body: string
}

export interface PtsLatestEntry {
  value: number | null
  year: number
  source: string
  note?: string
}

export interface StakeholderPriority {
  role: string
  priorities: string
}

export type Confidence = 'VERIFIED' | 'OBSERVED' | 'INFERRED' | 'OPEN'
export type TrackKey = 'A' | 'B' | 'C' | 'D'
