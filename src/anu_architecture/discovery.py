"""Script discovery — glob L01/P02/etc by phase."""
from __future__ import annotations

import re
from pathlib import Path

PHASE_DIRS = {
    "S": "setup", "L": "loading", "P": "processing", "V": "validation",
    "M": "manual", "A": "analysis", "O": "outputs", "E": "exploration",
}

SCRIPT_RE = re.compile(r"^[SLPVMAOE]\d{2}_[A-Za-z0-9_]+\.(py|R|do)$")


def discover_scripts(project: Path, phase: str,
                     include_orchestrator: bool = False) -> list[Path]:
    """Return scripts for one phase, sorted by number.

    By default skips the `XX00_run_all` orchestrator file. The master `run.py`
    invokes XX00 once per phase; XX00 internally iterates XX01-XX99. Pass
    `include_orchestrator=True` to include XX00 (useful for the master
    orchestrator itself).
    """
    phase_dir = project / "code" / PHASE_DIRS.get(phase, phase)
    if not phase_dir.exists():
        return []
    scripts = [p for p in phase_dir.iterdir()
               if p.is_file() and SCRIPT_RE.match(p.name) and p.name[0] == phase]
    if not include_orchestrator:
        scripts = [p for p in scripts if not p.name.startswith(f"{phase}00_")]
    scripts.sort(key=lambda p: int(p.name[1:3]))
    return scripts


def discover_all(project: Path, order: str = "SLPVMAOVO") -> list[tuple[str, Path]]:
    """Discover all scripts in canonical execution order.

    Default order: S -> L -> P -> V -> M -> A -> V (diagnostics) -> O.
    E## runs concurrently in normal use; not included here.
    """
    out = []
    for ph in order:
        for s in discover_scripts(project, ph):
            out.append((ph, s))
    return out
