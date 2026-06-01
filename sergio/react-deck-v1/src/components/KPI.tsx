import type { ReactNode } from 'react'

interface Props {
  value: ReactNode
  label: ReactNode
  unit?: string
  sub?: ReactNode
  tone?: 'default' | 'accent' | 'warn' | 'good'
}

const toneStyle: Record<string, React.CSSProperties> = {
  default: {},
  accent: { borderLeft: '3px solid var(--accent)' },
  warn: { borderLeft: '3px solid var(--warn)' },
  good: { borderLeft: '3px solid var(--good)' },
}

export function KPI({ value, label, unit, sub, tone = 'default' }: Props) {
  return (
    <div className="kpi" style={toneStyle[tone]}>
      <div className="kpi-value">
        {value}
        {unit && <span style={{ fontSize: '13px', color: 'var(--gray-1)', fontWeight: 500, marginLeft: 3 }}>{unit}</span>}
      </div>
      <div className="kpi-label">{label}</div>
      {sub && <div style={{ fontSize: 9, color: 'var(--gray-2)', marginTop: 2, fontVariantNumeric: 'tabular-nums' }}>{sub}</div>}
    </div>
  )
}

interface GridProps {
  cols: 2 | 3 | 4
  children: ReactNode
}

export function KPIGrid({ cols, children }: GridProps) {
  return <div className={`kpi-grid cols-${cols}`}>{children}</div>
}
