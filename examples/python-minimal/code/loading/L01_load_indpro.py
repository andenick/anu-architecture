"""L01: Load FRED INDPRO
====================
Phase:   Loading
Purpose: Fetch Industrial Production Index from FRED.
Public Source: https://fred.stlouisfed.org/series/INDPRO
Units:   Index, 2017=100
Vintage: 2026-05-15
"""
from pathlib import Path
from urllib.request import urlopen

PROJECT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT / "data" / "raw-data"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# This example deliberately uses FRED's public CSV download URL rather than
# the keyed API, so it runs identically for everyone with no registration.
# A real L## script would try the public API first (see docs/SPEC.md,
# "Data Acquisition Priority") and fall back to this URL when no key is set.
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO"

with urlopen(URL) as r:
    text = r.read().decode("utf-8")

out = RAW_DIR / "indpro.csv"
out.write_text(text)
print(f"  Wrote {out}")
