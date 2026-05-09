"""Tests for _lighttable_utils.py — Light Table path resolution and JSON output."""

import json
import sys
from pathlib import Path

import pytest

_utils = sys.modules["_lighttable_utils"]


class TestGetLightTablePath:
    """Test Light Table path resolution: env var > default path."""

    def test_env_var_overrides_default(self, tmp_path, monkeypatch):
        """GLYPHS_LIGHT_TABLE_PATH env var takes precedence."""
        lt_dir = tmp_path / "Light-Table"
        lt_dir.mkdir()
        monkeypatch.setenv("GLYPHS_LIGHT_TABLE_PATH", str(lt_dir))
        result = _utils.get_lighttable_path()
        assert result == lt_dir

    def test_env_var_nonexistent_raises(self, monkeypatch):
        """Non-existent env var path raises FileNotFoundError."""
        monkeypatch.setenv("GLYPHS_LIGHT_TABLE_PATH", "/nonexistent/path")
        with pytest.raises(FileNotFoundError):
            _utils.get_lighttable_path()

    def test_default_path_fallback(self, lt_path, monkeypatch):
        """Falls back to default path when env var not set."""
        monkeypatch.delenv("GLYPHS_LIGHT_TABLE_PATH", raising=False)
        result = _utils.get_lighttable_path()
        assert result == lt_path

    def test_missing_path_raises(self, monkeypatch):
        """Raises FileNotFoundError when no path is available."""
        monkeypatch.delenv("GLYPHS_LIGHT_TABLE_PATH", raising=False)
        monkeypatch.setattr(_utils, "_DEFAULT_LT_PATH", Path("/nonexistent"))
        with pytest.raises(FileNotFoundError):
            _utils.get_lighttable_path()

    def test_returns_path_object(self, tmp_path, monkeypatch):
        """Returns a Path object, not a string."""
        lt_dir = tmp_path / "Light-Table"
        lt_dir.mkdir()
        monkeypatch.setenv("GLYPHS_LIGHT_TABLE_PATH", str(lt_dir))
        result = _utils.get_lighttable_path()
        assert isinstance(result, Path)


class TestGetApiSourcePath:
    """Test API source path derivation."""

    def test_derives_init_py_path(self, tmp_path, monkeypatch):
        """Derives __init__.py path from Light Table root."""
        lt_dir = tmp_path / "Light-Table"
        api_file = lt_dir / "Python API" / "lighttable" / "__init__.py"
        api_file.parent.mkdir(parents=True)
        api_file.write_text("# mock")
        monkeypatch.setenv("GLYPHS_LIGHT_TABLE_PATH", str(lt_dir))
        result = _utils.get_api_source_path()
        assert result == api_file
        assert result.name == "__init__.py"


class TestOutputJson:
    """Test JSON output helper."""

    def test_outputs_valid_json(self, capsys):
        data = {"key": "value"}
        _utils.output_json(data)
        captured = capsys.readouterr()
        assert json.loads(captured.out) == data

    def test_ensure_ascii_false(self, capsys):
        data = {"name": "中文測試"}
        _utils.output_json(data)
        captured = capsys.readouterr()
        assert "中文測試" in captured.out


class TestOutputError:
    """Test error output helper."""

    def test_outputs_error_json(self, capsys):
        with pytest.raises(SystemExit):
            _utils.output_error("something went wrong")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["error"] == "something went wrong"

    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            _utils.output_error("fail")
        assert exc_info.value.code == 1
