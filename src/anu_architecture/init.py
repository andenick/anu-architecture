"""Project scaffolding — anu-architecture init."""
from __future__ import annotations

from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import __version__

TEMPLATE_ROOT = Path(__file__).parent / "templates"


PHASES = ["setup", "loading", "processing", "validation",
          "manual", "analysis", "outputs", "exploration"]
PHASE_PREFIXES = {"setup": "S", "loading": "L", "processing": "P",
                  "validation": "V", "manual": "M", "analysis": "A",
                  "outputs": "O", "exploration": "E"}


def _stub(ext: str, header: list[str], body: str) -> str:
    """Render a script stub with comment syntax the target language accepts.

    A Python triple-quoted docstring is a syntax error in R and in Stata, so
    the header block cannot be shared verbatim across languages: `.R` uses
    `#`, `.do` uses `*`, and only `.py` gets a docstring.
    """
    if ext == ".py":
        head = '"""' + "\n".join(header) + '\n"""'
        return f"{head}\n\n# {body}\n"
    marker = "*" if ext == ".do" else "#"
    head = "\n".join(f"{marker} {line}".rstrip() for line in header)
    return f"{head}\n\n{marker} {body}\n"


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
        # Stamped from the installed package so a scaffold can never claim a
        # version of the architecture other than the one that produced it.
        "arch_version": __version__,
        "arch_version_short": ".".join(__version__.split(".")[:2]),
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
            _stub(ext, [
                f"L{i:02d}: Load {source}",
                "====================",
                "Phase:   Loading",
                "Purpose: TODO",
                "Public Source: TODO",
                "Units:   TODO",
            ], "TODO: implement loader"),
            encoding="utf-8",
        )

    # A## stubs per study
    for i, study in enumerate(studies, start=1):
        stub_name = f"A{i:02d}_{study.lower()}{ext}"
        stub_path = location / "code" / "analysis" / stub_name
        stub_path.write_text(
            _stub(ext, [
                f"A{i:02d}: {study}",
                "====================",
                "Phase:   Analysis",
                "Purpose: TODO",
                f"Studies: {study}",
            ], "TODO: implement analysis"),
            encoding="utf-8",
        )

    next_cmd = {"python": "python run.py --dry-run",
                "R": "Rscript run.R",
                "stata": "stata -b do run.do"}[lang_dir]
    typer.echo(f"\n[anu-architecture] Scaffolded {name} at {location}")
    typer.echo(f"  Studies: {', '.join(studies)}")
    typer.echo(f"  Sources: {', '.join(sources)}")
    typer.echo(f"\nNext: cd {location.name} && {next_cmd}")
    return location
