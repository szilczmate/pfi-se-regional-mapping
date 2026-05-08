# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Build 08_PFIZER_THURSDAY_DECK_v5.pptx — surgical v28 integration + 4 backup figure slides.

Approach: copy v4 -> v5, surgically patch text on existing slides, then append 4 new appendix
slides (B5-B8) embedding F5/F8/F6/F7 at their natural aspect ratios (no stretching).

CRITICAL correction propagated: Kisqali (Novartis) is +15.7% GROWING, not part of "mutual stall".
P2 narrative shifts to "defend against Kisqali" not "defend against compounding Verzenios".
"""

from copy import deepcopy
from pathlib import Path
from shutil import copyfile

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from PIL import Image

ROOT = Path(r"C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main")
V4 = ROOT / "delivery" / "08_PFIZER_THURSDAY_DECK_v4.pptx"
V5 = ROOT / "delivery" / "08_PFIZER_THURSDAY_DECK_v5.pptx"
FIG_DIR = ROOT / "delivery" / "figures"

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
DARKGREY = RGBColor(0x44, 0x44, 0x44)
LIGHTGREY = RGBColor(0x88, 0x88, 0x88)
ACCENT = RGBColor(0x00, 0x93, 0xD0)

SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5


# ============================================================================
# Helpers — text patching that preserves run-level formatting
# ============================================================================

def replace_in_text_frame(tf, search, replace):
    """Replace `search` with `replace` in a text frame, preserving run formatting where possible."""
    full_text = tf.text
    if search not in full_text:
        return False

    # If the search appears entirely within a single run, do a clean replacement
    for paragraph in tf.paragraphs:
        for run in paragraph.runs:
            if search in run.text:
                run.text = run.text.replace(search, replace)
                return True

    # Multi-run case — fall back to writing into the first run, clearing the others
    # (only used for less-common cases)
    for paragraph in tf.paragraphs:
        if search in paragraph.text:
            new_text = paragraph.text.replace(search, replace)
            if paragraph.runs:
                paragraph.runs[0].text = new_text
                for run in paragraph.runs[1:]:
                    run.text = ''
            return True
    return False


def find_shape_by_text(slide, text_substring):
    for shape in slide.shapes:
        if shape.has_text_frame and text_substring in shape.text_frame.text:
            return shape
    return None


def append_run_to_text_frame(tf, text, *, bold=False, italic=False, size=10, color=None):
    """Append a new paragraph + run with the given text & formatting at the end of tf."""
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = text
    r.font.bold = bold
    r.font.italic = italic
    r.font.size = Pt(size)
    if color is not None:
        r.font.color.rgb = color


# ============================================================================
# Per-slide surgical edits
# ============================================================================

def edit_slide_1(slide):
    """Slide 1 (cover): update subtitle from v4 to v5."""
    print('  Slide 1: cover subtitle')
    for shape in slide.shapes:
        if shape.has_text_frame:
            replace_in_text_frame(shape.text_frame,
                'STRATEGIC PLAN — VS-2026-PFI-001 · v4 (workbook v27, Codex audit v2 corrections)',
                'STRATEGIC PLAN — VS-2026-PFI-001 · v5 (workbook v28, A+B+C deferred analyses)')


def edit_slide_3(slide):
    """Slide 3 (Five plays): P2 description gets Kisqali correction."""
    print('  Slide 3: P2 description — Kisqali correction')
    for shape in slide.shapes:
        if shape.has_text_frame:
            replace_in_text_frame(shape.text_frame,
                "Defend Pfizer's third-place CDK4/6 position. Verzenios national leader (39%); Halland the only Pfizer-leading region (51",
                "Defend Pfizer's third-place CDK4/6 position. v5: Kisqali (Novartis) +15.7% is the live share-gainer; Ibrance −3.0% and Verzenios −0.1% both PLATEAUING (last-6 vs prev-6 mo). Halland 51")


def edit_slide_6(slide):
    """Slide 6 (Abrysvo): add Stockholm MINORITY footnote."""
    print('  Slide 6: Abrysvo — Stockholm MINORITY footnote')
    # Find the "What it means for P3" body text shape and append a v5 note
    for shape in slide.shapes:
        if shape.has_text_frame and 'If regions are buying despite the formal hold' in shape.text_frame.text:
            append_run_to_text_frame(shape.text_frame,
                'v5 (workbook v28): Stockholm-specific anomaly — Abrysvo Stockholm 45.6% MINORITY by units '
                '(Arexvy leads at 54.4%). Stockholm requires Abrysvo-vs-Arexvy tactic, not the national '
                'avvakta-override message.',
                bold=False, italic=True, size=9, color=DARKGREY)
            return


def edit_slide_7(slide):
    """Slide 7 (Prevenar 20): add Stockholm Vaxneuvance lead footnote."""
    print('  Slide 7: Prevenar 20 — Stockholm Vaxneuvance footnote')
    for shape in slide.shapes:
        if shape.has_text_frame and 'Prevenar 13 is sunsetting' in shape.text_frame.text:
            append_run_to_text_frame(shape.text_frame,
                'v5 (workbook v28): Stockholm pneumococcal class is led by Vaxneuvance (MSD) at 71.5% units; '
                'Prevenar 20 at 28%; PCV13 at 0.5%. The displacement target in Stockholm is Vaxneuvance, '
                'not legacy PCV13.',
                bold=False, italic=True, size=9, color=DARKGREY)
            return


def edit_slide_11(slide):
    """Slide 11 (90 days): P2 row — sharpen Kisqali language."""
    print('  Slide 11: P2 row — Kisqali specificity')
    # Find the P2 lead-action cell and update
    for shape in slide.shapes:
        if shape.has_text_frame and 'Verzenios + Kisqali competitive monitoring' in shape.text_frame.text:
            replace_in_text_frame(shape.text_frame,
                'Verzenios + Kisqali competitive monitoring (monthly IQVIA pull); open Stockholm + VGR LK dialogue on outcomes-based agreement using Halland (51% Pfizer share) as the reference case.',
                'Defend against Kisqali (the live +15.7% gainer); Verzenios + Ibrance both plateaued. Open Stockholm + VGR LK dialogue on outcomes-based agreement using Halland (51% Pfizer share) as the reference case.')
            return


def edit_slide_12(slide):
    """Slide 12 (validation gates): Gate 1 closure note — Kisqali correction."""
    print('  Slide 12: Gate 1 — Kisqali correction in closure note')
    for shape in slide.shapes:
        if shape.has_text_frame and 'Closed today via IQVIA Oncology extract' in shape.text_frame.text:
            # The full text mentions "Verzenios is the larger competitor by units" — patch
            replace_in_text_frame(shape.text_frame,
                'Substitution direction confirmed; Verzenios is the larger competitor by units (39% national vs Kisqali 33% vs Ibrance ',
                'v5 refinement: at the 6+6-month most-recent-window time-scale, Kisqali (+15.7%) is the live CDK4/6 share-gainer; Verzenios (−0.1%) and Ibrance (−3.0%) both PLATEAUING. National class shares: Verzenios 39% / Kisqali 33% / Ibrance ')
            return


def edit_slide_16(slide):
    """Slide 16 (Plays scenarios B4): P2 Conservative — sharpen with Kisqali +15.7%."""
    print('  Slide 16: P2 Conservative scenario — Kisqali +15.7%')
    for shape in slide.shapes:
        if shape.has_text_frame and 'Three-way race stabilises at ~Verzenios 40%' in shape.text_frame.text:
            replace_in_text_frame(shape.text_frame,
                'Three-way race stabilises at ~Verzenios 40% / Kisqali 33% / Ibrance 28%. Last-6mo Verzenios PLATEAUING. Without action, Kisqali takes incremental share. Ibrance ~614 patients (-31M SEK gross).',
                'Class shares: Verzenios 40% / Kisqali 33% / Ibrance 28%. Last-6 vs prev-6: Kisqali +15.7% GROWING (live gainer); Verzenios −0.1% PLATEAUING; Ibrance −3.0% PLATEAUING. Without action, Kisqali takes incremental share. Ibrance ~614 patients (-31M SEK gross).')
            return


def update_page_numbers(prs, new_total):
    """Replace 'X / 16' page-number footers with 'X / new_total' on all slides."""
    print(f'  Updating page numbers to / {new_total}')
    n_changed = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            # Pattern is "N / 16" — slide number / total
            for paragraph in tf.paragraphs:
                for run in paragraph.runs:
                    if ' / 16' in run.text:
                        # Only patch if it looks like a page number (short text)
                        if len(run.text) < 12:
                            run.text = run.text.replace(' / 16', f' / {new_total}')
                            n_changed += 1
    print(f'    {n_changed} page-number runs patched')


# ============================================================================
# New appendix backup slides — F5 / F6 / F7 / F8
# ============================================================================

def add_appendix_slide(prs, *, label, title, subtitle, figure_path, caption,
                      max_fig_w_in=11.5, max_fig_h_in=4.8, page_num=None, page_total=20):
    """Add a backup-style appendix slide with figure preserving aspect ratio.

    Layout (slide is 13.33 × 7.5 inches):
      0.45 → 0.85   small grey label "BACKUP · BX"
      0.90 → 1.55   navy bold title
      1.60 → 1.95   subtitle (one line, dark grey)
      2.10 → 6.90   figure region (centered, max_fig_w_in × max_fig_h_in)
      6.95 → 7.20   italic caption (one line)
      7.20 → 7.40   page number + viti footer
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Determine actual figure dims (preserve aspect ratio)
    img = Image.open(str(figure_path))
    img_w, img_h = img.size
    ratio = img_w / img_h
    # Try max_fig_w first
    fit_w = max_fig_w_in
    fit_h = fit_w / ratio
    if fit_h > max_fig_h_in:
        fit_h = max_fig_h_in
        fit_w = fit_h * ratio
    fig_left = (SLIDE_W_IN - fit_w) / 2

    # Determine y placement: center the figure in the available 2.10-6.90 band (mid 4.50)
    avail_top, avail_bot = 2.10, 6.90
    avail_mid = (avail_top + avail_bot) / 2
    fig_top = avail_mid - fit_h / 2

    # Label (small grey, top left)
    txt = slide.shapes.add_textbox(Inches(0.45), Inches(0.40), Inches(6.0), Inches(0.40))
    tf = txt.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = label
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = LIGHTGREY
    r.font.name = 'Calibri'

    # Title (large navy bold)
    txt = slide.shapes.add_textbox(Inches(0.45), Inches(0.85), Inches(12.5), Inches(0.65))
    tf = txt.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = NAVY
    r.font.name = 'Calibri'

    # Subtitle (dark grey, smaller)
    txt = slide.shapes.add_textbox(Inches(0.45), Inches(1.55), Inches(12.5), Inches(0.40))
    tf = txt.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = subtitle
    r.font.size = Pt(13)
    r.font.color.rgb = DARKGREY
    r.font.name = 'Calibri'

    # Add the figure at preserved aspect ratio
    slide.shapes.add_picture(str(figure_path),
                             Inches(fig_left), Inches(fig_top),
                             width=Inches(fit_w), height=Inches(fit_h))

    # Caption (italic dark grey, just under figure)
    cap_y = fig_top + fit_h + 0.05
    cap_y = min(cap_y, 6.95)
    txt = slide.shapes.add_textbox(Inches(0.7), Inches(cap_y), Inches(12.0), Inches(0.30))
    tf = txt.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = caption
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = DARKGREY
    r.font.name = 'Calibri'

    # Footer: page number (right) + viti footer (left)
    if page_num is not None:
        txt = slide.shapes.add_textbox(Inches(11.5), Inches(7.20), Inches(1.5), Inches(0.30))
        tf = txt.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        r = p.add_run()
        r.text = f'{page_num} / {page_total}'
        r.font.size = Pt(9)
        r.font.color.rgb = LIGHTGREY
        r.font.name = 'Calibri'

    txt = slide.shapes.add_textbox(Inches(0.45), Inches(7.20), Inches(10.0), Inches(0.30))
    tf = txt.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = 'Viti Science · Pfizer Sweden Regional Landscape · April 2026'
    r.font.size = Pt(9)
    r.font.color.rgb = LIGHTGREY
    r.font.name = 'Calibri'

    return slide


# ============================================================================
# Main
# ============================================================================

def main():
    print(f'Copying v4 → v5')
    copyfile(V4, V5)
    prs = Presentation(str(V5))

    print(f'\nLoaded v5 deck ({len(prs.slides)} slides, {prs.slide_width / 914400:.2f} × '
          f'{prs.slide_height / 914400:.2f} in)')

    # ----- Surgical text edits to existing 16 slides -----
    print('\n=== Surgical text edits ===')
    slides = list(prs.slides)
    edit_slide_1(slides[0])
    edit_slide_3(slides[2])
    edit_slide_6(slides[5])
    edit_slide_7(slides[6])
    edit_slide_11(slides[10])
    edit_slide_12(slides[11])
    edit_slide_16(slides[15])

    # ----- Add 4 backup appendix slides -----
    print('\n=== Adding 4 backup appendix slides ===')
    add_appendix_slide(prs,
        label='BACKUP · B5',
        title='CDK4/6 trajectory — Kisqali (Novartis) is the live gainer',
        subtitle='Last-6 vs prev-6 month IQVIA units. Pfizer Ibrance and Lilly Verzenios both plateaued; '
                 'Novartis Kisqali +15.7% GROWING — P2 strategic implication: defend against Kisqali specifically.',
        figure_path=FIG_DIR / 'F5_cdk46_mutual_stall.png',
        caption='F5 · Source: IQVIA Oncology 2026-04-27 · Three-panel national monthly trajectory · Workbook v28 sheet "Competitive class trajectories"',
        max_fig_w_in=12.0, max_fig_h_in=4.5,
        page_num=17)
    print('  Added B5 (F5 — CDK4/6 trajectory)')

    add_appendix_slide(prs,
        label='BACKUP · B6',
        title='Multi-class verdict view — 12 products at a glance',
        subtitle='Of seven major competitors, three PLATEAUING or DECLINING (Verzenios, Alecensa, Lynparza). '
                 'Pfizer side: Vyndaqel HOLDING +3.4%; Tukysa breakout +29.9%; Ibrance plateaued −3.0%.',
        figure_path=FIG_DIR / 'F8_multiclass_verdict_view.png',
        caption='F8 · Source: IQVIA RD/IM 2026-04-27 + Oncology 2026-04-27 · Last-6 vs prev-6 mo IQVIA units · Pfizer products marked navy',
        max_fig_w_in=10.5, max_fig_h_in=5.0,
        page_num=18)
    print('  Added B6 (F8 — multi-class verdict view)')

    add_appendix_slide(prs,
        label='BACKUP · B7',
        title='Vyndaqel anchor: HOLDING through ATTR competitor entry',
        subtitle='Vyndaqel +3.4% PLATEAUING-positive last-6 vs prev-6 despite AMVUTTRA + BEYONTTRA Sweden launch. '
                 'Combined competitor volume = 4.5% of Vyndaqel last-6. P1 anchor durability is now Observed.',
        figure_path=FIG_DIR / 'F6_vyndaqel_anchor_durability.png',
        caption='F6 · Top: Vyndaqel monthly bars (national). Bottom: AMVUTTRA + BEYONTTRA on zoomed scale showing post-launch entry. Source: IQVIA RD/IM 2026-04-27.',
        max_fig_w_in=11.5, max_fig_h_in=4.6,
        page_num=19)
    print('  Added B7 (F6 — Vyndaqel anchor durability)')

    add_appendix_slide(prs,
        label='BACKUP · B8',
        title='Precision oncology split: Tukysa wins, Talzenna sits in a contracting class',
        subtitle='Tukysa +29.9% near compounding boundary; Talzenna −16.0% and Lynparza −8.4% both DECLINING. '
                 'P4 plays brief should weight Tukysa as LEAD, Talzenna as a holding/secondary bet.',
        figure_path=FIG_DIR / 'F7_precision_oncology_split.png',
        caption='F7 · Left: Tukysa national monthly trajectory. Right: Talzenna (left axis) + Lynparza (right axis) — both PARP products declining. Source: IQVIA Oncology 2026-04-27.',
        max_fig_w_in=12.0, max_fig_h_in=4.5,
        page_num=20)
    print('  Added B8 (F7 — precision oncology split)')

    # ----- Update all "X / 16" → "X / 20" -----
    print('\n=== Updating page numbers ===')
    update_page_numbers(prs, 20)

    prs.save(str(V5))
    print(f'\nSaved {V5} ({len(prs.slides)} slides total)')


if __name__ == '__main__':
    main()
