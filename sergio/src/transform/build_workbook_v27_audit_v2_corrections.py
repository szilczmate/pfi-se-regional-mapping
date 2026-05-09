# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v27.xlsx — audit v2 corrections.

Phase A scope:
- Fix internal README sheet ("51 sheets" → "60 sheets")
- Fix Build pipeline sheet QC line (was "QC v2 NEEDS UPDATE for v26")
- Update Evidence Ledger EX-04 + EX-06 (remove pending-IQVIA-Kisqali language)
- NEW SHEET: "Pfizer total footprint" — unified all-product per-region view (Vaccines + RD/IM + Oncology)
- NEW SHEET: "Verzenios trajectory" — last-6-month slope analysis per region (vs 1H/2H comparison only)
"""

from copy import copy
from pathlib import Path
from shutil import copyfile
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V26 = ROOT / "delivery" / "06_master_workbook_v26.xlsx"
V27_WORKING = ROOT / "working" / "data" / "master" / "master_workbook_v27.xlsx"
V27_DELIVERY = ROOT / "delivery" / "06_master_workbook_v27.xlsx"
RAW_DIR = ROOT / "working" / "data" / "raw"
VAC_RAW = RAW_DIR / "VitiScience_Vaccines_Apr-02-2026.xlsx"
RDIM_RAW = RAW_DIR / "VitiScience RD_IM_Apr-27-2026.xlsx"
ONC_RAW = RAW_DIR / "VitiScience Oncology_Apr-27-2026.xlsx"

COUNTY_TO_REGION = {
    '01': 'Region Stockholm', '03': 'Region Uppsala', '04': 'Region Sörmland',
    '05': 'Region Östergötland', '06': 'Region Jönköpings län', '07': 'Region Kronoberg',
    '08': 'Region Kalmar', '09': 'Region Gotland', '10': 'Region Blekinge',
    '12': 'Region Skåne', '13': 'Region Halland', '14': 'Västra Götalandsregionen',
    '17': 'Region Värmland', '18': 'Region Örebro län', '19': 'Region Västmanland',
    '20': 'Region Dalarna', '21': 'Region Gävleborg', '22': 'Region Västernorrland',
    '23': 'Region Jämtland Härjedalen', '24': 'Region Västerbotten',
    '25': 'Region Norrbotten',
}

PFIZER_PRODUCTS = {
    # Vaccines
    'ABRYSVO': 'RSV vaccine',
    'PREVENAR 13': 'Pneumococcal (legacy)',
    'PREVENAR 20': 'Pneumococcal (adult)',
    'FSME-IMMUN VUXEN': 'TBE vaccine (adult)',
    'FSME-IMMUN JUNIOR': 'TBE vaccine (junior)',
    # RD/IM
    'VYNDAQEL': 'ATTR-CM (rare)',
    'VYDURA': 'Migraine (CGRP)',
    'PAXLOVID': 'COVID antiviral',
    'BENEFIX': 'Haemophilia B (FIX)',
    'REFACTO AF': 'Haemophilia A (FVIII, legacy)',
    # Oncology
    'IBRANCE': 'CDK4/6 (BC)',
    'TUKYSA': 'HER2-SM (BC brain mets)',
    'TALZENNA': 'PARP (BC + HRR-mCRPC)',
    'LORVIQUA': 'ALK (NSCLC)',
    'XALKORI': 'ALK (NSCLC, legacy)',
    'ELREXFIO': 'BCMA bispecific (MM)',
    'XTANDI': 'Androgen receptor (mCRPC)',
}

HDR_FILL = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
NEW_FILL = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")
AUDIT_FILL = PatternFill(start_color="E8F0FF", end_color="E8F0FF", fill_type="solid")
DEFAULT_ALIGN = Alignment(vertical="center", horizontal="left", wrap_text=True)


def style_header(ws, row=1):
    for cell in ws[row]:
        if cell.value is not None:
            cell.fill = HDR_FILL
            cell.font = HDR_FONT
            cell.alignment = DEFAULT_ALIGN
    ws.row_dimensions[row].height = 26


def load_pops(wb):
    ws = wb['Region master']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    region_col = headers.index('Region')
    pop_col = headers.index('Population')
    return {row[region_col]: row[pop_col] for row in ws.iter_rows(min_row=2, values_only=True) if row[region_col]}


def aggregate_iqvia_for_pfizer(file_path, sheet_names=None):
    """Returns {(region, product): {sek, units, monthly_units (list)}}"""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheets = sheet_names or wb_raw.sheetnames
    out = defaultdict(lambda: {'sek': 0.0, 'units': 0.0, 'monthly_units': None})

    for sn in sheets:
        ws = wb_raw[sn]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        # Sell-in cols (handle both "Sell-In Value" and "Sell In Value" styles)
        sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
        units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]

        for row in ws.iter_rows(min_row=2, values_only=True):
            product = row[1]
            if not product or product not in PFIZER_PRODUCTS:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2])
            if not region:
                continue
            key = (region, product)
            sek = sum(v for i, v in enumerate(row) if i in sek_cols and v is not None)
            units = sum(v for i, v in enumerate(row) if i in units_cols and v is not None)
            out[key]['sek'] += sek
            out[key]['units'] += units
            # Monthly units
            if out[key]['monthly_units'] is None:
                out[key]['monthly_units'] = [0.0] * len(units_cols)
            for i, idx in enumerate(units_cols):
                v = row[idx]
                if v is not None and i < len(out[key]['monthly_units']):
                    out[key]['monthly_units'][i] += v
    return out


def aggregate_verzenios_monthly(file_path):
    """Returns {region: {monthly_units: [...]}} for Verzenios specifically (Lilly, abemaciclib)."""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw['Ibrance']  # CDK4/6 sheet
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
    month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip() for i in sek_cols]

    out = defaultdict(lambda: [0.0] * len(units_cols))
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        if product != 'VERZENIOS':
            continue
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if not region:
            continue
        for i, idx in enumerate(units_cols):
            v = row[idx]
            if v is not None:
                out[region][i] += v
    return out, month_labels


# =============================================================================
# Audit fixes
# =============================================================================

def fix_internal_readme(wb):
    """A8 says '51 sheets'; v27 has 62. Update."""
    ws = wb['README']
    n = 0
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                # Update sheet count
                replacements = [
                    ('51 sheets', '62 sheets'),
                    ('Fifty-one sheets', 'Sixty-two sheets'),
                    ('Fifty-one-sheet', 'Sixty-two-sheet'),
                    ('master workbook v23', 'master workbook v27'),
                    ('master workbook v25', 'master workbook v27'),
                    ('master workbook v26', 'master workbook v27'),
                    ('Version 23', 'Version 27'),
                    ('Version 25', 'Version 27'),
                    ('Version 26', 'Version 27'),
                ]
                new_value = cell.value
                changed = False
                for old, new in replacements:
                    if old in new_value:
                        new_value = new_value.replace(old, new)
                        changed = True
                if changed:
                    cell.value = new_value
                    cell.fill = AUDIT_FILL
                    n += 1
    print(f'  Fixed {n} stale references in internal README sheet')


def fix_build_pipeline(wb):
    """Build pipeline sheet QC row: was 'QC v2 NEEDS UPDATE for v26'. Update for v27."""
    ws = wb['Build pipeline']
    n = 0
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                if 'NEEDS UPDATE for v26' in cell.value or 'QC v2' in cell.value:
                    cell.value = cell.value.replace(
                        'QC v2', 'QC v3').replace(
                        'NEEDS UPDATE for v26', 'refreshed for v27 — see qc_v4_delivery.py')
                    cell.fill = AUDIT_FILL
                    n += 1
    # Add a row for v26 → v27 (this build)
    ws.append(['Workbook v26 → v27 (THIS BUILD)', '06_master_workbook_v27.xlsx', 'build_workbook_v27_audit_v2_corrections.py',
               'audit v2 corrections: version-control cleanup; Evidence Ledger EX-04/06 stale-Kisqali language fix; '
               'NEW Pfizer total footprint sheet (unified Vaccines + RD/IM + Oncology view); NEW Verzenios trajectory sheet '
               '(last-6-month slope analysis to test "continues compounding" claim).'])
    for cell in ws[ws.max_row]:
        cell.fill = NEW_FILL
        cell.alignment = DEFAULT_ALIGN
    print(f'  Fixed {n} stale Build pipeline refs + added v26→v27 row')


def fix_evidence_ledger_ex04_ex06(wb):
    """EX-04 and EX-06 still preserve pending-IQVIA-Kisqali language."""
    ws = wb['Evidence ledger']
    n = 0
    for row in ws.iter_rows(min_row=2, values_only=False):
        if row[0].value in ('EX-04', 'EX-06'):
            for cell in row[6:8]:  # Decision rule, Evidence trail
                if cell.value and isinstance(cell.value, str):
                    new_text = cell.value
                    if 'pending IQVIA Kisqali validation' in new_text:
                        new_text = new_text.replace(
                            'pending IQVIA Kisqali validation',
                            'IQVIA Kisqali volume now Observed (G2 closed 2026-04-27): Stockholm 5,930 / VGR 2,738 units')
                    if 'Needs Pfizer validation: IQVIA Kisqali' in new_text:
                        new_text = new_text.replace(
                            'Needs Pfizer validation: IQVIA Kisqali',
                            '[CLOSED 2026-04-27 via IQVIA Oncology] IQVIA Kisqali')
                    if new_text != cell.value:
                        cell.value = new_text
                        cell.fill = AUDIT_FILL
                        n += 1
    print(f'  Updated EX-04/EX-06 to remove pending-Kisqali language ({n} cells)')


def add_pfizer_total_footprint_sheet(wb, vac_agg, rdim_agg, onc_agg, pops):
    """B1.P1 — unified Pfizer presence per region across all 11 IQVIA-visible products."""
    if 'Pfizer total footprint' in wb.sheetnames:
        del wb['Pfizer total footprint']
    ws = wb.create_sheet('Pfizer total footprint')

    # Layout: Region | Population | per-product SEK columns | per-product units columns | Total SEK | Total units | per-100k | rank
    products_ordered = [
        ('Vaccines', ['ABRYSVO', 'PREVENAR 20', 'PREVENAR 13', 'FSME-IMMUN VUXEN', 'FSME-IMMUN JUNIOR']),
        ('RD/IM', ['VYNDAQEL', 'VYDURA', 'PAXLOVID', 'BENEFIX', 'REFACTO AF']),
        ('Oncology', ['IBRANCE', 'TUKYSA', 'TALZENNA', 'LORVIQUA', 'XALKORI', 'ELREXFIO', 'XTANDI']),
    ]
    flat_products = [p for _, plist in products_ordered for p in plist]

    headers = ['Region', 'Population']
    for portfolio, plist in products_ordered:
        for p in plist:
            headers.append(f'{p} SEK (3yr)')
    headers += ['Total Pfizer SEK', 'Total Pfizer SEK per 100k', 'Pfizer SEK rank']
    headers += ['Vaccines SEK', 'RD/IM SEK', 'Oncology SEK']
    ws.append(headers)
    style_header(ws)

    # Combine aggregators
    all_agg = {**vac_agg}
    for k, v in rdim_agg.items():
        all_agg[k] = v
    for k, v in onc_agg.items():
        all_agg[k] = v

    # Row per region
    region_rows = []
    for region in pops.keys():
        row = [region, pops[region]]
        portfolio_totals = {'Vaccines': 0.0, 'RD/IM': 0.0, 'Oncology': 0.0}
        for portfolio, plist in products_ordered:
            for p in plist:
                d = all_agg.get((region, p), {'sek': 0.0})
                row.append(d['sek'])
                portfolio_totals[portfolio] += d['sek']
        total_sek = sum(portfolio_totals.values())
        per_100k = total_sek / pops[region] * 100000 if pops[region] else 0
        row.extend([total_sek, per_100k, 0])  # rank filled later
        row.extend([portfolio_totals['Vaccines'], portfolio_totals['RD/IM'], portfolio_totals['Oncology']])
        region_rows.append(row)

    # Compute SEK rank (1 = highest)
    region_rows.sort(key=lambda r: -r[len(headers) - 6])  # by Total Pfizer SEK
    for rank, row in enumerate(region_rows, start=1):
        row[len(headers) - 4] = rank
    # Sort back by rank for display
    for row in region_rows:
        ws.append(row)

    # National total row
    ws.append([])
    nat_pop = sum(pops.values())
    nat_total = sum(r[len(headers) - 6] for r in region_rows)
    nat_row = ['NATIONAL TOTAL', nat_pop]
    for col_idx in range(2, len(headers) - 6):
        nat_row.append(sum(r[col_idx] for r in region_rows))
    nat_row.extend([nat_total, nat_total / nat_pop * 100000, ''])
    nat_row.extend([
        sum(r[-3] for r in region_rows),
        sum(r[-2] for r in region_rows),
        sum(r[-1] for r in region_rows),
    ])
    ws.append(nat_row)

    # Column widths
    for i, h in enumerate(headers):
        ws.column_dimensions[get_column_letter(i+1)].width = 30 if i == 0 else 14
    ws.freeze_panes = 'C2'
    print(f'  Created Pfizer total footprint sheet (21 regions × 17 Pfizer products)')


def add_verzenios_trajectory_sheet(wb):
    """B1.P1 — last-6-month slope analysis to test "continues compounding" claim."""
    if 'Verzenios trajectory' in wb.sheetnames:
        del wb['Verzenios trajectory']
    ws = wb.create_sheet('Verzenios trajectory')

    verz_agg, month_labels = aggregate_verzenios_monthly(ONC_RAW)

    n_months = len(month_labels)
    last_6_start = n_months - 6
    prev_6_start = n_months - 12

    headers = ['Region', 'First-6mo units', 'Mid-window-6mo units', 'Last-6mo units',
               'Last-6 vs Prev-6 (%)', 'Trajectory verdict']
    ws.append(headers)
    style_header(ws)

    rows = []
    for region in sorted(verz_agg.keys()):
        monthly = verz_agg[region]
        first_6 = sum(monthly[:6])
        mid_6 = sum(monthly[(n_months // 2 - 3):(n_months // 2 + 3)])
        last_6 = sum(monthly[last_6_start:])
        prev_6 = sum(monthly[prev_6_start:last_6_start])

        if prev_6 > 0:
            pct = round(100 * (last_6 - prev_6) / prev_6, 1)
        else:
            pct = None

        if pct is None:
            verdict = 'No prior-6mo baseline'
        elif pct > 30:
            verdict = 'COMPOUNDING (last-6 still growing >30%)'
        elif pct > 5:
            verdict = 'GROWING (last-6 vs prev-6 +5–30%)'
        elif pct >= -5:
            verdict = 'PLATEAUING (last-6 vs prev-6 ±5%)'
        elif pct >= -20:
            verdict = 'DECLINING (last-6 vs prev-6 −5–20%)'
        else:
            verdict = 'CONTRACTING (last-6 vs prev-6 <−20%)'

        rows.append([region, first_6, mid_6, last_6, pct, verdict])

    rows.sort(key=lambda r: -(r[3] or 0))
    for row in rows:
        ws.append(row)

    # National
    ws.append([])
    nat_first_6 = sum(r[1] for r in rows)
    nat_mid_6 = sum(r[2] for r in rows)
    nat_last_6 = sum(r[3] for r in rows)
    nat_prev_6 = nat_last_6 / (1 + max(rows[0][4] or 0, 0)/100) if rows else 0  # rough
    # Actually compute national prev 6
    nat_monthly = [sum(verz_agg[r][i] for r in verz_agg.keys()) for i in range(n_months)]
    nat_prev_6 = sum(nat_monthly[prev_6_start:last_6_start])
    nat_last_6_check = sum(nat_monthly[last_6_start:])
    nat_pct = round(100 * (nat_last_6_check - nat_prev_6) / nat_prev_6, 1) if nat_prev_6 > 0 else None
    nat_verdict = 'National Verzenios trajectory'
    if nat_pct > 30:
        nat_verdict = 'NATIONAL: COMPOUNDING'
    elif nat_pct > 5:
        nat_verdict = 'NATIONAL: GROWING'
    elif nat_pct >= -5:
        nat_verdict = 'NATIONAL: PLATEAUING'
    elif nat_pct >= -20:
        nat_verdict = 'NATIONAL: DECLINING'
    else:
        nat_verdict = 'NATIONAL: CONTRACTING'
    ws.append(['NATIONAL TOTAL', nat_first_6, nat_mid_6, nat_last_6, nat_pct, nat_verdict])

    # Notes
    ws.append([])
    ws.append(['Methods note', f'Last-6-month window: {month_labels[last_6_start]} – {month_labels[-1]}.'])
    ws.append(['', f'Prev-6-month window: {month_labels[prev_6_start]} – {month_labels[last_6_start - 1]}.'])
    ws.append(['', 'Verdict thresholds: COMPOUNDING >30% / GROWING +5–30% / PLATEAUING ±5% / DECLINING −5–20% / CONTRACTING <−20%.'])
    ws.append(['Why this matters', 'audit v2 P1 finding: 1H vs 2H comparison overstates trend if Verzenios was '
               'ramping from a low base. Last-6-month slope tests whether "continues compounding" claim is empirically '
               'supported in the most recent window.'])

    widths = [30, 16, 18, 16, 18, 50]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'
    print(f'  Created Verzenios trajectory sheet (21 regions + national, last-6-month slope analysis)')


def main():
    print(f'Copying v26 → v27')
    copyfile(V26, V27_WORKING)
    wb = openpyxl.load_workbook(V27_WORKING)
    pops = load_pops(wb)

    print('Aggregating IQVIA data for Pfizer products...')
    vac_agg = aggregate_iqvia_for_pfizer(VAC_RAW)
    rdim_agg = aggregate_iqvia_for_pfizer(RDIM_RAW)
    onc_agg = aggregate_iqvia_for_pfizer(ONC_RAW)

    print('\n=== Audit v2 corrections ===')
    fix_internal_readme(wb)
    fix_build_pipeline(wb)
    fix_evidence_ledger_ex04_ex06(wb)

    print('\n=== New analytical sheets ===')
    add_pfizer_total_footprint_sheet(wb, vac_agg, rdim_agg, onc_agg, pops)
    add_verzenios_trajectory_sheet(wb)

    wb.save(V27_WORKING)
    print(f'\nSaved {V27_WORKING}')

    copyfile(V27_WORKING, V27_DELIVERY)
    print(f'Copied to {V27_DELIVERY}')

    wb_check = openpyxl.load_workbook(V27_WORKING, read_only=True)
    print(f'\nv27 has {len(wb_check.sheetnames)} sheets')
    for s in ['Pfizer total footprint', 'Verzenios trajectory']:
        if s in wb_check.sheetnames:
            print(f'  ★ NEW in v27: {s}')


if __name__ == '__main__':
    main()
