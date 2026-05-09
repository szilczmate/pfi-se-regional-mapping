# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V3 — CDK4/6 class-naive capture (deck slide 4).

Single horizontal stacked bar showing share of class-naive new starts last 6
months. Pfizer captures 7% versus Kisqali 52% and Verzenios 41% — the leading
indicator behind V2's lagging 17.5% SEK share.

Output: delivery/figures/deck/V3_class_naive_capture.png
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, CDK46_PALETTE,
                         add_title_block, add_source_line, add_accent_rule,
                         DECK_FIG_SIZE_WIDE)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
OUT = ROOT / "delivery" / "figures" / "deck"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Load
result = pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevData.RDS"))
df = list(result.values())[0]
df["date"] = pd.to_datetime(df["date"].astype(str))

LAST6_END = pd.Timestamp("2026-01-01")
LAST6_START = LAST6_END - pd.DateOffset(months=5)

last6 = df[(df["date"] >= LAST6_START) & (df["date"] <= LAST6_END) &
           (df["region"] == "Sweden") &
           (df["analysis"] == "New CDK4/6 user")]
agg = last6.groupby("drug")["n"].sum()
total = agg.sum()
shares = (agg / total * 100).reindex(["Ibrance", "Verzenios", "Kisqali"])
counts = agg.reindex(["Ibrance", "Verzenios", "Kisqali"])

print(f"Total class-naive starts last 6mo Sweden: {int(total)}")
for d, s in shares.items():
    print(f"  {d}: {int(counts[d])} = {s:.1f}%")

# ---------------------------------------------------------------------------
# Figure: single horizontal stacked bar
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.4))
fig.subplots_adjust(left=0.06, right=0.94, top=0.62, bottom=0.20)

bar_y = 0.5
bar_height = 0.55

cumulative = 0
for drug in ["Ibrance", "Verzenios", "Kisqali"]:
    width = shares[drug]
    color = CDK46_PALETTE[drug]
    ax.barh(bar_y, width, left=cumulative, height=bar_height,
            color=color, edgecolor="white", linewidth=2)

    # Label inside the segment if wide enough; outside if narrow
    label_x = cumulative + width / 2
    if width > 12:
        ax.text(label_x, bar_y, f"{drug}\n{width:.0f}%  ·  {int(counts[drug])} patients",
                ha="center", va="center",
                color="white", fontsize=11.5, fontweight="bold")
    else:
        # Place label above the bar with a leader callout
        ax.text(label_x, bar_y + 0.55,
                f"{drug}\n{width:.0f}%",
                ha="center", va="bottom",
                color=color, fontsize=11.5, fontweight="bold")
        ax.text(label_x, bar_y + 0.30,
                f"{int(counts[drug])} patients",
                ha="center", va="bottom",
                color=COLORS["viti_gray"], fontsize=9)

    cumulative += width

ax.set_xlim(0, 100)
ax.set_ylim(-0.2, 1.4)
ax.set_yticks([])
ax.set_xticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.grid(False)

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="CDK4/6 NEW STARTS · SWEDEN · OCT 2025–MAR 2026",
    headline="Pfizer captures 7% of class-naive new starts. Novartis captures 52%.",
    takeaway=f"Of {int(total)} patients starting CDK4/6 therapy for the first time, {int(counts['Ibrance'])} received Ibrance.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: AVA patient-level data, 'New CDK4/6 user' = patient with no prior CDK4/6 dispensation. "
                "Window: Aug 2025–Jan 2026 (6 months, AVA latest available).",
                x=0.06, y=0.05)

plt.savefig(OUT / "V3_class_naive_capture.png", facecolor="#FFFFFF")
print(f"\nWrote {OUT / 'V3_class_naive_capture.png'}")
