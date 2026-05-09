"""Shared utilities for glyphs-python-api scripts.

Provides SDK path resolution and JSON output helpers.
Not meant to be executed directly.
"""

import json
import os
import sys
from pathlib import Path

# Relative path from scripts/ to GlyphsSDK
_RELATIVE_SDK_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "GlyphsSDK"


def get_sdk_path() -> Path:
    """Resolve GlyphsSDK path: GLYPHS_SDK_PATH env var > relative path."""
    env_path = os.environ.get("GLYPHS_SDK_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_dir():
            raise FileNotFoundError(f"GlyphsSDK not found at: {path}")
        return path

    if _RELATIVE_SDK_PATH.is_dir():
        return _RELATIVE_SDK_PATH

    raise FileNotFoundError(
        "GlyphsSDK not found. Set GLYPHS_SDK_PATH or ensure the submodule is cloned."
    )


def get_sphinx_rst_path() -> Path:
    """Return path to Sphinx Documentation/sphinx folder/index.rst."""
    return (
        get_sdk_path()
        / "ObjectWrapper"
        / "Sphinx Documentation"
        / "sphinx folder"
        / "index.rst"
    )


def get_init_py_path() -> Path:
    """Return path to ObjectWrapper/GlyphsApp/__init__.py."""
    return get_sdk_path() / "ObjectWrapper" / "GlyphsApp" / "__init__.py"


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)
