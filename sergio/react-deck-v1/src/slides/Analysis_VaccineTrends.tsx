import { Slide } from '../components/Slide'
import { LineChart } from '../components/LineChart'
import type { SlideProps } from '../types'
import VACCINE_MONTHLY from '../data/vaccine_monthly.json'

const monthly: Record<string, Array<[string, number]>> = (VACCINE_MONTHLY as any).national || {}

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

export function Analysis_VaccineTrends({ isActive }: SlideProps) {
  const rsv = buildSeries(Object.entries(RSV_COLORS).map(([name, color]) => ({ name, color })))
  const pcv = buildSeries(Object.entries(PCV_COLORS).map(([name, color]) => ({ name, color })))
  const tbe = buildSeries(Object.entries(TBE_COLORS).map(([name, color]) => ({ name, color })))

  return (
    <Slide
      isActive={isActive}
      sectionLabel="National vaccine trajectories"
      title="The three Pfizer vaccine markets, by month"
      subtitle="Current standings and direction of travel matter more here than three-year totals; these markets shift faster than the SEK aggregations suggest."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14, overflow: 'hidden' }}>

        {/* RSV */}
        <div className="card" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)' }}>
            RSV (adult vaccination)
          </div>
          <LineChart series={rsv.series} xLabels={rsv.xLabels} width={340} height={140} />
          <p style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
            Abrysvo (Pfizer) and Arexvy (GSK) are the two adult-RSV options. mResvia (Moderna) is the
            newer entrant. NT-rådet has been in "avvakta" since October 2023, yet the market is moving.
          </p>
        </div>

        {/* PCV */}
        <div className="card" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)' }}>
            Pneumococcal
          </div>
          <LineChart series={pcv.series} xLabels={pcv.xLabels} width={340} height={140} />
          <p style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
            Folkhälsomyndigheten's January 2026 update made PCV20 (Prevenar 20 / Apexxnar) the
            recommended conjugate for nearly all adult risk groups. Vaxneuvance and Capvaxive are
            the MSD competitors.
          </p>
        </div>

        {/* TBE */}
        <div className="card" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)' }}>
            TBE
          </div>
          <LineChart series={tbe.series} xLabels={tbe.xLabels} width={340} height={140} />
          <p style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
            FSME-IMMUN (Pfizer) leads against ENCEPUR. Folkhälsomyndigheten's May 2026 recommendation,
            based on the risk-area 1/2/3 classification, is the new framing for regional procurement.
          </p>
        </div>
      </div>
      <div className="source-note">
        Source: IQVIA Vaccines monthly aggregation, national.
      </div>
    </Slide>
  )
}
