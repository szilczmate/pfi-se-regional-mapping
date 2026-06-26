import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const STAGES = [
  {
    n: '1',
    label: 'Frame',
    body: 'The four-track decision architecture (five with vaccines) as the organising principle.',
    color: 'var(--track-a)',
    soft: 'var(--track-a-soft)',
  },
  {
    n: '2',
    label: 'Map',
    body: '21 regions × 5 roles, plus the three national bodies: who holds each access decision and who governs around them.',
    color: 'var(--track-b)',
    soft: 'var(--track-b-soft)',
  },
  {
    n: '3',
    label: 'Analyse',
    body: 'Each region on the same dimensions (demographics, equity, budget and disease burden), read against the priorities its decision-makers act on.',
    color: 'var(--track-c)',
    soft: 'var(--track-c-soft)',
  },
  {
    n: '4',
    label: 'Verify',
    body: 'One workbook in which every figure reconciles, with each claim confidence-tagged and open items flagged.',
    color: 'var(--accent)',
    soft: 'var(--accent-xl)',
  },
]

const SOURCES = [
  ['TLV · NT-rådet', 'access decisions'],
  ['SKR', 'budget & spend'],
  ['SCB · Kolada · FoHM', 'regional context'],
  ['Socialstyrelsen', 'guidance & forecasts'],
]

export function Slide03_Methodology({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Method"
      title="How the work was done"
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 80, paddingTop: 8, paddingBottom: 8 }}>

        {/* Four-stage flow */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, position: 'relative' }}>
          {/* Connecting line */}
          <div style={{
            position: 'absolute',
            top: 48, left: '12.5%', right: '12.5%',
            height: 2, background: 'linear-gradient(90deg, var(--track-a), var(--track-b), var(--track-c), var(--accent))',
            opacity: 0.25, zIndex: 0,
          }} />

          {STAGES.map(s => (
            <div key={s.n} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', zIndex: 1 }}>
              <div style={{
                width: 96, height: 96, borderRadius: '50%',
                background: s.soft, border: `2px solid ${s.color}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 16,
              }}>
                <span style={{ fontSize: 40, fontWeight: 800, color: s.color, lineHeight: 1 }}>{s.n}</span>
              </div>
              <div style={{
                fontSize: 15, fontWeight: 700, color: 'var(--navy)',
                letterSpacing: '0.04em', marginBottom: 10, textTransform: 'uppercase',
              }}>
                {s.label}
              </div>
              <p style={{
                fontSize: 13, color: 'var(--navy-soft)', lineHeight: 1.6,
                margin: 0, textAlign: 'center', padding: '0 6px',
              }}>
                {s.body}
              </p>
            </div>
          ))}
        </div>

        {/* Source spine — minimal strip */}
        <div style={{
          marginTop: 0, padding: '18px 24px', background: 'var(--bg-tint)',
          borderRadius: 4, display: 'flex', justifyContent: 'space-around',
          alignItems: 'center', gap: 16,
        }}>
          {SOURCES.map(([src, role], i) => (
            <div key={src} style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1, justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy)', marginBottom: 3 }}>
                  {src}
                </div>
                <div style={{ fontSize: 10.5, color: 'var(--gray-1)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {role}
                </div>
              </div>
              {i < SOURCES.length - 1 && (
                <div style={{ width: 1, height: 40, background: 'var(--gray-3)' }} />
              )}
            </div>
          ))}
        </div>
      </div>
      <div className="source-note">
        Data protection: personal data shown (names, public roles, party affiliation) relates solely to individuals’
        official public functions and is drawn from public regional and national sources or registers. Processed under
        legitimate interest (GDPR Art. 6(1)(f)) for stakeholder mapping; no private contact details are included. Queries
        or removal requests should be sent to: mate.szilcz@vitiscience.se.
      </div>
    </Slide>
  )
}
