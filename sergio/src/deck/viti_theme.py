# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
Viti Science visual theme for matplotlib.

Implements the brand palette + typography from viti-brand.skill, with chart-
appropriate adaptations: no reds (per brand rule), Pfizer blue used as the
data hero for Pfizer products, neutral grays for competitors.

Usage:
    from viti_theme import apply_viti_theme, COLORS, style_axes, add_takeaway
    apply_viti_theme()

Output target: 16:9 deck slides, content area ~12in x 6.75in. Default fig
sizes here leave room for slide titles.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams


# ---------------------------------------------------------------------------
# Color tokens (per viti-brand skill)
# ---------------------------------------------------------------------------
COLORS = {
    # Viti brand chrome
    "viti_blue":   "#2B9FD4",   # Headings, accent bars
    "viti_dark":   "#2A3439",   # Body text, secondary data
    "viti_cyan":   "#00E5FF",   # Thin accent lines only
    "viti_light":  "#E8F6FC",   # Subtle background fills
    "viti_medium": "#B8E2F3",   # Secondary fills
    "viti_gray":   "#5D6D7E",   # Captions, footnotes

    # Data accents (Pfizer products get their corporate blue)
    "pfizer_blue": "#0093D0",   # Pfizer corporate blue — for Ibrance, Vyndaqel, etc.
    "competitor_charcoal": "#2A3439",  # Strong competitor (Verzenios, etc.)
    "competitor_gray":     "#8896A6",  # Secondary competitor (Kisqali, etc.)
    "highlight_amber":     "#C8932B",  # Used SPARINGLY for "this is the bad number" callouts
                                       # (warm but muted; avoids brand-rule warm tones at high saturation)
}

# Drug-specific palette for the CDK4/6 trio
CDK46_PALETTE = {
    "Ibrance":   COLORS["pfizer_blue"],
    "Kisqali":   COLORS["competitor_gray"],
    "Verzenios": COLORS["competitor_charcoal"],
}


def _resolve_font():
    """Prefer Inter; fall back to a sensible chain."""
    available = {f.name for f in fm.fontManager.ttflist}
    for candidate in ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]:
        if candidate in available:
            return candidate
    return "DejaVu Sans"


def apply_viti_theme():
    """Apply Viti rcParams. Call once at top of figure scripts."""
    font = _resolve_font()
    rcParams.update({
        # Typography
        "font.family":       font,
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "semibold",
        "axes.titlepad":     16,
        "axes.labelsize":    10.5,
        "axes.labelweight":  "regular",
        "axes.labelcolor":   COLORS["viti_dark"],
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "xtick.color":       COLORS["viti_dark"],
        "ytick.color":       COLORS["viti_dark"],
        "legend.fontsize":   10,
        "legend.frameon":    False,

        # Spines and gridlines
        "axes.edgecolor":    COLORS["viti_gray"],
        "axes.linewidth":    0.6,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.spines.left":  True,
        "axes.spines.bottom":True,
        "grid.color":        COLORS["viti_medium"],
        "grid.linewidth":    0.5,
        "grid.alpha":        0.5,
        "axes.grid":         True,
        "axes.grid.axis":    "y",
        "axes.axisbelow":    True,

        # Output
        "figure.dpi":        120,
        "savefig.dpi":       300,
        "savefig.bbox":      "tight",
        "savefig.facecolor": "#FFFFFF",
        "axes.facecolor":    "#FFFFFF",
        "figure.facecolor":  "#FFFFFF",

        # Tick spacing
        "xtick.major.size":  0,        # Hide tick marks; rely on labels alone
        "ytick.major.size":  0,
        "xtick.major.pad":   6,
        "ytick.major.pad":   6,
    })


def style_axes(ax, hide_x_grid=True, ylim_pad=0.05):
    """Apply per-axes Viti polish: muted spines, no x grid by default,
    consistent label spacing."""
    ax.spines["left"].set_color(COLORS["viti_gray"])
    ax.spines["bottom"].set_color(COLORS["viti_gray"])
    if hide_x_grid:
        ax.xaxis.grid(False)
    ax.tick_params(axis="both", which="both", length=0)


def _space_letters(text, n=1):
    """Approximate letter-spacing by injecting thin spaces between chars.
    matplotlib doesn't support CSS-style letterspacing directly."""
    sep = " " * n  # thin space
    return sep.join(text)


def add_title_block(fig, eyebrow, headline, takeaway=None,
                    x=0.04, y_eyebrow=0.96, y_headline=0.91, y_takeaway=0.86,
                    takeaway_width=None, takeaway_line_step=0.026):
    """Three-line title block above the chart:
        eyebrow:  small caps, Viti Blue
        headline: bold, Viti Dark, the chart's structural title
        takeaway: optional, regular weight Viti Dark, the key sentence

    If takeaway_width (chars) is provided, the takeaway is wrapped across
    multiple lines using takeaway_line_step (figure-fraction y step).
    """
    fig.text(x, y_eyebrow, eyebrow.upper(),
             color=COLORS["viti_blue"], fontsize=10,
             fontweight="semibold")
    fig.text(x, y_headline, headline,
             color=COLORS["viti_dark"], fontsize=15,
             fontweight="bold")
    if takeaway:
        if takeaway_width:
            import textwrap
            lines = textwrap.wrap(takeaway, width=takeaway_width)
            for i, line in enumerate(lines):
                fig.text(x, y_takeaway - i * takeaway_line_step, line,
                         color=COLORS["viti_dark"], fontsize=11,
                         fontweight="regular")
        else:
            fig.text(x, y_takeaway, takeaway,
                     color=COLORS["viti_dark"], fontsize=11,
                     fontweight="regular")


def add_source_line(fig, text, x=0.04, y=0.02):
    """Footer source/credit line."""
    fig.text(x, y, text,
             color=COLORS["viti_gray"], fontsize=8, fontweight="regular")


def add_accent_rule(fig, x=0.04, y=0.94, length=0.08, color=None):
    """Thin horizontal accent rule under eyebrow text."""
    color = color or COLORS["viti_cyan"]
    from matplotlib.lines import Line2D
    line = Line2D([x, x + length], [y, y], transform=fig.transFigure,
                  color=color, linewidth=1.5, solid_capstyle="butt")
    fig.add_artist(line)


def annotate_endpoint(ax, x, y, text, color, side="right", offset=(8, 0),
                      fontsize=10.5, fontweight="semibold"):
    """Place a label at the end of a line series. side='right' or 'left'."""
    ha = "left" if side == "right" else "right"
    sign = 1 if side == "right" else -1
    ax.annotate(text, xy=(x, y), xytext=(sign * abs(offset[0]), offset[1]),
                textcoords="offset points", ha=ha, va="center",
                color=color, fontsize=fontsize, fontweight=fontweight)


def percent_axis(ax):
    """Format y-axis as percentages (assumes values are 0-100)."""
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v)}%"))


# ---------------------------------------------------------------------------
# Quick-reference for figure scripts
# ---------------------------------------------------------------------------
DECK_FIG_SIZE = (11, 5.6)        # 16:9 content area, leaves room for slide title
DECK_FIG_SIZE_TALL = (11, 6.8)   # When the chart needs more vertical room
DECK_FIG_SIZE_WIDE = (12, 5.0)   # For wide bar charts and timelines
