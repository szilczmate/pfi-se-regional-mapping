import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import CAL from '../data/reform_calendar.json'

interface Ev { date: string; kind: string; title: string }
const EVENTS = (CAL as { events: Ev[] }).events

const KIND_COLOR: Record<string, string> = {
  policy: 'var(--track-a)',
  'nt-radet': 'var(--track-c)',
  contract: 'var(--track-b)',
  guideline: 'var(--gold)',
  regulatory: 'var(--accent)',
}
const KIND_LABEL: Record<string, string> = {
  policy: 'Policy',
  'nt-radet': 'NT-rådet',
  contract: 'Contract',
  guideline: 'Guideline',
  regulatory: 'Regulatory / TLV',
}
const YEARS = ['2025', '2026', '2027']

// Normalise stray em/en dashes in source titles to a middot (keep hyphens in compounds).
const clean = (t: string) => t.replace(/\s[—–]\s/g, ' · ')

export function Slide_ReformCalendarFull({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Reform-signal calendar"
      title="The full reform calendar, 2025–2027"
      subtitle="All 23 tracked reform signals across policy, governance, clinical guidance, contracts and vaccines. The four key windows still ahead are highlighted on the previous slide."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14, minHeight: 0 }}>
        {YEARS.map(y => {
          const evs = EVENTS.filter(e => e.date.startsWith(y))
          return (
            <div key={y} className="card" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
                marginBottom: 9, paddingBottom: 6, borderBottom: '1px solid var(--gray-4)',
              }}>
                <span style={{ fontSize: 16, fontWeight: 800, color: 'var(--navy)' }}>{y}</span>
                <span style={{ fontSize: 10, color: 'var(--gray-1)', fontWeight: 600 }}>{evs.length} signals</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                {evs.map((e, i) => (
                  <div key={i} style={{ borderLeft: `2.5px solid ${KIND_COLOR[e.kind] || 'var(--gray-2)'}`, paddingLeft: 8 }}>
                    <span style={{ fontSize: 9.5, fontWeight: 700, color: 'var(--accent-d)', fontVariantNumeric: 'tabular-nums' }}>{e.date}</span>
                    <span style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.3 }}>{'  '}{clean(e.title)}</span>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 10, fontSize: 10, color: 'var(--gray-1)' }}>
        {Object.keys(KIND_LABEL).map(k => (
          <span key={k} style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 10, height: 3, borderRadius: 2, background: KIND_COLOR[k], display: 'inline-block' }} />
            {KIND_LABEL[k]}
          </span>
        ))}
      </div>

      <div className="source-note">
        Sources: samverkanlakemedel.se, SKR Cirkulär 26-16, regeringen.se, E-hälsomyndigheten, Folkhälsomyndigheten, TLV. Per-event Pfizer impact, products and confidence sit in the reform-signal calendar workbook.
      </div>
    </Slide>
  )
}
