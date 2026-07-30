# R-dissertation example

A registry-only example: what `project_registry.json` looks like for a
multi-study R project such as a dissertation, as opposed to the
single-study registry in [`../python-minimal/`](../python-minimal/).

**What ships here is this README and `project_registry.json` — nothing
else.** There is no `code/` tree, no data and no runnable pipeline; every
study is `PENDING` and the `L##`/`P##`/`A##` identifiers name the scripts
you would write, not scripts that exist.

For a project you can actually run end to end, see
[`../python-minimal/`](../python-minimal/). To generate the full folder
layout for a project like this one:

```bash
anu-architecture init my-dissertation --language R
```

## What this registry demonstrates

- **Several studies in one project** — each with its own method, dependent
  variable, falsifiable prediction and `A##` script, tracked independently
  through `PENDING` → `IN_PROGRESS` → `COMPLETE`.
- **Several datasets feeding those studies** — each declaring the `L##`
  loaders and `P##` processors responsible for it, so the registry stays
  the single source of truth about which script produces what.
