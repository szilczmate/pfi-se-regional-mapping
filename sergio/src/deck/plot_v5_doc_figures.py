# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""F5 + F6 + F7 + F8 — figures for plays brief v5 + exec summary v5.

Triple-check protocol baked in:
  1. Pull raw IQVIA data
  2. Compute the values + PRINT them as a sanity table BEFORE plotting
  3. Generate PNG
  4. (caller verifies by Read-tool inspection)

F5 — CDK4/6 mutual stall (3-panel: Ibrance / Verzenios / Kisqali national trajectory)
F6 — Vyndaqel anchor durability vs ATTR competitor entry (Vyndaqel + AMVUTTRA + BEYONTTRA monthly)
F7 — Precision oncology split (Tukysa national trajectory + Talzenna+Lynparza class trajectory)
F8 — Multi-class verdict tile (compact one-glance view for exec summary)
"""

from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
import openpyxl

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
RAW_DIR = ROOT / "working" / "data" / "raw"
RDIM_RAW = RAW_DIR / "VitiScience RD_IM_Apr-27-2026.xlsx"
ONC_RAW = RAW_DIR / "VitiScience Oncology_Apr-27-2026.xlsx"
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

# Pfizer brand palette
PFIZER_BLUE = '#0093D0'
PFIZER_NAVY = '#1F3A5F'
PFIZER_LIGHT = '#7CC8E5'
GROW_GREEN = '#3A8C50'
PLATEAU_AMBER = '#E0A030'
DECLINE_ORANGE = '#D08060'
DECLINE_RED = '#C04030'
GREY = '#888888'
BACKGROUND_BAND = '#FFF2CC'  # plateau zone shading


def aggregate_product_monthly(file_path, sheet_name, product_name):
    """Returns (national_monthly_units list of length 36, month_labels list)."""
    wb_raw = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb_raw[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    sek_cols = [i for i, h in enumerate(headers) if h and ('Sell-In Value' in str(h) or 'Sell In Value' in str(h))]
    month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip() for i in sek_cols]

    per_region = defaultdict(lambda: [0.0] * len(units_cols))
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
                per_region[region][i] += v
    n = len(units_cols)
    nat = [sum(per_region[r][i] for r in per_region.keys()) for i in range(n)]
    return nat, month_labels


def slope_pct(monthly):
    n = len(monthly)
    last_6 = sum(monthly[n - 6:])
    prev_6 = sum(monthly[n - 12:n - 6])
    if prev_6 <= 0:
        return None, last_6, prev_6
    return 100 * (last_6 - prev_6) / prev_6, last_6, prev_6


def verdict_tier(pct):
    if pct is None:
        return 'just-launched', GREY
    if pct > 30:
        return 'COMPOUNDING', GROW_GREEN
    if pct > 5:
        return 'GROWING', GROW_GREEN
    if pct >= -5:
        return 'PLATEAUING', PLATEAU_AMBER
    if pct >= -20:
        return 'DECLINING', DECLINE_ORANGE
    return 'CONTRACTING', DECLINE_RED


# ============================================================================
# Sanity printer
# ============================================================================

def print_sanity(label, monthly, month_labels):
    pct, l6, p6 = slope_pct(monthly)
    v, _ = verdict_tier(pct)
    total = sum(monthly)
    print(f'  {label:24s}: 36mo total={total:9,.0f}  prev6={p6:8,.0f}  last6={l6:8,.0f}  '
          f'Δ={pct if pct is not None else "n/a":>7}{"%" if pct is not None else " "} → {v}')


# ============================================================================
# F5 — CDK4/6 mutual stall (3-panel)
# ============================================================================

def plot_f5():
    print('\n=== F5 sanity check (CDK4/6 trajectory data) ===')
    products = [('IBRANCE', 'Ibrance — Pfizer'),
                ('VERZENIOS', 'Verzenios — Lilly'),
                ('KISQALI', 'Kisqali — Novartis')]
    series = {}
    for prod, label in products:
        nat, month_labels = aggregate_product_monthly(ONC_RAW, 'Ibrance', prod)
        series[prod] = (nat, month_labels)
        print_sanity(label, nat, month_labels)

    # Build figure: 3 panels horizontal, sharing x-axis
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=False)
    plt.subplots_adjust(top=0.80, bottom=0.18, left=0.06, right=0.98, wspace=0.22)

    for ax, (prod, label) in zip(axes, products):
        nat, month_labels = series[prod]
        n = len(nat)
        x = np.arange(n)

        # Background bands: highlight last-6 and prev-6 windows
        ax.axvspan(n - 12 - 0.5, n - 6 - 0.5, color='#EAEAEA', alpha=0.6, zorder=0, label='_nolegend_')
        ax.axvspan(n - 6 - 0.5, n - 1 + 0.5, color='#FFE9C7', alpha=0.7, zorder=0, label='_nolegend_')

        # Bars: monthly units
        if prod == 'IBRANCE':
            color = PFIZER_BLUE
        elif prod == 'VERZENIOS':
            color = '#A04CB6'
        else:
            color = '#E07030'
        ax.bar(x, nat, color=color, edgecolor='black', linewidth=0.3, width=0.85, zorder=2)

        pct, l6, p6 = slope_pct(nat)
        verdict, vcolor = verdict_tier(pct)

        # Verdict box at top of panel
        ax.text(0.98, 0.95, verdict,
                transform=ax.transAxes, ha='right', va='top',
                fontsize=11, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.4', facecolor=vcolor, edgecolor='none'))
        ax.text(0.98, 0.83, f'{pct:+.1f}% last-6 vs prev-6',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=9.5, color=PFIZER_NAVY, style='italic')

        ax.set_title(label, fontsize=11, fontweight='bold', color=PFIZER_NAVY, loc='left')
        ax.set_xticks([0, 5, 11, 17, 23, 29, 35])
        ax.set_xticklabels(['Apr\'23', 'Sep\'23', 'Mar\'24', 'Sep\'24', 'Mar\'25', 'Sep\'25', 'Mar\'26'],
                           fontsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.set_ylabel('IQVIA units / month', fontsize=9)
        ax.grid(axis='y', alpha=0.25, zorder=1)
        ax.set_ylim(bottom=0)

    fig.suptitle('F5 — CDK4/6 class: Ibrance + Verzenios both plateaued; Kisqali (Novartis) is the live gainer',
                 fontsize=13, fontweight='bold', color=PFIZER_NAVY, x=0.06, ha='left', y=0.96)
    fig.text(0.06, 0.04,
             'Grey band = prev-6 window (Apr–Sep 2025). Amber band = last-6 window (Oct 2025–Mar 2026). Bars are national '
             'monthly IQVIA units. Pfizer Ibrance (−3.0%) and Lilly Verzenios (−0.1%) are flat — but Novartis Kisqali (+15.7%) is GROWING. '
             'P2 strategic implication: the live competitive threat is Kisqali, not compounding Verzenios.  Source: IQVIA Oncology 2026-04-27.',
             fontsize=8.5, color='#444', ha='left', style='italic')

    out = FIG_DIR / 'F5_cdk46_mutual_stall.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


# ============================================================================
# F6 — Vyndaqel anchor durability vs ATTR competitor entry
# ============================================================================

def plot_f6():
    print('\n=== F6 sanity check (ATTR class trajectory data) ===')
    products = [('VYNDAQEL', 'Vyndaqel — Pfizer (anchor)', PFIZER_BLUE),
                ('AMVUTTRA', 'AMVUTTRA — Alnylam (siRNA)', '#A04CB6'),
                ('BEYONTTRA', 'BEYONTTRA — BridgeBio (stabiliser)', '#E07030')]
    series = {}
    for prod, label, _ in products:
        nat, month_labels = aggregate_product_monthly(RDIM_RAW, 'ATTR', prod)
        series[prod] = (nat, month_labels)
        print_sanity(label, nat, month_labels)

    # Two-panel layout: top = Vyndaqel (full window); bottom = competitor entry (last 18 months only,
    # zoomed in to where the action is — eliminates dead space).
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(13, 6.0),
                                          gridspec_kw={'height_ratios': [2.0, 1.1]})
    plt.subplots_adjust(top=0.88, bottom=0.13, left=0.07, right=0.985, hspace=0.22)

    n = len(series['VYNDAQEL'][0])
    x = np.arange(n)

    # ----- Top panel: Vyndaqel monthly bars (full 36 months) -----
    ax_top.axvspan(n - 12 - 0.5, n - 6 - 0.5, color='#EAEAEA', alpha=0.55, zorder=0)
    ax_top.axvspan(n - 6 - 0.5, n - 1 + 0.5, color='#FFE9C7', alpha=0.65, zorder=0)

    vynd, _ = series['VYNDAQEL']
    ax_top.bar(x, vynd, color=PFIZER_BLUE, edgecolor='black', linewidth=0.3, width=0.85,
               label='Vyndaqel (Pfizer)', zorder=2)

    pct_v, l6_v, p6_v = slope_pct(vynd)
    verdict_v, vcolor_v = verdict_tier(pct_v)
    ax_top.text(0.985, 0.95, f'Vyndaqel: {pct_v:+.1f}%  →  {verdict_v}',
                transform=ax_top.transAxes, ha='right', va='top',
                fontsize=13, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=vcolor_v, edgecolor='none'))

    # Window labels on top panel
    ax_top.text(n - 9, 8, 'prev-6 window', fontsize=9, color='#555', ha='center', va='bottom')
    ax_top.text(n - 3, 8, 'last-6 window', fontsize=9, color='#555', ha='center', va='bottom')

    ax_top.set_xlim(-0.5, n - 0.5)  # Tighter x-limits, no whitespace
    ax_top.set_ylabel('Vyndaqel monthly\nIQVIA units (national)', fontsize=10, color=PFIZER_NAVY)
    ax_top.tick_params(axis='y', labelsize=9)
    ax_top.tick_params(axis='x', labelbottom=False)
    ax_top.grid(axis='y', alpha=0.3, zorder=1)
    ax_top.set_title('F6 — Vyndaqel anchor: holding through ATTR competitor entry',
                     fontsize=14, fontweight='bold', color=PFIZER_NAVY, loc='left', pad=10)
    ax_top.legend(loc='upper left', fontsize=10, framealpha=0.95)

    # ----- Bottom panel: AMVUTTRA + BEYONTTRA monthly (zoom on last 18 months only) -----
    # Find the zoom range: from month 18 (Oct 2024) to month 35 (Mar 2026)
    zoom_start = 18
    x_zoom = np.arange(zoom_start, n)

    amv, _ = series['AMVUTTRA']
    bey, _ = series['BEYONTTRA']
    amv_zoom = amv[zoom_start:]
    bey_zoom = bey[zoom_start:]
    vynd_zoom = vynd[zoom_start:]

    # Background bands aligned to the zoomed view
    ax_bot.axvspan(n - 12 - 0.5, n - 6 - 0.5, color='#EAEAEA', alpha=0.55, zorder=0)
    ax_bot.axvspan(n - 6 - 0.5, n - 1 + 0.5, color='#FFE9C7', alpha=0.65, zorder=0)

    # Plot competitors as bars (more visible than lines for small values)
    bar_width = 0.38
    ax_bot.bar(x_zoom - bar_width / 2, amv_zoom, width=bar_width, color='#A04CB6',
               label='AMVUTTRA (Alnylam — siRNA)', zorder=3)
    ax_bot.bar(x_zoom + bar_width / 2, bey_zoom, width=bar_width, color='#E07030',
               label='BEYONTTRA (BridgeBio — stabiliser)', zorder=3)

    pct_a, l6_a, _ = slope_pct(amv)
    pct_b, l6_b, _ = slope_pct(bey)

    # Annotate AMVUTTRA + BEYONTTRA first-unit months
    first_amv = next((i for i, v in enumerate(amv) if v > 0), None)
    first_bey = next((i for i, v in enumerate(bey) if v > 0), None)
    y_max = max(max(amv_zoom), max(bey_zoom)) * 1.25
    ax_bot.set_ylim(0, y_max)

    # First-units annotations placed near data points
    if first_amv is not None and first_amv >= zoom_start:
        ax_bot.annotate('AMVUTTRA\nfirst units',
                        xy=(first_amv - bar_width / 2, amv[first_amv]),
                        xytext=(first_amv - 4, y_max * 0.75),
                        fontsize=9, color='#A04CB6', fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color='#A04CB6', lw=1.2))
    if first_bey is not None and first_bey >= zoom_start:
        ax_bot.annotate('BEYONTTRA\nfirst units',
                        xy=(first_bey + bar_width / 2, bey[first_bey]),
                        xytext=(first_bey - 1, y_max * 0.45),
                        fontsize=9, color='#E07030', fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color='#E07030', lw=1.2))

    # Info text — placed lower-left where there's empty space
    last6_vyn = l6_v
    last6_amv = l6_a
    last6_bey = l6_b
    info_text = (f'Last-6 absolute units:\n'
                 f'  Vyndaqel: {last6_vyn:,.0f}\n'
                 f'  AMVUTTRA: {last6_amv:,.0f}\n'
                 f'  BEYONTTRA: {last6_bey:,.0f}\n'
                 f'Combined competitor: {(last6_amv + last6_bey) / last6_vyn * 100:.1f}% of Vyndaqel')
    ax_bot.text(0.01, 0.97, info_text,
                transform=ax_bot.transAxes, ha='left', va='top',
                fontsize=9, color=PFIZER_NAVY,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor='#ccc', alpha=0.95))

    # X-axis: show the zoomed range with proper labels
    ax_bot.set_xlim(zoom_start - 0.5, n - 0.5)
    tick_positions = [18, 23, 29, 35]  # Oct'24, Mar'25, Sep'25, Mar'26
    tick_labels = ['Oct\'24', 'Mar\'25', 'Sep\'25', 'Mar\'26']
    ax_bot.set_xticks(tick_positions)
    ax_bot.set_xticklabels(tick_labels, fontsize=10)
    ax_bot.set_ylabel('Competitor monthly\nunits (zoomed)', fontsize=10, color='#666')
    ax_bot.tick_params(axis='y', labelsize=9, colors='#666')
    ax_bot.grid(axis='y', alpha=0.3, zorder=1)
    ax_bot.legend(loc='upper right', fontsize=9, framealpha=0.95)

    # Top panel x-tick labels — show on top panel since bottom panel is now zoomed
    ax_top.set_xticks([0, 5, 11, 17, 23, 29, 35])
    ax_top.set_xticklabels(['Apr\'23', 'Sep\'23', 'Mar\'24', 'Sep\'24', 'Mar\'25', 'Sep\'25', 'Mar\'26'],
                           fontsize=9)
    ax_top.tick_params(axis='x', labelbottom=True, labelsize=9)

    fig.text(0.07, 0.03,
             'Top: full 36-month window of Vyndaqel monthly bars. Bottom: zoomed view of AMVUTTRA + BEYONTTRA monthly post-launch '
             'entry. Despite two new same-class competitors entering Sweden 2025, Vyndaqel grew 3.4% last-6 vs prev-6.  '
             'Source: IQVIA RD/IM 2026-04-27.',
             fontsize=9, color='#444', ha='left', style='italic')

    out = FIG_DIR / 'F6_vyndaqel_anchor_durability.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


# ============================================================================
# F7 — Precision oncology split (Tukysa vs Talzenna)
# ============================================================================

def plot_f7():
    print('\n=== F7 sanity check (precision oncology trajectory data) ===')
    # Tukysa national + class context
    tukysa_nat, _ = aggregate_product_monthly(ONC_RAW, 'Tukysa L01EH', 'TUKYSA')
    print_sanity('Tukysa (Pfizer)', tukysa_nat, None)
    # Talzenna + Lynparza class
    talz_nat, _ = aggregate_product_monthly(ONC_RAW, 'Talzenna', 'TALZENNA')
    lynp_nat, _ = aggregate_product_monthly(ONC_RAW, 'Talzenna', 'LYNPARZA')
    print_sanity('Talzenna (Pfizer)', talz_nat, None)
    print_sanity('Lynparza (AZ — class anchor)', lynp_nat, None)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    plt.subplots_adjust(top=0.82, bottom=0.20, left=0.06, right=0.97, wspace=0.22)

    n = len(tukysa_nat)
    x = np.arange(n)

    # ---- Panel 1: Tukysa national trajectory ----
    ax1 = axes[0]
    ax1.axvspan(n - 12 - 0.5, n - 6 - 0.5, color='#EAEAEA', alpha=0.5, zorder=0)
    ax1.axvspan(n - 6 - 0.5, n - 1 + 0.5, color='#FFE9C7', alpha=0.6, zorder=0)
    ax1.bar(x, tukysa_nat, color=PFIZER_BLUE, edgecolor='black', linewidth=0.3, width=0.85, zorder=2)
    pct_t, l6_t, p6_t = slope_pct(tukysa_nat)
    verdict_t, vcolor_t = verdict_tier(pct_t)
    ax1.text(0.04, 0.95, f'Tukysa\n{pct_t:+.1f}%\n{verdict_t}',
             transform=ax1.transAxes, ha='left', va='top',
             fontsize=11, fontweight='bold', color='white',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=vcolor_t, edgecolor='none'))
    ax1.text(0.98, 0.95,
             f'Prev-6: {p6_t:,.0f} units\nLast-6: {l6_t:,.0f} units',
             transform=ax1.transAxes, ha='right', va='top',
             fontsize=9, color=PFIZER_NAVY, style='italic')
    ax1.set_title('Tukysa (HER2-SM brain mets) — P4 winner',
                  fontsize=11, fontweight='bold', color=PFIZER_NAVY, loc='left')
    ax1.set_xticks([0, 11, 23, 35])
    ax1.set_xticklabels(['Apr\'23', 'Mar\'24', 'Mar\'25', 'Mar\'26'], fontsize=9)
    ax1.set_ylabel('IQVIA units / month (national)', fontsize=10)
    ax1.grid(axis='y', alpha=0.3, zorder=1)
    ax1.set_ylim(bottom=0)

    # ---- Panel 2: Talzenna + Lynparza overlay ----
    ax2 = axes[1]
    ax2.axvspan(n - 12 - 0.5, n - 6 - 0.5, color='#EAEAEA', alpha=0.5, zorder=0)
    ax2.axvspan(n - 6 - 0.5, n - 1 + 0.5, color='#FFE9C7', alpha=0.6, zorder=0)

    # Use a SECONDARY y-axis so Lynparza (much larger) doesn't crush Talzenna
    ax2.bar(x, talz_nat, color=PFIZER_BLUE, edgecolor='black', linewidth=0.3, width=0.85,
            label='Talzenna (Pfizer)', zorder=2)
    ax2_r = ax2.twinx()
    ax2_r.plot(x, lynp_nat, color='#888888', linewidth=2.2, marker='.', markersize=4,
               label='Lynparza (AZ — class anchor)', zorder=3)
    ax2_r.set_ylabel('Lynparza monthly units (right axis)', fontsize=9, color='#666')
    ax2_r.tick_params(axis='y', labelsize=8, colors='#666')
    ax2_r.set_ylim(bottom=0)

    pct_tlz, l6_tlz, p6_tlz = slope_pct(talz_nat)
    verdict_tlz, vcolor_tlz = verdict_tier(pct_tlz)
    pct_lyn, l6_lyn, p6_lyn = slope_pct(lynp_nat)
    verdict_lyn, vcolor_lyn = verdict_tier(pct_lyn)

    ax2.text(0.04, 0.95, f'Talzenna\n{pct_tlz:+.1f}%\n{verdict_tlz}',
             transform=ax2.transAxes, ha='left', va='top',
             fontsize=11, fontweight='bold', color='white',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=vcolor_tlz, edgecolor='none'))
    ax2.text(0.04, 0.70, f'Lynparza\n{pct_lyn:+.1f}%\n{verdict_lyn}',
             transform=ax2.transAxes, ha='left', va='top',
             fontsize=10, fontweight='bold', color='white',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=vcolor_lyn, edgecolor='none'))
    ax2.text(0.98, 0.95,
             'PARP class is contracting\n(both products declining)',
             transform=ax2.transAxes, ha='right', va='top',
             fontsize=9.5, color=PFIZER_NAVY, style='italic', fontweight='bold')

    ax2.set_title('Talzenna + Lynparza (PARP class) — both declining',
                  fontsize=11, fontweight='bold', color=PFIZER_NAVY, loc='left')
    ax2.set_xticks([0, 11, 23, 35])
    ax2.set_xticklabels(['Apr\'23', 'Mar\'24', 'Mar\'25', 'Mar\'26'], fontsize=9)
    ax2.set_ylabel('Talzenna monthly units (left axis)', fontsize=10, color=PFIZER_NAVY)
    ax2.tick_params(axis='y', labelsize=8, colors=PFIZER_NAVY)
    ax2.grid(axis='y', alpha=0.3, zorder=1)
    ax2.set_ylim(bottom=0)

    fig.suptitle('F7 — Precision oncology split: Tukysa is the P4 winner; Talzenna sits in a contracting class',
                 fontsize=13, fontweight='bold', color=PFIZER_NAVY, x=0.06, ha='left', y=0.96)
    fig.text(0.06, 0.04,
             'Left: Tukysa national monthly units, +29.9% last-6 vs prev-6 (near compounding boundary). Right: Talzenna (Pfizer, '
             'left bars) and Lynparza (AZ class anchor, grey line on right axis). Both PARP products declining. P4 plays brief should '
             'weight Tukysa as the lead, Talzenna as a holding/secondary bet.  Source: IQVIA Oncology 2026-04-27.',
             fontsize=8.5, color='#444', ha='left', style='italic')

    out = FIG_DIR / 'F7_precision_oncology_split.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


# ============================================================================
# F8 — Multi-class verdict tile (compact one-glance for exec summary)
# ============================================================================

def plot_f8():
    print('\n=== F8 sanity check (multi-class verdict view) ===')
    targets = [
        # (label, file, sheet, product, role)
        ('Verzenios (Lilly)',     ONC_RAW,  'Ibrance',         'VERZENIOS', 'CDK4/6 — competitor'),
        ('Kisqali (Novartis)',    ONC_RAW,  'Ibrance',         'KISQALI',   'CDK4/6 — competitor'),
        ('Ibrance (Pfizer)',      ONC_RAW,  'Ibrance',         'IBRANCE',   'CDK4/6 — Pfizer'),
        ('Tecvayli (Janssen)',    ONC_RAW,  'Elrexfio',        'TECVAYLI',  'BCMA — competitor'),
        ('Elrexfio (Pfizer)',     ONC_RAW,  'Elrexfio',        'ELREXFIO',  'BCMA — Pfizer'),
        ('Alecensa (Roche)',      ONC_RAW,  'Lorviqua L01ED',  'ALECENSA',  'ALK NSCLC — competitor'),
        ('Lynparza (AZ)',         ONC_RAW,  'Talzenna',        'LYNPARZA',  'PARP — competitor'),
        ('Talzenna (Pfizer)',     ONC_RAW,  'Talzenna',        'TALZENNA',  'PARP — Pfizer'),
        ('Tukysa (Pfizer)',       ONC_RAW,  'Tukysa L01EH',    'TUKYSA',    'HER2-SM — Pfizer'),
        ('Vyndaqel (Pfizer)',     RDIM_RAW, 'ATTR',            'VYNDAQEL',  'ATTR — Pfizer anchor'),
        ('AMVUTTRA (Alnylam)',    RDIM_RAW, 'ATTR',            'AMVUTTRA',  'ATTR — competitor (siRNA)'),
        ('BEYONTTRA (BridgeBio)', RDIM_RAW, 'ATTR',            'BEYONTTRA', 'ATTR — competitor (stabiliser)'),
    ]
    rows = []
    for label, fpath, sheet, prod, role in targets:
        nat, _ = aggregate_product_monthly(fpath, sheet, prod)
        pct, l6, p6 = slope_pct(nat)
        verdict, vcolor = verdict_tier(pct)
        rows.append({'label': label, 'role': role, 'pct': pct, 'l6': l6, 'p6': p6,
                     'verdict': verdict, 'vcolor': vcolor})
        print_sanity(label, nat, None)

    # Sort: COMPOUNDING / GROWING first, PLATEAUING middle, DECLINING / CONTRACTING last
    verdict_order = {'COMPOUNDING': 0, 'GROWING': 1, 'PLATEAUING': 2,
                     'DECLINING': 3, 'CONTRACTING': 4, 'just-launched': 5}
    rows.sort(key=lambda r: (verdict_order[r['verdict']], -(r['pct'] or 0)))

    # Larger figure for breathing room. 12 rows + header + legend.
    fig, ax = plt.subplots(figsize=(13, 8.2))
    plt.subplots_adjust(top=0.86, bottom=0.10, left=0.03, right=0.97)

    n_rows = len(rows)
    box_h = 0.92  # taller rows for readability
    for i, r in enumerate(rows):
        y = n_rows - 1 - i
        # Background tile (slightly higher alpha for crisp colours)
        ax.add_patch(Rectangle((0, y - box_h / 2), 10, box_h,
                               facecolor=r['vcolor'], alpha=0.92, edgecolor='white', linewidth=2.5))
        # Pfizer marker (small navy bar at left if Pfizer)
        is_pfizer = '(Pfizer)' in r['label']
        if is_pfizer:
            ax.add_patch(Rectangle((0.05, y - 0.36), 0.22, 0.72,
                                   facecolor=PFIZER_NAVY, edgecolor='white', linewidth=1.5))
        # Drug name (larger, bolder)
        ax.text(0.42, y, r['label'], ha='left', va='center',
                fontsize=13, fontweight='bold', color='white')
        # Class / role tag
        ax.text(4.6, y, r['role'], ha='left', va='center',
                fontsize=11, color='white', style='italic')
        # Slope % (right-aligned, bold, BIG)
        if r['pct'] is None:
            pct_str = 'just-launched'
        elif abs(r['pct']) > 200:
            pct_str = f'{r["pct"]:+.0f}%'
        else:
            pct_str = f'{r["pct"]:+.1f}%'
        ax.text(7.95, y, pct_str, ha='right', va='center',
                fontsize=14, fontweight='bold', color='white')
        # Verdict label (right side, bold)
        ax.text(8.25, y, r['verdict'], ha='left', va='center',
                fontsize=11, fontweight='bold', color='white')

    ax.set_xlim(0, 10)
    ax.set_ylim(-0.7, n_rows - 0.3)
    ax.axis('off')

    # Header row (column labels)
    ax.text(0.42, n_rows - 0.05, 'Product (company)', ha='left', va='bottom',
            fontsize=11, fontweight='bold', color=PFIZER_NAVY)
    ax.text(4.6, n_rows - 0.05, 'Class / role', ha='left', va='bottom',
            fontsize=11, fontweight='bold', color=PFIZER_NAVY)
    ax.text(7.95, n_rows - 0.05, 'Δ %  (last-6 vs prev-6)', ha='right', va='bottom',
            fontsize=11, fontweight='bold', color=PFIZER_NAVY)

    # Title (clean, single line, no jargon)
    fig.suptitle('F8 — Twelve products, last-6 vs prev-6 month IQVIA units',
                 fontsize=15, fontweight='bold', color=PFIZER_NAVY, x=0.03, ha='left', y=0.97)
    fig.text(0.03, 0.93,
             'Most competitors are flat or declining. Kisqali (Novartis) is the live CDK4/6 share-gainer at +15.7%. '
             'Vyndaqel holds +3.4%; Tukysa breakout +29.9%; Ibrance plateaued −3.0%.',
             fontsize=10.5, color=PFIZER_NAVY, ha='left', style='italic')

    # Legend — cleaner, fewer items, single row at bottom
    legend_handles = [
        mpatches.Patch(color=GROW_GREEN, label='GROWING / COMPOUNDING'),
        mpatches.Patch(color=PLATEAU_AMBER, label='PLATEAUING'),
        mpatches.Patch(color=DECLINE_ORANGE, label='DECLINING'),
        mpatches.Patch(color=GREY, label='Just-launched'),
        mpatches.Patch(color=PFIZER_NAVY, label='Pfizer (navy tab)'),
    ]
    ax.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.07),
              ncol=5, fontsize=10, frameon=False)

    fig.text(0.03, 0.025,
             'Source: IQVIA RD/IM 2026-04-27 + Oncology 2026-04-27.',
             fontsize=9, color='#666', ha='left', style='italic')

    out = FIG_DIR / 'F8_multiclass_verdict_view.png'
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out.name}')


def main():
    plot_f5()
    plot_f6()
    plot_f7()
    plot_f8()
    print('\nAll figures saved.')


if __name__ == '__main__':
    main()
