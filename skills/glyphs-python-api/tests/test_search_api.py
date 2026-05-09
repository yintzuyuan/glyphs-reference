"""Tests for search_api.py — search/list classes, members, constants CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import search_api

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestListClasses:
    """Test listing all classes (default mode)."""

    def test_returns_35_classes(self, sphinx_rst_path, env_sdk_path):
        result = search_api.list_classes(sphinx_rst_path)
        assert len(result) == 35

    def test_class_entry_has_counts(self, sphinx_rst_path, env_sdk_path):
        result = search_api.list_classes(sphinx_rst_path)
        first = result[0]
        assert "name" in first
        assert "property_count" in first
        assert "method_count" in first

    def test_gsfont_has_many_properties(self, sphinx_rst_path, env_sdk_path):
        result = search_api.list_classes(sphinx_rst_path)
        gsfont = next(c for c in result if c["name"] == "GSFont")
        assert gsfont["property_count"] > 20


class TestSearch:
    """Test cross-type search."""

    def test_search_finds_classes(self, sphinx_rst_path, init_py_path, env_sdk_path):
        results = search_api.search("GSFont", sphinx_rst_path, init_py_path)
        class_results = [r for r in results if r["type"] == "class"]
        assert any(r["name"] == "GSFont" for r in class_results)

    def test_search_finds_properties(self, sphinx_rst_path, init_py_path, env_sdk_path):
        results = search_api.search("masters", sphinx_rst_path, init_py_path)
        prop_results = [r for r in results if r["type"] == "property"]
        assert len(prop_results) > 0

    def test_search_case_insensitive(self, sphinx_rst_path, init_py_path, env_sdk_path):
        results = search_api.search("gsfont", sphinx_rst_path, init_py_path)
        assert any(r["name"] == "GSFont" for r in results)

    def test_search_finds_constants(self, sphinx_rst_path, init_py_path, env_sdk_path):
        results = search_api.search("LINE", sphinx_rst_path, init_py_path)
        const_results = [r for r in results if r["type"] == "constant"]
        assert len(const_results) > 0

    def test_search_finds_standalone_functions(self, sphinx_rst_path, init_py_path, env_sdk_path):
        results = search_api.search("divideCurve", sphinx_rst_path, init_py_path)
        func_results = [r for r in results if r["type"] == "function"]
        assert any(r["name"] == "divideCurve" for r in func_results)


class TestListConstants:
    """Test listing all constants."""

    def test_returns_many_constants(self, sphinx_rst_path, init_py_path, env_sdk_path):
        result = search_api.list_constants(sphinx_rst_path, init_py_path)
        assert len(result) > 50

    def test_constant_has_value(self, sphinx_rst_path, init_py_path, env_sdk_path):
        result = search_api.list_constants(sphinx_rst_path, init_py_path)
        line_const = next(c for c in result if c["name"] == "LINE")
        assert line_const["value"]


class TestListFunctions:
    """Test listing standalone functions."""

    def test_returns_16_functions(self, sphinx_rst_path, env_sdk_path):
        result = search_api.list_functions(sphinx_rst_path)
        assert len(result) == 16

    def test_function_has_params(self, sphinx_rst_path, env_sdk_path):
        result = search_api.list_functions(sphinx_rst_path)
        divide = next(f for f in result if f["name"] == "divideCurve")
        assert divide["params"]


class TestCLI:
    """Test CLI integration via subprocess."""

    def test_default_lists_classes(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_api.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 35

    def test_search_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_api.py"), "--search", "layer"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) > 0

    def test_constants_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_api.py"), "--constants"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) > 50

    def test_functions_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_api.py"), "--functions"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 16
