# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""
W1 EXTENSION — Per-region CDK4/6 class-naive capture.

The W1 headline "Pfizer captures 7% of class-naive CDK4/6 starts" is national.
Disaggregating to the 21 regions answers: where is Pfizer doing better/worse
than the 7% national rate? Which regions should P2 prioritise for engagement?

OUTPUT:
  delivery/figures/F19_cdk46_per_region_class_naive_capture.png
  delivery/figures/F20_cdk46_per_region_pwd_share.png
"""

from pathlib import Path
import sys
import pyreadr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 220)

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
AVA = ROOT / "AVA data for mapping 2026-05-02"
FIG = ROOT / "delivery" / "figures"
INTERIM = ROOT / "working" / "data" / "interim"

COLOR = {"Ibrance": "#0093D0", "Kisqali": "#E03C31", "Verzenios": "#7B2D8E"}

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.family": "DejaVu Sans",
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

# Load AVA
result = pyreadr.read_r(str(AVA / "Ibrance" / "IncPrevData.RDS"))
df = list(result.values())[0]
df["date"] = pd.to_datetime(df["date"].astype(str))

# Last-6 window
LAST6_END = df["date"].max()
LAST6_START = LAST6_END - pd.DateOffset(months=5)
print(f"Last-6 window: {LAST6_START.date()} → {LAST6_END.date()}")

# Filter to last-6 + 21 regions (exclude Sweden national)
last6 = df[(df["date"] >= LAST6_START) & (df["date"] <= LAST6_END) &
           (df["region"] != "Sweden")].copy()


# ---------------------------------------------------------------------------
# Class-naive starts per region per drug (last 6mo total)
# ---------------------------------------------------------------------------
naive = (last6[last6["analysis"] == "New CDK4/6 user"]
         .groupby(["region", "drug"])["n"].sum().unstack(fill_value=0))
naive["Total"] = naive.sum(axis=1)
naive["Ibrance_share"] = naive["Ibrance"] / naive["Total"] * 100
naive["Kisqali_share"] = naive["Kisqali"] / naive["Total"] * 100
naive["Verzenios_share"] = naive["Verzenios"] / naive["Total"] * 100

# Sort by total volume to surface the regions where the share matters most
naive_sorted = naive.sort_values("Total", ascending=False)
print("\nClass-naive starts per region (last 6mo Aug 2025–Jan 2026):")
print(naive_sorted.to_string(float_format="%.1f"))

# National share for reference (sum across regions)
nat_total = naive[["Ibrance", "Kisqali", "Verzenios"]].sum().sum()
nat_ibr = naive["Ibrance"].sum() / nat_total * 100
nat_kis = naive["Kisqali"].sum() / nat_total * 100
nat_ver = naive["Verzenios"].sum() / nat_total * 100
print(f"\nNational shares (sum of 21 regions):")
print(f"  Ibrance:   {nat_ibr:.1f}%   ({naive['Ibrance'].sum():.0f})")
print(f"  Kisqali:   {nat_kis:.1f}%   ({naive['Kisqali'].sum():.0f})")
print(f"  Verzenios: {nat_ver:.1f}%   ({naive['Verzenios'].sum():.0f})")
print(f"  Total class-naive (sum of regions): {nat_total:.0f}")

# Identify regions where Pfizer (Ibrance) over- or under-indexes vs 7% national
naive["Ibrance_index_vs_national"] = naive["Ibrance_share"] / nat_ibr * 100
print("\nRegions ranked by Ibrance class-naive share (last 6mo):")
ranked = naive[["Total", "Ibrance", "Ibrance_share", "Ibrance_index_vs_national"]].sort_values(
    "Ibrance_share", ascending=False)
print(ranked.to_string(float_format="%.1f"))


# ---------------------------------------------------------------------------
# Per-region PWD share (already used as Sweden in W1; here per region)
# ---------------------------------------------------------------------------
pwd = (last6[last6["analysis"] == "Patients with dispensations"]
       .groupby(["region", "drug"])["n"].sum().unstack(fill_value=0))
pwd["Total"] = pwd.sum(axis=1)
pwd["Ibrance_share"] = pwd["Ibrance"] / pwd["Total"] * 100
pwd["Kisqali_share"] = pwd["Kisqali"] / pwd["Total"] * 100
pwd["Verzenios_share"] = pwd["Verzenios"] / pwd["Total"] * 100
pwd_sorted = pwd.sort_values("Total", ascending=False)
print("\nPWD share per region (last 6mo, all 21 regions):")
print(pwd_sorted.to_string(float_format="%.1f"))


# ---------------------------------------------------------------------------
# FIGURE F19 — Per-region class-naive capture (the "where is Ibrance failing" map)
# ---------------------------------------------------------------------------
print("\nRendering F19…")
# Filter to regions with meaningful volume (Total >= 10 class-naive starts last-6)
sig = naive[naive["Total"] >= 10].sort_values("Total", ascending=True).copy()
print(f"  Regions with ≥10 class-naive starts last-6: {len(sig)}/21")

fig, ax = plt.subplots(figsize=(11, 8))
y = np.arange(len(sig))

# Stacked bars — each segment = absolute count, label = share
ibr_vals = sig["Ibrance"].values
kis_vals = sig["Kisqali"].values
ver_vals = sig["Verzenios"].values

ax.barh(y, ibr_vals, color=COLOR["Ibrance"], label="Ibrance (Pfizer)")
ax.barh(y, kis_vals, left=ibr_vals, color=COLOR["Kisqali"], label="Kisqali")
ax.barh(y, ver_vals, left=ibr_vals + kis_vals, color=COLOR["Verzenios"], label="Verzenios")

# Annotate Ibrance % per row
for i, (region, row) in enumerate(sig.iterrows()):
    # Ibrance label on its segment if wide enough, otherwise to the right
    ibr_pct = row["Ibrance_share"]
    if row["Ibrance"] >= 5:
        ax.text(row["Ibrance"] / 2, i, f"{ibr_pct:.0f}%", ha="center", va="center",
                fontsize=8, color="white", fontweight="bold")
    else:
        ax.text(row["Ibrance"] + 1, i, f"{ibr_pct:.0f}%", ha="left", va="center",
                fontsize=8, color=COLOR["Ibrance"], fontweight="bold")
    # Total to the right of the bar
    ax.text(row["Total"] + 3, i, f"  n={int(row['Total'])}",
            ha="left", va="center", fontsize=8, color="dimgray")

ax.set_yticks(y)
ax.set_yticklabels(sig.index, fontsize=9)
ax.set_xlabel("Class-naive CDK4/6 starts (last 6 months, count of patients)")
ax.set_title(f"F19 — Where is Pfizer winning class-naive CDK4/6 starts? "
              f"(National avg: Ibrance {nat_ibr:.1f}%, Kisqali {nat_kis:.1f}%, Verzenios {nat_ver:.1f}%)\n"
              f"Per-region disaggregation of the W1 headline; AVA last 6 months "
              f"({LAST6_START:%b %Y}–{LAST6_END:%b %Y})",
              fontsize=11, fontweight="bold")
ax.axvline(x=0, color="black", linewidth=0.5)
ax.legend(loc="lower right", fontsize=9)
ax.set_xlim(0, sig["Total"].max() * 1.18)
fig.tight_layout()
fig.savefig(FIG / "F19_cdk46_per_region_class_naive_capture.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F19_cdk46_per_region_class_naive_capture.png'}")


# ---------------------------------------------------------------------------
# FIGURE F20 — PWD share per region (the "stock market" view)
# ---------------------------------------------------------------------------
print("Rendering F20…")
sig2 = pwd[pwd["Total"] >= 30].sort_values("Total", ascending=True).copy()
print(f"  Regions with ≥30 PWD last-6: {len(sig2)}/21")

fig, ax = plt.subplots(figsize=(11, 8))
y = np.arange(len(sig2))

ibr = sig2["Ibrance"].values
kis = sig2["Kisqali"].values
ver = sig2["Verzenios"].values

ax.barh(y, ibr, color=COLOR["Ibrance"], label="Ibrance")
ax.barh(y, kis, left=ibr, color=COLOR["Kisqali"], label="Kisqali")
ax.barh(y, ver, left=ibr + kis, color=COLOR["Verzenios"], label="Verzenios")

for i, (region, row) in enumerate(sig2.iterrows()):
    ibr_pct = row["Ibrance_share"]
    if row["Ibrance"] >= 30:
        ax.text(row["Ibrance"] / 2, i, f"{ibr_pct:.0f}%", ha="center", va="center",
                fontsize=8, color="white", fontweight="bold")
    ax.text(row["Total"] + 8, i, f"  n={int(row['Total'])}",
            ha="left", va="center", fontsize=8, color="dimgray")

# National avg lines
nat_ibr_pwd = pwd["Ibrance"].sum() / pwd["Total"].sum() * 100
nat_kis_pwd = pwd["Kisqali"].sum() / pwd["Total"].sum() * 100
nat_ver_pwd = pwd["Verzenios"].sum() / pwd["Total"].sum() * 100

ax.set_yticks(y)
ax.set_yticklabels(sig2.index, fontsize=9)
ax.set_xlabel("Patients with dispensations (last 6 months sum)")
ax.set_title(f"F20 — CDK4/6 PWD share per region (last 6 months)\n"
              f"National PWD shares: Ibrance {nat_ibr_pwd:.0f}%, Kisqali {nat_kis_pwd:.0f}%, "
              f"Verzenios {nat_ver_pwd:.0f}%",
              fontsize=11, fontweight="bold")
ax.legend(loc="lower right", fontsize=9)
ax.set_xlim(0, sig2["Total"].max() * 1.15)
fig.tight_layout()
fig.savefig(FIG / "F20_cdk46_per_region_pwd_share.png", bbox_inches="tight")
plt.close(fig)
print(f"  ✓ {FIG / 'F20_cdk46_per_region_pwd_share.png'}")


# Persist
naive.to_csv(INTERIM / "ava_w1b_cdk46_class_naive_per_region.csv")
pwd.to_csv(INTERIM / "ava_w1b_cdk46_pwd_per_region.csv")
print(f"\n  Tables: {INTERIM}/ava_w1b_*.csv")
print("\nDone.")
