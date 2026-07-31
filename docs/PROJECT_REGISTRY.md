# `project_registry.json`

The single source of truth for study configuration. Read by every script in
the pipeline.

## Schema (excerpt)

`version` is the *project's* own version — `init` seeds it at `0.1.0` and you
bump it. `architecture` records which version of the tool scaffolded the
project and is stamped by `init`; it is not something you maintain by hand.

```json
{
  "version": "0.1.0",
  "project": "My Banking Study",
  "architecture": "Anu Architecture v2.2",
  "language": "Python",
  "author": "Alice Researcher",

  "studies": {
    "STUDY_01": {
      "name": "Mean reversion of bank profitability",
      "method": "GMM",
      "dependent_variable": "roa",
      "key_prediction": "rho > 0.7 in equilibrium",
      "analysis_scripts": ["A01", "A02"],
      "status": "PENDING"
    }
  },

  "datasets": {
    "main_panel": {
      "description": "Bank-quarter panel 1990-2024",
      "loading_scripts": ["L01", "L02", "L03"],
      "processing_scripts": ["P01", "P02"],
      "format": "parquet"
    }
  }
}
```

Full schema: [`src/anu_architecture/schemas/project_registry.schema.json`](../src/anu_architecture/schemas/project_registry.schema.json)
— the copy that ships in the package and that `anu-architecture` actually
validates against.

## Proxy declarations

If a series substitutes a proxy for the canonical source, declare it:

```json
"datasets": {
  "main_panel": {
    "columns": {
      "earnings_yield": {
        "proxy": true,
        "proxy_justification": "Sectoral earnings unavailable for 1860-1929; using firm-level Cowles index as proxy. Validated by R^2 = 0.91 over 1930-1960 overlap."
      }
    }
  }
}
```

Every proxy must have a justification. The audit refuses to pass undocumented proxies.

## Status values

`PENDING`, `IN_PROGRESS`, `COMPLETE`, `BLOCKED:<dependency>`,
`DATA_UNAVAILABLE`.

## Updating

`anu-architecture status` reads it; `anu-architecture init` creates it;
`anu-architecture version up` copies it into the version snapshot under
`_archive/`. Nothing rewrites the `version` field for you — bump it yourself
when you decide the project has moved on.
