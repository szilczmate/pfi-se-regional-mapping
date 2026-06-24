import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import priorities from '../data/stakeholderpriorities.json'

interface PriorityRow {
  role: string
  focus: string
}

interface Props extends SlideProps {
  region?: string
}

type RoleType = 'political' | 'operational' | 'formulary' | 'national'

const TYPE_META: Record<RoleType, { color: string; label: string }> = {
  political:   { color: 'var(--track-a)', label: 'Political' },
  operational: { color: 'var(--track-b)', label: 'Operational' },
  formulary:   { color: 'var(--track-c)', label: 'Clinical-pharma' },
  national:    { color: 'var(--accent)',  label: 'National coordination' },
}

function classify(role: string): RoleType {
  const r = role.toLowerCase()
  if (r.includes('nt-rådet') || r.includes('nsg')) return 'national'
  if (r.includes('lk ordf')) return 'formulary'
  if (r.includes('hsd') || r.includes('rd ·')) return 'operational'
  return 'political'  // HSN, RS
}

export function Slide12_StakeholderPriorities({ isActive, region = 'Region Stockholm' }: Props) {
  const data = ((priorities as Record<string, any[]>)[region] || []) as PriorityRow[]
  const regionShort = region.replace('Region ', '').replace('Västra Götalandsregionen', 'VGR')

  return (
    <Slide
      isActive={isActive}
      sectionLabel={`${regionShort} · governance`}
      title="Each decision-maker's priorities"
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, overflow: 'hidden' }}>
        {data.filter(d => d.focus).map((p, i) => {
          const t = classify(p.role)
          const meta = TYPE_META[t]
          return (
            <div key={i} className="card" style={{
              padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 6,
              borderLeft: `4px solid ${meta.color}`, background: 'white',
            }}>
              <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 8 }}>
                <div style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--navy)' }}>
                  {p.role}
                </div>
                <span style={{
                  fontSize: 8.5, fontWeight: 700, color: meta.color,
                  letterSpacing: '0.06em', textTransform: 'uppercase',
                  whiteSpace: 'nowrap',
                }}>
                  {meta.label}
                </span>
              </div>
              <div>
                <span style={{
                  fontSize: 9, fontWeight: 700, color: 'var(--gray-1)',
                  letterSpacing: '0.06em', textTransform: 'uppercase', marginRight: 6,
                }}>
                  Focus
                </span>
                <span style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5 }}>
                  {p.focus}
                </span>
              </div>
              {/* Samira 2026-06-16 (Bild 18): "Pfizer angle" block removed — the slide now shows
                  each decision-maker's role + type + focus only (no Pfizer-commercial overlay).
                  Applies to all region instances (Stockholm / Skåne / VGR). */}
            </div>
          )
        })}
      </div>

      {/* Legend strip explaining the four role types */}
      <div style={{
        marginTop: 8, display: 'flex', gap: 16, justifyContent: 'center',
        fontSize: 9.5, color: 'var(--gray-1)',
      }}>
        {(Object.keys(TYPE_META) as RoleType[]).map(t => (
          <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{
              display: 'inline-block', width: 10, height: 3,
              background: TYPE_META[t].color, borderRadius: 1,
            }} />
            <span>{TYPE_META[t].label}</span>
          </span>
        ))}
      </div>

      <div className="source-note">
        Sources: per-role priorities drawn from regional budget documents, annual plans, and recent public statements by the named incumbents.
      </div>
    </Slide>
  )
}
