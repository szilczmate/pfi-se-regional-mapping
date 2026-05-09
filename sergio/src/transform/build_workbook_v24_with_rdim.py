# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v24.xlsx — integrates IQVIA RD/IM extract (received 2026-04-27).

Three new sheets:
- RD-IM IQVIA detail — long-format per region × product × monthly
- ATTR competitive landscape — Vyndaqel vs AMVUTTRA vs BEYONTTRA per region
- Pfizer RD-IM footprint — Pfizer-only summary (Vyndaqel, Vydura, Paxlovid, BeneFIX, Refacto AF)

Updates:
- Evidence Ledger CH-04 confidence: Modeled → Observed (Norrland cluster IQVIA-confirmed)
- Add new claim CH-14: AMVUTTRA + BEYONTTRA Swedish entry threatens Vyndaqel mechanism dominance
- Plays detail P1 validation row #2 (Hympavzi launch): annotation that confirmed not launched as of Mar 2026
"""

from copy import copy
from pathlib import Path
from shutil import copyfile
from collections import defaultdict
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V23 = ROOT / "delivery" / "06_master_workbook_v23.xlsx"
V24_WORKING = ROOT / "working" / "data" / "master" / "master_workbook_v24.xlsx"
V24_DELIVERY = ROOT / "delivery" / "06_master_workbook_v24.xlsx"
RDIM_RAW = ROOT / "working" / "data" / "raw" / "VitiScience RD_IM_Apr-27-2026.xlsx"

# Map IQVIA county council codes (first 2 digits) to canonical region names
COUNTY_TO_REGION = {
    '01': 'Region Stockholm', '03': 'Region Uppsala', '04': 'Region Sörmland',
    '05': 'Region Östergötland', '06': 'Region Jönköpings län', '07': 'Region Kronoberg',
    '08': 'Region Kalmar', '09': 'Region Gotland', '10': 'Region Blekinge',
    '12': 'Region Skåne', '13': 'Region Halland', '14': 'Västra Götalandsregionen',
    '17': 'Region Värmland', '18': 'Region Örebro län', '19': 'Region Västmanland',
    '20': 'Region Dalarna', '21': 'Region Gävleborg', '22': 'Region Västernorrland',
    '23': 'Region Jämtland Härjedalen', '24': 'Region Västerbotten',
    '25': 'Region Norrbotten', '00': 'Unknown',
}

# Population per region (matches Region master in v23)
POP = {
    'Region Stockholm': 2470000, 'Region Uppsala': 401000, 'Region Sörmland': 304000,
    'Region Östergötland': 470000, 'Region Jönköpings län': 369000, 'Region Kronoberg': 207000,
    'Region Kalmar': 247000, 'Region Gotland': 61000, 'Region Blekinge': 159000,
    'Region Skåne': 1411000, 'Region Halland': 343000, 'Västra Götalandsregionen': 1755000,
    'Region Värmland': 282000, 'Region Örebro län': 308000, 'Region Västmanland': 281000,
    'Region Dalarna': 290000, 'Region Gävleborg': 287000, 'Region Västernorrland': 245000,
    'Region Jämtland Härjedalen': 132000, 'Region Västerbotten': 281138,
    'Region Norrbotten': 248620,
}

PFIZER_PRODUCTS_RDIM = {'VYNDAQEL', 'PAXLOVID', 'VYDURA', 'BENEFIX', 'REFACTO AF'}

# Header style
HDR_FILL = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
NEW_FILL = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")  # light amber
DEFAULT_ALIGN = Alignment(vertical="center", horizontal="left", wrap_text=True)


def style_header(ws, row=1):
    for cell in ws[row]:
        if cell.value is not None:
            cell.fill = HDR_FILL
            cell.font = HDR_FONT
            cell.alignment = DEFAULT_ALIGN
    ws.row_dimensions[row].height = 26


def aggregate_iqvia(raw_path):
    """Returns dict: {sheet_name: list of dicts with region/product/atc/manufacturer/sek/units/months}"""
    wb_raw = openpyxl.load_workbook(raw_path, read_only=True, data_only=True)
    out = {}
    for sheet_name in wb_raw.sheetnames:
        ws = wb_raw[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sell_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
        # Sell-in column months in order
        sell_month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip() for i in sell_cols]

        # Aggregate region × product (sum across bricks)
        agg = defaultdict(lambda: {
            'sek_total': 0.0, 'units_total': 0.0,
            'monthly_sek': [0.0] * len(sell_cols),
            'monthly_units': [0.0] * len(units_cols),
            'atc': '', 'manufacturer': '',
        })
        for row in ws.iter_rows(min_row=2, values_only=True):
            atc = row[0]
            product = row[1]
            county = str(row[7] or '')
            county_code = county[:2] if county else ''
            region = COUNTY_TO_REGION.get(county_code, 'Unknown')
            if not product or region == 'Unknown':
                continue
            key = (region, product)
            agg[key]['atc'] = atc
            agg[key]['manufacturer'] = 'Pfizer' if product in PFIZER_PRODUCTS_RDIM else 'Competitor'
            for i, idx in enumerate(sell_cols):
                v = row[idx]
                if v is not None:
                    agg[key]['monthly_sek'][i] += v
                    agg[key]['sek_total'] += v
            for i, idx in enumerate(units_cols):
                v = row[idx]
                if v is not None:
                    agg[key]['monthly_units'][i] += v
                    agg[key]['units_total'] += v
        out[sheet_name] = (agg, sell_month_labels)
    return out


def add_rdim_detail_sheet(wb, iqvia_agg):
    """Long-format sheet with one row per region × product, monthly columns."""
    if 'RD-IM IQVIA detail' in wb.sheetnames:
        del wb['RD-IM IQVIA detail']
    ws = wb.create_sheet('RD-IM IQVIA detail')

    # Headers
    sample_months = next(iter(iqvia_agg.values()))[1]
    headers = ['Therapy area', 'Region', 'Product', 'ATC', 'Manufacturer',
               'Total Sell-In SEK', 'Total Units']
    headers += [f'SEK {m}' for m in sample_months]
    headers += [f'Units {m}' for m in sample_months]
    ws.append(headers)
    style_header(ws)

    for ta, (agg, _months) in iqvia_agg.items():
        # Sort by SEK descending
        sorted_keys = sorted(agg.keys(), key=lambda k: -agg[k]['sek_total'])
        for (region, product) in sorted_keys:
            d = agg[(region, product)]
            row = [ta, region, product, d['atc'], d['manufacturer'],
                   d['sek_total'], d['units_total']]
            row += d['monthly_sek']
            row += d['monthly_units']
            ws.append(row)

    # Column widths
    ws.column_dimensions['A'].width = 16
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 26
    ws.column_dimensions['D'].width = 38
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 14
    for i in range(len(sample_months) * 2):
        ws.column_dimensions[get_column_letter(8 + i)].width = 12
    ws.freeze_panes = 'F2'
    return ws


def add_attr_competitive_sheet(wb, iqvia_agg):
    """ATTR market split per region: Vyndaqel vs AMVUTTRA vs BEYONTTRA."""
    if 'ATTR competitive landscape' in wb.sheetnames:
        del wb['ATTR competitive landscape']
    ws = wb.create_sheet('ATTR competitive landscape')

    headers = ['Region', 'Population',
               'VYNDAQEL units', 'VYNDAQEL SEK', 'Vyndaqel units per 100k',
               'AMVUTTRA units', 'AMVUTTRA SEK',
               'BEYONTTRA units', 'BEYONTTRA SEK',
               'Total ATTR market SEK', 'Pfizer share %', 'Notes']
    ws.append(headers)
    style_header(ws)

    attr_agg, _ = iqvia_agg['ATTR']
    regions = sorted(POP.keys(), key=lambda r: -attr_agg.get((r, 'VYNDAQEL'), {'units_total': 0})['units_total'])
    for region in regions:
        v = attr_agg.get((region, 'VYNDAQEL'), {'sek_total': 0, 'units_total': 0})
        a = attr_agg.get((region, 'AMVUTTRA'), {'sek_total': 0, 'units_total': 0})
        b = attr_agg.get((region, 'BEYONTTRA'), {'sek_total': 0, 'units_total': 0})
        total_sek = v['sek_total'] + a['sek_total'] + b['sek_total']
        pfizer_share = 100 * v['sek_total'] / total_sek if total_sek > 0 else 0
        per_100k = v['units_total'] / POP[region] * 100000

        notes = ''
        if region in ('Region Norrbotten', 'Region Västerbotten'):
            notes = 'Skellefteå founder cluster — TTR V30M variant'
        elif region == 'Region Örebro län' and pfizer_share < 50:
            notes = 'Outlier: low Pfizer share suggests active switching to non-tafamidis therapy'

        ws.append([region, POP[region], v['units_total'], v['sek_total'],
                   round(per_100k, 1), a['units_total'], a['sek_total'],
                   b['units_total'], b['sek_total'], total_sek,
                   round(pfizer_share, 1), notes])

    # Add summary row
    ws.append([])
    norrland_v = sum(attr_agg.get((r, 'VYNDAQEL'), {'units_total': 0})['units_total']
                     for r in ['Region Norrbotten', 'Region Västerbotten'])
    national_v = sum(attr_agg.get((r, 'VYNDAQEL'), {'units_total': 0})['units_total']
                     for r in POP.keys())
    norrland_pop = POP['Region Norrbotten'] + POP['Region Västerbotten']
    national_pop = sum(POP.values())
    ws.append(['Norrland (Norrbotten + Västerbotten)', norrland_pop, norrland_v, '',
               round(norrland_v / norrland_pop * 100000, 1), '', '', '', '', '', '',
               f'{100 * norrland_v / national_v:.1f}% of national Vyndaqel units in {100 * norrland_pop / national_pop:.1f}% of population'])
    ws.append(['National total', national_pop, national_v, '',
               round(national_v / national_pop * 100000, 1), '', '', '', '', '', '', ''])

    # Column widths
    widths = [30, 12, 16, 18, 18, 14, 16, 16, 16, 20, 14, 60]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'
    return ws


def add_pfizer_rdim_footprint_sheet(wb, iqvia_agg):
    """Pfizer-only RD/IM footprint per region (Vyndaqel + Vydura + Paxlovid + BeneFIX + Refacto AF)."""
    if 'Pfizer RD-IM footprint' in wb.sheetnames:
        del wb['Pfizer RD-IM footprint']
    ws = wb.create_sheet('Pfizer RD-IM footprint')

    headers = ['Region', 'Population',
               'Vyndaqel SEK', 'Vyndaqel units',
               'Vydura SEK', 'Vydura units',
               'Paxlovid SEK', 'Paxlovid units',
               'BeneFIX SEK', 'BeneFIX units',
               'Refacto AF SEK', 'Refacto AF units',
               'Total Pfizer RD/IM SEK', 'Total Pfizer RD/IM units']
    ws.append(headers)
    style_header(ws)

    # Map: product → therapy area sheet
    PRODUCT_TA = {
        'VYNDAQEL': 'ATTR', 'PAXLOVID': 'Covid', 'VYDURA': 'Migraine',
        'BENEFIX': 'Haemophilia', 'REFACTO AF': 'Haemophilia',
    }

    def get(product, region):
        ta = PRODUCT_TA.get(product)
        agg = iqvia_agg.get(ta, ({}, []))[0]
        return agg.get((region, product), {'sek_total': 0, 'units_total': 0})

    rows = []
    for region in POP.keys():
        v = get('VYNDAQEL', region)
        vyd = get('VYDURA', region)
        p = get('PAXLOVID', region)
        bf = get('BENEFIX', region)
        rf = get('REFACTO AF', region)
        total_sek = v['sek_total'] + vyd['sek_total'] + p['sek_total'] + bf['sek_total'] + rf['sek_total']
        total_u = v['units_total'] + vyd['units_total'] + p['units_total'] + bf['units_total'] + rf['units_total']
        rows.append([region, POP[region],
                     v['sek_total'], v['units_total'],
                     vyd['sek_total'], vyd['units_total'],
                     p['sek_total'], p['units_total'],
                     bf['sek_total'], bf['units_total'],
                     rf['sek_total'], rf['units_total'],
                     total_sek, total_u])
    rows.sort(key=lambda r: -r[12])  # by total Pfizer SEK desc
    for row in rows:
        ws.append(row)

    # National total
    nat = ['NATIONAL TOTAL', sum(POP.values())]
    for col in range(2, 14):
        nat.append(sum(r[col] for r in rows))
    ws.append([])
    ws.append(nat)

    widths = [30, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 18, 18]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'
    return ws


def update_evidence_ledger(wb):
    """Bump CH-04 → Observed; add new claim CH-14 about ATTR competitive entry."""
    ws = wb['Evidence ledger']
    # Find CH-04 row
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'CH-04':
            ws.cell(row=row[0].row, column=6).value = 'Observed'
            ws.cell(row=row[0].row, column=7).value = (
                'IQVIA RD/IM extract 2026-04-27 confirms Vyndaqel units per 100k: '
                'Norrbotten 971.8 + Västerbotten 717.4 over 36 months Apr 2023 – Mar 2026. '
                'Norrland (5.0% pop) holds 29.7% of national Vyndaqel units. '
                'Was Modeled (Läkemedelsregistret patient counts) — now Observed (IQVIA actual).'
            )
            ws.cell(row=row[0].row, column=8).value = (
                'IQVIA RD/IM ATTR sheet → ATTR competitive landscape sheet (this workbook). '
                'Pop denominators from Region master.'
            )
            print(f'Updated CH-04 row {row[0].row} → Observed')
            break

    # Add new claim CH-14 (or next available CH-NN slot)
    # Find the last CH-XX row to know what number to use
    last_ch = 0
    last_row = None
    for row in ws.iter_rows(min_row=2, values_only=False):
        if row[0].value and isinstance(row[0].value, str) and row[0].value.startswith('CH-'):
            n = int(row[0].value.split('-')[1])
            if n > last_ch:
                last_ch = n
                last_row = row[0].row
    new_id = f'CH-{last_ch + 1:02d}'
    new_row_idx = ws.max_row + 1

    ws.append([
        new_id,
        'Rare disease — competitive',
        'IQVIA RD/IM extract 2026-04-27',
        'Chapter 11.1 (planned update)',
        'AMVUTTRA (Alnylam) and BEYONTTRA (Bridge Bio acoramidis) Swedish entry — direct mechanism competitors to Vyndaqel',
        'Observed',
        'IQVIA cumulative Apr 2023 – Mar 2026 shows AMVUTTRA at 95 units (~106M SEK) and BEYONTTRA at 40 units (~3.8M SEK). Pfizer national share ~94%. Örebro outlier: Pfizer share 20% (data quality vs active switching uncertain). New competitive entry materially affects P1 strategic stance from "anchor + extend" to "anchor + defend".',
        'IQVIA RD/IM extract; ATTR competitive landscape sheet (this workbook).',
        '',
    ])

    # Style the new row with light amber fill to mark it as new
    for cell in ws[new_row_idx]:
        cell.fill = NEW_FILL
        cell.alignment = DEFAULT_ALIGN
    print(f'Added new claim {new_id} at row {new_row_idx}')

    return new_id


def update_plays_detail(wb):
    """Annotate P1 Pfizer validation #2 (Hympavzi launch) with confirmed-not-launched note."""
    ws = wb['Plays detail']
    for row in ws.iter_rows(min_row=2, values_only=False):
        if (row[0].value == 'P1' and row[1].value == 'Pfizer validation'
                and str(row[2].value) == '2'):
            current = ws.cell(row=row[0].row, column=4).value or ''
            if 'IQVIA RD/IM 2026-04-27' not in current:
                new_text = current + (
                    ' [UPDATE 2026-04-27: IQVIA RD/IM extract confirms zero Hympavzi rows in Sweden through Mar 2026 — '
                    'product not yet launched. Outstanding ask narrows to "what is the planned launch date?"]'
                )
                ws.cell(row=row[0].row, column=4).value = new_text
                ws.cell(row=row[0].row, column=4).fill = NEW_FILL
                ws.cell(row=row[0].row, column=4).alignment = DEFAULT_ALIGN
                print(f'Updated Plays detail P1 #2 (Hympavzi launch) row {row[0].row}')
            break


def update_change_log(wb, new_claim_id):
    """If there's a Change log or README sheet, note the v23 → v24 update."""
    if 'Change log' in wb.sheetnames:
        ws = wb['Change log']
        ws.append([
            '2026-04-27',
            'v24',
            f'Integrated IQVIA RD/IM extract (ATTR + Migraine + Covid + Haemophilia, Apr 2023 – Mar 2026). '
            f'Three new sheets: RD-IM IQVIA detail (long-format), ATTR competitive landscape, Pfizer RD-IM footprint. '
            f'CH-04 Norrland Vyndaqel cluster confidence upgraded Modeled → Observed (Norrbotten 971.8 + Västerbotten 717.4 Vyndaqel units per 100k; '
            f'Norrland 5.0% population holds 29.7% of national Vyndaqel units). '
            f'New claim {new_claim_id}: AMVUTTRA + BEYONTTRA Swedish entry as direct mechanism competitors to Vyndaqel. '
            f'P1 Hympavzi-launch validation item annotated: confirmed not launched in Sweden as of Mar 2026.'
        ])
        print('Updated Change log sheet')


def main():
    print(f'Loading IQVIA RD/IM extract: {RDIM_RAW.name}')
    iqvia_agg = aggregate_iqvia(RDIM_RAW)
    print(f'Aggregated {len(iqvia_agg)} therapy areas')
    for ta, (agg, _) in iqvia_agg.items():
        print(f'  {ta}: {len(agg)} region × product cells')

    print(f'\nCopying v23 → v24')
    copyfile(V23, V24_WORKING)

    wb = openpyxl.load_workbook(V24_WORKING)

    print('\nAdding new sheets...')
    add_rdim_detail_sheet(wb, iqvia_agg)
    add_attr_competitive_sheet(wb, iqvia_agg)
    add_pfizer_rdim_footprint_sheet(wb, iqvia_agg)

    print('\nUpdating Evidence Ledger...')
    new_claim_id = update_evidence_ledger(wb)

    print('\nUpdating Plays detail...')
    update_plays_detail(wb)

    print('\nUpdating Change log (if present)...')
    update_change_log(wb, new_claim_id)

    wb.save(V24_WORKING)
    print(f'\nSaved {V24_WORKING}')

    copyfile(V24_WORKING, V24_DELIVERY)
    print(f'Copied to {V24_DELIVERY}')

    # Print sheet listing for verification
    wb_check = openpyxl.load_workbook(V24_WORKING, read_only=True)
    print(f'\nv24 has {len(wb_check.sheetnames)} sheets:')
    for s in wb_check.sheetnames:
        if 'IQVIA' in s or 'ATTR competitive' in s or 'RD-IM' in s:
            print(f'  ★ NEW: {s}')
        else:
            print(f'    {s}')


if __name__ == '__main__':
    main()
