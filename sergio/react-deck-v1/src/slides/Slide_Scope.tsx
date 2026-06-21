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
    detail: 'Each on the same dimensions: demographics, equity, budget, disease burden and governance.',
  },
  {
    num: '93',
    label: 'Stakeholders named',
    detail: 'Across 21 regions × 5 roles plus the national bodies. Three regions carry structural exceptions where the role is split or distributed; nine seats remain in confirmation.',
  },
  {
    num: '23',
    label: 'Reform signals',
    detail: 'Dated changes through 2027 to policy, contracts, recommendations and vaccine programmes that open engagement windows.',
  },
]

export function Slide_Scope({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="What we have built"
      title="Scope of the work"
      subtitle="The focus is on governance and the priorities of regional decision-makers."
    >
      <div style={{
        flex: 1, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)',
        gridTemplateRows: '1fr 1fr', gap: 16, paddingTop: 8, paddingBottom: 8,
      }}>
        {ANCHORS.map(a => (
          <div key={a.label} className="card card-accent" style={{
            padding: '22px 26px', display: 'flex', flexDirection: 'column',
            justifyContent: 'center', gap: 10,
          }}>
            <div>
              <div style={{
                fontSize: 64, fontWeight: 800, color: 'var(--navy)',
                lineHeight: 1, marginBottom: 6,
                fontVariantNumeric: 'tabular-nums',
              }}>
                {a.num}
                {a.unit && (
                  <span style={{
                    fontSize: 24, color: 'var(--accent)', fontWeight: 600, marginLeft: 6,
                  }}>
                    {a.unit}
                  </span>
                )}
              </div>
              <div style={{
                fontSize: 13, fontWeight: 700, color: 'var(--accent-d)',
                letterSpacing: '0.06em', textTransform: 'uppercase',
              }}>
                {a.label}
              </div>
            </div>
            <p style={{
              fontSize: 13, color: 'var(--navy-soft)', lineHeight: 1.6, margin: 0,
            }}>
              {a.detail}
            </p>
          </div>
        ))}
      </div>
    </Slide>
  )
}
