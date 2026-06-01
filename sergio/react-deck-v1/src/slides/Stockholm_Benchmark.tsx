import { Slide } from '../components/Slide'
import { Icon } from '../components/Icon'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

const REGIONS = DATA as any[]
const TOTAL_POP = REGIONS.reduce((s, d) => s + d.pop, 0)

// Population-weighted national average = Σ(value·pop) / Σpop.
const nat = (field: string): number =>
  REGIONS.reduce((s, d) => s + d[field] * d.pop, 0) / TOTAL_POP

// Region's position when ordered high→low (1 = highest) and low→high (1 = lowest).
const rankDesc = (field: string, region: string): number =>
  [...REGIONS].sort((a, b) => b[field] - a[field]).findIndex(d => d.region === region) + 1
const rankAsc = (field: string, region: string): number =>
  [...REGIONS].sort((a, b) => a[field] - b[field]).findIndex(d => d.region === region) + 1

const ordinal = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

const cardHeader = (icon: React.ReactNode, title: string, note: string) => (
  <div style={{ marginBottom: 10 }}>
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8,
      fontSize: 13, fontWeight: 700, color: 'var(--navy)',
      letterSpacing: '0.04em', textTransform: 'uppercase',
    }}>
      <span style={{ color: 'var(--accent)' }}>{icon}</span>
      <span>{title}</span>
    </div>
    <div style={{ fontSize: 11, color: 'var(--gray-1)', marginTop: 3, letterSpacing: '0.02em' }}>
      {note}
    </div>
  </div>
)

// Diverging bar: centre line = national average; segment grows toward the region's side.
function DivergeBar({ pct, tone }: { pct: number; tone: 'neutral' | 'good' | 'warn' }) {
  const HALF = 52
  const seg = Math.min(Math.abs(pct) / 20, 1) * HALF
  const below = pct < 0
  const color = tone === 'neutral' ? 'var(--accent)' : tone === 'good' ? 'var(--good)' : 'var(--warn)'
  return (
    <div style={{ position: 'relative', height: 14, width: HALF * 2, flexShrink: 0 }}>
      <div style={{ position: 'absolute', left: 0, right: 0, top: '50%', height: 1, background: 'var(--gray-3)' }} />
      <div style={{ position: 'absolute', left: '50%', top: 1, bottom: 1, width: 1, background: 'var(--gray-1)' }} />
      <div style={{
        position: 'absolute', top: '50%', transform: 'translateY(-50%)',
        height: 6, borderRadius: 2, background: color, width: seg,
        ...(below ? { right: '50%' } : { left: '50%' }),
      }} />
    </div>
  )
}

interface RowDef {
  field: string
  label: string
  render: (v: number) => string
  unit?: string
  deltaMode: 'pct' | 'pp'
  tone: 'neutral' | 'lowerBetter'
  rankWord: string
}

function MetricRow({ r, rec }: { r: RowDef; rec: any }) {
  const sv = rec[r.field] as number
  const nv = nat(r.field)
  const deltaAbs = sv - nv
  const pct = (deltaAbs / nv) * 100
  const below = deltaAbs < 0
  const tone = r.tone === 'neutral' ? 'neutral' : below ? 'good' : 'warn'
  const rank = r.tone === 'lowerBetter' ? rankAsc(r.field, rec.region) : rankDesc(r.field, rec.region)
  const deltaLabel =
    r.deltaMode === 'pp'
      ? `${below ? '−' : '+'}${Math.abs(deltaAbs).toFixed(1)} pp`
      : `${below ? '−' : '+'}${Math.abs(pct).toFixed(1)}%`
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1fr auto', gap: 6,
      padding: '7px 0', borderTop: '1px solid var(--gray-4)',
    }}>
      <div>
        <div style={{ fontSize: 11.5, color: 'var(--navy)', fontWeight: 600, lineHeight: 1.2 }}>
          {r.label}
        </div>
        <div style={{ fontSize: 9.5, color: 'var(--gray-1)', marginTop: 2 }}>
          {r.rankWord} · {ordinal(rank)} of 21
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'flex-end' }}>
        <div style={{ textAlign: 'right', minWidth: 84 }}>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--navy)', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
            {r.render(sv)}{r.unit && <span style={{ fontSize: 10, color: 'var(--gray-1)', fontWeight: 500, marginLeft: 2 }}>{r.unit}</span>}
          </div>
          <div style={{ fontSize: 9.5, color: 'var(--gray-1)', marginTop: 2 }}>
            nat {r.render(nv)}{r.unit ? ` ${r.unit}` : ''}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
          <DivergeBar pct={pct} tone={tone} />
          <div style={{ fontSize: 9.5, fontWeight: 700, color: tone === 'neutral' ? 'var(--accent-d)' : tone === 'good' ? 'var(--good)' : 'var(--warn)' }}>
            {deltaLabel}
          </div>
        </div>
      </div>
    </div>
  )
}

const SPEND: RowDef[] = [
  { field: 'hc_cost_per_capita', label: 'Healthcare cost / capita', render: v => fmt.num(Math.round(v)), unit: 'SEK', deltaMode: 'pct', tone: 'neutral', rankWord: 'spend' },
  { field: 'pharma_per_capita', label: 'Pharma / capita', render: v => fmt.num(Math.round(v)), unit: 'SEK', deltaMode: 'pct', tone: 'neutral', rankWord: 'spend' },
  { field: 'primary_care_per_capita', label: 'Primary care / capita', render: v => fmt.num(Math.round(v)), unit: 'SEK', deltaMode: 'pct', tone: 'neutral', rankWord: 'spend' },
  { field: 'pharma_pct_hc', label: 'Pharma share of healthcare', render: v => fmt.dec(v, 1), unit: '%', deltaMode: 'pp', tone: 'neutral', rankWord: 'share' },
]

const OUTCOMES: RowDef[] = [
  { field: 'premature_mortality_25_64', label: 'Premature mortality 25–64', render: v => fmt.dec(v, 1), unit: '/100k', deltaMode: 'pct', tone: 'lowerBetter', rankWord: 'lowest' },
  { field: 'hc_amenable_mortality', label: 'Healthcare-amenable mortality', render: v => fmt.dec(v, 1), unit: '/100k', deltaMode: 'pct', tone: 'lowerBetter', rankWord: 'lowest' },
  { field: 'suicide_25plus', label: 'Suicide 25 +', render: v => fmt.dec(v, 1), unit: '/100k', deltaMode: 'pct', tone: 'lowerBetter', rankWord: 'lowest' },
  { field: 'overweight_obese_pct', label: 'Overweight / obese', render: v => fmt.dec(v, 1), unit: '%', deltaMode: 'pp', tone: 'lowerBetter', rankWord: 'lowest' },
]

// Stockholm keeps its reviewed narrative; other regions get a factual, data-driven version.
const SUBTITLE: Record<string, string> = {
  'Region Stockholm': 'Stockholm spends below the national average per capita while recording among the strongest health outcomes in the country. Relative need is low; access is driven by specialist appetite and the adoption of innovation.',
}
const SYNTHESIS: Record<string, string> = {
  'Region Stockholm': "With outcomes already among the country’s best, access here rests on specialist appetite, trial infrastructure and early adoption of innovation, set against a spend envelope that sits below the national line by design.",
}

interface Props extends SlideProps { region?: string }

export function Stockholm_Benchmark({ isActive, region = 'Region Stockholm' }: Props) {
  const rec: any = REGIONS.find(d => d.region === region)
  const short = region.replace('Region ', '').replace('Västra Götalandsregionen', 'VGR')
  const spendBelow = SPEND.filter(r => rec[r.field] < nat(r.field)).length
  const outcomeBelow = OUTCOMES.filter(r => rec[r.field] < nat(r.field)).length
  const subtitle = SUBTITLE[region] ||
    `${short}'s spend per capita and health outcomes, each centred on the population-weighted national average across all 21 regions.`
  const synth = SYNTHESIS[region] ||
    `${short} sits below the national average on ${spendBelow} of 4 spend measures and ${outcomeBelow} of 4 outcome measures, at equity-need rank ${rec.equity_rank} of 21. Weigh spend against need before judging access appetite.`

  return (
    <Slide
      isActive={isActive}
      sectionLabel={`${short} · spend vs outcomes`}
      title={`${short} against the national benchmark`}
      subtitle={subtitle}
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>

          <div className="card card-accent" style={{ padding: '14px 16px' }}>
            {cardHeader(<Icon name="budget" />, 'Spend per capita', 'bar centred on national average · rank 1 = highest spend')}
            {SPEND.map(r => <MetricRow key={r.field} r={r} rec={rec} />)}
            <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, marginTop: 10, paddingTop: 8, borderTop: '1px solid var(--gray-4)' }}>
              Below the national average on {spendBelow} of 4 spend measures; {ordinal(rankDesc('hc_cost_per_capita', region))} of 21 on total healthcare spend per capita.
            </div>
          </div>

          <div className="card card-accent" style={{ padding: '14px 16px' }}>
            {cardHeader(<Icon name="equity" />, 'Health outcomes', 'bar centred on national average · lower is better · rank 1 = lowest')}
            {OUTCOMES.map(r => <MetricRow key={r.field} r={r} rec={rec} />)}
            <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, marginTop: 10, paddingTop: 8, borderTop: '1px solid var(--gray-4)' }}>
              Below the national average on {outcomeBelow} of 4 outcome measures (lower is better). Equity-need rank {rec.equity_rank} of 21 (1 = highest need).
            </div>
          </div>
        </div>

        <div style={{ background: 'var(--bg-tint)', borderRadius: 4, padding: '11px 16px', fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5 }}>
          {synth}
        </div>
      </div>

      <div className="source-note">
        National figures are population-weighted across all 21 regions (Σ value·pop ÷ Σ pop). Sources: Kolada KPIs, SCB, Folkhälsomyndigheten. Same reconciled dataset as the region overview.
      </div>
    </Slide>
  )
}
