# Changelog

## Unreleased

Correctness and accuracy pass.

**Fixed — orchestration**

- The canonical phase order was the literal `SLPVMAOVO`, which ran `O##`
  *before* the post-analysis diagnostics pass and then ran it a second
  time. It is now `SLPVMAVO`, matching the documented promise that `O##`
  runs last. `run --from O` consequently runs the output phase once
  instead of `O -> V -> O`.
- A scaffolded Python project ran every script twice: the generated
  `run.py` picked up `XX00_run_all.py` alongside `XX01-XX99`, and each
  `XX00` re-ran the same scripts as subprocesses. All four orchestrators
  (library, Python, R, Stata) now skip `XX00`. `XX01-XX99` is the unit of
  execution; `XX00` is an optional per-phase convenience runner.
- The Stata orchestrator's phase-to-directory mapping resolved to the
  literal `"..."` for five of seven phases, so only setup and loading
  could ever run. Rewritten. Note that CI has no Stata runner — run it by
  hand once before relying on it.
- A Stata project's generated README told the user to run `python run.py`.
  It now says `stata -b do run.do`.

**Fixed — scaffolds**

- The R and Stata scaffolds now ship `config/api_keys.env.example` and
  `utils/paths.R` / `utils/paths.do`. Their generated READMEs and
  `.gitignore` files already referenced those paths, which did not exist.

**Fixed — accuracy**

- `docs/GETTING_STARTED.md` opened with `pip install anu-architecture`.
  The package is not on PyPI; the walkthrough now installs from source.
- `docs/PUBLIC_REPRODUCIBILITY.md` claimed "CI runs it on every PR". It did
  not. The `test` workflow now runs `anu-architecture audit --strict`
  against the shipped example, and the gate's coverage is stated
  explicitly rather than implied.
- Framework version and skill-count claims were stale. Hard counts have
  been dropped from the public surface so they cannot re-stale.
- The two quantitative claims in `SPEC.md`'s core principles are now
  labelled as indicative from a single unpublished project rather than
  stated as measured fact.
- `examples/R-dissertation` shipped a copy of the python-minimal registry,
  declaring `COMPLETE` for scripts that do not exist. Its README and
  registry now describe what actually ships.

**Changed**

- `anu-architecture audit` now also scans `utils/**` and the root
  orchestrator, not just `code/**`. Projects that hid a machine-local path
  in `utils/paths.*` will start failing the gate — that is the point.
- Dropped the `pyyaml` runtime dependency; nothing in the package imported
  it.
- Removed the duplicated copy of `project_registry.schema.json` at the repo
  root. The packaged copy under `src/anu_architecture/schemas/` is the one
  the tool loads and is now the only one.
- Removed the internal "Skill Evolution Log" from `docs/SPEC.md`; the
  Lineage section below and `docs/DESIGN_DECISIONS.md` carry what a reader
  of this repo needs.

**Tests**

- Added coverage for `run`, `status`, `checklist` and `version`, which had
  none — including regression tests for both orchestration bugs above, a
  negative control for the `proxy_justification` warning, and a check that
  every shipped example registry validates against the schema.

## v2.1.0 — 2026-05-15

Initial standalone release. Extracted from the Anu Framework v12.0
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
