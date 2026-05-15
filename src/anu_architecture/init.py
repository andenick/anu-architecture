"""Project scaffolding — anu-architecture init."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_ROOT = Path(__file__).parent / "templates"


PHASES = ["setup", "loading", "processing", "validation",
          "manual", "analysis", "outputs", "exploration"]
PHASE_PREFIXES = {"setup": "S", "loading": "L", "processing": "P",
                  "validation": "V", "manual": "M", "analysis": "A",
                  "outputs": "O", "exploration": "E"}


def _prompt(label: str, default: str | None = None) -> str:
    if default:
        v = typer.prompt(label, default=default)
    else:
        v = typer.prompt(label)
    return v.strip()


def init_project(
    name: str | None = None,
    language: str | None = None,
    location: Path | None = None,
    non_interactive: bool = False,
) -> Path:
    """Interactive (or non-interactive) project scaffold."""
    if non_interactive:
        name = name or "anu-project"
        language = language or "Python"
        location = location or Path.cwd() / name
        studies = ["STUDY_01"]
        sources = ["fred"]
    else:
        name = name or _prompt("Project name", default="anu-project")
        if not language:
            language = _prompt("Language [Python/R/Stata/Mixed]", default="Python")
        location = location or (Path.cwd() / name)
        n_studies = int(_prompt("How many studies?", default="1"))
        studies = []
        for i in range(n_studies):
            s = _prompt(f"  Study {i+1} name", default=f"STUDY_{i+1:02d}")
            studies.append(s)
        sources_raw = _prompt("Data sources (comma-separated, e.g., fred,bea,bls)",
                              default="fred")
        sources = [s.strip() for s in sources_raw.split(",") if s.strip()]

    location = Path(location).resolve()
    if location.exists() and any(location.iterdir()):
        typer.echo(f"  ERROR: {location} exists and is non-empty.", err=True)
        raise typer.Exit(1)
    location.mkdir(parents=True, exist_ok=True)

    lang_dir = {"Python": "python", "R": "R", "Stata": "stata",
                "Mixed": "python"}.get(language, "python")
    template_dir = TEMPLATE_ROOT / lang_dir
    if not template_dir.exists():
        typer.echo(f"  ERROR: no templates for language {language}", err=True)
        raise typer.Exit(1)

    # Folder skeleton
    for phase in PHASES:
        (location / "code" / phase).mkdir(parents=True, exist_ok=True)
    for sub in ("user-inputs", "raw-data", "int-data", "final-data",
                "adjusted-final-data", "scratch"):
        (location / "data" / sub).mkdir(parents=True, exist_ok=True)
    for sub in ("validation", "analysis", "exploration", "deliverables"):
        (location / "outputs" / sub).mkdir(parents=True, exist_ok=True)
    (location / "outputs" / "deliverables" / "tables").mkdir(exist_ok=True)
    (location / "outputs" / "deliverables" / "figures").mkdir(exist_ok=True)
    (location / "outputs" / "deliverables" / "reports").mkdir(exist_ok=True)
    for d in ("utils", "logs", "logs/setup", "logs/validation", "logs/runs", "docs"):
        (location / d).mkdir(parents=True, exist_ok=True)

    # Render templates
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(),
        keep_trailing_newline=True,
    )
    ctx = {
        "project_name": name,
        "language": language,
        "studies": studies,
        "sources": sources,
    }
    for tpl_path in template_dir.rglob("*.template"):
        rel = tpl_path.relative_to(template_dir)
        # Strip .template suffix from output filename
        out_rel = rel.with_suffix("") if rel.suffix == ".template" else rel
        out_path = location / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tpl_name = str(rel).replace("\\", "/")
        tpl = env.get_template(tpl_name)
        out_path.write_text(tpl.render(**ctx), encoding="utf-8")

    # Stub L## scripts per source
    ext = {"python": ".py", "R": ".R", "stata": ".do"}.get(lang_dir, ".py")
    for i, source in enumerate(sources, start=1):
        stub_name = f"L{i:02d}_load_{source}{ext}"
        stub_path = location / "code" / "loading" / stub_name
        stub_path.write_text(
            f'"""L{i:02d}: Load {source}\n'
            f'====================\n'
            f'Phase:   Loading\n'
            f'Purpose: TODO\n'
            f'Public Source: TODO\n'
            f'Units:   TODO\n'
            f'"""\n\n# TODO: implement loader\n',
            encoding="utf-8",
        )

    # A## stubs per study
    for i, study in enumerate(studies, start=1):
        stub_name = f"A{i:02d}_{study.lower()}{ext}"
        stub_path = location / "code" / "analysis" / stub_name
        stub_path.write_text(
            f'"""A{i:02d}: {study}\n'
            f'====================\n'
            f'Phase:   Analysis\n'
            f'Purpose: TODO\n'
            f'Studies: {study}\n'
            f'"""\n\n# TODO: implement analysis\n',
            encoding="utf-8",
        )

    typer.echo(f"\n[anu-architecture] Scaffolded {name} at {location}")
    typer.echo(f"  Studies: {', '.join(studies)}")
    typer.echo(f"  Sources: {', '.join(sources)}")
    typer.echo(f"\nNext: cd {location.name} && python run.py --dry-run")
    return location
