import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

interface Body {
  name: string
  swedish: string
  oneLiner: string
  color: string
  track: string
  remit: string
  decides: string
}

const BODIES: Body[] = [
  {
    name: 'NT-rådet',
    swedish: 'Rådet för nya terapier',
    oneLiner: 'SKR-convened advisory council · one rep per sjukvårdsregion + secretariat',
    color: 'var(--track-c)',
    track: 'Track C · national managed introduction',
    remit: 'Decides whether a new high-impact medicine enters national collaboration, then issues a recommendation in the four-phrase language (bör använda · kan använda · bör avstå · avvakta) with an implementation strategy: patient subgroups, sequencing, restrictions.',
    decides: 'Weighs the per-patient cost-effectiveness TLV establishes, alongside disease severity, evidence certainty, rarity and aggregate budget impact. Reaches the Track B hospital products TLV never covers. Not legally binding, but followed in practice.',
  },
  {
    name: 'NSG Läkemedel',
    swedish: 'Nationell samverkansgrupp Läkemedel',
    oneLiner: 'Clinical-strategy representatives from the six sjukvårdsregioner',
    color: 'var(--accent)',
    track: 'National clinical-strategy coordination',
    remit: 'Coordinates national clinical-strategy and signal-setting across the sjukvårdsregioner. Commissions the nationella arbetsgrupper (NAG LOK and its peers) that write the treatment recommendations clinics follow.',
    decides: 'Signals which therapy areas get strategic attention before anything becomes a formal recommendation. The earliest forum where a conversation can land.',
  },
  {
    name: 'Läkemedelskommittéer',
    swedish: '21 regional drugs & therapeutics committees',
    oneLiner: 'One per region · independent formulary authority',
    color: 'var(--track-d)',
    track: 'Track D · sub-regional implementation',
    remit: 'Publishes the regional rekommendationslista (Janusinfo, Skånelistan, …), localises NT-rådet recommendations, and stewards evidence quality on new entrants. The final step before access.',
    decides: 'Effectively binding within the region; specialist chefläkare hold the final prescribing call. Where a national recommendation becomes local practice, or does not.',
  },
]

export function Slide_GovernanceRemits({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Part B · The stakeholders"
      title="What each governance body decides"
      subtitle="Two national bodies shape access; the 21 regional committees make the final call."
    >
      <div className="gov-grid">
        {BODIES.map(b => (
          <div className="gov-card" key={b.name} style={{ borderTop: `3px solid ${b.color}` }}>
            <div className="gov-card-header">
              <div className="gov-card-title">{b.name}</div>
              <div className="gov-card-subtitle">{b.swedish} · {b.oneLiner}</div>
            </div>
            <div className="gov-card-body" style={{ display: 'flex', flexDirection: 'column', gap: 16, paddingTop: 4 }}>
              <span style={{
                alignSelf: 'flex-start', fontSize: 8.5, fontWeight: 700,
                letterSpacing: '0.05em', textTransform: 'uppercase',
                color: b.color, background: 'var(--bg-soft)',
                border: `1px solid ${b.color}`, padding: '2px 7px', borderRadius: 8,
              }}>
                {b.track}
              </span>

              <div>
                <div style={{
                  fontSize: 9, fontWeight: 700, color: 'var(--gray-1)',
                  letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 3,
                }}>
                  Remit
                </div>
                <p style={{ fontSize: 11.5, color: 'var(--navy-soft)', lineHeight: 1.6, margin: 0 }}>
                  {b.remit}
                </p>
              </div>

              <div>
                <div style={{
                  fontSize: 9, fontWeight: 700, color: 'var(--gray-1)',
                  letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 3,
                }}>
                  In practice
                </div>
                <p style={{ fontSize: 11.5, color: 'var(--navy-soft)', lineHeight: 1.6, margin: 0 }}>
                  {b.decides}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: 12, padding: '8px 14px', background: 'var(--bg-soft)',
        borderLeft: '3px solid var(--accent)', borderRadius: 3,
        fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55,
      }}>
        <strong style={{ color: 'var(--navy)' }}>How they relate.</strong> NSG coordinates clinical
        strategy, NT-rådet issues the national recommendation, and the 21 läkemedelskommittéer
        decide what reaches patients. A product can clear the national step and still stall
        regionally.
      </div>

      <div className="source-note">
        Sources: samverkanlakemedel.se, SKR, regional läkemedelskommittéer.
      </div>
    </Slide>
  )
}
