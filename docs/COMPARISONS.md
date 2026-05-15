# Anu Architecture vs other standards

| Feature | Anu Architecture | cookiecutter-data-science | Project TIER 4.0 | dbt |
|---|---|---|---|---|
| Folder structure | Prescribed 8-phase | Prescribed 5-phase | Prescribed | Convention-based |
| Phases | S/L/P/V/M/A/O/E | data/raw, data/processed, models, reports | Inputs/Command/Output | models/, tests/ |
| Master orchestrator | `run.py` (glob discovery) | None | None | `dbt run` |
| Validation phase | First-class (V##) | None | None | `dbt test` |
| Manual adjustments | First-class (M##) | None | Documented | None |
| Exploration preservation | E## scripts, never deleted | notebooks/ | Not formalized | None |
| Registry-driven | `project_registry.json` | None | None | `schema.yml` |
| No synthetic data | Mandatory, enforced | Not addressed | Not addressed | Not addressed |
| No proxy substitution | Mandatory unless justified | Not addressed | Not addressed | Not addressed |
| Audit trail | Structured JSON per script | None | README | Run logs |
| Language | Python / R / Stata / mixed | Python | Any | SQL |
| Versioning | Snake-shedding (`_archive/vN/`) | git only | git only | git only |

## When to choose Anu Architecture

- Original econometric research (panel, time-series, empirical testing)
- Dissertation work — multi-test, robustness-heavy
- Multi-source data construction where provenance matters
- You want a single zip-able folder a reviewer can verify

## When NOT to choose Anu Architecture

- **Replicating** a published data series — use
  [Anu Replicator](https://github.com/andenick/anu-framework/tree/main/skills/anu-replicator)
  instead (sibling skill, 4-phase L/P/V/M, designed for replication
  packages).
- Quick prototyping — the discipline is overkill for a one-off notebook.
- You only need SQL transforms — use dbt.

## Borrowed from prior art

- **From cookiecutter-data-science**: data/raw + data/processed + outputs/ split
- **From Project TIER 4.0**: prescribed hierarchy + relative paths + master script
- **From dbt**: registry-driven pipeline, declarative model definitions
- **From AEA Data Editor**: Data Availability Statement (built into `O##`)
- **From the FAIR principles**: persistent identifiers, machine-readable metadata

## What Anu Architecture adds

- **First-class manual adjustment phase** with five-field audit requirement
- **First-class exploration preservation** — E## scripts never deleted
- **Anti-fabrication absolutism** — explicit prohibition of synthetic data,
  proxy substitution, lazy splices
- **Language-agnostic** — Python, R, Stata interchangeable
- **Evolutionary versioning** — snake-shedding for long-running projects
- **Assumptions register** — ASSUMPTIONS.md tracks every claim
