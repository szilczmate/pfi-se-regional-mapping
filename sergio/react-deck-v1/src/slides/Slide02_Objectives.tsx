import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const OBJECTIVES = [
  {
    n: 1,
    headline: 'Know the decision-makers',
    body: 'Region by region, role by role: who currently holds the seats that decide on access for the twelve in-scope products, and who sits on the three national bodies — NT-rådet, NSG Läkemedel, and the regional läkemedelskommittéer.',
  },
  {
    n: 2,
    headline: 'Understand what is on their table',
    body: 'For each decision-maker, the actual budget, capacity, equity and quality issues shaping their 2025–2026 priorities. Concrete numbers, named programmes and dated reform signals rather than generic descriptions.',
  },
  {
    n: 3,
    headline: 'Understand the evidence they use',
    body: 'Which indicators they look at, where those indicators come from, which forums consume them, and which decisions those numbers actually shape. Not just what is measured, but who acts on it.',
  },
  {
    n: 4,
    headline: 'Lift the right questions',
    body: 'For each Pfizer product, which forum is the right place to take a question and which ones are not. The recurring missteps are catalogued explicitly so they can be avoided in the field.',
  },
]

export function Slide02_Objectives({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Why this work exists"
      title="Four questions this deck sets out to answer"
      subtitle="Drawn directly from what Pfizer asked for at the start of the engagement."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, paddingBottom: 8 }}>
        {OBJECTIVES.map(o => (
          <div
            key={o.n}
            className="card card-accent"
            style={{ display: 'flex', flexDirection: 'column', gap: 6 }}
          >
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 4 }}>
              <span style={{
                fontSize: 28, fontWeight: 800, color: 'var(--accent)',
                lineHeight: 1, fontVariantNumeric: 'tabular-nums',
              }}>{o.n}</span>
              <span style={{ fontSize: 15, fontWeight: 700, color: 'var(--navy)', lineHeight: 1.25 }}>
                {o.headline}
              </span>
            </div>
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              {o.body}
            </p>
          </div>
        ))}
      </div>
    </Slide>
  )
}
