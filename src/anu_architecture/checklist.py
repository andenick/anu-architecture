"""Checklist display — anu-architecture checklist."""
from __future__ import annotations

from pathlib import Path

import typer


def render_checklist(project: Path) -> int:
    checklist = project / "CHECKLIST.md"
    if not checklist.exists():
        typer.echo(f"  ERROR: no CHECKLIST.md in {project}", err=True)
        return 1
    typer.echo(checklist.read_text(encoding="utf-8"))
    return 0
