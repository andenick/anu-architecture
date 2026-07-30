"""Test project_registry.json validation."""
import json
from pathlib import Path

import pytest

from anu_architecture.registry import validate_registry

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.mark.parametrize("example", sorted(p.name for p in EXAMPLES.iterdir()
                                           if (p / "project_registry.json").exists()))
def test_shipped_example_registry_is_valid(example):
    reg = json.loads((EXAMPLES / example / "project_registry.json")
                     .read_text(encoding="utf-8"))
    errors = validate_registry(reg)
    assert not errors, errors


def test_valid_registry():
    reg = {
        "version": "2.1.0",
        "project": "Test",
        "architecture": "Anu Architecture v2.1",
        "studies": {
            "STUDY_01": {"name": "Test study", "status": "PENDING"}
        },
        "datasets": {
            "panel": {"description": "Test panel"}
        }
    }
    errors = validate_registry(reg)
    assert not errors, errors


def test_invalid_status_rejected():
    reg = {
        "version": "2.1.0",
        "project": "Test",
        "architecture": "Anu Architecture v2.1",
        "studies": {
            "STUDY_01": {"name": "Test study", "status": "NOT_A_VALID_STATUS"}
        },
        "datasets": {"panel": {"description": "x"}}
    }
    errors = validate_registry(reg)
    assert errors  # may be empty if jsonschema not installed


def test_proxy_without_justification_rejected():
    reg = {
        "version": "2.1.0",
        "project": "Test",
        "architecture": "Anu Architecture v2.1",
        "studies": {},
        "datasets": {
            "panel": {
                "description": "x",
                "columns": {
                    "yield": {"proxy": True}  # missing proxy_justification
                }
            }
        }
    }
    errors = validate_registry(reg)
    assert errors  # may be empty if jsonschema not installed
