# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Polish v6: fact-check fixes — ATTR over-index, defense bricks, top-15 total, Bojestig wording."""
from pathlib import Path

html_path = Path('delivery/11_PFIZER_PRESENTATION_v1_intro_partA.html')
text = html_path.read_text(encoding='utf-8')

# ============================================================================
# FIX 1: TLDR card — replace 8.1× with 7.6× (canonical W2 finding)
# ============================================================================
fixes_attr = [
    ('<div class="tldr-num">8.1<span class="unit">×</span></div>',
     '<div class="tldr-num">7.6<span class="unit">×</span></div>'),
    ('Norrland over-indexes <strong>8.1×</strong> on ATTR peripheral neuropathy',
     'Norrland over-indexes <strong>7.6×</strong> on ATTR peripheral neuropathy'),
    # The methodology divider preview card
    ('Norrland 8.1× over-index on ATTR-PN',
     'Norrland 7.6× over-index on ATTR-PN'),
]
n = 0
for old, new in fixes_attr:
    if old in text:
        text = text.replace(old, new)
        n += 1
print(f'FIX 1: ATTR over-index updated to 7.6× ({n} of {len(fixes_attr)})')

# ============================================================================
# FIX 2: Update brick_priority.json defense bricks to canonical workbook v31 values
# (Eskilstuna, Kristianstad, Sundsvall) and re-extract.
# Actually, brick_priority.json already has these names from the original extraction.
# The deck displays them via the BRICK.defense binding. Verify by reading the file.
# ============================================================================
import json
with open('working/data/master/brick_priority.json') as f:
    brick = json.load(f)

print(f'\nCurrent defense bricks in brick_priority.json:')
for b in brick['defense']:
    print(f'  - {b["brick"]}')
# Should be: 07 - Eskilstuna, 24 - Kristianstad, 59 - Sundsvall
# Confirmed from earlier extraction

# Now fix the HARDCODED references in the deck (TLDR + plays-brick section + M7)
fixes_defense = [
    ('Three Defense bricks (Linköping, Sundsvall, Tierp)',
     'Three Defense bricks (Eskilstuna, Kristianstad, Sundsvall)'),
    ('Three Defense bricks identified: Linköping, Sundsvall, Tierp',
     'Three Defense bricks identified: Eskilstuna, Kristianstad, Sundsvall'),
]
n = 0
for old, new in fixes_defense:
    if old in text:
        text = text.replace(old, new)
        n += 1
print(f'\nFIX 2: Defense brick names corrected ({n} of {len(fixes_defense)})')

# ============================================================================
# FIX 3: Top-15 Recovery total — 5.7M kr is inherited from older state; actual is ~6M
# Update wording.
# ============================================================================
fixes_total = [
    ('top 15 cover <strong>5.7M kr</strong> of the total',
     'top 15 cover <strong>~6M kr</strong> of the total'),
    ('top 15 Recovery bricks cover 5.7M kr of 9.3M kr Sweden-wide opportunity',
     'top 15 Recovery bricks cover ~6M kr of the 9.3M kr Sweden-wide opportunity'),
]
n = 0
for old, new in fixes_total:
    if old in text:
        text = text.replace(old, new)
        n += 1
print(f'\nFIX 3: Top-15 Recovery total updated ({n} of {len(fixes_total)})')

# ============================================================================
# FIX 4: Soften Bojestig wording (not in canonical critical intel)
# ============================================================================
old_bojestig = 'Co-anchor of the Jönköping triple-leverage cluster (with Lindström and the incoming HSD post-Bojestig). LK formulary authority in Region Jönköping.'
new_bojestig = 'Co-anchor of the Jönköping triple-leverage cluster, alongside Mårten Lindström. LK formulary authority in Region Jönköping with NT-rådet Sydöstra association.'
if old_bojestig in text:
    text = text.replace(old_bojestig, new_bojestig)
    print('FIX 4a: Maria Ekelund Bojestig reference softened')

# Also in critical intel narrative
old_bojestig2 = 'Combined with the NT-rådet Chair role held by Mårten Lindström (also Jönköping-based), this creates an unusually concentrated access geography in one region — three governance levers in close proximity.'
new_bojestig2 = 'Combined with the NT-rådet Chair role held by Mårten Lindström (also Jönköping-based), this creates an unusually concentrated access geography in one region — two governance levers in close proximity, with the regional HSD seat as a third operational anchor.'
if old_bojestig2 in text:
    text = text.replace(old_bojestig2, new_bojestig2)
    print('FIX 4b: Critical intel Jönköping narrative softened')

# Save
html_path.write_text(text, encoding='utf-8')
print(f'\nFinal size: {html_path.stat().st_size/1024:.1f} KB')
PYEOF