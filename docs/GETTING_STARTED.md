# Getting Started

## 1. Install

```bash
pip install anu-architecture
```

Verify:

```bash
anu-architecture --version
```

## 2. Scaffold a project

```bash
anu-architecture init my-study
```

You'll be prompted for:

- **Project name** (defaults to the dir name)
- **Language**: Python / R / Stata / Mixed
- **Studies**: how many, names
- **Data sources**: comma-separated

The scaffold writes:

```
my-study/
├── README.md
├── run.py                       # Master orchestrator
├── project_registry.json        # Single source of truth
├── DECISION_LOG.md              # Document every design decision
├── CHECKLIST.md                 # Auto-populated
├── code/
│   ├── setup/        S##        # Package install, env config
│   ├── loading/      L##        # Data loaders (one per source)
│   ├── processing/   P##        # Construction
│   ├── validation/   V##        # Data + model diagnostics
│   ├── manual/       M##        # Documented adjustments
│   ├── analysis/     A##        # Estimation + robustness
│   ├── outputs/      O##        # Final outputs (runs LAST)
│   └── exploration/  E##        # Ephemeral exploration
├── data/{user-inputs,raw-data,int-data,final-data,adjusted-final-data,scratch}/
├── outputs/{validation,analysis,exploration,deliverables}/
├── utils/
├── logs/
├── docs/
└── .gitignore
```

## 3. Add data sources

Edit `code/loading/L01_<source>.py` (a stub was generated). Every L## must
document its source:

```python
"""
L01: Load FRED INDPRO
====================
Phase:   Loading
Purpose: Fetch monthly industrial production index from FRED.
Public Source: https://fred.stlouisfed.org/series/INDPRO
Units:   Index, 2017=100
"""
```

## 4. Run the pipeline

```bash
cd my-study
python run.py --dry-run        # See what would execute
python run.py --setup-only     # Just S##
python run.py --from P         # Resume from processing phase
python run.py                  # Full pipeline
```

## 5. Check status

```bash
anu-architecture status
```

Reports: studies defined, scripts written per phase, data loaded, analyses
complete, outputs generated.

## 6. Audit before publishing

```bash
anu-architecture audit
```

Scans for hardcoded local paths, missing PUBLIC SOURCE: headers in L##
scripts, synthetic-data heuristics. Refuses to pass if any FAIL hits.

## Next

- [`THE_8_PHASES.md`](THE_8_PHASES.md) — what each phase does and doesn't do
- [`PROJECT_REGISTRY.md`](PROJECT_REGISTRY.md) — the single-source-of-truth file
- [`PUBLIC_REPRODUCIBILITY.md`](PUBLIC_REPRODUCIBILITY.md) — the no-synthetic-data contract
- [`COMPARISONS.md`](COMPARISONS.md) — Anu Architecture vs other standards
