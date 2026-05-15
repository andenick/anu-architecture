"""O01: Render summary table
====================
Phase:   Output
Purpose: Generate publication-quality summary.
Inputs:  outputs/analysis/A01_growth.json
Outputs: outputs/deliverables/tables/growth_summary.md
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "outputs" / "analysis" / "A01_growth.json"
out = PROJECT / "outputs" / "deliverables" / "tables" / "growth_summary.md"
out.parent.mkdir(parents=True, exist_ok=True)

r = json.loads(src.read_text())
out.write_text(
    f"# INDPRO Growth Summary\n\n"
    f"| Metric | Value |\n"
    f"|---|---|\n"
    f"| Period | {r['start_year']}–{r['end_year']} |\n"
    f"| Start value | {r['start_value']:.2f} |\n"
    f"| End value | {r['end_value']:.2f} |\n"
    f"| Annual growth | {r['annual_growth_pct']:.2f}% |\n"
)
print(f"  Wrote {out}")
