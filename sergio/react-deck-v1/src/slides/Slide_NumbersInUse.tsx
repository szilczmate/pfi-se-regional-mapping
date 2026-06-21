import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

interface Row {
  indicator: string
  detail: string
  source: string
  forum: string
  decision: string
}

const ROWS: Row[] = [
  {
    indicator: 'Behovsmodell weights',
    detail: 'age · income · education · household',
    source: 'SKR · SCB',
    forum: 'SKR nationally → RS / HSN',
    decision: 'How the state grant is split between the 21 regions, then each region’s own resursfördelningsmodell for sub-regional distribution.',
  },
  {
    indicator: 'Premature & amenable mortality',
    detail: 'ages 25–64, per 100k',
    source: 'SCB · Socialstyrelsen · FoHM',
    forum: 'HSN · regional folkhälsa',
    decision: 'Where equity-of-access pressure concentrates and which populations capacity gets targeted toward.',
  },
  {
    indicator: 'Care Need Index (CNI)',
    detail: 'Kolada N00992',
    source: 'Kolada · Socialstyrelsen',
    forum: 'HSN · primary-care allocation',
    decision: 'Weighting of vårdcentral resources (e.g. Stockholm’s 580 mnkr to vårdcentraler in the 2026 budget).',
  },
  {
    indicator: 'Väntetider / vårdgaranti',
    detail: 'wait-time compliance',
    source: 'SKR Väntetider i vården',
    forum: 'HSD · HSN',
    decision: 'Capacity investment and where the delivery-bottleneck budget goes. It is also how a capacity-sparing therapy is judged.',
  },
  {
    indicator: 'Läkemedelskostnad per capita',
    detail: '+ förmånsprognos',
    source: 'SKR cost tracking · Socialstyrelsen prognos · TLV',
    forum: 'LK · HSD · ekonomistab',
    decision: 'Budget-impact acceptance for new entrants and formulary positioning on the rekommendationslista.',
  },
]

export function Slide_NumbersInUse({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Indicators in use"
      title="Which indicators drive which decisions"
      subtitle="Every region tracks broadly the same indicators. The difference is which forum acts on each one and the decision it drives."
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm">
          <thead>
            <tr>
              <th style={{ width: '23%' }}>Indicator</th>
              <th style={{ width: '21%' }}>Where it comes from</th>
              <th style={{ width: '20%' }}>Forum that acts on it</th>
              <th style={{ width: '36%' }}>The decision it shapes</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map(r => (
              <tr key={r.indicator}>
                <td style={{ padding: '18px 10px' }}>
                  <div style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 12 }}>{r.indicator}</div>
                  <div style={{ fontSize: 10, color: 'var(--gray-1)', marginTop: 2 }}>{r.detail}</div>
                </td>
                <td style={{ fontSize: 11 }}>{r.source}</td>
                <td style={{ fontSize: 11, fontWeight: 600, color: 'var(--navy-soft)' }}>{r.forum}</td>
                <td style={{ fontSize: 11, fontWeight: 600, color: 'var(--navy)' }}>{r.decision}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{
        marginTop: 12, padding: '8px 14px', background: 'var(--bg-soft)',
        borderLeft: '3px solid var(--accent)', borderRadius: 3,
        fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55,
      }}>
        <strong style={{ color: 'var(--navy)' }}>Next:</strong> the Stockholm section applies this same view to a single region.
      </div>

      <div className="source-note">
        Sources: SKR, SCB, Socialstyrelsen, Kolada (N00992), TLV, Folkhälsomyndigheten.
      </div>
    </Slide>
  )
}
