"""Test the read-only CLI commands: status, checklist, version.

`init`, `audit` and `run` have their own test modules; these three had no
coverage at all.
"""
import json

from typer.testing import CliRunner

from anu_architecture import __version__
from anu_architecture.cli import app

runner = CliRunner()

REGISTRY = {
    "version": "2.1.0",
    "project": "Status Test Project",
    "architecture": "Anu Architecture v2.1",
    "language": "Python",
    "studies": {"STUDY_01": {"name": "A study", "status": "IN_PROGRESS"}},
    "datasets": {"panel": {"description": "A panel"}},
}


def _make_proj(tmp_path):
    for ph in ("setup", "loading", "processing", "validation",
               "manual", "analysis", "outputs", "exploration"):
        (tmp_path / "code" / ph).mkdir(parents=True)
    (tmp_path / "code" / "loading" / "L01_load.py").write_text("")
    (tmp_path / "project_registry.json").write_text(json.dumps(REGISTRY))
    return tmp_path


# --- status ---------------------------------------------------------------

def test_status_reports_registry_contents(tmp_path):
    proj = _make_proj(tmp_path)
    result = runner.invoke(app, ["status", "--project", str(proj)])
    assert result.exit_code == 0, result.output
    assert "Status Test Project" in result.output
    assert "STUDY_01" in result.output
    assert "IN_PROGRESS" in result.output
    assert "1 script(s)" in result.output  # the single L01


def test_status_errors_without_registry(tmp_path):
    result = runner.invoke(app, ["status", "--project", str(tmp_path)])
    assert "no project_registry.json" in result.output


# --- checklist ------------------------------------------------------------

def test_checklist_prints_file(tmp_path):
    (tmp_path / "CHECKLIST.md").write_text("# Checklist\n\n- [ ] L01: load data\n")
    result = runner.invoke(app, ["checklist", "--project", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "L01: load data" in result.output


def test_checklist_errors_when_missing(tmp_path):
    result = runner.invoke(app, ["checklist", "--project", str(tmp_path)])
    assert "no CHECKLIST.md" in result.output


# --- version --------------------------------------------------------------

def test_version_flag_reports_package_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0, result.output
    assert __version__ in result.output


def test_version_up_log_archive_round_trip(tmp_path):
    proj = _make_proj(tmp_path)

    # Nothing archived yet.
    assert "No version history yet" in runner.invoke(
        app, ["version", "log", "--project", str(proj)]).output
    assert "No archived versions yet" in runner.invoke(
        app, ["version", "archive", "--project", str(proj)]).output

    # First bump lands at v0.1 and copies the tracked trees.
    up = runner.invoke(app, ["version", "up", "--project", str(proj)])
    assert up.exit_code == 0, up.output
    archived = sorted(d.name for d in (proj / "_archive").iterdir() if d.is_dir())
    assert len(archived) == 1 and archived[0].startswith("v0.1_")
    assert (proj / "_archive" / archived[0] / "project_registry.json").exists()
    assert (proj / "_archive" / archived[0] / "code" / "loading" / "L01_load.py").exists()

    # Second bump increments the minor version.
    runner.invoke(app, ["version", "up", "--project", str(proj)])
    archived = sorted(d.name for d in (proj / "_archive").iterdir() if d.is_dir())
    assert len(archived) == 2
    assert any(d.startswith("v0.2_") for d in archived), archived

    # log and archive now report both.
    log_out = runner.invoke(app, ["version", "log", "--project", str(proj)]).output
    assert "v0.1" in log_out and "v0.2" in log_out
    arch_out = runner.invoke(app, ["version", "archive", "--project", str(proj)]).output
    assert "v0.1" in arch_out and "v0.2" in arch_out


def test_version_rejects_unknown_action(tmp_path):
    result = runner.invoke(app, ["version", "sideways", "--project", str(tmp_path)])
    assert result.exit_code == 1
