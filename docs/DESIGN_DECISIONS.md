# Design Decisions

## Why 8 phases, not 5 or 12?

Five (cookiecutter-data-science: raw/processed/models/reports/notebooks)
conflates several concerns. Three additions in Anu Architecture:

- **Validation as a first-class phase (V##)** — without this, validation
  hides inside processing and only the author knows what was checked.
- **Manual adjustment as a first-class phase (M##)** — every empirical
  project has them; making them explicit forces documentation.
- **Exploration preservation (E##)** — the conclusions of exploratory work
  are valuable; deleting the scripts that produced them loses the audit
  trail.

Twelve would over-fit. Eight is the smallest set where each phase is
semantically distinct.

## Why prefix-based file naming (`L01_`, `P02_`)?

Glob-based discovery. The orchestrator does
`glob("code/loading/L[0-9][0-9]_*.py")` and runs scripts in numeric order.
No need for a manifest file that drifts out of sync with the file system.

Trade-off: renumbering is painful. The renumbering protocol (in
`docs/SPEC.md`) documents the steps.

## Why no letter suffixes (no `P01b.py`)?

Letter suffixes are invisible to the orchestrator glob and break pipeline
discovery. If you need to insert between P03 and P04, renumber the phase.
Painful once; reliable forever.

## Why is O## guaranteed to run last?

Outputs are the user-facing artifacts. Running O## last guarantees that
everything they depend on (analysis, validation, diagnostics) has already
run. The orchestrator enforces this.

## Why language-agnostic?

Real econometric projects mix tools — R for plm/cointegration, Python for
pandas/scikit-learn, Stata for legacy methods. Forcing one language forces
a translation cost that's avoidable.

## Why a single `project_registry.json` instead of YAML or TOML?

JSON is the only format with a universal schema language (JSON Schema). The
schema is checked-in; `anu-architecture init` validates it on every change.

## Why no built-in CI integration?

Two reasons:

1. CI is a project decision (GitHub Actions vs GitLab CI vs Jenkins).
2. The pipeline itself runs locally with `python run.py`. CI is just
   "run that on a fresh container" — and we can't predict the dependencies.

This repository's own [`.github/workflows/`](../.github/workflows/) is a
usable starting template: a lint job and a test matrix, plus one step that
runs `anu-architecture audit --strict` against the shipped example.

## Why does the master orchestrator skip `XX00_run_all`?

Because there are two plausible units of execution and only one can be
correct. Either the orchestrator runs the eight `XX00` per-phase runners
and each of those runs its own `XX01-XX99`, or the orchestrator runs
`XX01-XX99` directly. Doing both runs every script twice — loaders
re-download, `M##` adjustments re-apply.

`XX01-XX99` is the unit of execution. `XX00` is a convenience runner for
executing one phase by hand, and every orchestrator filters it out.

## Why does `V##` appear twice in the phase order but nothing else does?

The canonical order is `S -> L -> P -> V -> M -> A -> V -> O`. Validation
is genuinely two different jobs: data quality before analysis, and model
diagnostics after estimation. Every other phase — `O##` above all — runs
exactly once, and `O##` runs last so that everything it renders already
exists.

## Why "snake-shedding" evolutionary versioning?

Long-running projects (multi-year studies with many revisions) accumulate
decisions, data updates, methodological shifts. Snake-shedding archives
each version intact rather than rewriting history. The `_archive/` is the
permanent record.

This and the assumptions register were both added after the first
real-world use of the architecture, which surfaced the same gap twice: a
long project cannot defend a result if the state that produced it has been
overwritten, and it cannot defend a method if the assumptions behind it
were never written down.

## Why an `ASSUMPTIONS.md` register?

In research code, the assumptions are the part most likely to be
challenged and least likely to be recorded. Giving them a file, an ID
scheme (`ASM-D01`, `ASM-M01`, `ASM-T01`) and a source citation makes them
reviewable — and makes "revisit every assumption" a concrete step when
versioning up rather than an intention.
