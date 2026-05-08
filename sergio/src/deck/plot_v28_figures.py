# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Generate F3 + F4 figures for v28 deliverables.

F3 — Multi-class trajectory bar chart (6 competitors + 5 Pfizer products).
F4 — Stockholm multi-dimensional view (CDK4/6 share, ATTR per-100k, Abrysvo share, oncology rank, cornerstone density).
"""

from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW_DIR = ROOT / "working" / "data" / "raw"
RDIM_RAW = RAW_DIR / "VitiScience RD_IM_Apr-27-2026.xlsx"
ONC_RAW = RAW_DIR / "VitiScience Oncology_Apr-27-2026.xlsx"
VAC_RAW = RAW_DIR / "VitiScience_Vaccines_Apr-02-2026.xlsx"
FIG_DIR = ROOT / "delivery" / "figures"

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

PFIZER_BLUE = '#0093D0'
PFIZER_NAVY = '#1F3A5F'
COMPETITOR_GREY = '#888888'
PLATEAU_AMBER = '#E0A030'
DECLINE_RED = '#C04030'
GROWTH_GREEN = '#3A8C50'


def aggregate_product_monthly(file_path, sheet_name, product_name):
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    out = defaultdict(lambda: [0.0] * len(units_cols))
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] != product_name:
            continue
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2])
        if not region:
            continue
        for i, idx in enumerate(units_cols):
            v = row[idx]
            if v is not None:
                out[region][i] += v
    n = len(units_cols)
    nat = [sum(out[r][i] for r in out.keys()) for i in range(n)]
    return nat


def slope_pct(monthly):
    n = len(monthly)
    last_6 = sum(monthly[n - 6:])
    prev_6 = sum(monthly[n - 12:n - 6])
    return 100 * (last_6 - prev_6) / prev_6 if prev_6 > 0 else None


# ----------------------------------------------------------------------------
# F3 — Multi-class trajectory bar chart (competitors + Pfizer products)
# ----------------------------------------------------------------------------

def plot_f3():
    targets = [
        # (label, file, sheet, product, role)
        ('Verzenios',  ONC_RAW,  'Ibrance',         'VERZENIOS',  'competitor'),
        ('Tecvayli',   ONC_RAW,  'Elrexfio',        'TECVAYLI',   'competitor'),
        ('Alecensa',   ONC_RAW,  'Lorviqua L01ED',  'ALECENSA',   'competitor'),
        ('Lynparza',   ONC_RAW,  'Talzenna',        'LYNPARZA',   'competitor'),
        ('AMVUTTRA',   RDIM_RAW, 'ATTR',            'AMVUTTRA',   'competitor'),
        ('BEYONTTRA',  RDIM_RAW, 'ATTR',            'BEYONTTRA',  'competitor'),
        ('Ibrance',    ONC_RAW,  'Ibrance',         'IBRANCE',    'pfizer'),
        ('Vyndaqel',   RDIM_RAW, 'ATTR',            'VYNDAQEL',   'pfizer'),
        ('Tukysa',     ONC_RAW,  'Tukysa L01EH',    'TUKYSA',     'pfizer'),
        ('Talzenna',   ONC_RAW,  'Talzenna',        'TALZENNA',   'pfizer'),
        ('Elrexfio',   ONC_RAW,  'Elrexfio',        'ELREXFIO',   'pfizer'),
    ]

    rows = []
    for label, fpath, sheet, prod, role in targets:
        nat = aggregate_product_monthly(fpath, sheet, prod)
        pct = slope_pct(nat)
        rows.append({'label': label, 'pct': pct, 'role': role})

    # Cap AMVUTTRA pct to keep scale readable; real value is ~9300%
    capped = []
    for r in rows:
        if r['pct'] is None:
            capped.append({**r, 'pct': 0, 'note': 'just-launched'})
        elif r['pct'] > 200:
            capped.append({**r, 'pct': 200, 'note': f'actual {r["pct"]:.0f}%'})
        else:
            capped.append({**r, 'pct': r['pct'], 'note': None})

    fig, ax = plt.subplots(figsize=(11, 6.5))
    labels = [r['label'] for r in capped]
    pcts = [r['pct'] for r in capped]
    colors = []
    for r, original in zip(capped, rows):
        op = original['pct']
        is_pfizer = r['role'] == 'pfizer'
        if op is None:
            colors.append(COMPETITOR_GREY if not is_pfizer else PFIZER_BLUE)
        elif op > 30:
            colors.append(GROWTH_GREEN)
        elif op > 5:
            colors.append('#7AB890' if not is_pfizer else PFIZER_BLUE)
        elif op >= -5:
            colors.append(PLATEAU_AMBER)
        elif op >= -20:
            colors.append('#D08060')
        else:
            colors.append(DECLINE_RED)

    bars = ax.bar(labels, pcts, color=colors, edgecolor='black', linewidth=0.6)
    # Mark Pfizer products with a navy edge
    for bar, r in zip(bars, capped):
        if r['role'] == 'pfizer':
            bar.set_edgecolor(PFIZER_NAVY)
            bar.set_linewidth(2.5)

    # Plateau zone shading
    ax.axhspan(-5, 5, color='#FFF2CC', alpha=0.5, zorder=0)
    ax.axhline(0, color='black', linewidth=0.7)
    ax.axhline(30, color=GROWTH_GREEN, linestyle='--', linewidth=0.6, alpha=0.6)
    ax.axhline(-20, color=DECLINE_RED, linestyle='--', linewidth=0.6, alpha=0.6)

    # Annotate bars with original % (or "n/a" / "post-launch")
    for bar, r, original in zip(bars, capped, rows):
        op = original['pct']
        h = bar.get_height()
        if op is None:
            label = 'just-launched'
            y = h + 4
        elif op > 200:
            label = f'+{op:.0f}%'
            y = h + 4
        else:
            label = f'{op:+.1f}%'
            y = h + (4 if h >= 0 else -10)
        ax.text(bar.get_x() + bar.get_width() / 2, y, label,
                ha='center', va='bottom' if y >= 0 else 'top', fontsize=8.5, fontweight='bold')

    ax.set_ylabel('Last-6 vs Prev-6 month units (%)', fontsize=10)
    ax.set_title('F3 — Multi-class trajectory: 6 competitors + 5 Pfizer products\n'
                 'Last-6mo (Oct 2025–Mar 2026) vs Prev-6mo (Apr–Sep 2025) IQVIA units',
                 fontsize=11, fontweight='bold', loc='left', color=PFIZER_NAVY)
    ax.text(0.0, -0.18,
            'Plateau band ±5%. Pfizer products bordered in navy. AMVUTTRA capped at +200% on chart (actual +9300% post-launch ramp).\n'
            'Verdicts: COMPOUNDING >+30% / GROWING +5–+30% / PLATEAUING ±5% / DECLINING −5 to −20% / CONTRACTING <−20%. Source: IQVIA RD/IM 2026-04-27 + Oncology 2026-04-27.',
            transform=ax.transAxes, fontsize=8, color='#444', ha='left')
    plt.xticks(rotation=30, ha='right')
    ax.set_ylim(-30, 220)
    ax.grid(axis='y', alpha=0.25)
    plt.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.28)

    out = FIG_DIR / 'F3_multiclass_trajectory.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


# ----------------------------------------------------------------------------
# F4 — Stockholm multi-dimensional anomaly view
# ----------------------------------------------------------------------------

def plot_f4():
    """Five-dimension Stockholm view as a 2x3 grid (1 panel left blank for title/notes)."""
    fig = plt.figure(figsize=(13, 8.5))
    gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.30,
                          left=0.06, right=0.98, top=0.92, bottom=0.07)

    # ---- Panel 1: CDK4/6 Pfizer share by region (Stockholm highlighted) ----
    cdk_data = []
    for fpath, sheet, prod in [(ONC_RAW, 'Ibrance', 'IBRANCE'),
                                (ONC_RAW, 'Ibrance', 'VERZENIOS'),
                                (ONC_RAW, 'Ibrance', 'KISQALI')]:
        nat = aggregate_product_monthly(fpath, sheet, prod)  # not used for this panel
    # For per-region we need a different aggregation:
    def per_region_units(file_path, sheet_name, product_name):
        wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb_raw[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
        out = defaultdict(float)
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != product_name:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2])
            if not region:
                continue
            for idx in units_cols:
                v = row[idx]
                if v is not None:
                    out[region] += v
        return dict(out)

    ibr = per_region_units(ONC_RAW, 'Ibrance', 'IBRANCE')
    ver = per_region_units(ONC_RAW, 'Ibrance', 'VERZENIOS')
    kis = per_region_units(ONC_RAW, 'Ibrance', 'KISQALI')
    regions = sorted(set(ibr) | set(ver) | set(kis))
    shares = []
    for r in regions:
        total = ibr.get(r, 0) + ver.get(r, 0) + kis.get(r, 0)
        share = 100 * ibr.get(r, 0) / total if total else None
        shares.append((r, share))
    shares = [s for s in shares if s[1] is not None]
    shares.sort(key=lambda x: x[1])

    ax1 = fig.add_subplot(gs[0, 0])
    names = [s[0].replace('Region ', '') for s in shares]
    vals = [s[1] for s in shares]
    sthlm_idx = next(i for i, n in enumerate(names) if 'Stockholm' in n)
    colors1 = ['#cccccc'] * len(names)
    colors1[sthlm_idx] = PFIZER_BLUE
    ax1.barh(names, vals, color=colors1)
    nat_avg = 100 * sum(ibr.values()) / (sum(ibr.values()) + sum(ver.values()) + sum(kis.values()))
    ax1.axvline(nat_avg, color=DECLINE_RED, linestyle='--', linewidth=1, alpha=0.7)
    ax1.text(nat_avg + 0.5, 0.5, f'national {nat_avg:.0f}%', color=DECLINE_RED, fontsize=8)
    ax1.set_xlabel('Pfizer (Ibrance) share of CDK4/6 by units (%)', fontsize=9)
    ax1.set_title('1) CDK4/6 — Stockholm Pfizer share', fontsize=10, fontweight='bold', color=PFIZER_NAVY)
    ax1.tick_params(axis='y', labelsize=7.5)
    ax1.grid(axis='x', alpha=0.25)

    # ---- Panel 2: ATTR Vyndaqel per-100k by region (Stockholm highlighted) ----
    pop = {
        'Region Stockholm': 2473307, 'Region Uppsala': 407912, 'Region Sörmland': 301542,
        'Region Östergötland': 472446, 'Region Jönköpings län': 370009, 'Region Kronoberg': 203351,
        'Region Kalmar': 246352, 'Region Gotland': 60971, 'Region Blekinge': 157223,
        'Region Skåne': 1428626, 'Region Halland': 345074, 'Västra Götalandsregionen': 1772821,
        'Region Värmland': 283384, 'Region Örebro län': 308375, 'Region Västmanland': 281158,
        'Region Dalarna': 286546, 'Region Gävleborg': 284558, 'Region Västernorrland': 241458,
        'Region Jämtland Härjedalen': 132839, 'Region Västerbotten': 281138,
        'Region Norrbotten': 248620,
    }
    vynd = per_region_units(RDIM_RAW, 'ATTR', 'VYNDAQEL')
    per_100k = sorted(
        [(r, v / pop[r] * 100000) for r, v in vynd.items() if r in pop],
        key=lambda x: x[1]
    )
    ax2 = fig.add_subplot(gs[0, 1])
    names2 = [r.replace('Region ', '') for r, _ in per_100k]
    vals2 = [v for _, v in per_100k]
    sthlm_idx2 = next(i for i, n in enumerate(names2) if 'Stockholm' in n)
    colors2 = ['#cccccc'] * len(names2)
    colors2[sthlm_idx2] = PFIZER_BLUE
    ax2.barh(names2, vals2, color=colors2)
    ax2.set_xlabel('Vyndaqel units per 100k population', fontsize=9)
    ax2.set_title('2) ATTR — Stockholm per-capita vs Norrland', fontsize=10, fontweight='bold', color=PFIZER_NAVY)
    ax2.tick_params(axis='y', labelsize=7.5)
    ax2.grid(axis='x', alpha=0.25)

    # ---- Panel 3: Abrysvo share by region ----
    wb_v = openpyxl.load_workbook(VAC_RAW, read_only=True)
    vac_sn = wb_v.sheetnames[0]
    abr = per_region_units(VAC_RAW, vac_sn, 'ABRYSVO')
    arx = per_region_units(VAC_RAW, vac_sn, 'AREXVY')
    rsv_share = []
    for r in pop:
        a = abr.get(r, 0)
        x = arx.get(r, 0)
        if a + x > 0:
            rsv_share.append((r, 100 * a / (a + x)))
    rsv_share.sort(key=lambda x: x[1])

    ax3 = fig.add_subplot(gs[0, 2])
    names3 = [r.replace('Region ', '').replace('Västra Götalandsregionen', 'VGR') for r, _ in rsv_share]
    vals3 = [v for _, v in rsv_share]
    sthlm_idx3 = next((i for i, n in enumerate(names3) if 'Stockholm' in n), None)
    colors3 = ['#cccccc'] * len(names3)
    if sthlm_idx3 is not None:
        colors3[sthlm_idx3] = PFIZER_BLUE
    ax3.barh(names3, vals3, color=colors3)
    ax3.axvline(50, color='black', linestyle='--', linewidth=0.6, alpha=0.5)
    ax3.set_xlabel('Abrysvo share of RSV class by units (%)', fontsize=9)
    ax3.set_title('3) Vaccines — Abrysvo share in Stockholm', fontsize=10, fontweight='bold', color=PFIZER_NAVY)
    ax3.tick_params(axis='y', labelsize=7.5)
    ax3.grid(axis='x', alpha=0.25)

    # ---- Panel 4: Pfizer oncology absolute footprint Stockholm vs national mean ----
    onc_products = [('IBRANCE', ONC_RAW, 'Ibrance'),
                    ('TUKYSA', ONC_RAW, 'Tukysa L01EH'),
                    ('TALZENNA', ONC_RAW, 'Talzenna'),
                    ('XTANDI', ONC_RAW, 'Talzenna'),
                    ('LORVIQUA', ONC_RAW, 'Lorviqua L01ED'),
                    ('ELREXFIO', ONC_RAW, 'Elrexfio')]
    sthlm_units = []
    nat_mean_units = []
    onc_labels = []
    for prod, fp, sn in onc_products:
        units = per_region_units(fp, sn, prod)
        if 'Region Stockholm' in units and units['Region Stockholm'] > 0:
            onc_labels.append(prod)
            sthlm_units.append(units['Region Stockholm'])
            nat_total = sum(units.values())
            nat_mean_units.append(nat_total / 21)

    ax4 = fig.add_subplot(gs[1, 0])
    x = np.arange(len(onc_labels))
    w = 0.35
    ax4.bar(x - w/2, sthlm_units, w, label='Stockholm', color=PFIZER_BLUE)
    ax4.bar(x + w/2, nat_mean_units, w, label='National per-region mean', color='#cccccc')
    ax4.set_xticks(x)
    ax4.set_xticklabels(onc_labels, rotation=30, ha='right', fontsize=8)
    ax4.set_ylabel('Units (3yr)', fontsize=9)
    ax4.set_title('4) Pfizer oncology footprint — Stockholm vs national mean', fontsize=10, fontweight='bold', color=PFIZER_NAVY)
    ax4.legend(fontsize=8, loc='upper right')
    ax4.grid(axis='y', alpha=0.25)
    ax4.set_yscale('log')

    # ---- Panel 5: Stakeholder cornerstone density (info graphic) ----
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.axis('off')
    ax5.text(0.0, 0.95, '5) Stakeholders — cornerstone density',
             fontsize=10, fontweight='bold', color=PFIZER_NAVY, transform=ax5.transAxes)
    rows = [
        ('Mats Ek',          'LK ordf Region Stockholm'),
        ('Rickard Malmström','NT-rådet + Stockholm LK vice ordf'),
        ('Johan Bratt',      'NSG referensperson, prior CMO Sthlm'),
        ('+ 17 Stockholm LK ledamöter', 'Full LK pool captured 2026-04-27'),
    ]
    for i, (n, role) in enumerate(rows):
        y = 0.78 - i * 0.18
        ax5.text(0.02, y, '●', fontsize=18, color=PFIZER_BLUE, transform=ax5.transAxes)
        ax5.text(0.10, y + 0.02, n, fontsize=10, fontweight='bold', color=PFIZER_NAVY, transform=ax5.transAxes)
        ax5.text(0.10, y - 0.04, role, fontsize=8.5, color='#444', transform=ax5.transAxes)
    ax5.text(0.02, 0.05, '3 of 8 cornerstones (37.5%) from a region with 23.5% of population',
             fontsize=8, style='italic', color='#666', transform=ax5.transAxes)

    # ---- Panel 6: Reading across the dimensions ----
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    ax6.text(0.0, 0.95, 'Reading across the dimensions',
             fontsize=10, fontweight='bold', color=PFIZER_NAVY, transform=ax6.transAxes)
    synthesis = [
        '• CDK4/6: lowest Pfizer share among major regions',
        '• ATTR: large absolute, mid-table per-100k',
        '• Vaccines: Abrysvo minority vs Arexvy here',
        '• Oncology: highest absolute Pfizer footprint',
        '• 3 cornerstones + full LK pool = high engagement leverage',
        '',
        'Stockholm is not the ATTR hot spot (that is Norrland).',
        'Stockholm carries both risk and leverage — across multiple plays.',
    ]
    for i, line in enumerate(synthesis):
        y = 0.84 - i * 0.085
        weight = 'bold' if line.startswith('Stockholm') else 'normal'
        ax6.text(0.02, y, line, fontsize=9, color='#222', transform=ax6.transAxes, fontweight=weight)

    fig.suptitle('F4 — Stockholm strategic profile: five-dimensional view',
                 fontsize=13, fontweight='bold', color=PFIZER_NAVY, x=0.06, y=0.97, ha='left')
    out = FIG_DIR / 'F4_stockholm_strategic_profile.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


def main():
    print('Generating F3 + F4 figures...')
    plot_f3()
    plot_f4()
    print('Done.')


if __name__ == '__main__':
    main()
