"""Master orchestrator for python-minimal example.

Discovers and runs scripts by phase prefix in canonical order:
    S -> L -> P -> V -> M -> A -> V (diagnostics) -> O

Usage:
    python run.py                  Full pipeline
    python run.py --dry-run        List what would run
    python run.py --setup-only     Just S##
    python run.py --from P         Resume from processing
    python run.py --validate-only  Just V##
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
PHASE_DIRS = {"S": "setup", "L": "loading", "P": "processing", "V": "validation",
              "M": "manual", "A": "analysis", "O": "outputs", "E": "exploration"}


def discover(phase: str) -> list[Path]:
    d = PROJECT / "code" / PHASE_DIRS[phase]
    if not d.exists():
        return []
    scripts = [p for p in d.iterdir() if p.is_file()
               and p.name.startswith(phase) and p.suffix == ".py"
               and p.name[1:3].isdigit()]
    return sorted(scripts, key=lambda p: int(p.name[1:3]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--from", dest="from_phase", default=None)
    args = ap.parse_args()

    order = "SLPVMAOVO"
    if args.setup_only:
        order = "S"
    elif args.validate_only:
        order = "V"
    elif args.from_phase:
        idx = order.find(args.from_phase.upper())
        if idx == -1:
            print(f"Unknown phase: {args.from_phase}")
            sys.exit(1)
        order = order[idx:]

    scripts = []
    for ph in order:
        for s in discover(ph):
            scripts.append((ph, s))

    print(f"[run] {len(scripts)} script(s):")
    for ph, s in scripts:
        print(f"  {ph}  {s.relative_to(PROJECT)}")
    if args.dry_run:
        return

    for ph, s in scripts:
        print(f"\n[{ph}] {s.name}")
        r = subprocess.run([sys.executable, str(s)], cwd=PROJECT)
        if r.returncode != 0:
            print(f"FAILED at {s.name}", file=sys.stderr)
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
