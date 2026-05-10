interface Props {
  values: number[]
  width?: number
  height?: number
  color?: string
  showEndpoints?: boolean
}

/**
 * Inline mini line chart for table cells (slide 23 trendline column etc.).
 * Auto-scales Y to fit the value range.
 */
export function Sparkline({
  values,
  width = 80,
  height = 22,
  color,
  showEndpoints = true,
}: Props) {
  if (!values || values.length < 2) {
    return <span style={{ fontSize: 9, color: 'var(--gray-2)' }}>—</span>
  }

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const xStep = (width - 4) / (values.length - 1)

  // Determine trend color if not specified
  const slope = values[values.length - 1] - values[0]
  const autoColor = color
    || (slope > range * 0.05 ? 'var(--good)'
      : slope < -range * 0.05 ? 'var(--warn)'
      : 'var(--gray-1)')

  const points = values.map((v, i) => {
    const x = 2 + i * xStep
    const y = height - 2 - ((v - min) / range) * (height - 4)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')

  const last = values[values.length - 1]
  const first = values[0]

  return (
    <svg width={width} height={height} style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <polyline
        points={points}
        fill="none"
        stroke={autoColor}
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {showEndpoints && (
        <>
          <circle
            cx={2}
            cy={height - 2 - ((first - min) / range) * (height - 4)}
            r={1.8}
            fill={autoColor}
            opacity={0.5}
          />
          <circle
            cx={width - 2}
            cy={height - 2 - ((last - min) / range) * (height - 4)}
            r={2.2}
            fill={autoColor}
          />
        </>
      )}
    </svg>
  )
}
