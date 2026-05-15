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
