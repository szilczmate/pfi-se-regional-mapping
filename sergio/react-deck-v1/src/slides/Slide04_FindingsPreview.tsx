import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const FINDINGS = [
  {
    num: '17.5%',
    headline: 'Ibrance national CDK4/6 share, where it currently sits',
    detail: 'Down from a peak of 58.6%. The recovery scenario in this work targets restoration of the 17.5% share, not a return to peak. The opportunity is concentrated in a handful of bricks; Stockholm-S is the largest single one, with the rest spread across roughly five other regions.',
    tag: 'Headline',
  },
  {
    num: '7.6×',
    headline: 'ATTR over-representation in the northern cluster',
    detail: 'Norrland over-indexes 7.6× the national rate for ATTR incidence, driven by the V30M hereditary cluster (predominantly polyneuropathy). Norrlands universitetssjukhus in Umeå is the reference centre. The NT-rådet process for Vyndaqel closed in September 2025; recommendation work moved to NAG LOK.',
    tag: 'Northern cornerstone',
  },
  {
    num: '4',
    headline: 'Parallel decision tracks',
    detail: 'TLV förmån, rekvisition, NT-rådet managed introduction, and sub-regional implementation each operate as their own process, with their own forums and their own rhythm. Mapping a product to the right track is what makes a stakeholder conversation land in the right place.',
    tag: 'Architecture',
  },
  {
    num: '2026-07-01',
    headline: 'NT-rådet chair transition',
    detail: 'Mårten Lindström hands over the chair to Margareta Holmström, an academic clinician at Karolinska University Hospital and Linköping University. A quiet but real signal for any item passing through national review in the second half of 2026.',
    tag: 'Reform signal',
  },
  {
    num: '135',
    headline: 'Decision-maker seats mapped, covering roughly 103 individuals',
    detail: 'Across 21 regions and seven roles per region, 135 of the 147 possible seats are filled with named incumbents. Three regions have structural exceptions (Halland runs local municipal HSNs; VGR splits HSN into strategic and operational; Sörmland routes through Regionstyrelsen). Nine seats are in transition or not yet publicly confirmed.',
    tag: 'Coverage',
  },
]

export function Slide04_FindingsPreview({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="What we found"
      title="Five numbers to anchor on"
      subtitle="The rest of the deck unpacks each of these in the order they appear here."
    >
      <div className="tldr-row">
        {FINDINGS.map(f => (
          <div key={f.num} className="tldr-card">
            <div>
              <span className="tldr-tag">{f.tag}</span>
              <div className="tldr-num">{f.num}</div>
              <div className="tldr-headline">{f.headline}</div>
            </div>
            <div className="tldr-detail">{f.detail}</div>
          </div>
        ))}
      </div>
    </Slide>
  )
}
