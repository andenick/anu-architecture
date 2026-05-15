"""L01: Load FRED INDPRO
====================
Phase:   Loading
Purpose: Fetch Industrial Production Index from FRED.
Public Source: https://fred.stlouisfed.org/series/INDPRO
Units:   Index, 2017=100
Vintage: 2026-05-15
"""
import csv
import os
from pathlib import Path
from urllib.request import urlopen

PROJECT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT / "data" / "raw-data"
RAW_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("FRED_API_KEY", "")
if not API_KEY:
    print("WARN: FRED_API_KEY not set. Falling back to public download URL.")
    URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO"
    with urlopen(URL) as r:
        text = r.read().decode("utf-8")
    out = RAW_DIR / "indpro.csv"
    out.write_text(text)
    print(f"  Wrote {out}")
else:
    # API path here (omitted for brevity)
    pass
