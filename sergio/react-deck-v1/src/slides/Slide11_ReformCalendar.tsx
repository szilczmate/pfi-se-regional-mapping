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
  { date: '2025-07-01', title: 'Högkostnadsskydd → 3 800 SEK',
    impact: 'OOP exposure for all chronic Pfizer förmån products',
    products: ['Vyndaqel', 'Vydura', 'Ibrance', 'Lorviqua', 'Xtandi', 'Talzenna'],
    kind: 'policy' },
  { date: '2025-09-02', title: 'Vyndaqel — national collaboration archived',
    impact: 'Forum shifts: NAG LOK now produces the treatment recommendation. Beyonttra is in the same picture.',
    products: ['Vyndaqel'], kind: 'nt' },
  { date: '2025-11-04', title: 'Talzenna TLV further expansion (dnr 2380/2025)',
    impact: 'Patient-group expansion. HRR-mutated mCRPC scope to be confirmed.',
    products: ['Talzenna'], kind: 'regulatory' },
  { date: '2026-01', title: 'PCV20 single vaccine for risk groups',
    impact: 'Favourable for Pfizer — Prevenar 20 / Apexxnar is now the only conjugate pneumococcal vaccine recommended for nearly all risk groups.',
    products: ['Prevenar 20'], kind: 'guideline' },
  { date: '2026-01-01', title: 'State-region agreement 2026 — 41,461 mnkr',
    impact: 'Covers all reimbursed products. The 2027 solidarity-financing revision is parked for further work.',
    products: ['(all reimbursed)'], kind: 'policy' },
  { date: '2026-05', title: 'Folkhälsomyndigheten TBE recommendation (risk-area 1/2/3)',
    impact: 'A reframe of regional procurement for FSME-IMMUN.',
    products: ['FSME-IMMUN'], kind: 'guideline' },
  { date: '2026-05-31', title: 'Talzenna agreement ends (option to extend by one year)',
    impact: 'Extension/renegotiation window opens.',
    products: ['Talzenna'], kind: 'contract' },
  { date: '2026-07-01', title: 'Margareta Holmström becomes NT-rådet chair',
    impact: 'Quiet but real signal for items moving through national review in the second half of 2026.',
    products: ['(all)'], kind: 'nt' },
  { date: '2026-08-31', title: 'Vyndaqel agreement ends (option to extend by one year)',
    impact: 'Decision point: extend, renegotiate, or terminate against the Beyonttra alternative.',
    products: ['Vyndaqel'], kind: 'contract' },
  { date: '2026-Q4', title: 'HER2CLIMB-05 first-line data — care-programme update window',
    impact: 'The forum here is RCC and the breast-cancer national care-programme group, since NT-rådet has declined to recommend.',
    products: ['Tukysa'], kind: 'guideline' },
  { date: '2027', title: 'Revised solidarity-financing model — target establishment',
    impact: 'Potential change in financing route for some hospital and high-cost products. No specific Pfizer product is publicly confirmed as qualifying.',
    products: ['Vyndaqel', 'Hympavzi', 'Elrexfio', 'Tukysa', 'Abrysvo'], kind: 'policy' },
  { date: '2027-04-30', title: 'Tukysa agreement ends (option to extend by one year)',
    impact: 'Renegotiation window. The breast-cancer care-programme group is the operating lever for positioning.',
    products: ['Tukysa'], kind: 'contract' },
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
      title="2025–2027 — when each window actually opens"
      subtitle="The twelve dated inflections worth planning stakeholder cadence around. Each one shifts which forum is engageable, or which contract becomes negotiable."
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
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
                <td style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 10.5 }}>{e.date}</td>
                <td>
                  <span style={{
                    fontSize: 9, fontWeight: 700, padding: '1px 6px',
                    borderRadius: 8, background: 'white',
                    border: `1px solid ${kindColor[e.kind]}`,
                    color: kindColor[e.kind],
                  }}>{kindLabel[e.kind]}</span>
                </td>
                <td style={{ fontWeight: 600, color: 'var(--navy)', fontSize: 10.5 }}>{e.title}</td>
                <td style={{ fontSize: 10 }}>{e.impact}</td>
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
      <div className="source-note">
        Sources: SKR Cirkulär 26-16, regeringen.se, samverkanlakemedel.se, Folkhälsomyndigheten programme pages, E-hälsomyndigheten.
      </div>
    </Slide>
  )
}
