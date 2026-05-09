"""Tests for read_component.py — Read Vanilla UI component details."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import _vanilla_utils
import read_component

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestReadComponent:
    """Test reading a component from mock source files."""

    def test_read_existing_class(self, sample_init_py, sample_source_file):
        """Reads a class with source, docstring, and methods."""
        mapping = {"Window": "vanillaWindows"}
        result = read_component.read_component(
            "Window", mapping, sample_source_file.parent
        )
        assert result is not None
        assert result["class_name"] == "Window"
        assert "source" in result
        assert "methods" in result
        assert result["module"] == "vanillaWindows"

    def test_read_from_multiclass_file(self, sample_init_py, sample_source_file):
        """Extracts only the target class from a multi-class file."""
        mapping = {"FloatingWindow": "vanillaWindows"}
        result = read_component.read_component(
            "FloatingWindow", mapping, sample_source_file.parent
        )
        assert result is not None
        assert result["class_name"] == "FloatingWindow"
        assert "class Window" not in result.get("source", "")

    def test_summary_mode(self, sample_init_py, sample_source_file):
        """Summary mode returns methods list without source."""
        mapping = {"Window": "vanillaWindows"}
        result = read_component.read_component(
            "Window", mapping, sample_source_file.parent, summary=True
        )
        assert result is not None
        assert "methods" in result
        assert "source" not in result

    def test_not_found_returns_none(self, sample_init_py, sample_source_file):
        """Returns None for a class not in the mapping."""
        mapping = {"Window": "vanillaWindows"}
        result = read_component.read_component(
            "NonExistent", mapping, sample_source_file.parent
        )
        assert result is None

    def test_result_includes_file_path(self, sample_init_py, sample_source_file):
        """Result includes the source file path."""
        mapping = {"Window": "vanillaWindows"}
        result = read_component.read_component(
            "Window", mapping, sample_source_file.parent
        )
        assert "file_path" in result
        assert "vanillaWindows.py" in result["file_path"]


class TestReadComponentIntegration:
    """Integration tests with real Vanilla library."""

    def test_read_real_window(self, vanilla_path):
        """Reads Window class from real vanillaWindows.py."""
        mapping = _vanilla_utils.parse_init_imports(vanilla_path / "__init__.py")
        result = read_component.read_component("Window", mapping, vanilla_path)
        assert result is not None
        assert result["class_name"] == "Window"
        assert len(result["methods"]) > 0

    def test_read_real_button(self, vanilla_path):
        """Reads Button class from real vanillaButton.py."""
        mapping = _vanilla_utils.parse_init_imports(vanilla_path / "__init__.py")
        result = read_component.read_component("Button", mapping, vanilla_path)
        assert result is not None
        assert result["class_name"] == "Button"


class TestReadComponentCLI:
    """Test CLI interface via subprocess."""

    def test_cli_outputs_json(self, env_vanilla_path):
        """CLI outputs valid JSON for a known component."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_component.py"), "Button"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["class_name"] == "Button"

    def test_cli_not_found_exits_1(self, env_vanilla_path):
        """CLI exits with code 1 for unknown component."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_component.py"), "NonExistent"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data

    def test_cli_summary_flag(self, env_vanilla_path):
        """CLI --summary returns methods without source."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "read_component.py"),
                "Button",
                "--summary",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "methods" in data
        assert "source" not in data
