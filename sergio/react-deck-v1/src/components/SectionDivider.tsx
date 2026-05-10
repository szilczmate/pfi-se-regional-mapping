import type { SlideProps } from '../types'

interface Props extends SlideProps {
  number: string
  title: string
  subtitle?: string
}

/**
 * Section divider — a clean full-bleed slide marking the start of a new section.
 * Used between Open / National mapping / Stockholm / Analysis / Close.
 */
export function SectionDivider({ isActive, number, title, subtitle }: Props) {
  return (
    <div className={`slide${isActive ? ' active' : ''}`}>
      <div className="topbar" />
      <div className="conf-strip">Confidential — General Business</div>
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
        padding: '0 100px',
        background: 'linear-gradient(135deg, #FAFCFD 0%, #F0FAFE 100%)',
        position: 'relative',
      }}>
        <div style={{
          fontSize: 14, letterSpacing: '0.2em', color: 'var(--accent)',
          fontWeight: 600, textTransform: 'uppercase', marginBottom: 18,
        }}>
          Section {number}
        </div>
        <div style={{
          fontSize: 56, fontWeight: 800, color: 'var(--navy)',
          lineHeight: 1.05, marginBottom: 18, maxWidth: 900,
        }}>
          {title}
        </div>
        {subtitle && (
          <div style={{
            fontSize: 18, color: 'var(--navy-soft)', lineHeight: 1.5,
            maxWidth: 800, fontWeight: 400,
          }}>
            {subtitle}
          </div>
        )}
        <div style={{
          position: 'absolute', bottom: 0, left: 0,
          width: 250, height: 6, background: 'var(--accent)',
        }} />
      </div>
      <div className="foot">
        <span></span>
        <span className="center">Internal Use Only</span>
        <span className="brand">Viti Science</span>
      </div>
    </div>
  )
}
