# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V6 — CDK4/6 stickiness gap (PoT/PWD ratio, deck slide 7).

Three-bar comparison. Last-6-month Sweden values:
  Ibrance   1.42
  Kisqali   1.62
  Verzenios 1.58

Even if Pfizer wins back class-naive starts, faster Ibrance churn amplifies
losses on the back end.

Output: delivery/figures/deck/V6_persistence_gap.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, CDK46_PALETTE,
                         style_axes, add_title_block, add_source_line,
                         add_accent_rule, DECK_FIG_SIZE)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
INTERIM = ROOT / "working" / "data" / "interim"
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

df = pd.read_csv(INTERIM / "cdk46_persistence_ratios.csv")
df = df.set_index("drug").loc[["Ibrance", "Verzenios", "Kisqali"]]
print(df)

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.4))
fig.subplots_adjust(left=0.10, right=0.94, top=0.74, bottom=0.16)

drugs = df.index.tolist()
ratios = df["ratio"].tolist()
pwd_counts = df["PWD_total"].astype(int).tolist()
colors = [CDK46_PALETTE[d] for d in drugs]

bar_x = list(range(len(drugs)))
bars = ax.bar(bar_x, ratios, color=colors, width=0.55,
              edgecolor="white", linewidth=2)

# Value labels above each bar
for i, (drug, ratio, pwd) in enumerate(zip(drugs, ratios, pwd_counts)):
    color = CDK46_PALETTE[drug]
    ax.text(i, ratio + 0.04, f"{ratio:.2f}",
            ha="center", va="bottom", color=color,
            fontsize=18, fontweight="bold")
    ax.text(i, ratio + 0.005, "",
            ha="center", va="bottom",
            color=COLORS["viti_gray"], fontsize=9)

# Drug labels under each bar
ax.set_xticks(bar_x)
ax.set_xticklabels(drugs, fontsize=12, fontweight="semibold")

# Light reference line at 1.0 (no on-treatment buffer)
ax.axhline(1.0, color=COLORS["viti_gray"], lw=0.8, ls=(0, (3, 3)),
           alpha=0.5, zorder=1)
ax.text(2.55, 1.0, "PoT = PWD\n(no buffer)",
        ha="left", va="center",
        color=COLORS["viti_gray"], fontsize=8.5, alpha=0.85,
        clip_on=False)

# Sample size below x-axis labels
for i, (drug, pwd) in enumerate(zip(drugs, pwd_counts)):
    ax.text(i, -0.16, f"PWD = {pwd:,}",
            transform=ax.get_xaxis_transform(),
            ha="center", va="top",
            color=COLORS["viti_gray"], fontsize=9)

# Headline already states the +14% comparison; no inline annotation needed.

# Polish
ax.set_ylabel("Patients on Treatment / Patients with Dispensations",
              fontsize=10, color=COLORS["viti_dark"])
ax.set_ylim(0, 2.0)
ax.set_xlim(-0.55, len(drugs) + 0.20)
style_axes(ax)
ax.spines["bottom"].set_visible(False)
ax.tick_params(axis="x", which="both", length=0)

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="CDK4/6 STICKINESS · SWEDEN · OCT 2025–JAN 2026",
    headline="Kisqali patients sit on-treatment 14% longer than Ibrance patients.",
    takeaway="Even if Pfizer wins back new starts, faster churn amplifies losses on the back end.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: AVA patient-level data, last-6-month Sweden national aggregate. "
                "Ratio = Patients-on-Treatment / Patients-with-Dispensations (3-month grace rule). "
                "Stickiness proxy, not median treatment duration.",
                x=0.06, y=0.03)

plt.savefig(OUT / "V6_persistence_gap.png", facecolor="#FFFFFF")
print(f"\nWrote {OUT / 'V6_persistence_gap.png'}")
