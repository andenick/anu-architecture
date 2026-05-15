"""Anu Architecture CLI entry point."""
from __future__ import annotations

from pathlib import Path

import typer

from . import __version__
from .init import init_project
from .status import report_status
from .run import run_pipeline
from .checklist import render_checklist
from .audit import run_audit
from .version_cmd import version_up, version_log, version_archive

app = typer.Typer(
    name="anu-architecture",
    help="Standardized 8-phase architecture for econometric data construction.",
    no_args_is_help=True,
)


@app.command()
def init(
    name: str = typer.Argument(None, help="Project name (defaults to dir name)"),
    language: str = typer.Option(None, "--language", "-l",
                                 help="Python | R | Stata | Mixed"),
    location: Path = typer.Option(None, "--location",
                                  help="Target directory (default: ./<name>)"),
    non_interactive: bool = typer.Option(False, "--yes", "-y",
                                          help="Skip prompts; use defaults"),
) -> None:
    """Scaffold a new Anu Architecture project."""
    init_project(name=name, language=language, location=location,
                 non_interactive=non_interactive)


@app.command()
def status(
    project: Path = typer.Option(Path("."), "--project", "-p"),
) -> None:
    """Report pipeline state of an Anu Architecture project."""
    report_status(project)


@app.command()
def run(
    project: Path = typer.Option(Path("."), "--project", "-p"),
    from_phase: str = typer.Option(None, "--from", help="Resume from phase letter"),
    validate_only: bool = typer.Option(False, "--validate-only"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    series: str = typer.Option(None, "--series", help="Run for specific subset"),
) -> None:
    """Run the master orchestrator."""
    run_pipeline(project=project, from_phase=from_phase,
                 validate_only=validate_only, dry_run=dry_run, series=series)


@app.command()
def checklist(
    project: Path = typer.Option(Path("."), "--project", "-p"),
) -> None:
    """Display CHECKLIST.md with completion status."""
    render_checklist(project)


@app.command()
def audit(
    project: Path = typer.Option(Path("."), "--project", "-p"),
    strict: bool = typer.Option(False, "--strict",
                                 help="Fail on WARN-severity hits too"),
) -> None:
    """Public-reproducibility scrub: hardcoded paths, synthetic data, missing sources."""
    rc = run_audit(project, strict=strict)
    raise typer.Exit(rc)


@app.command("version")
def version_cmd(
    action: str = typer.Argument(None, help="up | log | archive | (none for --version)"),
    project: Path = typer.Option(Path("."), "--project", "-p"),
    force: bool = typer.Option(False, "--force"),
) -> None:
    """Evolutionary versioning (snake-shedding)."""
    if action is None:
        typer.echo(f"anu-architecture {__version__}")
        return
    if action == "up":
        version_up(project, force=force)
    elif action == "log":
        version_log(project)
    elif action == "archive":
        version_archive(project)
    else:
        typer.echo(f"Unknown action: {action}. Use up | log | archive.", err=True)
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"anu-architecture {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: bool = typer.Option(False, "--version", callback=_version_callback,
                                  is_eager=True, help="Show version and exit"),
) -> None:
    pass


if __name__ == "__main__":
    app()
