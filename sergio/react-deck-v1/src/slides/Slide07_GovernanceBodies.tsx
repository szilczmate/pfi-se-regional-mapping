import { Slide } from '../components/Slide'
import type { SlideProps, NamedIndividual, RegionStakeholder } from '../types'
import NAMED from '../data/named.json'
import STAKEHOLDERS from '../data/stakeholders.json'

const named = NAMED as NamedIndividual[]
const stakeholders = STAKEHOLDERS as RegionStakeholder[]

export function Slide07_GovernanceBodies({ isActive }: SlideProps) {
  const ntRows = named.filter(n => /NT-rådet/.test(n.roles))
  const nsgRows = named.filter(n => /NSG/.test(n.roles))
  const lkOrdf = stakeholders
    .filter(s => s['LK ordf'])
    .map(s => ({
      region: (s.Region || '').replace('Region ', '').replace('Västra Götalandsregionen', 'VGR'),
      name: s['LK ordf'] || '—',
    }))

  const renderRow = (n: NamedIndividual) => {
    let tag: { label: string; warn?: boolean } | null = null
    if (n.name === 'Mårten Lindström') tag = { label: 'tf. Chair → 2026-07-01', warn: true }
    else if (n.name === 'Anders Bergström') tag = { label: 'Vice Chair' }
    else if (n.name === 'Margareta Holmström') tag = { label: 'Incoming Chair 2026-07-01' }

    return (
      <div className="gov-row" key={n.name}>
        <div style={{ flex: 1 }}>
          <div className="gov-name">{n.name}</div>
          <div className="gov-role">{n.roles.replace(/NT-rådet rep /, 'rep ').replace(/NSG rep /, 'rep ').replace(/HSD /, '+ HSD ')}</div>
        </div>
        {tag && <span className={`gov-tag${tag.warn ? ' warn' : ''}`}>{tag.label}</span>}
      </div>
    )
  }

  return (
    <Slide
      isActive={isActive}
      sectionLabel="Part B · The stakeholders"
      title="Three governance bodies · named seats"
      subtitle="NT-rådet recommends · NSG coordinates clinical strategy · 21 regional formularies decide locally · Holmström succession 2026-07-01"
    >
      <div className="gov-grid">
        {/* NT-rådet */}
        <div className="gov-card">
          <div className="gov-card-header">
            <div className="gov-card-title">NT-rådet</div>
            <div className="gov-card-subtitle">National Pharmacy Advisory Council · ordinary members + adjuncts coordinated by sjukvårdsregion</div>
          </div>
          <div className="gov-card-body">
            {ntRows.map(renderRow)}
          </div>
        </div>

        {/* NSG */}
        <div className="gov-card">
          <div className="gov-card-header">
            <div className="gov-card-title">NSG Läkemedel</div>
            <div className="gov-card-subtitle">National Support Group · 6 sjukvårdsregion clinical-strategy reps</div>
          </div>
          <div className="gov-card-body">
            {nsgRows.map(renderRow)}
          </div>
        </div>

        {/* LK ordföranden */}
        <div className="gov-card">
          <div className="gov-card-header">
            <div className="gov-card-title">LK ordföranden</div>
            <div className="gov-card-subtitle">21 regional läkemedelskommitté chairs · independent formulary authority per region</div>
          </div>
          <div className="gov-card-body">
            {lkOrdf.map(l => (
              <div className="gov-row" key={l.region} style={{ padding: '4px 0' }}>
                <div style={{ flex: 1 }}>
                  <div className="gov-name" style={{ fontSize: 10.5 }}>{l.name}</div>
                  <div className="gov-role" style={{ fontSize: 9 }}>{l.region}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Slide>
  )
}
