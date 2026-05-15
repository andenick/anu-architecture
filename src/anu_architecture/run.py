"""Master orchestrator — anu-architecture run."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer

from .discovery import discover_all, discover_scripts


def run_pipeline(
    project: Path,
    from_phase: str | None = None,
    validate_only: bool = False,
    dry_run: bool = False,
    series: str | None = None,
) -> int:
    project = project.resolve()
    if not (project / "project_registry.json").exists():
        typer.echo(f"  ERROR: {project} is not an Anu Architecture project "
                   "(no project_registry.json)", err=True)
        return 1

    order = "SLPVMAOVO"  # S -> L -> P -> V -> M -> A -> V(diag) -> O
    if validate_only:
        order = "V"
    elif from_phase:
        idx = order.find(from_phase.upper())
        if idx == -1:
            typer.echo(f"  ERROR: unknown phase {from_phase}", err=True)
            return 1
        order = order[idx:]

    scripts = discover_all(project, order=order)

    typer.echo(f"[anu-architecture run] {len(scripts)} script(s) discovered:")
    for ph, s in scripts:
        typer.echo(f"    {ph}  {s.relative_to(project)}")
    if dry_run:
        return 0

    log_dir = project / "logs" / "runs"
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')}"
    log = []

    for ph, s in scripts:
        t0 = datetime.now(timezone.utc).isoformat()
        cmd = _command_for(s)
        typer.echo(f"\n[{ph}] {s.name}")
        proc = subprocess.run(cmd, cwd=project)
        t1 = datetime.now(timezone.utc).isoformat()
        log.append({
            "phase": ph, "script": s.name, "started": t0, "completed": t1,
            "exit_code": proc.returncode,
        })
        if proc.returncode != 0:
            typer.echo(f"  FAILED at {s.name} (exit {proc.returncode})", err=True)
            break

    (log_dir / f"{run_id}.json").write_text(
        json.dumps(log, indent=2), encoding="utf-8")
    return 0 if all(e["exit_code"] == 0 for e in log) else 1


def _command_for(script: Path) -> list[str]:
    if script.suffix == ".py":
        return [sys.executable, str(script)]
    if script.suffix == ".R":
        return ["Rscript", str(script)]
    if script.suffix == ".do":
        return ["stata-mp", "-b", "do", str(script)]
    return [str(script)]
