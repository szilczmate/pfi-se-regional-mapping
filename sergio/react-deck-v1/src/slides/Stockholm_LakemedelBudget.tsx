import { Slide } from '../components/Slide'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

// Verified — Kolada KPI N70001 "Nettokostnad läkemedel inom läkemedelsförmånen, kr/inv", 2024.
// All 21 regions. Source CSV: working/data/interim/kolada_budget_latest.csv.
// NOTE: This is the FÖRMÅN-only series (N70001), deliberately DISTINCT from data.json
// `pharma_per_capita`, which is Kolada N70059 "Nettokostnad läkemedel, totalt" (incl. rekvisition).
// The two genuinely differ for ~10 regions (e.g. VGR 2806.83 vs 2799.49) — do NOT "dedupe" them.
const FORMAN_2024: Record<string, number> = {
  'Region Stockholm': 3104.35,
  'Region Uppsala': 3478.69,
  'Region Sörmland': 3637.97,
  'Region Östergötland': 3293.50,
  'Region Jönköpings län': 3324.24,
  'Region Kronoberg': 3422.65,
  'Region Kalmar': 3450.35,
  'Region Gotland': 4313.53,
  'Region Blekinge': 3911.64,
  'Region Skåne': 3276.57,
  'Region Halland': 4042.61,
  'Västra Götalandsregionen': 2806.83,
  'Region Värmland': 3804.03,
  'Region Örebro län': 3460.07,
  'Region Västmanland': 3386.00,
  'Region Dalarna': 3660.84,
  'Region Gävleborg': 3566.94,
  'Region Västernorrland': 3632.10,
  'Region Jämtland Härjedalen': 3492.95,
  'Region Västerbotten': 3215.50,
  'Region Norrbotten': 4094.60,
}

// Verified — regional läkemedelsprognoser 2025-2026. Per-region cost change 2025→2026
// (incl. national rebates) from Region Stockholm prognos (HSF 2025-11-05), Tabell 2;
// Stockholm 2025 absolute spend from Tabell 1 (after rebates, excl. VAT/co-pay/vaccines).
const OUTLOOK: Record<string, { spend2025?: string; forman: string; rekv: string; tail?: string }> = {
  'Region Stockholm': {
    spend2025: 'recept 6 950 + rekvisition 2 517 mnkr (≈9.5 bn, after rebates)',
    forman: '+1.7%',
    rekv: '+8.1%',
    tail: 'Receptkostnad then falls in 2027 as apixaban loses patent and the högkostnadsskydd ceiling rise reaches full effect.',
  },
  'Region Skåne': { spend2025: 'recept 4 869 + rekvisition 1 916 mnkr (≈6.8 bn, after rebates)', forman: '+0.7%', rekv: '+10.6%' },
  'Västra Götalandsregionen': { spend2025: '≈7.3 bn net (7 258 mnkr, 2025 forecast, after rebates)', forman: '+0.3%', rekv: '+6.6%' },
}

const REGIONS = DATA as any[]
const popOf = (name: string): number => REGIONS.find(d => d.region === name)?.pop ?? 0
const shortOf = (name: string): string =>
  REGIONS.find(d => d.region === name)?.short ?? name.replace('Region ', '')

// Population-weighted national average förmån cost (true national kr/inv).
const TOTAL_POP = Object.keys(FORMAN_2024).reduce((s, n) => s + popOf(n), 0)
const NAT_AVG = Object.entries(FORMAN_2024).reduce((s, [n, v]) => s + v * popOf(n), 0) / TOTAL_POP

const SORTED = Object.entries(FORMAN_2024)
  .map(([name, v]) => ({ name, short: shortOf(name), v }))
  .sort((a, b) => a.v - b.v)

const ordinal = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

const cardLabel = (text: string, color = 'var(--accent)') => (
  <div style={{
    fontSize: 10.5, fontWeight: 700, color,
    letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 5,
  }}>
    {text}
  </div>
)

interface Props extends SlideProps {
  region?: string
}

export function Stockholm_LakemedelBudget({ isActive, region = 'Region Stockholm' }: Props) {
  const short = shortOf(region)
  const val = FORMAN_2024[region] ?? NAT_AVG
  const rankAsc = SORTED.findIndex(d => d.name === region) + 1
  const deltaPct = ((val - NAT_AVG) / NAT_AVG) * 100
  const below = deltaPct < 0
  const outlook = OUTLOOK[region]

  return (
    <Slide
      isActive={isActive}
      sectionLabel={`${short} · läkemedel budget`}
      title="How the medicines budget is allocated"
      subtitle={`The state funds the läkemedelsförmån through a needs-based model. ${short}'s net förmån cost per inhabitant is shown against all 21 regions and the national average.`}
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.35fr 1fr', gap: 16, overflow: 'hidden' }}>

        {/* Left: per-region förmån cost chart */}
        <div className="card" style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
          <div className="card-title">Läkemedelsförmån net cost, kr/inhabitant (2024)</div>
          <div style={{ fontSize: 10, color: 'var(--gray-1)', marginTop: -4, marginBottom: 8 }}>
            All 21 regions, low to high. Dashed line is the population-weighted national average ({fmt.num(Math.round(NAT_AVG))} kr/inv).
          </div>

          <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            {/* National average overlay line */}
            <div style={{
              position: 'absolute', top: 0, bottom: 14,
              left: `calc(86px + (100% - 86px - 46px - 12px) * ${((NAT_AVG - SORTED[0].v * 0.95) / (SORTED[SORTED.length - 1].v - SORTED[0].v * 0.95)) * 100 / 100})`,
              borderLeft: '1.5px dashed var(--navy)', opacity: 0.55, pointerEvents: 'none', zIndex: 2,
            }}>
              <div style={{
                position: 'absolute', top: -2, left: 4, fontSize: 9, fontWeight: 700,
                color: 'var(--navy)', background: 'white', padding: '0 3px', whiteSpace: 'nowrap',
              }}>
                national avg
              </div>
            </div>

            {(() => {
              const scaleMin = SORTED[0].v * 0.95
              const range = SORTED[SORTED.length - 1].v - scaleMin
              return SORTED.map(r => {
                const isCur = r.name === region
                const widthPct = ((r.v - scaleMin) / range) * 100
                return (
                  <div key={r.name} style={{
                    display: 'grid', gridTemplateColumns: '86px 1fr 46px',
                    alignItems: 'center', gap: 6, fontSize: 9.5, position: 'relative', zIndex: 1,
                  }}>
                    <div style={{
                      color: isCur ? 'var(--accent-d)' : 'var(--navy)', fontWeight: isCur ? 700 : 400,
                      textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}>
                      {r.short}
                    </div>
                    <div style={{ position: 'relative', height: 12, background: 'var(--gray-5)', borderRadius: 2 }}>
                      <div style={{
                        position: 'absolute', top: 0, bottom: 0, left: 0, width: `${widthPct}%`,
                        background: isCur ? 'var(--accent)' : 'var(--gray-3)', borderRadius: 2,
                      }} />
                    </div>
                    <div style={{
                      textAlign: 'right', fontVariantNumeric: 'tabular-nums',
                      color: isCur ? 'var(--accent-d)' : 'var(--navy)', fontWeight: isCur ? 700 : 400,
                    }}>
                      {fmt.num(Math.round(r.v))}
                    </div>
                  </div>
                )
              })
            })()}
          </div>
        </div>

        {/* Right: how the budget is set */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="card card-accent" style={{ padding: '11px 13px' }}>
            {cardLabel('The state grant, 2026')}
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 4 }}>
              <span style={{ fontSize: 24, fontWeight: 800, color: 'var(--navy)', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
                {fmt.num(41461)}
              </span>
              <span style={{ fontSize: 12, color: 'var(--accent-d)', fontWeight: 700 }}>mnkr</span>
            </div>
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, margin: 0 }}>
              Total state läkemedelsbidrag (net contribution) in the Överenskommelse läkemedelsförmånerna 2026.
              Socialstyrelsen forecasts the national förmån cost rising from 40.1 to 47.3 bn SEK by 2029 (+18%),
              led by rare-disease therapies.
            </p>
          </div>

          <div className="card card-accent" style={{ padding: '11px 13px' }}>
            {cardLabel('How it is split (behovsmodellen)')}
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, margin: 0 }}>
              demographic groups per region (age, sex, marital status, employment, income, housing type), weighted against
              national average consumption to set each region's modellkostnad. Solidarisk finansiering then tops up
              regions carrying costly drugs unevenly (≥30 SEK/inv above the national average), where rare-disease
              and specialty therapy areas concentrate.
            </p>
          </div>

          <div className="card" style={{ padding: '11px 13px', background: 'var(--bg-tint)', borderLeft: '4px solid var(--accent)' }}>
            {cardLabel('Spend & outlook')}
            {outlook?.spend2025 && (
              <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: '0 0 5px' }}>
                <strong style={{ color: 'var(--navy)' }}>2025 spend:</strong> {outlook.spend2025}.
              </p>
            )}
            <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, margin: 0 }}>
              Förmån net cost <strong style={{ color: 'var(--navy)' }}>{fmt.num(Math.round(val))} kr/inv</strong>, {ordinal(rankAsc)} lowest of 21, {Math.abs(deltaPct).toFixed(1)}% {below ? 'below' : 'above'} the national average.
              {outlook ? ` Into 2026, incl. rebates: förmån ${outlook.forman}, rekvisition ${outlook.rekv}.` : ''}
              {outlook?.tail ? ` ${outlook.tail}` : ''} Per-region allocation (received vs returned) stays internal to Kammarkollegiet.
            </p>
          </div>
        </div>
      </div>

      <div className="source-note">
        Sources: Överenskommelse läkemedelsförmånerna 2026 (SKR), Tabell 1 + behovsmodell; Kolada KPI N70001 (förmån net cost/inv, 2024); regional läkemedelsprognoser 2025–2026 (Region Stockholm HSF 2025-11-05, Tabell 1–2; Skåne; VGR); Socialstyrelsen läkemedelsförsäljning – analys och prognos 2026–2029.
      </div>
    </Slide>
  )
}
