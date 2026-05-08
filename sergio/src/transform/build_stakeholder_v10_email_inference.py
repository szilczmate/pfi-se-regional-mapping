# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build 07_stakeholder_mapping_v10.xlsx — fill missing emails via regional pattern inference.

Approach: every Swedish region uses a predictable email pattern (firstname.lastname@regiondomain).
For the 60+ priority-region rows in v9 with no email, generate an inferred email and tag it
explicitly as "INFERRED" in a new "Email confidence" column. This is honest defaults — Pfizer
can paste them into their CRM and the bounces tell them which 5–10% are wrong.

Pattern verification source: 22 already-verified emails in v9 + WebSearch confirmation per region
(2026-04-29). Domains documented inline. Character normalization: å→a, ä→a, ö→o, é→e, ž→z, etc.

Wins from targeted WebSearch (added directly):
  - Helén Eliasson (VGR RS ordf): helen.m.eliasson@vgregion.se
  - Johan Bratt (Stockholm Chefläkare + NSG): johan.bratt@regionstockholm.se
  - Pia Näsvall (Västerbotten HSD): phone 070-324 95 77 confirmed
"""

import re
from copy import copy
from pathlib import Path
from shutil import copyfile

import openpyxl
from openpyxl.styles import Font, PatternFill

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V9 = ROOT / "delivery" / "07_stakeholder_mapping_v9.xlsx"
V10 = ROOT / "delivery" / "07_stakeholder_mapping_v10.xlsx"

# Verified or high-confidence regional email domains
REGION_DOMAIN = {
    'Region Stockholm': 'regionstockholm.se',
    'Region Uppsala': 'regionuppsala.se',
    'Region Sörmland': 'regionsormland.se',
    'Region Östergötland': 'regionostergotland.se',
    'Region Jönköpings län': 'rjl.se',
    'Region Kronoberg': 'kronoberg.se',
    'Region Kalmar': 'regionkalmar.se',
    'Region Gotland': 'gotland.se',
    'Region Blekinge': 'regionblekinge.se',
    'Region Skåne': 'skane.se',
    'Region Halland': 'regionhalland.se',
    'Västra Götalandsregionen': 'vgregion.se',
    'Region Värmland': 'regionvarmland.se',
    'Region Örebro län': 'regionorebrolan.se',
    'Region Västmanland': 'regionvastmanland.se',
    'Region Dalarna': 'regiondalarna.se',
    'Region Gävleborg': 'regiongavleborg.se',
    'Region Västernorrland': 'rvn.se',
    'Region Jämtland Härjedalen': 'regionjh.se',
    'Region Västerbotten': 'regionvasterbotten.se',
    'Region Norrbotten': 'norrbotten.se',
}

# Direct verified emails captured this session (2026-04-29 WebSearch)
DIRECT_HITS = {
    ('Region Stockholm', 'Johan Bratt'): 'johan.bratt@regionstockholm.se',
    ('Västra Götalandsregionen', 'Helén Eliasson'): 'helen.m.eliasson@vgregion.se',
}
# Phone hits
PHONE_HITS = {
    ('Region Västerbotten', 'Pia Näsvall'): '070-324 95 77',
}

# Character normalization for Swedish + common diacritics
CHAR_MAP = str.maketrans({
    'å': 'a', 'Å': 'a',
    'ä': 'a', 'Ä': 'a',
    'ö': 'o', 'Ö': 'o',
    'é': 'e', 'É': 'e',
    'è': 'e', 'È': 'e',
    'ê': 'e', 'Ê': 'e',
    'à': 'a', 'À': 'a',
    'á': 'a', 'Á': 'a',
    'â': 'a', 'Â': 'a',
    'í': 'i', 'Í': 'i',
    'ì': 'i', 'Ì': 'i',
    'ó': 'o', 'Ó': 'o',
    'ò': 'o', 'Ò': 'o',
    'ô': 'o', 'Ô': 'o',
    'ú': 'u', 'Ú': 'u',
    'ù': 'u', 'Ù': 'u',
    'ü': 'u', 'Ü': 'u',
    'ý': 'y', 'Ý': 'y',
    'ñ': 'n', 'Ñ': 'n',
    'ç': 'c', 'Ç': 'c',
    'ć': 'c', 'Ć': 'c',
    'č': 'c', 'Č': 'c',
    'ž': 'z', 'Ž': 'z',
    'š': 's', 'Š': 's',
    'ł': 'l', 'Ł': 'l',
    'ß': 'ss',
})


def clean_name(raw):
    """Remove parenthetical party labels, placeholders, return clean name or None."""
    if not raw:
        return None
    raw = raw.strip()
    # Skip placeholders + structural rows
    if raw in ('?', '-', '—'):
        return None
    if raw.startswith('STRUCTURAL') or 'pensioneras' in raw.lower():
        # 'STRUCTURAL — Sjukhusstyrelsen ordförande' = role doesn't have a single named individual
        if raw.startswith('STRUCTURAL'):
            return None
        # 'Mats Bojestig (pensioneras 2026)' — keep the name, drop the parenthetical
    # Strip parenthetical (party tag, retirement note, etc.)
    raw = re.sub(r'\s*\([^)]*\)', '', raw).strip()
    # Strip "av politiska skäl" or similar admin annotations
    raw = re.sub(r'\s*—.*$', '', raw).strip()
    if not raw or raw in ('?',):
        return None
    return raw


def infer_email(region, name, domain):
    """Build firstname.lastname@domain using normalised characters."""
    if not name or not domain:
        return None
    parts = name.split()
    if len(parts) < 2:
        return None
    first = parts[0]
    # For multi-name surnames (e.g. "Maria Palmetun Ekbäck"), default to LAST surname only
    # (most common pattern, e.g. christina.fischer not christina.maria-fischer)
    last = parts[-1]
    # Normalize special chars
    first_n = first.translate(CHAR_MAP).lower()
    last_n = last.translate(CHAR_MAP).lower()
    # Strip any remaining non-alphanumeric except hyphen
    first_n = re.sub(r"[^a-z0-9\-]", '', first_n)
    last_n = re.sub(r"[^a-z0-9\-]", '', last_n)
    if not first_n or not last_n:
        return None
    return f'{first_n}.{last_n}@{domain}'


def main():
    print(f'Copying v9 → v10')
    copyfile(V9, V10)
    wb = openpyxl.load_workbook(V10)
    ws = wb['Contacts']

    # Find column indices
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    col = {h: i for i, h in enumerate(headers)}
    region_c = col['Region / Sjukvårdsregion']
    name_c = col['Name']
    email_c = col['Email']
    phone_c = col['Phone or switchboard']
    notes_c = col['Notes']

    # Add a new "Email confidence" column at the end (after Notes if not yet present)
    if 'Email confidence' not in headers:
        new_col = len(headers) + 1
        ws.cell(row=1, column=new_col, value='Email confidence')
        ws.cell(row=1, column=new_col).font = Font(bold=True)
        confidence_c = new_col - 1  # 0-indexed for our row tuples
    else:
        confidence_c = headers.index('Email confidence')

    # Statistics
    n_total = 0
    n_already_email = 0
    n_filled_direct = 0
    n_filled_inferred = 0
    n_filled_phone = 0
    n_skipped = 0

    INFERRED_FILL = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")
    DIRECT_FILL = PatternFill(start_color="E0F0E0", end_color="E0F0E0", fill_type="solid")

    for row_idx in range(2, ws.max_row + 1):
        row = [ws.cell(row=row_idx, column=c+1).value for c in range(len(headers))]
        if not row[name_c]:
            continue
        n_total += 1

        region_raw = (row[region_c] or '').strip()
        name_raw = (row[name_c] or '').strip()
        existing_email = (row[email_c] or '').strip() if row[email_c] else ''
        existing_phone = (row[phone_c] or '').strip() if row[phone_c] else ''

        # Identify the "main" region for domain lookup. The region cell sometimes has
        # "Sydöstra — Region Jönköpings län" — extract the Region part.
        region_match = None
        for r in REGION_DOMAIN:
            if r in region_raw:
                region_match = r
                break

        if existing_email and '@' in existing_email and 'not published' not in existing_email.lower():
            n_already_email += 1
            ws.cell(row=row_idx, column=confidence_c+1, value='Verified')
            continue

        # Try direct hit first
        cleaned_name = clean_name(name_raw)
        if region_match and cleaned_name:
            direct = DIRECT_HITS.get((region_match, cleaned_name))
            if direct:
                ws.cell(row=row_idx, column=email_c+1, value=direct)
                ws.cell(row=row_idx, column=email_c+1).fill = DIRECT_FILL
                ws.cell(row=row_idx, column=confidence_c+1, value='Verified (WebSearch 2026-04-29)')
                n_filled_direct += 1
                # Also append to notes
                existing_note = ws.cell(row=row_idx, column=notes_c+1).value or ''
                ws.cell(row=row_idx, column=notes_c+1, value=
                    (existing_note + ' | ' if existing_note else '') +
                    f'Email verified 2026-04-29 via WebSearch (Pfizer-meeting-prep close-out).')
                # Phone hit?
                phone = PHONE_HITS.get((region_match, cleaned_name))
                if phone and not existing_phone:
                    ws.cell(row=row_idx, column=phone_c+1, value=phone)
                    n_filled_phone += 1
                continue

        # Phone-only hit (no email but phone known)
        if region_match and cleaned_name and not existing_phone:
            phone = PHONE_HITS.get((region_match, cleaned_name))
            if phone:
                ws.cell(row=row_idx, column=phone_c+1, value=phone)
                n_filled_phone += 1

        # Try inference
        if region_match and cleaned_name:
            domain = REGION_DOMAIN.get(region_match)
            inferred = infer_email(region_match, cleaned_name, domain)
            if inferred:
                ws.cell(row=row_idx, column=email_c+1, value=inferred)
                ws.cell(row=row_idx, column=email_c+1).fill = INFERRED_FILL
                ws.cell(row=row_idx, column=confidence_c+1, value=
                    f'INFERRED · pattern firstname.lastname@{domain} · NEEDS VERIFICATION')
                n_filled_inferred += 1
                # Append note
                existing_note = ws.cell(row=row_idx, column=notes_c+1).value or ''
                ws.cell(row=row_idx, column=notes_c+1, value=
                    (existing_note + ' | ' if existing_note else '') +
                    f'Email inferred from Region pattern (firstname.lastname@{domain}). 2026-04-29 close-out. '
                    f'For double-barrelled surnames or middle names, alternate forms may apply (e.g. with hyphen, '
                    f'or with middle initial as in helen.m.eliasson@vgregion.se).')
                continue

        # Skipped (placeholder name, structural row, unknown region)
        n_skipped += 1
        ws.cell(row=row_idx, column=confidence_c+1, value='— (no name or non-individual row)')

    # Resize confidence column
    from openpyxl.utils import get_column_letter
    ws.column_dimensions[get_column_letter(confidence_c+1)].width = 50

    wb.save(V10)
    print(f'\nSaved {V10}')
    print(f'\n=== Email coverage v9 → v10 ===')
    print(f'  Total stakeholder rows: {n_total}')
    print(f'  Already had verified email (v9):     {n_already_email}')
    print(f'  Newly filled — direct WebSearch:     {n_filled_direct}')
    print(f'  Newly filled — pattern inference:    {n_filled_inferred}')
    print(f'  Newly filled — phone (no email):     {n_filled_phone}')
    print(f'  Skipped (no name / structural):      {n_skipped}')
    total_email = n_already_email + n_filled_direct + n_filled_inferred
    print(f'\n  v9 email coverage: {n_already_email}/{n_total} ({n_already_email/n_total*100:.0f}%)')
    print(f'  v10 email coverage: {total_email}/{n_total} ({total_email/n_total*100:.0f}%)')


if __name__ == '__main__':
    main()
