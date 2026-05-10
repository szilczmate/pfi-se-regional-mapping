/**
 * Number formatting helpers (Swedish locale).
 */
export const fmt = {
  num: (v: number | null | undefined): string => {
    if (v == null || isNaN(v as number)) return '—'
    return Math.round(v as number).toLocaleString('sv-SE')
  },
  dec: (v: number | null | undefined, digits = 1): string => {
    if (v == null || isNaN(v as number)) return '—'
    return (v as number).toFixed(digits)
  },
  pct: (v: number | null | undefined, digits = 1): string => {
    if (v == null) return '—'
    return `${(v as number).toFixed(digits)}%`
  },
  sek: (v: number | null | undefined): string => {
    if (v == null) return '—'
    if (v >= 1e9) return `${(v / 1e9).toFixed(1)} bn SEK`
    if (v >= 1e6) return `${(v / 1e6).toFixed(0)} mn SEK`
    return `${Math.round(v).toLocaleString('sv-SE')} SEK`
  },
  mnkr: (v: number | null | undefined): string => {
    if (v == null) return '—'
    return `${Math.round(v / 1e6).toLocaleString('sv-SE')} mnkr`
  },
  per100k: (count: number | null | undefined, pop: number | null | undefined, digits = 2): string => {
    if (count == null || pop == null || pop === 0) return '—'
    return ((count / pop) * 100000).toFixed(digits)
  },
}
