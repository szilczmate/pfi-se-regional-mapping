import { Slide } from '../components/Slide'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

const REGION = 'Region Stockholm'
const ALL = DATA as any[]

const ordinal = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

interface Ind {
  field: string
  label: string
  year: string
  unit: string
  dec: number
}

// All four are "lower is better" — rank 1 = lowest = strongest outcome.
const INDICATORS: Ind[] = [
  { field: 'premature_mortality_25_64', label: 'Premature mortality, 25–64', year: '2024', unit: '/100k', dec: 0 },
  { field: 'hc_amenable_mortality', label: 'Healthcare-amenable mortality', year: '2023', unit: '/100k', dec: 0 },
  { field: 'suicide_25plus', label: 'Suicide, 25 +', year: '2024', unit: '/100k', dec: 1 },
  { field: 'overweight_obese_pct', label: 'Overweight / obese', year: '2023', unit: '%', dec: 1 },
]

function Strip({ ind }: { ind: Ind }) {
  const rows = ALL
    .map(d => ({ short: d.short, v: d[ind.field] as number, pop: d.pop, stk: d.region === REGION }))
    .filter(r => r.v != null)
  const lo = Math.min(...rows.map(r => r.v))
  const hi = Math.max(...rows.map(r => r.v))
  const pad = (hi - lo) * 0.08 || 1
  const a = lo - pad
  const b = hi + pad
  const pos = (v: number) => ((v - a) / (b - a)) * 100
  const natAvg = rows.reduce((s, r) => s + r.v * r.pop, 0) / rows.reduce((s, r) => s + r.pop, 0)
  const stk = rows.find(r => r.stk)!
  const rankAsc = [...rows].sort((x, y) => x.v - y.v).findIndex(r => r.stk) + 1

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 7 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--navy)' }}>
          {ind.label} <span style={{ fontSize: 9, fontWeight: 500, color: 'var(--gray-1)' }}>{ind.year}</span>
        </span>
        <span style={{ fontSize: 9.5, color: 'var(--gray-1)' }}>
          <span style={{ color: 'var(--accent-d)', fontWeight: 700 }}>
            Sthlm {fmt.dec(stk.v, ind.dec)}{ind.unit}
          </span>
          {' · '}{ordinal(rankAsc)} lowest · Sweden {fmt.dec(natAvg, ind.dec)}{ind.unit}
        </span>
      </div>
      <div style={{ position: 'relative', height: 16 }}>
        {/* baseline */}
        <div style={{ position: 'absolute', left: 0, right: 0, top: '50%', height: 2, background: 'var(--gray-5)', borderRadius: 2 }} />
        {/* national average tick */}
        <div style={{ position: 'absolute', top: -3, bottom: -3, left: `${pos(natAvg)}%`, width: 1.5, background: 'var(--navy)', opacity: 0.5 }} />
        {/* region dots */}
        {rows.map(r => (
          <div key={r.short} title={`${r.short}: ${fmt.dec(r.v, ind.dec)}${ind.unit}`} style={{
            position: 'absolute', top: '50%', left: `${pos(r.v)}%`,
            width: r.stk ? 11 : 7, height: r.stk ? 11 : 7, borderRadius: '50%',
            transform: 'translate(-50%, -50%)',
            background: r.stk ? 'var(--accent)' : 'var(--gray-3)',
            border: r.stk ? '1.5px solid white' : 'none',
            boxShadow: r.stk ? '0 0 0 1.5px var(--accent)' : 'none',
            zIndex: r.stk ? 3 : 1,
          }} />
        ))}
      </div>
    </div>
  )
}

export function Slide06_HealthEquityIndicators({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="How regions plan"
      title="Equity indicators that shape regional priorities"
      subtitle="The same view applied to four indicators: every region as a dot, the population-weighted national average marked, Stockholm highlighted. The resource-allocation model adjusts the grant for need."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16, overflow: 'hidden' }}>

        {/* Left: four indicators, same strip plot each */}
        <div className="card" style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
          <div className="card-title">Where Stockholm sits in the 21-region spread</div>
          <div style={{ fontSize: 10, color: 'var(--gray-1)', marginTop: -4, marginBottom: 12 }}>
            Each dot is a region; the line marks the national average. Lower is better on all four.
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            {INDICATORS.map(ind => <Strip key={ind.field} ind={ind} />)}
          </div>
          <div style={{ display: 'flex', gap: 16, fontSize: 9, color: 'var(--gray-1)', marginTop: 4 }}>
            <span><span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)', verticalAlign: 'middle', marginRight: 4 }} />Stockholm</span>
            <span><span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: 'var(--gray-3)', verticalAlign: 'middle', marginRight: 4 }} />Other regions</span>
            <span><span style={{ display: 'inline-block', width: 2, height: 10, background: 'var(--navy)', opacity: 0.5, verticalAlign: 'middle', marginRight: 5 }} />National average</span>
          </div>
        </div>

        {/* Right: the need model + what it means */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="card card-accent" style={{ padding: '11px 13px' }}>
            <div style={{
              fontSize: 10.5, fontWeight: 700, color: 'var(--accent)',
              letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
            }}>
              The need model (behovsmodellen)
            </div>
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              SKR weights 22 demographic groups per region (age, education, household income, living situation)
              against national average consumption to set each region's modellkostnad, then channels a larger grant
              per capita to higher-need regions. Each region layers its own resursfördelningsmodell on top.
            </p>
          </div>

          <div className="card" style={{ padding: '11px 13px', background: 'var(--bg-tint)', borderLeft: '4px solid var(--good)' }}>
            <div style={{
              fontSize: 10.5, fontWeight: 700, color: 'var(--good)',
              letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
            }}>
              Need, spend and equity
            </div>
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              Stockholm sits among the lowest on all four indicators, so equity-of-access is not the lever here.
              Higher-need regions carry more political pressure on access equity. Pharma spend per inhabitant does
              not track need in a simple way: several higher-need northern regions spend more per capita
              than Stockholm (see the läkemedel-budget slide), so an equity framing lands differently region to region.
            </p>
          </div>
        </div>
      </div>

      <div className="source-note">
        Indicators from Kolada (premature mortality N01451 2024; healthcare-amenable mortality N79190 2023; suicide N61603 2024; overweight/obese N00955 2023); also referenced regionally: Care Need Index (Kolada N00992) and Hälso- och sjukvårdsbarometern. Behovsmodell: Överenskommelse läkemedelsförmånerna 2026 (SKR).
      </div>
    </Slide>
  )
}
