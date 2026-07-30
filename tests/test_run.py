"""Test the master orchestrator: phase order and no double execution.

These are the regression tests for the two defects that made `run` execute
work it should not have:

* the canonical phase order must be S -> L -> P -> V -> M -> A -> V -> O,
  with O## last and running exactly once;
* the optional XX00 per-phase runner must never be picked up by the master
  orchestrator, or every script would run twice (directly, and again from
  inside its XX00).
"""
from pathlib import Path

from anu_architecture.discovery import discover_all, discover_scripts
from anu_architecture.run import run_pipeline

PHASES = ("setup", "loading", "processing", "validation",
          "manual", "analysis", "outputs", "exploration")
PREFIX = {"setup": "S", "loading": "L", "processing": "P", "validation": "V",
          "manual": "M", "analysis": "A", "outputs": "O", "exploration": "E"}


def _make_proj(tmp_path: Path, with_orchestrators: bool = True) -> Path:
    for ph in PHASES:
        (tmp_path / "code" / ph).mkdir(parents=True)
        if with_orchestrators:
            (tmp_path / "code" / ph / f"{PREFIX[ph]}00_run_all.py").write_text("")
        (tmp_path / "code" / ph / f"{PREFIX[ph]}01_first.py").write_text("")
    (tmp_path / "project_registry.json").write_text(
        '''{"version": "2.1.0", "project": "test",
            "architecture": "Anu Architecture v2.1",
            "studies": {}, "datasets": {}}''')
    return tmp_path


def test_default_order_runs_outputs_last(tmp_path):
    proj = _make_proj(tmp_path)
    phases = [ph for ph, _ in discover_all(proj)]
    assert phases[-1] == "O", phases
    o_positions = [i for i, ph in enumerate(phases) if ph == "O"]
    v_positions = [i for i, ph in enumerate(phases) if ph == "V"]
    assert v_positions, "validation should run"
    assert all(o > v for o in o_positions for v in v_positions), phases


def test_only_validation_repeats(tmp_path):
    """V## runs twice by design (data quality, then diagnostics). Nothing else does."""
    proj = _make_proj(tmp_path)
    phases = [ph for ph, _ in discover_all(proj)]
    repeated = {ph for ph in phases if phases.count(ph) > 1}
    assert repeated == {"V"}, phases


def test_no_script_is_discovered_twice(tmp_path):
    proj = _make_proj(tmp_path)
    names = [s.name for _, s in discover_all(proj)]
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert dupes == ["V01_first.py"], dupes  # only the deliberate second V pass


def test_orchestrator_files_are_never_discovered(tmp_path):
    proj = _make_proj(tmp_path)
    names = [s.name for _, s in discover_all(proj)]
    assert not [n for n in names if "00_run_all" in n], names
    # ...but they can be asked for explicitly.
    explicit = discover_scripts(proj, "L", include_orchestrator=True)
    assert "L00_run_all.py" in [p.name for p in explicit]


def test_from_phase_o_runs_outputs_once(tmp_path):
    proj = _make_proj(tmp_path)
    out = discover_all(proj, order="SLPVMAVO"[len("SLPVMAV"):])
    assert [ph for ph, _ in out] == ["O"], out


def test_dry_run_lists_without_executing(tmp_path):
    proj = _make_proj(tmp_path)
    # Every discovered script is empty, so executing them would be harmless —
    # but a dry run must not create the run-log directory at all.
    rc = run_pipeline(proj, dry_run=True)
    assert rc == 0
    assert not (proj / "logs" / "runs").exists()


def test_run_rejects_non_project(tmp_path):
    assert run_pipeline(tmp_path) == 1
