"""Shared fixtures for glyphs-web-search tests."""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "network: marks tests requiring network access")


@pytest.fixture
def sample_html():
    """Sample HTML for testing html_to_text."""
    return """
    <html>
    <head><title>Test</title></head>
    <body>
    <header><nav>Navigation</nav></header>
    <script>var x = 1;</script>
    <style>.foo { color: red; }</style>
    <h1>Main Title</h1>
    <p>First paragraph with <strong>bold</strong> text.</p>
    <p>Second paragraph.</p>
    <ul>
        <li>Item one</li>
        <li>Item two</li>
    </ul>
    <footer>Footer content</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_custom_params_text():
    """Sample text mimicking custom parameters page structure."""
    return """\
### Custom Parameters

Custom parameters provide extra settings.

postscriptSlantAngle

float The slant angle for PostScript.

glyphOrder

string A list of glyph names.

postscriptIsFixedPitch

boolean Whether the font is monospaced.

blueValues

list The list of blue values.
These define alignment zones.
Used for hinting.
"""
