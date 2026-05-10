/**
 * Tiny SVG icon set. All icons render at 16x16 by default; pass `size` to override.
 * Used in KPI card headers to give visual scaffolding without text.
 */
interface Props {
  name:
    | 'people' | 'projection' | 'budget' | 'equity'
    | 'cancer' | 'virus' | 'pipeline' | 'heart'
    | 'governance' | 'product' | 'calendar' | 'priority'
  size?: number
  color?: string
}

export function Icon({ name, size = 16, color = 'currentColor' }: Props) {
  const stroke = color
  const fill = 'none'
  const sw = 1.7

  const paths: Record<Props['name'], React.ReactNode> = {
    people: (
      <>
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </>
    ),
    projection: (
      <>
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
        <polyline points="17 6 23 6 23 12" />
      </>
    ),
    budget: (
      <>
        <line x1="12" y1="20" x2="12" y2="10" />
        <line x1="18" y1="20" x2="18" y2="4" />
        <line x1="6" y1="20" x2="6" y2="16" />
      </>
    ),
    equity: (
      <>
        <path d="M16 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z" />
        <path d="M2 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z" />
        <path d="M7 21h10" />
        <path d="M12 3v18" />
        <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2" />
      </>
    ),
    cancer: (
      <>
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="12" r="3" />
        <line x1="12" y1="3" x2="12" y2="6" />
        <line x1="12" y1="18" x2="12" y2="21" />
        <line x1="3" y1="12" x2="6" y2="12" />
        <line x1="18" y1="12" x2="21" y2="12" />
      </>
    ),
    virus: (
      <>
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="2" x2="12" y2="6" />
        <line x1="12" y1="18" x2="12" y2="22" />
        <line x1="2" y1="12" x2="6" y2="12" />
        <line x1="18" y1="12" x2="22" y2="12" />
        <line x1="5" y1="5" x2="7.5" y2="7.5" />
        <line x1="16.5" y1="16.5" x2="19" y2="19" />
        <line x1="5" y1="19" x2="7.5" y2="16.5" />
        <line x1="16.5" y1="7.5" x2="19" y2="5" />
      </>
    ),
    pipeline: (
      <>
        <path d="M9 11H5a2 2 0 0 0-2 2v3c0 1.1.9 2 2 2h4M15 11h4a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-4" />
        <path d="M9 11V8a3 3 0 0 1 6 0v3" />
        <line x1="9" y1="13" x2="15" y2="13" />
        <line x1="9" y1="16" x2="15" y2="16" />
      </>
    ),
    heart: (
      <>
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </>
    ),
    governance: (
      <>
        <rect x="3" y="11" width="18" height="10" rx="1" />
        <polyline points="3 11 12 3 21 11" />
        <line x1="7" y1="15" x2="7" y2="21" />
        <line x1="12" y1="15" x2="12" y2="21" />
        <line x1="17" y1="15" x2="17" y2="21" />
      </>
    ),
    product: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),
    calendar: (
      <>
        <rect x="3" y="4" width="18" height="18" rx="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </>
    ),
    priority: (
      <>
        <line x1="4" y1="22" x2="4" y2="15" />
        <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
      </>
    ),
  }

  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={stroke} strokeWidth={sw}
         strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
      {paths[name]}
    </svg>
  )
}
