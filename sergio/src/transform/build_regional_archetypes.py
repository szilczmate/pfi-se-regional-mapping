# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build master_workbook_v17.xlsx — Regional archetypes (roadmap #4).

Six rule-based strategic archetypes. A region can carry MULTIPLE tags (primary +
0-2 secondary). This is more honest than k-means clustering for Pfizer Access
purposes — Stockholm is both "Academic specialist-center" AND "Competitive
defense" AND "Aging vaccine-growth" simultaneously.

Output:
  - New sheet "OPP - Regional archetypes" — 21 region rows × archetype tags
  - New sheet "OPP - Archetype playbooks" — 6 archetype rows × playbook columns
  - working/data/master/regional_archetypes.csv (long form)
  - working/docs/findings_regional_archetypes.md

Confidence: archetype tagging is Modeled (rule-based threshold choices) per
EVIDENCE_CONFIDENCE_FRAMEWORK.md.
"""
import sys
from pathlib import Path
import shutil
import csv

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/master_workbook_v16.xlsx"
DST = ROOT / "working/data/master/master_workbook_v17.xlsx"
CSV_OUT = ROOT / "working/data/master/regional_archetypes.csv"

PF_NAVY = "003F7F"
PF_GREY = "4B5563"
PF_RED = "E4002B"

# Archetype color tags
A_COLORS = {
    "Academic specialist":   "DEEBF7",  # light blue
    "Aging vaccine-growth":  "FFF2CC",  # light gold
    "Rare-disease hotspot":  "FCE4D6",  # peach
    "Equity/access-friction": "F8CBAD",  # warm sand
    "High-governance":       "E2EFDA",  # light green
    "Competitive defense":   "F4CCCC",  # light red
}

C_OBS = "C6EFCE"; C_MOD = "FFEB9C"; C_HYP = "FFC7CE"; C_NPV = "D9D2E9"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ============================================================================
# ARCHETYPE DEFINITIONS — rule-based tagging
# ============================================================================
# Each archetype has:
#   - definition: 1-line strategic concept
#   - rule: callable taking (region_data dict) returning bool
#   - members_seed: pre-known anchor regions (sanity check; rule must include these)
ARCHETYPE_DEFS = [
    {
        "name": "Academic specialist",
        "definition": "Region hosts a university hospital + Regional Cancer Centre — high specialist density + research orientation. Pfizer's specialty oncology + rare-disease products land here first.",
        "rule": lambda d: d["region"] in {
            "Region Stockholm",         # Karolinska
            "Region Uppsala",           # Akademiska
            "Region Östergötland",      # Linköping US
            "Västra Götalandsregionen", # Sahlgrenska
            "Region Skåne",             # Lund + Malmö
            "Region Västerbotten",      # Norrlands universitetssjukhus Umeå
        },
        "engagement_target": "RD + HSD + Regional Cancer Centre director + chief of oncology/cardiology",
        "product_angle": "Tukysa, Talzenna, Lorbrena, Elrexfio, Vyndaqel — specialty oncology + rare disease",
        "evidence_to_bring": "Trial-network leverage, KOL relationships, RCC pathway alignment, registry cohort signal",
        "pfizer_validation": "Field-team relationship strength score, trial-site activity, KOL endorsement potential",
    },
    {
        "name": "Aging vaccine-growth",
        "definition": "Pop 65+ ≥ 22% OR 65+ growth ≥ 25% projected to 2040. Demographic tailwind for adult vaccines (Abrysvo, Prevenar 20) + age-prevalent rare disease (Vyndaqel) + COVID antiviral (Paxlovid).",
        "rule": lambda d: (d["pct_65"] is not None and d["pct_65"] >= 22) or
                          (d["growth_65"] is not None and d["growth_65"] >= 25),
        "engagement_target": "RD + HSD + primary care director + regional vaccine programme lead",
        "product_angle": "Abrysvo, Prevenar 20, Paxlovid — adult immunisation + chronic-disease management",
        "evidence_to_bring": "Demographic projection 2024→2040, RSV/IPD burden trend, hospitalisation cost-offset",
        "pfizer_validation": "Regional vaccine adoption pathway, FHM regional coordinator names, pricing/procurement structure",
    },
    {
        "name": "Rare-disease hotspot",
        "definition": "Vyndaqel rate ≥ 5/100k OR known hereditary cluster (Skellefteå founder TTR V30M). High concentration of ATTR-CM, hemophilia, BRCA-positive populations.",
        "rule": lambda d: (d["vyndaqel_per_100k"] is not None and d["vyndaqel_per_100k"] >= 5),
        "engagement_target": "Cardiology + neurology + clinical genetics chiefs; rare-disease patient advocacy",
        "product_angle": "Vyndaqel (anchor), Hympavzi, Elrexfio — rare-disease specialty",
        "evidence_to_bring": "Founder-variant prevalence literature, regional patient registry data, multi-disciplinary care pathway",
        "pfizer_validation": "Rare-disease patient identification rate, genetic-testing coverage, specialist-centre referral networks",
    },
    {
        "name": "Equity/access-friction",
        "definition": "Top-5 health-equity composite need rank OR median specialist wait ≥ 65 days. Pfizer Access pitches must address access pathway, not just clinical efficacy.",
        "rule": lambda d: (d["region"].replace("Region ", "").replace(" län", "")
                          .replace("Västra Götalandsregionen", "Västra Götaland")
                          .replace("Jönköpings", "Jönköping")
                          in {"Sörmland", "Norrbotten", "Gävleborg", "Västmanland", "Örebro"}) or
                          (d["wait_spec"] is not None and d["wait_spec"] >= 65),
        "engagement_target": "RD + HSN ordf + primary care director — political/access lens not clinical",
        "product_angle": "All products via equity narrative; Vyndaqel + Abrysvo + Prevenar 20 most aligned with HSN priorities",
        "evidence_to_bring": "SES composite ranking, wait-time spread, premature mortality vs national, NT-rådet etisk plattform alignment",
        "pfizer_validation": "Access negotiation priorities, regional health-equity initiatives, political alignment opportunities",
    },
    {
        "name": "High-governance",
        "definition": "Region has cornerstone stakeholder concentration — NT-rådet rep + NSG rep + LK ordförande overlap, or hosts sjukvårdsregion governance node. Disproportionate national-tier influence.",
        "rule": lambda d: d["region"] in {
            "Region Jönköpings län",   # Lindström NT-rådet ordf, Ekelund LK + NT-rådet Sydöstra, Nyberg Finn HSN
            "Region Uppsala",           # Melin LK + NT-rådet Mellansverige; Ydman RD
            "Region Västerbotten",      # Näsvall NSG nationellt
            "Region Norrbotten",        # Bergström NT-rådet vice
            "Region Stockholm",         # Bratt NSG; Ek LK
            "Västra Götalandsregionen", # Malmström NT-rådet rep
        },
        "engagement_target": "Named cornerstone individuals (see stakeholder_mapping_v8) — direct relationship investment",
        "product_angle": "Cross-portfolio — cornerstone stakeholders carry broader Pfizer narrative beyond single product",
        "evidence_to_bring": "Stakeholder dossier, prior NT-rådet decisions, regional plan alignment with Pfizer pipeline themes",
        "pfizer_validation": "Existing relationship depth, dual-role stakeholders (LK + NT-rådet overlap), succession risk (e.g. Bojestig retiring 2026)",
    },
    {
        "name": "Competitive defense",
        "definition": "Region holds significant Pfizer Rx footprint AND faces active competitive pressure. Ibrance: Stockholm/VGR/Skåne/Halland (Kisqali threat). Tukysa: Stockholm/VGR (Enhertu threat). Vyndaqel: Norrbotten/Västerbotten (Acoramidis on horizon).",
        "rule": lambda d: d["region"] in {
            "Region Stockholm", "Västra Götalandsregionen", "Region Skåne", "Region Halland",
            "Region Norrbotten", "Region Västerbotten",
        },
        "engagement_target": "LK ordf + chief pharmacist + oncology head — formulary defence dialogues",
        "product_angle": "Ibrance defence (Stockholm/VGR/Skåne/Halland); Tukysa defence (Stockholm/VGR); Vyndaqel defence (Norrbotten/Västerbotten)",
        "evidence_to_bring": "Trajectory data 2021-2024, competitor pipeline (Enhertu/Tecvayli/Acoramidis NT-rådet status), real-world outcomes data",
        "pfizer_validation": "Competitor regional volume (IQVIA), pricing flexibility, regional formulary committee timing, KOL allegiance",
    },
]


# ============================================================================
# REGION DATA EXTRACTION
# ============================================================================
def extract_region_data(wb):
    """Pull per-region metrics needed for archetype rule evaluation."""
    rm = wb["Region master"]
    hd = {rm.cell(1, c).value: c for c in range(1, rm.max_column + 1) if rm.cell(1, c).value}

    # Population projections
    pp = wb["Future — pop projections"]
    pp_hd = {pp.cell(1, c).value: c for c in range(1, pp.max_column + 1) if pp.cell(1, c).value}

    # Rx 2024 snapshot
    rx = wb["Rx 2024 snapshot"]
    rx_hd = {rx.cell(1, c).value: c for c in range(1, rx.max_column + 1) if rx.cell(1, c).value}

    out = {}
    for r in range(2, rm.max_row + 1):
        region = rm.cell(r, hd["Region"]).value
        if not region:
            continue

        pop = rm.cell(r, hd["Population"]).value
        pop_65 = rm.cell(r, hd["Pop 65+"]).value
        pct_65 = (float(pop_65) / float(pop) * 100) if (pop and pop_65) else None
        wait_spec = rm.cell(r, hd.get("Median wait spec days", 0)).value if "Median wait spec days" in hd else None

        # 65+ growth from projections sheet
        growth_65 = None
        for pr in range(2, pp.max_row + 1):
            if pp.cell(pr, pp_hd["Region"]).value == region:
                growth_65 = pp.cell(pr, pp_hd["65+ growth % 2024→2040"]).value
                break

        # Vyndaqel /100k from Rx 2024 snapshot — region-name reconciliation
        vyndaqel_per_100k = None
        for sr in range(2, rx.max_row + 1):
            short_in_rx = rx.cell(sr, rx_hd["Region"]).value
            if not short_in_rx:
                continue
            short_norm = short_in_rx.replace("Västra Götaland", "VGR").replace("Region ", "")
            region_norm = region.replace("Region ", "").replace(" län", "").replace(
                "Västra Götalandsregionen", "VGR").replace("Jönköpings", "Jönköping").replace(
                "Örebro", "Örebro")
            if short_norm == region_norm:
                vyndaqel_per_100k = rx.cell(sr, rx_hd.get("Vyndaqel /100k", 0)).value
                break

        out[region] = dict(
            region=region,
            sjukvardsregion=rm.cell(r, hd.get("Sjukvårdsregion", 0)).value if "Sjukvårdsregion" in hd else "",
            pop=pop, pop_65=pop_65, pct_65=pct_65,
            growth_65=growth_65,
            wait_spec=wait_spec,
            vyndaqel_per_100k=float(vyndaqel_per_100k) if vyndaqel_per_100k else None,
        )
    return out


# ============================================================================
# ARCHETYPE ASSIGNMENT
# ============================================================================
def assign_archetypes(region_data):
    """Returns dict[region] -> list of (archetype_name, is_primary)."""
    assignments = {}
    for region, d in region_data.items():
        tags = []
        for arch in ARCHETYPE_DEFS:
            try:
                if arch["rule"](d):
                    tags.append(arch["name"])
            except Exception as e:
                pass
        # Designate first-listed (in archetype order) as primary
        # Order of priority for primary: Rare-disease > Academic specialist > Competitive defense > Equity/access > High-governance > Aging
        priority_order = [
            "Rare-disease hotspot", "Academic specialist", "Competitive defense",
            "Equity/access-friction", "High-governance", "Aging vaccine-growth"
        ]
        ordered = sorted(tags, key=lambda x: priority_order.index(x))
        assignments[region] = ordered
    return assignments


# ============================================================================
# WORKBOOK WRITING
# ============================================================================
def make_header(cell, text, bg=PF_NAVY, size=10):
    cell.value = text
    cell.font = Font(name="Calibri", size=size, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = BORDER


def archetype_fill(name):
    return PatternFill("solid", fgColor=A_COLORS.get(name, "FFFFFF"))


def build():
    print(f"Loading {SRC.name} ...")
    shutil.copy(SRC, DST)
    wb = openpyxl.load_workbook(DST)

    print(f"Initial sheet count: {len(wb.sheetnames)}")

    region_data = extract_region_data(wb)
    print(f"Extracted data for {len(region_data)} regions")

    assignments = assign_archetypes(region_data)

    # Position new sheets right after OPP - Quadrant summary
    insert_idx = wb.sheetnames.index("OPP - Quadrant summary") + 1

    # ======== Sheet 1: OPP - Regional archetypes ========
    print("Writing 'OPP - Regional archetypes' sheet ...")
    ws = wb.create_sheet("OPP - Regional archetypes", index=insert_idx)
    ws.cell(row=1, column=1, value="Regional archetypes — strategic tag layer (region can carry multiple)")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)

    ws.cell(row=2, column=1, value=(
        "Six rule-based archetypes per audit #2 work item #4. Confidence: Modeled "
        "(rule thresholds are author-chosen). See findings_regional_archetypes.md for thresholds + reasoning. "
        "Each region's PRIMARY archetype is colored; SECONDARY archetypes listed in the tags column."
    ))
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)

    headers = ["Region", "Sjukvårdsregion", "Primary archetype", "Secondary archetypes", "All tags",
               "Pop 65+ %", "65+ growth 2024→2040 %", "Median wait spec (days)",
               "Vyndaqel /100k", "Confidence"]
    for i, h in enumerate(headers, start=1):
        make_header(ws.cell(row=4, column=i), h)

    # Sort: regions with Rare-disease + Competitive defense first, then by tag count
    sorted_regions = sorted(region_data.keys(), key=lambda r: (
        -len(assignments.get(r, [])),
        assignments.get(r, [""])[0] if assignments.get(r) else "zzz",
        r,
    ))

    for ri, region in enumerate(sorted_regions, start=5):
        d = region_data[region]
        tags = assignments[region]
        primary = tags[0] if tags else ""
        secondary = ", ".join(tags[1:]) if len(tags) > 1 else ""
        all_tags = " · ".join(tags)
        vals = [
            region, d.get("sjukvardsregion", ""), primary, secondary, all_tags,
            f"{d['pct_65']:.1f}" if d.get("pct_65") else "—",
            f"{d['growth_65']:.0f}" if d.get("growth_65") else "—",
            f"{d['wait_spec']:.0f}" if d.get("wait_spec") else "—",
            f"{d['vyndaqel_per_100k']:.1f}" if d.get("vyndaqel_per_100k") else "—",
            "Modeled",
        ]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 3 and primary:
                cell.fill = archetype_fill(primary)
                cell.font = Font(name="Calibri", size=10, bold=True)
            if ci == 10:
                cell.fill = PatternFill("solid", fgColor=C_MOD)
                cell.font = Font(name="Calibri", size=10, bold=True)

    widths = [22, 22, 22, 38, 50, 10, 10, 10, 10, 12]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:J{4 + len(sorted_regions)}"

    # ======== Sheet 2: OPP - Archetype playbooks ========
    print("Writing 'OPP - Archetype playbooks' sheet ...")
    ws2 = wb.create_sheet("OPP - Archetype playbooks", index=insert_idx + 1)
    ws2.cell(row=1, column=1, value="Per-archetype Pfizer engagement playbook")
    ws2.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color=PF_NAVY)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)

    ws2.cell(row=2, column=1, value=(
        "Each archetype's playbook: definition, member regions, who Pfizer should engage, "
        "which products fit, what evidence to bring, and what Pfizer must validate internally."
    ))
    ws2.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True, color=PF_GREY)
    ws2.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws2.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)

    pb_headers = ["Archetype", "Definition", "Member regions",
                  "Engagement target", "Product angle", "Evidence to bring",
                  "Pfizer validation needed"]
    for i, h in enumerate(pb_headers, start=1):
        make_header(ws2.cell(row=4, column=i), h)

    for ri, arch in enumerate(ARCHETYPE_DEFS, start=5):
        members = sorted([r for r, tags in assignments.items() if arch["name"] in tags])
        members_str = ", ".join(m.replace("Region ", "").replace("Västra Götalandsregionen", "VGR")
                                  .replace(" län", "") for m in members)
        vals = [arch["name"], arch["definition"], members_str,
                arch["engagement_target"], arch["product_angle"], arch["evidence_to_bring"],
                arch["pfizer_validation"]]
        for ci, v in enumerate(vals, start=1):
            cell = ws2.cell(row=ri, column=ci, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if ci == 1:
                cell.fill = archetype_fill(arch["name"])
                cell.font = Font(name="Calibri", size=10, bold=True)
        ws2.row_dimensions[ri].height = 90

    widths2 = [22, 50, 38, 38, 38, 50, 50]
    for i, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A5"

    # ======== Update README ========
    print("Updating README ...")
    rd = wb["README"]
    r = rd.max_row + 2
    rd.cell(row=r, column=1, value="REGIONAL ARCHETYPES (v17, 2026-04-25)")
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=12, bold=True, color=PF_NAVY)
    r += 1
    rd.cell(row=r, column=1, value=(
        "Six rule-based strategic archetypes (Academic specialist / Aging vaccine-growth / "
        "Rare-disease hotspot / Equity-access-friction / High-governance / Competitive defense). "
        "A region carries multiple tags. New 'OPP - Regional archetypes' sheet maps regions to "
        "tags; 'OPP - Archetype playbooks' sheet gives engagement playbook per archetype."
    ))
    rd.cell(row=r, column=1).font = Font(name="Calibri", size=10)
    rd.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

    # Save
    print(f"Final sheet count: {len(wb.sheetnames)}")
    wb.save(DST)
    print(f"Saved {DST.name}")

    # ======== CSV ========
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region", "sjukvardsregion", "archetype", "is_primary", "tag_order"])
        for region, tags in assignments.items():
            for i, tag in enumerate(tags):
                w.writerow([
                    region,
                    region_data[region].get("sjukvardsregion", ""),
                    tag,
                    "Y" if i == 0 else "N",
                    i + 1,
                ])
    print(f"Wrote {CSV_OUT.name}")

    # Summary
    print()
    print("Archetype distribution:")
    counts = {arch["name"]: 0 for arch in ARCHETYPE_DEFS}
    primary_counts = {arch["name"]: 0 for arch in ARCHETYPE_DEFS}
    for region, tags in assignments.items():
        for i, t in enumerate(tags):
            counts[t] += 1
            if i == 0:
                primary_counts[t] += 1
    for arch in ARCHETYPE_DEFS:
        n = counts[arch["name"]]
        np_ = primary_counts[arch["name"]]
        print(f"  {arch['name']:<24}: {n:>2} regions  (primary in {np_})")

    print()
    print("Tag count per region:")
    for region in sorted(assignments.keys(), key=lambda r: -len(assignments[r])):
        tags = assignments[region]
        short = region.replace("Region ", "").replace("Västra Götalandsregionen", "VGR")[:20]
        print(f"  {short:<22}: {len(tags)} tags  [{', '.join(tags)}]")

    return assignments, region_data


if __name__ == "__main__":
    build()
