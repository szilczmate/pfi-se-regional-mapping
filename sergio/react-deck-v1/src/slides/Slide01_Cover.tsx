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
        <div style={{ marginTop: 64 }}>
          <div style={{
            fontSize: 14, fontWeight: 600, color: 'var(--accent)',
            letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 12,
          }}>
            Viti Science
          </div>
          <div style={{ fontSize: 14, color: 'var(--navy-soft)', lineHeight: 1.7 }}>
            <div>Sergio Flores · <a href="mailto:sergio.flores@vitiscience.se" style={{ color: 'var(--accent-d)', textDecoration: 'none', fontWeight: 600 }}>sergio.flores@vitiscience.se</a></div>
            <div>Máté Szilcz · <a href="mailto:mate.szilcz@vitiscience.se" style={{ color: 'var(--accent-d)', textDecoration: 'none', fontWeight: 600 }}>mate.szilcz@vitiscience.se</a> · <a href="mailto:mate.szilcz@pfizer.com" style={{ color: 'var(--accent-d)', textDecoration: 'none', fontWeight: 600 }}>mate.szilcz@pfizer.com</a></div>
          </div>
          <div style={{ fontSize: 13, color: 'var(--gray-1)', marginTop: 20 }}>
            26 June 2026
          </div>
        </div>
        <div className="cover-accent-bar" />
      </div>
    </div>
  )
}
