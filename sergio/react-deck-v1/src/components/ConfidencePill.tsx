import type { Confidence } from '../types'

interface Props {
  level: Confidence
  label?: string
}

const colorMap: Record<Confidence, string> = {
  VERIFIED: 'verified',
  OBSERVED: 'observed',
  INFERRED: 'inferred',
  OPEN: 'open',
}

export function ConfidencePill({ level, label }: Props) {
  return <span className={`conf-pill ${colorMap[level]}`}>{label || level}</span>
}
