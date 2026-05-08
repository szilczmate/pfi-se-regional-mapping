# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
N3 — Sweden's pharmaceutical access governance (stakeholder mapping overview).

Visualises the 3-tier governance architecture:
  National tier   — NT-rådet (chair + 6 reps) + NSG Läkemedel (chair + reps)
  Sjukvårdsregion — 6 healthcare regions with their reps + key roles
  Regional        — 21 regions × 5-role per-region grid (handled in R5 deep dives)

Output: delivery/figures/region_profiles/_overview/N3_stakeholder_governance.png
"""

from pathlib import Path
import sys
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS, add_title_block, add_source_line, add_accent_rule

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
OUT = ROOT / "delivery" / "figures" / "region_profiles" / "_overview"
OUT.mkdir(parents=True, exist_ok=True)

apply_viti_theme()

# Sjukvårdsregion data — names, NT-rådet rep, NSG rep, regions covered
SVR_DATA = [
    {"name": "Stockholm-Gotland",
     "regions": "Stockholm + Gotland",
     "n_regions": 2,
     "population": "2.5M",
     "nt_rep": "Rickard Malmström",
     "nt_role": "NT-rådet rep",
     "nsg_rep": "Johan Bratt",
     "nsg_role": "NSG ledamot"},
    {"name": "Mellansverige",
     "regions": "Uppsala, Sörmland, Värmland,\nÖrebro, Västmanland, Dalarna,\nGävleborg",
     "n_regions": 7,
     "population": "1.85M",
     "nt_rep": "Jan Melin",
     "nt_role": "NT-rådet rep + LK ordf Uppsala",
     "nsg_rep": "Jonas Claesson",
     "nsg_role": "NSG ledamot (now VGR)"},
    {"name": "Sydöstra",
     "regions": "Östergötland, Jönköping, Kalmar",
     "n_regions": 3,
     "population": "1.09M",
     "nt_rep": "Mårten Lindström",
     "nt_role": "NT-rådet acting Chair",
     "nsg_rep": "Johan Rosenqvist",
     "nsg_role": "NSG ledamot (HSD Kalmar)"},
    {"name": "Södra",
     "regions": "Skåne, Halland,\nBlekinge, Kronoberg",
     "n_regions": 4,
     "population": "2.12M",
     "nt_rep": "Linda Staaf",
     "nt_role": "NT-rådet rep (Skåne)",
     "nsg_rep": "Pia Lundbom",
     "nsg_role": "NSG ledamot (Halland)"},
    {"name": "Västra",
     "regions": "Västra Götaland",
     "n_regions": 1,
     "population": "1.77M",
     "nt_rep": "Anna Lindhé",
     "nt_role": "NT-rådet rep (VGR)",
     "nsg_rep": "Jonas Claesson",
     "nsg_role": "NSG ledamot (VGR)"},
    {"name": "Norra",
     "regions": "Norrbotten, Västerbotten,\nVästernorrland, Jämtland H.",
     "n_regions": 4,
     "population": "0.90M",
     "nt_rep": "Anders Bergström",
     "nt_role": "NT-rådet Vice Chair",
     "nsg_rep": "Pia Näsvall",
     "nsg_role": "NSG Chair (HSD V-botten)"},
]

# 8 named cornerstones at the national tier
CORNERSTONES = [
    ("Mårten Lindström",   "NT-rådet acting Chair",    "Sydöstra · Jönköping"),
    ("Anders Bergström",   "NT-rådet Vice Chair",      "Norra · Norrbotten"),
    ("Pia Näsvall",        "NSG Chair + HSD",          "Norra · Västerbotten"),
    ("Rickard Malmström",  "NT-rådet rep (Stockholm)", "Stockholm-Gotland"),
    ("Johan Bratt",        "NSG ledamot (Stockholm)",  "Stockholm-Gotland"),
    ("Jan Melin",          "NT-rådet rep + LK ordf",   "Mellansverige · Uppsala"),
    ("Maria Ekelund",      "NT-rådet Sydöstra + LK",   "Sydöstra · Jönköping"),
    ("Mats Ek",            "LK ordf Stockholm",        "Stockholm-Gotland"),
]


def render_n3():
    fig = plt.figure(figsize=(13.33, 7.5))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56.25)
    ax.axis("off")

    # Top accent bar
    ax.add_patch(Rectangle((0, 56.0), 100, 0.25,
                              facecolor=COLORS["pfizer_blue"], linewidth=0))

    # Header
    ax.text(5.5, 54.0, "STAKEHOLDER MAPPING  ·  PART A  ·  GOVERNANCE OVERVIEW",
             fontsize=10, color=COLORS["viti_blue"],
             fontweight="semibold", va="top")
    ax.text(5.5, 52.5, "Sweden's pharmaceutical access governance",
             fontsize=22, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    ax.text(5.5, 48.0,
             "Three tiers · 138 stakeholders mapped · 92% combined verified-or-HIGH coverage.",
             fontsize=11, color=COLORS["viti_gray"], va="top")

    # ---------- Tier 1: National bodies ----------
    tier1_y = 36.5
    tier1_h = 8.0
    # NT-rådet card
    nt_x, nt_w = 5.0, 43.0
    ax.add_patch(FancyBboxPatch(
        (nt_x, tier1_y), nt_w, tier1_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0, facecolor=COLORS["competitor_charcoal"], zorder=1))
    ax.text(nt_x + 1.5, tier1_y + tier1_h - 1.5,
             "NT-rådet  ·  National therapeutic-use council",
             fontsize=12, color="white", fontweight="bold", va="top")
    ax.text(nt_x + 1.5, tier1_y + tier1_h - 4.0,
             "Acting Chair: Mårten Lindström (Jönköping)\n"
             "Vice Chair: Anders Bergström (Norrbotten)\n"
             "6 SVR reps + Koordinator",
             fontsize=10, color="white", va="top", linespacing=1.4)

    # NSG card
    nsg_x, nsg_w = 52.0, 43.0
    ax.add_patch(FancyBboxPatch(
        (nsg_x, tier1_y), nsg_w, tier1_h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0, facecolor=COLORS["competitor_charcoal"], zorder=1))
    ax.text(nsg_x + 1.5, tier1_y + tier1_h - 1.5,
             "NSG Läkemedel och medicinteknik",
             fontsize=12, color="white", fontweight="bold", va="top")
    ax.text(nsg_x + 1.5, tier1_y + tier1_h - 4.0,
             "Chair: Pia Näsvall (Västerbotten)\n"
             "6 SVR reps · cross-regional infrastructure\n"
             "Successor (Margareta Holmström) takes Chair 2026-07-01",
             fontsize=10, color="white", va="top", linespacing=1.4)

    # Tier label (above the cards)
    ax.text(5.0, tier1_y + tier1_h + 0.5,
             "TIER 1 · NATIONAL DECISION BODIES",
             fontsize=9, color=COLORS["viti_blue"],
             fontweight="bold", va="bottom")

    # ---------- Tier 2: 6 sjukvårdsregioner ----------
    tier2_y = 11.0
    tier2_h = 22.5
    n_svr = 6
    gap = 1.0
    svr_w = (90 - gap * (n_svr - 1)) / n_svr

    for i, svr in enumerate(SVR_DATA):
        x = 5.0 + i * (svr_w + gap)
        # Card body
        ax.add_patch(FancyBboxPatch(
            (x, tier2_y), svr_w, tier2_h,
            boxstyle="round,pad=0,rounding_size=1.0",
            linewidth=0.6, edgecolor=COLORS["viti_medium"],
            facecolor="#FFFFFF", zorder=1))
        ax.add_patch(Rectangle((x, tier2_y + tier2_h - 0.4), svr_w, 0.4,
                                  facecolor=COLORS["pfizer_blue"], linewidth=0))

        # SVR name
        ax.text(x + svr_w/2, tier2_y + tier2_h - 1.8, svr["name"],
                 ha="center", va="top",
                 fontsize=11.5, color=COLORS["viti_dark"], fontweight="bold")

        # Region count + population
        ax.text(x + svr_w/2, tier2_y + tier2_h - 3.6,
                 f"{svr['n_regions']} regions  ·  {svr['population']}",
                 ha="center", va="top",
                 fontsize=8.5, color=COLORS["viti_gray"])

        # Regions list (wrapped)
        regions_lines = svr["regions"].split("\n")
        for j, line in enumerate(regions_lines):
            ax.text(x + svr_w/2, tier2_y + tier2_h - 5.5 - j*1.4, line,
                     ha="center", va="top",
                     fontsize=8.5, color=COLORS["viti_dark"], style="italic")

        # NT-rådet rep section
        sect_y = tier2_y + tier2_h - 11.0
        ax.text(x + svr_w/2, sect_y, "NT-RÅDET REP",
                 ha="center", va="top",
                 fontsize=7.5, color=COLORS["viti_blue"], fontweight="bold")
        ax.text(x + svr_w/2, sect_y - 1.5, svr["nt_rep"],
                 ha="center", va="top",
                 fontsize=9.5, color=COLORS["viti_dark"], fontweight="semibold")
        nt_role_lines = textwrap.wrap(svr["nt_role"], width=22)
        for j, line in enumerate(nt_role_lines[:2]):
            ax.text(x + svr_w/2, sect_y - 3.0 - j*1.3, line,
                     ha="center", va="top",
                     fontsize=8, color=COLORS["viti_gray"])

        # NSG rep section
        sect2_y = tier2_y + tier2_h - 17.0
        ax.text(x + svr_w/2, sect2_y, "NSG REP",
                 ha="center", va="top",
                 fontsize=7.5, color=COLORS["viti_blue"], fontweight="bold")
        ax.text(x + svr_w/2, sect2_y - 1.5, svr["nsg_rep"],
                 ha="center", va="top",
                 fontsize=9.5, color=COLORS["viti_dark"], fontweight="semibold")
        nsg_role_lines = textwrap.wrap(svr["nsg_role"], width=22)
        for j, line in enumerate(nsg_role_lines[:2]):
            ax.text(x + svr_w/2, sect2_y - 3.0 - j*1.3, line,
                     ha="center", va="top",
                     fontsize=8, color=COLORS["viti_gray"])

    # Tier label
    ax.text(5.0, tier2_y + tier2_h + 1.0,
             "TIER 2 · SIX SJUKVÅRDSREGIONER",
             fontsize=9, color=COLORS["viti_blue"],
             fontweight="bold", va="bottom")

    # ---------- Tier 3 footer + compact methodology ----------
    foot_y = 9.0
    ax.text(5.0, foot_y, "TIER 3 · 21 REGIONER",
             fontsize=9, color=COLORS["viti_blue"],
             fontweight="bold", va="top")
    ax.text(5.0, foot_y - 1.7,
             "Per-region 5-role grid (Regiondirektör + HSD + RS ordf + HSN ordf + LK ordf). "
             "138 named individuals total. Stockholm and Västerbotten shown in full R5 detail.",
             fontsize=9, color=COLORS["viti_dark"], va="top")

    # Methodology block — compact horizontal form
    method_y = 5.5
    ax.text(5.0, method_y,
             "INFLUENCE SCORE  =  ROLE POWER  ×  CONFIDENCE  ×  SVR BONUS",
             fontsize=9, color=COLORS["viti_blue"],
             fontweight="bold", va="top")
    ax.text(5.0, method_y - 1.5,
             "Role power: NT-rådet rep 95 · NSG rep 85 · LK ordf 75 · HSD 70 · RD 65 · HSN ordf 55 · RS ordf 50",
             fontsize=8, color=COLORS["viti_dark"], va="top")
    ax.text(5.0, method_y - 2.7,
             "Confidence: HIGH × 1.00 · MEDIUM × 0.70 · LOW × 0.40 · STRUCTURAL × 0.50    "
             "SVR bonus (NT-rådet + NSG only): Stockholm-Gotland × 1.20 · Västra × 1.15 · "
             "Mellansverige + Södra × 1.10 · Sydöstra × 1.05 · Norra × 1.00",
             fontsize=8, color=COLORS["viti_dark"], va="top")
    ax.text(5.0, method_y - 4.0,
             "Worked example  →  Rickard Malmström (Stockholm-Gotland NT-rådet rep) = 95 × 1.00 × 1.20 = 114 (highest national score).",
             fontsize=8, color=COLORS["pfizer_blue"], fontweight="semibold",
             style="italic", va="top")

    # Source line
    ax.text(5.0, 0.2,
             "Source: samverkanlakemedel.se NT-rådet + NSG Läkemedel chairs (verified 2026-04-26), "
             "regional websites, Stakeholder mapping v10 (138 individuals), Workbook v30 \"Stakeholder influence\".",
             fontsize=8, color=COLORS["viti_gray"], va="bottom")

    plt.savefig(OUT / "N3_stakeholder_governance.png", facecolor="#FFFFFF", dpi=200)
    plt.close()
    print(f"Wrote {OUT / 'N3_stakeholder_governance.png'}")


if __name__ == "__main__":
    render_n3()
