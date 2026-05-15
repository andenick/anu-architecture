"""Test anu-architecture init."""
from pathlib import Path

from typer.testing import CliRunner

from anu_architecture.cli import app

runner = CliRunner()


def test_init_non_interactive_creates_tree(tmp_path):
    target = tmp_path / "test-proj"
    result = runner.invoke(app, [
        "init", "test-proj", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code == 0, result.output
    # 8 phase folders
    for phase in ("setup", "loading", "processing", "validation",
                  "manual", "analysis", "outputs", "exploration"):
        assert (target / "code" / phase).is_dir()
    # 6 data folders
    for sub in ("user-inputs", "raw-data", "int-data", "final-data",
                "adjusted-final-data", "scratch"):
        assert (target / "data" / sub).is_dir()
    # Output subdirs
    for sub in ("validation", "analysis", "exploration", "deliverables"):
        assert (target / "outputs" / sub).is_dir()
    # Key files
    assert (target / "project_registry.json").exists()
    assert (target / "run.py").exists()
    assert (target / "README.md").exists()
    assert (target / "DECISION_LOG.md").exists()
    assert (target / "CHECKLIST.md").exists()
    assert (target / ".gitignore").exists()


def test_init_refuses_existing_non_empty(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "file.txt").write_text("hi")
    result = runner.invoke(app, [
        "init", "existing", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code != 0
