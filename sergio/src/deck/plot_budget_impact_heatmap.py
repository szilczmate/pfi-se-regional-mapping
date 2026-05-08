# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Render B1 budget impact heatmap with per-product normalisation.

Replaces the absolute-SEK heatmap (where Vyndaqel and Ibrance dominate the colour
scale and the other nine products fade to near-white) with a per-product normalisation:
each product column is scaled to its own maximum, so the regional pattern within
each product is legible regardless of absolute volume. Cell labels still show the
absolute M SEK figure so magnitude isn't lost.

Reads from master_workbook_v22.xlsx → Rx 2024 snapshot. Writes
working/data/master/figures_R/B1_budget_impact_heatmap.png.
"""
import sys
from pathlib import Path
import openpyxl
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from _pf_chart_setup import apply_pf_style, PF
apply_pf_style()

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v22.xlsx"
OUT_DIR = ROOT / "working/data/master/figures_R"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Annual cost benchmarks per Pfizer oral Rx product (SEK / patient / year).
# These are the same TLV/published benchmark estimates used in the R version.
ANNUAL_COST_SEK = {
    "Ibrance":            220_000,
    "Vyndaqel":           800_000,
    "Talzenna":           320_000,
    "Lorbrena/Lorviqua":  350_000,
    "Tukysa":             580_000,
    "Vydura":             2_500,
    "Paxlovid":           5_400,
}

# Display order: high-volume first, then specialty oncology, then high-volume Rx.
PRODUCT_ORDER = [
    "Vyndaqel", "Ibrance", "Tukysa", "Talzenna",
    "Lorbrena/Lorviqua", "Vydura", "Paxlovid",
]

# Region order — large to small population, matches the rest of the figure pack.
REGION_ORDER = [
    "Stockholm", "Västra Götaland", "Skåne", "Östergötland", "Uppsala",
    "Jönköping", "Halland", "Örebro län", "Södermanland", "Dalarna",
    "Värmland", "Gävleborg", "Västerbotten", "Västmanland", "Norrbotten",
    "Kronoberg", "Kalmar", "Blekinge", "Västernorrland",
    "Jämtland Härjedalen", "Gotland",
]


def load_patient_counts():
    """Returns dict of dicts: {region: {product: patient_count}}."""
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["Rx 2024 snapshot"]
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

    # Map each "<Product> patients 2024" header to the product
    product_cols = {}
    for i, h in enumerate(headers):
        if h and " patients 2024" in str(h):
            product = h.replace(" patients 2024", "")
            product_cols[product] = i

    data = {}
    for r in range(2, ws.max_row + 1):
        row = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
        region = row[0]
        if not region:
            continue
        # Drop "Region " / "län" prefixes/suffixes for display
        display = (str(region).replace("Region ", "").replace(" län", "")
                              .replace("Västra Götalandsregionen", "Västra Götaland")
                              .replace("Jämtland Härjedalen", "Jämtland H"))
        # Use the raw key for sourcing, but display label for axis
        data[display] = {}
        for product, col_idx in product_cols.items():
            v = row[col_idx]
            data[display][product] = float(v) if v is not None else 0.0
    return data


def main():
    print("Loading patient counts ...")
    patients = load_patient_counts()
    print(f"  {len(patients)} regions, {len(PRODUCT_ORDER)} products")

    # Build cost matrix (M SEK)
    regions = [r for r in REGION_ORDER if r in patients] + \
              [r for r in patients if r not in REGION_ORDER]
    n_rows = len(regions)
    n_cols = len(PRODUCT_ORDER)

    cost_matrix = np.zeros((n_rows, n_cols))
    for i, region in enumerate(regions):
        for j, product in enumerate(PRODUCT_ORDER):
            n = patients.get(region, {}).get(product, 0)
            cost_matrix[i, j] = n * ANNUAL_COST_SEK[product] / 1e6  # M SEK

    # Per-product (column-wise) normalisation for colour, keep absolute M SEK for labels
    col_max = cost_matrix.max(axis=0)
    col_max[col_max == 0] = 1  # avoid divide-by-zero for empty products
    norm_matrix = cost_matrix / col_max[np.newaxis, :]

    # National totals per product (for column subtitle)
    col_totals = cost_matrix.sum(axis=0)

    # Pfizer blue gradient
    cmap = LinearSegmentedColormap.from_list(
        "pf_blue",
        ["#F5F8FB", "#CFE5F2", "#86B6D9", "#3F7BB7", "#003F7F"],
    )

    # Layout — wide to give product columns room
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(norm_matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)

    # Tick labels
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))

    # Product column header: name + national total (gives magnitude back to the reader)
    col_labels = [f"{prod}\n{col_totals[j]:.0f} M SEK total"
                  for j, prod in enumerate(PRODUCT_ORDER)]
    ax.set_xticklabels(col_labels, fontsize=8.5, color=PF.navy)
    ax.set_yticklabels(regions, fontsize=8.5, color=PF.navy)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", which="both", length=0, pad=4)
    ax.tick_params(axis="y", which="both", length=0, pad=4)

    # White grid lines
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)

    # Cell labels — absolute M SEK, with dynamic text colour for legibility
    for i in range(n_rows):
        for j in range(n_cols):
            v = cost_matrix[i, j]
            if v <= 0:
                continue
            if v >= 1:
                label = f"{v:.0f}"
            elif v >= 0.1:
                label = f"{v:.1f}"
            else:
                continue  # skip near-zero
            text_color = "white" if norm_matrix[i, j] > 0.55 else PF.navy
            ax.text(j, i, label, ha="center", va="center",
                    fontsize=8, fontweight="bold", color=text_color)

    # Title and subtitle
    ax.set_title(
        "Regional budget impact of Pfizer oral-Rx products — 2024\n"
        "Cell colour normalised per product column so each product's regional pattern "
        "is visible regardless of absolute SEK volume; cell labels show absolute M SEK",
        fontsize=11, color=PF.navy, pad=14, loc="left",
    )

    # Colour bar — labelled to make the per-column normalisation explicit
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.04,
                        fraction=0.04, aspect=40)
    cbar.set_label(
        "Share of column (per-product) maximum   ·   "
        "0 = product absent in that region   ·   "
        "1 = highest-spending region for that product",
        fontsize=8.5, color=PF.navy,
    )
    cbar.ax.tick_params(labelsize=8, colors=PF.text_secondary)
    cbar.outline.set_visible(False)

    # Footer
    fig.text(
        0.01, -0.01,
        "Source: Socialstyrelsen Prescribed Drug Register 2024 + TLV / published "
        "benchmark annual-cost estimates per product. "
        "Conservative price estimates: Vyndaqel ~800k, Ibrance ~220k, Tukysa ~580k, "
        "Lorbrena ~350k, Talzenna ~320k, Vydura ~2.5k, Paxlovid ~5.4k SEK/patient/year.",
        ha="left", va="top", fontsize=7, color=PF.text_secondary, style="italic",
        wrap=True,
    )

    fig.tight_layout()
    out_png = OUT_DIR / "B1_budget_impact_heatmap.png"
    out_svg = OUT_DIR / "B1_budget_impact_heatmap.svg"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  Wrote {out_png}")
    print(f"  Wrote {out_svg}")


if __name__ == "__main__":
    main()
