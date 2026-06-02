import { useState, useMemo, useEffect } from 'react'

interface Props {
  current: number
  total: number
  onPrev: () => void
  onNext: () => void
  onJump: (n: number) => void
  slideTitles: string[]
}

interface Group {
  header: string
  dividerIndex: number | null
  items: { index: number; title: string }[]
}

// Group slides into collapsible sections. A title like "Section 3 · Region focus: Skåne"
// starts a new section (that slide is the divider); everything before the first such title
// is the "Opening" group.
function buildGroups(titles: string[]): Group[] {
  const groups: Group[] = []
  let cur: Group = { header: 'Opening', dividerIndex: null, items: [] }
  titles.forEach((title, i) => {
    if (/^Section\s+\d+/.test(title)) {
      if (cur.items.length || cur.dividerIndex !== null) groups.push(cur)
      cur = { header: title, dividerIndex: i, items: [] }
    } else {
      cur.items.push({ index: i, title })
    }
  })
  if (cur.items.length || cur.dividerIndex !== null) groups.push(cur)
  return groups
}

const sectionTopic = (header: string) => header.replace(/^Section\s+\d+\s*·\s*/, '')

export function Navigation({ current, total, onPrev, onNext, onJump, slideTitles }: Props) {
  const [tocOpen, setTocOpen] = useState(false)
  const groups = useMemo(() => buildGroups(slideTitles), [slideTitles])
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  const groupOf = (idx: number) =>
    groups.findIndex(g => g.dividerIndex === idx || g.items.some(it => it.index === idx))

  // When the ToC opens, expand the section that contains the current slide.
  useEffect(() => {
    if (tocOpen) {
      const gi = groupOf(current)
      setExpanded(new Set(gi >= 0 ? [gi] : [0]))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tocOpen])

  const toggle = (gi: number) =>
    setExpanded(prev => {
      const n = new Set(prev)
      if (n.has(gi)) n.delete(gi)
      else n.add(gi)
      return n
    })

  const jump = (i: number) => { onJump(i); setTocOpen(false) }

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
          <div className="toc-panel" onClick={e => e.stopPropagation()}>
            <div className="toc-panel-title">Contents · {total} slides</div>
            {groups.map((g, gi) => {
              const isOpen = expanded.has(gi)
              const hasCurrent = groupOf(current) === gi
              return (
                <div className="toc-section" key={gi}>
                  <button
                    className={`toc-section-head${hasCurrent ? ' current' : ''}`}
                    onClick={() => toggle(gi)}
                  >
                    <span className="toc-chevron">{isOpen ? '▾' : '▸'}</span>
                    <span className="toc-section-label">{g.header}</span>
                    <span className="toc-section-count">{g.items.length}</span>
                  </button>
                  {isOpen && (
                    <div className="toc-leaves">
                      {g.dividerIndex !== null && (
                        <button
                          className={`toc-leaf${current === g.dividerIndex ? ' current' : ''}`}
                          onClick={() => jump(g.dividerIndex as number)}
                        >
                          <span className="toc-num">{g.dividerIndex + 1}</span>
                          <span>{sectionTopic(g.header)}</span>
                        </button>
                      )}
                      {g.items.map(it => (
                        <button
                          key={it.index}
                          className={`toc-leaf${current === it.index ? ' current' : ''}`}
                          onClick={() => jump(it.index)}
                        >
                          <span className="toc-num">{it.index + 1}</span>
                          <span>{it.title}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </>
  )
}
