"""Shared utilities for GlyphsSDK reference scripts.

Provides SDK path resolution and JSON output helpers.
Not meant to be executed directly.
"""

import json
import os
import sys
from pathlib import Path

# Candidate relative paths from scripts/_sdk_utils.py to GlyphsSDK.
# Order: standalone repo layout first, then marketplace-embedded layout.
_SCRIPTS_DIR = Path(__file__).parent
_STANDALONE_SDK_PATH = _SCRIPTS_DIR.parent.parent.parent / "GlyphsSDK"
_MARKETPLACE_SDK_PATH = _SCRIPTS_DIR.parent.parent.parent.parent.parent / "GlyphsSDK"


def get_sdk_path() -> Path:
    """Resolve GlyphsSDK path: GLYPHS_SDK_PATH env var > relative paths."""
    env_path = os.environ.get("GLYPHS_SDK_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_dir():
            raise FileNotFoundError(f"GlyphsSDK not found at: {path}")
        return path

    for candidate in (_STANDALONE_SDK_PATH, _MARKETPLACE_SDK_PATH):
        if candidate.is_dir():
            return candidate

    raise FileNotFoundError(
        "GlyphsSDK not found. Set GLYPHS_SDK_PATH or ensure the submodule is cloned."
    )


def get_plugins_py_path() -> Path:
    """Return path to ObjectWrapper/GlyphsApp/plugins.py."""
    return get_sdk_path() / "ObjectWrapper" / "GlyphsApp" / "plugins.py"


def get_templates_path() -> Path:
    """Return path to Python Templates/ directory."""
    return get_sdk_path() / "Python Templates"


def get_samples_path() -> Path:
    """Return path to Python Samples/ directory."""
    return get_sdk_path() / "Python Samples"


def get_drawing_tools_path() -> Path:
    """Return path to ObjectWrapper/GlyphsApp/drawingTools.py."""
    return get_sdk_path() / "ObjectWrapper" / "GlyphsApp" / "drawingTools.py"


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)
