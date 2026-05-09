# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
"""Pull SCB sub-demographics: foreign-born %, education levels per region."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests, json, csv
from pathlib import Path
from collections import defaultdict

OUT_RAW = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/raw")
OUT_INT = Path("C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/interim")
REGIONS = ["01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20","21","22","23","24","25"]

# Foreign-born: BE/BE0101/BE0101E - Befolkning efter födelseregion, alder, kön, år
# Educational attainment: UF/UF0506/UF0506B - Utbildningsnivå
print("=== Foreign-born population per region ===")
URL_FB = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101E/UtrikesFoddaR"
try:
    meta = requests.get(URL_FB, timeout=30).json()
    print("Variables in UtrikesFoddaR:")
    for v in meta.get("variables", []):
        print(f"  {v['code']:<15} {len(v.get('values', []))} values")
        if v['code'] == 'Tid':
            print(f"    latest year: {v['values'][-1]}")
        if v['code'] == 'ContentsCode':
            for code, txt in zip(v['values'], v.get('valueTexts', v['values'])):
                print(f"    contents: {code} - {txt}")
except Exception as e:
    print(f"  Table not found: {e}")

# Try alternative — look at births by mother's country of birth or just get basic pop by origin
print("\n=== Trying BE0101E tables ===")
r = requests.get("https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101E", timeout=30).json()
for x in r:
    print(f"  {x.get('id'):<25} {x.get('text')[:80]}")
