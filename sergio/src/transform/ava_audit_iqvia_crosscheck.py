# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
AVA × IQVIA cross-validation:
  1. Compute Vydura's true share of TOTAL migraine market (replaces W3 5–15% guess)
  2. Compute Vydura's share of preventive-only segment (gepants + injectable mAbs)
  3. Cross-check AVA Vydura PWD trend vs IQVIA Vydura units trend (consistency)
  4. Same exercise for ATTR — Vyndaqel share of total ATTR market
  5. Render F17 (market context) + F17b (trend agreement)
"""

from pathlib import Path
import sys
import pyreadr
import openpyxl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 220)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
WB = ROOT / "delivery" / "06_master_workbook_v29.xlsx"
FIG = ROOT / "delivery" / "figures"
INTERIM = ROOT / "working" / "data" / "interim"

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


# ---------------------------------------------------------------------------
# Load IQVIA RD-IM
# ---------------------------------------------------------------------------
print("Loading IQVIA RD-IM detail…")
wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
ws = wb["RD-IM IQVIA detail"]
data = list(ws.values)
hdr = data[0]
iqvia = pd.DataFrame(data[1:], columns=hdr)
wb.close()

# Parse date columns
date_cols_sek = [c for c in iqvia.columns if str(c).startswith("SEK ")]
date_cols_units = [c for c in iqvia.columns if str(c).startswith("Units ")]
print(f"  rows: {len(iqvia):,}")
print(f"  SEK date cols: {len(date_cols_sek)}; Units date cols: {len(date_cols_units)}")
print(f"  date range: {date_cols_sek[0]} → {date_cols_sek[-1]}")

# Helper: parse "SEK Apr 2023" → datetime. AVA uses mid-month (-15), so align IQVIA to -15 too.
def parse_col(c: str) -> pd.Timestamp:
    parts = str(c).split()
    if len(parts) >= 3:
        return pd.to_datetime(f"{parts[1]} 15, {parts[2]}")
    return pd.NaT

date_map_sek = {c: parse_col(c) for c in date_cols_sek}
date_map_units = {c: parse_col(c) for c in date_cols_units}

# Last-6 window: Oct 2025 – Mar 2026 (matches AVA W2/W3 windows)
LAST6_END = pd.Timestamp("2026-03-15")
LAST6_START = pd.Timestamp("2025-10-15")
last6_sek_cols = [c for c, d in date_map_sek.items() if LAST6_START <= d <= LAST6_END]
last6_units_cols = [c for c, d in date_map_units.items() if LAST6_START <= d <= LAST6_END]
print(f"  last-6 SEK cols ({len(last6_sek_cols)}): {last6_sek_cols}")


# ---------------------------------------------------------------------------
# (1) Migraine market context — Sweden total, last 6 mo
# ---------------------------------------------------------------------------
print("\n=== (1) MIGRAINE — Vydura's share of total market ===")
mig = iqvia[iqvia["Therapy area"] == "Migraine"].copy()
# Coerce numeric — IQVIA cells may be None or strings
for c in last6_sek_cols + last6_units_cols:
    mig[c] = pd.to_numeric(mig[c], errors="coerce").fillna(0)

# Aggregate to Sweden total per product (sum across regions)
mig["last6_sek"] = mig[last6_sek_cols].sum(axis=1)
mig["last6_units"] = mig[last6_units_cols].sum(axis=1)
prod_swe = (mig.groupby(["Product", "ATC", "Manufacturer"], as_index=False)
            [["last6_sek", "last6_units"]].sum())

# Classify segments
def segment(atc: str) -> str:
    a = str(atc).upper()
    if a.startswith("N02CD"):  # CGRP-targeted
        if a == "N02CD06 RIMEGEPANT" or a == "N02CD07 ATOGEPANT":
            return "Oral gepant"
        return "Injectable CGRP mAb"
    if a.startswith("N02CC"):
        return "Triptan"
    return "Other"

prod_swe["segment"] = prod_swe["ATC"].apply(segment)

# Sums per segment
seg_sek = prod_swe.groupby("segment")["last6_sek"].sum()
seg_units = prod_swe.groupby("segment")["last6_units"].sum()
total_sek = seg_sek.sum()
total_units = seg_units.sum()
print("\n  Total migraine market (Sweden, last 6mo Oct 2025–Mar 2026):")
print(f"    SEK   total: {total_sek:>15,.0f}")
print(f"    Units total: {total_units:>15,.0f}")
print(f"\n  By segment (SEK):")
for seg in ["Oral gepant", "Injectable CGRP mAb", "Triptan", "Other"]:
    sek = seg_sek.get(seg, 0)
    print(f"    {seg:<22} {sek:>14,.0f}  ({sek/total_sek*100:>5.1f}%)")

# Vydura specifically
vyd_row = prod_swe[prod_swe["Product"] == "VYDURA"].iloc[0]
ato_row = prod_swe[prod_swe["Product"] == "AQUIPTA"].iloc[0]
print(f"\n  Vydura  (rimegepant) last-6 SEK: {vyd_row['last6_sek']:,.0f}; units: {vyd_row['last6_units']:,.0f}")
print(f"  Aquipta (atogepant)  last-6 SEK: {ato_row['last6_sek']:,.0f}; units: {ato_row['last6_units']:,.0f}")

# Share computations (SEK basis — most meaningful for "market position")
shares_sek = {
    "Vydura % of TOTAL migraine market":
        vyd_row["last6_sek"] / total_sek * 100,
    "Vydura % of CGRP-targeted (gepants + mAbs)":
        vyd_row["last6_sek"] / (seg_sek["Oral gepant"] + seg_sek["Injectable CGRP mAb"]) * 100,
    "Vydura % of ORAL GEPANT segment (within-class)":
        vyd_row["last6_sek"] / seg_sek["Oral gepant"] * 100,
    "Vydura % of MIGRAINE PREVENTION (CGRP-targeted)":
        vyd_row["last6_sek"] / (seg_sek["Oral gepant"] + seg_sek["Injectable CGRP mAb"]) * 100,
}
print("\n  Vydura shares (IQVIA SEK basis, Sweden last 6mo):")
for k, v in shares_sek.items():
    print(f"    {k:<55} {v:>5.1f}%")

# Aquipta within oral gepants
ato_share_oral = ato_row["last6_sek"] / seg_sek["Oral gepant"] * 100
print(f"    Aquipta % of ORAL GEPANT segment (IQVIA SEK):     {ato_share_oral:>5.1f}%  "
      f"(AVA PWD-based was 35.2%)")


# ---------------------------------------------------------------------------
# (2) AVA Vydura PWD trend vs IQVIA Vydura units trend (consistency check)
# ---------------------------------------------------------------------------
print("\n=== (2) AVA Vydura PWD vs IQVIA Vydura units — trend consistency ===")
# Load AVA Vydura monthly PWD
vyd_pre = list(pyreadr.read_r(str(AVA / "Vydura" / "region.RDS")).values())[0]
vyd_pre["month"] = pd.to_datetime(vyd_pre["month"].astype(str))
ava_vyd_swe = (vyd_pre[(vyd_pre["region"] == "Sweden") & (vyd_pre["drug"] == "Vydura")]
               .sort_values("month").rename(columns={"month": "date", "prevalens": "ava_pwd"}))

# IQVIA Vydura monthly units (Sweden = sum across regions)
vyd_iqvia_rows = mig[mig["Product"] == "VYDURA"]
iqvia_vyd_monthly = []
for c, d in date_map_units.items():
    val = pd.to_numeric(vyd_iqvia_rows[c], errors="coerce").fillna(0).sum()
    iqvia_vyd_monthly.append({"date": d, "iqvia_units": val})
iqvia_vyd = pd.DataFrame(iqvia_vyd_monthly).sort_values("date")

merged_vyd = ava_vyd_swe[["date", "ava_pwd"]].merge(iqvia_vyd, on="date", how="inner")
print(f"\n  Overlap months: {len(merged_vyd)}")
if len(merged_vyd):
    corr = merged_vyd["ava_pwd"].corr(merged_vyd["iqvia_units"])
    print(f"  Pearson correlation (Vydura AVA PWD vs IQVIA units): {corr:.3f}")
    # Ratio
    merged_vyd["units_per_patient"] = merged_vyd["iqvia_units"] / merged_vyd["ava_pwd"]
    print(f"  Units/patient ratio: mean {merged_vyd['units_per_patient'].mean():.2f}, "
          f"median {merged_vyd['units_per_patient'].median():.2f}, "
          f"std {merged_vyd['units_per_patient'].std():.2f}")
    print(merged_vyd.tail(8).to_string(index=False, float_format="%.1f"))


# ---------------------------------------------------------------------------
# (3) ATTR market — Vyndaqel share of total ATTR market
# ---------------------------------------------------------------------------
print("\n=== (3) ATTR — Vyndaqel's share of total market ===")
attr = iqvia[iqvia["Therapy area"] == "ATTR"].copy()
for c in last6_sek_cols + last6_units_cols:
    attr[c] = pd.to_numeric(attr[c], errors="coerce").fillna(0)
attr["last6_sek"] = attr[last6_sek_cols].sum(axis=1)
attr["last6_units"] = attr[last6_units_cols].sum(axis=1)
attr_swe = (attr.groupby(["Product", "ATC", "Manufacturer"], as_index=False)
            [["last6_sek", "last6_units"]].sum())
print("\n  ATTR products (Sweden last 6mo, IQVIA):")
print(attr_swe.sort_values("last6_sek", ascending=False).to_string(index=False, float_format="%.0f"))

attr_total_sek = attr_swe["last6_sek"].sum()
vyn_sek = attr_swe[attr_swe["Product"] == "VYNDAQEL"]["last6_sek"].iloc[0]
print(f"\n  Total ATTR SEK (last 6mo): {attr_total_sek:,.0f}")
print(f"  Vyndaqel share by SEK:     {vyn_sek/attr_total_sek*100:.1f}%")
print(f"  AVA prevalens share (DG3 ATTR-CM): 88.0% (Vyndaqel of CM-only)")
print(f"  AVA prevalens share (DG1+DG2 PN total): 54.8% (Vyndaqel of PN-only)")


# ---------------------------------------------------------------------------
# (4) AVA Vyndaqel ATTR-CM prevalens vs IQVIA Vyndaqel units (trend)
# ---------------------------------------------------------------------------
print("\n=== (4) AVA Vyndaqel CM prevalens vs IQVIA Vyndaqel units — trend ===")
vqa_a = list(pyreadr.read_r(str(AVA / "Vyndaquel" / "tab12a.RDS")).values())[0]
vqa_a["date"] = pd.to_datetime(vqa_a["date"].astype(str))
ava_vyn = vqa_a[(vqa_a["drug"] == "Vyndaqel") & (vqa_a["region"] == "Sweden") &
                 (vqa_a["grupp"] == "Diagnosgrupp 3") &
                 (vqa_a["analysis"] == "Prevalens rullande 3 månader")].sort_values("date")

# IQVIA Vyndaqel monthly Sweden units
iqvia_vyn_monthly = []
for c, d in date_map_units.items():
    val = pd.to_numeric(attr[attr["Product"] == "VYNDAQEL"][c], errors="coerce").fillna(0).sum()
    iqvia_vyn_monthly.append({"date": d, "iqvia_units": val})
iqvia_vyn = pd.DataFrame(iqvia_vyn_monthly).sort_values("date")

merged_vyn = ava_vyn[["date", "n"]].rename(columns={"n": "ava_cm_prevalens"}).merge(
    iqvia_vyn, on="date", how="inner")
if len(merged_vyn):
    corr = merged_vyn["ava_cm_prevalens"].corr(merged_vyn["iqvia_units"])
    print(f"  Overlap months: {len(merged_vyn)}")
    print(f"  Pearson correlation (Vyndaqel AVA CM-prevalens vs IQVIA units): {corr:.3f}")
    print(merged_vyn.tail(8).to_string(index=False, float_format="%.1f"))


# ---------------------------------------------------------------------------
# FIGURE F17 — Market context (replaces "5–15%" guess with measured numbers)
# ---------------------------------------------------------------------------
print("\nRendering F17 (Migraine market context)…")

# Build segment shares (SEK + Units)
seg_data = (prod_swe.groupby("segment")[["last6_sek", "last6_units"]]
            .sum().reindex(["Oral gepant", "Injectable CGRP mAb", "Triptan", "Other"]).fillna(0))
seg_data["sek_share"] = seg_data["last6_sek"] / seg_data["last6_sek"].sum() * 100
seg_data["units_share"] = seg_data["last6_units"] / seg_data["last6_units"].sum() * 100

# Vydura inside Oral gepant segment
vyd_in_gepant = vyd_row["last6_sek"] / seg_sek["Oral gepant"] * 100
ato_in_gepant = ato_row["last6_sek"] / seg_sek["Oral gepant"] * 100

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

# Panel A — Total migraine market by segment (SEK)
ax = axes[0]
colors = ["#0093D0", "#7B2D8E", "#888888", "#CCCCCC"]
ax.pie(seg_data["last6_sek"], labels=[f"{s}\n{seg_data.loc[s, 'sek_share']:.1f}%" for s in seg_data.index],
       colors=colors, startangle=90, autopct="", pctdistance=0.7)
ax.set_title(f"Total migraine market (IQVIA SEK)\nSweden last 6mo: {total_sek/1e6:.0f} MSEK")

# Panel B — Within preventive (CGRP-targeted) — gepants + mAbs
ax = axes[1]
prev_total_sek = seg_sek["Oral gepant"] + seg_sek["Injectable CGRP mAb"]
mab_share_in_prev = seg_sek["Injectable CGRP mAb"] / prev_total_sek * 100
gep_share_in_prev = seg_sek["Oral gepant"] / prev_total_sek * 100
vyd_in_prev = vyd_row["last6_sek"] / prev_total_sek * 100
ato_in_prev = ato_row["last6_sek"] / prev_total_sek * 100
prev_mab_sek = seg_sek["Injectable CGRP mAb"]
ax.pie([vyd_row["last6_sek"], ato_row["last6_sek"], prev_mab_sek],
       labels=[f"Vydura\n{vyd_in_prev:.1f}%", f"Aquipta\n{ato_in_prev:.1f}%",
                f"Injectable mAbs\n{mab_share_in_prev:.1f}%"],
       colors=["#0093D0", "#7B2D8E", "#888888"], startangle=90)
ax.set_title(f"Within CGRP-targeted prevention (IQVIA SEK)\n"
              f"Sweden last 6mo: {prev_total_sek/1e6:.0f} MSEK")

# Panel C — Vydura's share at three nesting levels
ax = axes[2]
levels = ["Within oral\ngepants", "Within CGRP-\ntargeted prev.", "Within total\nmigraine market"]
values = [vyd_in_gepant, vyd_in_prev, vyd_row["last6_sek"] / total_sek * 100]
bars = ax.bar(levels, values, color="#0093D0", edgecolor="dimgray")
for i, alpha in enumerate([1.0, 0.7, 0.4]):
    bars[i].set_alpha(alpha)
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, v + 1, f"{v:.1f}%", ha="center",
            fontsize=11, fontweight="bold")
ax.set_ylabel("Vydura share (% IQVIA SEK)")
ax.set_title("Vydura's market position — three nesting levels\n(IQVIA SEK basis, Sweden last 6mo)")
ax.set_ylim(0, max(values) * 1.2)

fig.suptitle("F17 — Vydura's market context: AVA × IQVIA cross-validation\n"
              "Replaces the W3 '5–15% of total migraine market' guess with measured IQVIA-based numbers",
              fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F17_vydura_market_context.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F17_vydura_market_context.png'}")


# ---------------------------------------------------------------------------
# FIGURE F17b — Trend consistency (AVA vs IQVIA)
# ---------------------------------------------------------------------------
print("Rendering F17b (trend consistency)…")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel A — Vydura trend agreement
ax = axes[0]
ax2 = ax.twinx()
ax.plot(merged_vyd["date"], merged_vyd["ava_pwd"], color="#0093D0", linewidth=2,
        label="AVA — Patients with dispensations (left axis)")
ax2.plot(merged_vyd["date"], merged_vyd["iqvia_units"], color="black", linewidth=1.5,
         linestyle="--", label="IQVIA — Sell-In units (right axis)")
ax.set_ylabel("AVA patients (PWD)", color="#0093D0")
ax2.set_ylabel("IQVIA units (Sell-In)")
ax.set_title(f"Vydura: AVA PWD vs IQVIA units (Sweden monthly)\n"
              f"Pearson r = {merged_vyd['ava_pwd'].corr(merged_vyd['iqvia_units']):.3f}",
              fontsize=10)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.tick_params(axis="x", labelsize=8)
ax.legend(loc="upper left", fontsize=8)
ax2.legend(loc="lower right", fontsize=8)

# Panel B — Vyndaqel trend agreement
ax = axes[1]
ax2 = ax.twinx()
ax.plot(merged_vyn["date"], merged_vyn["ava_cm_prevalens"], color="#0093D0", linewidth=2,
        label="AVA — DG3 (ATTR-CM) prevalens (left)")
ax2.plot(merged_vyn["date"], merged_vyn["iqvia_units"], color="black", linewidth=1.5,
         linestyle="--", label="IQVIA — Sell-In units (right)")
ax.set_ylabel("AVA CM prevalens (3mo rolling)", color="#0093D0")
ax2.set_ylabel("IQVIA units (Sell-In)")
ax.set_title(f"Vyndaqel: AVA CM prevalens vs IQVIA units (Sweden monthly)\n"
              f"Pearson r = {merged_vyn['ava_cm_prevalens'].corr(merged_vyn['iqvia_units']):.3f}",
              fontsize=10)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.tick_params(axis="x", labelsize=8)
ax.legend(loc="upper left", fontsize=8)
ax2.legend(loc="lower right", fontsize=8)

fig.suptitle("F17b — AVA × IQVIA trend consistency check\n"
              "Same product, two independent data sources — should move together",
              fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "F17b_ava_iqvia_trend_consistency.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F17b_ava_iqvia_trend_consistency.png'}")


# Persist
out_rows = []
for k, v in shares_sek.items():
    out_rows.append({"metric": k, "value_pct": v})
out_rows.extend([
    {"metric": "Total migraine SEK Sweden last-6 (MSEK)", "value_pct": total_sek / 1e6},
    {"metric": "Total ATTR SEK Sweden last-6 (MSEK)", "value_pct": attr_total_sek / 1e6},
    {"metric": "Vyndaqel share of total ATTR (IQVIA SEK)", "value_pct": vyn_sek/attr_total_sek*100},
    {"metric": "Pearson r — Vydura AVA PWD vs IQVIA units",
     "value_pct": merged_vyd["ava_pwd"].corr(merged_vyd["iqvia_units"])},
    {"metric": "Pearson r — Vyndaqel AVA CM-prevalens vs IQVIA units",
     "value_pct": merged_vyn["ava_cm_prevalens"].corr(merged_vyn["iqvia_units"])},
])
pd.DataFrame(out_rows).to_csv(INTERIM / "ava_audit_iqvia_crosscheck.csv", index=False)
print(f"\n  Tables: {INTERIM}/ava_audit_iqvia_crosscheck.csv")
print("\nDone.")
