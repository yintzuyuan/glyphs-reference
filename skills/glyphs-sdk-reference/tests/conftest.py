"""Shared fixtures for glyphs-sdk-reference tests."""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

# Scripts directory for this skill
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def load_script(name: str):
    """Load a script module by file path, avoiding sys.path pollution."""
    file_path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Eagerly load all scripts in dependency order
load_script("_sdk_utils")
load_script("list_templates")
load_script("read_template")
load_script("search_methods")

# Skill root (glyphs-sdk-reference/)
SKILL_ROOT = Path(__file__).parent.parent


def _resolve_sdk_path() -> Path:
    """Resolve GlyphsSDK path with fallbacks for different deployment layouts.

    Supports:
    - Standalone layout: <repo>/{skills/<skill>, GlyphsSDK}
    - Embedded layout (e.g. submodule under parent): <parent>/plugins/<plugin>/{skills/<skill>, ...}, with GlyphsSDK at <parent>/GlyphsSDK
    - Explicit env var: GLYPHS_SDK_PATH

    Resolution order: env var → public repo layout → marketplace layout.
    """
    env_path = os.environ.get("GLYPHS_SDK_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    public_repo_sdk = SKILL_ROOT.parent.parent / "GlyphsSDK"
    if public_repo_sdk.exists():
        return public_repo_sdk

    marketplace_sdk = SKILL_ROOT.parent.parent.parent.parent / "GlyphsSDK"
    if marketplace_sdk.exists():
        return marketplace_sdk

    # Fallback (will fail .exists() check; sdk_path fixture will pytest.skip)
    return public_repo_sdk


SDK_PATH = _resolve_sdk_path()


@pytest.fixture
def sdk_path():
    """Return the GlyphsSDK path, skip if not present."""
    if not SDK_PATH.exists():
        pytest.skip("GlyphsSDK submodule not available")
    return SDK_PATH


@pytest.fixture
def plugins_py_path(sdk_path):
    """Return path to plugins.py."""
    path = sdk_path / "ObjectWrapper" / "GlyphsApp" / "plugins.py"
    if not path.exists():
        pytest.skip("plugins.py not found")
    return path


@pytest.fixture
def templates_path(sdk_path):
    """Return path to Python Templates/."""
    path = sdk_path / "Python Templates"
    if not path.exists():
        pytest.skip("Python Templates not found")
    return path


@pytest.fixture
def samples_path(sdk_path):
    """Return path to Python Samples/."""
    path = sdk_path / "Python Samples"
    if not path.exists():
        pytest.skip("Python Samples not found")
    return path


@pytest.fixture
def env_sdk_path(sdk_path, monkeypatch):
    """Set GLYPHS_SDK_PATH environment variable."""
    monkeypatch.setenv("GLYPHS_SDK_PATH", str(sdk_path))
    return sdk_path
