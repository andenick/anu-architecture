# python-minimal example

A minimal Anu Architecture project demonstrating the full pipeline on one
public series: FRED INDPRO (Industrial Production Index).

## Run

```bash
python run.py
```

No API key required — uses FRED's public CSV download URL.

## What runs

| Phase | Script | Purpose |
|---|---|---|
| L | `L01_load_indpro.py` | Download from `fred.stlouisfed.org` |
| P | `P01_annual_avg.py` | Monthly → annual averages |
| V | `V01_validate.py` | Completeness + plausibility |
| A | `A01_growth.py` | Long-run geometric growth rate |
| O | `O01_table.py` | Markdown summary table |

## Outputs

- `outputs/analysis/A01_growth.json` — growth rate result
- `outputs/deliverables/tables/growth_summary.md` — human-readable summary
