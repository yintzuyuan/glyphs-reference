"""Tests for _format_utils module."""

import json

import pytest

import _format_utils


class TestGetSdkPath:
    """Test get_sdk_path() resolution."""

    def test_env_var_takes_priority(self, env_sdk_path):
        result = _format_utils.get_sdk_path()
        assert result == env_sdk_path

    def test_env_var_nonexistent_raises(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GLYPHS_SDK_PATH", str(tmp_path / "nonexistent"))
        with pytest.raises(FileNotFoundError, match="GlyphsSDK not found"):
            _format_utils.get_sdk_path()

    def test_relative_path_fallback(self, sdk_path, monkeypatch):
        monkeypatch.delenv("GLYPHS_SDK_PATH", raising=False)
        result = _format_utils.get_sdk_path()
        assert result.is_dir()

    def test_no_sdk_raises(self, monkeypatch, tmp_path):
        monkeypatch.delenv("GLYPHS_SDK_PATH", raising=False)
        monkeypatch.setattr(
            _format_utils, "_RELATIVE_SDK_PATH", tmp_path / "nonexistent"
        )
        with pytest.raises(FileNotFoundError, match="GlyphsSDK not found"):
            _format_utils.get_sdk_path()


class TestGetFileFormatPath:
    """Test get_file_format_path()."""

    def test_returns_correct_path(self, env_sdk_path):
        result = _format_utils.get_file_format_path()
        assert result == env_sdk_path / "GlyphsFileFormat"

    def test_directory_exists(self, env_sdk_path):
        result = _format_utils.get_file_format_path()
        assert result.is_dir()


class TestGetSpecPath:
    """Test get_spec_path()."""

    def test_v3_path(self, env_sdk_path):
        result = _format_utils.get_spec_path(3)
        assert result.name == "GlyphsFileFormatv3.md"

    def test_v2_path(self, env_sdk_path):
        result = _format_utils.get_spec_path(2)
        assert result.name == "GlyphsFileFormatv2.md"

    def test_v3_exists(self, env_sdk_path):
        result = _format_utils.get_spec_path(3)
        assert result.exists()


class TestGetSchemaPath:
    """Test get_schema_path()."""

    def test_glyphs_3_schema(self, env_sdk_path):
        result = _format_utils.get_schema_path("glyphs-3")
        assert result.name == "glyphs-3.schema.json"

    def test_fontinfo_3_schema(self, env_sdk_path):
        result = _format_utils.get_schema_path("fontinfo-3")
        assert result.name == "fontinfo-3.schema.json"

    def test_schema_exists(self, env_sdk_path):
        result = _format_utils.get_schema_path("glyphs-3")
        assert result.exists()


class TestExtractDefinition:
    """Test extract_definition() from spec markdown."""

    def test_extract_first_definition(self, sample_spec_v3):
        result = _format_utils.extract_definition(sample_spec_v3, "anchor", version=3)
        assert result is not None
        assert "anchor" in result
        assert "GSAnchor" in result
        assert "The name of the anchor" in result

    def test_extract_middle_definition(self, sample_spec_v3):
        result = _format_utils.extract_definition(sample_spec_v3, "axis", version=3)
        assert result is not None
        assert "GSAxis" in result
        assert "OpenType tag" in result

    def test_extract_last_definition(self, sample_spec_v3):
        result = _format_utils.extract_definition(sample_spec_v3, "glyph", version=3)
        assert result is not None
        assert "GSGlyph" in result
        assert "glyphname" in result

    def test_not_found_returns_none(self, sample_spec_v3):
        result = _format_utils.extract_definition(
            sample_spec_v3, "nonexistent", version=3
        )
        assert result is None

    def test_v2_extraction(self, sample_spec_v2):
        result = _format_utils.extract_definition(sample_spec_v2, "anchor", version=2)
        assert result is not None
        assert "GSAnchor" in result

    def test_v2_not_found(self, sample_spec_v2):
        result = _format_utils.extract_definition(
            sample_spec_v2, "axis", version=2
        )
        assert result is None

    def test_includes_sub_properties(self, sample_spec_v3):
        result = _format_utils.extract_definition(sample_spec_v3, "anchor", version=3)
        assert "pos" in result

    def test_does_not_include_next_definition(self, sample_spec_v3):
        result = _format_utils.extract_definition(sample_spec_v3, "anchor", version=3)
        assert "GSAxis" not in result


class TestListDefinitions:
    """Test list_definitions() from spec markdown."""

    def test_list_v3_definitions(self, sample_spec_v3):
        result = _format_utils.list_definitions(sample_spec_v3, version=3)
        assert len(result) == 3
        names = [d["name"] for d in result]
        assert names == ["anchor", "axis", "glyph"]

    def test_list_v2_definitions(self, sample_spec_v2):
        result = _format_utils.list_definitions(sample_spec_v2, version=2)
        assert len(result) == 2
        names = [d["name"] for d in result]
        assert names == ["anchor", "glyph"]

    def test_includes_gs_class(self, sample_spec_v3):
        result = _format_utils.list_definitions(sample_spec_v3, version=3)
        anchor = next(d for d in result if d["name"] == "anchor")
        assert anchor["gs_class"] == "GSAnchor"

    def test_gs_class_none_when_absent(self, sample_spec_v3):
        spec = """\
## Definitions

- <a name="spec-glyphs-3-attr"></a><code><strong>attr</strong>: object</code>

## Changes
"""
        result = _format_utils.list_definitions(spec, version=3)
        assert len(result) == 1
        assert result[0]["gs_class"] is None

    def test_real_v3_spec(self, spec_v3_path):
        text = spec_v3_path.read_text()
        result = _format_utils.list_definitions(text, version=3)
        assert len(result) > 20
        names = [d["name"] for d in result]
        assert "anchor" in names
        assert "glyph" in names
        assert "layer" in names


class TestExtractSchemaDef:
    """Test extract_schema_def() from JSON Schema."""

    def test_extract_existing(self, sample_schema_v3):
        result = _format_utils.extract_schema_def(sample_schema_v3, "anchor")
        assert result is not None
        assert result["type"] == "object"
        assert "name" in result["properties"]

    def test_extract_nonexistent(self, sample_schema_v3):
        result = _format_utils.extract_schema_def(sample_schema_v3, "nonexistent")
        assert result is None

    def test_no_defs_key(self):
        result = _format_utils.extract_schema_def({"type": "object"}, "anchor")
        assert result is None


class TestListSchemaDefs:
    """Test list_schema_defs() from JSON Schema."""

    def test_list_all_defs(self, sample_schema_v3):
        result = _format_utils.list_schema_defs(sample_schema_v3)
        assert result == ["anchor", "axis", "glyph"]

    def test_no_defs_key(self):
        result = _format_utils.list_schema_defs({"type": "object"})
        assert result == []

    def test_real_schema(self, schema_v3_path):
        data = json.loads(schema_v3_path.read_text())
        result = _format_utils.list_schema_defs(data)
        assert len(result) > 20
        assert "anchor" in result
        assert "glyph" in result


class TestOutputHelpers:
    """Test output_json() and output_error()."""

    def test_output_json(self, capsys):
        _format_utils.output_json({"key": "value"})
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data == {"key": "value"}

    def test_output_error(self, capsys):
        with pytest.raises(SystemExit, match="1"):
            _format_utils.output_error("something went wrong")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["error"] == "something went wrong"
