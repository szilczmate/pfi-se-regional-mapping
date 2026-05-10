import { useState, useEffect, useCallback, useRef, useLayoutEffect } from 'react'
import { Navigation } from './components/Navigation'
import { ALL_SLIDES, SLIDE_TITLES } from './slides'

export default function App() {
  const [current, setCurrent] = useState(0)
  const stageRef = useRef<HTMLDivElement>(null)
  const total = ALL_SLIDES.length

  const goSlide = useCallback((n: number) => {
    setCurrent(Math.max(0, Math.min(n, total - 1)))
  }, [total])

  const next = useCallback(() => setCurrent(c => Math.min(c + 1, total - 1)), [total])
  const prev = useCallback(() => setCurrent(c => Math.max(c - 1, 0)), [])

  // Auto-scale 1280×720 stage to viewport
  useLayoutEffect(() => {
    function fit() {
      if (!stageRef.current) return
      const { innerWidth: w, innerHeight: h } = window
      const scale = Math.min(w / 1280, h / 720) * 0.95
      stageRef.current.style.transform = `scale(${scale})`
    }
    fit()
    window.addEventListener('resize', fit)
    return () => window.removeEventListener('resize', fit)
  }, [])

  // Keyboard nav
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
        e.preventDefault(); next()
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault(); prev()
      } else if (e.key === 'Home') {
        e.preventDefault(); setCurrent(0)
      } else if (e.key === 'End') {
        e.preventDefault(); setCurrent(total - 1)
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [next, prev, total])

  return (
    <div className="presentation">
      <div ref={stageRef} className="slide-stage">
        {ALL_SLIDES.map((Component, i) => (
          <Component key={i} isActive={current === i} goSlide={goSlide} />
        ))}
      </div>
      <Navigation
        current={current}
        total={total}
        onPrev={prev}
        onNext={next}
        onJump={goSlide}
        slideTitles={SLIDE_TITLES}
      />
    </div>
  )
}
