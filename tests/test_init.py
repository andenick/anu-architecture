"""Test anu-architecture init."""
import json
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


@pytest.mark.parametrize("language,ext,marker", [
    ("R", ".R", "#"),
    ("Stata", ".do", "*"),
])
def test_non_python_stubs_are_not_python(tmp_path, language, ext, marker):
    """Regression: the L##/A## stubs were emitted as Python for every
    language. A `\"\"\"` docstring is a syntax error in R and in Stata, so the
    first script the scaffolded orchestrator reached aborted the run."""
    target = tmp_path / f"stub-{language}"
    result = runner.invoke(app, [
        "init", f"stub-{language}", "--language", language,
        "--location", str(target), "--yes",
    ])
    assert result.exit_code == 0, result.output

    stubs = [target / "code" / "loading" / f"L01_load_fred{ext}",
             target / "code" / "analysis" / f"A01_study_01{ext}"]
    for stub in stubs:
        assert stub.exists(), stub
        text = stub.read_text(encoding="utf-8")
        assert '"""' not in text, text
        for line in text.splitlines():
            if line.strip():
                assert line.startswith(marker), (stub, line)
    # The audit gate wants a Public Source: header on every L## script.
    assert "Public Source:" in stubs[0].read_text(encoding="utf-8")


def test_scaffold_stamps_the_installed_architecture_version(tmp_path):
    """The registry used to hardcode `Anu Architecture v2.1`, so every project
    scaffolded by a later release claimed the wrong architecture version."""
    from anu_architecture import __version__

    target = tmp_path / "stamp-proj"
    result = runner.invoke(app, [
        "init", "stamp-proj", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code == 0, result.output
    registry = json.loads((target / "project_registry.json").read_text(encoding="utf-8"))
    short = ".".join(__version__.split(".")[:2])
    assert registry["architecture"] == f"Anu Architecture v{short}"


def test_stata_orchestrator_skips_xx00_case_insensitively(tmp_path):
    """Stata's `dir` extended macro function reports names in whatever case
    the OS gives it — Windows lower-cases them — so an exact-case comparison
    against `L00_run_all.do` silently never skips."""
    target = tmp_path / "stata-skip"
    runner.invoke(app, [
        "init", "stata-skip", "--language", "Stata",
        "--location", str(target), "--yes",
    ])
    run_do = (target / "run.do").read_text(encoding="utf-8")
    assert "strlower(" in run_do, run_do
    assert '"`f\'" != "`phase\'00_run_all.do"' not in run_do, run_do


def test_r_orchestrator_honours_dry_run(tmp_path):
    """The generated R README advertises `Rscript run.R --dry-run`; run.R
    used to ignore its arguments and execute the whole pipeline instead."""
    target = tmp_path / "r-dry"
    runner.invoke(app, [
        "init", "r-dry", "--language", "R",
        "--location", str(target), "--yes",
    ])
    run_r = (target / "run.R").read_text(encoding="utf-8")
    assert "commandArgs(" in run_r, run_r
    assert "'--dry-run' %in% args" in run_r, run_r
    assert "if (!dry_run) source(s)" in run_r, run_r


def test_init_refuses_existing_non_empty(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "file.txt").write_text("hi")
    result = runner.invoke(app, [
        "init", "existing", "--language", "Python",
        "--location", str(target), "--yes",
    ])
    assert result.exit_code != 0
