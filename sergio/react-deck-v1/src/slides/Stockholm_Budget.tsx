import { Slide } from '../components/Slide'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

const REGIONS = DATA as any[]

// Per-inhabitant net of the kommunalekonomisk utjämning system, 2026 (total across all five
// parts). Source: SCB table OE0115A / KomEkUtj, ContentsCode OE0115B7 (utfall kr/invånare).
// Each region is shown against AVG_NET (mean net across the 21 regions); MAX_ABS scales the bars.
const AVG_NET = Math.round(REGIONS.reduce((s, d) => s + d.utjamning_net_2026, 0) / REGIONS.length)
const MAX_ABS = Math.max(...REGIONS.map(d => Math.abs(d.utjamning_net_2026)))

const STAGES = [
  {
    n: '1',
    title: 'Regional income tax',
    body: 'The primary source. Each region sets its own tax rate on residents’ income.',
    note: 'Tax bases differ widely between regions.',
    color: 'var(--track-a)',
    soft: 'var(--track-a-soft)',
  },
  {
    n: '2',
    title: 'Income equalisation',
    body: 'The largest lever. High tax-base regions pay a fee; low tax-base regions receive a grant.',
    note: 'High tax-base regions pay; low receive.',
    color: 'var(--track-b)',
    soft: 'var(--track-b-soft)',
  },
  {
    n: '3',
    title: 'Cost equalisation',
    body: 'Compensates for structural need a region can’t control: age structure, density, geography.',
    note: 'Age, density and geography drive compensated need.',
    color: 'var(--track-c)',
    soft: 'var(--track-c-soft)',
  },
  {
    n: '4',
    title: 'Region allocates',
    body: 'The region distributes its envelope across primary care, hospitals and pharma, by need model and political priority.',
    note: 'Targeted state grants layer on top.',
    color: 'var(--accent)',
    soft: 'var(--accent-xl)',
  },
]

// Diverging bar centred on break-even (0). Left = pays in, right = receives.
function NetBar({ value, max }: { value: number; max: number }) {
  const HALF = 150
  const seg = (Math.abs(value) / max) * HALF
  const pays = value < 0
  return (
    <div style={{ position: 'relative', height: 20, width: HALF * 2, flexShrink: 0 }}>
      <div style={{ position: 'absolute', left: 0, right: 0, top: '50%', height: 1, background: 'var(--gray-3)' }} />
      <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 1.5, background: 'var(--gray-1)' }} />
      <div style={{
        position: 'absolute', top: '50%', transform: 'translateY(-50%)',
        height: 11, borderRadius: 2,
        background: pays ? 'var(--navy)' : 'var(--accent)',
        width: seg,
        ...(pays ? { right: '50%' } : { left: '50%' }),
      }} />
    </div>
  )
}

function NetRow({ name, value, max, tag, highlight }: { name: string; value: number; max: number; tag: string; highlight?: boolean }) {
  const pays = value < 0
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr 120px', alignItems: 'center', gap: 14, padding: '8px 0' }}>
      <div>
        <div style={{ fontSize: 12.5, fontWeight: 700, color: highlight ? 'var(--accent-d)' : 'var(--navy)' }}>{name}</div>
        <div style={{ fontSize: 10, color: 'var(--gray-1)' }}>{tag}</div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <NetBar value={value} max={max} />
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: 18, fontWeight: 800, color: pays ? 'var(--navy)' : 'var(--accent-d)', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
          {pays ? '−' : '+'}{fmt.num(Math.abs(value))}
        </div>
        <div style={{ fontSize: 9.5, color: 'var(--gray-1)', marginTop: 2 }}>SEK / inhabitant</div>
      </div>
    </div>
  )
}

const shortName = (r: string) => r.replace('Region ', '').replace('Västra Götalandsregionen', 'VGR')

interface Props extends SlideProps { region?: string }

export function Stockholm_Budget({ isActive, region = 'Region Stockholm' }: Props) {
  const stk: any = REGIONS.find(d => d.region === region)
  const short = shortName(region)
  const grpRank = [...REGIONS].sort((a, b) => b.grp_per_capita_ksek - a.grp_per_capita_ksek)
    .findIndex(d => d.region === region) + 1
  const NET = stk.utjamning_net_2026
  const isStockholm = region === 'Region Stockholm'
  const isGotland = region === 'Region Gotland'

  const regionTag = isStockholm ? 'the only region that pays in'
    : isGotland ? 'receives the most of all 21 regions'
    : NET < 0 ? 'net contributor' : 'net recipient'

  const rows: { name: string; value: number; tag: string; highlight?: boolean }[] = [
    { name: region, value: NET, tag: regionTag, highlight: true },
    { name: 'Average region', value: AVG_NET, tag: 'mean across the 21 regions' },
  ]

  const subtitleTail = isStockholm
    ? 'Among the 21 regions, Stockholm is the only one that pays in.'
    : `${short} is a net ${NET < 0 ? 'contributor' : 'recipient'} in 2026.`

  const synth = isStockholm ? (
    <>Stockholm’s below-national spend per capita is partly by design. As one of Sweden’s wealthiest and lowest-need
      regions (highest GRP per capita, {fmt.num(stk.grp_per_capita_ksek)} kSEK, rank {grpRank} of 21), its tax base is
      the only one above the income-equalisation guarantee (110% of the national average), making it the sole net
      contributor of the 21 regions in 2026 rather than a recipient. Budget conversations here are about <em>reallocation
      and innovation appetite inside a constrained envelope</em> rather than topping up unmet need. </>
  ) : (
    <>{short} {NET < 0 ? 'contributes' : 'receives'} {fmt.num(Math.abs(NET))} SEK per inhabitant through the equalisation
      system, with GRP per capita {fmt.num(stk.grp_per_capita_ksek)} kSEK (rank {grpRank} of 21). </>
  )

  return (
    <Slide
      isActive={isActive}
      sectionLabel={`${short} · how the budget is set`}
      title="Where the regional budget comes from"
      subtitle={`Regional healthcare runs on regional income tax, smoothed by a national equalisation system that moves resources from wealthier, lower-need regions to poorer, higher-need ones. ${subtitleTail}`}
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', paddingTop: 12, paddingBottom: 4 }}>

        {/* Funding chain */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, position: 'relative' }}>
          {STAGES.map((s, i) => (
            <div key={s.n} style={{ position: 'relative' }}>
              <div className="card" style={{
                padding: '12px 13px', height: '100%', borderTop: `3px solid ${s.color}`,
                display: 'flex', flexDirection: 'column',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <div style={{
                    width: 22, height: 22, borderRadius: '50%', background: s.soft,
                    border: `1.5px solid ${s.color}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 12, fontWeight: 800, color: s.color, flexShrink: 0,
                  }}>{s.n}</div>
                  <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--navy)', lineHeight: 1.1 }}>{s.title}</div>
                </div>
                <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.45, margin: '0 0 8px 0', flex: 1 }}>{s.body}</p>
                <div style={{
                  fontSize: 11, fontWeight: 700, color: s.color,
                  borderTop: '1px solid var(--gray-4)', paddingTop: 6,
                }}>{s.note}</div>
              </div>
              {i < STAGES.length - 1 && (
                <div style={{
                  position: 'absolute', right: -8, top: '50%', transform: 'translateY(-50%)',
                  fontSize: 16, color: 'var(--gray-2)', zIndex: 2, fontWeight: 700,
                }}>›</div>
              )}
            </div>
          ))}
        </div>

        {/* Net position contrast */}
        <div className="card card-accent" style={{ padding: '12px 18px' }}>
          <div style={{
            fontSize: 12, fontWeight: 700, color: 'var(--navy)', textTransform: 'uppercase',
            letterSpacing: '0.04em', marginBottom: 4,
          }}>
            Pays in vs receives · equalisation system · 2026
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--gray-1)', marginBottom: 2 }}>
            <span>← pays in</span>
            <span>break-even</span>
            <span>receives →</span>
          </div>
          {rows.map((r, i) => (
            <div key={r.name} style={i > 0 ? { borderTop: '1px solid var(--gray-4)' } : undefined}>
              <NetRow name={shortName(r.name)} value={r.value} max={MAX_ABS} tag={r.tag} highlight={r.highlight} />
            </div>
          ))}
        </div>

        {/* Synthesis */}
        <div style={{
          background: 'var(--bg-tint)', borderRadius: 4, padding: '11px 16px',
          fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5,
        }}>
          {synth}
        </div>
      </div>

      <div className="source-note">
        Equalisation system has five parts (income- and cost-equalisation, structural &amp; transition grants, the regulating post). Per-inhabitant net among regions, 2026: SCB table OE0115A (utfall kr/invånare). GRP: SCB regional accounts.
      </div>
    </Slide>
  )
}
