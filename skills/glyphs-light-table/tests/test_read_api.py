"""Tests for read_api.py — Light Table API parser."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_read_api = sys.modules["read_api"]

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestParseEnums:
    """Test enum parsing from API source."""

    def test_finds_all_enums(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        enum_names = [e["name"] for e in parsed["enums"]]
        assert "DocumentState" in enum_names
        assert "ObjectStatus" in enum_names

    def test_enum_members(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        doc_state = next(e for e in parsed["enums"] if e["name"] == "DocumentState")
        member_names = [m["name"] for m in doc_state["members"]]
        assert "UNKNOWN" in member_names
        assert "NO_FILE" in member_names
        assert "OPERATIONAL" in member_names

    def test_enum_member_values(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        doc_state = next(e for e in parsed["enums"] if e["name"] == "DocumentState")
        values = {m["name"]: m["value"] for m in doc_state["members"]}
        assert values["UNKNOWN"] == 0
        assert values["OPERATIONAL"] == 4


class TestParseObjcClasses:
    """Test ObjC class binding detection."""

    def test_finds_public_classes(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        class_names = [c["python_name"] for c in parsed["objc_classes"]]
        assert "Signature" in class_names
        assert "Commit" in class_names

    def test_skips_private_classes(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        class_names = [c["python_name"] for c in parsed["objc_classes"]]
        assert "_LightTableInterface" not in class_names

    def test_objc_class_name(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        sig = next(c for c in parsed["objc_classes"] if c["python_name"] == "Signature")
        assert sig["objc_class"] == "LightTableSignature"


class TestParseGsExtensions:
    """Test GSFont/GSGlyph/GSLayer extension parsing."""

    def test_gs_font_extensions(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        font_exts = parsed["gs_extensions"]["GSFont"]
        ext_names = [e["name"] for e in font_exts]
        assert "lt_document_state" in ext_names
        assert "lt_load_version" in ext_names

    def test_gs_glyph_extensions(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        glyph_exts = parsed["gs_extensions"]["GSGlyph"]
        ext_names = [e["name"] for e in glyph_exts]
        assert "lt_status" in ext_names

    def test_gs_layer_extensions(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        layer_exts = parsed["gs_extensions"]["GSLayer"]
        ext_names = [e["name"] for e in layer_exts]
        assert "lt_status" in ext_names

    def test_property_vs_method(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        font_exts = {e["name"]: e for e in parsed["gs_extensions"]["GSFont"]}
        assert font_exts["lt_document_state"]["kind"] == "property"
        assert font_exts["lt_load_version"]["kind"] == "method"

    def test_objc_selector_extraction(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        font_exts = {e["name"]: e for e in parsed["gs_extensions"]["GSFont"]}
        assert font_exts["lt_document_state"]["objc_selector"] == "documentStateOfFont_"
        assert (
            font_exts["lt_load_version"]["objc_selector"]
            == "font_loadVersionForRecord_completionHandler_"
        )


class TestParseObjcClassExtensions:
    """Test property/method extensions on ObjC bridge classes."""

    def test_signature_extensions(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        sig_exts = parsed["objc_class_extensions"]["Signature"]
        ext_names = [e["name"] for e in sig_exts]
        assert "name" in ext_names
        assert "email_address" in ext_names

    def test_commit_extensions(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        commit_exts = parsed["objc_class_extensions"]["Commit"]
        ext_names = [e["name"] for e in commit_exts]
        assert "id" in ext_names
        assert "summary" in ext_names

    def test_pyobjc_accessor(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        sig_exts = {e["name"]: e for e in parsed["objc_class_extensions"]["Signature"]}
        assert sig_exts["name"]["objc_accessor"] == "name"
        assert sig_exts["email_address"]["objc_accessor"] == "emailAddress"


class TestParseDataclasses:
    """Test dataclass parsing."""

    def test_finds_dataclass(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        dc_names = [d["name"] for d in parsed["dataclasses"]]
        assert "ComponentIntegrationPlan" in dc_names

    def test_dataclass_fields(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        plan = next(
            d for d in parsed["dataclasses"] if d["name"] == "ComponentIntegrationPlan"
        )
        assert "strategies" in plan["fields"]
        assert "fallback" in plan["fields"]


class TestDetailMode:
    """Test detail() for specific type lookup."""

    def test_detail_enum(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.detail(parsed, "DocumentState")
        assert result["type"] == "enum"
        assert result["name"] == "DocumentState"
        assert len(result["members"]) > 0

    def test_detail_gs_class(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.detail(parsed, "GSFont")
        assert result["type"] == "gs_extensions"
        assert result["class"] == "GSFont"
        assert len(result["extensions"]) > 0

    def test_detail_objc_class(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.detail(parsed, "Signature")
        assert result["type"] == "objc_class"
        assert result["python_name"] == "Signature"
        assert result["objc_class"] == "LightTableSignature"
        assert len(result["extensions"]) > 0

    def test_detail_dataclass(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.detail(parsed, "ComponentIntegrationPlan")
        assert result["type"] == "dataclass"
        assert result["name"] == "ComponentIntegrationPlan"

    def test_detail_not_found(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.detail(parsed, "NonexistentType")
        assert result is None


class TestSearchMode:
    """Test search() for cross-type searching."""

    def test_search_finds_enum(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.search(parsed, "ObjectStatus")
        types = [r["type"] for r in result["results"]]
        assert "enum" in types

    def test_search_finds_extension(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.search(parsed, "lt_status")
        assert len(result["results"]) >= 2  # GSGlyph + GSLayer

    def test_search_case_insensitive(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.search(parsed, "document")
        assert len(result["results"]) > 0

    def test_search_no_results(self, mock_api_source):
        source = mock_api_source.read_text()
        parsed = _read_api.parse_api(source)
        result = _read_api.search(parsed, "zzz_nonexistent_zzz")
        assert len(result["results"]) == 0


class TestCLI:
    """Test CLI via subprocess."""

    def _run_cli(self, *args, lt_path=None):
        cmd = [sys.executable, str(SCRIPTS_DIR / "read_api.py")]
        cmd.extend(args)
        env = {**os.environ}
        if lt_path:
            env["GLYPHS_LIGHT_TABLE_PATH"] = str(lt_path)
        return subprocess.run(cmd, capture_output=True, text=True, env=env)

    def test_list_mode(self, mock_lt_dir):
        result = self._run_cli(lt_path=mock_lt_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "enums" in data
        assert "objc_classes" in data

    def test_detail_mode(self, mock_lt_dir):
        result = self._run_cli("DocumentState", lt_path=mock_lt_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "DocumentState"

    def test_search_mode(self, mock_lt_dir):
        result = self._run_cli("--search", "status", lt_path=mock_lt_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "results" in data

    def test_not_found_exits_error(self, mock_lt_dir):
        result = self._run_cli("NonexistentType", lt_path=mock_lt_dir)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data
