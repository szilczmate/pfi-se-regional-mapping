# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Generate figures for the IQVIA Oncology integration (v26).

- O1: CDK4/6 three-way competitive landscape per region (Ibrance + Verzenios + Kisqali)
- O2: Stockholm + VGR + Skåne CDK4/6 substitution trajectory (monthly time series)
- O3: Pfizer oncology portfolio mosaic — Ibrance, Tukysa, Talzenna, Lorviqua, Elrexfio, Xtandi

Style matches deck/report system: navy primary, amber accent, Pfizer blue, clean academic.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v26.xlsx"
RAW = ROOT / "working" / "data" / "raw" / "VitiScience Oncology_Apr-27-2026.xlsx"
OUT = ROOT / "delivery" / "figures"
OUT.mkdir(exist_ok=True)

NAVY = "#1F3A5F"
AMBER = "#D97A1F"
LIGHT_GREY = "#E8E8E8"
DARK_GREY = "#333333"
PFIZER_BLUE = "#0050A0"
LILLY_GREEN = "#5B9D7E"   # Verzenios
NOVARTIS_PURPLE = "#7E5BAA"  # Kisqali

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


def grid_y(ax):
    ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.6)
    ax.set_axisbelow(True)


def short_name(region):
    return (region.replace("Region ", "")
                  .replace("Västra Götalandsregionen", "Västra Götaland")
                  .replace(" län", "")
                  .replace("Jämtland Härjedalen", "Jämtland H."))


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


def load_pops_from_workbook():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws = wb['Region master']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    region_col = headers.index('Region')
    pop_col = headers.index('Population')
    return {row[region_col]: row[pop_col] for row in ws.iter_rows(min_row=2, values_only=True) if row[region_col]}


def load_cdk46_data():
    """Returns region → product → {units, sek, monthly_units (36)}"""
    wb = openpyxl.load_workbook(RAW, read_only=True, data_only=True)
    ws = wb['Ibrance']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    month_labels = [str(headers[i]).replace('Sell-In Value', '').replace('\n', ' ').strip() for i in sek_cols]

    data = defaultdict(lambda: defaultdict(lambda: {
        'units': 0.0, 'sek': 0.0,
        'monthly_units': [0.0] * len(units_cols),
    }))
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2], 'Unknown')
        if region == 'Unknown' or not product:
            continue
        for i, idx in enumerate(units_cols):
            v = row[idx]
            if v is not None:
                data[region][product]['units'] += v
                data[region][product]['monthly_units'][i] += v
        for idx in sek_cols:
            v = row[idx]
            if v is not None:
                data[region][product]['sek'] += v
    return data, month_labels


def load_pfizer_oncology_data():
    """Returns product → region → {units, sek}"""
    wb = openpyxl.load_workbook(RAW, read_only=True, data_only=True)
    PRODUCT_SHEET = {
        'IBRANCE': 'Ibrance', 'TUKYSA': 'Tukysa L01EH', 'TALZENNA': 'Talzenna',
        'LORVIQUA': 'Lorviqua L01ED', 'XALKORI': 'Lorviqua L01ED',
        'ELREXFIO': 'Elrexfio', 'XTANDI': 'Talzenna',
    }
    out = defaultdict(lambda: defaultdict(lambda: {'units': 0.0, 'sek': 0.0}))
    for product, sheet_name in PRODUCT_SHEET.items():
        ws = wb[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != product:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2], 'Unknown')
            if region == 'Unknown':
                continue
            for idx in sek_cols:
                v = row[idx]
                if v is not None:
                    out[product][region]['sek'] += v
            for idx in units_cols:
                v = row[idx]
                if v is not None:
                    out[product][region]['units'] += v
    return out


# =============================================================================
# Figure O1 — CDK4/6 three-way competitive landscape per region
# =============================================================================

def figure_cdk46_three_way(cdk_data, pops):
    region_rows = []
    for region in pops.keys():
        ib = cdk_data[region].get('IBRANCE', {'units': 0})['units']
        vz = cdk_data[region].get('VERZENIOS', {'units': 0})['units']
        ks = cdk_data[region].get('KISQALI', {'units': 0})['units']
        if ib + vz + ks == 0:
            continue
        region_rows.append((region, ib, vz, ks))
    region_rows.sort(key=lambda r: -(r[1] + r[2] + r[3]))

    fig, ax = plt.subplots(figsize=(11.5, 7.0))
    region_labels = [short_name(r[0]) for r in region_rows]
    ib_arr = np.array([r[1] for r in region_rows])
    vz_arr = np.array([r[2] for r in region_rows])
    ks_arr = np.array([r[3] for r in region_rows])
    y_pos = np.arange(len(region_labels))[::-1]

    ax.barh(y_pos, ib_arr, color=PFIZER_BLUE, label="IBRANCE (Pfizer · palbociclib)", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, vz_arr, left=ib_arr, color=LILLY_GREEN, label="VERZENIOS (Lilly · abemaciclib)", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, ks_arr, left=ib_arr + vz_arr, color=NOVARTIS_PURPLE, label="KISQALI (Novartis · ribociclib)", edgecolor="white", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(region_labels, fontsize=9)
    ax.set_xlabel("CDK4/6 inhibitor units dispensed, cumulative Apr 2023 – Mar 2026", fontsize=10, color=DARK_GREY)
    ax.set_title("CDK4/6 — three-way race, Verzenios national leader, Pfizer third", fontsize=14, color=NAVY, loc="left", pad=15)
    fig.text(0.07, 0.93,
             "National split by units: Verzenios 39% · Kisqali 33% · Ibrance 28%. The original P2 frame ('Ibrance vs Kisqali') misses the larger competitor.",
             fontsize=10, color=DARK_GREY, style="italic")

    # Pfizer share annotation per region
    for i, (region, ib, vz, ks) in zip(y_pos, region_rows):
        total = ib + vz + ks
        share = 100 * ib / total if total > 0 else 0
        if share >= 45:
            color = PFIZER_BLUE
            weight = "bold"
        elif share < 15:
            color = "#C73E1D"
            weight = "bold"
        else:
            color = DARK_GREY
            weight = "normal"
        ax.text(total + max(ib_arr.max(), vz_arr.max())/100, i, f"{share:.0f}% Pfizer",
                fontsize=8, color=color, va="center", fontweight=weight)

    ax.legend(loc="lower right", frameon=False, fontsize=9, bbox_to_anchor=(1.0, -0.18), ncol=3)
    grid_x(ax)
    fig.text(0.07, 0.03, "Source: IQVIA Oncology extract 2026-04-27 (ATC L01EF). Units = packs cumulative across 36 months.",
             fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.16, right=0.96, top=0.86, bottom=0.16)

    out_path = OUT / "O1_cdk46_three_way_landscape.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")


# =============================================================================
# Figure O2 — Stockholm + VGR + Skåne substitution trajectory (monthly)
# =============================================================================

def figure_substitution_trajectory(cdk_data, month_labels):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=False, gridspec_kw={"wspace": 0.3})

    target_regions = [
        ("Region Stockholm", "Stockholm"),
        ("Västra Götalandsregionen", "Västra Götaland"),
        ("Region Skåne", "Skåne"),
    ]

    n_months = len(month_labels)
    x = np.arange(n_months)
    # Tick labels: every 6 months
    tick_idx = list(range(0, n_months, 6))
    tick_labels = [month_labels[i].replace(' ', '\n') for i in tick_idx]

    for ax, (region, short) in zip(axes, target_regions):
        ib = cdk_data[region].get('IBRANCE', {'monthly_units': [0]*n_months})['monthly_units']
        vz = cdk_data[region].get('VERZENIOS', {'monthly_units': [0]*n_months})['monthly_units']
        ks = cdk_data[region].get('KISQALI', {'monthly_units': [0]*n_months})['monthly_units']

        # Smooth with 3-month rolling
        def roll(arr, w=3):
            arr = np.array(arr, dtype=float)
            out = np.zeros_like(arr)
            for i in range(len(arr)):
                lo = max(0, i - w//2)
                hi = min(len(arr), i + w//2 + 1)
                out[i] = arr[lo:hi].mean()
            return out

        ax.plot(x, roll(ib), color=PFIZER_BLUE, linewidth=2.5, label="IBRANCE")
        ax.plot(x, roll(vz), color=LILLY_GREEN, linewidth=2.5, label="VERZENIOS")
        ax.plot(x, roll(ks), color=NOVARTIS_PURPLE, linewidth=2.5, label="KISQALI")
        ax.set_xticks(tick_idx)
        ax.set_xticklabels(tick_labels, fontsize=8)
        ax.set_title(short, fontsize=13, color=NAVY, loc="left", fontweight="bold")
        ax.set_xlim(0, n_months - 1)
        # Δ% annotations
        midpoint = n_months // 2
        ib_d = 100 * (sum(ib[midpoint:]) - sum(ib[:midpoint])) / max(sum(ib[:midpoint]), 1)
        vz_d = 100 * (sum(vz[midpoint:]) - sum(vz[:midpoint])) / max(sum(vz[:midpoint]), 1)
        ks_d = 100 * (sum(ks[midpoint:]) - sum(ks[:midpoint])) / max(sum(ks[:midpoint]), 1)

        ax.text(0.02, 0.97,
                f"Ibrance: {ib_d:+.0f}%\nVerzenios: {vz_d:+.0f}%\nKisqali: {ks_d:+.0f}%",
                transform=ax.transAxes, fontsize=9, va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=LIGHT_GREY, linewidth=0.8),
                family="monospace")
        grid_y(ax)

    axes[0].set_ylabel("Monthly units (3-mo rolling)", fontsize=10, color=DARK_GREY)
    axes[-1].legend(loc="center right", bbox_to_anchor=(1.30, 0.5), frameon=False, fontsize=9)

    fig.suptitle("CDK4/6 substitution trajectory — Pfizer's three biggest markets", fontsize=15, color=NAVY, y=0.97, x=0.07, ha="left", fontweight="bold")
    fig.text(0.07, 0.92,
             "In all three Pfizer-leading regions, Verzenios growth dwarfs Kisqali growth (1H vs 2H of 36-month window). The substitution channel is real but not Kisqali alone.",
             fontsize=10, color=DARK_GREY, style="italic")
    fig.text(0.07, 0.02, "Source: IQVIA Oncology 2026-04-27 (ATC L01EF). 3-month rolling mean shown to smooth supply lumpiness.",
             fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.06, right=0.92, top=0.85, bottom=0.12)

    out_path = OUT / "O2_cdk46_substitution_trajectory.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")


# =============================================================================
# Figure O3 — Pfizer oncology portfolio mosaic
# =============================================================================

def figure_pfizer_oncology_mosaic(pf_data, pops):
    products = [
        ('IBRANCE', 'CDK4/6 · breast cancer · core P2', PFIZER_BLUE),
        ('TUKYSA', 'HER2-SM · brain mets · 85% class share', NAVY),
        ('TALZENNA', 'PARP · BRCA-mutated · 5% class share', AMBER),
        ('LORVIQUA', 'ALK · NSCLC · 27% class share', '#5B9BD5'),
        ('ELREXFIO', 'BCMA bispecific · MM · 47% class share', LILLY_GREEN),
        ('XTANDI', 'AR · prostate · 1.42 BSEK · NEW VISIBILITY', '#C73E1D'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 9.5), gridspec_kw={"hspace": 0.6, "wspace": 0.4})
    fig.suptitle("Pfizer oncology portfolio — regional sell-in cumulative Apr 2023 – Mar 2026",
                 fontsize=15, color=NAVY, y=0.97, x=0.07, ha="left", fontweight="bold")

    for ax, (product, subtitle, color) in zip(axes.flat, products):
        d = pf_data[product]
        rows = [(r, d.get(r, {'sek': 0})['sek']) for r in pops.keys()]
        rows.sort(key=lambda x: -x[1])
        rows = [r for r in rows if r[1] > 0]
        if not rows:
            ax.set_visible(False)
            continue
        labels = [short_name(r[0]) for r in rows]
        vals = np.array([r[1] / 1e6 for r in rows])  # to MSEK
        y_pos = np.arange(len(labels))[::-1]

        ax.barh(y_pos, vals, color=color, edgecolor="white", linewidth=0.4)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("MSEK (3 yr cumulative)", fontsize=9, color=DARK_GREY)
        ax.set_title(f"{product}", fontsize=12, color=NAVY, loc="left", fontweight="bold", pad=4)
        ax.annotate(subtitle, xy=(0, 1.02), xycoords="axes fraction", fontsize=9, color=DARK_GREY, style="italic")
        grid_x(ax)
        # Top 3 annotations
        for i, (region, val) in enumerate(rows[:3]):
            ax.text(val/1e6 + (vals.max() / 80), len(rows) - i - 1,
                    f"{val/1e6:.0f}M", fontsize=8, color=color, va="center", fontweight="bold")

    fig.text(0.07, 0.93,
             "Six Pfizer oncology assets: Ibrance contested in three-way CDK4/6 race; Tukysa class-dominant; Talzenna structurally Lynparza-ceiling-bound; Lorviqua 2L ALK; Elrexfio at parity with Tecvayli; Xtandi a major asset previously not in our analysis.",
             fontsize=10, color=DARK_GREY, style="italic")
    fig.text(0.07, 0.02, "Source: IQVIA Oncology 2026-04-27.", fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.06)

    out_path = OUT / "O3_pfizer_oncology_portfolio_mosaic.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    pops = load_pops_from_workbook()
    cdk_data, month_labels = load_cdk46_data()
    pf_data = load_pfizer_oncology_data()
    figure_cdk46_three_way(cdk_data, pops)
    figure_substitution_trajectory(cdk_data, month_labels)
    figure_pfizer_oncology_mosaic(pf_data, pops)
    print("\nAll oncology figures generated.")
