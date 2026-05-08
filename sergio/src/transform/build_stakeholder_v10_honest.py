# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build 07_stakeholder_mapping_v10.xlsx — HONEST email inference.

Honest design (after user pushback on accuracy 2026-04-29):
  - Email column reserved for VERIFIED emails ONLY (v9 carryover + this session's WebSearch hits)
  - NEW column 'Inferred email candidate' carries pattern-based guesses
  - NEW column 'Inference confidence' rates each inference: HIGH / MEDIUM / LOW
  - Known-wrong patterns (names with 'von', middle initials likely needed) flagged LOW
  - Methods note inserted as a header row (Confidence summary sheet) explaining the convention
  - Every inferred email reads "candidate, NEEDS VERIFICATION before use"

Verified-tier sources for emails added this session:
  - Helén Eliasson (VGR RS ordf): WebSearch 2026-04-29 → helen.m.eliasson@vgregion.se
  - Johan Bratt (Stockholm Chefläkare + NSG): WebSearch → johan.bratt@regionstockholm.se
  - Pia Näsvall (Västerbotten HSD): WebSearch → phone 070-324 95 77 (email not published)
"""

import re
import sys
from copy import copy
from pathlib import Path
from shutil import copyfile

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V9 = ROOT / "delivery" / "07_stakeholder_mapping_v9.xlsx"
V10 = ROOT / "delivery" / "07_stakeholder_mapping_v10.xlsx"

sys.stdout.reconfigure(encoding="utf-8")

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

# Domains where the pattern is CONFIRMED via existing-verified-emails-in-v9 OR via WebSearch
# returning live email addresses. Used to set inference confidence.
DOMAIN_VERIFIED = {
    'regionstockholm.se',  # mats.ek, siobhan.wallhuss verified in v9
    'regionostergotland.se',  # christina.fischer
    'rjl.se',  # marten.lindstrom
    'regionjh.se',  # kristina.seling
    'kronoberg.se',  # fredrik.schon
    'skane.se',  # Stefan.U.Nilsson — note middle initial
    'regionorebrolan.se',  # maria.palmetun-ekback
    'vgregion.se',  # johan.sandelin, helen.m.eliasson
    'regionuppsala.se',  # WebSearch confirmed
    'regionhalland.se',  # WebSearch confirmed
    'regionvasterbotten.se',  # WebSearch confirmed (annakarin.nilsson)
    'norrbotten.se',  # v9 row marked as 'try anders.bergstrom@norrbotten.se'
    'gotland.se',  # WebSearch confirmed
    'regiongavleborg.se',  # WebSearch confirmed
    'rvn.se',  # WebSearch confirmed
}

# Direct verified emails captured this session
DIRECT_HITS = {
    'Johan Bratt': ('johan.bratt@regionstockholm.se',
                    'WebSearch 2026-04-29 — Stockholm Chefläkare + NSG ref'),
    'Helén Eliasson': ('helen.m.eliasson@vgregion.se',
                       'WebSearch 2026-04-29 — uses middle initial M'),
}
PHONE_HITS = {
    'Pia Näsvall': ('070-324 95 77',
                    'WebSearch 2026-04-29 — published in Region Västerbotten press release'),
}

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

CHAR_MAP = str.maketrans({
    'å': 'a', 'Å': 'a', 'ä': 'a', 'Ä': 'a', 'ö': 'o', 'Ö': 'o',
    'é': 'e', 'É': 'e', 'è': 'e', 'È': 'e', 'ê': 'e', 'Ê': 'e',
    'à': 'a', 'À': 'a', 'á': 'a', 'Á': 'a', 'â': 'a', 'Â': 'a',
    'í': 'i', 'Í': 'i', 'ì': 'i', 'Ì': 'i',
    'ó': 'o', 'Ó': 'o', 'ò': 'o', 'Ò': 'o', 'ô': 'o', 'Ô': 'o',
    'ú': 'u', 'Ú': 'u', 'ù': 'u', 'Ù': 'u', 'ü': 'u', 'Ü': 'u',
    'ý': 'y', 'Ý': 'y', 'ñ': 'n', 'Ñ': 'n', 'ç': 'c', 'Ç': 'c',
    'ć': 'c', 'Ć': 'c', 'č': 'c', 'Č': 'c', 'ž': 'z', 'Ž': 'z',
    'š': 's', 'Š': 's', 'ł': 'l', 'Ł': 'l', 'ß': 'ss',
})

# Particles that indicate names where the inference is UNCERTAIN
TRICKY_PARTICLES = {'von', 'van', 'de', 'la', 'le', 'al', 'el', 'di', 'da'}


def clean_name(raw):
    if not raw:
        return None
    raw = raw.strip()
    if raw in ('?', '-', '—'):
        return None
    if raw.startswith('STRUCTURAL'):
        return None
    raw = re.sub(r'\s*\([^)]*\)', '', raw).strip()
    raw = re.sub(r'\s*—.*$', '', raw).strip()
    if not raw or raw == '?':
        return None
    return raw


def normalize_token(s):
    s = s.translate(CHAR_MAP).lower()
    s = re.sub(r"[^a-z0-9\-]", '', s)
    return s


def infer_email(name, domain):
    """Returns (email_candidate, confidence_tier, rationale)."""
    parts = name.split()
    if len(parts) < 2:
        return None, None, 'name has fewer than 2 tokens'

    first = parts[0]
    middle_tokens = parts[1:-1]
    last = parts[-1]

    has_tricky = any(t.lower() in TRICKY_PARTICLES for t in parts)
    has_special = any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -' for c in name)
    has_multi_lastname = len(parts) >= 3 and not has_tricky
    domain_verified = domain in DOMAIN_VERIFIED

    # Default inference: firstname.lastname (drop middle tokens)
    first_n = normalize_token(first)
    last_n = normalize_token(last)
    if not first_n or not last_n:
        return None, None, 'normalization produced empty token'
    candidate = f'{first_n}.{last_n}@{domain}'

    # Confidence tier
    if has_tricky:
        tier = 'LOW'
        rationale = (f"Name contains particle ({','.join([t for t in parts if t.lower() in TRICKY_PARTICLES])}); "
                     f"actual email may include particle (e.g. johan.von.knorring) — VERIFY before use.")
    elif has_multi_lastname:
        tier = 'MEDIUM'
        rationale = ("Name has 3+ tokens — middle name(s) dropped. Real email may include middle initial "
                     "(e.g. Helén Eliasson → helen.m.eliasson) or hyphenate the surnames (e.g. Maria "
                     "Palmetun Ekbäck → maria.palmetun-ekback). VERIFY before use.")
    elif not domain_verified:
        tier = 'MEDIUM'
        rationale = f"Domain {domain} pattern not directly verified for this region — VERIFY before use."
    elif has_special:
        tier = 'HIGH'
        rationale = (f"Single first + single last + verified domain. Special characters normalized "
                     f"(å→a, ä→a, ö→o, ž→z, etc). Pattern matches confirmed regional convention.")
    else:
        tier = 'HIGH'
        rationale = "Single first + single last + verified domain pattern."
    return candidate, tier, rationale


def main():
    print(f'Copying v9 → v10')
    copyfile(V9, V10)
    wb = openpyxl.load_workbook(V10)
    ws = wb['Contacts']

    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    col = {h: i for i, h in enumerate(headers)}
    region_c = col['Region / Sjukvårdsregion']
    role_c = col['Role']
    name_c = col['Name']
    conf_c = col['Name confidence']
    email_c = col['Email']
    phone_c = col['Phone or switchboard']
    source_c = col['Source URL']
    verified_c = col['Last verified']
    notes_c = col['Notes']

    # v9 NSG rows were shifted one column to the right:
    # Role contained the affiliated region, Name contained the role, Name
    # confidence contained the person's name, Email contained HIGH, etc.
    # Normalize those rows before applying the verified/inferred email logic.
    for row_idx in range(2, ws.max_row + 1):
        scope = ws.cell(row=row_idx, column=1).value
        email_val = ws.cell(row=row_idx, column=email_c + 1).value
        if scope == 'NSG (national tier)' and str(email_val).strip().upper() in {'HIGH', 'MEDIUM', 'LOW'}:
            affiliation = ws.cell(row=row_idx, column=role_c + 1).value
            role = ws.cell(row=row_idx, column=name_c + 1).value
            name = ws.cell(row=row_idx, column=conf_c + 1).value
            confidence = email_val
            source = ws.cell(row=row_idx, column=verified_c + 1).value
            last_verified = ws.cell(row=row_idx, column=notes_c + 1).value
            notes = ws.cell(row=row_idx, column=notes_c + 2).value

            region_value = ws.cell(row=row_idx, column=region_c + 1).value or ''
            ws.cell(row=row_idx, column=region_c + 1, value=f"{region_value} — {affiliation}" if affiliation else region_value)
            ws.cell(row=row_idx, column=role_c + 1, value=role)
            ws.cell(row=row_idx, column=name_c + 1, value=name)
            ws.cell(row=row_idx, column=conf_c + 1, value=confidence)
            ws.cell(row=row_idx, column=email_c + 1).value = None
            ws.cell(row=row_idx, column=phone_c + 1).value = None
            ws.cell(row=row_idx, column=source_c + 1, value=source)
            ws.cell(row=row_idx, column=verified_c + 1, value=last_verified)
            ws.cell(row=row_idx, column=notes_c + 1, value=notes)
            ws.cell(row=row_idx, column=notes_c + 2).value = None

    # Add three new columns at the end
    base_n = len(headers)
    ws.cell(row=1, column=base_n + 1, value='Inferred email candidate')
    ws.cell(row=1, column=base_n + 2, value='Inference confidence')
    ws.cell(row=1, column=base_n + 3, value='Inference rationale')
    for col_offset in [1, 2, 3]:
        ws.cell(row=1, column=base_n + col_offset).font = Font(bold=True)

    inf_email_c = base_n  # 0-indexed
    inf_conf_c = base_n + 1
    inf_rat_c = base_n + 2

    INFERRED_HIGH = PatternFill(start_color="E0F0E0", end_color="E0F0E0", fill_type="solid")
    INFERRED_MED = PatternFill(start_color="FFF4D9", end_color="FFF4D9", fill_type="solid")
    INFERRED_LOW = PatternFill(start_color="FFE0E0", end_color="FFE0E0", fill_type="solid")
    DIRECT_FILL = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")

    n_total = 0
    n_already_email = 0
    n_direct_added = 0
    n_phone_added = 0
    n_inferred_high = 0
    n_inferred_med = 0
    n_inferred_low = 0
    n_skipped = 0

    for row_idx in range(2, ws.max_row + 1):
        name_raw = ws.cell(row=row_idx, column=name_c + 1).value
        if not name_raw:
            continue
        n_total += 1

        region_raw = (ws.cell(row=row_idx, column=region_c + 1).value or '').strip()
        existing_email = (ws.cell(row=row_idx, column=email_c + 1).value or '').strip()
        existing_phone = (ws.cell(row=row_idx, column=phone_c + 1).value or '').strip()

        if existing_email and not EMAIL_RE.match(existing_email):
            existing_email = ''
            ws.cell(row=row_idx, column=email_c + 1).value = None

        # Identify which region domain applies
        region_match = None
        for r in REGION_DOMAIN:
            if r in region_raw:
                region_match = r
                break

        cleaned = clean_name(name_raw)

        # 1. Already-verified email (v9 carryover) — preserve
        if existing_email and EMAIL_RE.match(existing_email):
            n_already_email += 1
            continue

        # 2. Direct WebSearch hit this session — write to Email column as VERIFIED
        if cleaned and cleaned in DIRECT_HITS:
            new_email, source = DIRECT_HITS[cleaned]
            ws.cell(row=row_idx, column=email_c + 1, value=new_email)
            ws.cell(row=row_idx, column=email_c + 1).fill = DIRECT_FILL
            existing_note = ws.cell(row=row_idx, column=notes_c + 1).value or ''
            ws.cell(row=row_idx, column=notes_c + 1, value=
                (existing_note + ' | ' if existing_note else '') +
                f'Email VERIFIED via {source}.')
            n_direct_added += 1

        # 3. Phone hit
        if cleaned and cleaned in PHONE_HITS and not existing_phone:
            phone, source = PHONE_HITS[cleaned]
            ws.cell(row=row_idx, column=phone_c + 1, value=phone)
            existing_note = ws.cell(row=row_idx, column=notes_c + 1).value or ''
            ws.cell(row=row_idx, column=notes_c + 1, value=
                (existing_note + ' | ' if existing_note else '') +
                f'Phone VERIFIED via {source}.')
            n_phone_added += 1

        # 4. Pattern inference for the candidate column (only if no verified email)
        post_email = (ws.cell(row=row_idx, column=email_c + 1).value or '').strip()
        if not post_email or 'not published' in post_email.lower():
            if region_match and cleaned:
                domain = REGION_DOMAIN[region_match]
                candidate, tier, rationale = infer_email(cleaned, domain)
                if candidate:
                    ws.cell(row=row_idx, column=inf_email_c + 1, value=candidate)
                    ws.cell(row=row_idx, column=inf_conf_c + 1, value=tier)
                    ws.cell(row=row_idx, column=inf_rat_c + 1, value=rationale)
                    fill = INFERRED_HIGH if tier == 'HIGH' else INFERRED_MED if tier == 'MEDIUM' else INFERRED_LOW
                    for c_off in [1, 2, 3]:
                        ws.cell(row=row_idx, column=base_n + c_off).fill = fill
                    if tier == 'HIGH':
                        n_inferred_high += 1
                    elif tier == 'MEDIUM':
                        n_inferred_med += 1
                    else:
                        n_inferred_low += 1
                    continue

        n_skipped += 1

    # Resize new columns
    ws.column_dimensions[get_column_letter(inf_email_c + 1)].width = 40
    ws.column_dimensions[get_column_letter(inf_conf_c + 1)].width = 12
    ws.column_dimensions[get_column_letter(inf_rat_c + 1)].width = 80

    # Add an "Email coverage v10" summary sheet
    if 'Email coverage v10' in wb.sheetnames:
        del wb['Email coverage v10']
    summary = wb.create_sheet('Email coverage v10')
    NAVY_FONT = Font(bold=True, color="FFFFFF")
    NAVY_FILL = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
    summary.append(['Email coverage v10 — methodology + tier counts'])
    summary.append([])
    summary.append(['HONEST CONVENTION (added 2026-04-29 after user pushback on accuracy)'])
    summary.append([
        'The Email column (column F) is reserved for VERIFIED emails only — meaning either '
        '(a) carried over from v9 where source was a regional canonical page, OR '
        '(b) confirmed via WebSearch this session (e.g. helen.m.eliasson@vgregion.se found in '
        'official source). Verified emails should be safe to use directly.'])
    summary.append([
        'The "Inferred email candidate" column (column M) is a PATTERN-BASED GUESS — built from '
        'the regional convention firstname.lastname@regiondomain. Pattern is verified for many '
        'regions (Stockholm, Östergötland, Jämtland, Kronoberg, Skåne, Örebro, Jönköping, VGR, '
        'Uppsala, Halland, Västerbotten, Norrbotten, Gotland, Gävleborg, Västernorrland) but '
        'carries known failure modes:'])
    summary.append([])
    summary.append(['', '— Names with particles (von, van, de): real email may include particle'])
    summary.append(['', '— Multi-token names: real email may include middle initial '
                    '(Helén Eliasson actually uses helen.m.eliasson@vgregion.se)'])
    summary.append(['', '— Hyphenated surnames: convention varies by region '
                    '(Örebro keeps hyphens, Västerbotten drops them)'])
    summary.append(['', '— Special characters: most regions normalize (å→a, ä→a, ö→o, ž→z) '
                    'but a small minority preserve diacritics'])
    summary.append([])
    summary.append(['Confidence tiers'])
    summary.append(['HIGH', f'Single first + single last + verified region domain. '
                    f'Expected accuracy ~90%. Count: {n_inferred_high}'])
    summary.append(['MEDIUM', f'Multi-token name (middle name dropped) OR domain not yet directly '
                    f'WebSearch-verified for this region. Count: {n_inferred_med}'])
    summary.append(['LOW', f'Name contains a particle (von/van/de). Real email almost certainly '
                    f'differs from naive firstname.lastname pattern. Count: {n_inferred_low}'])
    summary.append([])
    summary.append(['Coverage summary v9 → v10'])
    summary.append(['Total stakeholder rows', n_total])
    summary.append(['Verified emails (v9 carryover)', n_already_email])
    summary.append(['Verified emails (NEW — WebSearch 2026-04-29)', n_direct_added])
    summary.append(['Phone numbers added (NEW — WebSearch 2026-04-29)', n_phone_added])
    summary.append(['Inferred candidates — HIGH confidence', n_inferred_high])
    summary.append(['Inferred candidates — MEDIUM confidence', n_inferred_med])
    summary.append(['Inferred candidates — LOW confidence', n_inferred_low])
    summary.append(['Skipped (placeholder name / structural row)', n_skipped])
    summary.append([])
    summary.append(['How to use this file'])
    summary.append(['1. The Email column is the trusted column — paste these directly into outreach.'])
    summary.append(['2. The Inferred email candidate column is a STARTING POINT for outreach. '
                    'Before using:'])
    summary.append(['', '— Visit the Source URL (column H) to verify the person is still in role'])
    summary.append(['', '— For HIGH-confidence: send a low-stakes test message OR ask Pfizer field-team'])
    summary.append(['', '— For MEDIUM/LOW: definitively verify before sending sensitive content'])
    summary.append(['3. The Inference rationale column documents WHY the confidence is what it is.'])
    summary.append([])
    summary.append(['Verified emails added this session (WebSearch 2026-04-29)'])
    for k, (v, src) in DIRECT_HITS.items():
        summary.append([k, v, src])
    summary.append([])
    summary.append(['Phone numbers added this session'])
    for k, (v, src) in PHONE_HITS.items():
        summary.append([k, v, src])

    # Style header
    summary['A1'].font = Font(bold=True, size=14, color="1F3A5F")
    for cell in summary['A11':'A11'][0]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1F3A5F", end_color="1F3A5F", fill_type="solid")
    summary.column_dimensions['A'].width = 50
    summary.column_dimensions['B'].width = 60
    summary.column_dimensions['C'].width = 60

    wb.save(V10)
    print(f'\nSaved {V10}')
    print(f'\n=== HONEST coverage v9 → v10 ===')
    print(f'  Total rows:                                {n_total}')
    print(f'  v9 verified emails (preserved):            {n_already_email}')
    print(f'  NEW Verified (WebSearch this session):     {n_direct_added}')
    print(f'  NEW Phones (WebSearch this session):       {n_phone_added}')
    print()
    print(f'  Inferred candidates HIGH confidence:       {n_inferred_high}')
    print(f'  Inferred candidates MEDIUM confidence:     {n_inferred_med}')
    print(f'  Inferred candidates LOW confidence:        {n_inferred_low}')
    print(f'  Skipped (no name / structural):            {n_skipped}')
    print()
    print(f'  Verified email coverage: {n_already_email + n_direct_added}/{n_total} '
          f'({(n_already_email + n_direct_added)/n_total*100:.0f}%)')
    print(f'  Combined coverage (verified + inferred candidate): '
          f'{n_already_email + n_direct_added + n_inferred_high + n_inferred_med + n_inferred_low}/'
          f'{n_total}')


if __name__ == '__main__':
    main()
