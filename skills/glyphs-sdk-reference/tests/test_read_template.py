"""Tests for read_template.py — read template/sample source + README."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import read_template

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestReadTemplate:
    """Test reading template source code."""

    def test_read_reporter(self, env_sdk_path):
        result = read_template.read_entry("reporter")
        assert result is not None
        assert "source" in result
        assert "class ____PluginClassName____" in result["source"]

    def test_read_returns_ast_info(self, env_sdk_path):
        result = read_template.read_entry("reporter")
        assert "classes" in result
        assert len(result["classes"]) > 0
        cls = result["classes"][0]
        assert "name" in cls
        assert "methods" in cls

    def test_read_returns_imports(self, env_sdk_path):
        result = read_template.read_entry("reporter")
        assert "imports" in result
        assert len(result["imports"]) > 0

    def test_read_includes_readme(self, env_sdk_path):
        """Reporter template has a README.md."""
        result = read_template.read_entry("reporter")
        assert "readme" in result
        assert result["readme"] is not None
        assert len(result["readme"]) > 0

    def test_read_filter_with_variant(self, env_sdk_path):
        """Filter 'without dialog' variant."""
        result = read_template.read_entry("filter", variant="without dialog")
        assert result is not None
        assert "source" in result

    def test_read_nonexistent(self, env_sdk_path):
        result = read_template.read_entry("nonexistent_xyz")
        assert result is None


class TestReadSample:
    """Test reading sample source code."""

    def test_read_smiley(self, env_sdk_path):
        result = read_template.read_entry("Smiley Panel Plugin")
        assert result is not None
        assert "source" in result

    def test_read_callback(self, env_sdk_path):
        """Callback for context menu is a standalone script, not a bundle."""
        result = read_template.read_entry("Callback for context menu")
        assert result is not None
        assert "source" in result

    def test_sample_with_readme(self, env_sdk_path):
        """MultipleTools has a README.md."""
        result = read_template.read_entry("MultipleTools")
        assert result is not None
        assert "readme" in result
        assert result["readme"] is not None


class TestReadDrawingTools:
    """Test reading drawingTools.py."""

    def test_read_drawing_tools(self, env_sdk_path):
        result = read_template.read_drawing_tools()
        assert result is not None
        assert "source" in result
        assert "classes" in result

    def test_drawing_tools_has_imports(self, env_sdk_path):
        result = read_template.read_drawing_tools()
        assert "imports" in result


class TestCLI:
    """Test CLI integration."""

    def test_cli_read_reporter(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_template.py"), "reporter"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "source" in data

    def test_cli_read_with_variant(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_template.py"),
             "filter", "--variant", "without dialog"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "source" in data

    def test_cli_read_sample(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_template.py"), "Smiley Panel Plugin"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "source" in data

    def test_cli_drawing_tools(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_template.py"), "--drawing-tools"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "source" in data

    def test_cli_nonexistent(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_template.py"), "nonexistent_xyz"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 1
