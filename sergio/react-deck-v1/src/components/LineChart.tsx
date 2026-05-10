interface Series {
  name: string
  color: string
  values: number[]
}

interface Props {
  series: Series[]
  xLabels?: string[]
  width?: number
  height?: number
  title?: string
  yAxisLabel?: string
  showLegend?: boolean
}

/**
 * Multi-series line chart for vaccine trends (slide 13/24) and product trajectories.
 * Pure SVG, no external deps.
 */
export function LineChart({
  series,
  xLabels = [],
  width = 240,
  height = 110,
  title,
  yAxisLabel,
  showLegend = true,
}: Props) {
  if (!series || series.length === 0) return null
  const maxLen = Math.max(...series.map(s => s.values.length))
  const allValues = series.flatMap(s => s.values).filter(v => v != null && !isNaN(v))
  if (allValues.length === 0) return null

  const yMax = Math.max(...allValues)
  const yMin = Math.min(...allValues, 0)
  const yRange = yMax - yMin || 1
  const padL = 28
  const padR = 8
  const padT = title ? 16 : 4
  const padB = 22
  const plotW = width - padL - padR
  const plotH = height - padT - padB
  const xStep = plotW / Math.max(maxLen - 1, 1)

  const yScale = (v: number) => padT + plotH - ((v - yMin) / yRange) * plotH

  return (
    <svg width={width} height={height + (showLegend ? 16 : 0)}>
      {title && (
        <text x={padL} y={12} fontSize={9.5} fontWeight={600} fill="var(--navy)">
          {title}
        </text>
      )}
      {/* Y axis baseline */}
      <line
        x1={padL}
        x2={padL + plotW}
        y1={padT + plotH}
        y2={padT + plotH}
        stroke="var(--gray-3)"
        strokeWidth={0.8}
      />
      {/* Y axis labels (top + 0) */}
      <text x={padL - 4} y={padT + 4} fontSize={8} fill="var(--gray-1)" textAnchor="end">
        {Math.round(yMax)}
      </text>
      <text x={padL - 4} y={padT + plotH - 1} fontSize={8} fill="var(--gray-1)" textAnchor="end">
        0
      </text>
      {/* X axis tick labels (first + middle + last) */}
      {xLabels.length > 0 && (
        <>
          <text x={padL} y={height - 8} fontSize={8} fill="var(--gray-1)" textAnchor="start">
            {xLabels[0]}
          </text>
          {xLabels.length > 2 && (
            <text x={padL + plotW / 2} y={height - 8} fontSize={8} fill="var(--gray-1)" textAnchor="middle">
              {xLabels[Math.floor(xLabels.length / 2)]}
            </text>
          )}
          <text x={padL + plotW} y={height - 8} fontSize={8} fill="var(--gray-1)" textAnchor="end">
            {xLabels[xLabels.length - 1]}
          </text>
        </>
      )}
      {/* Series lines */}
      {series.map(s => {
        const points = s.values.map((v, i) =>
          `${(padL + i * xStep).toFixed(1)},${yScale(v).toFixed(1)}`
        ).join(' ')
        const lastIdx = s.values.length - 1
        const last = s.values[lastIdx]
        return (
          <g key={s.name}>
            <polyline
              points={points}
              fill="none"
              stroke={s.color}
              strokeWidth={1.6}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {/* End marker */}
            <circle
              cx={padL + lastIdx * xStep}
              cy={yScale(last)}
              r={2.5}
              fill={s.color}
            />
            {/* End value label */}
            <text
              x={padL + lastIdx * xStep + 4}
              y={yScale(last) - 4}
              fontSize={8}
              fill={s.color}
              fontWeight={600}
            >
              {Math.round(last)}
            </text>
          </g>
        )
      })}
      {yAxisLabel && (
        <text
          transform={`translate(8,${padT + plotH / 2}) rotate(-90)`}
          fontSize={8}
          fill="var(--gray-1)"
          textAnchor="middle"
        >
          {yAxisLabel}
        </text>
      )}
      {/* Legend */}
      {showLegend && (
        <g transform={`translate(${padL},${height + 6})`}>
          {series.map((s, i) => (
            <g key={s.name} transform={`translate(${i * 80},0)`}>
              <line x1={0} x2={10} y1={4} y2={4} stroke={s.color} strokeWidth={1.6} />
              <text x={14} y={7} fontSize={9} fill="var(--navy-soft)">{s.name}</text>
            </g>
          ))}
        </g>
      )}
    </svg>
  )
}
