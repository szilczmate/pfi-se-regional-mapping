# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N1 — Sweden Healthcare Equity Composite (national figure).

21 Swedish regions ranked by SES composite rank (1 = highest need).
Composite of: foreign-born %, post-secondary education %, premature mortality
25–64, healthcare-amenable mortality. Workbook v30 sheet "Equity composite".

Output: delivery/figures/national/N1_equity_composite.png
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS, add_title_block, add_source_line, add_accent_rule

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

df = pd.read_excel(ROOT / "delivery" / "06_master_workbook_v30.xlsx",
                    sheet_name="Equity composite")
df = df.sort_values("SES composite rank (1=highest need)", ascending=True).reset_index(drop=True)
df["region_short"] = df["Region"].str.replace("Region ", "")
df["region_short"] = df["region_short"].replace({
    "Västra Götalandsregionen": "Västra Götaland",
    "Region Jämtland Härjedalen": "Jämtland H.",
})

# Compute equity composite score (0-100, higher = better equity / lower need)
# Inverted from rank for visualization
df["equity_score"] = (22 - df["SES composite rank (1=highest need)"]) / 21 * 100

EXEMPLARS = {"Region Stockholm", "Region Västerbotten"}

# Colour bands by quartile of need
def quartile_color(rank):
    if rank <= 6:
        return COLORS["highlight_amber"]      # highest need
    if rank <= 11:
        return COLORS["competitor_charcoal"]  # high
    if rank <= 16:
        return COLORS["competitor_gray"]      # moderate
    return COLORS["pfizer_blue"]              # lowest need (best equity)


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13.33, 7.5))
fig.subplots_adjust(left=0.16, right=0.96, top=0.78, bottom=0.07)
ax = fig.add_subplot(111)

y_pos = list(range(len(df)))
colors = [quartile_color(r) for r in df["SES composite rank (1=highest need)"]]
bars = ax.barh(y_pos, df["equity_score"], color=colors,
                edgecolor="white", linewidth=0.8, height=0.7)

# Highlight exemplars with a thicker edge
for i, region in enumerate(df["Region"]):
    if region in EXEMPLARS:
        bars[i].set_edgecolor(COLORS["pfizer_blue"])
        bars[i].set_linewidth(2.2)

# Region labels on left
for i, name in enumerate(df["region_short"]):
    is_exemplar = df.loc[i, "Region"] in EXEMPLARS
    weight = "bold" if is_exemplar else "regular"
    ax.text(-2, i, name,
             fontsize=10, color=COLORS["viti_dark"],
             fontweight=weight, va="center", ha="right")

# Rank labels on right
for i, row in df.iterrows():
    ax.text(row["equity_score"] + 1.5, i, f"#{int(row['SES composite rank (1=highest need)'])}",
             fontsize=9.5, color=COLORS["viti_gray"], va="center")

# Reverse y so #1 is at top
ax.invert_yaxis()
ax.set_yticks([])
ax.set_xlim(0, 105)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["", "", "", "", ""])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.grid(False)

# X-axis labels: highest need (left) → best equity (right)
ax.text(0, len(df) + 0.5, "Highest need",
         fontsize=9, color=COLORS["highlight_amber"],
         fontweight="semibold", va="top", ha="left")
ax.text(100, len(df) + 0.5, "Best equity",
         fontsize=9, color=COLORS["pfizer_blue"],
         fontweight="semibold", va="top", ha="right")

# Title block
add_accent_rule(fig, x=0.06, y=0.93, length=0.05)
add_title_block(
    fig,
    eyebrow="NATIONAL  ·  HEALTHCARE EQUITY COMPOSITE  ·  21 REGIONS",
    headline="Sweden's healthcare equity gradient — Sörmland to Halland.",
    takeaway="Composite of foreign-born share, post-secondary education, premature mortality 25–64, and healthcare-amenable mortality. Stockholm and Västerbotten ranked #19 and #18 — among the lowest-need regions in this dataset.",
    x=0.06, y_eyebrow=0.94, y_headline=0.88, y_takeaway=0.83,
    takeaway_width=130, takeaway_line_step=0.027,
)

add_source_line(fig,
                "Source: Workbook v30 \"Equity composite\". Composite ranks 21 regions on four equity-of-access indicators "
                "(2024 SCB + Folkhälsomyndigheten data). Quartile bands shown: highest need (#1–6) → best equity (#17–21).",
                x=0.06, y=0.025)

plt.savefig(OUT / "N1_equity_composite.png", facecolor="#FFFFFF", dpi=200)
plt.close()
print(f"Wrote {OUT / 'N1_equity_composite.png'}")
