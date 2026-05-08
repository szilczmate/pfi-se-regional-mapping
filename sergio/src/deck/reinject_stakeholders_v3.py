# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Re-inject corrected STAKEHOLDERS + INTEL into the deck HTML.

After fix_stakeholders_v1.py corrects stakeholder_data.json, this script:
  1. Replaces the STAKEHOLDERS array in the deck with the corrected JSON
  2. Updates the INTEL array's Pia Näsvall observation with the 1 Oct 2025 date

Uses boundary-marker replacement to avoid fragile regex.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
SRC_HTML = ROOT / "delivery/11_PFIZER_PRESENTATION_v1_intro_partA.html"
SRC_JSON = ROOT / "working/data/master/stakeholder_data.json"
BACKUP = ROOT / f"delivery/11_PFIZER_PRESENTATION_v1_intro_partA_pre_codex_round1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

# Backup
shutil.copy2(SRC_HTML, BACKUP)
print(f"Backup written: {BACKUP.name}")

with open(SRC_JSON, encoding='utf-8') as f:
    data = json.load(f)

stakeholders = data['stakeholders']
intel = data.get('critical_intel', [])

with open(SRC_HTML, encoding='utf-8') as f:
    text = f.read()

# ---- Replace STAKEHOLDERS array ----
marker_start = 'const STAKEHOLDERS = '
marker_end = '];\nconst NAMED = '

idx_start = text.find(marker_start)
if idx_start < 0:
    raise SystemExit('STAKEHOLDERS marker not found')
idx_end = text.find(marker_end, idx_start)
if idx_end < 0:
    raise SystemExit('STAKEHOLDERS end marker not found')

# Build the new array literal — JSON dump with no extra spaces, single line
new_stakeholders_json = json.dumps(stakeholders, ensure_ascii=False, separators=(', ', ': '))
new_stakeholders_block = marker_start + new_stakeholders_json
# idx_end points to the start of the closing bracket sequence "];\n" — we want to replace up through "]"
# Find the actual end position of the array (the bracket before ];)
end_pos = idx_end + 1  # include the closing ]
text = text[:idx_start] + new_stakeholders_block + text[end_pos:]
print(f'STAKEHOLDERS replaced — new size: {len(new_stakeholders_json)} chars')

# ---- Replace INTEL array (only need to update Pia Näsvall observation) ----
marker_start_intel = 'const INTEL = '
marker_end_intel = '];\nconst QUAD = '

idx_start_i = text.find(marker_start_intel)
if idx_start_i < 0:
    print('WARN: INTEL marker not found — skipping intel update')
else:
    idx_end_i = text.find(marker_end_intel, idx_start_i)
    if idx_end_i < 0:
        print('WARN: INTEL end marker not found — skipping intel update')
    else:
        # Read the existing INTEL array
        intel_text = text[idx_start_i + len(marker_start_intel):idx_end_i + 1]
        # The intel in the JSON file is the canonical source; serialise it
        new_intel_json = json.dumps(intel, ensure_ascii=False, separators=(', ', ': '))
        text = text[:idx_start_i] + marker_start_intel + new_intel_json + text[idx_end_i + 1:]
        print(f'INTEL replaced — new size: {len(new_intel_json)} chars')

# Save
with open(SRC_HTML, 'w', encoding='utf-8') as f:
    f.write(text)
print(f'\nWritten: {SRC_HTML}')
print(f'Final size: {len(text)/1024:.1f} KB')
