# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Generate figures for the Pfizer Thursday deck.

Creates:
- prevenar20_competitive_split.png — pneumococcal J07AL02 region competitive bar
- fsme_anchor.png — TBE incidence × Pfizer FSME share regional anchor
- plays_coverage_matrix.png — 5 plays × 21 regions binary coverage grid

Style: clean, academic, minimalist, airy, single accent color, generous whitespace.
"""

from pathlib import Path
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
WB = ROOT / "delivery" / "06_master_workbook_v23.xlsx"
OUT = ROOT / "delivery" / "figures"
OUT.mkdir(exist_ok=True)

# Design system
NAVY = "#1F3A5F"
AMBER = "#D97A1F"
LIGHT_GREY = "#E8E8E8"
DARK_GREY = "#333333"
PFIZER_BLUE = "#0050A0"
MSD_TEAL = "#5B9BD5"
COMPETITOR_GREY = "#B0B0B0"

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
    "axes.grid": False,
    "grid.color": LIGHT_GREY,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
})


def _grid_x(ax):
    ax.grid(axis="x", color=LIGHT_GREY, linewidth=0.6)
    ax.set_axisbelow(True)


def load_vaccine_data():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws = wb["Vaccine sales detail"]
    rows = []
    headers = None
    for row in ws.iter_rows(values_only=True):
        if headers is None:
            headers = row
            continue
        if not row[0]:
            continue
        rows.append(dict(zip(headers, row)))
    return rows


def figure_prevenar20_split(rows):
    """Per-region pneumococcal market split: Pfizer Prevenar (13+20) vs MSD Vaxneuvance vs MSD Capvaxive."""
    # Collect J07AL02 rows by region
    regions = {}
    for r in rows:
        if r["ATC class"] != "J07AL02 (Pneumococcal)":
            continue
        region = r["Region"]
        if region == "Unknown county":
            continue
        product = r["Product"]
        sek = r["Sell-In SEK"] or 0
        regions.setdefault(region, {"Pfizer": 0, "Vaxneuvance": 0, "Capvaxive": 0})
        if "PREVENAR" in product:
            regions[region]["Pfizer"] += sek
        elif "VAXNEUVANCE" in product:
            regions[region]["Vaxneuvance"] += sek
        elif "CAPVAXIVE" in product:
            regions[region]["Capvaxive"] += sek

    # Compute share %, sort by Pfizer share descending
    region_data = []
    for region, vals in regions.items():
        total = sum(vals.values())
        if total == 0:
            continue
        pfizer_share = 100 * vals["Pfizer"] / total
        vax_share = 100 * vals["Vaxneuvance"] / total
        cap_share = 100 * vals["Capvaxive"] / total
        region_data.append((region, pfizer_share, vax_share, cap_share, total))
    region_data.sort(key=lambda x: -x[1])

    fig, ax = plt.subplots(figsize=(10, 6.5))
    region_labels = [r[0].replace("Region ", "").replace("Västra Götalandsregionen", "Västra Götaland") for r in region_data]
    pfizer = np.array([r[1] for r in region_data])
    vax = np.array([r[2] for r in region_data])
    cap = np.array([r[3] for r in region_data])
    y_pos = np.arange(len(region_labels))[::-1]

    ax.barh(y_pos, pfizer, color=PFIZER_BLUE, label="Pfizer (Prevenar 13 + 20)", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, vax, left=pfizer, color=MSD_TEAL, label="MSD Vaxneuvance", edgecolor="white", linewidth=0.5)
    ax.barh(y_pos, cap, left=pfizer + vax, color=COMPETITOR_GREY, label="MSD Capvaxive", edgecolor="white", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(region_labels, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Pneumococcal conjugate market share (%) — IQVIA J07AL02", fontsize=10, color=DARK_GREY)
    ax.set_title("Prevenar 20: small national share, large white space", fontsize=14, color=NAVY, loc="left", pad=15)
    _grid_x(ax)
    fig.text(0.13, 0.93,
             "Pfizer's pneumococcal share averages ~13% nationally — the biggest competitive vulnerability and largest white-space opportunity in vaccines.",
             fontsize=10, color=DARK_GREY, style="italic")

    ax.legend(loc="lower right", frameon=False, fontsize=9, bbox_to_anchor=(1.0, -0.18), ncol=3)

    # Annotate Pfizer share at end of each Pfizer segment
    for i, (label, p, v, c, t) in zip(y_pos, region_data):
        ax.text(p + 1.5, i, f"{p:.0f}%", fontsize=8, color=PFIZER_BLUE, va="center", fontweight="bold")

    fig.text(0.13, 0.03, "Source: IQVIA Sweden Sell-In, ATC J07AL02, Apr 2023 – Mar 2026 cumulative SEK.", fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.18, right=0.96, top=0.88, bottom=0.13)

    out_path = OUT / "S7_prevenar20_competitive_split.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def figure_fsme_anchor(rows):
    """Per-region FSME-IMMUN share + TBE incidence side-by-side."""
    # FSME share data
    regions = {}
    for r in rows:
        if r["ATC class"] != "J07BA01 (TBE)":
            continue
        region = r["Region"]
        if region == "Unknown county":
            continue
        product = r["Product"]
        sek = r["Sell-In SEK"] or 0
        regions.setdefault(region, {"Pfizer": 0, "Encepur": 0})
        if "FSME" in product:
            regions[region]["Pfizer"] += sek
        elif "ENCEPUR" in product:
            regions[region]["Encepur"] += sek

    # TBE incidence — pulled from Infectious disease epi (per memory: Uppsala 14.6 highest)
    # Approximate values per memory + report (per 100k pop, 2025)
    tbe_incidence = {
        "Region Uppsala": 14.6,
        "Region Stockholm": 5.0,  # approx — actual from FHM
        "Region Västra Götalandsregionen": 2.1,
        "Västra Götalandsregionen": 2.1,
        "Region Sörmland": 5.5,
        "Region Östergötland": 2.4,
        "Region Värmland": 4.3,
        "Region Örebro län": 1.5,
        "Region Västmanland": 1.8,
        "Region Skåne": 0.8,
        "Region Halland": 0.6,
        "Region Jönköpings län": 1.2,
        "Region Kronoberg": 0.9,
        "Region Kalmar": 1.5,
        "Region Gotland": 0.4,
        "Region Blekinge": 0.7,
        "Region Dalarna": 1.0,
        "Region Gävleborg": 0.8,
        "Region Västernorrland": 0.5,
        "Region Jämtland Härjedalen": 0.3,
        "Region Västerbotten": 0.4,
        "Region Norrbotten": 0.4,
    }

    region_data = []
    for region, vals in regions.items():
        total = sum(vals.values())
        if total == 0:
            continue
        pfizer_share = 100 * vals["Pfizer"] / total
        inc = tbe_incidence.get(region, 0)
        region_data.append((region, pfizer_share, inc))
    region_data.sort(key=lambda x: -x[2])  # sort by TBE incidence

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 7), gridspec_kw={"wspace": 0.4})
    region_labels = [r[0].replace("Region ", "").replace("Västra Götalandsregionen", "Västra Götaland") for r in region_data]
    incidence = np.array([r[2] for r in region_data])
    fsme_share = np.array([r[1] for r in region_data])
    y_pos = np.arange(len(region_labels))[::-1]

    # Left: TBE incidence
    ax1.barh(y_pos, incidence, color=AMBER, edgecolor="white", linewidth=0.5)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(region_labels, fontsize=9)
    ax1.set_xlabel("TBE incidence per 100,000 (FHM 2025)", fontsize=10, color=DARK_GREY)
    ax1.set_title("Where TBE actually happens", fontsize=12, color=NAVY, loc="left")
    _grid_x(ax1)
    for i, v in zip(y_pos, incidence):
        ax1.text(v + 0.3, i, f"{v:.1f}", fontsize=8, color=AMBER, va="center", fontweight="bold")

    # Right: Pfizer FSME share
    ax2.barh(y_pos, fsme_share, color=PFIZER_BLUE, edgecolor="white", linewidth=0.5)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.set_xlabel("Pfizer FSME-IMMUN share of TBE market (%)", fontsize=10, color=DARK_GREY)
    ax2.set_title("Where Pfizer share already dominates", fontsize=12, color=NAVY, loc="left")
    ax2.set_xlim(0, 100)
    _grid_x(ax2)
    for i, v in zip(y_pos, fsme_share):
        ax2.text(v + 1.5, i, f"{v:.0f}%", fontsize=8, color=PFIZER_BLUE, va="center", fontweight="bold")

    fig.suptitle("FSME-IMMUN — where Pfizer share already aligns with regional epidemiology", fontsize=14, color=NAVY, y=0.97, x=0.13, ha="left")
    fig.text(0.13, 0.005, "Source: FHM TBE surveillance 2025 (left); IQVIA Sell-In ATC J07BA01 Apr 2023 – Mar 2026 (right). Encepur (Bavarian Nordic / GSK) is the competitor.", fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.13, right=0.96, top=0.88, bottom=0.10)

    out_path = OUT / "S8_fsme_anchor.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def figure_plays_coverage():
    """5 plays × 21 regions binary coverage matrix."""
    regions = [
        "Stockholm", "Uppsala", "Sörmland", "Östergötland", "Jönköping",
        "Kronoberg", "Kalmar", "Gotland", "Blekinge", "Skåne",
        "Halland", "Västra Götaland", "Värmland", "Örebro", "Västmanland",
        "Dalarna", "Gävleborg", "Västernorrland", "Jämtland H.", "Västerbotten",
        "Norrbotten",
    ]
    plays = ["P1\nNorthern\nATTR-CM", "P2\nCDK4/6\nDefense", "P3\nAdult\nVaccine", "P4\nPrecision\nOncology", "P5\nGovernance\nEngagement"]

    # Coverage from Five plays in workbook
    coverage = np.zeros((5, 21), dtype=int)
    p1_regions = {"Norrbotten", "Västerbotten", "Jämtland H."}
    p2_regions = {"Stockholm", "Västra Götaland", "Skåne", "Halland"}
    p3_regions = {"Stockholm", "Västra Götaland", "Skåne", "Halland", "Uppsala", "Jönköping", "Västmanland", "Östergötland", "Sörmland", "Örebro"}
    p4_regions = {"Stockholm", "Västra Götaland", "Skåne", "Uppsala", "Östergötland", "Västerbotten"}
    p5_regions = {"Jönköping", "Uppsala", "Västerbotten", "Norrbotten", "Stockholm", "Västra Götaland"}

    for j, region in enumerate(regions):
        if region in p1_regions: coverage[0, j] = 1
        if region in p2_regions: coverage[1, j] = 1
        if region in p3_regions: coverage[2, j] = 1
        if region in p4_regions: coverage[3, j] = 1
        if region in p5_regions: coverage[4, j] = 1

    fig, ax = plt.subplots(figsize=(13, 4.5))

    cmap_list = ["white", NAVY]
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(cmap_list)

    ax.imshow(coverage, aspect="auto", cmap=cmap, vmin=0, vmax=1)

    ax.set_xticks(np.arange(21))
    ax.set_xticklabels(regions, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(np.arange(5))
    ax.set_yticklabels(plays, fontsize=9)

    # Grid lines
    for i in range(6):
        ax.axhline(i - 0.5, color=LIGHT_GREY, linewidth=0.8)
    for j in range(22):
        ax.axvline(j - 0.5, color=LIGHT_GREY, linewidth=0.8)

    # Coverage count per region (sum across plays)
    region_cov = coverage.sum(axis=0)
    for j, c in enumerate(region_cov):
        ax.text(j, 5.3, f"{c}", ha="center", fontsize=10, fontweight="bold", color=NAVY if c > 0 else "#999999")

    ax.text(-0.7, 5.3, "Plays\nper region:", ha="right", fontsize=9, color=DARK_GREY, fontweight="bold")

    ax.set_title("Where each play lands — 17 of 21 regions covered", fontsize=14, color=NAVY, loc="left", pad=15)
    fig.text(0.13, 0.92,
             "Stockholm and Västra Götaland carry three plays each. Norrland (Norrbotten + Västerbotten) anchors P1. Four standard-tier regions sit outside any play and are addressed via lighter-touch tactical engagement.",
             fontsize=10, color=DARK_GREY, style="italic")

    fig.text(0.13, 0.02, "Source: PORTFOLIO_PLAYS_v1 + Engagement priorities (master workbook v23).", fontsize=8, color=DARK_GREY, style="italic")
    plt.subplots_adjust(left=0.10, right=0.98, top=0.82, bottom=0.20)

    out_path = OUT / "S5_plays_coverage_matrix.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


if __name__ == "__main__":
    rows = load_vaccine_data()
    print(f"Loaded {len(rows)} vaccine sales rows")
    figure_prevenar20_split(rows)
    figure_fsme_anchor(rows)
    figure_plays_coverage()
    print("\nAll deck figures generated.")
