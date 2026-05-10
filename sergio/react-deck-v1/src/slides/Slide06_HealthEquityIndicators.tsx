import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

interface RegionRow {
  region: string
  short: string
  pop: number
  premature_mortality_25_64?: number
  hc_amenable_mortality?: number
}

const ROWS = (DATA as RegionRow[])
  .filter(d => d.premature_mortality_25_64 != null)
  .sort((a, b) => (a.premature_mortality_25_64 ?? 0) - (b.premature_mortality_25_64 ?? 0))

const VALUES = ROWS.map(r => r.premature_mortality_25_64 as number)
const MIN = Math.min(...VALUES)
const MAX = Math.max(...VALUES)
const SCALE_MIN = MIN * 0.92
const RANGE = MAX - SCALE_MIN
const NATIONAL_AVG = VALUES.reduce((a, b) => a + b, 0) / VALUES.length
const AVG_PCT = ((NATIONAL_AVG - SCALE_MIN) / RANGE) * 100

export function Slide06_HealthEquityIndicators({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="How regions plan"
      title="The equity indicators that shape regional priorities"
      subtitle="The indicators regions reference, the spread that makes a national average insufficient, and how the resource-allocation model partially compensates."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16, overflow: 'hidden' }}>

        {/* Left: regional spread chart with national-average line */}
        <div className="card" style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
          <div className="card-title">Premature mortality, ages 25 to 64, per 100,000 (2024)</div>
          <div style={{ fontSize: 10, color: 'var(--gray-1)', marginTop: -4, marginBottom: 8 }}>
            All 21 regions, sorted low to high. The dashed line is the national average ({Math.round(NATIONAL_AVG)} per 100k).
          </div>

          <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* National average dashed line — overlay positioned over the bar columns */}
            <div style={{
              position: 'absolute',
              top: 0, bottom: 0,
              left: `calc(94px + (100% - 94px - 36px - 12px) * ${AVG_PCT / 100})`,
              borderLeft: '1.5px dashed var(--navy)',
              opacity: 0.55,
              pointerEvents: 'none',
              zIndex: 2,
            }}>
              <div style={{
                position: 'absolute', top: -2, left: 4,
                fontSize: 9, fontWeight: 700, color: 'var(--navy)',
                background: 'white', padding: '0 3px',
                whiteSpace: 'nowrap',
              }}>
                national avg
              </div>
            </div>

            {ROWS.map((r) => {
              const v = r.premature_mortality_25_64 as number
              const widthPct = ((v - SCALE_MIN) / RANGE) * 100
              const above = v > NATIONAL_AVG
              const fillColor = above ? 'var(--warn)' : 'var(--accent)'
              const opacity = above ? 0.7 : 0.55
              return (
                <div key={r.region} style={{
                  display: 'grid', gridTemplateColumns: '88px 1fr 36px',
                  alignItems: 'center', gap: 6, fontSize: 9.5, position: 'relative', zIndex: 1,
                }}>
                  <div style={{ color: 'var(--navy)', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {r.short}
                  </div>
                  <div style={{ position: 'relative', height: 12, background: 'var(--gray-5)', borderRadius: 2 }}>
                    <div style={{
                      position: 'absolute', top: 0, bottom: 0, left: 0,
                      width: `${widthPct}%`, background: fillColor, opacity,
                      borderRadius: 2,
                    }} />
                  </div>
                  <div style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--navy)' }}>
                    {Math.round(v)}
                  </div>
                </div>
              )
            })}
          </div>

          <div style={{ marginTop: 8, fontSize: 9.5, color: 'var(--gray-1)', display: 'flex', gap: 14 }}>
            <span><span style={{
              display: 'inline-block', width: 10, height: 10, background: 'var(--accent)',
              opacity: 0.55, borderRadius: 2, verticalAlign: 'middle', marginRight: 4,
            }} />Below national average</span>
            <span><span style={{
              display: 'inline-block', width: 10, height: 10, background: 'var(--warn)',
              opacity: 0.7, borderRadius: 2, verticalAlign: 'middle', marginRight: 4,
            }} />Above national average</span>
          </div>
        </div>

        {/* Right: indicators + behovsmodell + Pfizer relevance */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="card" style={{ padding: '10px 12px', borderLeft: '4px solid var(--accent)' }}>
            <div style={{
              fontSize: 10.5, fontWeight: 700, color: 'var(--accent)',
              letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
            }}>
              The indicators in common use
            </div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              Premature mortality 25 to 64. Healthcare-amenable mortality. Suicide rates above 25.
              Lifestyle drivers. The Care Need Index (Kolada N00992). Hälso- och sjukvårdsbarometern
              for patient-reported access. Maintained by SCB, Folkhälsomyndigheten, Socialstyrelsen,
              RCC and Kolada.
            </p>
          </div>

          <div className="card card-accent" style={{ padding: '10px 12px' }}>
            <div style={{
              fontSize: 10.5, fontWeight: 700, color: 'var(--accent)',
              letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
            }}>
              The behovsmodell, and what it does
            </div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              SKR distributes the state grant for the reimbursement system between the 21 regions,
              weighted on age, household income, education and household type. Higher-need regions
              receive more grant per capita. Each region then layers its own resursfördelningsmodell
              for sub-regional distribution.
            </p>
          </div>

          <div className="card" style={{
            padding: '10px 12px', background: 'var(--bg-tint)',
            borderLeft: '4px solid var(--good)',
          }}>
            <div style={{
              fontSize: 10.5, fontWeight: 700, color: 'var(--good)',
              letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
            }}>
              Why this matters for engagement
            </div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              Pfizer cannot influence the behovsmodell, but reading it gives useful context. Regions
              high on premature mortality face more political pressure on access equity. They also
              receive a relatively larger state grant, but typically still face tighter pharma
              budgets per inhabitant. Therapies framed around equity-of-access tend to land
              differently in those regions than in low-need ones.
            </p>
          </div>
        </div>
      </div>
    </Slide>
  )
}
