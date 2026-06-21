import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

// Samira feedback 2026-06-16 (Bild 12): removed the "Most relevant products" column (incl. Xtandi)
// and the product-specific co-marketing row. The slide now shows the decision flow only — each kind
// of decision, the forum that owns it, and the decision-makers/seats involved.
const ROUTING = [
  {
    question: 'Reimbursement scope or restriction (förmån)',
    forum: 'TLV nämnd · pris- och subventionsenhet for technical follow-up',
    deciders: 'TLV board (national) · regional LK ordförande localises the listing',
  },
  {
    question: 'Whether a national recommendation will be issued for a new medicine',
    forum: 'NT-rådet',
    deciders: 'NT-rådet ordförande + the six sjukvårdsregional NT-rådet representatives',
  },
  {
    question: 'Treatment recommendation for a product after the national process closes',
    forum: 'NAG LOK / relevant NPO-NAG group under SKR Kunskapsstyrning',
    deciders: 'NAG/NPO clinical chairs (nationella programområden)',
  },
  {
    question: 'Clinical positioning or pathway for a förmån product NT-rådet has not recommended on',
    forum: 'RCC and the relevant national care-programme group',
    deciders: 'RCC line + the vårdprogram group chair',
  },
  {
    question: 'Vaccine programme inclusion or population recommendation',
    forum: 'Folkhälsomyndigheten vaccination unit',
    deciders: 'FoHM (national) · regional smittskydd implements',
  },
  {
    question: 'Regional formulary listing or local clinical guidance',
    forum: "The region's drugs and therapeutics committee (Janusinfo, Skånelistan, etc.)",
    deciders: 'Läkemedelskommitténs ordförande (LK ordf), per region',
  },
  {
    question: 'Nationally negotiated agreement renewal or renegotiation',
    forum: 'Regional procurement, coordinated nationally via SKR / the regions',
    deciders: 'Regional inköp/upphandling + ekonomistab',
  },
]

export function Slide09_AntiPatterns({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Engagement routing"
      title="Which forum for which kind of question"
      subtitle="For each kind of decision: the forum that owns it and the decision-makers involved."
    >
      {/* Samira 2026-06-16 (Bild 12): rebuilt as an explicit decision → forum → decision-makers
          FLOW (her word: "ett tydligt flöde"), replacing the product-centric table. Lanes fill
          the slide vertically, so there is no empty space. */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 7, overflow: 'hidden' }}>
        {/* stage header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1.25fr 22px 1.05fr 22px 1fr',
          alignItems: 'center', gap: 8, padding: '0 14px',
          fontSize: 9, fontWeight: 700, color: 'var(--gray-1)',
          letterSpacing: '0.06em', textTransform: 'uppercase',
        }}>
          <div>The kind of decision</div>
          <div />
          <div>The forum that owns it</div>
          <div />
          <div>Decision-makers involved</div>
        </div>

        {ROUTING.map((r, i) => (
          <div key={i} className="card" style={{
            display: 'grid', gridTemplateColumns: '1.25fr 22px 1.05fr 22px 1fr',
            alignItems: 'center', gap: 8, padding: '9px 14px', flex: 1,
            borderLeft: '4px solid var(--accent)',
          }}>
            <div style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--navy)', lineHeight: 1.35 }}>{r.question}</div>
            <div style={{ textAlign: 'center', color: 'var(--accent)', fontSize: 15, fontWeight: 700 }}>→</div>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: 'var(--accent-d)', lineHeight: 1.4 }}>{r.forum}</div>
            <div style={{ textAlign: 'center', color: 'var(--accent)', fontSize: 15, fontWeight: 700 }}>→</div>
            <div style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.4 }}>{r.deciders}</div>
          </div>
        ))}
      </div>
    </Slide>
  )
}
