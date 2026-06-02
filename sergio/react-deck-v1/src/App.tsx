import { useState, useEffect, useCallback, useRef, useLayoutEffect } from 'react'
import { Navigation } from './components/Navigation'
import { ALL_SLIDES, SLIDE_TITLES } from './slides'

const MIN_ZOOM = 1
const MAX_ZOOM = 3
const ZOOM_STEP = 0.2

export default function App() {
  const [current, setCurrent] = useState(0)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const stageRef = useRef<HTMLDivElement>(null)
  const fitRef = useRef(1)            // current fit-to-window scale
  const zoomRef = useRef(1)           // mirror of zoom for resize handler
  const panRef = useRef({ x: 0, y: 0 })
  const total = ALL_SLIDES.length

  const goSlide = useCallback((n: number) => {
    setCurrent(Math.max(0, Math.min(n, total - 1)))
  }, [total])

  const next = useCallback(() => setCurrent(c => Math.min(c + 1, total - 1)), [total])
  const prev = useCallback(() => setCurrent(c => Math.max(c - 1, 0)), [])

  // Set the stage transform. At zoom 1 / pan 0 this is exactly `scale(fit)` — identical
  // to the original behaviour, so the default (and print) experience is unchanged.
  const setStageTransform = useCallback((f: number, z: number, p: { x: number; y: number }) => {
    const el = stageRef.current
    if (!el) return
    el.style.transform = (z === 1 && p.x === 0 && p.y === 0)
      ? `scale(${f})`
      : `translate(${p.x}px, ${p.y}px) scale(${f * z})`
  }, [])

  // Clamp pan so the scaled stage can't be dragged fully off-screen.
  const clampPan = useCallback((x: number, y: number, z: number) => {
    const s = fitRef.current * z
    const maxX = Math.max(0, (1280 * s - window.innerWidth) / 2)
    const maxY = Math.max(0, (720 * s - window.innerHeight) / 2)
    return { x: Math.max(-maxX, Math.min(maxX, x)), y: Math.max(-maxY, Math.min(maxY, y)) }
  }, [])

  // Fit 1280×720 to the viewport (mount + on resize). Reads current zoom/pan from refs.
  useLayoutEffect(() => {
    const fit = () => {
      fitRef.current = Math.min(window.innerWidth / 1280, window.innerHeight / 720) * 0.95
      setStageTransform(fitRef.current, zoomRef.current, panRef.current)
    }
    fit()
    window.addEventListener('resize', fit)
    return () => window.removeEventListener('resize', fit)
  }, [setStageTransform])

  // Re-apply transform when zoom/pan change, keeping the refs in sync.
  useLayoutEffect(() => {
    zoomRef.current = zoom
    panRef.current = pan
    setStageTransform(fitRef.current, zoom, pan)
  }, [zoom, pan, setStageTransform])

  // Re-centre (but keep the zoom level) when the slide changes.
  useEffect(() => { setPan({ x: 0, y: 0 }) }, [current])

  const zoomBy = useCallback((delta: number) => {
    const nz = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, +(zoomRef.current + delta).toFixed(2)))
    zoomRef.current = nz   // sync immediately so rapid wheel/clicks accumulate correctly
    setZoom(nz)
    setPan(p => (nz === 1 ? { x: 0, y: 0 } : clampPan(p.x, p.y, nz)))
  }, [clampPan])

  const resetZoom = useCallback(() => { setZoom(1); setPan({ x: 0, y: 0 }) }, [])

  // Ctrl/⌘ + wheel zooms the deck instead of the browser.
  useEffect(() => {
    const onWheel = (e: WheelEvent) => {
      if (!(e.ctrlKey || e.metaKey)) return
      e.preventDefault()
      zoomBy(e.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP)
    }
    window.addEventListener('wheel', onWheel, { passive: false })
    return () => window.removeEventListener('wheel', onWheel)
  }, [zoomBy])

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

  // Drag-to-pan (only when zoomed in).
  const dragStart = useRef<{ sx: number; sy: number; px: number; py: number } | null>(null)
  const onPointerDown = (e: React.PointerEvent) => {
    if (zoom === 1) return
    dragStart.current = { sx: e.clientX, sy: e.clientY, px: pan.x, py: pan.y }
    setDragging(true)
    try { (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId) } catch { /* noop */ }
  }
  const onPointerMove = (e: React.PointerEvent) => {
    const d = dragStart.current
    if (!d) return
    setPan(clampPan(d.px + (e.clientX - d.sx), d.py + (e.clientY - d.sy), zoom))
  }
  const onPointerUp = () => { dragStart.current = null; setDragging(false) }

  return (
    <div className="presentation">
      <div
        ref={stageRef}
        className="slide-stage"
        style={{ cursor: zoom > 1 ? (dragging ? 'grabbing' : 'grab') : undefined }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
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
      <div className="zoom-bar">
        <button onClick={() => zoomBy(-ZOOM_STEP)} disabled={zoom <= MIN_ZOOM} title="Zoom out">−</button>
        <button onClick={resetZoom} title="Reset zoom">{Math.round(zoom * 100)}%</button>
        <button onClick={() => zoomBy(ZOOM_STEP)} disabled={zoom >= MAX_ZOOM} title="Zoom in">+</button>
      </div>
    </div>
  )
}
