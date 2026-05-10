import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

export function Slide14_Closing({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Where this could go next"
      title="From a deck to a live dashboard"
      subtitle="A short note on how this same work could continue, if it would be useful."
    >
      <div style={{
        flex: 1, display: 'grid', gridTemplateColumns: '1.1fr 1fr',
        gap: 24, alignItems: 'center', padding: '20px 0',
      }}>

        {/* Left narrative */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <p style={{ fontSize: 14, color: 'var(--navy)', lineHeight: 1.6, margin: 0 }}>
            Most of what we have just walked through is built once and then ages. Stakeholders
            change seats, NT-rådet recommendations land, agreements expire, and new products
            enter the picture, all on a quiet but constant cadence.
          </p>
          <p style={{ fontSize: 14, color: 'var(--navy-soft)', lineHeight: 1.6, margin: 0 }}>
            One natural next step would be to take the same data behind this deck and put it
            into a live dashboard that updates as the underlying registers and pages do, so
            access and field teams can consult it through the year rather than reread a deck
            quarterly.
          </p>
          <p style={{
            fontSize: 12, color: 'var(--gray-1)', lineHeight: 1.6, margin: 0,
            fontStyle: 'italic',
          }}>
            We would be glad to scope what that could look like for Pfizer Sweden, including
            what to include, how often to refresh, and where it would sit alongside the tools
            you already use.
          </p>
        </div>

        {/* Right discreet visual hint */}
        <div style={{
          display: 'flex', flexDirection: 'column', gap: 10,
          padding: '20px 24px', background: 'var(--bg-tint)',
          borderRadius: 6, border: '1px solid var(--accent-l)',
        }}>
          <div style={{
            fontSize: 11, fontWeight: 700, color: 'var(--accent-d)',
            letterSpacing: '0.08em', textTransform: 'uppercase',
          }}>
            What such a dashboard could carry
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
            {[
              ['The four-track architecture', 'kept as the persistent frame.'],
              ['A live stakeholder map', 'where seat changes are flagged as they happen.'],
              ['Per-product status', 'pulled from TLV and samverkanlakemedel.se.'],
              ['Brick-level commercial view', 'refreshed against the IQVIA data.'],
              ['The reform-signal calendar', 'with upcoming windows highlighted in advance.'],
              ['An open-status tracker', 'so verification gaps remain visible.'],
            ].map(([head, tail]) => (
              <div key={head} style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
                <span style={{
                  width: 4, height: 4, borderRadius: '50%',
                  background: 'var(--accent)', flexShrink: 0,
                  marginTop: 5,
                }} />
                <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5 }}>
                  <span style={{ color: 'var(--navy)', fontWeight: 600 }}>{head}</span>
                  {', '}
                  <span style={{ color: 'var(--gray-1)' }}>{tail}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{
        marginTop: 4, fontSize: 11, color: 'var(--gray-2)',
        textAlign: 'center', fontStyle: 'italic',
      }}>
        Thank you.
      </div>
    </Slide>
  )
}
