import { Slide } from '../components/Slide'
import { Sparkline } from '../components/Sparkline'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'
import PTS_LATEST from '../data/pts_latest.json'
import NT_RADET from '../data/nt_radet.json'
import PFIZER_MONTHLY from '../data/pfizer_monthly.json'

const stk: any = (DATA as any[]).find(d => d.region === 'Region Stockholm')
const ptsLatest: any = (PTS_LATEST as any)['Region Stockholm'] || {}
const ntRadet: Record<string, string> = NT_RADET as any
const monthly: Record<string, Array<[string, number]>> = (PFIZER_MONTHLY as any).stockholm || {}

interface Product {
  key: string
  label: string
  ind: string
  ptKey: string
  trend: 'declining' | 'growing' | 'stable' | 'launch' | 'prelaunch'
  ntKey: string
}

const PRODUCTS: Product[] = [
  { key: 'vyndaqel', label: 'Vyndaqel', ind: 'ATTR cardiomyopathy', ptKey: 'Vyndaqel', trend: 'growing', ntKey: 'Vyndaqel' },
  { key: 'ibrance', label: 'Ibrance', ind: 'HR+/HER2− breast cancer', ptKey: 'Ibrance', trend: 'declining', ntKey: 'Ibrance' },
  { key: 'lorviqua', label: 'Lorviqua', ind: 'ALK+ NSCLC', ptKey: 'Lorbrena/Lorviqua', trend: 'stable', ntKey: 'Lorviqua' },
  { key: 'tukysa', label: 'Tukysa', ind: 'HER2+ breast cancer (incl. brain mets)', ptKey: 'Tukysa', trend: 'growing', ntKey: 'Tukysa' },
  { key: 'elrexfio', label: 'Elrexfio', ind: 'Multiple myeloma 4L+', ptKey: '', trend: 'launch', ntKey: 'Elrexfio' },
  { key: 'talzenna', label: 'Talzenna', ind: 'BRCA breast / mCRPC + Xtandi', ptKey: 'Talzenna', trend: 'stable', ntKey: 'Talzenna' },
  { key: 'vydura', label: 'Vydura', ind: 'Acute migraine (specialist)', ptKey: 'Vydura', trend: 'growing', ntKey: 'Vydura' },
  { key: 'hympavzi', label: 'Hympavzi', ind: 'Haemophilia A/B', ptKey: '', trend: 'prelaunch', ntKey: 'Hympavzi' },
]

const trendLabel = (t: string) =>
  t === 'declining' ? 'Declining' :
  t === 'growing' ? 'Growing' :
  t === 'stable' ? 'Stable' :
  t === 'launch' ? 'Launch' : 'Pre-launch'

export function Stockholm03_Portfolio({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — Pfizer portfolio"
      title="The 12 products in Stockholm — by SEK, by patients, by trajectory"
      subtitle="Latest patient counts (AVA where available, Socialstyrelsen otherwise) alongside the three-year SEK footprint and recent monthly trend."
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm">
          <thead>
            <tr>
              <th style={{ width: '12%' }}>Product</th>
              <th style={{ width: '20%' }}>Indication</th>
              <th className="numeric" style={{ width: '8%' }}>Patients (latest)</th>
              <th style={{ width: '8%' }}>Source · Year</th>
              <th className="numeric" style={{ width: '8%' }}>3-yr SEK (M)</th>
              <th style={{ width: '15%' }}>NT-rådet status</th>
              <th style={{ width: '9%' }}>Trend</th>
              <th style={{ width: '20%' }}>Stockholm SEK trendline</th>
            </tr>
          </thead>
          <tbody>
            {PRODUCTS.map(p => {
              const sek = (stk as any)[p.key]
              const sekM = sek ? (sek / 1e6).toFixed(1) : '—'
              const ptsEntry = p.ptKey ? ptsLatest[p.ptKey] : null
              const pts = ptsEntry?.value
              const ptsSrc = ptsEntry ? `${ptsEntry.source} · ${ptsEntry.year}` : '—'
              const ntStatus = ntRadet[p.ntKey] || '—'
              const series = monthly[p.label] || monthly[p.label === 'Lorviqua' ? 'Lorbrena' : p.label] || []
              const sparkValues = series.map(s => s[1])
              return (
                <tr key={p.key}>
                  <td className="product">{p.label}</td>
                  <td style={{ fontSize: 10.5 }}>{p.ind}</td>
                  <td className="numeric">{pts != null ? fmt.num(pts) : '—'}</td>
                  <td style={{ fontSize: 9.5, color: 'var(--gray-1)' }}>{ptsSrc}</td>
                  <td className="numeric">{sekM}</td>
                  <td style={{ fontSize: 10 }}>{ntStatus}</td>
                  <td><span className={`rp-trend ${p.trend}`}>{trendLabel(p.trend)}</span></td>
                  <td><Sparkline values={sparkValues} width={120} height={26} /></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div style={{
        marginTop: 12, padding: '8px 12px', background: 'var(--bg-soft)', borderRadius: 4,
        display: 'flex', justifyContent: 'space-between', fontSize: 10.5, color: 'var(--navy-soft)',
      }}>
        <div><strong>{(stk.pfizer_total_3yr / 1e6).toFixed(0)} M kr</strong> · Total Pfizer 3-yr footprint</div>
        <div><strong>{(stk.pfizer_vaccines / 1e6).toFixed(0)} M</strong> · Vaccines</div>
        <div><strong>{(stk.pfizer_rdim / 1e6).toFixed(0)} M</strong> · RD/IM</div>
        <div><strong>{(stk.pfizer_oncology / 1e6).toFixed(0)} M</strong> · Oncology</div>
      </div>

      <div className="source-note">
        Patient counts from Pfizer's AVA platform (Ibrance, Vydura — 2025 latest; Vyndaqel — sjukvårdsregion level)
        and from Socialstyrelsen Läkemedelsregistret (other products — most recent open year). SEK from IQVIA Sell-In.
        Xtandi ({(stk.xtandi/1e6).toFixed(0)} M kr 3-yr) is co-marketed with Astellas; included in oncology total.
      </div>
    </Slide>
  )
}
