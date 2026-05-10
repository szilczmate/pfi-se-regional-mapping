import { Slide } from '../components/Slide'
import { KPI, KPIGrid } from '../components/KPI'
import { Icon } from '../components/Icon'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

const cardHeader = (icon: React.ReactNode, title: string, color = 'var(--accent)') => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: 8,
    fontSize: 13, fontWeight: 700, color: 'var(--navy)',
    letterSpacing: '0.04em', marginBottom: 8, textTransform: 'uppercase',
  }}>
    <span style={{ color }}>{icon}</span>
    <span>{title}</span>
  </div>
)

const stk: any = (DATA as any[]).find(d => d.region === 'Region Stockholm')

export function Stockholm01_Overview({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — region overview"
      title="The region in numbers"
      subtitle={`Sjukvårdsregion: ${stk?.svr || '—'}. Largest region by population, with the densest concentration of specialist infrastructure in Sweden.`}
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, alignContent: 'start' }}>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="people" />, 'Demographics today')}
          <KPIGrid cols={3}>
            <KPI value={fmt.num(stk.pop)} label="Population" />
            <KPI value={fmt.dec(stk.pop_65_share)} unit="%" label="65 + share" />
            <KPI value={fmt.dec(stk.foreign_born_pct)} unit="%" label="Foreign-born" />
            <KPI value={fmt.num(stk.births_2024)} label="Births 2024" />
            <KPI value={fmt.num(stk.pop_women_15_44)} label="Women 15–44" />
            <KPI value={fmt.num(stk.pop_0_1)} label="Infants 0–1" />
          </KPIGrid>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="projection" />, 'Population projections')}
          <KPIGrid cols={2}>
            <KPI value={fmt.num(stk.pop_2040)} label="Population 2040" />
            <KPI value={fmt.num(stk.pop_65_2040)} label="65 + in 2040" />
            <KPI value={`+${Math.round(stk.growth_65_2040)}%`} label="65 + growth → 2040" tone="accent" />
            <KPI value={fmt.num(stk.pop_2050)} label="Population 2050" />
          </KPIGrid>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="budget" />, 'Healthcare budget per capita')}
          <KPIGrid cols={3}>
            <KPI value={`${Math.round(stk.grp_per_capita_ksek)}`} unit="kSEK" label="GRP / capita" />
            <KPI value={fmt.num(Math.round(stk.hc_cost_per_capita))} unit="SEK" label="HC cost / capita" />
            <KPI value={fmt.num(Math.round(stk.pharma_per_capita))} unit="SEK" label="Pharma / capita" />
            <KPI value={fmt.num(Math.round(stk.primary_care_per_capita))} unit="SEK" label="Primary care / capita" />
            <KPI value={fmt.dec(stk.pharma_pct_hc)} unit="%" label="Pharma share of HC" />
            <KPI value={Math.round(stk.vaccine_sellin_per_capita)} unit="SEK" label="Vaccine sell-in / capita" />
          </KPIGrid>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="equity" />, 'Equity indicators')}
          <KPIGrid cols={3}>
            <KPI value={Math.round(stk.premature_mortality_25_64)} unit="/100k" label="Premature mortality 25–64" />
            <KPI value={Math.round(stk.hc_amenable_mortality)} unit="/100k" label="HC-amenable mortality" />
            <KPI value={fmt.dec(stk.suicide_25plus)} unit="/100k" label="Suicide 25 +" />
            <KPI value={fmt.dec(stk.daily_smokers_pct)} unit="%" label="Daily smokers" />
            <KPI value={fmt.dec(stk.overweight_obese_pct)} unit="%" label="Overweight/obese" />
            <KPI value={`#${stk.equity_rank}`} label="Equity rank (1 = highest need)" />
          </KPIGrid>
        </div>
      </div>
      <div className="source-note">
        Sources: SCB demographics + projections, Kolada KPIs, Folkhälsomyndigheten vaccination programmes.
      </div>
    </Slide>
  )
}
