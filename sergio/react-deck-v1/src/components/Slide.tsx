import type { ReactNode, CSSProperties } from 'react'

interface SlideProps {
  isActive: boolean
  sectionLabel?: string
  title?: ReactNode
  subtitle?: ReactNode
  source?: string
  footCenter?: string
  footBrand?: string
  bodyStyle?: CSSProperties
  children: ReactNode
}

/**
 * Pfizer Sweden Mapping — slide shell.
 * Provides topbar (4px accent), conf-strip, body container, and foot.
 * Use this as the wrapper for every slide.
 */
export function Slide({
  isActive,
  sectionLabel,
  title,
  subtitle,
  source = '',
  footCenter = 'Internal Use Only',
  footBrand = 'Viti Science',
  bodyStyle,
  children,
}: SlideProps) {
  return (
    <div className={`slide${isActive ? ' active' : ''}`}>
      <div className="topbar" />
      <div className="conf-strip">Confidential — General Business</div>
      <div className="body" style={bodyStyle}>
        {sectionLabel && <div className="section-label">{sectionLabel}</div>}
        {title && <div className="slide-title">{title}</div>}
        {subtitle && <div className="slide-subtitle">{subtitle}</div>}
        {children}
      </div>
      <div className="foot">
        <span>{source}</span>
        <span className="center">{footCenter}</span>
        <span className="brand">{footBrand}</span>
      </div>
    </div>
  )
}
