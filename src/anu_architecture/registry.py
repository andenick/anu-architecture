"""project_registry.json loading + JSON Schema validation."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None  # type: ignore


SCHEMA_PATH = Path(__file__).parent / "schemas" / "project_registry.schema.json"


def load_registry(project: Path) -> dict:
    return json.loads((project / "project_registry.json").read_text(encoding="utf-8"))


def save_registry(project: Path, registry: dict) -> None:
    (project / "project_registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def validate_registry(registry: dict) -> list[str]:
    """Return list of validation errors; empty list = valid."""
    if Draft202012Validator is None:
        return []  # jsonschema not installed
    if not SCHEMA_PATH.exists():
        return []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    return [f"{'.'.join(str(p) for p in e.path)}: {e.message}"
            for e in v.iter_errors(registry)]
