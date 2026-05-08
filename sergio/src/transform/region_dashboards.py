# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Shared layout helpers for the 6-slide regional profile dashboards.

Imported by viz_r1_*.py through viz_r6_*.py — keeps card/narrative drawing
consistent across slides.
"""

from pathlib import Path
import sys
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
from viti_theme import apply_viti_theme, COLORS

apply_viti_theme()

# Slide canvas — 16:9 deck slide (13.33 × 7.5 in)
SLIDE_W = 100.0   # axis units
SLIDE_H = 56.25
FIG_SIZE = (13.33, 7.5)


def make_canvas():
    """Return (fig, ax) sized as a deck slide, axis-disabled."""
    fig = plt.figure(figsize=FIG_SIZE)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, SLIDE_W)
    ax.set_ylim(0, SLIDE_H)
    ax.axis("off")
    return fig, ax


def draw_header(ax, eyebrow, title, subtitle=None):
    """Slide-top accent bar + eyebrow + title + optional subtitle."""
    ax.add_patch(Rectangle((0, SLIDE_H - 0.25), SLIDE_W, 0.25,
                              facecolor=COLORS["pfizer_blue"],
                              linewidth=0, zorder=2))
    ax.text(5.5, SLIDE_H - 3.0, eyebrow.upper(),
             fontsize=10, color=COLORS["viti_blue"],
             fontweight="semibold", va="top")
    ax.text(5.5, SLIDE_H - 4.5, title,
             fontsize=26, color=COLORS["viti_dark"],
             fontweight="bold", va="top")
    if subtitle:
        ax.text(5.5, SLIDE_H - 9.0, subtitle,
                 fontsize=11, color=COLORS["viti_gray"],
                 va="top")


def draw_source(ax, text):
    """Bottom-left source line."""
    ax.text(5.0, 2.0, text,
             fontsize=8.5, color=COLORS["viti_gray"], va="bottom")


def draw_kpi_card(ax, x, y, w, h, title, kpis, accent_color=None,
                   n_cols=3, value_fontsize=15, label_fontsize=9):
    """Draw a card with title + KPI tile grid.

    kpis: list of (value_str, label_str)
    n_cols: tiles per row (3 by default)
    """
    accent = accent_color or COLORS["pfizer_blue"]

    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((x, y), 0.5, h, facecolor=accent,
                              linewidth=0, zorder=2))
    ax.text(x + 1.5, y + h - 1.6, title,
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top", ha="left", zorder=3)

    n_rows = (len(kpis) + n_cols - 1) // n_cols
    pad_left = 1.5
    pad_top = 4.5
    tile_w = (w - pad_left - 1.0) / n_cols
    tile_h = (h - pad_top - 1.0) / max(n_rows, 1)

    for idx, (val, lbl) in enumerate(kpis):
        col = idx % n_cols
        row = idx // n_cols
        tx = x + pad_left + col * tile_w
        ty = y + h - pad_top - row * tile_h
        ax.text(tx, ty, str(val),
                 fontsize=value_fontsize, color=COLORS["viti_dark"],
                 fontweight="bold", va="top", ha="left", zorder=3)
        ax.text(tx, ty - 1.7, lbl,
                 fontsize=label_fontsize, color=COLORS["viti_gray"],
                 va="top", ha="left", zorder=3)


def draw_narrative_card(ax, x, y, w, h, title, bullets, accent_color=None,
                         body_fontsize=9, line_step=1.25, wrap_width=72,
                         bullet_gap=0.55):
    """Card with title + bulleted narrative. bullets: tuple/list of strings.

    Defaults tightened to fit 4 two-line bullets in a 17-axis-unit-tall card.
    """
    accent = accent_color or COLORS["pfizer_blue"]

    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=1.0",
        linewidth=0.6, edgecolor=COLORS["viti_medium"],
        facecolor="#FFFFFF", zorder=1,
    ))
    ax.add_patch(Rectangle((x, y), 0.5, h, facecolor=accent,
                              linewidth=0, zorder=2))
    ax.text(x + 1.5, y + h - 1.6, title,
             fontsize=13, color=COLORS["viti_dark"],
             fontweight="bold", va="top", ha="left", zorder=3)

    body_y = y + h - 3.7
    bx = x + 1.5
    for bullet in bullets:
        ax.text(bx, body_y, "→",
                 fontsize=body_fontsize, color=COLORS["pfizer_blue"],
                 fontweight="bold", va="top", ha="left", zorder=3)
        lines = textwrap.wrap(bullet, width=wrap_width)
        for i, line in enumerate(lines):
            ax.text(bx + 1.5, body_y - i * line_step, line,
                     fontsize=body_fontsize, color=COLORS["viti_dark"],
                     va="top", ha="left", zorder=3)
        body_y -= len(lines) * line_step + bullet_gap


def fmt_int(v):
    if v is None or v != v:
        return "—"
    return f"{int(v):,}"


def fmt_pct(v, dp=1):
    if v is None or v != v:
        return "—"
    return f"{v:.{dp}f}%"


def fmt_sek_per_cap(v):
    if v is None or v != v:
        return "—"
    return f"{int(v):,} SEK"


def fmt_signed_pct(v):
    if v is None or v != v:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.0f}%"


def fmt_msek(v):
    if v is None or v != v:
        return "—"
    return f"{v / 1e6:.0f}M kr"


def out_path(region_short, slide_id):
    region_slug = (region_short.replace(" ", "_")
                   .replace("ö", "o").replace("ä", "a").replace("å", "a"))
    out_dir = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main") \
              / "delivery" / "figures" / "region_profiles" / region_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{slide_id}.png"
