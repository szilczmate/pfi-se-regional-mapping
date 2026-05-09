# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull FHM RSV regional surveillance (if available) via the sminet3 mapapp CSV pattern.

FHM publishes weekly/yearly per-region CSVs at:
  https://sminet3-prod.sminet.se/mapapp/{disease}_ySWE_ALL_{date}.csv

RSV may be exposed as 'rsv' or 'rsvirus'. We try several slugs.
Fallback: search Socialstyrelsen Patientregistret via WebSearch (documented here but separate step).
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, csv
from pathlib import Path
from datetime import date

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")

# Try several dates and slugs (FHM rotates filename dates)
SLUGS = ["rsv", "rsvirus", "rsvinfektion", "rsinfektion", "rsinfection"]
DATES = ["20260430", "20260416", "20260401", "20260315", "20260301", "20260228", "20260215"]

REGION_MAP = {
    "Stockholm": "01", "Uppsala": "03", "Södermanland": "04", "Östergötland": "05",
    "Jönköping": "06", "Kronoberg": "07", "Kalmar": "08", "Gotland": "09",
    "Blekinge": "10", "Skåne": "12", "Halland": "13", "Västra Götaland": "14",
    "Värmland": "17", "Örebro": "18", "Västmanland": "19", "Dalarna": "20",
    "Gävleborg": "21", "Västernorrland": "22", "Jämtland": "23", "Västerbotten": "24",
    "Norrbotten": "25",
    "Stockholms län": "01", "Uppsala län": "03", "Södermanlands län": "04",
    "Östergötlands län": "05", "Jönköpings län": "06", "Kronobergs län": "07",
    "Kalmar län": "08", "Gotlands län": "09", "Blekinge län": "10", "Skåne län": "12",
    "Hallands län": "13", "Västra Götalands län": "14", "Värmlands län": "17",
    "Örebro län": "18", "Västmanlands län": "19", "Dalarnas län": "20",
    "Gävleborgs län": "21", "Västernorrlands län": "22", "Jämtlands län": "23",
    "Västerbottens län": "24", "Norrbottens län": "25",
}

found = None
for slug in SLUGS:
    for d in DATES:
        url = f"https://sminet3-prod.sminet.se/mapapp/{slug}_ySWE_ALL_{d}.csv"
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and len(r.content) > 500 and b"region" in r.content.lower()[:2000]:
                print(f"  HIT: {slug} / {d} — {len(r.content)} bytes")
                found = (slug, d, r)
                break
            elif r.status_code == 200:
                print(f"  {slug}/{d}: OK but small ({len(r.content)}b)")
            else:
                print(f"  {slug}/{d}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  {slug}/{d}: {e.__class__.__name__}")
    if found: break

if not found:
    print("\nRSV CSV not discoverable via sminet3 pattern. Fallback: RSV is only in national weekly reports.")
    print("Document this as a structural limitation.")
    sys.exit(0)

slug, d, r = found
raw_path = OUT_RAW / f"fhm_rsv_raw_{d}.csv"
raw_path.write_bytes(r.content)
print(f"Saved raw: {raw_path}")

# Parse
text = r.text
reader = csv.reader(text.splitlines(), skipinitialspace=True)
rows = list(reader)
print(f"Rows: {len(rows)}")
print("First 3 rows:")
for row in rows[:3]:
    print(f"  {row}")
