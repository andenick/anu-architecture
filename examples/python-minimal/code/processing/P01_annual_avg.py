"""P01: Compute annual averages of INDPRO
====================
Phase:   Processing
Purpose: Convert monthly INDPRO to annual averages.
Inputs:  data/raw-data/indpro.csv
Outputs: data/final-data/indpro_annual.csv
"""
import csv
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "data" / "raw-data" / "indpro.csv"
dst = PROJECT / "data" / "final-data" / "indpro_annual.csv"
dst.parent.mkdir(parents=True, exist_ok=True)

annual = defaultdict(list)
with src.open() as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 2 or not row[0]:
            continue
        year = row[0][:4]
        try:
            val = float(row[1])
        except ValueError:
            continue
        annual[year].append(val)

with dst.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "indpro_annual"])
    for year in sorted(annual):
        avg = sum(annual[year]) / len(annual[year])
        w.writerow([year, f"{avg:.4f}"])
print(f"  Wrote {dst}")
