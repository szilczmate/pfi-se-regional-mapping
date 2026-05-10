import { useState } from 'react'

interface Props {
  current: number
  total: number
  onPrev: () => void
  onNext: () => void
  onJump: (n: number) => void
  slideTitles: string[]
}

export function Navigation({ current, total, onPrev, onNext, onJump, slideTitles }: Props) {
  const [tocOpen, setTocOpen] = useState(false)

  return (
    <>
      <div className="nav-bar">
        <button onClick={onPrev} disabled={current === 0}>‹ Prev</button>
        <span className="nav-counter">{current + 1} / {total}</span>
        <button onClick={onNext} disabled={current === total - 1}>Next ›</button>
        <button onClick={() => setTocOpen(o => !o)} title="Table of contents (T)">
          {tocOpen ? 'Close' : 'ToC'}
        </button>
      </div>

      {tocOpen && (
        <div className="toc-overlay" onClick={() => setTocOpen(false)}>
          <div className="toc-grid" onClick={e => e.stopPropagation()}>
            {slideTitles.map((title, i) => (
              <button
                key={i}
                className="toc-item"
                onClick={() => { onJump(i); setTocOpen(false) }}
                style={i === current ? { outline: '2px solid var(--accent)' } : undefined}
              >
                <span className="toc-num">Slide {i + 1}</span>
                <span>{title}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </>
  )
}
