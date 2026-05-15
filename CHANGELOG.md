# Changelog

## v2.1.0 — 2026-05-15

Initial standalone release. Extracted from the Anu Framework v11.0
`anu-architecture` skill.

- 8-phase architecture (S/L/P/V/M/A/O/E) for econometric data construction
- Python CLI: `init`, `status`, `run`, `checklist`, `audit`, `version`
- Templates for Python, R, and Stata projects
- `project_registry.json` JSON Schema
- Tests on Python 3.10, 3.11, 3.12
- Install: source only (`git clone` + `pip install -e .`); PyPI publication
  deferred

## Lineage

- NickyData v1.0 (2026-04-05) — original spec for econometric data projects
- NickyData v1.1 (2026-04-06) — added evolutionary versioning + assumptions register
- AnuData Architecture v2.0 (2026-05-09) — renamed and integrated into Anu Framework
- Anu Architecture v2.1 (2026-05-15) — renamed for framework-name consistency; canonical BEA/BLS/FRED cache schemas documented
