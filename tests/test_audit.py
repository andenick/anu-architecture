"""Test public-reproducibility audit."""
from pathlib import Path

from anu_architecture.audit import run_audit


def _make_proj(tmp_path: Path) -> Path:
    for ph in ("loading", "processing", "validation", "manual",
               "analysis", "outputs", "setup", "exploration"):
        (tmp_path / "code" / ph).mkdir(parents=True)
    (tmp_path / "project_registry.json").write_text(
        '''{"version": "2.1.0", "project": "test",
            "architecture": "Anu Architecture v2.1",
            "studies": {}, "datasets": {}}''')
    return tmp_path


def test_clean_project_passes(tmp_path):
    proj = _make_proj(tmp_path)
    rc = run_audit(proj)
    assert rc == 0


def test_hardcoded_local_path_fails(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L01_load.py").write_text(
        '''"""Public Source: https://fred.stlouisfed.org"""\n'''
        '''path = "/Users/alice/data/file.csv"\n'''
    )
    rc = run_audit(proj)
    assert rc == 1


def test_random_in_loading_fails(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L01_load.py").write_text(
        '''"""Public Source: https://fred.stlouisfed.org"""\n'''
        '''import numpy as np\nx = np.random.rand(10)\n'''
    )
    rc = run_audit(proj)
    assert rc == 1


def test_missing_public_source_warns_not_fails(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L01_load.py").write_text(
        '''# No public source header\nimport pandas as pd\n'''
    )
    rc = run_audit(proj)
    assert rc == 0  # warn only

    rc_strict = run_audit(proj, strict=True)
    assert rc_strict == 1


def test_l00_run_all_is_exempt_from_the_public_source_rule(tmp_path):
    """L00_run_all is the per-phase convenience runner, not a loader. Holding
    it to the Public Source: rule made a freshly scaffolded Python project
    fail `audit --strict` on a file the scaffold itself had just written."""
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L00_run_all.py").write_text(
        '"""Run every L01-L99 in this phase."""\n')
    assert run_audit(proj, strict=True) == 0

    # ...but a real loader with no source header still warns.
    (proj / "code" / "loading" / "L01_load.py").write_text("import pandas as pd\n")
    assert run_audit(proj, strict=True) == 1


# --- proxy_justification negative control ---------------------------------

def test_proxy_without_justification_warns_and_fails_strict(tmp_path):
    """Negative control for the WARN branch: prove it can actually fire."""
    proj = _make_proj(tmp_path)
    (proj / "project_registry.json").write_text(
        '''{"version": "2.1.0", "project": "test",
            "architecture": "Anu Architecture v2.1",
            "studies": {},
            "datasets": {"panel": {"description": "p",
                                   "columns": {"yield": {"proxy": true}}}}}''')
    assert run_audit(proj) == 0            # WARN only
    assert run_audit(proj, strict=True) == 1


def test_proxy_with_justification_is_clean(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "project_registry.json").write_text(
        '''{"version": "2.1.0", "project": "test",
            "architecture": "Anu Architecture v2.1",
            "studies": {},
            "datasets": {"panel": {"description": "p",
                                   "columns": {"yield": {"proxy": true,
                                   "proxy_justification": "documented"}}}}}''')
    assert run_audit(proj, strict=True) == 0


# --- coverage: utils/ and the root orchestrator ---------------------------

def test_hardcoded_path_in_utils_fails(tmp_path):
    """utils/paths.* is the designated home of every path constant, so it is
    the likeliest place a machine-local path hides. It must be in scope."""
    proj = _make_proj(tmp_path)
    (proj / "utils").mkdir()
    (proj / "utils" / "paths.py").write_text('ROOT = "C:/Users/alice/project"\n')
    assert run_audit(proj) == 1


def test_hardcoded_path_in_root_orchestrator_fails(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "run.py").write_text('PROJECT = "/Users/alice/project"\n')
    assert run_audit(proj) == 1


def test_random_outside_data_construction_is_allowed(tmp_path):
    """np.random is legitimate in analysis/ and in utils/ — only the five
    data-construction phase folders are checked."""
    proj = _make_proj(tmp_path)
    (proj / "code" / "analysis" / "A01_bootstrap.py").write_text(
        "import numpy as np\nx = np.random.rand(10)\n")
    (proj / "utils").mkdir()
    (proj / "utils" / "helpers.py").write_text(
        "import numpy as np\nx = np.random.rand(10)\n")
    assert run_audit(proj, strict=True) == 0
