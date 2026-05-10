import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'

/**
 * Stockholm strategic synthesis — three structural anomalies + the Pfizer-2026 priority list.
 */
export function Stockholm06_Synthesis({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Stockholm — strategic synthesis"
      title="Three structural anomalies in Stockholm"
      subtitle="The patterns that make Stockholm not just a bigger version of the rest of Sweden, and what they imply for Pfizer engagement here."
    >
      <div style={{ flex: 1, display: 'grid', gridTemplateRows: 'auto 1fr', gap: 14, overflow: 'hidden' }}>

        {/* Three anomaly cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14 }}>
          {[
            {
              n: '1', tone: 'warn', textColor: 'var(--warn)',
              title: 'Stockholm Abrysvo anomaly',
              body: "Pfizer holds 59.9% of RSV by SEK in Stockholm but a 45.6% minority by units, while the national picture is 64.5% by SEK. GSK's Arexvy outsells Abrysvo dose-for-dose here.",
              impl: 'Implication. The SEK lead in Stockholm is a price-mix illusion. Field engagement should lead with the dose-volume story, not the revenue victory lap.',
            },
            {
              n: '2', tone: 'warn', textColor: 'var(--warn)',
              title: 'CDK4/6 — Stockholm leads the recovery opportunity',
              body: 'Stockholm-S is the largest single recovery brick nationally, roughly 0.78 M kr at 12.6% Ibrance share. Stockholm-NO sits at #6 with around 0.41 M kr.',
              impl: 'The implication for engagement is brick-level rather than region-wide. The 17.5% national share figure averages a wide spread across bricks within Stockholm.',
            },
            {
              n: '3', tone: 'good', textColor: 'var(--good)',
              title: 'Hympavzi launch site',
              body: 'Stockholm has the largest haemophilia market in Sweden by SEK (BeneFIX 40.6 M kr plus Refacto AF). Karolinska is the natural Hympavzi launch infrastructure once a Swedish access route is established.',
              impl: "Implication. The northern cornerstone for ATTR anchors in Umeå, but Hympavzi's commercial launch site belongs in Stockholm where the patient pool exists.",
            },
          ].map(c => (
            <div key={c.n} className={`card card-${c.tone}`} style={{ padding: '12px 14px' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: c.textColor, marginBottom: 6 }}>
                {c.title}
              </div>
              <p style={{ fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55, margin: 0 }}>
                {c.body}
              </p>
              <p style={{ fontSize: 10, color: 'var(--navy)', fontWeight: 500, lineHeight: 1.5, margin: '8px 0 0 0' }}>
                {c.impl}
              </p>
            </div>
          ))}
        </div>

        {/* Stockholm-2026 priority list */}
        <div className="card card-accent" style={{ padding: '14px 18px' }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--navy)', marginBottom: 10 }}>
            Stockholm-specific priorities for Pfizer in 2026
          </div>
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 24px',
            fontSize: 10.5, color: 'var(--navy-soft)', lineHeight: 1.55,
          }}>
            <div>
              <strong style={{ color: 'var(--navy)' }}>CDK4/6 — class-naive capture is the leading edge.</strong>
              {' '}Stockholm shows 10.3% Pfizer share among class-naive starts versus a 7% national rate. The
              absolute volume of around 165 starts in six months is materially larger than any other region,
              which is what makes the brick-level recovery analysis later in the deck most actionable here.
            </div>
            <div>
              <strong style={{ color: 'var(--navy)' }}>RSV — frame the conversation in doses, not SEK.</strong>
              {' '}Stockholm is the only region where Pfizer's RSV share sits below 50% by units even though
              it leads by SEK. Field engagement reads more accurately when it leads with the dose volumes.
            </div>
            <div>
              <strong style={{ color: 'var(--navy)' }}>Precision oncology routes through Karolinska.</strong>
              {' '}Tukysa, Talzenna and Lorviqua all rely on the molecular-testing infrastructure at Karolinska.
              The largest absolute opportunity for HER2-positive brain metastases, BRCA-mutated mBC and
              ALK-positive NSCLC sits here, even where the per-100k rates run at or below national.
            </div>
            <div>
              <strong style={{ color: 'var(--navy)' }}>Stockholm-Gotland governance is a coordinated set.</strong>
              {' '}The regional drugs and therapeutics committee, the sjukvårdsregional NT-rådet representative
              and the NSG representative all sit within the same governance perimeter. Treating engagement
              across them as one connected motion tends to read better than independent threads.
            </div>
          </div>
        </div>
      </div>
      <div className="source-note">
        Sources: IQVIA Sell-In and IQVIA Vaccines aggregations, 78-brick CDK4/6 priority scoring, Stockholm-Gotland governance map.
      </div>
    </Slide>
  )
}
