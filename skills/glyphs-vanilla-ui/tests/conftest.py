"""Shared fixtures for glyphs-vanilla-ui tests."""

import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/ to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Default Vanilla path inside Glyphs 3
_DEFAULT_VANILLA_PATH = (
    Path.home() / "Library/Application Support/Glyphs 3/Repositories/vanilla/Lib/vanilla"
)


@pytest.fixture
def vanilla_path():
    """Return the local Vanilla path, skip if not present."""
    if not _DEFAULT_VANILLA_PATH.exists():
        pytest.skip("Vanilla library not available")
    return _DEFAULT_VANILLA_PATH


@pytest.fixture
def init_py_path(vanilla_path):
    """Return path to vanilla/__init__.py."""
    path = vanilla_path / "__init__.py"
    if not path.exists():
        pytest.skip("vanilla/__init__.py not found")
    return path


@pytest.fixture
def env_vanilla_path(vanilla_path, monkeypatch):
    """Set GLYPHS_VANILLA_PATH environment variable."""
    monkeypatch.setenv("GLYPHS_VANILLA_PATH", str(vanilla_path))
    return vanilla_path


@pytest.fixture
def sample_init_py(tmp_path):
    """Create a mock __init__.py with simple and multiline imports."""
    content = textwrap.dedent("""\
        from vanilla.vanillaButton import Button
        from vanilla.vanillaTextEditor import TextEditor
        from vanilla.vanillaList2 import (
            List2,
            List2DataSource,
            List2GroupRow,
        )
        from vanilla.vanillaWindows import (
            Window,
            FloatingWindow,
        )
    """)
    init_file = tmp_path / "__init__.py"
    init_file.write_text(content)
    return init_file


@pytest.fixture
def sample_source_file(tmp_path):
    """Create a mock source file with multiple classes."""
    content = textwrap.dedent('''\
        class Window(BaseWindow):
            """A standard window."""

            def __init__(self, posSize, title="Window", closable=True):
                """Initialize the window."""
                pass

            def open(self):
                """Open the window."""
                pass

            def close(self):
                """Close the window."""
                pass

        class FloatingWindow(BaseWindow):
            """A floating utility window."""

            def __init__(self, posSize, title=""):
                """Initialize the floating window."""
                pass

            def setTitle(self, title):
                """Set the window title."""
                pass
    ''')
    source_file = tmp_path / "vanillaWindows.py"
    source_file.write_text(content)
    return source_file
