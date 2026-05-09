"""Shared fixtures for glyphs-file-format tests."""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Skill root (glyphs-file-format/)
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
def spec_v3_path(sdk_path):
    """Return path to GlyphsFileFormatv3.md."""
    path = sdk_path / "GlyphsFileFormat" / "GlyphsFileFormatv3.md"
    if not path.exists():
        pytest.skip("GlyphsFileFormatv3.md not found")
    return path


@pytest.fixture
def spec_v2_path(sdk_path):
    """Return path to GlyphsFileFormatv2.md."""
    path = sdk_path / "GlyphsFileFormat" / "GlyphsFileFormatv2.md"
    if not path.exists():
        pytest.skip("GlyphsFileFormatv2.md not found")
    return path


@pytest.fixture
def schema_v3_path(sdk_path):
    """Return path to glyphs-3.schema.json."""
    path = sdk_path / "GlyphsFileFormat" / "Schemas" / "glyphs-3.schema.json"
    if not path.exists():
        pytest.skip("glyphs-3.schema.json not found")
    return path


@pytest.fixture
def env_sdk_path(sdk_path, monkeypatch):
    """Set GLYPHS_SDK_PATH environment variable."""
    monkeypatch.setenv("GLYPHS_SDK_PATH", str(sdk_path))
    return sdk_path


@pytest.fixture
def sample_spec_v3():
    """Mock v3 spec markdown with 3 definitions."""
    return """\
## Definitions

- <a name="spec-glyphs-3-anchor"></a><code><strong>anchor</strong>: object</code> – (`GSAnchor`)
    - <code><strong>name</strong>: string</code> – The name of the anchor.
    - <code><strong>pos</strong>: array = [0, 0]</code> – The position.
- <a name="spec-glyphs-3-axis"></a><code><strong>axis</strong>: object</code> – (`GSAxis`)
    - <code><strong>name</strong>: string = ""</code> – The user-facing name.
    - <code><strong>tag</strong>: string = ""</code> – The OpenType tag.
- <a name="spec-glyphs-3-glyph"></a><code><strong>glyph</strong>: object</code> – (`GSGlyph`)
    - <code><strong>glyphname</strong>: string</code> – The name of the glyph.
    - <code><strong>layers</strong>: array</code> – The layers.

## Changes
"""


@pytest.fixture
def sample_spec_v2():
    """Mock v2 spec markdown with 2 definitions."""
    return """\
## Definitions

- <a name="spec-glyphs-1-anchor"></a><code><strong>anchor</strong>: object</code> – (`GSAnchor`)
    - <code><strong>name</strong>: string</code> – The name of the anchor.
    - <code><strong>position</strong>: string</code> – The position.
- <a name="spec-glyphs-1-glyph"></a><code><strong>glyph</strong>: object</code> – (`GSGlyph`)
    - <code><strong>glyphname</strong>: string</code> – The name of the glyph.

## Changes
"""


@pytest.fixture
def sample_schema_v3():
    """Mock JSON Schema with $defs structure."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": {
            "anchor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the anchor."},
                    "pos": {"type": "array", "default": [0, 0]},
                },
                "required": ["name"],
            },
            "axis": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "default": ""},
                    "tag": {"type": "string", "default": ""},
                },
            },
            "glyph": {
                "type": "object",
                "properties": {
                    "glyphname": {"type": "string"},
                    "layers": {"type": "array"},
                },
                "required": ["glyphname", "layers"],
            },
        },
        "type": "object",
        "properties": {},
    }
