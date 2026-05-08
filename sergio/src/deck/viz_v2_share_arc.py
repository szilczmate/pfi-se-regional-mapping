# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
V2 — CDK4/6 share-erosion arc (deck-grade prototype).

Deck slide 3. The single most important correction in the deck: Pfizer's
Ibrance has fallen from 58.6% to 17.5% of CDK4/6 SEK over 36 months, while
Verzenios has surged from 12.5% to 50.1%.

Output: delivery/figures/deck/V2_share_erosion_arc.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import (apply_viti_theme, COLORS, CDK46_PALETTE,
                         style_axes, add_title_block, add_source_line,
                         add_accent_rule, annotate_endpoint, percent_axis,
                         DECK_FIG_SIZE)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
INTERIM = ROOT / "working" / "data" / "interim"
OUT = ROOT / "delivery" / "figures" / "deck"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
df = pd.read_csv(INTERIM / "cdk46_share_arc_monthly.csv")
df["month"] = pd.to_datetime(df["month"])
df = df.set_index("month")

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=DECK_FIG_SIZE)
fig.subplots_adjust(left=0.06, right=0.82, top=0.78, bottom=0.14)

# Plot lines
order = ["Verzenios", "Kisqali", "Ibrance"]  # Plot Ibrance last so it sits on top
linewidths = {"Ibrance": 3.0, "Kisqali": 2.0, "Verzenios": 2.0}

for drug in order:
    color = CDK46_PALETTE[drug]
    ax.plot(df.index, df[drug],
            color=color,
            linewidth=linewidths[drug],
            solid_capstyle="round",
            zorder=3 if drug == "Ibrance" else 2)

# Endpoint labels
last = df.iloc[-1]
first = df.iloc[0]

for drug in order:
    annotate_endpoint(ax, df.index[-1], last[drug],
                       f"{drug}  {last[drug]:.1f}%",
                       color=CDK46_PALETTE[drug],
                       side="right", offset=(10, 0),
                       fontsize=11, fontweight="semibold")

# Gap bracket: chunky measurement-style indicator past the right edge of data
# showing the Ibrance collapse from 58.6% to 17.5%
ibr_start = first["Ibrance"]
ibr_end = last["Ibrance"]
collapse_pct = ibr_start - ibr_end

# Place bracket well past the endpoint labels so it doesn't crowd them
bracket_x = df.index[-1] + pd.Timedelta(days=240)
cap_len = pd.Timedelta(days=22)

# Faint dashed leader lines from data start/end points across to the bracket
# extremes (visually link the bracket to the values it measures)
ax.plot([df.index[0], bracket_x], [ibr_start, ibr_start],
        color=COLORS["pfizer_blue"], lw=0.8, ls=(0, (3, 3)), alpha=0.30,
        clip_on=False, zorder=2)
ax.plot([df.index[-1], bracket_x], [ibr_end, ibr_end],
        color=COLORS["pfizer_blue"], lw=0.8, ls=(0, (3, 3)), alpha=0.30,
        clip_on=False, zorder=2)

# Vertical bracket line
ax.plot([bracket_x, bracket_x], [ibr_end, ibr_start],
        color=COLORS["pfizer_blue"], lw=2.5, solid_capstyle="butt",
        clip_on=False, zorder=10)

# Top and bottom caps (small horizontal nubs pointing left toward the data)
for y in [ibr_start, ibr_end]:
    ax.plot([bracket_x - cap_len, bracket_x], [y, y],
            color=COLORS["pfizer_blue"], lw=2.5, solid_capstyle="butt",
            clip_on=False, zorder=10)

# Label to the right of the bracket — toned down per Sergio's feedback
ax.text(bracket_x + pd.Timedelta(days=25), (ibr_start + ibr_end) / 2,
        f"−{collapse_pct:.0f}\npts",
        color=COLORS["pfizer_blue"], fontsize=13,
        fontweight="semibold", ha="left", va="center",
        clip_on=False, zorder=11)

# Axis polish
style_axes(ax, hide_x_grid=True)
percent_axis(ax)
ax.set_ylim(0, 70)
ax.set_xlim(df.index[0] - pd.Timedelta(days=30),
            df.index[-1] + pd.Timedelta(days=380))

# Evenly-spaced year ticks only. Data range is conveyed in the headline and
# source line; axis stays a clean rhythm.
year_ticks = pd.date_range("2024-01-01", "2026-01-01", freq="YS")
ax.set_xticks(list(year_ticks))
ax.set_xticklabels([d.strftime("%Y") for d in year_ticks], fontsize=9.5)

ax.set_ylabel("Share of CDK4/6 class SEK\n(rolling 6-month)",
              fontsize=10, color=COLORS["viti_dark"])
ax.set_xlabel("")

# Title block
add_accent_rule(fig, x=0.06, y=0.91, length=0.05)
add_title_block(
    fig,
    eyebrow="CDK4/6 CLASS · SWEDEN · 2023–2026",
    headline="Pfizer's CDK4/6 share has fallen from 58.6% to 17.5% in 36 months.",
    takeaway="Verzenios rose 38 points to 50.1%. Kisqali held flat at 32.4%.",
    x=0.06, y_eyebrow=0.92, y_headline=0.86, y_takeaway=0.81,
)

add_source_line(fig,
                "Source: IQVIA Sweden Sell-In SEK monthly Apr 2023–Mar 2026, rolling 6-month share. "
                "Last point Sep 2023 → Mar 2026.",
                x=0.06, y=0.04)

plt.savefig(OUT / "V2_share_erosion_arc.png", facecolor="#FFFFFF")
print(f"Wrote {OUT / 'V2_share_erosion_arc.png'}")
