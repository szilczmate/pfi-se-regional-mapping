import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

const TRACKS = [
  {
    key: 'A',
    label: 'Track A · Outpatient prescription (förmån)',
    body: <>
      TLV decides nationally on subsidy and the maximum public price. The decision applies
      in every region and is not repeated regionally. Regions pay through their own budgets
      plus the state grant, which sits at 41,461 mnkr in 2026.
      <br /><br />
      Several förmån products also carry a nationally negotiated agreement on top of the TLV
      decision. The agreement manages commercial terms; it does not change the access track.
    </>,
    klass: 'card-track-a',
  },
  {
    key: 'B',
    label: 'Track B · Hospital / requisition (rekvisition)',
    body: <>
      Regions buy directly under public-procurement law for hospital-administered medicines,
      typically infusions and ATMP-like therapies. Net prices are usually confidential, which
      makes the visible part of the conversation look quite different from the förmån track.
    </>,
    klass: 'card-track-b',
  },
  {
    key: 'C',
    label: 'Track C · National managed introduction',
    body: <>
      NT-rådet decides whether a new medicine enters national collaboration and, if it does,
      recommends to regions in a four-phrase language:{' '}
      <em>bör använda, kan använda, bör avstå, avvakta</em>, sometimes with a ranking
      between alternatives or with restrictions. The recommendations are not statutorily
      binding but in practice they are followed.
    </>,
    klass: 'card-track-c',
  },
  {
    key: 'D',
    label: 'Track D · Sub-regional implementation',
    body: <>
      Each region's drugs and therapeutics committee publishes its own formulary. National
      care-programme groups (NPO, NAG, RCC) write the clinical guidance that operationalises
      the decisions inside the clinics. Specialist chefläkare hold the final prescribing call.
    </>,
    klass: 'card-track-d',
  },
]

export function Slide05_FourTracks({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="The architecture"
      title="Sweden's pharmaceutical access architecture"
      subtitle="Four parallel decision tracks, plus a fifth for vaccines. The track a product sits on determines where its access is decided."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, overflow: 'hidden' }}>
        {TRACKS.map(t => (
          <div key={t.key} className={`card ${t.klass}`} style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{
              fontSize: 12, fontWeight: 700,
              color: t.key === 'A' ? 'var(--track-a)' :
                     t.key === 'B' ? 'var(--track-b)' :
                     t.key === 'C' ? 'var(--track-c)' : 'var(--track-d)',
              marginBottom: 6,
            }}>{t.label}</div>
            <div style={{ fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55 }}>
              {t.body}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: 12, padding: '8px 14px', background: 'var(--bg-soft)',
        borderLeft: '3px solid var(--accent)', borderRadius: 3,
        fontSize: 11, color: 'var(--navy-soft)', lineHeight: 1.55,
      }}>
        <strong style={{ color: 'var(--navy)' }}>Track E · Vaccines.</strong> Vaccines run
        on a fifth pattern. Folkhälsomyndigheten sets the recommendations and runs the
        national programmes; regions execute through procurement. Some adult vaccines
        (e.g. Apexxnar / Prevenar 20) also carry a TLV reimbursement decision for risk
        groups, but the operative decision sits with the public-health authority and
        regional procurement.
        <br /><br />
        <strong style={{ color: 'var(--navy)' }}>RSV is the exception.</strong> Rather than
        the standard vaccine route, it was steered through Track C (NT-rådet managed
        introduction). The track a product lands on is decided case by case,
        not by category.
      </div>

      <div className="source-note">
        Sources: TLV, samverkanlakemedel.se, SKR Meddelande 2/2026 (Överenskommelse läkemedelsförmånerna 2026), the public-procurement law (LOU/LUF).
      </div>
    </Slide>
  )
}
