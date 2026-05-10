import { Slide } from '../components/Slide'
import { fmt } from '../lib/format'
import type { SlideProps } from '../types'
import BRICK from '../data/brick.json'

const TOP = (BRICK as any).top_recovery as Array<{
  brick: string; county: string; total_sek: number;
  ibrance_share: number; kisqali_share: number; verzenios_share: number;
  recovery_sek: number; quadrant: string;
}>

const TOTALS = (BRICK as any).totals as {
  total_recovery_sek: number; top15_recovery_sek: number;
  total_bricks_with_recovery: number; recovery_target_count: number;
}

export function Analysis_BrickRecovery({ isActive }: SlideProps) {
  const top15 = TOP.slice(0, 15)
  const maxRecovery = Math.max(...top15.map(b => b.recovery_sek))

  return (
    <Slide
      isActive={isActive}
      sectionLabel="Where the CDK4/6 recovery actually sits"
      title="Top 15 raw recovery opportunities · 78-brick view"
      subtitle="The 41-percentage-point Ibrance share collapse is not evenly distributed. Two-thirds of the recoverable headroom sits in fewer than twenty bricks."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: 16, overflow: 'hidden' }}>

        {/* Bar chart of top 15 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, overflow: 'auto' }}>
          {top15.map((b, i) => {
            const widthPct = (b.recovery_sek / maxRecovery) * 100
            const region = b.county.replace(/^[0-9]+ - /, '').replace(' län', '').replace('Region ', '')
            return (
              <div key={b.brick} style={{ display: 'grid', gridTemplateColumns: '24px 1fr 60px', alignItems: 'center', gap: 6, fontSize: 10.5 }}>
                <div style={{ color: 'var(--gray-1)', fontWeight: 600, textAlign: 'right' }}>#{i + 1}</div>
                <div style={{ position: 'relative', height: 22, background: 'var(--gray-5)', borderRadius: 2 }}>
                  <div style={{
                    position: 'absolute', left: 0, top: 0, bottom: 0,
                    width: `${widthPct}%`,
                    background: i < 3 ? 'var(--accent-d)' : i < 8 ? 'var(--accent)' : 'var(--accent-l)',
                    borderRadius: 2,
                  }} />
                  <div style={{
                    position: 'absolute', left: 6, top: 0, bottom: 0,
                    display: 'flex', alignItems: 'center', fontSize: 10, fontWeight: 600, color: 'var(--navy)',
                  }}>
                    {b.brick.replace(/^[0-9]+ - /, '')} <span style={{ color: 'var(--gray-1)', fontWeight: 400, marginLeft: 4 }}>· {region}</span>
                  </div>
                </div>
                <div style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontSize: 10.5, color: 'var(--navy)', fontWeight: 600 }}>
                  {(b.recovery_sek / 1000).toFixed(0)} k
                </div>
              </div>
            )
          })}
        </div>

        {/* Right side: totals + structure */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="card card-accent" style={{ padding: '12px 14px' }}>
            <div className="card-title">The numbers behind the bars</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 6 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 11 }}>
                <span style={{ color: 'var(--gray-1)' }}>Total positive recovery (78 bricks)</span>
                <span style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 14 }}>{fmt.sek(TOTALS.total_recovery_sek)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 11 }}>
                <span style={{ color: 'var(--gray-1)' }}>Top 15 raw bricks</span>
                <span style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 14 }}>{fmt.sek(TOTALS.top15_recovery_sek)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 11 }}>
                <span style={{ color: 'var(--gray-1)' }}>Strict Recovery target quadrant ({TOTALS.recovery_target_count} bricks)</span>
                <span style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 14 }}>4.04 M kr</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 11 }}>
                <span style={{ color: 'var(--gray-1)' }}>Bricks with positive headroom (of 78)</span>
                <span style={{ fontWeight: 700, color: 'var(--navy)', fontSize: 14 }}>{TOTALS.total_bricks_with_recovery}</span>
              </div>
            </div>
          </div>

          <div className="card" style={{
            padding: '12px 14px', background: 'var(--bg-tint)',
            borderLeft: '4px solid var(--accent)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-d)', marginBottom: 6 }}>
              How to read this
            </div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
              "Recovery" here is the SEK headroom that would be unlocked if Ibrance share in each brick recovered
              to a 17.5% national-average benchmark. Stockholm-S leads, but Gävle and Luleå/Boden, both far smaller
              markets in absolute terms, show up in the top three because their Ibrance share is at zero or near-zero
              against an established CDK4/6 base. The strict Recovery-target quadrant (declining Kisqali growth and
              eligible structural fit) is a tighter subset.
            </p>
          </div>
        </div>
      </div>
      <div className="source-note">
        Sources: IQVIA Sell-In CDK4/6 brick aggregation (78 active bricks, 3-yr); benchmark = 17.5% Ibrance share of national CDK4/6 SEK Oct 2025–Mar 2026.
      </div>
    </Slide>
  )
}
