"""Tests for _vanilla_utils.py — Vanilla path resolution and AST parsing."""

import json
from pathlib import Path

import pytest

import _vanilla_utils


class TestGetVanillaPath:
    """Test Vanilla path resolution: GLYPHS_VANILLA_PATH > GLYPHS_REPOSITORIES_PATH > default."""

    def test_from_vanilla_path_env(self, env_vanilla_path):
        """GLYPHS_VANILLA_PATH env var takes precedence."""
        result = _vanilla_utils.get_vanilla_path()
        assert result == env_vanilla_path
        assert result.is_dir()

    def test_from_repositories_path_env(self, vanilla_path, monkeypatch):
        """GLYPHS_REPOSITORIES_PATH + vanilla/Lib/vanilla as fallback."""
        monkeypatch.delenv("GLYPHS_VANILLA_PATH", raising=False)
        repos_path = vanilla_path.parent.parent.parent
        monkeypatch.setenv("GLYPHS_REPOSITORIES_PATH", str(repos_path))
        result = _vanilla_utils.get_vanilla_path()
        assert result == vanilla_path

    def test_default_path_fallback(self, vanilla_path, monkeypatch):
        """Falls back to default Glyphs 3 path."""
        monkeypatch.delenv("GLYPHS_VANILLA_PATH", raising=False)
        monkeypatch.delenv("GLYPHS_REPOSITORIES_PATH", raising=False)
        result = _vanilla_utils.get_vanilla_path()
        assert result == vanilla_path

    def test_not_found_raises(self, monkeypatch):
        """Raises FileNotFoundError when no path exists."""
        monkeypatch.setenv("GLYPHS_VANILLA_PATH", "/nonexistent/vanilla")
        with pytest.raises(FileNotFoundError, match="Vanilla"):
            _vanilla_utils.get_vanilla_path()

    def test_returns_path_object(self, env_vanilla_path):
        """Returns a Path object, not a string."""
        result = _vanilla_utils.get_vanilla_path()
        assert isinstance(result, Path)


class TestParseInitImports:
    """Test __init__.py import parsing."""

    def test_parse_simple_imports(self, sample_init_py):
        """Parses simple 'from vanilla.module import Class' lines."""
        result = _vanilla_utils.parse_init_imports(sample_init_py)
        assert result["Button"] == "vanillaButton"
        assert result["TextEditor"] == "vanillaTextEditor"

    def test_parse_multiline_imports(self, sample_init_py):
        """Parses multiline 'from vanilla.module import (\\n    Class1,\\n    Class2,\\n)' blocks."""
        result = _vanilla_utils.parse_init_imports(sample_init_py)
        assert result["List2"] == "vanillaList2"
        assert result["List2DataSource"] == "vanillaList2"
        assert result["List2GroupRow"] == "vanillaList2"
        assert result["Window"] == "vanillaWindows"
        assert result["FloatingWindow"] == "vanillaWindows"

    def test_returns_correct_count(self, sample_init_py):
        """Mock __init__.py has exactly 7 classes."""
        result = _vanilla_utils.parse_init_imports(sample_init_py)
        assert len(result) == 7

    def test_real_init_has_many_classes(self, init_py_path):
        """Integration: real __init__.py has 70+ classes."""
        result = _vanilla_utils.parse_init_imports(init_py_path)
        assert len(result) >= 70


class TestExtractClassSource:
    """Test extracting a single class from a multi-class source file."""

    def test_extract_existing_class(self, sample_source_file):
        """Extracts the correct class with source, docstring, and methods."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "Window")
        assert result is not None
        assert result["class_name"] == "Window"
        assert result["bases"] == ["BaseWindow"]
        assert "A standard window." in result["docstring"]

    def test_extract_methods(self, sample_source_file):
        """Extracted methods include name and params."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "Window")
        method_names = [m["name"] for m in result["methods"]]
        assert "__init__" in method_names
        assert "open" in method_names
        assert "close" in method_names

    def test_method_params(self, sample_source_file):
        """Methods include parameter information."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "Window")
        init_method = next(m for m in result["methods"] if m["name"] == "__init__")
        assert "posSize" in init_method["params"]

    def test_extract_second_class(self, sample_source_file):
        """Can extract a class that isn't the first in the file."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "FloatingWindow")
        assert result is not None
        assert result["class_name"] == "FloatingWindow"
        assert result["bases"] == ["BaseWindow"]

    def test_not_found_returns_none(self, sample_source_file):
        """Returns None for a class that doesn't exist."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "NonExistent")
        assert result is None

    def test_source_included(self, sample_source_file):
        """Extracted result includes source code."""
        result = _vanilla_utils.extract_class_source(sample_source_file, "Window")
        assert "source" in result
        assert "class Window" in result["source"]
        assert "class FloatingWindow" not in result["source"]


class TestOutputJson:
    """Test JSON output helper."""

    def test_outputs_valid_json(self, capsys):
        data = {"key": "value", "count": 42}
        _vanilla_utils.output_json(data)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_ensure_ascii_false(self, capsys):
        data = {"name": "中文測試"}
        _vanilla_utils.output_json(data)
        captured = capsys.readouterr()
        assert "中文測試" in captured.out


class TestOutputError:
    """Test error output helper."""

    def test_outputs_error_json(self, capsys):
        with pytest.raises(SystemExit):
            _vanilla_utils.output_error("something went wrong")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["error"] == "something went wrong"

    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            _vanilla_utils.output_error("fail")
        assert exc_info.value.code == 1
