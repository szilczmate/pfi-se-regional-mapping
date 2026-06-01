import { Slide } from '../components/Slide'
import type { SlideProps, RegionStakeholder } from '../types'
import STAKEHOLDERS from '../data/stakeholders.json'

const stakeholders = STAKEHOLDERS as RegionStakeholder[]

const ROLES: Array<{ key: keyof RegionStakeholder; short: string }> = [
  { key: 'Regiondirektör', short: 'RD' },
  { key: 'HSD', short: 'HSD' },
  { key: 'RS ordf', short: 'RS ordf' },
  { key: 'HSN ordf', short: 'HSN ordf' },
  { key: 'LK ordf', short: 'LK ordf' },
]

export function Slide08_DMM({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Part B · The stakeholders"
      title="21 regions × 5 decision-maker roles"
      subtitle="Who holds each formal role in each region · structural exceptions noted · 91% verified"
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm dmm-compact">
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Region</th>
              {ROLES.map(r => <th key={r.short}>{r.short}</th>)}
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
                    if (name && /STRUCTURAL/i.test(name)) {
                      const desc = name.replace(/STRUCTURAL[\s—-]+/i, '').slice(0, 50)
                      return <td key={r.short}><span style={{ color: 'var(--gold)', fontStyle: 'italic', fontSize: 10 }}>structural · {desc}</span></td>
                    }
                    if ((!name || name === '?') && /sjukhusstyrelsen|exception|structural|local hsn|kombinerad|combined|differ|kommun\+region|bitr/i.test(sourceText)) {
                      return <td key={r.short}><span style={{ color: 'var(--gold)', fontStyle: 'italic', fontSize: 10 }}>structural exception</span></td>
                    }
                    if (!name || name === '?') {
                      return <td key={r.short}><span style={{ color: 'var(--warn)', fontWeight: 600, fontSize: 10 }}>verify</span></td>
                    }
                    return <td key={r.short}><span style={{ color: 'var(--navy)', fontWeight: 500 }}>{name}</span></td>
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', gap: 18, marginTop: 10, fontSize: 10, color: 'var(--gray-1)' }}>
        <div><span style={{ color: 'var(--navy)', fontWeight: 600 }}>Name</span> = verified incumbent</div>
        <div><span style={{ color: 'var(--gold)', fontStyle: 'italic' }}>structural exception</span> = role split / distributed</div>
        <div><span style={{ color: 'var(--warn)', fontWeight: 600 }}>verify</span> = incumbent unconfirmed</div>
      </div>
    </Slide>
  )
}
