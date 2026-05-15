"""Evolutionary versioning — anu-architecture version up|log|archive."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import typer


def version_up(project: Path, force: bool = False) -> int:
    project = project.resolve()
    archive_root = project / "_archive"
    history = project / "_version_history" / "VERSION_LOG.md"
    archive_root.mkdir(exist_ok=True)
    history.parent.mkdir(exist_ok=True)

    existing = sorted([d for d in archive_root.iterdir()
                      if d.is_dir() and d.name.startswith("v")])
    next_version = "v0.1" if not existing else _bump(existing[-1].name)
    date = datetime.now().strftime("%Y-%m-%d")
    target = archive_root / f"{next_version}_{date}"

    for sub in ("code", "data", "outputs", "logs", "project_registry.json"):
        src = project / sub
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, target / sub)
            else:
                target.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target / sub)

    if not history.exists():
        history.write_text("# VERSION_LOG\n\n", encoding="utf-8")
    with history.open("a", encoding="utf-8") as f:
        f.write(f"\n## {next_version} ({date})\n\n- TODO: describe what changed\n")

    typer.echo(f"[anu-architecture version] Archived to {target}")
    typer.echo(f"  Edit {history} to describe the changes.")
    return 0


def _bump(name: str) -> str:
    # name like "v0.3_2026-05-15" -> "v0.4"
    ver = name.split("_")[0]  # "v0.3"
    major, minor = ver[1:].split(".")
    return f"v{major}.{int(minor) + 1}"


def version_log(project: Path) -> int:
    history = project / "_version_history" / "VERSION_LOG.md"
    if not history.exists():
        typer.echo("No version history yet. Run `anu-architecture version up` first.")
        return 1
    typer.echo(history.read_text(encoding="utf-8"))
    return 0


def version_archive(project: Path) -> int:
    archive_root = project / "_archive"
    if not archive_root.exists():
        typer.echo("No archived versions yet.")
        return 1
    for d in sorted(archive_root.iterdir()):
        if d.is_dir():
            typer.echo(f"  {d.name}")
    return 0
