"""Shared fixtures for glyphs-localization tests."""

from pathlib import Path

import pytest

# Skill root (glyphs-localization/)
SKILL_ROOT = Path(__file__).parent.parent

# Scripts directory
SCRIPTS_DIR = SKILL_ROOT / "scripts"

# Glyphs 3 app path
GLYPHS_APP = Path("/Applications/Glyphs 3.app")

# Whether Glyphs 3 is installed
GLYPHS_INSTALLED = GLYPHS_APP.is_dir()


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "requires_glyphs: marks tests requiring Glyphs 3 installation")


def pytest_collection_modifyitems(config, items):
    """Skip tests marked requires_glyphs when Glyphs is not installed."""
    if GLYPHS_INSTALLED:
        return
    skip_marker = pytest.mark.skip(reason="Glyphs 3 not installed")
    for item in items:
        if "requires_glyphs" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture
def scripts_dir():
    """Return the scripts directory path."""
    return SCRIPTS_DIR


@pytest.fixture
def translate_script(scripts_dir):
    """Return path to translate-term.sh."""
    return scripts_dir / "translate-term.sh"


@pytest.fixture
def search_script(scripts_dir):
    """Return path to search-glyphs-term.sh."""
    return scripts_dir / "search-glyphs-term.sh"


@pytest.fixture
def extract_script(scripts_dir):
    """Return path to extract-nib-strings.sh."""
    return scripts_dir / "extract-nib-strings.sh"
