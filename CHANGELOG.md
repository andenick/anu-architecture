# Changelog

## 2.2.1 — 2026-07-31

Second correctness pass. The R and Stata scaffolds were run end to end for the
first time, against real runtimes (R 4.4.1 and Stata 18 BE on Windows); both
were broken.

**Fixed — scaffolds that could not run**

- `init` wrote every `L##`/`A##` stub as Python regardless of project
  language, so an R or Stata project's first script was a syntax error
  (`"""` is a docstring only in Python). `Rscript run.R` died on
  `L01_load_fred.R` with *unexpected string constant*; `stata -b do run.do`
  died on `L01_load_fred.do`. Stubs now use `#` for R and `*` for Stata.
- The Stata orchestrator's `XX00` skip never fired. Stata's `dir` extended
  macro function reports filenames in whatever case the OS gives it — Windows
  lower-cases them — so `"l00_run_all.do" != "L00_run_all.do"` was always
  true and `L00_run_all.do` ran anyway, which is the double-execution bug
  2.2.0 set out to fix. The comparison is now case-insensitive.
- `run.R` ignored its arguments, so `Rscript run.R --dry-run` — which the
  generated README tells you to run first — executed the entire pipeline
  instead of listing it. It now honours `--dry-run`.
- `anu-architecture run` invoked `stata-mp` by name, so it could not drive an
  SE, BE or IC installation. It now takes the first Stata console binary on
  `PATH`.

**Fixed — the audit gate failed on its own scaffold**

- A freshly scaffolded Python project failed `anu-architecture audit --strict`
  on `code/loading/L00_run_all.py`, because the `Public Source:` rule matched
  every `L##` including the per-phase convenience runner, which loads nothing.
  `L00` is now exempt; `L01`-`L99` are unchanged.

**Fixed — accuracy**

- `docs/SPEC.md` documented five master-orchestrator flags that do not exist
  (`--load-only`, `--test A01`, `--report`, and `--setup-only`/`--dry-run` for
  languages that did not implement them). It now lists, per language, only the
  flags each generated orchestrator actually accepts.
- `anu-architecture run --series` was accepted and then ignored — the argument
  was never read. Removed rather than documented.
- The scaffolded `project_registry.json` hardcoded
  `"architecture": "Anu Architecture v2.1"`, so every project scaffolded after
  2.1 claimed the wrong architecture version. It is now stamped from the
  installed package and cannot re-stale. `"version"` is the *project's* own
  version and now seeds at `0.1.0`; `docs/PROJECT_REGISTRY.md` says which is
  which.
- `docs/SPEC.md` was titled `v2.1` and footed "Anu Architecture v2.1 — Part of
  the Anu Framework v12.2" while the package shipped 2.2.0. The spec no longer
  pins a release; `anu-architecture --version` and `CHANGELOG.md` are the
  answer. (The dated `v2.1.0 — 2026-05-15` entry below still says "Anu
  Framework v12.0" and is left alone: it records what that release was
  extracted from on that date, not what the framework version is today.)
- `docs/SPEC.md`'s "Versioning" section read "No CHANGELOG file" next to a tag
  example this repo does not use. It is a rule for the research project you
  scaffold, not for this tool, and now says so.
- `anu-architecture init --help` claimed the project name defaults to the
  directory name; it defaults to `anu-project`.
- `docs/GETTING_STARTED.md` named the generated loader stub
  `L01_<source>.py`; it is `L01_load_<source>.py`.

**Tests**

- Added regression coverage for every fix above: non-Python stubs contain no
  Python syntax, the Stata `XX00` comparison is case-insensitive, `run.R`
  parses `--dry-run`, the architecture stamp tracks the package version, the
  Stata executable is discovered rather than assumed, and `L00_run_all` is
  exempt from the `Public Source:` rule while `L01` is not.

## 2.2.0 — 2026-07-30

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
