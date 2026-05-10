import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import ATTR from '../data/attr.json'

const SVR_DATA = ATTR as Record<string, {
  PN_per100k: number; CM_per100k: number; PN_idx: number; CM_idx: number;
}>

const ORDER = ['Norrland', 'Stockholm Sörmland', 'VGR', 'Mellansverige', 'Södra', 'Sydöstra']

export function Analysis_ATTRConcentration({ isActive }: SlideProps) {
  const maxPN = Math.max(...Object.values(SVR_DATA).map(v => v.PN_per100k))
  const maxCM = Math.max(...Object.values(SVR_DATA).map(v => v.CM_per100k))

  return (
    <Slide
      isActive={isActive}
      sectionLabel="ATTR concentration"
      title="The northern V30M cluster — 7.6× the national rate"
      subtitle="ATTR-PN incidence in Norrland over-indexes 7.6× the national rate; ATTR-CM is more evenly distributed. The asymmetry is the entire reason a Northern Cornerstone strategy exists."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, overflow: 'hidden' }}>

        {/* Left: ATTR-PN bar chart */}
        <div className="card card-accent" style={{ padding: '14px 16px' }}>
          <div className="card-title">ATTR-PN incidence per 100k · by sjukvårdsregion</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
            {ORDER.map(svr => {
              const v = SVR_DATA[svr]
              if (!v) return null
              const pct = (v.PN_per100k / maxPN) * 100
              const isNorth = svr === 'Norrland'
              return (
                <div key={svr} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 60px', alignItems: 'center', gap: 8 }}>
                  <div style={{ fontSize: 10.5, color: 'var(--navy)', fontWeight: isNorth ? 700 : 500 }}>{svr}</div>
                  <div style={{ position: 'relative', height: 22, background: 'var(--gray-5)', borderRadius: 2 }}>
                    <div style={{
                      position: 'absolute', left: 0, top: 0, bottom: 0,
                      width: `${pct}%`,
                      background: isNorth ? 'var(--accent-d)' : 'var(--accent-l)',
                      borderRadius: 2,
                    }} />
                  </div>
                  <div style={{ textAlign: 'right', fontSize: 11, color: 'var(--navy)', fontWeight: isNorth ? 700 : 500, fontVariantNumeric: 'tabular-nums' }}>
                    {v.PN_per100k.toFixed(2)}
                  </div>
                </div>
              )
            })}
          </div>
          <p style={{ fontSize: 10, color: 'var(--gray-1)', lineHeight: 1.55, marginTop: 12, marginBottom: 0 }}>
            Norrland's ATTR-PN index is 758 against a national 100, driven by the V30M founder cluster
            historically associated with the Skellefteå/Piteå area. Norrlands universitetssjukhus in Umeå
            is the Swedish reference centre.
          </p>
        </div>

        {/* Right: ATTR-CM bar chart */}
        <div className="card" style={{ padding: '14px 16px', borderLeft: '4px solid var(--gray-2)' }}>
          <div className="card-title" style={{ color: 'var(--navy-soft)' }}>
            ATTR-CM incidence per 100k · by sjukvårdsregion
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
            {ORDER.map(svr => {
              const v = SVR_DATA[svr]
              if (!v) return null
              const pct = (v.CM_per100k / maxCM) * 100
              return (
                <div key={svr} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 60px', alignItems: 'center', gap: 8 }}>
                  <div style={{ fontSize: 10.5, color: 'var(--navy)' }}>{svr}</div>
                  <div style={{ position: 'relative', height: 22, background: 'var(--gray-5)', borderRadius: 2 }}>
                    <div style={{
                      position: 'absolute', left: 0, top: 0, bottom: 0,
                      width: `${pct}%`,
                      background: 'var(--gray-2)',
                      borderRadius: 2,
                    }} />
                  </div>
                  <div style={{ textAlign: 'right', fontSize: 11, color: 'var(--navy)', fontVariantNumeric: 'tabular-nums' }}>
                    {v.CM_per100k.toFixed(2)}
                  </div>
                </div>
              )
            })}
          </div>
          <p style={{ fontSize: 10, color: 'var(--gray-1)', lineHeight: 1.55, marginTop: 12, marginBottom: 0 }}>
            ATTR-CM (cardiomyopathy) is far more evenly distributed. Södra actually leads on per-100k
            incidence (older population structure), while Norrland sits below the national average.
            Vyndaqel's Swedish patient pool spans both populations.
          </p>
        </div>
      </div>

      <div style={{
        marginTop: 12, padding: '10px 14px', background: 'var(--bg-tint)',
        borderLeft: '3px solid var(--accent)', borderRadius: 4,
        fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55,
      }}>
        <strong style={{ color: 'var(--navy)' }}>Why this matters for engagement.</strong> A Northern Cornerstone
        framing is justified by ATTR-PN concentration in the V30M cluster, not by ATTR-CM distribution.
        NT-rådet's national collaboration for Vyndaqel was archived on 2 September 2025, with treatment
        recommendation work moving to NAG LOK. The northern sjukvårdsregion infrastructure, anchored at the
        Umeå reference centre and represented in the NSG and NT-rådet structures, is the operative engagement
        environment for ATTR work going forward.
      </div>
      <div className="source-note">
        Sources: AVA Vyndaqel proxy aggregated to sjukvårdsregion level; per-100k indexed against national rate (national = 100).
      </div>
    </Slide>
  )
}
