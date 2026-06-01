import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import DATA from '../data/data.json'
import PFIZER_MONTHLY from '../data/pfizer_monthly.json'

const stk: any = (DATA as any[]).find(d => d.region === 'Region Stockholm')
const monthly: Record<string, Array<[string, number]>> = (PFIZER_MONTHLY as any).stockholm || {}

interface Item {
  label: string
  sek: number
  growthPct: number
  note?: string
}

function trend(name: string): number | null {
  const series = monthly[name]
  if (!series || series.length < 12) return null
  const last6 = series.slice(-6).reduce((s, [, v]) => s + v, 0)
  const prev6 = series.slice(-12, -6).reduce((s, [, v]) => s + v, 0)
  if (!prev6) return null
  return ((last6 - prev6) / prev6) * 100
}

const ITEMS: Item[] = ([
  { key: 'vyndaqel', label: 'Vyndaqel', monthlyKey: 'Vyndaqel' },
  { key: 'xtandi', label: 'Xtandi', monthlyKey: 'Xtandi' },
  { key: 'elrexfio', label: 'Elrexfio', monthlyKey: 'Elrexfio' },
  { key: 'ibrance', label: 'Ibrance', monthlyKey: 'Ibrance' },
  { key: 'lorviqua', label: 'Lorviqua', monthlyKey: 'Lorviqua' },
  { key: 'vydura', label: 'Vydura', monthlyKey: 'Vydura' },
  { key: 'tukysa', label: 'Tukysa', monthlyKey: 'Tukysa' },
  { key: 'talzenna', label: 'Talzenna', monthlyKey: 'Talzenna' },
] as Array<{ key: string; label: string; monthlyKey: string; note?: string }>).map(p => {
  const sek = (stk as any)[p.key] || 0
  const g = trend(p.monthlyKey)
  return { label: p.label, sek, growthPct: g ?? 0, note: p.note }
}).filter(i => i.sek > 0)

const Y_MAX = 60   // % growth cap
const Y_MIN = -60
const X_LABEL_MAX = Math.max(...ITEMS.map(i => i.sek))

const W = 540
const H = 360
const PAD_L = 50
const PAD_R = 16
const PAD_T = 16
const PAD_B = 38
const PLOT_W = W - PAD_L - PAD_R
const PLOT_H = H - PAD_T - PAD_B

function xPos(sek: number): number {
  // log scale
  const logV = Math.log10(Math.max(sek, 1e5))
  const logMax = Math.log10(X_LABEL_MAX)
  const logMin = Math.log10(1e6)  // 1M floor
  const t = (logV - logMin) / (logMax - logMin)
  return PAD_L + t * PLOT_W
}

function yPos(g: number): number {
  const t = (g - Y_MIN) / (Y_MAX - Y_MIN)
  return PAD_T + (1 - t) * PLOT_H
}

const yZero = yPos(0)
const xMid = PAD_L + PLOT_W / 2

const quadrantColor = (sek: number, g: number) => {
  const lowSek = sek < X_LABEL_MAX * 0.1
  if (g >= 0 && !lowSek) return 'var(--good)'        // Defend — high SEK, growing
  if (g >= 0 && lowSek) return 'var(--accent)'       // Build — low SEK, growing
  if (g < 0 && !lowSek) return 'var(--warn)'         // Recover — high SEK, declining
  return 'var(--gray-2)'                             // Monitor — low SEK, declining
}

export function Stockholm05_PositioningQuadrant({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — strategic positioning"
      title="Where each Pfizer product sits in Stockholm"
      subtitle="Stockholm SEK on the horizontal, recent growth direction on the vertical. The four quadrants give the strategic instruction at a glance."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 18, overflow: 'hidden' }}>

        {/* Quadrant chart */}
        <div className="card" style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
          <div className="card-title">Stockholm portfolio quadrant</div>

          <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxHeight: 380 }}>
            {/* Quadrant fills */}
            <rect x={PAD_L} y={PAD_T} width={xMid - PAD_L} height={yZero - PAD_T} fill="#F0FAFE" />
            <rect x={xMid} y={PAD_T} width={PAD_L + PLOT_W - xMid} height={yZero - PAD_T} fill="#DCFCE7" opacity={0.5} />
            <rect x={PAD_L} y={yZero} width={xMid - PAD_L} height={PAD_T + PLOT_H - yZero} fill="#F4F6F9" />
            <rect x={xMid} y={yZero} width={PAD_L + PLOT_W - xMid} height={PAD_T + PLOT_H - yZero} fill="#FEE2E2" opacity={0.4} />

            {/* Axes */}
            <line x1={PAD_L} y1={yZero} x2={PAD_L + PLOT_W} y2={yZero} stroke="#9CA3AF" strokeWidth={1} />
            <line x1={xMid} y1={PAD_T} x2={xMid} y2={PAD_T + PLOT_H} stroke="#9CA3AF" strokeWidth={1} strokeDasharray="3,3" />
            <line x1={PAD_L} y1={PAD_T} x2={PAD_L} y2={PAD_T + PLOT_H} stroke="#9CA3AF" strokeWidth={0.8} />

            {/* Quadrant labels */}
            <text x={PAD_L + 10} y={PAD_T + 18} fontSize={10} fontWeight={700} fill="var(--accent-d)">Build</text>
            <text x={xMid + 10} y={PAD_T + 18} fontSize={10} fontWeight={700} fill="var(--good)">Defend / expand</text>
            <text x={PAD_L + 10} y={PAD_T + PLOT_H - 8} fontSize={10} fontWeight={700} fill="var(--gray-1)">Monitor</text>
            <text x={xMid + 10} y={PAD_T + PLOT_H - 8} fontSize={10} fontWeight={700} fill="var(--warn)">Recover</text>

            {/* Y axis labels */}
            <text x={PAD_L - 6} y={PAD_T + 4} fontSize={9} fill="var(--gray-1)" textAnchor="end">+{Y_MAX}%</text>
            <text x={PAD_L - 6} y={yZero + 3} fontSize={9} fill="var(--gray-1)" textAnchor="end">0</text>
            <text x={PAD_L - 6} y={PAD_T + PLOT_H + 1} fontSize={9} fill="var(--gray-1)" textAnchor="end">{Y_MIN}%</text>

            {/* Y axis title */}
            <text transform={`translate(14,${PAD_T + PLOT_H / 2}) rotate(-90)`}
              fontSize={9.5} fill="var(--gray-1)" textAnchor="middle">
              Growth · last 6 mo vs prior 6 mo
            </text>

            {/* X axis tick labels — log decades + actual max anchor */}
            {(() => {
              const ticks: Array<{ v: number; label: string }> = [
                { v: 1e6, label: '1 M' },
                { v: 1e7, label: '10 M' },
                { v: 1e8, label: '100 M' },
              ]
              const maxLabel = `${Math.round(X_LABEL_MAX / 1e6)} M`
              return (
                <g>
                  {ticks.map(t => {
                    const x = xPos(t.v)
                    return (
                      <g key={t.v}>
                        <line x1={x} y1={PAD_T + PLOT_H} x2={x} y2={PAD_T + PLOT_H + 3}
                          stroke="#9CA3AF" strokeWidth={0.8} />
                        <text x={x} y={PAD_T + PLOT_H + 12} fontSize={9}
                          fill="var(--gray-1)" textAnchor="middle">{t.label}</text>
                      </g>
                    )
                  })}
                  {/* Max anchor at right edge */}
                  <line x1={PAD_L + PLOT_W} y1={PAD_T + PLOT_H} x2={PAD_L + PLOT_W} y2={PAD_T + PLOT_H + 3}
                    stroke="#9CA3AF" strokeWidth={1} />
                  <text x={PAD_L + PLOT_W} y={PAD_T + PLOT_H + 12} fontSize={9} fontWeight={700}
                    fill="var(--navy-soft)" textAnchor="end">{maxLabel}</text>
                </g>
              )
            })()}

            {/* X axis label */}
            <text x={PAD_L + PLOT_W / 2} y={H - 4} fontSize={9.5} fill="var(--gray-1)" textAnchor="middle">
              Stockholm 3-yr SEK (log scale)
            </text>

            {/* Bubbles with anti-collision label placement */}
            {(() => {
              type Placed = { x: number; y: number; w: number; h: number; anchor: 'start' | 'end' }
              const placed: Placed[] = []
              const labelH = 12

              return ITEMS.map(it => {
                const cx = xPos(it.sek)
                const cy = yPos(Math.max(Math.min(it.growthPct, Y_MAX), Y_MIN))
                const r = 5 + Math.sqrt(it.sek / 1e6) * 0.6
                const color = quadrantColor(it.sek, it.growthPct)
                const labelW = it.label.length * 6.2
                const overflowsRight = cx + r + 3 + labelW > PAD_L + PLOT_W - 4
                let anchor: 'start' | 'end' = overflowsRight ? 'end' : 'start'
                let labelX = overflowsRight ? cx - r - 3 : cx + r + 3
                let labelY = cy + 3

                const collides = (lx: number, ly: number) => placed.some(p => {
                  const xLeft = anchor === 'start' ? lx : lx - labelW
                  const xRight = anchor === 'start' ? lx + labelW : lx
                  const pLeft = p.anchor === 'start' ? p.x : p.x - p.w
                  const pRight = p.anchor === 'start' ? p.x + p.w : p.x
                  const xOverlap = !(xRight < pLeft || xLeft > pRight)
                  const yOverlap = Math.abs(ly - p.y) < labelH
                  return xOverlap && yOverlap
                })

                let attempts = 0
                while (collides(labelX, labelY) && attempts < 8) {
                  labelY += attempts % 2 === 0 ? labelH + 2 : -(labelH + 2 + attempts * 2)
                  attempts++
                }
                placed.push({ x: labelX, y: labelY, w: labelW, h: labelH, anchor })

                return (
                  <g key={it.label}>
                    <circle cx={cx} cy={cy} r={r} fill={color} fillOpacity={0.55} stroke={color} strokeWidth={1.4} />
                    {/* Connector line if label was offset vertically */}
                    {Math.abs(labelY - (cy + 3)) > 4 && (
                      <line x1={cx} y1={cy} x2={anchor === 'start' ? labelX - 1 : labelX + 1} y2={labelY - 3}
                            stroke={color} strokeWidth={0.6} opacity={0.5} />
                    )}
                    <text x={labelX} y={labelY} fontSize={10} fontWeight={600} fill="var(--navy)" textAnchor={anchor}>{it.label}</text>
                  </g>
                )
              })
            })()}
          </svg>
        </div>

        {/* Right side — read */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="card card-good" style={{ padding: '10px 12px' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--good)' }}>Defend / expand</div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: '4px 0 0 0' }}>
              Vyndaqel anchors the quadrant; Elrexfio is climbing in on launch trajectory;
              Lorviqua sits at the boundary on positive Stockholm momentum. Defend Vyndaqel
              ahead of the August 2026 agreement renewal in a Beyonttra-shaped competitive
              picture; support Elrexfio's launch; confirm whether Lorviqua sustains — the
              gap between national care-programme positioning and the formal NT-rådet text
              is the open thread.
            </p>
          </div>
          <div className="card card-warn" style={{ padding: '10px 12px' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--warn)' }}>Recover</div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: '4px 0 0 0' }}>
              Ibrance and Xtandi both sit here. Ibrance is the deck's central recovery story
              (material Stockholm SEK with a declining trajectory; the brick-recovery analysis
              later in the deck identifies the headroom). Xtandi's decline is less expected
              for a mature co-marketed product and warrants a coordinated Pfizer-Astellas
              response.
            </p>
          </div>
          <div className="card" style={{ padding: '10px 12px', borderLeft: '4px solid var(--accent)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-d)' }}>Build</div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: '4px 0 0 0' }}>
              Vydura, Tukysa and Talzenna are the build positions: smaller current Stockholm
              SEK but strong growth. Each has a clear clinical forum (the breast-cancer
              care-programme group for Tukysa, specialist neurology for Vydura, the
              precision-oncology pathway for Talzenna).
            </p>
          </div>
          <div className="card" style={{ padding: '10px 12px', borderLeft: '4px solid var(--gray-2)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--gray-1)' }}>Monitor</div>
            <p style={{ fontSize: 10, color: 'var(--navy-soft)', lineHeight: 1.5, margin: '4px 0 0 0' }}>
              Currently empty for the Stockholm portfolio: no products combine low SEK with
              flat or declining trajectory at the moment. Pre-launch products (Hympavzi) and
              vaccines are excluded by construction.
            </p>
          </div>
        </div>
      </div>
      <div className="source-note">
        Source: IQVIA Sell-In Stockholm-region monthly aggregation. Growth = Oct 2025 to Mar 2026 vs Apr to Sep 2025.
      </div>
    </Slide>
  )
}
