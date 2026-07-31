r"""Public-reproducibility audit — anu-architecture audit.

Checks:
    FAIL  - Hardcoded local paths (D:\, /Users/, C:\)
    FAIL  - np.random in S/L/P/V/M scripts (data construction; never in analysis/E paths)
    WARN  - L01-L99 scripts without 'Public Source:' header (L00_run_all is a
            per-phase convenience runner, not a loader, and is exempt)
    WARN  - 'proxy: true' without proxy_justification

COVERAGE — this gate is not a whole-repo scan. It reads:
    - code/**            (.py, .R, .do)
    - utils/**           (.py, .R, .do)  — the designated home of every path
                         constant, and therefore the likeliest place for a
                         hardcoded local path to hide
    - the root master orchestrator (run.py / run.R / run.do)
    - project_registry.json (proxy justifications only)

It does NOT read data/, outputs/, logs/, docs/, notebooks, or anything
outside the project folder. The np.random check is narrower still: it
applies only to code/{setup,loading,processing,validation,manual}, because
randomness in analysis/ and exploration/ is legitimate.

Keep this docstring and docs/PUBLIC_REPRODUCIBILITY.md in agreement — a
gate that does not state its coverage cannot be relied on.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import typer

HARDCODED_PATH_RE = re.compile(
    r"(?:[A-Z]:[\\/]|/Users/|/home/[a-z]+/)\S"
)
# L01-L99 only. L00_run_all is the optional per-phase convenience runner: it
# loads nothing, so demanding a Public Source: header from it made a freshly
# scaffolded Python project fail `audit --strict` on its own generated file.
LOAD_SCRIPT_RE = re.compile(r"L(?!00_)\d{2}_.*\.(py|R|do)$")
PUBLIC_SOURCE_RE = re.compile(r"Public\s+Source\s*:", re.IGNORECASE)
RANDOM_RE = re.compile(r"\bnp\.random\b|\brandom\.(rand|randint|normal|choice)\b")

DATA_CONSTRUCTION_PHASES = {"setup", "loading", "processing", "validation", "manual"}

SCANNED_SUFFIXES = (".py", ".R", ".do")
SCANNED_DIRS = ("code", "utils")
ROOT_ORCHESTRATORS = ("run.py", "run.R", "run.do")


def _scanned_files(project: Path) -> list[Path]:
    """Every source file this gate reads. See the module docstring for coverage."""
    files: list[Path] = []
    for sub in SCANNED_DIRS:
        root = project / sub
        if not root.is_dir():
            continue
        for f in root.rglob("*"):
            if f.is_file() and f.suffix in SCANNED_SUFFIXES:
                files.append(f)
    for name in ROOT_ORCHESTRATORS:
        f = project / name
        if f.is_file():
            files.append(f)
    return sorted(files)


def run_audit(project: Path, strict: bool = False) -> int:
    project = project.resolve()
    findings: list[tuple[str, str, str]] = []  # (severity, path, message)

    for code_file in _scanned_files(project):
        rel = code_file.relative_to(project).as_posix()
        text = code_file.read_text(encoding="utf-8", errors="ignore")

        # FAIL: hardcoded paths
        for m in HARDCODED_PATH_RE.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings.append(("FAIL", rel,
                            f"L{line_no}: hardcoded local path: {m.group(0)[:60]}"))
            break  # one per file

        # FAIL: random in data construction — code/<phase>/ only, never
        # analysis/, exploration/, utils/ or the root orchestrator.
        parent = code_file.parent
        if parent.parent.name == "code" and parent.name in DATA_CONSTRUCTION_PHASES:
            for m in RANDOM_RE.finditer(text):
                line_no = text[:m.start()].count("\n") + 1
                msg = f"L{line_no}: random call in data-construction phase: {m.group(0)}"
                findings.append(("FAIL", rel, msg))
                break

        # WARN: L## without Public Source
        if LOAD_SCRIPT_RE.match(code_file.name) and not PUBLIC_SOURCE_RE.search(text):
            findings.append(("WARN", rel, "L## script missing 'Public Source:' header"))

    # WARN: proxy without justification
    reg_path = project / "project_registry.json"
    if reg_path.exists():
        try:
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            for did, d in reg.get("datasets", {}).items():
                for cid, c in (d.get("columns") or {}).items():
                    if isinstance(c, dict) and c.get("proxy") and not c.get("proxy_justification"):
                        msg = (f"datasets.{did}.columns.{cid}: proxy=true "
                               f"without proxy_justification")
                        findings.append(("WARN", "project_registry.json", msg))
        except Exception as e:
            findings.append(("WARN", "project_registry.json", f"could not parse: {e}"))

    # Report
    n_fail = sum(1 for f in findings if f[0] == "FAIL")
    n_warn = sum(1 for f in findings if f[0] == "WARN")
    if not findings:
        typer.echo("[anu-architecture audit] CLEAN — zero findings.")
        return 0
    typer.echo(f"[anu-architecture audit] {n_fail} FAIL + {n_warn} WARN findings:")
    for sev, rel, msg in findings:
        typer.echo(f"    [{sev}] {rel}: {msg}")

    if n_fail:
        return 1
    if strict and n_warn:
        return 1
    return 0
