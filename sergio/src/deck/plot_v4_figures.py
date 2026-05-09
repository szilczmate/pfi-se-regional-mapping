# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Generate Phase B figures for v4.

NEW:
- F1: Pfizer total footprint per region (unified Vaccines + RD/IM + Oncology)
- F2: Verzenios trajectory by region — last-6 vs prev-6 slope (the honest plateau view)

REGENERATE with layout fixes:
- O3 Pfizer oncology mosaic — fix title overlap
- C3 Pfizer RD/IM mosaic — fix title overlap
- A_abrysvo — clarify SEK vs units in title; soften "override" to "regional pattern despite avvakta"
"""

from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v27.xlsx"
RAW_DIR = ROOT / "working" / "data" / "raw"
ONC_RAW = RAW_DIR / "VitiScience Oncology_Apr-27-2026.xlsx"
RDIM_RAW = RAW_DIR / "VitiScience RD_IM_Apr-27-2026.xlsx"
VAC_RAW = RAW_DIR / "VitiScience_Vaccines_Apr-02-2026.xlsx"
OUT = ROOT / "delivery" / "figures"
OUT.mkdir(exist_ok=True)

NAVY = "#1F3A5F"
AMBER = "#D97A1F"
LIGHT_GREY = "#E8E8E8"
DARK_GREY = "#333333"
PFIZER_BLUE = "#0050A0"
VACCINES_GREEN = "#2D7A4D"
RDIM_TEAL = "#5B9BD5"
ONCOLOGY_PURPLE = "#7E5BAA"
PLATEAU_GREY = "#999999"
COMPOUND_RED = "#C73E1D"

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.edgecolor": DARK_GREY,
    "xtick.color": DARK_GREY,
    "ytick.color": DARK_GREY,
    "ytick.left": False,
    "axes.axisbelow": True,
})


def grid_x(ax):
    ax.grid(axis="x", color=LIGHT_GREY, linewidth=0.6)
    ax.set_axisbelow(True)


def short(region):
    return (region.replace("Region ", "")
                  .replace("Västra Götalandsregionen", "Västra Götaland")
                  .replace(" län", "")
                  .replace("Jämtland Härjedalen", "Jämtland H."))


# =============================================================================
# F1: Pfizer total footprint per region (unified)
# =============================================================================

def figure_pfizer_total_footprint():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws = wb['Pfizer total footprint']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    region_col = 0
    pop_col = headers.index('Population')
    total_sek_col = headers.index('Total Pfizer SEK')
    per_100k_col = headers.index('Total Pfizer SEK per 100k')
    vac_col = headers.index('Vaccines SEK')
    rdim_col = headers.index('RD/IM SEK')
    onc_col = headers.index('Oncology SEK')

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[region_col] or 'NATIONAL' in str(row[region_col]):
            continue
        rows.append({
            'region': row[region_col],
            'pop': row[pop_col],
            'total': row[total_sek_col],
            'per_100k': row[per_100k_col],
            'vac': row[vac_col],
            'rdim': row[rdim_col],
            'onc': row[onc_col],
        })

    # Sort by per-100k (more interesting than absolute SEK)
    rows.sort(key=lambda r: -r['per_100k'])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), gridspec_kw={'wspace': 0.45})
    region_labels = [short(r['region']) for r in rows]
    y_pos = np.arange(len(region_labels))[::-1]

    # Left: stacked bar by portfolio (per capita)
    vac_pc = np.array([r['vac'] / r['pop'] * 100000 / 1e3 for r in rows])  # kSEK per 100k
    rdim_pc = np.array([r['rdim'] / r['pop'] * 100000 / 1e3 for r in rows])
    onc_pc = np.array([r['onc'] / r['pop'] * 100000 / 1e3 for r in rows])

    ax1.barh(y_pos, vac_pc, color=VACCINES_GREEN, label='Vaccines', edgecolor='white', linewidth=0.5)
    ax1.barh(y_pos, rdim_pc, left=vac_pc, color=RDIM_TEAL, label='RD/IM', edgecolor='white', linewidth=0.5)
    ax1.barh(y_pos, onc_pc, left=vac_pc + rdim_pc, color=ONCOLOGY_PURPLE, label='Oncology', edgecolor='white', linewidth=0.5)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(region_labels, fontsize=9)
    ax1.set_xlabel('Pfizer SEK per 100,000 population (3 yr cumulative, kSEK)', fontsize=10, color=DARK_GREY)
    ax1.set_title('Per-capita Pfizer footprint', fontsize=13, color=NAVY, loc='left', fontweight='bold')
    ax1.legend(loc='lower right', frameon=False, fontsize=9)
    grid_x(ax1)

    # Annotate top per-100k
    for i, r in zip(y_pos, rows):
        total_pc = r['per_100k'] / 1e3
        if i in [y_pos[0], y_pos[1], y_pos[-1]]:
            ax1.text(total_pc + 5, i, f'{total_pc:.0f}k', fontsize=8, color=NAVY, va='center', fontweight='bold')

    # Right: absolute SEK rank
    abs_total = np.array([r['total'] / 1e6 for r in rows])
    rows_sorted_abs = sorted(rows, key=lambda r: -r['total'])
    abs_total_sorted = np.array([r['total'] / 1e6 for r in rows_sorted_abs])
    abs_labels_sorted = [short(r['region']) for r in rows_sorted_abs]
    abs_vac = np.array([r['vac'] / 1e6 for r in rows_sorted_abs])
    abs_rdim = np.array([r['rdim'] / 1e6 for r in rows_sorted_abs])
    abs_onc = np.array([r['onc'] / 1e6 for r in rows_sorted_abs])
    y_pos2 = np.arange(len(abs_labels_sorted))[::-1]

    ax2.barh(y_pos2, abs_vac, color=VACCINES_GREEN, label='Vaccines', edgecolor='white', linewidth=0.5)
    ax2.barh(y_pos2, abs_rdim, left=abs_vac, color=RDIM_TEAL, label='RD/IM', edgecolor='white', linewidth=0.5)
    ax2.barh(y_pos2, abs_onc, left=abs_vac + abs_rdim, color=ONCOLOGY_PURPLE, label='Oncology', edgecolor='white', linewidth=0.5)
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(abs_labels_sorted, fontsize=9)
    ax2.set_xlabel('Pfizer SEK absolute (3 yr cumulative, MSEK)', fontsize=10, color=DARK_GREY)
    ax2.set_title('Absolute Pfizer footprint', fontsize=13, color=NAVY, loc='left', fontweight='bold')
    grid_x(ax2)

    fig.suptitle('Pfizer Sweden — total IQVIA footprint per region (17 products, 3 portfolios)',
                 fontsize=15, color=NAVY, y=0.98, x=0.07, ha='left', fontweight='bold')
    fig.text(0.07, 0.94,
             'Per-capita view (left) shows where Pfizer is structurally strong; absolute view (right) shows scale. '
             'Norrbotten + Västerbotten lead per-capita driven by Vyndaqel; Stockholm leads absolute driven by oncology.',
             fontsize=10, color=DARK_GREY, style='italic')
    fig.text(0.07, 0.02,
             'Source: IQVIA Vaccines + RD/IM + Oncology extracts, cumulative Apr 2023 – Mar 2026. '
             '17 Pfizer products: Abrysvo, Prevenar 13/20, FSME-IMMUN VUXEN/JUNIOR, Vyndaqel, Vydura, Paxlovid, BeneFIX, Refacto AF, '
             'Ibrance, Tukysa, Talzenna, Lorviqua, Xalkori, Elrexfio, Xtandi.',
             fontsize=8, color=DARK_GREY, style='italic')
    plt.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.10)

    out_path = OUT / 'F1_pfizer_total_footprint_per_region.png'
    fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved {out_path}')


# =============================================================================
# F2: Verzenios trajectory honest view — last-6 vs prev-6
# =============================================================================

def figure_verzenios_trajectory_honest():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws = wb['Verzenios trajectory']

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0] or 'NATIONAL' in str(row[0]) or 'Methods note' in str(row[0]) or row[0] == 'Why this matters' or row[0] == '':
            continue
        if row[3] is not None and row[4] is not None:
            rows.append({
                'region': row[0],
                'last_6': row[3],
                'pct': row[4],
                'verdict': row[5],
            })
    rows.sort(key=lambda r: -r['last_6'])

    fig, ax = plt.subplots(figsize=(11, 7))
    labels = [short(r['region']) for r in rows]
    pcts = np.array([r['pct'] for r in rows])
    last_6 = np.array([r['last_6'] for r in rows])
    y_pos = np.arange(len(labels))[::-1]

    # Color by verdict
    colors = []
    for r in rows:
        v = r['verdict']
        if 'COMPOUNDING' in v:
            colors.append(COMPOUND_RED)
        elif 'GROWING' in v:
            colors.append(AMBER)
        elif 'PLATEAUING' in v:
            colors.append(PLATEAU_GREY)
        elif 'DECLINING' in v:
            colors.append('#5C8DA0')
        elif 'CONTRACTING' in v:
            colors.append(PFIZER_BLUE)
        else:
            colors.append(DARK_GREY)

    ax.barh(y_pos, pcts, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Verzenios change: last 6 months vs prior 6 months (%)', fontsize=10, color=DARK_GREY)
    ax.axvline(0, color=DARK_GREY, linewidth=1)
    ax.axvspan(-5, 5, color=PLATEAU_GREY, alpha=0.15, zorder=0)
    ax.text(0.5, len(labels) + 0.5, '±5% plateau zone', fontsize=8, color=DARK_GREY,
            ha='center', va='bottom', style='italic')

    ax.set_title('Verzenios is plateauing nationally — not compounding',
                 fontsize=14, color=NAVY, loc='left', pad=15)
    fig.text(0.07, 0.93,
             'Last-6-month slope analysis. National Verzenios trajectory: -0.1% (PLATEAUING). '
             'Stockholm, VGR, Skåne — Pfizer\'s three biggest CDK4/6 markets — all PLATEAUING. The +114% / +128% / +192% '
             '1H-vs-2H comparisons reflect the early ramp; the most recent window shows the three-way race has stabilised.',
             fontsize=10, color=DARK_GREY, style='italic')

    # Annotate volume
    for i, r in zip(y_pos, rows):
        x = r['pct']
        ax.text(x + (3 if x >= 0 else -3), i,
                f"({r['last_6']:,.0f} u)", fontsize=8, color=DARK_GREY, va='center',
                ha='left' if x >= 0 else 'right')

    fig.text(0.07, 0.02,
             'Source: IQVIA Oncology extract 2026-04-27, ATC L01EF03 (abemaciclib). Last 6 months: Oct 2025 – Mar 2026. Prior 6 months: Apr 2025 – Sep 2025.',
             fontsize=8, color=DARK_GREY, style='italic')
    plt.subplots_adjust(left=0.18, right=0.95, top=0.88, bottom=0.10)

    out_path = OUT / 'F2_verzenios_trajectory_honest.png'
    fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved {out_path}')


# =============================================================================
# Regenerate O3 / C3 / A_abrysvo with layout fixes
# =============================================================================

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


def regen_o3_pfizer_oncology_mosaic():
    """Fix title overlap. Use clear space at top, smaller per-panel labels."""
    wb_raw = openpyxl.load_workbook(ONC_RAW, read_only=True, data_only=True)
    PRODUCT_SHEET = {
        'IBRANCE': 'Ibrance', 'TUKYSA': 'Tukysa L01EH', 'TALZENNA': 'Talzenna',
        'LORVIQUA': 'Lorviqua L01ED', 'ELREXFIO': 'Elrexfio', 'XTANDI': 'Talzenna',
    }
    products = [
        ('IBRANCE', 'CDK4/6 · breast cancer · core P2', PFIZER_BLUE),
        ('TUKYSA', 'HER2-SM · brain mets · 85% class share', NAVY),
        ('TALZENNA', 'PARP · 5% class share (Lynparza-bound)', AMBER),
        ('LORVIQUA', 'ALK · NSCLC · 27% class share', RDIM_TEAL),
        ('ELREXFIO', 'BCMA bispecific · MM · 47% share', '#5B9D7E'),
        ('XTANDI', 'Androgen receptor · 1.42 BSEK', COMPOUND_RED),
    ]

    pf_data = defaultdict(lambda: defaultdict(lambda: {'sek': 0.0, 'units': 0.0}))
    for product, sheet_name in PRODUCT_SHEET.items():
        ws = wb_raw[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != product:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2])
            if not region:
                continue
            for idx in sek_cols:
                v = row[idx]
                if v is not None:
                    pf_data[product][region]['sek'] += v

    pops = {}
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws_rm = wb['Region master']
    headers = [c.value for c in next(ws_rm.iter_rows(min_row=1, max_row=1))]
    for row in ws_rm.iter_rows(min_row=2, values_only=True):
        if row[headers.index('Region')]:
            pops[row[headers.index('Region')]] = row[headers.index('Population')]

    fig, axes = plt.subplots(2, 3, figsize=(15.5, 11), gridspec_kw={'hspace': 0.65, 'wspace': 0.45})

    for ax, (product, subtitle, color) in zip(axes.flat, products):
        d = pf_data[product]
        rows = [(r, d.get(r, {'sek': 0})['sek']) for r in pops.keys()]
        rows.sort(key=lambda x: -x[1])
        rows = [r for r in rows if r[1] > 0]
        if not rows:
            ax.set_visible(False)
            continue
        labels = [short(r[0]) for r in rows]
        vals = np.array([r[1] / 1e6 for r in rows])
        y_pos = np.arange(len(labels))[::-1]

        ax.barh(y_pos, vals, color=color, edgecolor='white', linewidth=0.4)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel('MSEK (3 yr cumulative)', fontsize=9, color=DARK_GREY)
        # Title with clear space
        ax.set_title(f'{product}\n{subtitle}', fontsize=11, color=NAVY, loc='left', fontweight='bold', pad=10)
        grid_x(ax)
        # Top 3 annotations
        for i, (region, val) in enumerate(rows[:3]):
            ax.text(val/1e6 + (vals.max() / 80), len(rows) - i - 1,
                    f'{val/1e6:.0f}M', fontsize=8, color=color, va='center', fontweight='bold')

    fig.suptitle('Pfizer oncology portfolio — regional sell-in cumulative Apr 2023 – Mar 2026',
                 fontsize=15, color=NAVY, y=0.995, x=0.05, ha='left', fontweight='bold')
    fig.text(0.05, 0.965,
             'Six Pfizer oncology assets. Tukysa class-dominant. Talzenna structurally Lynparza-bound. '
             'Lorviqua 2L+ ALK. Elrexfio at parity with Tecvayli. Xtandi a major asset previously not in our analysis.',
             fontsize=10, color=DARK_GREY, style='italic')
    fig.text(0.05, 0.01, 'Source: IQVIA Oncology 2026-04-27. SEK shown; unit comparability across products limited (see Methods notes).',
             fontsize=8, color=DARK_GREY, style='italic')
    plt.subplots_adjust(left=0.05, right=0.97, top=0.92, bottom=0.05)

    out_path = OUT / 'O3_pfizer_oncology_portfolio_mosaic.png'
    fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved (regenerated) {out_path}')


def regen_c3_pfizer_rdim_mosaic():
    wb_raw = openpyxl.load_workbook(RDIM_RAW, read_only=True, data_only=True)
    PRODUCT_TA = {'VYNDAQEL': 'ATTR', 'VYDURA': 'Migraine', 'PAXLOVID': 'Covid', 'BENEFIX': 'Haemophilia'}
    products = [
        ('VYNDAQEL', 'ATTR-CM · 94% class share · core P1', PFIZER_BLUE),
        ('VYDURA', 'Migraine CGRP · 5% class share', AMBER),
        ('PAXLOVID', 'COVID antiviral · per-protocol use', RDIM_TEAL),
        ('BENEFIX', 'Haemophilia FIX · niche legacy', NAVY),
    ]

    pf_data = defaultdict(lambda: defaultdict(lambda: {'sek': 0.0}))
    for product, sheet_name in PRODUCT_TA.items():
        ws = wb_raw[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != product:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2])
            if not region:
                continue
            for idx in sek_cols:
                v = row[idx]
                if v is not None:
                    pf_data[product][region]['sek'] += v

    pops = {}
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws_rm = wb['Region master']
    headers = [c.value for c in next(ws_rm.iter_rows(min_row=1, max_row=1))]
    for row in ws_rm.iter_rows(min_row=2, values_only=True):
        if row[headers.index('Region')]:
            pops[row[headers.index('Region')]] = row[headers.index('Population')]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.65, 'wspace': 0.4})

    for ax, (product, subtitle, color) in zip(axes.flat, products):
        d = pf_data[product]
        rows = [(r, d.get(r, {'sek': 0})['sek']) for r in pops.keys()]
        rows.sort(key=lambda x: -x[1])
        rows = [r for r in rows if r[1] > 0]
        if not rows:
            ax.set_visible(False)
            continue
        labels = [short(r[0]) for r in rows]
        vals = np.array([r[1] / 1e6 for r in rows])
        y_pos = np.arange(len(labels))[::-1]

        ax.barh(y_pos, vals, color=color, edgecolor='white', linewidth=0.4)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel('MSEK (3 yr cumulative)', fontsize=9, color=DARK_GREY)
        ax.set_title(f'{product}\n{subtitle}', fontsize=11, color=NAVY, loc='left', fontweight='bold', pad=10)
        grid_x(ax)
        for i, (region, val) in enumerate(rows[:3]):
            ax.text(val/1e6 + (vals.max() / 80), len(rows) - i - 1,
                    f'{val/1e6:.0f}M', fontsize=8, color=color, va='center', fontweight='bold')

    fig.suptitle('Pfizer RD/IM portfolio — regional sell-in cumulative Apr 2023 – Mar 2026',
                 fontsize=15, color=NAVY, y=0.995, x=0.05, ha='left', fontweight='bold')
    fig.text(0.05, 0.96,
             'Vyndaqel anchors P1 (1.58 BSEK over 3 yr). Vydura small but visible (53 MSEK). Paxlovid + BeneFIX broadly distributed minor footprint.',
             fontsize=10, color=DARK_GREY, style='italic')
    fig.text(0.05, 0.01, 'Source: IQVIA RD/IM extract 2026-04-27.',
             fontsize=8, color=DARK_GREY, style='italic')
    plt.subplots_adjust(left=0.05, right=0.97, top=0.92, bottom=0.06)

    out_path = OUT / 'C3_pfizer_rdim_portfolio_mosaic.png'
    fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved (regenerated) {out_path}')


def regen_a_abrysvo():
    """Regenerate Abrysvo regional pattern with explicit SEK label and softened claim."""
    wb_raw = openpyxl.load_workbook(VAC_RAW, read_only=True, data_only=True)
    ws = wb_raw['Sweden Sell-In']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]

    # Compute Pfizer Abrysvo + GSK Arexvy SEK per region
    region_data = defaultdict(lambda: {'abrysvo_sek': 0.0, 'arexvy_sek': 0.0,
                                        'abrysvo_units': 0.0, 'arexvy_units': 0.0})
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if not region or product not in ('ABRYSVO', 'AREXVY'):
            continue
        sek = sum(v for i, v in enumerate(row) if i in sek_cols and v is not None)
        units = sum(v for i, v in enumerate(row) if i in units_cols and v is not None)
        if product == 'ABRYSVO':
            region_data[region]['abrysvo_sek'] += sek
            region_data[region]['abrysvo_units'] += units
        else:
            region_data[region]['arexvy_sek'] += sek
            region_data[region]['arexvy_units'] += units

    rows = []
    for region, d in region_data.items():
        total_sek = d['abrysvo_sek'] + d['arexvy_sek']
        total_units = d['abrysvo_units'] + d['arexvy_units']
        sek_share = 100 * d['abrysvo_sek'] / total_sek if total_sek > 0 else 0
        units_share = 100 * d['abrysvo_units'] / total_units if total_units > 0 else 0
        rows.append({'region': region, 'sek_share': sek_share, 'units_share': units_share,
                     'abrysvo_sek': d['abrysvo_sek']})
    rows.sort(key=lambda r: -r['sek_share'])

    fig, ax = plt.subplots(figsize=(11, 7))
    labels = [short(r['region']) for r in rows]
    sek_shares = np.array([r['sek_share'] for r in rows])
    units_shares = np.array([r['units_share'] for r in rows])
    y_pos = np.arange(len(labels))[::-1]

    width = 0.4
    ax.barh(y_pos + width/2, sek_shares, width, color=PFIZER_BLUE, label='Share by SEK', edgecolor='white', linewidth=0.5)
    ax.barh(y_pos - width/2, units_shares, width, color=AMBER, label='Share by units (doses)', edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Pfizer Abrysvo share of RSV vaccine market (%)', fontsize=10, color=DARK_GREY)
    ax.axvline(60, linestyle='--', color=DARK_GREY, linewidth=0.8, alpha=0.6)
    ax.text(60.5, len(labels) - 0.5, '60% reference', fontsize=8, color=DARK_GREY, va='center', style='italic')

    ax.set_title('Abrysvo — regional pattern despite NT-rådet "avvakta" hold',
                 fontsize=14, color=NAVY, loc='left', pad=15)
    fig.text(0.07, 0.93,
             'NT-rådet issued an "avvakta" hold on Abrysvo on 2023-10-05. National share by SEK: 64.5% (17 of 21 regions ≥ 60%). '
             'By units (doses): 56.8% (only 11 of 21 regions ≥ 60%). The SEK and unit views tell different stories — both are shown.',
             fontsize=10, color=DARK_GREY, style='italic')

    ax.legend(loc='lower right', frameon=False, fontsize=9, bbox_to_anchor=(1.0, -0.18), ncol=2)
    grid_x(ax)
    fig.text(0.07, 0.03,
             'Source: IQVIA Vaccines extract 2026-04-02 (ATC J07BX05). Pfizer Abrysvo vs GSK Arexvy. National RSV market includes only these two products in Sweden.',
             fontsize=8, color=DARK_GREY, style='italic')
    plt.subplots_adjust(left=0.16, right=0.96, top=0.86, bottom=0.16)

    out_path = OUT / 'A_abrysvo_avvakta_signal.png'
    fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved (regenerated) {out_path}')


if __name__ == '__main__':
    figure_pfizer_total_footprint()
    figure_verzenios_trajectory_honest()
    regen_o3_pfizer_oncology_mosaic()
    regen_c3_pfizer_rdim_mosaic()
    regen_a_abrysvo()
    print('\nAll Phase B figures generated.')
