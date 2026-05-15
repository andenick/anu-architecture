# `project_registry.json`

The single source of truth for study configuration. Read by every script in
the pipeline.

## Schema (excerpt)

```json
{
  "version": "2.1.0",
  "project": "My Banking Study",
  "architecture": "Anu Architecture v2.1",
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

Full schema: [`schemas/project_registry.schema.json`](../schemas/project_registry.schema.json).

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
`anu-architecture version up` archives it before bumping the project
version.
