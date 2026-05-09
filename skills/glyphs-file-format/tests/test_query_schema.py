"""Tests for query_schema.py CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
QUERY_SCHEMA = SCRIPTS_DIR / "query_schema.py"


def run_query_schema(*args, env_override=None):
    """Run query_schema.py as a subprocess and return result."""
    result = subprocess.run(
        [sys.executable, str(QUERY_SCHEMA), *args],
        capture_output=True,
        text=True,
        env=env_override,
    )
    return result


class TestQuerySchemaQuery:
    """Test querying a specific $defs entry."""

    def test_query_anchor(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema("anchor", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "anchor"
        assert data["schema"] == "glyphs-3"
        assert "definition" in data
        assert data["definition"]["type"] == "object"

    def test_query_with_different_schema(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema(
            "anchor", "--schema", "glyphs-1", env_override=env
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema"] == "glyphs-1"

    def test_query_not_found(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema("nonexistent_xyz", env_override=env)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data

    def test_query_glyph(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema("glyph", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "glyph"
        assert "properties" in data["definition"]


class TestQuerySchemaList:
    """Test listing all $defs keys."""

    def test_list_default(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema("--list", env_override=env)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema"] == "glyphs-3"
        assert len(data["definitions"]) > 20
        assert "anchor" in data["definitions"]
        assert "glyph" in data["definitions"]

    def test_list_fontinfo(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema(
            "--list", "--schema", "fontinfo-3", env_override=env
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema"] == "fontinfo-3"


class TestQuerySchemaEdgeCases:
    """Test edge cases."""

    def test_no_args_shows_error(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema(env_override=env)
        assert result.returncode != 0

    def test_invalid_schema_name(self, env_sdk_path):
        import os

        env = os.environ.copy()
        env["GLYPHS_SDK_PATH"] = str(env_sdk_path)
        result = run_query_schema(
            "anchor", "--schema", "nonexistent-schema", env_override=env
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data
