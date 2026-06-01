import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

interface Event {
  date: string
  title: string
  impact: string
  products: string[]
  kind: 'policy' | 'nt' | 'contract' | 'guideline' | 'regulatory'
}

const EVENTS: Event[] = [
  { date: '2026-05', title: 'Folkhälsomyndigheten TBE recommendation (risk-area 1/2/3)',
    impact: 'A reframe of regional procurement and the forum where the vaccine question is decided.',
    products: ['FSME-IMMUN'], kind: 'guideline' },
  { date: '2026-07-01', title: 'Margareta Holmström becomes NT-rådet chair',
    impact: 'Quiet but real signal for items moving through national review in the second half of 2026.',
    products: ['(all)'], kind: 'nt' },
  { date: '2026-Q4', title: 'HER2CLIMB-05 first-line data: care-programme update window',
    impact: 'The forum here is RCC and the breast-cancer national care-programme group, since NT-rådet has declined to recommend.',
    products: ['Tukysa'], kind: 'guideline' },
  { date: '2027', title: 'Revised solidarity-financing model: target establishment',
    impact: 'Potential change in financing route for some hospital and high-cost products. No specific Pfizer product is publicly confirmed as qualifying.',
    products: ['Vyndaqel', 'Hympavzi', 'Elrexfio', 'Tukysa', 'Abrysvo'], kind: 'policy' },
]

const kindColor: Record<string, string> = {
  policy: 'var(--track-a)',
  nt: 'var(--track-c)',
  contract: 'var(--track-b)',
  guideline: 'var(--gold)',
  regulatory: 'var(--accent)',
}

const kindLabel: Record<string, string> = {
  policy: 'Policy',
  nt: 'NT-rådet',
  contract: 'Contract',
  guideline: 'Guideline',
  regulatory: 'TLV',
}

export function Slide11_ReformCalendar({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Reform-signal calendar"
      title="Reform windows, 2026–2027"
      subtitle="The reform signals still ahead in national policy, governance and clinical guidance."
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div className="dmm-wrap" style={{ flex: 'none' }}>
          <table className="dmm">
          <thead>
            <tr>
              <th style={{ width: '11%' }}>Date</th>
              <th style={{ width: '10%' }}>Kind</th>
              <th style={{ width: '24%' }}>Inflection</th>
              <th style={{ width: '34%' }}>Pfizer impact</th>
              <th style={{ width: '21%' }}>Products affected</th>
            </tr>
          </thead>
          <tbody>
            {EVENTS.map(e => (
              <tr key={e.date + e.title}>
                <td style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 12, padding: '16px 10px' }}>{e.date}</td>
                <td>
                  <span style={{
                    fontSize: 9, fontWeight: 700, padding: '1px 6px',
                    borderRadius: 8, background: 'white',
                    border: `1px solid ${kindColor[e.kind]}`,
                    color: kindColor[e.kind],
                  }}>{kindLabel[e.kind]}</span>
                </td>
                <td style={{ fontWeight: 600, color: 'var(--navy)', fontSize: 12 }}>{e.title}</td>
                <td style={{ fontSize: 11 }}>{e.impact}</td>
                <td>
                  {e.products.map(p => (
                    <span key={p} style={{
                      display: 'inline-block', marginRight: 3, marginBottom: 2,
                      padding: '1px 6px', background: 'var(--accent-l)',
                      color: 'var(--accent-d)', borderRadius: 8, fontSize: 9, fontWeight: 600,
                    }}>{p}</span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
      <div className="source-note">
        Sources: SKR Cirkulär 26-16, regeringen.se, samverkanlakemedel.se, Folkhälsomyndigheten programme pages, E-hälsomyndigheten.
      </div>
    </Slide>
  )
}
