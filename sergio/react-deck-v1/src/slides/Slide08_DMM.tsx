import { Slide } from '../components/Slide'
import type { SlideProps, RegionStakeholder } from '../types'
import STAKEHOLDERS from '../data/stakeholders.json'

const stakeholders = STAKEHOLDERS as RegionStakeholder[]

// Samira feedback 2026-06-16 (Bild 11): colour-code the role columns by decision-maker
// TYPE, reusing the exact taxonomy + colours from the "Question ownership" slide
// (Slide_QuestionOwnership) and the stakeholder-priorities slide, so the matrix reads at a
// glance as Political / Operational / Clinical-pharma. In-cell colours still encode
// verification status (verified name / structural exception / verify).
type RoleType = 'political' | 'operational' | 'clinical'

// color = header text + underline; headBg = column-header tint; cellBg = faint full-column tint
// (Samira 2026-06-16 (Bild 11): tint the whole column, not just the header, for clarity).
const TYPE_META: Record<RoleType, { color: string; headBg: string; cellBg: string; label: string }> = {
  political:   { color: 'var(--track-a)', headBg: 'color-mix(in srgb, var(--track-a) 20%, white)', cellBg: 'color-mix(in srgb, var(--track-a) 10%, white)', label: 'Political' },
  operational: { color: 'var(--track-b)', headBg: 'color-mix(in srgb, var(--track-b) 20%, white)', cellBg: 'color-mix(in srgb, var(--track-b) 10%, white)', label: 'Operational' },
  clinical:    { color: 'var(--track-c)', headBg: 'color-mix(in srgb, var(--track-c) 20%, white)', cellBg: 'color-mix(in srgb, var(--track-c) 10%, white)', label: 'Clinical-pharma' },
}

const ROLES: Array<{ key: keyof RegionStakeholder; short: string; type: RoleType }> = [
  { key: 'Regiondirektör', short: 'RD', type: 'operational' },
  { key: 'HSD', short: 'HSD', type: 'operational' },
  { key: 'RS ordf', short: 'RS ordf', type: 'political' },
  { key: 'HSN ordf', short: 'HSN ordf', type: 'political' },
  { key: 'LK ordf', short: 'LK ordf', type: 'clinical' },
]

export function Slide08_DMM({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Part B · The stakeholders"
      title="21 regions × 5 decision-maker roles"
      subtitle="Who holds each formal role in each region · structural exceptions noted"
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm dmm-compact">
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Region</th>
              {ROLES.map(r => (
                <th key={r.short} style={{
                  color: TYPE_META[r.type].color,
                  background: TYPE_META[r.type].headBg,
                  borderBottom: `2px solid ${TYPE_META[r.type].color}`,
                }}>{r.short}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {stakeholders.map(s => {
              const region = (s.Region || '').replace('Region ', '').replace('Västra Götalandsregionen', 'VGR')
              return (
                <tr key={s.Region}>
                  <td className="product">{region}</td>
                  {ROLES.map(r => {
                    const name = s[r.key]
                    const sourceText = (s[`${r.key} source`] || '').toLowerCase()
                    const cellBg = TYPE_META[r.type].cellBg // Samira 2026-06-16 (Bild 11): faint full-column tint
                    if (name && /STRUCTURAL/i.test(name)) {
                      const desc = name.replace(/STRUCTURAL[\s—-]+/i, '').slice(0, 80)
                      return <td key={r.short} style={{ background: cellBg }}><span style={{ color: 'var(--gold)', fontStyle: 'italic', fontSize: 10 }}>structural · {desc}</span></td>
                    }
                    if ((!name || name === '?') && /sjukhusstyrelsen|exception|structural|local hsn|kombinerad|combined|differ|kommun\+region|bitr/i.test(sourceText)) {
                      return <td key={r.short} style={{ background: cellBg }}><span style={{ color: 'var(--gold)', fontStyle: 'italic', fontSize: 10 }}>structural exception</span></td>
                    }
                    if (!name || name === '?') {
                      return <td key={r.short} style={{ background: cellBg }}><span style={{ color: 'var(--warn)', fontWeight: 600, fontSize: 10 }}>verify</span></td>
                    }
                    return <td key={r.short} style={{ background: cellBg }}><span style={{ color: 'var(--navy)', fontWeight: 500 }}>{name}</span></td>
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
        {/* Samira 2026-06-16 (Bild 11): role-type colour legend — matches the header colours */}
        <div style={{ display: 'flex', gap: 16, fontSize: 10, color: 'var(--gray-1)', alignItems: 'center' }}>
          <span style={{ fontWeight: 700, color: 'var(--navy)' }}>Role type</span>
          {(Object.keys(TYPE_META) as RoleType[]).map(t => (
            <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ display: 'inline-block', width: 12, height: 3, background: TYPE_META[t].color, borderRadius: 1 }} />
              <span>{TYPE_META[t].label}</span>
            </span>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 18, fontSize: 10, color: 'var(--gray-1)' }}>
          <div><span style={{ color: 'var(--navy)', fontWeight: 600 }}>Name</span> = verified incumbent</div>
          <div><span style={{ color: 'var(--gold)', fontStyle: 'italic' }}>structural exception</span> = role shared or run through another body (shown in the cell)</div>
          <div><span style={{ color: 'var(--warn)', fontWeight: 600 }}>verify</span> = incumbent unconfirmed</div>
        </div>
      </div>
    </Slide>
  )
}
