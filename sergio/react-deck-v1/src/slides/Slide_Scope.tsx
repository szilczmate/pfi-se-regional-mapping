import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

interface Anchor {
  num: string
  unit?: string
  label: string
  detail: string
}

const ANCHORS: Anchor[] = [
  {
    num: '4',
    label: 'Decision tracks',
    detail: 'The architecture underlying every Pfizer access decision in Sweden, used as the organising frame throughout.',
  },
  {
    num: '21',
    label: 'Regions analysed',
    detail: 'Each on the same dimensions: demographics, equity, budget, disease burden, governance and Pfizer footprint.',
  },
  {
    num: '12',
    label: 'Pfizer products mapped',
    detail: 'Across vaccines, oncology and rare disease/internal medicine, each placed against the four-track architecture.',
  },
  {
    num: '135',
    label: 'Stakeholder seats',
    detail: 'Across 21 regions × 7 roles plus the national bodies, covering roughly 103 distinct individuals.',
  },
  {
    num: '23',
    label: 'Reform inflections',
    detail: 'Dated changes through 2027 to policy, contracts, recommendations and vaccine programmes that reshape engagement windows.',
  },
  {
    num: '36',
    unit: 'months',
    label: 'of monthly brick-level data',
    detail: 'IQVIA Sell-In at brick granularity from April 2023, complemented by AVA patient-level depth on three products.',
  },
]

export function Slide_Scope({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="What we have built"
      title="The scope of the work, in six numbers"
      subtitle="An overview of what this analysis covers, before going into how it was built and what it found."
    >
      <div style={{
        flex: 1, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gridTemplateRows: '1fr 1fr', gap: 16, paddingTop: 8, paddingBottom: 8,
      }}>
        {ANCHORS.map(a => (
          <div key={a.label} className="card card-accent" style={{
            padding: '18px 20px', display: 'flex', flexDirection: 'column',
            justifyContent: 'space-between',
          }}>
            <div>
              <div style={{
                fontSize: 56, fontWeight: 800, color: 'var(--navy)',
                lineHeight: 1, marginBottom: 4,
                fontVariantNumeric: 'tabular-nums',
              }}>
                {a.num}
                {a.unit && (
                  <span style={{
                    fontSize: 22, color: 'var(--accent)', fontWeight: 600, marginLeft: 6,
                  }}>
                    {a.unit}
                  </span>
                )}
              </div>
              <div style={{
                fontSize: 12, fontWeight: 700, color: 'var(--accent-d)',
                letterSpacing: '0.06em', textTransform: 'uppercase',
                marginBottom: 8,
              }}>
                {a.label}
              </div>
            </div>
            <p style={{
              fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0,
            }}>
              {a.detail}
            </p>
          </div>
        ))}
      </div>
    </Slide>
  )
}
