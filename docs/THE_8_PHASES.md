# The 8 Phases

The Anu Architecture organizes every script into one of eight phases. The
prefix declares the phase; the number declares execution order within the
phase.

## S## — Setup

**Purpose**: Package installation, environment config, API key validation,
path-existence checks. Runs first.

**Reads**: nothing (validates the system).
**Writes**: `logs/setup/`.

Example: `S01_install_packages.py`, `S02_validate_api_keys.py`.

## L## — Load

**Purpose**: Pull raw data from files and APIs into a standardized format.
Every L## must document:

- **Public Source** (URL)
- **API endpoint** or **download path**
- **Units** (e.g., `billions_usd`)
- **Vintage** (when the data was fetched)

**Reads**: `data/user-inputs/`, external APIs, project `Inputs/`.
**Writes**: `data/raw-data/`.

## P## — Process

**Purpose**: Clean, transform, merge, reshape, construct analysis-ready
datasets.

**Reads**: `data/raw-data/`.
**Writes**: `data/int-data/` (checkpoints) and `data/final-data/` (final).

## V## — Validate

**Two passes**:

1. **Pre-analysis**: data integrity, completeness, distributions, cross-checks
   on `data/final-data/`.
2. **Post-analysis**: model diagnostics (Sargan, AR tests, Hausman,
   specification tests) on `outputs/analysis/`.

**Writes**: `logs/validation/`, `outputs/validation/`.

## M## — Manual Adjust

**Purpose**: Documented, justified manual corrections with full audit trail.

Every M## adjustment requires **all five**:

1. **Specific reason** (not "data looks wrong")
2. **Evidence** (source documentation)
3. **Original values**
4. **Adjusted values**
5. **Reversibility**

**Reads**: `data/final-data/`.
**Writes**: `data/adjusted-final-data/` — *never* writes to `final-data/`.

## A## — Analyze

**Purpose**: Econometric estimation, statistical tests, robustness,
cross-model comparison.

**Reads**: `data/final-data/` or `data/adjusted-final-data/`.
**Writes**: `outputs/analysis/`.

## O## — Output

**Purpose**: Publication-quality tables, figures, reports.

**Runs LAST.** Reads `outputs/analysis/`, writes `outputs/deliverables/`.

## E## — Explore

**Purpose**: Standalone exploratory scripts. New methods, data sources,
sensitivity scans.

**Outputs are ephemeral** (`data/scratch/`). E## scripts are **never
deleted** — they are the permanent record of the research process.
Conclusions flow to `DECISION_LOG.md`.

## Execution order

```
S## -> L## -> P## (+ E## concurrent) -> V## -> M## -> A## -> V## (diagnostics) -> O##
```

The master orchestrator (`run.py`) discovers scripts via glob
(`code/loading/L[0-9][0-9]_*.py`) and runs them in numeric order.

## Why not "just" cookiecutter-data-science?

See [`COMPARISONS.md`](COMPARISONS.md).
