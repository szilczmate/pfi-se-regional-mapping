import type { SlideProps } from '../types'

export function Slide01_Cover({ isActive }: SlideProps) {
  return (
    <div className={`slide${isActive ? ' active' : ''}`}>
      <div className="topbar" />
      <div className="conf-strip">Confidential — General Business · Pfizer Sweden + Viti Science only</div>
      <div className="cover-bg">
        <div className="cover-title">Pfizer Sweden Regional Landscape Mapping</div>
        <div className="cover-sub">
          Who decides on regional access, what shapes their priorities,
          the evidence they use, and where Pfizer can lift the right questions.
        </div>
        <div style={{
          marginTop: 80, fontSize: 14, fontWeight: 600,
          color: 'var(--accent)', letterSpacing: '0.08em', textTransform: 'uppercase',
        }}>
          Viti Science
        </div>
        <div className="cover-accent-bar" />
      </div>
    </div>
  )
}
