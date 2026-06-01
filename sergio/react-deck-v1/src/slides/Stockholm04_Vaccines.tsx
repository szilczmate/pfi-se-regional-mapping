import { Slide } from '../components/Slide'
import { LineChart } from '../components/LineChart'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'
import VACCINE_MONTHLY from '../data/vaccine_monthly.json'

const stk: any = (DATA as any[]).find(d => d.region === 'Region Stockholm')
const monthly: Record<string, Array<[string, number]>> = (VACCINE_MONTHLY as any).stockholm || {}

const RSV_COLORS = { Abrysvo: '#1A7CA8', Arexvy: '#DC2626', mResvia: '#92400E' }
const PCV_COLORS = { 'Prevenar 20': '#1A7CA8', Vaxneuvance: '#DC2626', Capvaxive: '#92400E' }
const TBE_COLORS = { 'FSME-IMMUN': '#1A7CA8', ENCEPUR: '#DC2626' }

function fmtMonth(m: string): string {
  const d = new Date(m)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[d.getMonth()]}-${String(d.getFullYear()).slice(2)}`
}

function buildSeries(specs: Array<{ name: string; color: string }>) {
  const allMonths = new Set<string>()
  specs.forEach(s => (monthly[s.name] || []).forEach(([m]) => allMonths.add(m)))
  const sortedMonths = Array.from(allMonths).sort()
  const xLabels = sortedMonths.map(fmtMonth)
  const series = specs.map(s => {
    const map = new Map((monthly[s.name] || []) as Array<[string, number]>)
    return { name: s.name, color: s.color, values: sortedMonths.map(m => map.get(m) || 0) }
  })
  return { xLabels, series }
}

// Compute units share for each market (Pfizer units / total units, last 12 months)
function unitsShare(pfizerName: string, allNames: string[]): number {
  const allMonths = new Set<string>()
  allNames.forEach(n => (monthly[n] || []).forEach(([m]) => allMonths.add(m)))
  const sortedMonths = Array.from(allMonths).sort().slice(-12)
  let pfizerSum = 0
  let totalSum = 0
  sortedMonths.forEach(m => {
    allNames.forEach(n => {
      const map = new Map((monthly[n] || []) as Array<[string, number]>)
      const v = map.get(m) || 0
      totalSum += v
      if (n === pfizerName) pfizerSum += v
    })
  })
  return totalSum > 0 ? (pfizerSum / totalSum) * 100 : 0
}

interface Market {
  market: string
  pfizerProduct: string
  series: ReturnType<typeof buildSeries>
  sekShare: number
  unitsShare: number
  caption: string
  border: string
}

export function Stockholm04_Vaccines({ isActive }: SlideProps) {
  const rsvSeries = buildSeries(Object.entries(RSV_COLORS).map(([name, color]) => ({ name, color })))
  const pcvSeries = buildSeries(Object.entries(PCV_COLORS).map(([name, color]) => ({ name, color })))
  const tbeSeries = buildSeries(Object.entries(TBE_COLORS).map(([name, color]) => ({ name, color })))

  const MARKETS: Market[] = [
    {
      market: 'RSV (adult)',
      pfizerProduct: 'Abrysvo',
      series: rsvSeries,
      sekShare: stk.rsv_share,
      unitsShare: unitsShare('Abrysvo', Object.keys(RSV_COLORS)),
      caption: 'Pfizer leads by SEK but is a minority by units. Arexvy is outselling Abrysvo dose-for-dose. The accurate framing here leads with dose volume.',
      border: 'var(--accent-d)',
    },
    {
      market: 'Pneumococcal',
      pfizerProduct: 'Prevenar 20',
      series: pcvSeries,
      sekShare: stk.pneu_share,
      unitsShare: unitsShare('Prevenar 20', Object.keys(PCV_COLORS)),
      caption: "Low Pfizer share. Folkhälsomyndigheten's January 2026 update made PCV20 the recommended conjugate for nearly all adult risk groups. Procurement cycle paces the move.",
      border: 'var(--track-a)',
    },
    {
      market: 'TBE',
      pfizerProduct: 'FSME-IMMUN',
      series: tbeSeries,
      sekShare: stk.tbe_share,
      unitsShare: unitsShare('FSME-IMMUN', Object.keys(TBE_COLORS)),
      caption: "Pfizer-dominant. Folkhälsomyndigheten's May 2026 risk-area guidance is the new framing for regional procurement. ENCEPUR is the residual challenger.",
      border: 'var(--good)',
    },
  ]

  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — vaccine landscape"
      title="Pfizer's three vaccine markets in Stockholm"
      subtitle="Monthly trajectories with current share. The dose-volume picture differs from the SEK picture in two of the three markets."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14, overflow: 'hidden' }}>
        {MARKETS.map(m => (
          <div key={m.market} className="card" style={{
            padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10,
            borderLeft: `4px solid ${m.border}`, background: 'white',
            minWidth: 0, overflow: 'hidden',
          }}>
            {/* Header: market name + Pfizer product */}
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy)' }}>
                {m.market}
              </div>
              <div style={{ fontSize: 10.5, color: 'var(--gray-1)', marginTop: 2 }}>
                Pfizer product: {m.pfizerProduct}
              </div>
            </div>

            {/* Two big share stats side-by-side */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <div style={{
                padding: '8px 10px', background: 'var(--bg-soft)', borderRadius: 3,
              }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: m.border, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
                  {fmt.dec(m.sekShare)}%
                </div>
                <div style={{ fontSize: 9.5, color: 'var(--gray-1)', marginTop: 2 }}>
                  Share by SEK
                </div>
              </div>
              <div style={{
                padding: '8px 10px', background: 'var(--bg-soft)', borderRadius: 3,
              }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: m.border, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
                  {fmt.dec(m.unitsShare)}%
                </div>
                <div style={{ fontSize: 9.5, color: 'var(--gray-1)', marginTop: 2 }}>
                  Share by units (last 12 mo)
                </div>
              </div>
            </div>

            {/* Chart */}
            <LineChart series={m.series.series} xLabels={m.series.xLabels} width={300} height={110} />

            {/* Caption */}
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: 0 }}>
              {m.caption}
            </p>
          </div>
        ))}
      </div>
      <div className="source-note">
        Sources: IQVIA Vaccines monthly aggregation, Stockholm-region cut. Folkhälsomyndigheten programme pages.
      </div>
    </Slide>
  )
}
