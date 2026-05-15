# Anu Architecture

Standardized 8-phase architecture for econometric data construction and
analysis. Scaffolds a self-contained, language-agnostic project where every
script, dataset, output, and decision is tracked in one folder.

> Anu Architecture is one of 20 skills in the
> [Anu Framework](https://github.com/andenick/anu-framework). This repo
> extracts it as an independent tool.

## Install

```bash
pip install anu-architecture
```

Or from source:

```bash
git clone https://github.com/andenick/anu-architecture
cd anu-architecture
pip install -e .
```

## Quick start

```bash
anu-architecture init my-project
cd my-project
python run.py --dry-run
```

See [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) for the 5-minute
walkthrough.

## The 8 phases

| Prefix | Name | Purpose |
|---|---|---|
| **S##** | Setup | Packages, env, API keys, path validation |
| **L##** | Load | Raw data from files + APIs into `data/raw-data/` |
| **P##** | Process | Clean, transform, construct analysis-ready datasets |
| **V##** | Validate | Data integrity AND model diagnostics |
| **M##** | Manual | Documented manual adjustments with audit trail |
| **A##** | Analyze | Estimation, robustness, comparison |
| **O##** | Output | Tables, figures, reports (runs LAST) |
| **E##** | Explore | Standalone exploratory work (ephemeral) |

Full spec: [`docs/SPEC.md`](docs/SPEC.md). The 8 phases in depth:
[`docs/THE_8_PHASES.md`](docs/THE_8_PHASES.md).

## Core principles

1. **Containment** — everything in one folder, zip and hand it to a reviewer.
2. **No synthetic data** — every value traces to a real, documented source.
3. **No proxies without justification** — concept substitutions degrade
   faithfulness; document them in `project_registry.json` with `"proxy": true`.
4. **Reproducibility without agents** — a researcher runs `python run.py`
   and gets every output.
5. **Audit trail** — every transformation logged in structured JSON.

## Commands

```bash
anu-architecture init [project_name]         # Interactive scaffold
anu-architecture status                      # Pipeline state report
anu-architecture run [--dry-run] [--from P]  # Master orchestrator
anu-architecture checklist                   # Render CHECKLIST.md
anu-architecture audit                       # Public-reproducibility scrub
anu-architecture version up|log|archive      # Evolutionary versioning
```

## See also

- [Anu Framework](https://github.com/andenick/anu-framework) — the full
  20-skill data-construction framework. Use that if you need replication,
  extension, three-channel distribution, etc.
- [Anu Replicator](https://github.com/andenick/anu-framework/tree/main/skills/anu-replicator)
  — the sibling skill for replicating *published* data series (vs Anu
  Architecture which is for original research).

## License

MIT.
