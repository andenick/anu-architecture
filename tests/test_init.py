"""Test anu-architecture init."""
import subprocess
import sys

import pytest
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


@pytest.mark.parametrize("language,orchestrator,paths_file", [
    ("Python", "run.py", "utils/paths.py"),
    ("R", "run.R", "utils/paths.R"),
    ("Stata", "run.do", "utils/paths.do"),
])
def test_init_scaffolds_promised_files(tmp_path, language, orchestrator, paths_file):
    """Every advertised language must get the files its README tells the user
    to use — most importantly config/api_keys.env.example, which both the
    generated README and the generated .gitignore reference by name."""
    target = tmp_path / f"proj-{language}"
    result = runner.invoke(app, [
        "init", f"proj-{language}", "--language", language,
        "--location", str(target), "--yes",
    ])
    assert result.exit_code == 0, result.output
    assert (target / orchestrator).exists()
    assert (target / paths_file).exists()
    assert (target / "config" / "api_keys.env.example").exists()

    gitignore = (target / ".gitignore").read_text(encoding="utf-8")
    assert "config/api_keys.env" in gitignore

    readme = (target / "README.md").read_text(encoding="utf-8")
    if "config/api_keys.env.example" in readme:
        assert (target / "config" / "api_keys.env.example").exists()


@pytest.mark.parametrize("language,expected", [
    ("Python", "python run.py"),
    ("R", "Rscript run.R"),
    ("Stata", "stata -b do run.do"),
])
def test_generated_readme_names_the_right_runner(tmp_path, language, expected):
    target = tmp_path / f"readme-{language}"
    runner.invoke(app, [
        "init", f"readme-{language}", "--language", language,
        "--location", str(target), "--yes",
    ])
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert expected in readme, readme


def test_scaffolded_run_py_lists_each_script_once(tmp_path):
    """Regression: the scaffolded run.py must not pick up XX00_run_all.py.
    If it does, every script executes twice — once directly and once from
    inside its phase orchestrator."""
    target = tmp_path / "dryrun-proj"
    result = runner.invoke(app, [
        "init", "dryrun-proj", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code == 0, result.output
    # The scaffold really does ship the XX00 files we must not run.
    assert (target / "code" / "loading" / "L00_run_all.py").exists()

    proc = subprocess.run([sys.executable, "run.py", "--dry-run"],
                          cwd=target, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    listed = [ln.split()[-1] for ln in proc.stdout.splitlines()
              if ln.startswith("  ") and ln.strip()]
    assert listed, proc.stdout
    assert not [n for n in listed if "00_run_all" in n], proc.stdout
    # The scaffold ships no V## scripts, so the deliberate second V pass
    # cannot account for a repeat here: any duplicate is the XX00 bug.
    assert len(listed) == len(set(listed)), proc.stdout

    phases = [ln.strip().split()[0] for ln in proc.stdout.splitlines()
              if ln.startswith("  ") and ln.strip()]
    if "O" in phases:
        assert phases.index("O") == len(phases) - 1, proc.stdout


def test_init_refuses_existing_non_empty(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "file.txt").write_text("hi")
    result = runner.invoke(app, [
        "init", "existing", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code != 0
