"""Test project_registry.json validation."""
import json

from anu_architecture.registry import validate_registry


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
