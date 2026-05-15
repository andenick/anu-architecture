"""Project status report — anu-architecture status."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from .discovery import PHASE_DIRS, discover_scripts


def report_status(project: Path) -> int:
    project = project.resolve()
    reg_path = project / "project_registry.json"
    if not reg_path.exists():
        typer.echo(f"  ERROR: no project_registry.json in {project}", err=True)
        return 1

    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    studies = registry.get("studies", {})
    datasets = registry.get("datasets", {})

    typer.echo(f"Anu Architecture project: {registry.get('project', '?')}")
    typer.echo(f"  Architecture: {registry.get('architecture', '?')}")
    typer.echo(f"  Language:     {registry.get('language', '?')}")
    typer.echo(f"  Studies:      {len(studies)}")
    for sid, s in studies.items():
        typer.echo(f"    - {sid}: {s.get('name', '')}  [{s.get('status', 'PENDING')}]")
    typer.echo(f"  Datasets:     {len(datasets)}")
    for did, d in datasets.items():
        typer.echo(f"    - {did}: {d.get('description', '')}")

    typer.echo("\nScripts per phase:")
    total = 0
    for ph in "SLPVMAOE":
        n = len(discover_scripts(project, ph))
        total += n
        typer.echo(f"    {ph}##  {PHASE_DIRS[ph]:13s}  {n} script(s)")
    typer.echo(f"  Total: {total}")

    # Data presence
    typer.echo("\nData state:")
    for sub in ("raw-data", "int-data", "final-data", "adjusted-final-data"):
        d = project / "data" / sub
        count = sum(1 for _ in d.rglob("*") if _.is_file()) if d.exists() else 0
        typer.echo(f"    data/{sub:21s} {count} file(s)")

    # Outputs presence
    typer.echo("\nOutputs state:")
    for sub in ("validation", "analysis", "deliverables"):
        d = project / "outputs" / sub
        count = sum(1 for _ in d.rglob("*") if _.is_file()) if d.exists() else 0
        typer.echo(f"    outputs/{sub:21s} {count} file(s)")

    return 0
