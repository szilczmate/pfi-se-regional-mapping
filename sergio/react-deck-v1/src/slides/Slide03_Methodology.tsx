import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const STAGES = [
  {
    n: '1',
    label: 'Frame',
    body: 'The four-track decision architecture as the organising principle.',
    color: 'var(--track-a)',
    soft: 'var(--track-a-soft)',
  },
  {
    n: '2',
    label: 'Map',
    body: '21 regions × 7 roles, plus the three national bodies. 12 products positioned against the four tracks.',
    color: 'var(--track-b)',
    soft: 'var(--track-b-soft)',
  },
  {
    n: '3',
    label: 'Analyse',
    body: 'Brick-level commercial decomposition, patient-level depth where AVA gives it, regional archetypes.',
    color: 'var(--track-c)',
    soft: 'var(--track-c-soft)',
  },
  {
    n: '4',
    label: 'Verify',
    body: 'One workbook, every figure reconciles. Confidence tagged per claim. Open items flagged.',
    color: 'var(--accent)',
    soft: 'var(--accent-xl)',
  },
]

const SOURCES = [
  ['IQVIA Sell-In', 'commercial backbone'],
  ['AVA', 'patient-level depth'],
  ['TLV · NT-rådet', 'access decisions'],
  ['SCB · Kolada · FoHM', 'regional context'],
]

export function Slide03_Methodology({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Method"
      title="How the work was done"
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', paddingTop: 20, paddingBottom: 8 }}>

        {/* Four-stage flow */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, position: 'relative' }}>
          {/* Connecting line */}
          <div style={{
            position: 'absolute',
            top: 36, left: '12.5%', right: '12.5%',
            height: 2, background: 'linear-gradient(90deg, var(--track-a), var(--track-b), var(--track-c), var(--accent))',
            opacity: 0.25, zIndex: 0,
          }} />

          {STAGES.map(s => (
            <div key={s.n} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', zIndex: 1 }}>
              <div style={{
                width: 72, height: 72, borderRadius: '50%',
                background: s.soft, border: `2px solid ${s.color}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 12,
              }}>
                <span style={{ fontSize: 28, fontWeight: 800, color: s.color, lineHeight: 1 }}>{s.n}</span>
              </div>
              <div style={{
                fontSize: 14, fontWeight: 700, color: 'var(--navy)',
                letterSpacing: '0.04em', marginBottom: 8, textTransform: 'uppercase',
              }}>
                {s.label}
              </div>
              <p style={{
                fontSize: 11.5, color: 'var(--navy-soft)', lineHeight: 1.55,
                margin: 0, textAlign: 'center', padding: '0 8px',
              }}>
                {s.body}
              </p>
            </div>
          ))}
        </div>

        {/* Source spine — minimal strip */}
        <div style={{
          marginTop: 20, padding: '14px 20px', background: 'var(--bg-tint)',
          borderRadius: 4, display: 'flex', justifyContent: 'space-around',
          alignItems: 'center', gap: 16,
        }}>
          {SOURCES.map(([src, role], i) => (
            <div key={src} style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1, justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--navy)', marginBottom: 2 }}>
                  {src}
                </div>
                <div style={{ fontSize: 9.5, color: 'var(--gray-1)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {role}
                </div>
              </div>
              {i < SOURCES.length - 1 && (
                <div style={{ width: 1, height: 32, background: 'var(--gray-3)' }} />
              )}
            </div>
          ))}
        </div>
      </div>
    </Slide>
  )
}
