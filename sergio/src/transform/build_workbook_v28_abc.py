# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v28.xlsx — A + B + C deferred analyses.

A — Competitive class trajectories (last-6 vs prev-6 mo slope, 6 competitors):
    Verzenios (CDK4/6), Tecvayli (BCMA), Alecensa (ALK), Lynparza (PARP),
    AMVUTTRA (ATTR), BEYONTTRA (ATTR). Same methodology as v27 Verzenios trajectory sheet.

B — Stockholm strategic profile (synthesis across CDK4/6, ATTR, Vaccines, Oncology, Stakeholders).

C — Pfizer product trajectories (last-6 vs prev-6 mo slope, 5 Pfizer products):
    Ibrance, Vyndaqel, Tukysa, Talzenna, Elrexfio.
"""

from collections import defaultdict
from pathlib import Path
from shutil import copyfile

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V27 = ROOT / "delivery" / "06_master_workbook_v27.xlsx"
V28_WORKING = ROOT / "working" / "data" / "master" / "master_workbook_v28.xlsx"
V28_DELIVERY = ROOT / "delivery" / "06_master_workbook_v28.xlsx"
RAW_DIR = ROOT / "working" / "data" / "raw"
RDIM_RAW = RAW_DIR / "VitiScience RD_IM_Apr-27-2026.xlsx"
ONC_RAW = RAW_DIR / "VitiScience Oncology_Apr-27-2026.xlsx"
VAC_RAW = RAW_DIR / "VitiScience_Vaccines_Apr-02-2026.xlsx"

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

# (display_label, file, sheet_name, product_name_in_data, atc_or_class_note)
COMPETITORS = [
    ('Verzenios',  ONC_RAW,  'Ibrance',         'VERZENIOS',  'CDK4/6 — Lilly (abemaciclib)'),
    ('Tecvayli',   ONC_RAW,  'Elrexfio',        'TECVAYLI',   'BCMA bispecific — Janssen (teclistamab)'),
    ('Alecensa',   ONC_RAW,  'Lorviqua L01ED',  'ALECENSA',   'ALK NSCLC — Roche (alectinib)'),
    ('Lynparza',   ONC_RAW,  'Talzenna',        'LYNPARZA',   'PARP — AstraZeneca (olaparib)'),
    ('AMVUTTRA',   RDIM_RAW, 'ATTR',            'AMVUTTRA',   'ATTR siRNA — Alnylam (vutrisiran)'),
    ('BEYONTTRA',  RDIM_RAW, 'ATTR',            'BEYONTTRA',  'ATTR stabiliser — BridgeBio (acoramidis)'),
]

PFIZER_TARGETS = [
    ('Ibrance',  ONC_RAW,  'Ibrance',         'IBRANCE',  'CDK4/6 — Pfizer (palbociclib) — P2 anchor'),
    ('Vyndaqel', RDIM_RAW, 'ATTR',            'VYNDAQEL', 'ATTR-CM — Pfizer (tafamidis) — P1 anchor'),
    ('Tukysa',   ONC_RAW,  'Tukysa L01EH',    'TUKYSA',   'HER2-SM (BC brain mets) — Pfizer (tucatinib) — P4'),
    ('Talzenna', ONC_RAW,  'Talzenna',        'TALZENNA', 'PARP — Pfizer (talazoparib) — P4'),
    ('Elrexfio', ONC_RAW,  'Elrexfio',        'ELREXFIO', 'BCMA bispecific — Pfizer (elranatamab) — P1 carry'),
]

HDR_FILL = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
NEW_FILL = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")
SECTION_FILL = PatternFill(start_color="E8F0FF", end_color="E8F0FF", fill_type="solid")
SECTION_FONT = Font(bold=True, size=11, color="1F3A5F")
NATIONAL_FILL = PatternFill(start_color="F0E8D0", end_color="F0E8D0", fill_type="solid")
DEFAULT_ALIGN = Alignment(vertical="center", horizontal="left", wrap_text=True)


def style_header(ws, row=1):
    for cell in ws[row]:
        if cell.value is not None:
            cell.fill = HDR_FILL
            cell.font = HDR_FONT
            cell.alignment = DEFAULT_ALIGN
    ws.row_dimensions[row].height = 26


def aggregate_product_monthly(file_path, sheet_name, product_name):
    """Returns ({region: [monthly_units]}, {region: [monthly_sek]}, [month_labels]) for a single product."""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip() for i in sek_cols]

    units_out = defaultdict(lambda: [0.0] * len(units_cols))
    sek_out = defaultdict(lambda: [0.0] * len(sek_cols))
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        if product != product_name:
            continue
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if not region:
            continue
        for i, idx in enumerate(units_cols):
            v = row[idx]
            if v is not None:
                units_out[region][i] += v
        for i, idx in enumerate(sek_cols):
            v = row[idx]
            if v is not None:
                sek_out[region][i] += v
    return units_out, sek_out, month_labels


def verdict_for_pct(pct):
    if pct is None:
        return 'No prior-6mo baseline'
    if pct > 30:
        return 'COMPOUNDING (>+30%)'
    if pct > 5:
        return 'GROWING (+5 to +30%)'
    if pct >= -5:
        return 'PLATEAUING (±5%)'
    if pct >= -20:
        return 'DECLINING (−5 to −20%)'
    return 'CONTRACTING (<−20%)'


def compute_slope_row(monthly):
    """Given a 36-month list, return (first_6, mid_6, last_6, prev_6, pct, verdict)."""
    n = len(monthly)
    last_6_start = n - 6
    prev_6_start = n - 12
    first_6 = sum(monthly[:6])
    mid_6 = sum(monthly[(n // 2 - 3):(n // 2 + 3)])
    last_6 = sum(monthly[last_6_start:])
    prev_6 = sum(monthly[prev_6_start:last_6_start])
    pct = round(100 * (last_6 - prev_6) / prev_6, 1) if prev_6 > 0 else None
    return first_6, mid_6, last_6, prev_6, pct, verdict_for_pct(pct)


# ============================================================================
# A — Competitive class trajectories
# ============================================================================

def add_competitive_class_trajectories_sheet(wb):
    """A — last-6-month slope analysis for 6 competitors (Verzenios + 5 new)."""
    name = 'Competitive class trajectories'
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)

    headers = ['Competitor', 'Class / company', 'Region',
               'First-6mo units', 'Mid-window-6mo units',
               'Prev-6mo units (Apr–Sep 2025)', 'Last-6mo units (Oct 2025–Mar 2026)',
               'Last-6 vs Prev-6 (%)', 'Trajectory verdict']
    ws.append(headers)
    style_header(ws)

    summary_rows = []  # for the national summary section
    last_window_label, prev_window_label = None, None

    for label, fpath, sheet, prod, class_note in COMPETITORS:
        units_agg, _, month_labels = aggregate_product_monthly(fpath, sheet, prod)
        n_months = len(month_labels)
        last_window_label = f'{month_labels[n_months - 6]} – {month_labels[-1]}'
        prev_window_label = f'{month_labels[n_months - 12]} – {month_labels[n_months - 7]}'

        if not units_agg:
            ws.append([label, class_note, '(no IQVIA rows found)', None, None, None, None, None, None])
            continue

        # National total
        nat_monthly = [sum(units_agg[r][i] for r in units_agg.keys()) for i in range(n_months)]
        f6, m6, l6, p6, pct, verdict = compute_slope_row(nat_monthly)
        ws.append([label, class_note, 'NATIONAL TOTAL', f6, m6, p6, l6, pct, f'NATIONAL: {verdict}'])
        for cell in ws[ws.max_row]:
            cell.fill = NATIONAL_FILL
            cell.font = Font(bold=True)
        summary_rows.append((label, class_note, l6, p6, pct, verdict))

        # Per-region rows (only regions with non-zero last-12mo activity, sorted by last-6 desc)
        region_rows = []
        for region, monthly in units_agg.items():
            if sum(monthly[-12:]) == 0:
                continue
            f6, m6, l6, p6, pct, vrd = compute_slope_row(monthly)
            region_rows.append([label, class_note, region, f6, m6, p6, l6, pct, vrd])
        region_rows.sort(key=lambda r: -(r[6] or 0))
        for row in region_rows:
            ws.append(row)
        ws.append([])  # spacer between competitors

    # National summary block
    ws.append([])
    ws.append(['===== NATIONAL SUMMARY: all six competitors, last-6 vs prev-6 =====', None, None, None, None, None, None, None, None])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT
    ws.append(['Competitor', 'Class / company', '', '', '', 'Prev-6 units', 'Last-6 units', 'Δ %', 'Verdict'])
    style_header(ws, ws.max_row)
    for label, class_note, l6, p6, pct, verdict in summary_rows:
        ws.append([label, class_note, '', '', '', p6, l6, pct, verdict])

    # Methods notes
    ws.append([])
    ws.append(['Methods note', f'Last-6mo window: {last_window_label}.'])
    ws.append(['', f'Prev-6mo window: {prev_window_label}.'])
    ws.append(['', 'Verdict thresholds: COMPOUNDING >+30% / GROWING +5 to +30% / PLATEAUING ±5% / DECLINING −5 to −20% / CONTRACTING <−20%.'])
    ws.append(['', 'Units = IQVIA pack count (not patient days/courses); cross-product unit comparisons NOT valid. Within-product trajectory IS valid.'])
    ws.append(['Why this matters', 'Tests whether the Verzenios plateau finding (v27) generalises. If multiple competitors are PLATEAUING/DECLINING in the most recent window, the conservative defense scenarios for P1/P2/P4 tighten — competitor compounding cannot be assumed for FY26 planning. AMVUTTRA + BEYONTTRA are the inverse case (newer launches, expected ramping); their trajectories tell us launch tempo, not plateau.'])
    ws.append(['Caveat', 'AMVUTTRA + BEYONTTRA may have <12 months of post-launch data and/or 0 prior-6 baseline; verdict cells may show "No prior-6mo baseline" — that is the correct empirical answer, not an error.'])

    widths = [14, 38, 28, 16, 18, 22, 26, 14, 38]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w
    ws.freeze_panes = 'D2'
    print(f'  Created {name} sheet (6 competitors, per-region + national + summary)')


# ============================================================================
# C — Pfizer product trajectories
# ============================================================================

def add_pfizer_trajectories_sheet(wb):
    """C — last-6-month slope for 5 Pfizer products."""
    name = 'Pfizer product trajectories'
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)

    headers = ['Pfizer product', 'Class / role', 'Region',
               'First-6mo units', 'Mid-window-6mo units',
               'Prev-6mo units (Apr–Sep 2025)', 'Last-6mo units (Oct 2025–Mar 2026)',
               'Last-6 vs Prev-6 (%)', 'Trajectory verdict']
    ws.append(headers)
    style_header(ws)

    summary_rows = []
    last_window_label, prev_window_label = None, None

    for label, fpath, sheet, prod, class_note in PFIZER_TARGETS:
        units_agg, _, month_labels = aggregate_product_monthly(fpath, sheet, prod)
        n_months = len(month_labels)
        last_window_label = f'{month_labels[n_months - 6]} – {month_labels[-1]}'
        prev_window_label = f'{month_labels[n_months - 12]} – {month_labels[n_months - 7]}'

        if not units_agg:
            ws.append([label, class_note, '(no IQVIA rows found)', None, None, None, None, None, None])
            continue

        nat_monthly = [sum(units_agg[r][i] for r in units_agg.keys()) for i in range(n_months)]
        f6, m6, l6, p6, pct, verdict = compute_slope_row(nat_monthly)
        ws.append([label, class_note, 'NATIONAL TOTAL', f6, m6, p6, l6, pct, f'NATIONAL: {verdict}'])
        for cell in ws[ws.max_row]:
            cell.fill = NATIONAL_FILL
            cell.font = Font(bold=True)
        summary_rows.append((label, class_note, l6, p6, pct, verdict))

        region_rows = []
        for region, monthly in units_agg.items():
            if sum(monthly[-12:]) == 0:
                continue
            f6, m6, l6, p6, pct, vrd = compute_slope_row(monthly)
            region_rows.append([label, class_note, region, f6, m6, p6, l6, pct, vrd])
        region_rows.sort(key=lambda r: -(r[6] or 0))
        for row in region_rows:
            ws.append(row)
        ws.append([])

    ws.append([])
    ws.append(['===== NATIONAL SUMMARY: 5 Pfizer products, last-6 vs prev-6 =====', None, None, None, None, None, None, None, None])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT
    ws.append(['Product', 'Class / role', '', '', '', 'Prev-6 units', 'Last-6 units', 'Δ %', 'Verdict'])
    style_header(ws, ws.max_row)
    for label, class_note, l6, p6, pct, verdict in summary_rows:
        ws.append([label, class_note, '', '', '', p6, l6, pct, verdict])

    ws.append([])
    ws.append(['Methods note', f'Last-6mo window: {last_window_label}.'])
    ws.append(['', f'Prev-6mo window: {prev_window_label}.'])
    ws.append(['', 'Verdict thresholds same as Competitive class trajectories sheet (±5% = PLATEAUING etc.).'])
    ws.append(['Why this matters', 'Pfizer-internal trajectory is the missing complement to the competitor analysis. If Ibrance is DECLINING and Verzenios is PLATEAUING, the CDK4/6 class is in mutual stall — different defense story than "Verzenios still gaining; Ibrance bleeding." If Vyndaqel is GROWING despite AMVUTTRA/BEYONTTRA pressure, the ATTR P1 anchor is more durable than feared. Elrexfio trajectory = ramp curve (post-launch).'])
    ws.append(['Caveat', 'Elrexfio is post-launch and may show "No prior-6mo baseline" if Sweden launch < 12 months old at end-of-window.'])

    widths = [14, 42, 28, 16, 18, 22, 26, 14, 38]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w
    ws.freeze_panes = 'D2'
    print(f'  Created {name} sheet (5 Pfizer products, per-region + national + summary)')


# ============================================================================
# B — Stockholm strategic profile
# ============================================================================

def aggregate_all_for_stockholm(file_path, sheet_name):
    """Returns {product: {'units_3yr': float, 'sek_3yr': float, 'monthly_units': [..]}} for Region Stockholm only."""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    out = defaultdict(lambda: {'units_3yr': 0.0, 'sek_3yr': 0.0, 'monthly_units': [0.0] * len(units_cols)})
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        if not product:
            continue
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if region != 'Region Stockholm':
            continue
        for i, idx in enumerate(units_cols):
            v = row[idx]
            if v is not None:
                out[product]['units_3yr'] += v
                out[product]['monthly_units'][i] += v
        for idx in sek_cols:
            v = row[idx]
            if v is not None:
                out[product]['sek_3yr'] += v
    return dict(out)


def aggregate_national(file_path, sheet_name):
    """Returns {product: {region: units_3yr}} for cross-region context."""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
    out = defaultdict(lambda: defaultdict(lambda: {'units': 0.0, 'sek': 0.0}))
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        if not product:
            continue
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if not region:
            continue
        for idx in units_cols:
            v = row[idx]
            if v is not None:
                out[product][region]['units'] += v
        for idx in sek_cols:
            v = row[idx]
            if v is not None:
                out[product][region]['sek'] += v
    return out


def add_stockholm_strategic_profile_sheet(wb):
    """B — single unified Stockholm view across CDK4/6, ATTR, Vaccines, Oncology, Stakeholders."""
    name = 'Stockholm strategic profile'
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)

    pops = {}
    rm = wb['Region master']
    rm_headers = [c.value for c in next(rm.iter_rows(min_row=1, max_row=1))]
    region_col = rm_headers.index('Region')
    pop_col = rm_headers.index('Population')
    for row in rm.iter_rows(min_row=2, values_only=True):
        if row[region_col]:
            pops[row[region_col]] = row[pop_col]
    sthlm_pop = pops['Region Stockholm']

    # Pull data
    cdk46_nat = aggregate_national(ONC_RAW, 'Ibrance')   # IBRANCE / VERZENIOS / KISQALI
    attr_nat = aggregate_national(RDIM_RAW, 'ATTR')      # VYNDAQEL / AMVUTTRA / BEYONTTRA
    wb_v = openpyxl.load_workbook(VAC_RAW, read_only=True)
    vac_sn = wb_v.sheetnames[0]  # 'Sweden Sell-In'
    vac_nat = aggregate_national(VAC_RAW, vac_sn)
    onc_tukysa = aggregate_national(ONC_RAW, 'Tukysa L01EH')
    onc_lorviqua = aggregate_national(ONC_RAW, 'Lorviqua L01ED')
    onc_talzenna = aggregate_national(ONC_RAW, 'Talzenna')
    onc_elrexfio = aggregate_national(ONC_RAW, 'Elrexfio')

    def stockholm_units(agg, product):
        return agg.get(product, {}).get('Region Stockholm', {}).get('units', 0.0)

    def stockholm_sek(agg, product):
        return agg.get(product, {}).get('Region Stockholm', {}).get('sek', 0.0)

    def total_class_units_stockholm(agg, products):
        return sum(stockholm_units(agg, p) for p in products)

    def total_class_sek_stockholm(agg, products):
        return sum(stockholm_sek(agg, p) for p in products)

    # ---------- Title block ----------
    ws.append(['Stockholm strategic profile — multi-dimensional anomaly view'])
    ws['A1'].font = Font(bold=True, size=14, color="1F3A5F")
    ws.row_dimensions[1].height = 30
    ws.append(['Population', sthlm_pop, '', '23.5% of national population (largest region by far)'])
    ws.append(['Why this sheet exists',
               'Stockholm is anomalous across at least five dimensions (CDK4/6 share, ATTR per-capita, vaccine adoption, oncology absolute footprint, stakeholder cornerstone density). No prior workbook sheet pulled them into one view. This sheet is the answer to "what is the Stockholm story?" for the Pfizer Thursday meeting.'])
    ws.append([])

    # ---------- Section 1: CDK4/6 ----------
    ws.append(['1) CDK4/6 — Stockholm has the LOWEST Pfizer share of any major region'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT

    cdk_products = ['IBRANCE', 'VERZENIOS', 'KISQALI']
    sthlm_cdk_units = total_class_units_stockholm(cdk46_nat, cdk_products)
    sthlm_cdk_sek = total_class_sek_stockholm(cdk46_nat, cdk_products)
    ws.append(['Product', 'Stockholm units (3yr)', 'Stockholm SEK (3yr)', '% of Stockholm class (units)', '% of Stockholm class (SEK)'])
    style_header(ws, ws.max_row)
    for p in cdk_products:
        u = stockholm_units(cdk46_nat, p)
        s = stockholm_sek(cdk46_nat, p)
        ws.append([p, u, s,
                   round(100 * u / sthlm_cdk_units, 1) if sthlm_cdk_units else None,
                   round(100 * s / sthlm_cdk_sek, 1) if sthlm_cdk_sek else None])
    ws.append(['CDK4/6 TOTAL', sthlm_cdk_units, sthlm_cdk_sek, 100, 100])

    # Cross-region Pfizer share comparison
    ws.append([])
    ws.append(['Cross-region context: Pfizer (Ibrance) share of CDK4/6 by units, by region (sorted ascending = Stockholm anomaly)'])
    ws[ws.max_row][0].font = Font(italic=True)
    ws.append(['Region', 'Ibrance units', 'Class total units', 'Pfizer share (units, %)'])
    style_header(ws, ws.max_row)
    region_share_rows = []
    for region in pops:
        ibr = cdk46_nat.get('IBRANCE', {}).get(region, {}).get('units', 0.0)
        ver = cdk46_nat.get('VERZENIOS', {}).get(region, {}).get('units', 0.0)
        kis = cdk46_nat.get('KISQALI', {}).get(region, {}).get('units', 0.0)
        total = ibr + ver + kis
        share = 100 * ibr / total if total else None
        region_share_rows.append([region, ibr, total, round(share, 1) if share is not None else None])
    region_share_rows.sort(key=lambda r: r[3] if r[3] is not None else 999)
    for row in region_share_rows:
        if row[0] == 'Region Stockholm':
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.fill = NEW_FILL
                cell.font = Font(bold=True)
        else:
            ws.append(row)
    ws.append(['Note', 'Stockholm is at the LOW end of Pfizer CDK4/6 share — physician preference (likely Karolinska oncology) skews toward Verzenios + Kisqali. P2 defense play is more about HOLDING Stockholm than recovering it; the upside lives in Halland (51%), VGR (35%), Skåne (36%) where the share is closer to the national mean and the slope question matters more.'])
    ws[ws.max_row][1].alignment = DEFAULT_ALIGN
    ws.append([])

    # ---------- Section 2: ATTR ----------
    ws.append(['2) ATTR — Stockholm has large absolute Vyndaqel volume but low per-capita vs Norrland'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT

    attr_products = ['VYNDAQEL', 'AMVUTTRA', 'BEYONTTRA']
    ws.append(['Product', 'Stockholm units (3yr)', 'Stockholm SEK (3yr)', 'Stockholm units per 100k pop'])
    style_header(ws, ws.max_row)
    for p in attr_products:
        u = stockholm_units(attr_nat, p)
        s = stockholm_sek(attr_nat, p)
        per_100k = round(u / sthlm_pop * 100000, 1) if sthlm_pop else None
        ws.append([p, u, s, per_100k])
    ws.append([])
    ws.append(['Cross-region context: Vyndaqel units per 100k by region (sorted by per-100k descending)'])
    ws[ws.max_row][0].font = Font(italic=True)
    ws.append(['Region', 'Vyndaqel units', 'Population', 'Vyndaqel units per 100k'])
    style_header(ws, ws.max_row)
    vynd_per_100k_rows = []
    for region, pop in pops.items():
        u = attr_nat.get('VYNDAQEL', {}).get(region, {}).get('units', 0.0)
        per_100k = u / pop * 100000 if pop else 0
        vynd_per_100k_rows.append([region, u, pop, round(per_100k, 1)])
    vynd_per_100k_rows.sort(key=lambda r: -r[3])
    for row in vynd_per_100k_rows:
        if row[0] == 'Region Stockholm':
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.fill = NEW_FILL
                cell.font = Font(bold=True)
        else:
            ws.append(row)
    ws.append(['Note', 'Stockholm at ~108/100k (rank ~mid-table) versus Norrbotten ~972/100k and Västerbotten ~600+/100k. Reflects the Norrland founder-variant cluster (CH-04, CH-17), NOT a Pfizer commercial gap. Stockholm ATTR strategy = absolute volume defense, not per-capita expansion. AMVUTTRA + BEYONTTRA penetration in Stockholm is the metric to watch (P1 carry-strategy for Hympavzi + Elrexfio depends on whether Karolinska cardiology / neurology stays on tafamidis or shifts.)'])
    ws[ws.max_row][1].alignment = DEFAULT_ALIGN
    ws.append([])

    # ---------- Section 3: Vaccines ----------
    ws.append(['3) Vaccines — Abrysvo lagging Arexvy in Stockholm; Prevenar 20 squeezed by Vaxneuvance'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT

    vac_products = ['ABRYSVO', 'AREXVY', 'PREVENAR 13', 'PREVENAR 20', 'VAXNEUVANCE',
                    'FSME-IMMUN VUXEN', 'FSME-IMMUN JUNIOR']
    ws.append(['Product', 'Stockholm units (3yr)', 'Stockholm SEK (3yr)'])
    style_header(ws, ws.max_row)
    for p in vac_products:
        u = stockholm_units(vac_nat, p)
        s = stockholm_sek(vac_nat, p)
        if u or s:  # only show products with actual presence
            ws.append([p, u, s])

    # RSV class: Abrysvo vs Arexvy
    abr_u = stockholm_units(vac_nat, 'ABRYSVO')
    arx_u = stockholm_units(vac_nat, 'AREXVY')
    rsv_total = abr_u + arx_u
    abr_share = round(100 * abr_u / rsv_total, 1) if rsv_total else None
    ws.append([])
    ws.append(['Abrysvo share of RSV vaccine class in Stockholm (units, %)', abr_share, '', f'{abr_u:.0f} of {rsv_total:.0f} class units'])
    if abr_share is not None:
        if abr_share >= 65:
            note = f'Stockholm Abrysvo dominant ({abr_share}%) — defend tender; commercial focus elsewhere.'
        elif abr_share >= 55:
            note = f'Stockholm Abrysvo at the boundary ({abr_share}%) — contested; tender / formulary timing matters more than commercial messaging.'
        elif abr_share >= 40:
            note = f'Stockholm Abrysvo MINORITY ({abr_share}%) — Arexvy is leading the RSV class in Stockholm. Concrete P3 vaccine play threat here, not opportunity. Different from the national picture (Abrysvo national 64.5% by SEK).'
        else:
            note = f'Stockholm Abrysvo LAGGING ({abr_share}%) — Arexvy clear leader. Stockholm RSV vaccine position is the weakest of any major region; P3 play needs targeted Stockholm tender / KOL strategy.'
        ws.append(['', note])

    # P20 vs P13 vs Vaxneuvance
    p13_u = stockholm_units(vac_nat, 'PREVENAR 13')
    p20_u = stockholm_units(vac_nat, 'PREVENAR 20')
    vxn_u = stockholm_units(vac_nat, 'VAXNEUVANCE')
    pneumo_total = p13_u + p20_u + vxn_u
    ws.append([])
    ws.append(['Pneumococcal class in Stockholm (units share, %)', '', '', ''])
    if pneumo_total:
        ws.append(['Prevenar 13 (legacy)', p13_u, '', round(100 * p13_u / pneumo_total, 1)])
        ws.append(['Prevenar 20', p20_u, '', round(100 * p20_u / pneumo_total, 1)])
        ws.append(['Vaxneuvance (MSD)', vxn_u, '', round(100 * vxn_u / pneumo_total, 1)])
        p20_share = round(100 * p20_u / pneumo_total, 1)
        vxn_share = round(100 * vxn_u / pneumo_total, 1)
        if vxn_share > p20_share:
            ws.append(['Note', f'Stockholm pneumococcal class is led by Vaxneuvance ({vxn_share}% units) over Prevenar 20 ({p20_share}%). White-space framing requires nuance: P20 is not the default; the conversion target is Vaxneuvance share, not just P13 legacy. Stockholm pneumococcal demand is large (largest absolute denominator); P3 vaccine play upside is real but the competitor to dislodge is MSD, not P13 inertia.'])
        else:
            ws.append(['Note', f'Stockholm Prevenar 20 leads ({p20_share}% units) over Vaxneuvance ({vxn_share}%). White-space remaining = P13 legacy candidate-for-conversion volume. P3 play in good shape here.'])
    ws.append([])

    # ---------- Section 4: Oncology footprint ----------
    ws.append(['4) Oncology — Stockholm is the absolute Pfizer footprint leader'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT

    onc_pfizer_lookup = {
        'IBRANCE': cdk46_nat,
        'TUKYSA': onc_tukysa,
        'TALZENNA': onc_talzenna,
        'XTANDI': onc_talzenna,  # XTANDI lives in Talzenna sheet (PARP/AR sheet)
        'LORVIQUA': onc_lorviqua,
        'XALKORI': onc_lorviqua,
        'ELREXFIO': onc_elrexfio,
    }
    ws.append(['Pfizer onc product', 'Stockholm units (3yr)', 'Stockholm SEK (3yr)', 'Stockholm rank (by SEK across 21 regions)'])
    style_header(ws, ws.max_row)
    for p, src in onc_pfizer_lookup.items():
        u = stockholm_units(src, p)
        s = stockholm_sek(src, p)
        # Compute Stockholm's rank by SEK
        all_regions_sek = [(r, src.get(p, {}).get(r, {}).get('sek', 0.0)) for r in pops]
        all_regions_sek.sort(key=lambda x: -x[1])
        rank = next((i + 1 for i, (r, _) in enumerate(all_regions_sek) if r == 'Region Stockholm'), None)
        ws.append([p, u, s, rank])
    ws.append(['Note', 'Stockholm leads or co-leads absolute Pfizer oncology footprint across ~all products (Ibrance, Tukysa, Talzenna, Xtandi, Lorviqua, Elrexfio). This is "biggest pie, smallest share gain delta" — defense priority across the Pfizer oncology portfolio. Cross-link to P4 precision oncology backbone.'])
    ws[ws.max_row][1].alignment = DEFAULT_ALIGN
    ws.append([])

    # ---------- Section 5: Stakeholders ----------
    ws.append(['5) Stakeholders — 3 of 8 cornerstones in Stockholm + full LK pool captured'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT

    stockholm_stakeholders = [
        ('Mats Ek', 'LK ordförande Region Stockholm', 'P5 cornerstone tier; Stockholm formulary lead (largest single regional formulary in Sweden)'),
        ('Rickard Malmström', 'NT-rådet member + Stockholm LK vice ordf', 'P5 cornerstone tier; dual national-and-regional engagement angle; clinical pharmacology'),
        ('Johan Bratt', 'NSG referensperson, prior CMO Region Stockholm', 'P5 cornerstone tier; national-tier expertise + Stockholm institutional knowledge'),
        ('Stockholm LK ledamotgrupp (17 named individuals)', 'Stockholm Läkemedelskommitté full membership captured 2026-04-27', 'See stakeholder mapping v9 Stockholm tab; engagement angle for P3 vaccines + P2 CDK4/6 formulary work'),
    ]
    ws.append(['Name', 'Role', 'Why on the cornerstone list'])
    style_header(ws, ws.max_row)
    for n, role, why in stockholm_stakeholders:
        ws.append([n, role, why])
    ws.append(['Note', 'Stockholm cornerstone density (3 of 8 = 37.5% of cornerstone tier from a region with 23.5% of population) is itself an engagement signal: the regional formulary, the national NT-rådet, and the NSG advisory chain all converge in this region. P5 governance play has its highest-leverage entry points here.'])
    ws[ws.max_row][1].alignment = DEFAULT_ALIGN
    ws.append([])

    # ---------- Section 6: Strategic implications ----------
    ws.append(['6) Strategic implications — the unified Stockholm story'])
    for cell in ws[ws.max_row]:
        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT
    implications = [
        ('Convergence region', 'Stockholm sits at the intersection of P2 (CDK4/6 defense — share is lowest of major regions, volume is largest), P3 (vaccines — Abrysvo lagging Arexvy in Stockholm specifically, Vaxneuvance leads pneumococcal not P20), P4 (oncology backbone — Stockholm is the largest Pfizer oncology denominator) and P5 (governance — 3 cornerstones + LK pool). It is the play-convergence region — not because every play is winning here, but because the leverage and risk both concentrate here.'),
        ('What Stockholm is NOT', 'Stockholm is NOT the ATTR-CM hot spot — that is Norrland. Stockholm ATTR strategy is volume defense + readiness for AMVUTTRA / BEYONTTRA shift, not per-capita expansion.'),
        ('Engagement angle 1 — formulary', 'P2 + P3: Stockholm LK (Mats Ek) is the lever for both CDK4/6 formulary stance and pneumococcal P20 conversion. Single relationship, two-play impact.'),
        ('Engagement angle 2 — national-tier policy', 'P5: Rickard Malmström dual NT-rådet / Stockholm LK position is the highest-leverage single relationship in the deck — national policy AND regional formulary in one person.'),
        ('Engagement angle 3 — clinical opinion leadership', 'P4: Karolinska oncology + Karolinska University Hospital are the de facto clinical-opinion leadership centre for Sweden. Tukysa / Talzenna / Lorviqua / Elrexfio adoption nationally tracks Karolinska adoption; engagement at the senior-oncologist level there is the leverage point for P4.'),
        ('Risk view', 'The same convergence makes Stockholm a single-point-of-failure region for the portfolio: a single formulary-restriction event in Stockholm has multi-play impact. Mitigation: spread defense across Halland (P2 strongest position), VGR (large second denominator), Skåne (national third pole) so no one region is a sole pivot.'),
    ]
    ws.append(['Theme', 'Implication'])
    style_header(ws, ws.max_row)
    for theme, imp in implications:
        ws.append([theme, imp])
        ws[ws.max_row][1].alignment = DEFAULT_ALIGN

    ws.append([])
    ws.append(['Methods note', 'Stockholm-specific aggregation pulled from raw IQVIA Vaccines (2026-04-02), RD/IM (2026-04-27), Oncology (2026-04-27). Cross-region context computed at sheet build time. Shares are by IQVIA pack count; SEK is sell-in (not net revenue). Stakeholder rows reference v9 stakeholder mapping; cornerstone list is the 8-name P5 list from v27 workbook + plays brief v4.'])
    ws[ws.max_row][1].alignment = DEFAULT_ALIGN

    widths = [44, 24, 22, 26, 30]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w
    ws.freeze_panes = 'A4'
    print(f'  Created {name} sheet (6 sections: CDK4/6, ATTR, Vaccines, Oncology, Stakeholders, Implications)')


# ============================================================================
# Version-bump housekeeping (README, Build pipeline)
# ============================================================================

def bump_internal_readme(wb):
    if 'README' not in wb.sheetnames:
        return
    ws = wb['README']
    n = 0
    new_count = len(wb.sheetnames)
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                replacements = [
                    ('62 sheets', f'{new_count} sheets'),
                    ('Sixty-two sheets', f'{new_count} sheets'),
                    ('master workbook v27', 'master workbook v28'),
                    ('Version 27', 'Version 28'),
                ]
                new_value = cell.value
                changed = False
                for old, new in replacements:
                    if old in new_value:
                        new_value = new_value.replace(old, new)
                        changed = True
                if changed:
                    cell.value = new_value
                    cell.fill = SECTION_FILL
                    n += 1
    print(f'  Bumped README sheet — {n} cells updated to v28 / {new_count} sheets')


def bump_build_pipeline(wb):
    if 'Build pipeline' not in wb.sheetnames:
        return
    ws = wb['Build pipeline']
    ws.append(['Workbook v27 → v28 (THIS BUILD)', '06_master_workbook_v28.xlsx', 'build_workbook_v28_abc.py',
               'A+B+C deferred analyses: NEW Competitive class trajectories sheet (6 competitors, last-6 vs prev-6 mo); '
               'NEW Pfizer product trajectories sheet (5 Pfizer products, same methodology); '
               'NEW Stockholm strategic profile sheet (synthesis across CDK4/6, ATTR, Vaccines, Oncology, Stakeholders).'])
    for cell in ws[ws.max_row]:
        cell.fill = NEW_FILL
        cell.alignment = DEFAULT_ALIGN
    print(f'  Added v27→v28 row to Build pipeline')


def main():
    print(f'Copying v27 → v28')
    V28_WORKING.parent.mkdir(parents=True, exist_ok=True)
    copyfile(V27, V28_WORKING)
    wb = openpyxl.load_workbook(V28_WORKING)

    print('\n=== A — Competitive class trajectories ===')
    add_competitive_class_trajectories_sheet(wb)

    print('\n=== C — Pfizer product trajectories ===')
    add_pfizer_trajectories_sheet(wb)

    print('\n=== B — Stockholm strategic profile ===')
    add_stockholm_strategic_profile_sheet(wb)

    print('\n=== Version bump housekeeping ===')
    bump_internal_readme(wb)
    bump_build_pipeline(wb)

    wb.save(V28_WORKING)
    print(f'\nSaved {V28_WORKING}')

    copyfile(V28_WORKING, V28_DELIVERY)
    print(f'Copied to {V28_DELIVERY}')

    wb_check = openpyxl.load_workbook(V28_WORKING, read_only=True)
    print(f'\nv28 has {len(wb_check.sheetnames)} sheets')
    for s in ['Competitive class trajectories', 'Pfizer product trajectories', 'Stockholm strategic profile']:
        if s in wb_check.sheetnames:
            print(f'  ★ NEW in v28: {s}')


if __name__ == '__main__':
    main()
