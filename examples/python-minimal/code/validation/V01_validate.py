"""V01: Validate INDPRO annual data
====================
Phase:   Validation
Purpose: Check completeness, monotonicity of years, plausible range.
Inputs:  data/final-data/indpro_annual.csv
Outputs: logs/validation/V01_indpro.json
"""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "data" / "final-data" / "indpro_annual.csv"
log_path = PROJECT / "logs" / "validation" / "V01_indpro.json"
log_path.parent.mkdir(parents=True, exist_ok=True)

checks = {}
years = []
values = []
with src.open() as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        years.append(int(row[0]))
        values.append(float(row[1]))

checks["n_years"] = len(years)
checks["years_monotonic"] = years == sorted(years)
checks["values_plausible"] = all(0.1 < v < 1000 for v in values)
checks["status"] = "PASS" if all([checks["years_monotonic"], checks["values_plausible"]]) else "FAIL"

log_path.write_text(json.dumps(checks, indent=2))
print(f"  V01: {checks['status']}  ({checks['n_years']} years)")
