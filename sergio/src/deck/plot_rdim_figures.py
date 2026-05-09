# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Generate figures for the IQVIA RD/IM integration.

- F1: ATTR competitive landscape per region (Vyndaqel + AMVUTTRA + BEYONTTRA stacked)
- F2: Norrland founder cluster — Vyndaqel units per 100k regional
- F3: Pfizer RD/IM portfolio mosaic — Vyndaqel + Vydura + Paxlovid + BeneFIX

Style matches deck/report system: navy primary, amber accent, Pfizer blue, clean academic.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v24.xlsx"
RAW = ROOT / "working" / "data" / "raw" / "VitiScience RD_IM_Apr-27-2026.xlsx"
OUT = ROOT / "delivery" / "figures"
OUT.mkdir(exist_ok=True)

NAVY = "#1F3A5F"
AMBER = "#D97A1F"
LIGHT_GREY = "#E8E8E8"
DARK_GREY = "#333333"
PFIZER_BLUE = "#0050A0"
COMPETITOR_TEAL = "#5B9BD5"
COMPETITOR_GREY = "#B0B0B0"
NORRLAND_HIGHLIGHT = "#C73E1D"  # warm red for Norrland

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
NORRLAND = {'Region Norrbotten', 'Region Västerbotten'}


def load_attr_data():
    """Returns dict region → {VYNDAQEL: units, AMVUTTRA: units, BEYONTTRA: units}"""
    wb = openpyxl.load_workbook(RAW, read_only=True, data_only=True)
    ws = wb['ATTR']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    units_cols = [i for i, h in enumerate(headers) if h and str(h).startswith('Units')]
    sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
    data = defaultdict(lambda: defaultdict(lambda: {'units': 0.0, 'sek': 0.0}))
    for row in ws.iter_rows(min_row=2, values_only=True):
        product = row[1]
        county = str(row[7] or '')
        region = COUNTY_TO_REGION.get(county[:2], 'Unknown')
        if region == 'Unknown':
            continue
        u = sum(v for i, v in enumerate(row) if i in units_cols and v is not None)
        s = sum(v for i, v in enumerate(row) if i in sek_cols and v is not None)
        data[region][product]['units'] += u
        data[region][product]['sek'] += s
    return data


def figure_attr_competitive(attr_data):
    """Per-region ATTR market share — Vyndaqel/AMVUTTRA/BEYONTTRA."""
    region_rows = []
    for region in POP.keys():
        v_u = attr_data[region]['VYNDAQEL']['units']
        a_u = attr_data[region]['AMVUTTRA']['units']
        b_u = attr_data[region]['BEYONTTRA']['units']
        if v_u + a_u + b_u == 0:
            continue
        region_rows.append((region, v_u, a_u, b_u))
    region_rows.sort(key=lambda r: -(r[1] + r[2] + r[3]))

    fig, ax = plt.subplots(figsize=(11, 6.8))
    region_labels = [short_name(r[0]) for r in region_rows]
    v = np.array([r[1] for r in region_rows])
    a = np.array([r[2] for r in region_rows])
    b = np.array([r[3] for r in region_rows])
    y_pos = np.arange(len(region_labels))[::-1]

    ax.barh(y_pos, v, color=PFIZER_BLUE, label="VYNDAQEL (Pfizer · tafamidis)", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, a, left=v, color=COMPETITOR_TEAL, label="AMVUTTRA (Alnylam · vutrisiran siRNA)", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, b, left=v + a, color=AMBER, label="BEYONTTRA (Bridge Bio · acoramidis stabiliser)", edgecolor="white", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(region_labels, fontsize=9)
    ax.set_xlabel("ATTR units dispensed, cumulative Apr 2023 – Mar 2026", fontsize=10, color=DARK_GREY)
    ax.set_title("ATTR competitive entry — Vyndaqel still dominant, two new mechanisms launching", fontsize=14, color=NAVY, loc="left", pad=15)
    fig.text(0.07, 0.93,
             "AMVUTTRA (siRNA) and BEYONTTRA (TTR-stabiliser, same mechanism as tafamidis) are the strategic threat. "
             "Pfizer national share ~94% by SEK; Örebro is a 20% Pfizer-share outlier worth a follow-up.",
             fontsize=10, color=DARK_GREY, style="italic")

    # Pfizer share annotations
    for i, (region, vu, au, bu) in zip(y_pos, region_rows):
        total = vu + au + bu
        share = 100 * vu / total if total > 0 else 0
        ax.text(total + max(v.max()/100, 5), i, f"{share:.0f}% Pfizer", fontsize=8,
                color=PFIZER_BLUE if share >= 80 else AMBER, va="center", fontweight="bold")

    ax.legend(loc="lower right", frameon=False, fontsize=9, bbox_to_anchor=(1.0, -0.20), ncol=3)
    grid_x(ax)
    fig.text(0.07, 0.03, "Source: IQVIA RD/IM extract 2026-04-27 (ATC C01EB16 + C01EB25). Units = capsules/tablets dispensed cumulative across 36 months.",
             fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.16, right=0.96, top=0.86, bottom=0.16)

    out_path = OUT / "C1_attr_competitive_landscape.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def figure_norrland_cluster(attr_data):
    """Vyndaqel units per 100k by region, Norrland highlighted."""
    rows = []
    for region in POP.keys():
        units = attr_data[region]['VYNDAQEL']['units']
        per_100k = units / POP[region] * 100000
        rows.append((region, per_100k, units))
    rows.sort(key=lambda r: -r[1])

    fig, ax = plt.subplots(figsize=(10, 7.0))
    labels = [short_name(r[0]) for r in rows]
    vals = np.array([r[1] for r in rows])
    colors = [NORRLAND_HIGHLIGHT if r[0] in NORRLAND else PFIZER_BLUE for r in rows]
    y_pos = np.arange(len(labels))[::-1]

    ax.barh(y_pos, vals, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Vyndaqel units per 100,000 population (Apr 2023 – Mar 2026 cumulative)", fontsize=10, color=DARK_GREY)
    ax.set_title("The Skellefteå founder cluster, made empirical", fontsize=14, color=NAVY, loc="left", pad=15)

    # National mean line
    national_mean = sum(r[1] * POP[r[0]] for r in rows) / sum(POP[r[0]] for r in rows)
    ax.axvline(national_mean, linestyle="--", color=DARK_GREY, linewidth=1, alpha=0.6)
    ax.text(national_mean + 15, 0.5, f"National mean\n{national_mean:.0f}/100k",
            fontsize=9, color=DARK_GREY, va="center", style="italic")

    # Annotations
    for i, (region, val, units) in zip(y_pos, rows):
        if region in NORRLAND:
            multiple = val / national_mean
            ax.text(val + 20, i, f"{val:.0f}  ·  {multiple:.1f}× national",
                    fontsize=9, color=NORRLAND_HIGHLIGHT, va="center", fontweight="bold")
        else:
            ax.text(val + 15, i, f"{val:.0f}", fontsize=8, color=PFIZER_BLUE, va="center")

    fig.text(0.10, 0.93,
             "Norrbotten + Västerbotten = 5.0% of Sweden's population, 29.7% of national Vyndaqel units. "
             "TTR V30M founder variant (Skellefteå cluster). Was Modeled — now Observed via IQVIA.",
             fontsize=10, color=DARK_GREY, style="italic")
    grid_x(ax)
    fig.text(0.10, 0.03, "Source: IQVIA RD/IM extract 2026-04-27 (ATC C01EB16 tafamidis). Pop denominator: SCB regional populations.",
             fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.18, right=0.97, top=0.88, bottom=0.10)

    out_path = OUT / "C2_norrland_founder_cluster.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def figure_pfizer_rdim_mosaic():
    """4-panel mosaic: Vyndaqel, Vydura, Paxlovid, BeneFIX regional SEK."""
    wb = openpyxl.load_workbook(RAW, read_only=True, data_only=True)
    PRODUCT_TA = {'VYNDAQEL': 'ATTR', 'VYDURA': 'Migraine', 'PAXLOVID': 'Covid', 'BENEFIX': 'Haemophilia'}

    def per_region(product, sheet_name):
        ws = wb[sheet_name]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        sek_cols = [i for i, h in enumerate(headers) if h and 'Sell-In Value' in str(h)]
        d = defaultdict(float)
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != product:
                continue
            county = str(row[7] or '')
            region = COUNTY_TO_REGION.get(county[:2], 'Unknown')
            if region == 'Unknown':
                continue
            sek = sum(v for i, v in enumerate(row) if i in sek_cols and v is not None)
            d[region] += sek
        return d

    products = [
        ('VYNDAQEL', 'ATTR-CM · tafamidis · core P1', PFIZER_BLUE),
        ('VYDURA', 'Migraine · rimegepant · sleeper', AMBER),
        ('PAXLOVID', 'COVID antiviral · per-protocol', COMPETITOR_TEAL),
        ('BENEFIX', 'Haemophilia FIX · niche legacy', NAVY),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), gridspec_kw={"hspace": 0.55, "wspace": 0.4})
    fig.suptitle("Pfizer RD/IM portfolio — regional sell-in cumulative Apr 2023 – Mar 2026",
                 fontsize=15, color=NAVY, y=0.97, x=0.07, ha="left", fontweight="bold")

    for ax, (product, subtitle, color) in zip(axes.flat, products):
        d = per_region(product, PRODUCT_TA[product])
        rows = [(r, d.get(r, 0)) for r in POP.keys()]
        rows.sort(key=lambda x: -x[1])
        rows = [r for r in rows if r[1] > 0]  # keep only regions with sales

        labels = [short_name(r[0]) for r in rows]
        vals = np.array([r[1] / 1e6 for r in rows])  # to MSEK
        y_pos = np.arange(len(labels))[::-1]

        ax.barh(y_pos, vals, color=color, edgecolor="white", linewidth=0.4)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("MSEK (3 years)", fontsize=9, color=DARK_GREY)
        ax.set_title(f"{product}", fontsize=12, color=NAVY, loc="left", fontweight="bold", pad=4)
        # subtitle just below title via text
        ax.annotate(subtitle, xy=(0, 1.02), xycoords="axes fraction", fontsize=9,
                    color=DARK_GREY, style="italic")
        grid_x(ax)
        # Annotate top 3
        for i, (region, val) in enumerate(rows[:3]):
            ax.text(val/1e6 + (vals.max() / 80), len(rows) - i - 1,
                    f"{val/1e6:.1f}M", fontsize=8, color=color, va="center", fontweight="bold")

    fig.text(0.07, 0.93,
             "Vyndaqel anchors P1 (1.58 BSEK over 3 yr). Vydura is small but visible (53 MSEK). Paxlovid + BeneFIX broadly distributed minor footprint.",
             fontsize=10, color=DARK_GREY, style="italic")
    fig.text(0.07, 0.02, "Source: IQVIA RD/IM extract 2026-04-27. Excludes regions with zero recorded sell-in.",
             fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.07, right=0.96, top=0.88, bottom=0.07)

    out_path = OUT / "C3_pfizer_rdim_portfolio_mosaic.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


if __name__ == "__main__":
    attr = load_attr_data()
    figure_attr_competitive(attr)
    figure_norrland_cluster(attr)
    figure_pfizer_rdim_mosaic()
    print("\nAll RD/IM figures generated.")
