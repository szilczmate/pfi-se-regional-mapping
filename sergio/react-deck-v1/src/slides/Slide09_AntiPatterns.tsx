import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const ROUTING = [
  {
    question: 'Reimbursement scope or restriction (förmån)',
    forum: 'TLV nämnd · TLV pris- och subventionsenhet for technical follow-up',
    products: ['Vyndaqel', 'Vydura', 'Ibrance', 'Lorviqua', 'Xtandi', 'Talzenna'],
  },
  {
    question: 'Whether a national recommendation will be issued for a new medicine',
    forum: 'NT-rådet ordförande and the sjukvårdsregional NT-rådet representatives',
    products: ['Abrysvo', 'Elrexfio', '(any new entrant)'],
  },
  {
    question: 'Treatment recommendation for a product after the national process closes',
    forum: 'NAG LOK or the relevant NPO/NAG group under SKR Kunskapsstyrning',
    products: ['Vyndaqel'],
  },
  {
    question: 'Clinical positioning or pathway for a förmån product NT-rådet has not recommended on',
    forum: 'RCC and the relevant national care-programme group',
    products: ['Tukysa', 'Talzenna', 'Lorviqua'],
  },
  {
    question: 'Vaccine programme inclusion or population recommendation',
    forum: 'Folkhälsomyndigheten vaccination unit',
    products: ['Abrysvo (maternal)', 'Prevenar 20 / Apexxnar', 'FSME-IMMUN'],
  },
  {
    question: 'Regional formulary listing or local clinical guidance',
    forum: "The region's drugs and therapeutics committee (Janusinfo, Skånelistan, etc.)",
    products: ['(any förmån product post-listing)'],
  },
  {
    question: 'Nationally negotiated agreement renewal or renegotiation',
    forum: 'Pfizer Marknad/Förhandling, coordinated with the regional procurement function',
    products: ['Tukysa', 'Vyndaqel', 'Talzenna'],
  },
  {
    question: 'Co-marketed product positioning',
    forum: 'Coordinated message with the partner. Uncoordinated outreach creates channel conflict',
    products: ['Xtandi (with Astellas)'],
  },
]

export function Slide09_AntiPatterns({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Engagement routing"
      title="Which forum for which kind of question"
      subtitle="Where to route the recurring engagement questions in the portfolio."
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm">
          <thead>
            <tr>
              <th style={{ width: '34%' }}>The question</th>
              <th style={{ width: '40%' }}>The forum that owns it</th>
              <th style={{ width: '26%' }}>Most relevant products</th>
            </tr>
          </thead>
          <tbody>
            {ROUTING.map((r, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600, color: 'var(--navy)', fontSize: 12, padding: '15px 10px' }}>{r.question}</td>
                <td style={{ fontSize: 11 }}>
                  <span style={{ color: 'var(--accent-d)', fontWeight: 600 }}>{r.forum}</span>
                </td>
                <td style={{ fontSize: 10 }}>
                  {r.products.map(p => (
                    <span key={p} style={{
                      display: 'inline-block', marginRight: 4, marginBottom: 2,
                      padding: '1px 6px', background: 'var(--accent-l)',
                      color: 'var(--accent-d)', borderRadius: 8, fontSize: 9, fontWeight: 600,
                    }}>{p}</span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Slide>
  )
}
