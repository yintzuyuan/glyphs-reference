"""Tests for _sdk_utils.py — SDK path resolution and JSON output."""

import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "_sdk_utils",
    Path(__file__).parent.parent / "scripts" / "_sdk_utils.py",
)
_sdk_utils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sdk_utils)


class TestGetSdkPath:
    """Test SDK path resolution: env var > relative path."""

    def test_from_env_var(self, env_sdk_path):
        """GLYPHS_SDK_PATH env var takes precedence."""
        result = _sdk_utils.get_sdk_path()
        assert result == env_sdk_path
        assert result.is_dir()

    def test_from_relative_path(self, sdk_path, monkeypatch):
        """Falls back to relative path from scripts/ directory."""
        monkeypatch.delenv("GLYPHS_SDK_PATH", raising=False)
        result = _sdk_utils.get_sdk_path()
        assert result == sdk_path
        assert result.is_dir()

    def test_env_var_invalid_path_raises(self, monkeypatch):
        """Raises FileNotFoundError for invalid env var path."""
        monkeypatch.setenv("GLYPHS_SDK_PATH", "/nonexistent/path")
        with pytest.raises(FileNotFoundError, match="GlyphsSDK"):
            _sdk_utils.get_sdk_path()

    def test_returns_path_object(self, env_sdk_path):
        """Returns a Path object, not a string."""
        result = _sdk_utils.get_sdk_path()
        assert isinstance(result, Path)


class TestGetPluginsPyPath:
    """Test plugins.py path resolution."""

    def test_returns_existing_file(self, env_sdk_path):
        result = _sdk_utils.get_plugins_py_path()
        assert result.exists()
        assert result.name == "plugins.py"

    def test_path_under_sdk(self, env_sdk_path):
        result = _sdk_utils.get_plugins_py_path()
        expected = env_sdk_path / "ObjectWrapper" / "GlyphsApp" / "plugins.py"
        assert result == expected


class TestGetTemplatesPath:
    """Test Python Templates/ path resolution."""

    def test_returns_existing_dir(self, env_sdk_path):
        result = _sdk_utils.get_templates_path()
        assert result.exists()
        assert result.is_dir()
        assert result.name == "Python Templates"


class TestGetSamplesPath:
    """Test Python Samples/ path resolution."""

    def test_returns_existing_dir(self, env_sdk_path):
        result = _sdk_utils.get_samples_path()
        assert result.exists()
        assert result.is_dir()
        assert result.name == "Python Samples"


class TestGetDrawingToolsPath:
    """Test drawingTools.py path resolution."""

    def test_returns_existing_file(self, env_sdk_path):
        result = _sdk_utils.get_drawing_tools_path()
        assert result.exists()
        assert result.name == "drawingTools.py"


class TestOutputJson:
    """Test JSON output helper."""

    def test_outputs_valid_json(self, capsys):
        data = {"key": "value", "count": 42}
        _sdk_utils.output_json(data)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_outputs_with_indent(self, capsys):
        data = {"a": 1}
        _sdk_utils.output_json(data)
        captured = capsys.readouterr()
        assert "  " in captured.out  # indented

    def test_handles_list(self, capsys):
        data = [1, 2, 3]
        _sdk_utils.output_json(data)
        captured = capsys.readouterr()
        assert json.loads(captured.out) == [1, 2, 3]

    def test_ensure_ascii_false(self, capsys):
        data = {"name": "中文測試"}
        _sdk_utils.output_json(data)
        captured = capsys.readouterr()
        assert "中文測試" in captured.out


class TestOutputError:
    """Test error output helper."""

    def test_outputs_error_json(self, capsys):
        with pytest.raises(SystemExit):
            _sdk_utils.output_error("something went wrong")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["error"] == "something went wrong"

    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            _sdk_utils.output_error("fail")
        assert exc_info.value.code == 1
