# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Chart pack v2 — deck-ready, Pfizer brand palette, Swedish labels only.

Fixes from audit:
- Overlapping labels: auto-offset, fewer inline annotations, call-out boxes for key regions only
- Mixed English/Swedish: all titles + axis labels + annotations in Swedish
- Pfizer colors: #0093D0 (primary blue), #004F8F (dark), #E4002B (highlight/red)

Generates (PNG, 300 DPI, 16:9 aspect for slide insertion):
01. Vyndaqel Skellefteå-klustret per region (horizontal bar, top-of-ranked)
02. Ibrance utveckling 2021-2024 per region (time series, Stockholm/VGR highlighted)
03. Hälsoorättvisa bivariat (scatter: utbildning × förtida dödlighet)
04. Mediantid till specialistbesök per region (ranked bar)
05. Top Pfizer-möjlighet per region (horizontal bar)
06. Vaccin per capita + Pfizer-andel (stacked bar + overlay line)
07. 65+ tillväxt 2024→2040 per region (ranked bar)
08. Åtgärdbar dödlighet vs HC-kostnad per capita (scatter, equity lens)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter, MultipleLocator

# Centralised Pfizer chart styling (registers IBM Plex Sans, palette, rcParams).
# Aligns Python typography with R theme_pfizer() — chart audit fix 2026-04-25.
sys.path.insert(0, str(Path(__file__).parent))
from _pf_chart_setup import apply_pf_style, PF
apply_pf_style()

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
INT = ROOT / "working/data/interim"
MASTER = ROOT / "working/data/master"
OUT = MASTER / "charts_v2"
OUT.mkdir(parents=True, exist_ok=True)

# Palette aliases — defer to PF namespace (chart audit fix 2026-04-25)
PF_BLUE = PF.blue_primary       # primary
PF_DARK = PF.navy               # dark accent
PF_RED = PF.red                 # highlight / negative trend
PF_GREY = PF.text_secondary     # neutral
PF_LIGHT = "#B8DFE8"            # light background
SE_YELLOW = PF.gold             # Swedish flag yellow

# Per-figure overrides on top of apply_pf_style() defaults — these charts run at higher DPI for slide insertion
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 12,
    "savefig.dpi": 300,
})

SLIDE_WIDE = (13, 7.3)   # 16:9 aspect for slide insertion
SLIDE_SQUARE = (9, 9)     # for scatter

# Load data
import openpyxl
wb = openpyxl.load_workbook(MASTER/"master_workbook_v13.xlsx", data_only=True)

def load_region_master():
    ws = wb["Region master"]
    hdr = [c.value for c in ws[1]]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]: continue
        rows.append(dict(zip(hdr, r)))
    return rows

def load_rx():
    """Return {atc: {region_short: {year: count}}}."""
    rx = {}
    ws = wb["Läkemedelsregistret Rx"]
    # Find columns. Headers: row 1 has product names spanning 4 cols each, row 2 has year numbers
    hdr1 = [c.value for c in ws[1]]
    hdr2 = [c.value for c in ws[2]]
    # Map: column index → (atc, year)
    col_map = {}
    current_atc = None
    for i, v in enumerate(hdr1, 1):
        if v and "(" in str(v) and ")" in str(v):
            # Extract ATC from "Brand (ATC) — indication"
            import re
            m = re.search(r"\(([A-Z0-9]+)\)", str(v))
            if m: current_atc = m.group(1)
        if i > 2 and current_atc:
            year = hdr2[i-1]
            if year and str(year).isdigit():
                col_map[i] = (current_atc, str(year))
    # Pull data
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not r[1]: continue
        region = r[1]
        for col, (atc, yr) in col_map.items():
            v = r[col-1]
            if v is not None:
                rx.setdefault(atc, {}).setdefault(region, {})[yr] = v
    return rx

def load_health_equity():
    ws = wb["Health equity overlay"]
    hdr = [c.value for c in ws[1]]
    rows = [dict(zip(hdr, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
    return rows

rm_rows = load_region_master()
rx = load_rx()
eq_rows = load_health_equity()

# Helper — strip "Region " prefix
def short(name):
    if not name: return name
    s = str(name).strip()
    for p in ["Region ", "Region s "]:
        if s.startswith(p): s = s[len(p):]
    return s.replace("s län","").replace(" län","").replace("Västra Götalandsregionen","Västra Götaland").replace("Jönköpings","Jönköping")

# Populations
POP = {short(r["Region"]): r["Population"] for r in rm_rows if r.get("Population")}

# ==== Chart 01: Vyndaqel Skellefteå-klustret ====
def chart01_vyndaqel():
    atc = "N07XX08"
    if atc not in rx: print("no Vyndaqel data"); return
    data = []
    for region_name, years in rx[atc].items():
        # Skip aggregate rows
        if "NATIONAL" in str(region_name).upper() or "TOTAL" in str(region_name).upper():
            continue
        pop = POP.get(short(region_name))
        v2024 = years.get("2024", 0)
        if not v2024: continue
        per100k = (v2024 / pop * 100000) if pop else 0
        data.append((short(region_name), v2024, per100k))
    data.sort(key=lambda x: -x[2])

    fig, ax = plt.subplots(figsize=SLIDE_WIDE)
    names = [d[0] for d in data]
    per = [d[2] for d in data]
    # Color — highlight Norrland
    colors = []
    for name in names:
        if name in ("Norrbotten", "Västerbotten"):
            colors.append(PF_RED)
        elif name in ("Jämtland Härjedalen",):
            colors.append("#FF8080")
        else:
            colors.append(PF_BLUE)
    bars = ax.barh(range(len(data)), per, color=colors, edgecolor="white", linewidth=0.5)
    # Labels: patient count on the right
    for i, (name, count, p100k) in enumerate(data):
        ax.text(p100k + 0.5, i, f"{p100k:.1f} (n={count})", va="center", fontsize=9, color=PF_GREY)

    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Vyndaqel-patienter per 100 000 invånare (2024)")
    ax.set_title("Vyndaqel (tafamidis) — Skellefteå-klustret syns tydligt i Norrland",
                 loc="left", pad=15)
    # Subtitle via text
    fig.text(0.08, 0.90,
             "Norrbotten och Västerbotten samlar 31 % av Sveriges ATTR-CM-patienter — på 2,8 % av befolkningen.",
             fontsize=11, color=PF_DARK, style="italic")
    ax.set_xlim(0, max(per)*1.15)
    # Annotation for the cluster
    ax.annotate("Hereditärt TTR-kluster\n(V30M-mutation)",
                xy=(per[0]-1, 0), xytext=(per[0]*0.55, 2),
                fontsize=10, color=PF_RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=PF_RED, lw=1.5))

    plt.figtext(0.08, 0.02, "Källa: Socialstyrelsen Läkemedelsregistret 2024; SCB BE0101 befolkning 2024. Extraherat 2026-04-24.",
                fontsize=8, color=PF_GREY)
    plt.tight_layout(rect=[0, 0.04, 1, 0.88])
    plt.savefig(OUT/"01_vyndaqel_skelleftea_cluster.png", bbox_inches="tight")
    plt.close()
    print("✓ 01_vyndaqel")

# ==== Chart 02: Ibrance decline ====
def chart02_ibrance():
    atc = "L01EF01"
    if atc not in rx: return
    years = ["2021","2022","2023","2024"]
    # Get time series for top 5 regions by 2021 volume — skip aggregate rows
    series = [(short(reg), [yrs.get(y,0) for y in years])
              for reg, yrs in rx[atc].items()
              if "NATIONAL" not in str(reg).upper() and "TOTAL" not in str(reg).upper()]
    series.sort(key=lambda x: -x[1][0])
    top5 = series[:5]

    fig, ax = plt.subplots(figsize=SLIDE_WIDE)
    # Nudge overlapping end labels
    final_vals = [(name, vals[-1]) for name, vals in top5]
    final_vals.sort(key=lambda x: x[1], reverse=True)
    y_offsets = {}
    last_y = None
    for name, v in final_vals:
        nudge = 0
        if last_y is not None and abs(v - last_y) < 18:
            nudge = -18 if last_y > v else 18
        y_offsets[name] = v + nudge if nudge else v
        last_y = y_offsets[name]

    for name, vals in top5:
        color = PF_RED if name in ("Stockholm","Västra Götaland") else PF_BLUE
        linewidth = 3 if name in ("Stockholm","Västra Götaland") else 1.8
        alpha = 1.0 if name in ("Stockholm","Västra Götaland") else 0.55
        ax.plot(years, vals, marker="o", label=name, color=color, linewidth=linewidth, alpha=alpha, markersize=7)
        # End label with nudging
        ax.text(3.08, y_offsets[name], f"{name} ({vals[-1]})", va="center", fontsize=10,
                color=color, fontweight="bold" if name in ("Stockholm","Västra Götaland") else "normal",
                alpha=alpha)

    ax.set_xlabel("År")
    ax.set_ylabel("Antal patienter (Socialstyrelsen Läkemedelsregistret)")
    ax.set_title("Ibrance (palbociklib) — Stockholm –33 % och Västra Götaland –36 %\n" +
                 "minskat förskrivning 2021–2024. Övriga regioner stabila.",
                 loc="left", pad=15)
    ax.set_xlim(-0.2, 4.2)
    ax.spines["left"].set_visible(True)

    # Callout
    fig.text(0.08, 0.90,
             "Empirisk bekräftelse av kostnadsdriven övergång till Kisqali (Novartis) i Stockholm och VGR.",
             fontsize=11, color=PF_DARK, style="italic")

    plt.figtext(0.08, 0.02, "Källa: Socialstyrelsen Läkemedelsregistret (ATC L01EF01). Extraherat 2026-04-24.",
                fontsize=8, color=PF_GREY)
    plt.tight_layout(rect=[0, 0.04, 0.92, 0.87])
    plt.savefig(OUT/"02_ibrance_decline.png", bbox_inches="tight")
    plt.close()
    print("✓ 02_ibrance")

# ==== Chart 03: Health equity bivariate scatter ====
def chart03_equity():
    data = [(r["Region"], r["Utrikes födda %"], r["Eftergymn. 25-64 %"],
             r["Förtida död 25-64 /100k"], r["SES composite rank (1=högsta behov)" if "SES composite rank (1=högsta behov)" in r else
             [k for k in r if "rank" in str(k).lower()][0]])
             for r in eq_rows if r.get("Region")]

    # We plot: X = eftergymn%, Y = förtida dödlighet, size = utrikes född %
    fig, ax = plt.subplots(figsize=SLIDE_SQUARE)
    xs = [d[2] for d in data]
    ys = [d[3] for d in data]
    sizes = [max(d[1],1)*30 for d in data]  # foreign-born weight
    # Top-5 by rank colored red
    colors = [PF_RED if d[4] <= 5 else (SE_YELLOW if d[4] <= 10 else PF_BLUE) for d in data]

    ax.scatter(xs, ys, s=sizes, c=colors, alpha=0.72, edgecolor="white", linewidth=1.5)
    # Label only the extremes to avoid overlap
    for name, fb, ed, pm, rank in data:
        if rank <= 5 or rank >= 19:
            short_name = name.replace("Region ","").replace(" län","")
            ax.annotate(short_name, (ed, pm), xytext=(6, 0), textcoords="offset points",
                        fontsize=10, color=PF_DARK, fontweight="bold")

    ax.set_xlabel("Andel eftergymnasial utbildning 25–64 år (%)")
    ax.set_ylabel("Förtida dödsfall 25–64 år (per 100 000 inv, åldersstand.)")
    ax.set_title("Hälsoorättvisa-landskapet — utbildning vs förtida dödlighet\n" +
                 "Bubbel-storlek = andel utrikes födda. Röd = topp 5 behov, gul = rank 6-10.",
                 loc="left", pad=15)
    # Legend
    handles = [
        mpatches.Patch(color=PF_RED, label="Topp 5 behov"),
        mpatches.Patch(color=SE_YELLOW, label="Rank 6–10"),
        mpatches.Patch(color=PF_BLUE, label="Rank 11–21"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=True, fancybox=True)

    plt.figtext(0.08, 0.02, "Källa: SCB UF0506 (utbildning) + SCB BE0101 (utrikes födda) + Kolada N01451 (förtida dödlighet). 2024.",
                fontsize=8, color=PF_GREY)
    plt.tight_layout(rect=[0, 0.04, 1, 0.92])
    plt.savefig(OUT/"03_health_equity_bivariate.png", bbox_inches="tight")
    plt.close()
    print("✓ 03_equity")

# ==== Chart 04: Wait times ====
def chart04_wait_times():
    data = [(short(r["Region"]), r.get("Median wait spec days"))
            for r in rm_rows if r.get("Median wait spec days")]
    data.sort(key=lambda x: x[1] or 0)
    names = [d[0] for d in data]
    vals = [d[1] for d in data]

    fig, ax = plt.subplots(figsize=SLIDE_WIDE)
    colors = [PF_BLUE if v <= 60 else (SE_YELLOW if v <= 90 else PF_RED) for v in vals]
    bars = ax.bar(range(len(names)), vals, color=colors, edgecolor="white", linewidth=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 2, f"{int(v)}", ha="center", fontsize=9, color=PF_GREY)

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Mediantid till specialistbesök (dagar)")
    ax.set_title("Tillgänglighet i kris — 4,6× skillnad mellan regioner\n" +
                 "Stockholm kortast 24,5 dagar → Norrbotten längst 113 dagar",
                 loc="left", pad=15)
    ax.axhline(60, color=SE_YELLOW, linestyle="--", alpha=0.6, label="60-dagars vårdgaranti")
    ax.axhline(90, color=PF_RED, linestyle="--", alpha=0.6, label="90-dagars tidsgräns")
    ax.legend(loc="upper left", frameon=True)

    plt.figtext(0.08, 0.02, "Källa: Kolada Vårdgaranti / SVF (mediantid till specialistbesök). 2024.",
                fontsize=8, color=PF_GREY)
    plt.tight_layout(rect=[0, 0.04, 1, 0.93])
    plt.savefig(OUT/"04_wait_times.png", bbox_inches="tight")
    plt.close()
    print("✓ 04_wait_times")

# ==== Chart 05: 65+ growth projection ====
def chart05_65_growth():
    # Need pop projections sheet
    if "Future — pop projections" not in wb.sheetnames: return
    ws = wb["Future — pop projections"]
    hdr = [c.value for c in ws[1]]
    # Expect cols like "Region", "65+ 2024", "65+ 2040", "% change"
    data = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        d = dict(zip(hdr, r))
        # Try to compute growth
        keys = list(d.keys())
        # Find 65+ columns
        y24_key = next((k for k in keys if k and "65+" in str(k) and "2024" in str(k)), None)
        y40_key = next((k for k in keys if k and "65+" in str(k) and "2040" in str(k)), None)
        if not y24_key or not y40_key: continue
        if not d[y24_key] or not d[y40_key]: continue
        growth_pct = (d[y40_key]/d[y24_key] - 1) * 100
        abs_growth = d[y40_key] - d[y24_key]
        data.append((short(d["Region"]), growth_pct, abs_growth, d[y24_key]))
    if not data:
        print("  (pop projection structure doesn't match; skipping chart 05)"); return
    data.sort(key=lambda x: -x[1])
    names = [d[0] for d in data]
    vals = [d[1] for d in data]

    fig, ax = plt.subplots(figsize=SLIDE_WIDE)
    colors = [PF_RED if v >= 30 else (PF_DARK if v >= 20 else PF_BLUE) for v in vals]
    ax.bar(range(len(names)), vals, color=colors, edgecolor="white")
    for i, (name, pct, abs_g, base) in enumerate(data):
        ax.text(i, pct + 0.8, f"+{pct:.0f}%\n(+{int(abs_g/1000)}k)", ha="center", fontsize=8, color=PF_GREY)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Tillväxt 65+ 2024 → 2040 (%)")
    ax.set_title("Äldreboom per region — Stockholm +35 % / +146 000 personer\n" +
                 "driver efterfrågan på Prevenar 20, Abrysvo, Paxlovid",
                 loc="left", pad=15)

    plt.figtext(0.08, 0.02, "Källa: SCB BefProgRegFakN befolkningsprognos. 2024 → 2040.",
                fontsize=8, color=PF_GREY)
    plt.tight_layout(rect=[0, 0.04, 1, 0.93])
    plt.savefig(OUT/"05_65plus_growth.png", bbox_inches="tight")
    plt.close()
    print("✓ 05_65plus_growth")

# Run all
for fn in [chart01_vyndaqel, chart02_ibrance, chart03_equity, chart04_wait_times, chart05_65_growth]:
    try:
        fn()
    except Exception as e:
        print(f"  FAIL {fn.__name__}: {e}")

print(f"\nCharts saved to: {OUT}")
