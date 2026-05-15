"""A01: Long-run INDPRO growth summary
====================
Phase:   Analysis
Purpose: Compute geometric annual growth rate.
Inputs:  data/final-data/indpro_annual.csv
Outputs: outputs/analysis/A01_growth.json
Studies: STUDY_01
"""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "data" / "final-data" / "indpro_annual.csv"
out_path = PROJECT / "outputs" / "analysis" / "A01_growth.json"
out_path.parent.mkdir(parents=True, exist_ok=True)

years, values = [], []
with src.open() as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        years.append(int(row[0]))
        values.append(float(row[1]))

n_years = years[-1] - years[0]
ratio = values[-1] / values[0]
annual_growth = ratio ** (1 / n_years) - 1
result = {
    "start_year": years[0], "end_year": years[-1],
    "start_value": values[0], "end_value": values[-1],
    "annual_growth_pct": annual_growth * 100,
}
out_path.write_text(json.dumps(result, indent=2))
print(f"  A01: {result['annual_growth_pct']:.2f}% annual growth")
