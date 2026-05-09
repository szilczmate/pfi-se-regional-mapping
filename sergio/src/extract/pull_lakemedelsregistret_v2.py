# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Läkemedelsregistret pull — v2 with CSV download via __doPostBack.

Approach:
  1. Build form via Playwright clicks (proven working in v1)
  2. Submit to resultat.aspx (GridView renders with data)
  3. Trigger CSV download via __doPostBack('ctl00$ph1$lbCSV','')
  4. Save CSV per ATC
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_RAW.mkdir(exist_ok=True, parents=True)

ATCS = [
    ("L01EF01", "Ibrance"),
    ("N07XX08", "Vyndaqel"),
    ("L01XK04", "Talzenna"),   # corrected from L01XX60 (2026-04-24); Talzenna is in PARP inhibitor class L01XK, not misc L01XX
    ("L01ED04", "Lorbrena"),
    ("L01EH03", "Tukysa"),
    ("N02CD06", "Vydura"),
    ("J05AE30", "Paxlovid"),
]
YEARS = ["2024","2023","2022","2021"]
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]
AGES = [str(i) for i in range(1, 19)]
DATE = "20260424"

import os
if os.environ.get("ATC_ONE"):
    ATCS = ATCS[:1]
elif os.environ.get("ATC_LIMIT"):
    ATCS = ATCS[:int(os.environ["ATC_LIMIT"])]

def pull_atc(page, atc, brand):
    print(f"\n=== {atc} ({brand}) ===")
    page.goto("https://sdb.socialstyrelsen.se/if_lak/val.aspx", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(700)

    page.fill("#Sokord", atc)
    page.press("#Sokord", "Enter")
    page.wait_for_timeout(1500)

    cc_call = page.evaluate("""() => {
        const link = document.querySelector('#sokListaArea a[href*="cc("]');
        const m = link && link.getAttribute('href').match(/cc\\('([^']+)'\\)/);
        return m ? m[1] : null;
    }""")
    if not cc_call:
        print(f"  [SKIP] ATC not found in register")
        return None
    print(f"  ATC ref: {cc_call}")
    page.evaluate(f"cc('{cc_call}')")
    page.wait_for_timeout(400)

    page.select_option("#OMR", value=REGIONS)
    page.evaluate("antal_Omr()")
    page.select_option("#AGI", value=AGES)
    page.evaluate("antal('AGI')")
    page.select_option("#AR", value=YEARS)
    page.evaluate("antal('AR')")
    page.select_option("#KON", value="3")
    page.evaluate("antal('KON')")
    page.evaluate("cc_matt('matti_1_1')")
    page.wait_for_timeout(400)

    dia_c = page.evaluate("document.getElementById('aDIA').innerHTML")
    omr_c = page.evaluate("document.getElementById('aOMR').innerHTML")
    agi_c = page.evaluate("document.getElementById('aAGI').innerHTML")
    ar_c = page.evaluate("document.getElementById('aAR').innerHTML")
    matt_c = page.evaluate("document.getElementById('aMATT').innerHTML")
    print(f"  Fields: DIA={dia_c}  OMR={omr_c}  AGI={agi_c}  AR={ar_c}  MATT={matt_c}")

    # Submit
    page.evaluate("submitResultat()")
    page.wait_for_url("**/resultat.aspx", timeout=60000)
    # Wait for GridView to render
    try:
        page.wait_for_selector("table[id*='GridView1']", timeout=30000)
    except:
        body = page.inner_text("body")[:500]
        print(f"  [FAIL] No GridView: {body}")
        return None
    page.wait_for_timeout(1000)

    # Check for error
    body = page.inner_text("body")
    if "Kan ej visa" in body:
        print(f"  [FAIL] Error page")
        return None

    # Trigger CSV download via __doPostBack
    with page.expect_download(timeout=30000) as dl_info:
        page.evaluate("__doPostBack('ctl00$ph1$lbCSV','')")
    dl = dl_info.value
    dest = OUT_RAW / f"sos_rx_{atc}_{DATE}.csv"
    dl.save_as(dest)
    print(f"  [OK] Saved: {dest.name} ({dest.stat().st_size:,} bytes)")
    return dest

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(accept_downloads=True)
    page = ctx.new_page()

    results = {}
    for atc, brand in ATCS:
        try:
            results[atc] = pull_atc(page, atc, brand)
        except Exception as e:
            print(f"  [EXCEPTION] {atc}: {type(e).__name__}: {str(e)[:300]}")
            results[atc] = None

    browser.close()

print("\n=== Summary ===")
for atc, path in results.items():
    brand = next(b for a, b in ATCS if a == atc)
    tag = "[OK]" if path else "[FAIL]"
    print(f"  {tag} {atc} ({brand}): {path}")
