# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Round 1 fixes — stakeholder data corrections per fact-check audit.

Fixes:
  1. Stockholm HSN ordf: Anna Starbrink → Talla Alkurdi (S)
     Vice chairs: 1st Christine Lorne (C), 2nd Axel Conradi (M)
  2. NSG rep per sjukvårdsregion:
     - Mellansverige (7 regions): Jonas Claesson → Magnus Johansson (Region Sörmland HSD)
     - Södra (4 regions): Martin Engström → Emma Pihl (Region Halland HSD)
     - Västra (1 region): Kaarina Sundelin → Jonas Claesson (VGR HSD, moved Oct 2025)
  3. Pia Näsvall HSD source note: clarify "took up Västerbotten role 1 October 2025"

Updates the JSON in place after creating a backup.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC = ROOT / "working/data/master/stakeholder_data.json"
BACKUP = ROOT / f"working/data/master/stakeholder_data_pre_audit_round1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Backup
shutil.copy2(SRC, BACKUP)
print(f"Backup written: {BACKUP.name}")

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

stakeholders = data['stakeholders']

# Sjukvårdsregion → NSG rep replacement map
NSG_REPLACEMENTS = {
    'Mellansverige': 'Magnus Johansson (Region Sörmland - HSD)',
    'Södra': 'Emma Pihl (Region Halland - HSD)',
    'Västra': 'Jonas Claesson (VGR - HSD, moved from Mellansverige Oct 2025)',
}

n_nsg = 0
n_stockholm = 0
n_vasterbotten = 0

for s in stakeholders:
    region = s.get('Region', '')
    svr = s.get('Sjukvårdsregion', '')

    # Fix 1 — Stockholm HSN
    if region == 'Region Stockholm':
        old_hsn = s.get('HSN ordf', '')
        s['HSN ordf'] = 'Talla Alkurdi (S)'
        s['HSN source'] = (
            'Region Stockholm official politiker register 2026 (regionstockholm.se '
            'Hälso- och sjukvårdsnämnden); 1:e vice ordförande Christine Lorne (C), '
            '2:e vice ordförande Axel Conradi (M). Verified 2026-05-08.'
        )
        n_stockholm += 1
        print(f"  Stockholm HSN: {old_hsn!r} → 'Talla Alkurdi (S)'")

    # Fix 2 — NSG rep per sjukvårdsregion
    if svr in NSG_REPLACEMENTS:
        old_nsg = s.get('NSG rep (SVR)', '')
        new_nsg = NSG_REPLACEMENTS[svr]
        if old_nsg != new_nsg:
            s['NSG rep (SVR)'] = new_nsg
            n_nsg += 1

    # Fix 3 — Pia Näsvall date precision (Västerbotten + Norrbotten records reference her move)
    if region == 'Region Västerbotten':
        s['HSD source'] = (
            'Pia Näsvall confirmed; took up Västerbotten HSD role on 1 October 2025 '
            '(announced June 2025; replaced Elisabeth Karlsson who retired). Previously '
            'Norrbotten HSD 2021–2025. Continues as NSG Läkemedel ordförande. Verified 2026-05-08.'
        )
        n_vasterbotten += 1

# Fix 3b — Norrbotten record references "replaced Pia Näsvall who moved to Västerbotten"
for s in stakeholders:
    if s.get('Region') == 'Region Norrbotten':
        s['HSD source'] = (
            "norrbotten.se organisation page Apr 2026 + press release; replaces Pia Näsvall who moved to "
            "Västerbotten on 1 October 2025. Maria Joelsson currently tf. HSD pending permanent appointment. "
            "Verified 2026-05-08."
        )
        n_vasterbotten += 1

# Fix 3c — Critical intel observation about Pia Näsvall move
for obs in data.get('critical_intel', []):
    if 'NSG' in obs.get('observation', '') and 'transfer' in obs.get('observation', '').lower():
        old = obs.get('detail', '')
        if '2024' in old or 'flyttade' in old:
            obs['detail'] = (
                'Pia Näsvall moved from Norrbotten to Västerbotten on 1 October 2025 (announced '
                'June 2025). Continues as NSG Läkemedel ordförande. Norrbotten HSD seat held tf. by '
                'Maria Joelsson pending permanent appointment.'
            )
            print(f"  Critical intel transfer obs updated: {old[:50]}... → 1 Oct 2025")
    if 'Stockholm HSN' in obs.get('observation', ''):
        # The existing observation already says Talla Alkurdi is correct; just confirm
        print(f"  Critical intel HSN obs already correct: {obs.get('detail','')[:80]}...")

with open(SRC, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print()
print(f"NSG rep updates: {n_nsg} regions (expected 12: 7 Mellansverige + 4 Södra + 1 Västra)")
print(f"Stockholm HSN updates: {n_stockholm}")
print(f"Pia Näsvall date updates: {n_vasterbotten}")
print(f"\nWritten: {SRC}")
