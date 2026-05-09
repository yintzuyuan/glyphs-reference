"""Tests for search_methods.py — AST parsing of plugins.py."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import search_methods

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# Known plugin base classes in plugins.py
EXPECTED_CLASSES = {
    "FileFormatPlugin",
    "FilterWithDialog",
    "FilterWithoutDialog",
    "GeneralPlugin",
    "PalettePlugin",
    "ReporterPlugin",
    "SelectTool",
}


class TestParsePluginClasses:
    """Test AST extraction of plugin base classes."""

    def test_finds_all_seven_classes(self, env_sdk_path):
        result = search_methods.parse_plugin_classes()
        class_names = {c["name"] for c in result}
        assert class_names == EXPECTED_CLASSES

    def test_class_has_required_fields(self, env_sdk_path):
        result = search_methods.parse_plugin_classes()
        for cls in result:
            assert "name" in cls
            assert "base_class" in cls
            assert "methods" in cls
            assert "line" in cls
            assert isinstance(cls["methods"], list)

    def test_class_base_classes(self, env_sdk_path):
        result = search_methods.parse_plugin_classes()
        by_name = {c["name"]: c for c in result}
        assert by_name["ReporterPlugin"]["base_class"] == "BaseReporterPlugin"
        assert by_name["SelectTool"]["base_class"] == "GSToolSelect"
        assert by_name["FileFormatPlugin"]["base_class"] == "BaseFileFormatPlugin"


class TestMethodClassification:
    """Test method type classification: protocol, python_helper, python_wrapped."""

    def test_protocol_method_has_underscore_suffix(self, env_sdk_path):
        """ObjC selector methods (name ending with _) are classified as protocol."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        foreground = next(
            m for m in reporter["methods"]
            if m["name"] == "drawForegroundForLayer_options_"
        )
        assert foreground["type"] == "protocol"

    def test_python_method_decorator(self, env_sdk_path):
        """Methods with @objc.python_method are python_helper."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        draw_text = next(
            m for m in reporter["methods"]
            if m["name"] == "drawTextAtPoint"
        )
        assert draw_text["type"] == "python_helper"

    def test_regular_method_is_python_wrapped(self, env_sdk_path):
        """Regular methods (no _ suffix, no python_method) are python_wrapped."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        title = next(m for m in reporter["methods"] if m["name"] == "title")
        assert title["type"] == "python_wrapped"

    def test_injected_methods_included(self, env_sdk_path):
        """Methods assigned outside class body (ClassName.method = python_method(...))."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        method_names = {m["name"] for m in reporter["methods"]}
        assert "logToConsole" in method_names
        assert "logError" in method_names
        assert "loadNib" in method_names

    def test_injected_methods_are_python_helper(self, env_sdk_path):
        """Injected python_method() assignments are python_helper type."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        log = next(m for m in reporter["methods"] if m["name"] == "logToConsole")
        assert log["type"] == "python_helper"


class TestMethodInfo:
    """Test method detail extraction."""

    def test_method_has_required_fields(self, env_sdk_path):
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        for method in reporter["methods"]:
            assert "name" in method
            assert "type" in method
            assert "line" in method

    def test_method_has_docstring(self, env_sdk_path):
        """Methods with docstrings should include them."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        foreground = next(
            m for m in reporter["methods"]
            if m["name"] == "drawForegroundForLayer_options_"
        )
        assert foreground.get("docstring")
        assert "FRONT OF" in foreground["docstring"]

    def test_method_has_args(self, env_sdk_path):
        """Methods should list their arguments."""
        result = search_methods.parse_plugin_classes()
        reporter = next(c for c in result if c["name"] == "ReporterPlugin")
        foreground = next(
            m for m in reporter["methods"]
            if m["name"] == "drawForegroundForLayer_options_"
        )
        assert "args" in foreground
        assert "layer" in foreground["args"]
        assert "options" in foreground["args"]


class TestSearchMethods:
    """Test method search functionality."""

    def test_search_by_name_substring(self, env_sdk_path):
        results = search_methods.search_methods("foreground")
        assert len(results) > 0
        for r in results:
            assert "foreground" in r["name"].lower()

    def test_search_case_insensitive(self, env_sdk_path):
        results = search_methods.search_methods("Foreground")
        assert len(results) > 0

    def test_search_returns_class_context(self, env_sdk_path):
        results = search_methods.search_methods("drawForeground")
        assert len(results) > 0
        assert any(r["class"] == "ReporterPlugin" for r in results)

    def test_search_no_results(self, env_sdk_path):
        results = search_methods.search_methods("xyznonexistent")
        assert results == []


class TestIdentifyMethod:
    """Test single method identification."""

    def test_identify_exact_method(self, env_sdk_path):
        result = search_methods.identify_method("drawForegroundForLayer_options_")
        assert result is not None
        assert result["name"] == "drawForegroundForLayer_options_"
        assert result["class"] == "ReporterPlugin"
        assert result["type"] == "protocol"

    def test_identify_nonexistent(self, env_sdk_path):
        result = search_methods.identify_method("nonexistentMethod")
        assert result is None


class TestFilterByPlugin:
    """Test filtering by plugin type."""

    def test_filter_reporter(self, env_sdk_path):
        result = search_methods.get_plugin_methods("reporter")
        assert result is not None
        assert result["name"] == "ReporterPlugin"
        assert len(result["methods"]) > 0

    def test_filter_case_insensitive(self, env_sdk_path):
        result = search_methods.get_plugin_methods("Reporter")
        assert result is not None
        assert result["name"] == "ReporterPlugin"

    def test_filter_partial_match(self, env_sdk_path):
        """'filter' matches FilterWithDialog or FilterWithoutDialog."""
        result = search_methods.get_plugin_methods("filter")
        # Should match one of the filter classes
        assert result is not None
        assert "Filter" in result["name"]

    def test_filter_nonexistent(self, env_sdk_path):
        result = search_methods.get_plugin_methods("nonexistent")
        assert result is None


class TestCLI:
    """Test CLI integration."""

    def test_cli_list_all(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_methods.py")],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 7

    def test_cli_plugin_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_methods.py"), "--plugin", "reporter"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "ReporterPlugin"

    def test_cli_search_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_methods.py"), "--search", "foreground"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) > 0

    def test_cli_method_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_methods.py"),
             "--method", "drawForegroundForLayer_options_"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "drawForegroundForLayer_options_"
