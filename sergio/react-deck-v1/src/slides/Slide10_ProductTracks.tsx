import { Slide } from '../components/Slide'
import type { SlideProps } from '../types'
import { ConfidencePill } from '../components/ConfidencePill'

interface ProductRow {
  product: string
  track: string
  trackKey: 'A' | 'B' | 'C' | 'D' | 'V'
  tlv: string
  ntradet: string
  avtal: string
  conf: 'VERIFIED' | 'OBSERVED' | 'INFERRED' | 'OPEN'
  note?: string
}

const ROWS: ProductRow[] = [
  { product: 'Vyndaqel', track: 'A → NAG LOK', trackKey: 'A',
    tlv: 'Limited subsidy 61 mg, 2021-09-01 (dnr 3859/2020)',
    ntradet: 'National collaboration archived 2025-09-02; recommendation work moved to NAG LOK',
    avtal: 'Agreement 2024-09-01 → 2026-08-31 (option +1y)',
    conf: 'VERIFIED' },
  { product: 'Vydura', track: 'A', trackKey: 'A',
    tlv: 'Limited subsidy 2023-12-15 (dnr 2035/2023); restriction left in place 2025-10-23',
    ntradet: 'For regional assessment; no NT-rådet recommendation',
    avtal: '—',
    conf: 'VERIFIED' },
  { product: 'Talzenna', track: 'A', trackKey: 'A',
    tlv: 'Limited subsidy 2021-05-21, expanded 2024-04-22 and 2025-11-04 (dnr 2380/2025)',
    ntradet: 'For regional assessment; no NT-rådet recommendation',
    avtal: 'Agreement 2024-06-01 → 2026-05-31 (option +1y)',
    conf: 'VERIFIED' },
  { product: 'Ibrance', track: 'A', trackKey: 'A',
    tlv: 'Limited subsidy 2017-06-15 (dnr 3686/2016); expanded with fulvestrant 2018-02-26',
    ntradet: 'Class-level handling; ribociclib placed as first choice in the 2024 national care programme',
    avtal: '—',
    conf: 'OBSERVED', note: 'Verbatim NT-rådet text not retrieved' },
  { product: 'Lorviqua', track: 'A', trackKey: 'A',
    tlv: '2019-09-30 limited subsidy; 2022-03-28 general subsidy first-line (dnr 3992/2021)',
    ntradet: 'NAC opinion 2020-03-23; the 2024–2025 national care programme lists lorlatinib among three equal first-choice options',
    avtal: '—',
    conf: 'INFERRED', note: 'First-line general subsidy claim is single-sourced; worth direct TLV verification' },
  { product: 'Xtandi (co-marketed with Astellas)', track: 'A', trackKey: 'A',
    tlv: 'Limited subsidy 2021-11-22 (dnr 1939/2021); earlier decision 2014',
    ntradet: 'NT-rådet recommendation archived 2021-12-23',
    avtal: '—',
    conf: 'VERIFIED' },
  { product: 'Tukysa', track: 'A + agreement', trackKey: 'A',
    tlv: 'Included in the reimbursement system from 2022-05-01 (dnr 3694/2021)',
    ntradet: 'NT-rådet has stated it will not issue a recommendation',
    avtal: 'Nationally negotiated agreement 2025-05-01 → 2027-04-30 (option +1y)',
    conf: 'VERIFIED', note: 'Reimbursed product with national-agreement overlay; the engagement forum is the cancer-pathway group, not NT-rådet' },
  { product: 'Elrexfio', track: 'B + C', trackKey: 'B',
    tlv: '—',
    ntradet: 'Entered national collaboration 2023-09-20; "avvakta" 2024-02-08; "kan använda" 2024-06-14',
    avtal: 'Confidential agreement',
    conf: 'VERIFIED' },
  { product: 'Hympavzi', track: 'pending', trackKey: 'C',
    tlv: 'No public TLV decision traced',
    ntradet: 'No public NT-rådet position traced',
    avtal: '—',
    conf: 'OPEN', note: 'Pre-launch / very early launch in Sweden' },
  { product: 'Abrysvo', track: 'C → vaccines', trackKey: 'V',
    tlv: 'Health-economic assessment 2024-06-18 (dnr 3686/2023); no public reimbursement decision traced',
    ntradet: 'avvakta 2023-10-05; reaffirmed 2024-11-08; supplementary analysis delivered Aug/Sep 2025',
    avtal: '—',
    conf: 'OBSERVED', note: 'No final NT-rådet recommendation as of mid-May 2026' },
  { product: 'Prevenar 20 / Apexxnar', track: 'Vaccines', trackKey: 'V',
    tlv: '2022-08-25 limited subsidy (filed under "Apexxnar" — same product)',
    ntradet: 'Sits under Folkhälsomyndigheten programme machinery rather than NT-rådet',
    avtal: 'Nationally procured for the risk-group programme',
    conf: 'OBSERVED', note: 'Pfizer materials say "Prevenar 20"; the public TLV file says "Apexxnar"' },
  { product: 'FSME-IMMUN', track: 'Vaccines', trackKey: 'V',
    tlv: 'Not in the reimbursement system',
    ntradet: 'Not in national collaboration',
    avtal: 'Regional procurement / patient-paid',
    conf: 'OBSERVED', note: 'Folkhälsomyndigheten TBE recommendation issued May 2026 (risk-area 1/2/3)' },
]

const trackColor = (k: string): string => ({
  A: 'var(--track-a)', B: 'var(--track-b)',
  C: 'var(--track-c)', D: 'var(--track-d)', V: 'var(--accent)',
}[k] || 'var(--gray-1)')

export function Slide10_ProductTracks({ isActive }: SlideProps) {
  return (
    <Slide
      isActive={isActive}
      sectionLabel="Per-product mapping"
      title="Where the 12 products sit"
      subtitle="The public TLV decision, the NT-rådet status, and any nationally negotiated agreement that applies. Vaccines sit in their own lane and are noted as such."
    >
      <div className="dmm-wrap" style={{ flex: 1 }}>
        <table className="dmm">
          <thead>
            <tr>
              <th style={{ width: '13%' }}>Product</th>
              <th style={{ width: '8%' }}>Track</th>
              <th style={{ width: '24%' }}>TLV decision</th>
              <th style={{ width: '24%' }}>NT-rådet status</th>
              <th style={{ width: '18%' }}>Agreement (avtal)</th>
              <th style={{ width: '13%' }}>Confidence + note</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map(r => (
              <tr key={r.product}>
                <td className="product">{r.product}</td>
                <td>
                  <span style={{
                    display: 'inline-block', padding: '1px 7px', borderRadius: 8,
                    fontSize: 9.5, fontWeight: 700, background: 'white',
                    border: `1.5px solid ${trackColor(r.trackKey)}`,
                    color: trackColor(r.trackKey),
                  }}>{r.track}</span>
                </td>
                <td style={{ fontSize: 10 }}>{r.tlv}</td>
                <td style={{ fontSize: 10 }}>{r.ntradet}</td>
                <td style={{ fontSize: 10 }}>{r.avtal}</td>
                <td>
                  <ConfidencePill level={r.conf} />
                  {r.note && (
                    <div style={{ fontSize: 9, color: 'var(--gray-1)', fontStyle: 'italic', marginTop: 2 }}>
                      {r.note}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="source-note">
        Sources: TLV decision database, samverkanlakemedel.se product pages, Folkhälsomyndigheten programme pages.
      </div>
    </Slide>
  )
}
