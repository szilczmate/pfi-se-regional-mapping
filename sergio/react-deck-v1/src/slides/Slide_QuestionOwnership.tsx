import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

type RoleType = 'political' | 'operational' | 'clinical'

const TYPE_META: Record<RoleType, { color: string; label: string }> = {
  political:   { color: 'var(--track-a)', label: 'Political' },
  operational: { color: 'var(--track-b)', label: 'Operational' },
  clinical:    { color: 'var(--track-c)', label: 'Clinical-pharma' },
}

interface RoleRow {
  abbr: string
  full: string
  type: RoleType
  owns: string
  bring: string
}

const ROLES: RoleRow[] = [
  {
    abbr: 'RS ordf',
    full: 'Regionstyrelsens ordförande',
    type: 'political',
    owns: 'The overall regional budget frame and strategic direction. This seat sets the size of the envelope; the choice of individual therapies sits elsewhere. Where there is no single HSN (e.g. Halland), it also absorbs the healthcare-board role.',
    bring: 'System-level and equity narratives, and budget-cycle timing. Rarely the route for a single product.',
  },
  {
    abbr: 'HSN ordf',
    full: 'Hälso- och sjukvårdsnämndens ordförande',
    type: 'political',
    owns: 'How the care budget is allocated: wait-times, prevention, where money moves across the system. Politically accountable for access.',
    bring: 'Budget-impact predictability; whether a therapy frees capacity rather than consumes it; equity-of-access framing.',
  },
  {
    abbr: 'RD',
    full: 'Regiondirektör',
    type: 'operational',
    owns: 'Turning political direction into operations; the scope of regional self-rule on klinikläkemedel; beredskap and continuity of care.',
    bring: 'When a national decision reaches regional practice: the operational rollout and its sequencing.',
  },
  {
    abbr: 'HSD',
    full: 'Hälso- och sjukvårdsdirektör',
    type: 'operational',
    owns: 'Healthcare-system steering: capacity, specialty workforce, vårdgaranti compliance, delivery pathways.',
    bring: 'Delivery practicality: infusion-chair allocation, referral pathways, implementation sequencing.',
  },
  {
    abbr: 'LK ordf',
    full: 'Läkemedelskommitténs ordförande',
    type: 'clinical',
    owns: 'The regional formulary / rekommendationslista, localisation of NT-rådet recommendations, and evidence quality on new entrants (Track D).',
    bring: 'Formulary positioning and vårdprogram updates, rather than national subsidy questions.',
  },
]

export function Slide_QuestionOwnership({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Part B · The stakeholders"
      title="Which question belongs to which seat"
      subtitle="Each of the five regional roles holds a different mandate."
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 7, overflow: 'hidden' }}>
        {/* Column headers */}
        <div style={{
          display: 'grid', gridTemplateColumns: '23% 41% 36%', gap: 12,
          fontSize: 9, fontWeight: 700, color: 'var(--gray-1)',
          letterSpacing: '0.06em', textTransform: 'uppercase', padding: '0 14px',
        }}>
          <div>Role</div>
          <div>What it owns</div>
          <div>The right question to bring</div>
        </div>

        {ROLES.map(r => {
          const meta = TYPE_META[r.type]
          return (
            <div key={r.abbr} className="card" style={{
              padding: '9px 14px', borderLeft: `4px solid ${meta.color}`,
              display: 'grid', gridTemplateColumns: '23% 41% 36%', gap: 12,
              alignItems: 'center', flex: 1,
            }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)' }}>{r.abbr}</div>
                <div style={{ fontSize: 9, color: 'var(--gray-1)', lineHeight: 1.3, marginTop: 1 }}>{r.full}</div>
                <span style={{
                  display: 'inline-block', marginTop: 4, fontSize: 8, fontWeight: 700,
                  letterSpacing: '0.05em', textTransform: 'uppercase', color: meta.color,
                }}>
                  {meta.label}
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5 }}>{r.owns}</div>
              <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.5 }}>{r.bring}</div>
            </div>
          )
        })}
      </div>

      <div className="source-note">
        The decision-maker matrix lists the verified incumbent in each seat, for all 21 regions.
      </div>
    </Slide>
  )
}
