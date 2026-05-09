"""Shared fixtures for glyphs-light-table tests."""

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
load_script("_lighttable_utils")
load_script("read_api")

# Default Light Table path
_DEFAULT_LT_PATH = (
    Path.home()
    / "Library/Application Support/Glyphs 3/Repositories/Light-Table"
)

# Mock API source covering all parsing patterns:
# - Enum (DocumentState, ObjectStatus)
# - objc.lookUpClass (public + private)
# - GS extensions: property + objc.python_method
# - ObjC class extensions: pyobjc properties
# - Dataclass
MOCK_API_SOURCE = '''\
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Dict
import objc
from GlyphsApp import Glyphs, GSFont, GSGlyph, GSLayer

Signature = objc.lookUpClass("LightTableSignature")
Commit = objc.lookUpClass("LightTableCommit")
_LightTableInterface = objc.lookUpClass("LightTableInterface")

## GSFont

class DocumentState(Enum):
    UNKNOWN = 0
    NO_FILE = 1
    OPERATIONAL = 4

GSFont.lt_document_state = property(
    lambda self: DocumentState(_LightTableInterface.documentStateOfFont_(self))
)

GSFont.lt_load_version = objc.python_method(
    lambda self, record, callback: _LightTableInterface.font_loadVersionForRecord_completionHandler_(
        self, record, callback
    )
)

## GSGlyph

class ObjectStatus(Enum):
    UNKNOWN = 0
    UNMODIFIED = 1

GSGlyph.lt_status = property(lambda self: ObjectStatus(self.lightTableStatus()))

## GSLayer

GSLayer.lt_status = property(lambda self: ObjectStatus(self.lightTableStatus()))

## Signature

Signature.name = property(lambda self: self.pyobjc_instanceMethods.name())
Signature.email_address = property(
    lambda self: self.pyobjc_instanceMethods.emailAddress()
)

## Commit

Commit.id = property(lambda self: self.pyobjc_instanceMethods.id())
Commit.summary = property(lambda self: self.pyobjc_instanceMethods.summary())

## Component Integration Plan

@dataclass
class ComponentIntegrationPlan:
    strategies: Dict[str, "ComponentIntegrationStrategy"]
    fallback: "ComponentIntegrationStrategy"
'''


@pytest.fixture
def lt_path():
    """Return the Light Table path, skip if not present."""
    if not _DEFAULT_LT_PATH.exists():
        pytest.skip("Light Table not installed")
    return _DEFAULT_LT_PATH


@pytest.fixture
def api_source_path(lt_path):
    """Return path to lighttable/__init__.py."""
    path = lt_path / "Python API" / "lighttable" / "__init__.py"
    if not path.exists():
        pytest.skip("Light Table Python API not found")
    return path


@pytest.fixture
def mock_lt_dir(tmp_path):
    """Create a mock Light Table directory with API source."""
    lt_dir = tmp_path / "Light-Table"
    lt_dir.mkdir()
    api_dir = lt_dir / "Python API" / "lighttable"
    api_dir.mkdir(parents=True)
    init_file = api_dir / "__init__.py"
    init_file.write_text(MOCK_API_SOURCE)
    return lt_dir


@pytest.fixture
def mock_api_source(mock_lt_dir):
    """Return path to mock __init__.py."""
    return mock_lt_dir / "Python API" / "lighttable" / "__init__.py"
