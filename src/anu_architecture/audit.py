r"""Public-reproducibility audit — anu-architecture audit.

Scans the project tree for:
    FAIL  - Hardcoded local paths (D:\, /Users/, C:\)
    FAIL  - np.random in S/L/P/V/M scripts (data construction; never in analysis E paths)
    WARN  - L## scripts without 'Public Source:' header
    WARN  - 'proxy: true' without proxy_justification
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import typer

HARDCODED_PATH_RE = re.compile(
    r"(?:[A-Z]:[\\/]|/Users/|/home/[a-z]+/)\S"
)
LOAD_SCRIPT_RE = re.compile(r"L\d{2}_.*\.(py|R|do)$")
PUBLIC_SOURCE_RE = re.compile(r"Public\s+Source\s*:", re.IGNORECASE)
RANDOM_RE = re.compile(r"\bnp\.random\b|\brandom\.(rand|randint|normal|choice)\b")

DATA_CONSTRUCTION_PHASES = {"setup", "loading", "processing", "validation", "manual"}


def run_audit(project: Path, strict: bool = False) -> int:
    project = project.resolve()
    findings: list[tuple[str, str, str]] = []  # (severity, path, message)

    # Walk code/
    for code_file in (project / "code").rglob("*"):
        if not code_file.is_file():
            continue
        if code_file.suffix not in (".py", ".R", ".do"):
            continue
        rel = code_file.relative_to(project).as_posix()
        text = code_file.read_text(encoding="utf-8", errors="ignore")

        # FAIL: hardcoded paths
        for m in HARDCODED_PATH_RE.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings.append(("FAIL", rel,
                            f"L{line_no}: hardcoded local path: {m.group(0)[:60]}"))
            break  # one per file

        # FAIL: random in data construction
        phase_dir = code_file.parent.name
        if phase_dir in DATA_CONSTRUCTION_PHASES:
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
