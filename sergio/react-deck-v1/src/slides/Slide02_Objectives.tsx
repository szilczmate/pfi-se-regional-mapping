import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const OBJECTIVES: { n: number; headline: string; body: string }[] = [
  {
    n: 1,
    headline: 'Know the decision-makers',
    body: 'Who holds the seats that decide on access in each region, across the four access tracks (five including vaccines), and who governs around them: NT-rådet, NSG Läkemedel and the regional läkemedelskommittéer.',
  },
  {
    n: 2,
    headline: 'Understand their priorities',
    body: 'For each decision-maker, the budget, capacity, equity and quality issues shaping their 2025–2026 priorities, with specific numbers, named programmes and dated reform signals.',
  },
  {
    n: 3,
    headline: 'Understand the evidence they use',
    body: 'Which indicators each region looks at, where those numbers come from, which forums use them and which decisions they shape. The focus is on what gets acted on and by whom, not only what is measured.',
  },
  {
    n: 4,
    headline: 'Lift the right questions',
    body: 'For each therapy area, which forum is the right place to take a question.',
  },
]

export function Slide02_Objectives({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Why this work exists"
      title="Four questions this work answers"
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 14, paddingBottom: 8 }}>
        {OBJECTIVES.map(o => (
          <div
            key={o.n}
            className="card card-accent"
            style={{
              display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 10,
              padding: '20px 22px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 4 }}>
              <span style={{
                fontSize: 52, fontWeight: 800, color: 'var(--accent)',
                lineHeight: 1, fontVariantNumeric: 'tabular-nums',
              }}>{o.n}</span>
              <span style={{ fontSize: 18.5, fontWeight: 700, color: 'var(--navy)', lineHeight: 1.25 }}>
                {o.headline}
              </span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--navy-soft)', lineHeight: 1.6, margin: 0 }}>
              {o.body}
            </p>
          </div>
        ))}
      </div>
    </Slide>
  )
}
