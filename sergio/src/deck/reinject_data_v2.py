# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Robust re-injection: rewrite the entire data block from scratch."""
import json, re
from pathlib import Path

with open('working/data/master/deck_model.json', encoding='utf-8') as f: deck = json.load(f)
with open('working/data/master/brick_priority.json', encoding='utf-8') as f: brick = json.load(f)
with open('working/data/master/share_arc.json', encoding='utf-8') as f: arc = json.load(f)
with open('working/data/master/attr_pn_cm.json', encoding='utf-8') as f: attr = json.load(f)
with open('working/data/master/stakeholder_data.json', encoding='utf-8') as f: stake = json.load(f)
with open('working/data/master/quadrant_and_nt.json', encoding='utf-8') as f: qnt = json.load(f)

html_path = Path('delivery/11_PFIZER_PRESENTATION_v1_intro_partA.html')
text = html_path.read_text(encoding='utf-8')

# Strategy: find the start of the data block (`const DATA = `) and the marker just before the
# logic begins (`const ARCHETYPE_KEY = `) — replace the ENTIRE data block as one operation.
data_start_marker = 'const DATA = '
data_end_marker = '\nconst ARCHETYPE_KEY ='

start = text.find(data_start_marker)
end = text.find(data_end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('Markers not found')

print(f'Data block: chars {start}–{end} (length {end-start})')

new_block_lines = [
    'const DATA = ' + json.dumps(deck, ensure_ascii=False) + ';',
    'const BRICK = ' + json.dumps(brick, ensure_ascii=False) + ';',
    'const ARC = ' + json.dumps(arc, ensure_ascii=False) + ';',
    'const ATTR = ' + json.dumps(attr, ensure_ascii=False) + ';',
    'const STAKEHOLDERS = ' + json.dumps(stake['stakeholders'], ensure_ascii=False) + ';',
    'const NAMED = ' + json.dumps(stake['named_individuals'], ensure_ascii=False) + ';',
    'const INTEL = ' + json.dumps(stake['critical_intel'], ensure_ascii=False) + ';',
    'const QUAD = ' + json.dumps(qnt['quadrant'], ensure_ascii=False) + ';',
    'const NT_RADET = ' + json.dumps(qnt['nt_radet'], ensure_ascii=False) + ';',
    'const PTS_2024 = ' + json.dumps(qnt['region_pts_2024'], ensure_ascii=False) + ';',
]
new_block = '\n'.join(new_block_lines)
print(f'New block length: {len(new_block)}')

# Replace text[start:end] with new_block
text = text[:start] + new_block + text[end:]

html_path.write_text(text, encoding='utf-8')
print(f'\nFinal size: {html_path.stat().st_size/1024:.1f} KB')
