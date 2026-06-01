import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

function Stat({ value, unit, label, delta, note, color }: {
  value: string; unit: string; label: string; delta: string; note: string; color: string
}) {
  return (
    <div className="card card-accent" style={{ padding: '14px 16px' }}>
      <div style={{
        fontSize: 10.5, fontWeight: 700, color: 'var(--accent)',
        letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 8,
      }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{ fontSize: 34, fontWeight: 800, color: 'var(--navy)', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{value}</span>
        <span style={{ fontSize: 16, color: 'var(--accent-d)', fontWeight: 700 }}>{unit}</span>
        <span style={{ fontSize: 14, fontWeight: 800, color, marginLeft: 4 }}>{delta}</span>
      </div>
      <div style={{ fontSize: 10, color: 'var(--gray-1)', marginTop: 6, lineHeight: 1.45 }}>{note}</div>
    </div>
  )
}

export function Slide_CostDriver({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="The cost driver"
      title="Where the spend growth concentrates"
      subtitle="The fastest-growing part of the medicines bill is rare-disease and specialty therapy: high-cost treatments spread unevenly across regions. The solidarisk finansiering top-up is designed for them."
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12, paddingTop: 4 }}>

        {/* Two national-trajectory stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <Stat
            value="47.3" unit="bn SEK" delta="+18%" color="var(--accent-d)"
            label="National förmån cost by 2029"
            note="Up from 40.1 bn in 2025 (Socialstyrelsen). Rare-disease therapies are the single fastest-growing segment."
          />
          <Stat
            value="17.1" unit="bn SEK" delta="+22%" color="var(--gold)"
            label="Hospital (rekvisition) cost by 2029"
            note="Up from 14.9 bn in 2025 (Socialstyrelsen). The steeper curve sits in clinic-administered specialty medicines."
          />
        </div>

        {/* Driver + mechanism */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, flex: 1 }}>
          <div className="card" style={{ padding: '14px 16px', borderLeft: '4px solid var(--accent)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)', marginBottom: 6 }}>What is driving it</div>
              <p style={{ fontSize: 12, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
                New, often costly medicines, and more patients reaching treatment. The steepest growth sits in
                clinic-administered specialty therapy rather than everyday prescriptions.
              </p>
            </div>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--gray-1)', marginBottom: 7 }}>
                On the hospital side
              </div>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {[
                  'Cancer medicines: roughly 40% of the hospital bill',
                  'Immunoglobulins',
                  'Medicines for rare hereditary diseases',
                  'CAR-T, with cost rising in 2026',
                ].map(t => (
                  <li key={t} style={{ fontSize: 11.5, color: 'var(--navy-soft)', lineHeight: 1.4, paddingLeft: 15, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, top: 6, width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)' }} />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
            <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5, paddingTop: 9, borderTop: '1px solid var(--gray-4)' }}>
              New 2026 entrants are expected in lung cancer, haemophilia and other hereditary conditions.
            </div>
          </div>

          <div className="card" style={{ padding: '14px 16px', background: 'var(--bg-tint)', borderLeft: '4px solid var(--good)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--good)', marginBottom: 6 }}>Solidarisk finansiering</div>
              <p style={{ fontSize: 12, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
                The state tops up regions centrally so that a few high-cost rare-disease patients do not distort one
                region's budget. Access for these therapies is therefore decided nationally.
              </p>
            </div>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--gray-1)', marginBottom: 7 }}>
                A medicine qualifies when it is
              </div>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {['Costly', 'Unevenly distributed between regions', 'Documented effective'].map(t => (
                  <li key={t} style={{ fontSize: 11.5, color: 'var(--navy-soft)', lineHeight: 1.4, paddingLeft: 15, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, top: 6, width: 5, height: 5, borderRadius: '50%', background: 'var(--good)' }} />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--good)', paddingTop: 9, borderTop: '1px solid var(--gray-4)' }}>
              Qualifying threshold: cost ≥ 30 SEK per inhabitant above the national average.
            </div>
          </div>
        </div>

        {/* Engagement strip */}
        <div style={{
          padding: '10px 14px', background: 'var(--bg-soft)',
          borderLeft: '3px solid var(--accent)', borderRadius: 3,
          fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55,
        }}>
          Rare-disease and specialty
          therapy areas (ATTR, haemophilia and similar) run through national managed introduction (Track C) and the
          central top-up rather than regional budget rounds. The forum and the evidence bar are national.
        </div>
      </div>

      <div className="source-note">
        Sources: Socialstyrelsen läkemedelsförsäljning – analys och prognos 2026–2029 (national förmån and rekvisition trajectory); Överenskommelse läkemedelsförmånerna 2026 (solidarisk finansiering); Region Stockholm läkemedelsprognos 2025–2026 (driver detail).
      </div>
    </Slide>
  )
}
