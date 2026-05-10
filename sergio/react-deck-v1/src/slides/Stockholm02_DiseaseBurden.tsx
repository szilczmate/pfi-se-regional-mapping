import { Slide } from '../components/Slide'
import { KPI, KPIGrid } from '../components/KPI'
import { Icon } from '../components/Icon'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'

const stk: any = (DATA as any[]).find(d => d.region === 'Region Stockholm')

const cardHeader = (icon: React.ReactNode, title: string) => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: 8,
    fontSize: 13, fontWeight: 700, color: 'var(--navy)',
    letterSpacing: '0.04em', marginBottom: 8, textTransform: 'uppercase',
  }}>
    <span style={{ color: 'var(--accent)' }}>{icon}</span>
    <span>{title}</span>
  </div>
)

export function Stockholm02_DiseaseBurden({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — disease burden"
      title="The conditions Pfizer's portfolio is positioned against"
      subtitle="Cancer, infectious disease, cardiovascular and rare-disease epidemiology in the Stockholm region."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, alignContent: 'start' }}>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="cancer" />, 'Cancer burden')}
          <KPIGrid cols={3}>
            <KPI value={Math.round(stk.breast_ca_rate)} unit="/100k" label="Breast cancer" />
            <KPI value={Math.round(stk.prostate_ca_rate)} unit="/100k" label="Prostate cancer" />
            <KPI value={Math.round(stk.lung_ca_incidence)} unit="/100k" label="Lung cancer" />
            <KPI value={`~${fmt.num(Math.round(stk.breast_implied_cases))}`} label="Implied breast cases" tone="accent" />
            <KPI value={`~${fmt.num(Math.round(stk.prostate_implied_cases))}`} label="Implied prostate cases" tone="accent" />
            <KPI value={`~${fmt.num(Math.round(stk.lung_implied_cases))}`} label="Implied lung cases" tone="accent" />
          </KPIGrid>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="virus" />, 'Infectious disease epidemiology')}
          <KPIGrid cols={3}>
            <KPI value={fmt.num(stk.tbe_cases_2025)} label="TBE cases 2025" />
            <KPI value={fmt.dec(stk.tbe_per100k_2025)} unit="/100k" label="TBE incidence" />
            <KPI value={fmt.num(stk.ipd_cases_2025)} label="IPD cases 2025" />
            <KPI value={fmt.dec(stk.ipd_per100k_2025)} unit="/100k" label="IPD incidence" />
            <KPI value={Math.round(stk.antibiotic_rx_per1000)} unit="/1000" label="Antibiotic Rx" />
            <KPI value={fmt.dec(stk.mpr_2yo_pct)} unit="%" label="MPR 2 yo coverage" />
          </KPIGrid>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="pipeline" />, 'Pipeline therapeutic areas')}
          <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: '4px 0 0 0' }}>
            The {fmt.dec(stk.overweight_obese_pct)}% overweight or obese share gives the cardiometabolic addressable
            population for future Pfizer pipeline entry. Prostate cancer at {fmt.dec(stk.prostate_ca_rate)}/100k
            and roughly {fmt.num(Math.round(stk.prostate_implied_cases))} implied cases makes Talzenna's
            BRCA-mutated subset reach scale here. Lung cancer at {fmt.dec(stk.lung_ca_incidence)}/100k and
            roughly {fmt.num(Math.round(stk.lung_implied_cases))} implied cases is where the Lorviqua ALK-positive
            subset opportunity sits.
          </p>
        </div>

        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          {cardHeader(<Icon name="heart" />, 'Cardiovascular and rare disease')}
          <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: '4px 0 6px 0' }}>
            <strong>Cardiovascular.</strong> MI incidence {Math.round(stk.mi_incidence)}/100k, prevalence
            {' '}{Math.round(stk.mi_prevalence)}/100k, regional heart-care quality
            {' '}{fmt.dec(stk.heart_care_quality)}/100.
          </p>
          <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
            <strong>ATTR.</strong> Stockholm sits inside the national amyloid referral network —
            ATTR-CM concentration here travels through Karolinska. The northern V30M founder cluster
            (predominantly polyneuropathy) is anchored at Norrlands universitetssjukhus in Umeå, not Stockholm.
          </p>
          <p style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55, margin: '6px 0 0 0' }}>
            <strong>Haemophilia.</strong> Stockholm has the largest haemophilia market in Sweden by SEK,
            making Karolinska the natural commercial-launch infrastructure for Hympavzi once its access
            route is established.
          </p>
        </div>
      </div>
      <div className="source-note">
        Sources: Socialstyrelsen cancer registers, RCC, Folkhälsomyndigheten epidemiology, regional reference-centre patterns.
      </div>
    </Slide>
  )
}
