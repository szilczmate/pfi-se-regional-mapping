# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V5 — Brick-level CDK4/6 priority quadrant (deck slide 6).

78-brick scatter: x = brick CDK4/6 market size (last 6mo SEK), y = Ibrance share.
Recovery targets in red-zone (low share, big market). Top-N labeled.

Output: delivery/figures/deck/V5_brick_priority_quadrant.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, style_axes,
                         add_title_block, add_source_line, add_accent_rule,
                         percent_axis)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
INTERIM = ROOT / "working" / "data" / "interim"
OUT = ROOT / "delivery" / "figures" / "deck"

apply_viti_theme()

df = pd.read_csv(INTERIM / "cdk46_brick_priority.csv")

NATIONAL_SHARE = 17.5  # last-6mo Sweden Ibrance share

# Categorise for color
def cat_color(row):
    if row["Priority quadrant"] == "Recovery target":
        return COLORS["pfizer_blue"]      # Brand blue for the priority targets
    if row["Priority quadrant"] == "Defense target":
        return COLORS["highlight_amber"]  # Sparingly-used amber for the at-risk
    if row["Priority quadrant"] == "Stronghold":
        return COLORS["competitor_charcoal"]
    return COLORS["competitor_gray"]      # Stable mid-tier or low priority

df["color"] = df.apply(cat_color, axis=1)
df["alpha"] = df["Priority quadrant"].map({
    "Recovery target": 0.95,
    "Defense target":  0.95,
    "Stronghold":      0.7,
    "Stable mid-tier": 0.4,
    "Low priority (small market)": 0.30,
})

# Bubble size scaling
max_market = df["CDK4/6 total SEK (last 6mo)"].max()
df["bubble"] = (df["CDK4/6 total SEK (last 6mo)"] / max_market) ** 0.7 * 700 + 30

# ---------------------------------------------------------------------------
# Figure: scatter on left, ranked recovery list on right
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 6.4))
gs = fig.add_gridspec(1, 5, left=0.06, right=0.97,
                       top=0.78, bottom=0.10,
                       wspace=0.05)
ax = fig.add_subplot(gs[0, :3])
ax_list = fig.add_subplot(gs[0, 3:])
ax_list.axis("off")

# Convert market size to M kr for x-axis
df["market_M"] = df["CDK4/6 total SEK (last 6mo)"] / 1e6

# Scatter
for _, row in df.iterrows():
    ax.scatter(row["market_M"], row["Ibrance share %"],
               s=row["bubble"], c=row["color"],
               alpha=row["alpha"],
               edgecolors="white", linewidths=0.8,
               zorder=3 if row["Priority quadrant"] == "Recovery target" else 2)

# National share reference line
ax.axhline(NATIONAL_SHARE, color=COLORS["viti_gray"],
           lw=0.9, ls=(0, (4, 4)), alpha=0.7, zorder=1)
ax.text(df["market_M"].max() * 1.01, NATIONAL_SHARE,
        f"National 17.5%",
        ha="left", va="center",
        color=COLORS["viti_gray"], fontsize=9, alpha=0.85,
        clip_on=False)

# In-chart: only label Stockholm-S (biggest) + 3 defense bricks. The full
# recovery list lives in the side panel.
recovery_top1 = df[df["Priority quadrant"] == "Recovery target"].nlargest(1, "CDK4/6 total SEK (last 6mo)")
for _, row in recovery_top1.iterrows():
    label = row["Brick"].split(" - ", 1)[1] if " - " in row["Brick"] else row["Brick"]
    ax.annotate(label,
                xy=(row["market_M"], row["Ibrance share %"]),
                xytext=(10, 8),
                textcoords="offset points",
                fontsize=9, color=COLORS["pfizer_blue"],
                fontweight="semibold")

# Defense labels listed in side panel instead of in-chart (points cluster
# tightly so any in-chart labelling stacks visually).

# Polish
percent_axis(ax)
ax.set_xlabel("Brick CDK4/6 market size, last 6 months (M kr)",
              fontsize=10, color=COLORS["viti_dark"])
ax.set_ylabel("Ibrance share of brick CDK4/6 SEK",
              fontsize=10, color=COLORS["viti_dark"])
ax.set_xlim(-df["market_M"].max() * 0.03, df["market_M"].max() * 1.08)
ax.set_ylim(0, 65)
style_axes(ax, hide_x_grid=True)
ax.grid(True, axis="both", alpha=0.25)

# Legend on chart
legend_items = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["pfizer_blue"], markersize=10,
           markeredgecolor="white", markeredgewidth=1,
           label="Recovery target  (11)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["highlight_amber"], markersize=10,
           markeredgecolor="white", markeredgewidth=1,
           label="Defense target  (3)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["competitor_charcoal"], markersize=10,
           markeredgecolor="white", markeredgewidth=1, alpha=0.7,
           label="Stronghold  (9)"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=COLORS["competitor_gray"], markersize=10,
           markeredgecolor="white", markeredgewidth=1, alpha=0.5,
           label="Other  (55)"),
]
leg = ax.legend(handles=legend_items, loc="upper right",
                 frameon=False, fontsize=9.5,
                 borderpad=0.4, labelspacing=0.5)
for text in leg.get_texts():
    text.set_color(COLORS["viti_dark"])

# ---------------------------------------------------------------------------
# Right panel: ranked top recovery bricks
# ---------------------------------------------------------------------------
ax_list.text(0.02, 0.97, "TOP RECOVERY BRICKS",
              transform=ax_list.transAxes,
              fontsize=10, fontweight="bold",
              color=COLORS["pfizer_blue"], va="top")
ax_list.text(0.02, 0.92, "ranked by Recovery SEK opportunity",
              transform=ax_list.transAxes,
              fontsize=8.5, color=COLORS["viti_gray"], va="top")

# Top 8 by Recovery SEK opportunity, regardless of which quadrant they land in
# (Stockholm-S has highest absolute opportunity at 782k kr but sits 0.1pp above
# the strict Recovery-target threshold, so we rank by SEK not quadrant)
top_recovery = df.nlargest(8, "Recovery SEK (kr)")
y_start = 0.85
y_step = 0.085
for i, (_, row) in enumerate(top_recovery.iterrows()):
    label = row["Brick"].split(" - ", 1)[1] if " - " in row["Brick"] else row["Brick"]
    y = y_start - i * y_step
    rec_kr = row["Recovery SEK (kr)"] / 1e3  # in k kr
    share = row["Ibrance share %"]
    # Rank dot
    ax_list.text(0.02, y, f"{i+1}.",
                  transform=ax_list.transAxes,
                  fontsize=9.5, color=COLORS["pfizer_blue"],
                  fontweight="bold", va="center")
    # Brick name
    ax_list.text(0.10, y, label,
                  transform=ax_list.transAxes,
                  fontsize=10, color=COLORS["viti_dark"],
                  fontweight="semibold", va="center")
    # Share % + SEK
    ax_list.text(0.95, y,
                  f"{share:.0f}% share  ·  {rec_kr:.0f}k kr",
                  transform=ax_list.transAxes,
                  fontsize=8.5, color=COLORS["viti_gray"],
                  va="center", ha="right")

# Defense bricks list at the bottom of the side panel
ax_list.text(0.02, 0.22, "DEFENSE TARGETS",
              transform=ax_list.transAxes,
              fontsize=9, fontweight="bold",
              color=COLORS["highlight_amber"], va="top")
ax_list.text(0.02, 0.185, "above-mean Pfizer share, Kisqali growing >10%",
              transform=ax_list.transAxes,
              fontsize=8, color=COLORS["viti_gray"], va="top")

defense_list = df[df["Priority quadrant"] == "Defense target"].sort_values(
    "Defense-risk SEK (kr)", ascending=False).head(3)
y = 0.13
for _, row in defense_list.iterrows():
    label = row["Brick"].split(" - ", 1)[1] if " - " in row["Brick"] else row["Brick"]
    risk_kr = row["Defense-risk SEK (kr)"] / 1e3
    share = row["Ibrance share %"]
    ax_list.text(0.10, y, label,
                  transform=ax_list.transAxes,
                  fontsize=9.5, color=COLORS["viti_dark"],
                  fontweight="semibold", va="center")
    ax_list.text(0.95, y, f"{share:.0f}% share  ·  {risk_kr:.0f}k risk",
                  transform=ax_list.transAxes,
                  fontsize=8.5, color=COLORS["viti_gray"],
                  va="center", ha="right")
    y -= 0.04

# Footer
ax_list.text(0.02, 0.005,
              "Recovery top 8 = 4.1M kr (44% of 9.3M total).",
              transform=ax_list.transAxes,
              fontsize=8.5, color=COLORS["viti_gray"],
              fontweight="semibold", va="bottom")

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="P2 FIELD DEPLOYMENT · 78 IQVIA BRICKS · LAST 6 MO",
    headline="Eight bricks carry 4.1M kr of the 9.3M kr CDK4/6 recovery opportunity.",
    takeaway="Stockholm-S, Gävle, Luleå/Boden, Örebro, Västerås — large markets where Pfizer sits well below the 17.5% national share.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: IQVIA Sweden Sell-In SEK Oct 2025–Mar 2026, 78 active CDK4/6 bricks. "
                "Recovery SEK = (national_share − brick_share) × brick_total. Bubble size = brick market.",
                x=0.06, y=0.03)

plt.savefig(OUT / "V5_brick_priority_quadrant.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V5_brick_priority_quadrant.png'}")
