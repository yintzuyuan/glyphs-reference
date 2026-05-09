"""Shared utilities for glyphs-light-table scripts.

Provides Light Table path resolution and JSON output helpers.
Not meant to be executed directly.
"""

import json
import os
import sys
from pathlib import Path

_DEFAULT_LT_PATH = (
    Path.home() / "Library/Application Support/Glyphs 3/Repositories/Light-Table"
)


def get_lighttable_path() -> Path:
    """Resolve Light Table path: GLYPHS_LIGHT_TABLE_PATH env var > default path."""
    env_path = os.environ.get("GLYPHS_LIGHT_TABLE_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Light Table not found at: {path}")
        return path

    if _DEFAULT_LT_PATH.is_dir():
        return _DEFAULT_LT_PATH

    raise FileNotFoundError(
        "Light Table not found. Set GLYPHS_LIGHT_TABLE_PATH or install via "
        "Glyphs Plugin Manager."
    )


def get_api_source_path() -> Path:
    """Return path to Python API/lighttable/__init__.py."""
    return get_lighttable_path() / "Python API" / "lighttable" / "__init__.py"


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)
