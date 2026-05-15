"""Test script discovery."""
from pathlib import Path

from anu_architecture.discovery import discover_all, discover_scripts


def _make_proj(tmp_path: Path) -> Path:
    for ph in ("setup", "loading", "processing", "validation",
               "manual", "analysis", "outputs", "exploration"):
        (tmp_path / "code" / ph).mkdir(parents=True)
    return tmp_path


def test_discover_scripts_sorted_numerically(tmp_path):
    proj = _make_proj(tmp_path)
    # Create out of order
    (proj / "code" / "loading" / "L10_late.py").write_text("")
    (proj / "code" / "loading" / "L02_mid.py").write_text("")
    (proj / "code" / "loading" / "L01_first.py").write_text("")
    scripts = discover_scripts(proj, "L")
    names = [s.name for s in scripts]
    assert names == ["L01_first.py", "L02_mid.py", "L10_late.py"]


def test_discover_scripts_ignores_invalid_names(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L01_ok.py").write_text("")
    (proj / "code" / "loading" / "L1_no_pad.py").write_text("")
    (proj / "code" / "loading" / "Lxx_bad.py").write_text("")
    scripts = discover_scripts(proj, "L")
    assert [s.name for s in scripts] == ["L01_ok.py"]


def test_discover_all_respects_phase_order(tmp_path):
    proj = _make_proj(tmp_path)
    (proj / "code" / "loading" / "L01_a.py").write_text("")
    (proj / "code" / "processing" / "P01_b.py").write_text("")
    (proj / "code" / "setup" / "S01_c.py").write_text("")
    out = discover_all(proj, order="SLP")
    phases = [ph for ph, _ in out]
    assert phases == ["S", "L", "P"]
