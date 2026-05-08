# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v25.xlsx — integrates IQVIA Oncology extract (received 2026-04-27).

Four new sheets:
- Oncology IQVIA detail — long-format per region × product × monthly
- CDK4/6 competitive landscape — Ibrance vs Verzenios vs Kisqali per region (substitution analysis)
- Pfizer oncology footprint — Pfizer-only per-region summary (Ibrance, Tukysa, Talzenna, Lorviqua, Xalkori, Elrexfio, Xtandi)
- Oncology class summary — national Pfizer share by ATC class

Updates:
- Evidence Ledger ST-01 (Stockholm Kisqali substitution): Hypothesis + Needs Pfizer validation → Observed
- Evidence Ledger EX-06 (Ibrance decline): refresh with IQVIA-extended data, retain Observed
- Add new claim CH-15: Verzenios (Lilly abemaciclib) as primary CDK4/6 competitor — not previously in analysis
- Add new claim CH-16: XTANDI (Pfizer enzalutamide) as previously undocumented major Pfizer Sweden asset (1.42B SEK 3-yr)
- Pfizer validation gates G2 (IQVIA Kisqali volume): Open → Received + Integrated
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
V24 = ROOT / "delivery" / "06_master_workbook_v24.xlsx"
V25_WORKING = ROOT / "working" / "data" / "master" / "master_workbook_v25.xlsx"
V25_DELIVERY = ROOT / "delivery" / "06_master_workbook_v25.xlsx"
ONC_RAW = ROOT / "working" / "data" / "raw" / "VitiScience Oncology_Apr-27-2026.xlsx"

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

PFIZER_ONC_PRODUCTS = {
    'IBRANCE': 'L01EF01 Palbociclib (CDK4/6 inhibitor)',
    'TUKYSA': 'L01EH03 Tucatinib (HER2 small molecule)',
    'TALZENNA': 'L01XK04 Talazoparib (PARP inhibitor)',
    'LORVIQUA': 'L01ED05 Lorlatinib (ALK inhibitor)',
    'XALKORI': 'L01ED01 Crizotinib (ALK inhibitor — older Pfizer ALK)',
    'ELREXFIO': 'L01FX32 Elranatamab (BCMA bispecific T-cell engager)',
    'XTANDI': 'L02BB04 Enzalutamide (androgen receptor inhibitor)',
}

# Header style
HDR_FILL = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
NEW_FILL = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")
DEFAULT_ALIGN = Alignment(vertical="center", horizontal="left", wrap_text=True)


def style_header(ws, row=1):
    for cell in ws[row]:
        if cell.value is not None:
            cell.fill = HDR_FILL
            cell.font = HDR_FONT
            cell.alignment = DEFAULT_ALIGN
    ws.row_dimensions[row].height = 26


def aggregate_oncology(raw_path):
    """Returns dict: {sheet_name: (agg_dict, sell_month_labels)}.
    agg_dict keyed by (region, product) → {atc, sek_total, units_total, monthly_sek, monthly_units}.
    For Ibrance sheet, includes early-vs-late period for substitution analysis.
    """
    wb_raw = openpyxl.load_workbook(raw_path, read_only=True, data_only=True)
    out = {}
    for sheet_name in wb_raw.sheetnames:
        ws = wb_raw[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sell_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
        sell_month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip()
                             for i in sell_cols]
        agg = defaultdict(lambda: {
            'atc': '', 'sek_total': 0.0, 'units_total': 0.0,
            'monthly_sek': [0.0] * len(sell_cols),
            'monthly_units': [0.0] * len(units_cols),
            'early_units': 0.0, 'late_units': 0.0,  # for substitution analysis
            'early_sek': 0.0, 'late_sek': 0.0,
        })
        midpoint = len(sell_cols) // 2
        for row in ws.iter_rows(min_row=2, values_only=True):
            atc = row[0]
            product = row[1]
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2], 'Unknown')
            if not product or region == 'Unknown':
                continue
            key = (region, product)
            agg[key]['atc'] = atc
            for i, idx in enumerate(sell_cols):
                v = row[idx]
                if v is not None:
                    agg[key]['monthly_sek'][i] += v
                    agg[key]['sek_total'] += v
                    if i < midpoint:
                        agg[key]['early_sek'] += v
                    else:
                        agg[key]['late_sek'] += v
            for i, idx in enumerate(units_cols):
                v = row[idx]
                if v is not None:
                    agg[key]['monthly_units'][i] += v
                    agg[key]['units_total'] += v
                    if i < midpoint:
                        agg[key]['early_units'] += v
                    else:
                        agg[key]['late_units'] += v
        out[sheet_name] = (agg, sell_month_labels)
    return out


def add_oncology_detail_sheet(wb, onc_agg):
    """Long-format: one row per region × product × therapy area."""
    if 'Oncology IQVIA detail' in wb.sheetnames:
        del wb['Oncology IQVIA detail']
    ws = wb.create_sheet('Oncology IQVIA detail')

    # Use a representative month labels list
    sample_months = next(iter(onc_agg.values()))[1]
    headers = ['Sheet (therapy area)', 'Region', 'Product', 'ATC', 'Manufacturer position',
               'Total Sell-In SEK', 'Total Units']
    ws.append(headers)
    style_header(ws)

    for ta, (agg, _) in onc_agg.items():
        sorted_keys = sorted(agg.keys(), key=lambda k: -agg[k]['sek_total'])
        for (region, product) in sorted_keys:
            d = agg[(region, product)]
            position = 'Pfizer' if product in PFIZER_ONC_PRODUCTS else 'Competitor'
            ws.append([ta, region, product, d['atc'], position,
                       d['sek_total'], d['units_total']])

    widths = [22, 30, 26, 38, 18, 18, 14]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'


def add_cdk46_competitive_sheet(wb, onc_agg):
    """CDK4/6 three-way landscape per region with substitution analysis."""
    if 'CDK4-6 competitive landscape' in wb.sheetnames:
        del wb['CDK4-6 competitive landscape']
    ws = wb.create_sheet('CDK4-6 competitive landscape')

    headers = [
        'Region', 'Population',
        'IBRANCE units', 'IBRANCE SEK', 'Ibrance Δ% (1H vs 2H)',
        'VERZENIOS units', 'VERZENIOS SEK', 'Verzenios Δ%',
        'KISQALI units', 'KISQALI SEK', 'Kisqali Δ%',
        'Class total units', 'Pfizer share % (units)', 'Pfizer share % (SEK)',
        'Substitution direction', 'Notes',
    ]
    ws.append(headers)
    style_header(ws)

    ibrance_agg, _ = onc_agg['Ibrance']
    regions = sorted(POP.keys(),
                     key=lambda r: -(ibrance_agg.get((r, 'IBRANCE'), {'units_total': 0})['units_total'] +
                                     ibrance_agg.get((r, 'VERZENIOS'), {'units_total': 0})['units_total'] +
                                     ibrance_agg.get((r, 'KISQALI'), {'units_total': 0})['units_total']))

    for region in regions:
        ib = ibrance_agg.get((region, 'IBRANCE'), {})
        vz = ibrance_agg.get((region, 'VERZENIOS'), {})
        ks = ibrance_agg.get((region, 'KISQALI'), {})

        ib_u, ib_s = ib.get('units_total', 0), ib.get('sek_total', 0)
        vz_u, vz_s = vz.get('units_total', 0), vz.get('sek_total', 0)
        ks_u, ks_s = ks.get('units_total', 0), ks.get('sek_total', 0)

        def pct(early, late):
            return round(100 * (late - early) / early, 1) if early > 0 else None

        ib_delta = pct(ib.get('early_units', 0), ib.get('late_units', 0))
        vz_delta = pct(vz.get('early_units', 0), vz.get('late_units', 0))
        ks_delta = pct(ks.get('early_units', 0), ks.get('late_units', 0))

        total_u = ib_u + vz_u + ks_u
        total_s = ib_s + vz_s + ks_s
        pfizer_units_share = round(100 * ib_u / total_u, 1) if total_u else 0
        pfizer_sek_share = round(100 * ib_s / total_s, 1) if total_s else 0

        # Substitution direction (which competitor grew most where Ibrance fell)
        direction = ''
        if ib_delta is not None and ib_delta < 0:
            growth = []
            if vz_delta and vz_delta > 0:
                growth.append(('Verzenios', vz_delta))
            if ks_delta and ks_delta > 0:
                growth.append(('Kisqali', ks_delta))
            if growth:
                top = max(growth, key=lambda x: x[1])
                direction = f"Ibrance {ib_delta}% → primarily {top[0]} (+{top[1]}%)"

        notes = ''
        if pfizer_units_share < 15:
            notes = 'Pfizer share <15% — far below national mean (28%)'
        elif pfizer_units_share > 45:
            notes = 'Pfizer-leading region (above 45%)'

        ws.append([region, POP[region],
                   ib_u, ib_s, ib_delta,
                   vz_u, vz_s, vz_delta,
                   ks_u, ks_s, ks_delta,
                   total_u, pfizer_units_share, pfizer_sek_share,
                   direction, notes])

    # National totals
    ws.append([])
    nat_ib_u = sum(ibrance_agg.get((r, 'IBRANCE'), {'units_total': 0})['units_total'] for r in POP.keys())
    nat_vz_u = sum(ibrance_agg.get((r, 'VERZENIOS'), {'units_total': 0})['units_total'] for r in POP.keys())
    nat_ks_u = sum(ibrance_agg.get((r, 'KISQALI'), {'units_total': 0})['units_total'] for r in POP.keys())
    nat_ib_s = sum(ibrance_agg.get((r, 'IBRANCE'), {'sek_total': 0})['sek_total'] for r in POP.keys())
    nat_vz_s = sum(ibrance_agg.get((r, 'VERZENIOS'), {'sek_total': 0})['sek_total'] for r in POP.keys())
    nat_ks_s = sum(ibrance_agg.get((r, 'KISQALI'), {'sek_total': 0})['sek_total'] for r in POP.keys())
    nat_total_u = nat_ib_u + nat_vz_u + nat_ks_u
    nat_total_s = nat_ib_s + nat_vz_s + nat_ks_s
    ws.append(['NATIONAL TOTAL', sum(POP.values()),
               nat_ib_u, nat_ib_s, '',
               nat_vz_u, nat_vz_s, '',
               nat_ks_u, nat_ks_s, '',
               nat_total_u,
               round(100 * nat_ib_u / nat_total_u, 1),
               round(100 * nat_ib_s / nat_total_s, 1),
               'Verzenios leading nationally',
               'Pfizer Ibrance is THIRD in 3-way race — was framed in v1-v2 analysis as Ibrance-vs-Kisqali only'])

    widths = [30, 12, 12, 14, 14, 12, 14, 14, 12, 14, 14, 14, 18, 18, 32, 50]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'


def add_pfizer_oncology_footprint_sheet(wb, onc_agg):
    """Pfizer oncology per-region summary (Ibrance, Tukysa, Talzenna, Lorviqua, Xalkori, Elrexfio, Xtandi)."""
    if 'Pfizer oncology footprint' in wb.sheetnames:
        del wb['Pfizer oncology footprint']
    ws = wb.create_sheet('Pfizer oncology footprint')

    products = ['IBRANCE', 'TUKYSA', 'TALZENNA', 'LORVIQUA', 'XALKORI', 'ELREXFIO', 'XTANDI']
    headers = ['Region', 'Population']
    for p in products:
        headers.extend([f'{p} SEK', f'{p} units'])
    headers.extend(['Total Pfizer onc SEK', 'Total Pfizer onc units'])
    ws.append(headers)
    style_header(ws)

    # Map: which sheet each Pfizer product appears in
    PRODUCT_SHEET = {
        'IBRANCE': 'Ibrance', 'TUKYSA': 'Tukysa L01EH', 'TALZENNA': 'Talzenna',
        'LORVIQUA': 'Lorviqua L01ED', 'XALKORI': 'Lorviqua L01ED',
        'ELREXFIO': 'Elrexfio', 'XTANDI': 'Talzenna',  # XTANDI lives in Talzenna sheet
    }

    rows_data = []
    for region in POP.keys():
        row = [region, POP[region]]
        total_sek, total_u = 0.0, 0.0
        for p in products:
            sheet = PRODUCT_SHEET[p]
            d = onc_agg[sheet][0].get((region, p), {'sek_total': 0, 'units_total': 0})
            row.extend([d['sek_total'], d['units_total']])
            total_sek += d['sek_total']
            total_u += d['units_total']
        row.extend([total_sek, total_u])
        rows_data.append(row)

    rows_data.sort(key=lambda r: -r[-2])  # by total SEK desc
    for row in rows_data:
        ws.append(row)

    # National total
    ws.append([])
    nat_row = ['NATIONAL TOTAL', sum(POP.values())]
    for col in range(2, len(headers)):
        nat_row.append(sum(r[col] for r in rows_data))
    ws.append(nat_row)

    widths = [30, 12] + [14] * (len(products) * 2) + [18, 18]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w
    ws.freeze_panes = 'B2'


def add_oncology_class_summary(wb, onc_agg):
    """National Pfizer share by ATC class."""
    if 'Oncology class summary' in wb.sheetnames:
        del wb['Oncology class summary']
    ws = wb.create_sheet('Oncology class summary')

    headers = ['Class', 'Pfizer product', 'Pfizer SEK (3yr)', 'Pfizer units (3yr)',
               'Class total SEK', 'Class total units',
               'Pfizer share % SEK', 'Pfizer share % units',
               'Top competitor', 'Top competitor SEK',
               'Strategic context']
    ws.append(headers)
    style_header(ws)

    # Aggregate per class manually
    classes = [
        ('CDK4/6 inhibitor (BC HR+/HER2-)', 'Ibrance', 'IBRANCE',
         'CDK4/6 — three-way race. Verzenios (Lilly) leads nationally; Ibrance third. Was framed in v1-v2 as Ibrance-vs-Kisqali only.'),
        ('HER2 small molecule (BC brain mets)', 'Tukysa L01EH', 'TUKYSA',
         'Pfizer dominant (~85%). Niche class, eligible-patient identification is the bottleneck not competition.'),
        ('PARP inhibitor (BC, prostate)', 'Talzenna', 'TALZENNA',
         'Lynparza (AstraZeneca) dominates (~95%). Talzenna structural ceiling — Pfizer effort cannot easily reshape this.'),
        ('ALK inhibitor (NSCLC)', 'Lorviqua L01ED', 'LORVIQUA',
         'Alecensa (Roche) leads first-line. Lorviqua positions 2L+ post-Alecensa. Pfizer also has older Xalkori (now declining).'),
        ('BCMA bispecific (multiple myeloma)', 'Elrexfio', 'ELREXFIO',
         'Two-horse race vs Tecvayli (Janssen). Near-parity by SEK; Tecvayli launched first.'),
        ('Androgen receptor inhibitor (prostate)', 'Talzenna', 'XTANDI',
         'XTANDI 1.42B SEK over 3 yr — major Pfizer asset previously not in our analysis. Co-administered with Talzenna for HRR-mutated mCRPC.'),
    ]

    for class_name, sheet, pfizer_product, context in classes:
        agg, _ = onc_agg[sheet]
        # Aggregate Pfizer
        pfizer_sek = sum(d['sek_total'] for (r, p), d in agg.items() if p == pfizer_product)
        pfizer_units = sum(d['units_total'] for (r, p), d in agg.items() if p == pfizer_product)

        # All products in this sheet
        per_product = defaultdict(lambda: {'sek': 0.0, 'units': 0.0})
        for (r, p), d in agg.items():
            per_product[p]['sek'] += d['sek_total']
            per_product[p]['units'] += d['units_total']

        # Class total — for special cases (Talzenna sheet has multiple classes), filter by ATC class
        if pfizer_product == 'XTANDI':
            # XTANDI's class L02BB04 — only enzalutamide
            class_total_sek = per_product['XTANDI']['sek']
            class_total_units = per_product['XTANDI']['units']
            top_comp = ''
            top_comp_sek = 0
        elif pfizer_product == 'TALZENNA':
            # PARP class only — exclude prednisolone (H02AB06) and abiraterone (L02BX03)
            class_total_sek = sum(d['sek'] for p, d in per_product.items() if p in {'TALZENNA', 'LYNPARZA'})
            class_total_units = sum(d['units'] for p, d in per_product.items() if p in {'TALZENNA', 'LYNPARZA'})
            top_comp = 'LYNPARZA'
            top_comp_sek = per_product['LYNPARZA']['sek']
        else:
            # All products in the sheet
            class_total_sek = sum(d['sek'] for d in per_product.values())
            class_total_units = sum(d['units'] for d in per_product.values())
            # Top competitor = largest non-Pfizer
            comp = sorted([(p, d['sek']) for p, d in per_product.items() if p not in PFIZER_ONC_PRODUCTS],
                          key=lambda x: -x[1])
            top_comp = comp[0][0] if comp else ''
            top_comp_sek = comp[0][1] if comp else 0

        share_sek = round(100 * pfizer_sek / class_total_sek, 1) if class_total_sek else 0
        share_units = round(100 * pfizer_units / class_total_units, 1) if class_total_units else 0

        ws.append([class_name, pfizer_product, pfizer_sek, pfizer_units,
                   class_total_sek, class_total_units,
                   share_sek, share_units,
                   top_comp, top_comp_sek, context])

    widths = [40, 14, 16, 14, 16, 16, 16, 16, 16, 16, 70]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i+1)].width = w


def update_evidence_ledger(wb):
    """Update ST-01 to Observed; add CH-15 and CH-16."""
    ws = wb['Evidence ledger']

    # ST-01 — Stockholm Kisqali substitution
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'ST-01':
            ws.cell(row=row[0].row, column=6).value = 'Observed'
            ws.cell(row=row[0].row, column=7).value = (
                'IQVIA Oncology extract 2026-04-27 confirms Kisqali presence in Stockholm (5,930 units cumulative) and '
                'VGR (2,738 units). Comparing first 18 months (Apr 2023 – Sep 2024) vs last 18 months (Oct 2024 – Mar 2026): '
                'Stockholm Ibrance -18.5%, Kisqali +24.9%; VGR Ibrance -22.7%, Kisqali +51.0%. The substitution channel '
                'is observed but not exclusive — Verzenios (Lilly abemaciclib) growth is larger than Kisqali in Stockholm '
                '(+114%) and VGR (+128%). The fuller story is a three-way race led by Verzenios. Was Hypothesis + '
                'Needs Pfizer validation; now Observed.'
            )
            ws.cell(row=row[0].row, column=8).value = (
                'IQVIA Oncology Apr 2023 – Mar 2026, Ibrance sheet (which includes Verzenios L01EF03 and Kisqali L01EF02). '
                'See "CDK4-6 competitive landscape" sheet (this workbook).'
            )
            print(f'Updated ST-01 row {row[0].row} → Observed (with Verzenios qualifier)')
            break

    # Refresh EX-06 trail with extended IQVIA data
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'EX-06':
            current_trail = ws.cell(row=row[0].row, column=8).value or ''
            if 'IQVIA Oncology 2026-04-27' not in current_trail:
                ws.cell(row=row[0].row, column=8).value = (
                    current_trail + ' [Updated 2026-04-27: IQVIA Oncology extract extends the trajectory to Mar 2026 and '
                    'confirms Stockholm -18.5% / VGR -22.7% on early-vs-late 18-month comparison. Verzenios +114% Stockholm, '
                    '+128% VGR; Kisqali +25% Stockholm, +51% VGR.]'
                )
                print(f'Refreshed EX-06 evidence trail row {row[0].row}')
            break

    # Find next available CH-NN
    last_ch = 0
    for row in ws.iter_rows(min_row=2, values_only=False):
        if row[0].value and isinstance(row[0].value, str) and row[0].value.startswith('CH-'):
            n = int(row[0].value.split('-')[1])
            if n > last_ch:
                last_ch = n

    new_id_15 = f'CH-{last_ch + 1:02d}'
    new_id_16 = f'CH-{last_ch + 2:02d}'

    # CH-15: Verzenios primary CDK4/6 competitor
    ws.append([
        new_id_15, 'Oncology — competitive', 'IQVIA Oncology 2026-04-27',
        'Chapter 11.2 (planned update); Plays brief P2',
        'Verzenios (Lilly abemaciclib) is the primary CDK4/6 competitor — not Kisqali. Verzenios national 39% units share; Ibrance 28%; Kisqali 33%.',
        'Observed',
        'IQVIA Oncology Apr 2023 – Mar 2026: Verzenios 26,223 units (39%), Kisqali 22,237 (33%), Ibrance 19,064 (28%). '
        'Across all six P2 target regions, Verzenios growth (1H vs 2H) ranges +50% to +196%, generally larger than Kisqali growth. '
        'P2 strategic stance ("anchor + defend Ibrance against Kisqali") was framed on incomplete competitive picture. '
        'Verzenios was not in v1-v2 analysis at all.',
        'IQVIA Oncology 2026-04-27, Ibrance sheet; CDK4-6 competitive landscape sheet (this workbook).',
        '',
    ])
    new_15_row = ws.max_row
    for cell in ws[new_15_row]:
        cell.fill = NEW_FILL
        cell.alignment = DEFAULT_ALIGN
    print(f'Added new claim {new_id_15} (Verzenios primary CDK4/6 competitor) at row {new_15_row}')

    # CH-16: XTANDI as undocumented Pfizer asset
    ws.append([
        new_id_16, 'Oncology — Pfizer footprint', 'IQVIA Oncology 2026-04-27',
        'Chapter 13/14 (planned update); workbook Pfizer oncology footprint',
        'XTANDI (Pfizer enzalutamide, ATC L02BB04) is a 1.42B SEK Swedish asset over 36 months that was not previously in our analysis.',
        'Observed',
        'IQVIA Oncology cumulative Apr 2023 – Mar 2026: XTANDI 1,420 MSEK / 56,919 units. Top regions: Stockholm 251M, '
        'Skåne 195M, VGR 181M, Östergötland 76M, Sörmland 76M. Co-administered with Talzenna for HRR-mutated mCRPC '
        '(via the Talzenna+Xtandi label). The original op-guide listed only 7 oral Rx Pfizer products excluding Xtandi; '
        'the IQVIA pull surfaced it because it sits in the Talzenna paradigm.',
        'IQVIA Oncology 2026-04-27, Talzenna sheet (which includes L02BB04); Pfizer oncology footprint sheet.',
        '',
    ])
    new_16_row = ws.max_row
    for cell in ws[new_16_row]:
        cell.fill = NEW_FILL
        cell.alignment = DEFAULT_ALIGN
    print(f'Added new claim {new_id_16} (XTANDI undocumented Pfizer asset) at row {new_16_row}')

    return new_id_15, new_id_16


def update_validation_gates(wb):
    """G2 status: Open → Received + Integrated."""
    ws = wb['Pfizer validation gates']
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'G2':
            ws.cell(row=row[0].row, column=4).value = 'Received'
            ws.cell(row=row[0].row, column=6).value = '2026-04-27'
            ws.cell(row=row[0].row, column=7).value = (
                'IQVIA Oncology extract 2026-04-27 covers Ibrance L01EF01, Kisqali L01EF02, Verzenios L01EF03 with '
                'monthly data Apr 2023 – Mar 2026 at brick level. National Kisqali 22,237 units / 372 MSEK over 36 months. '
                'Stockholm Kisqali 5,930 units; VGR 2,738. Substitution direction confirmed but not exclusive — '
                'Verzenios (not in original ask) is the larger competitor by units across most regions. '
                'See claims ST-01 (now Observed), CH-15 (new — Verzenios primary competitor).'
            )
            ws.cell(row=row[0].row, column=8).value = 'Yes (v25)'
            # Highlight
            for cell in ws[row[0].row]:
                cell.fill = NEW_FILL
                cell.alignment = DEFAULT_ALIGN
            print(f'Updated G2 row {row[0].row}: Open → Received + Integrated')
            break


def main():
    print(f'Loading IQVIA Oncology: {ONC_RAW.name}')
    onc_agg = aggregate_oncology(ONC_RAW)
    print(f'Aggregated {len(onc_agg)} therapy area sheets:')
    for ta, (agg, _) in onc_agg.items():
        print(f'  {ta}: {len(agg)} region × product cells')

    print(f'\nCopying v24 → v25')
    copyfile(V24, V25_WORKING)

    wb = openpyxl.load_workbook(V25_WORKING)

    print('\nAdding new sheets...')
    add_oncology_detail_sheet(wb, onc_agg)
    add_cdk46_competitive_sheet(wb, onc_agg)
    add_pfizer_oncology_footprint_sheet(wb, onc_agg)
    add_oncology_class_summary(wb, onc_agg)

    print('\nUpdating Evidence Ledger...')
    new_15, new_16 = update_evidence_ledger(wb)

    print('\nUpdating Pfizer validation gates...')
    update_validation_gates(wb)

    wb.save(V25_WORKING)
    print(f'\nSaved {V25_WORKING}')

    copyfile(V25_WORKING, V25_DELIVERY)
    print(f'Copied to {V25_DELIVERY}')

    # Verify
    wb_check = openpyxl.load_workbook(V25_WORKING, read_only=True)
    print(f'\nv25 has {len(wb_check.sheetnames)} sheets')
    new_sheets = ['Oncology IQVIA detail', 'CDK4-6 competitive landscape',
                  'Pfizer oncology footprint', 'Oncology class summary']
    for s in new_sheets:
        marker = '★ NEW' if s in wb_check.sheetnames else '⚠ MISSING'
        print(f'  {marker}: {s}')


if __name__ == '__main__':
    main()
