"""Tests for query_spec.py CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
QUERY_SPEC = SCRIPTS_DIR / "query_spec.py"


def run_query_spec(*args, env_override=None):
    """Run query_spec.py as a subprocess and return parsed JSON."""
    result = subprocess.run(
        [sys.executable, str(QUERY_SPEC), *args],
        capture_output=True,
        text=True,
        env=env_override,
    )
    return result


class TestQuerySpecQuery:
    """Test querying a specific definition."""

    def test_query_v3_anchor(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("anchor", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "anchor"
        assert data["version"] == 3
        assert "definition" in data
        assert "GSAnchor" in data["definition"]

    def test_query_v2_anchor(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("anchor", "--version", "2", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "anchor"
        assert data["version"] == 2

    def test_query_not_found(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("nonexistent_type_xyz", env_override=env)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data

    def test_query_glyph(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("glyph", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "glyph"
        assert "glyphname" in data["definition"]


class TestQuerySpecList:
    """Test listing all definitions."""

    def test_list_v3(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("--list", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["version"] == 3
        assert len(data["definitions"]) > 20
        names = [d["name"] for d in data["definitions"]]
        assert "anchor" in names
        assert "glyph" in names

    def test_list_v2(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec("--list", "--version", "2", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["version"] == 2
        assert len(data["definitions"]) > 10


class TestQuerySpecEdgeCases:
    """Test edge cases."""

    def test_no_args_shows_error(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_spec(env_override=env)
        assert result.returncode != 0
