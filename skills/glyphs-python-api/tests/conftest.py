"""Shared fixtures for glyphs-python-api tests."""

import importlib.util
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
load_script("_parse_rst")
load_script("read_class")
load_script("search_api")

# Skill root (glyphs-python-api/)
SKILL_ROOT = Path(__file__).parent.parent

# GlyphsSDK path relative to skill
SDK_PATH = SKILL_ROOT.parent.parent.parent.parent / "GlyphsSDK"


@pytest.fixture
def sdk_path():
    """Return the GlyphsSDK path, skip if not present."""
    if not SDK_PATH.exists():
        pytest.skip("GlyphsSDK submodule not available")
    return SDK_PATH


@pytest.fixture
def sphinx_rst_path(sdk_path):
    """Return path to Sphinx index.rst."""
    path = (
        sdk_path
        / "ObjectWrapper"
        / "Sphinx Documentation"
        / "sphinx folder"
        / "index.rst"
    )
    if not path.exists():
        pytest.skip("index.rst not found")
    return path


@pytest.fixture
def init_py_path(sdk_path):
    """Return path to __init__.py."""
    path = sdk_path / "ObjectWrapper" / "GlyphsApp" / "__init__.py"
    if not path.exists():
        pytest.skip("__init__.py not found")
    return path


@pytest.fixture
def env_sdk_path(sdk_path, monkeypatch):
    """Set GLYPHS_SDK_PATH environment variable."""
    monkeypatch.setenv("GLYPHS_SDK_PATH", str(sdk_path))
    return sdk_path
