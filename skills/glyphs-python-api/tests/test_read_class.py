"""Tests for read_class.py — read class/member/function details CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import read_class

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestReadClass:
    """Test reading full class details."""

    def test_read_gsfont(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_class_info("GSFont", sphinx_rst_path)
        assert result["name"] == "GSFont"
        assert len(result["properties"]) > 20
        assert len(result["methods"]) > 5

    def test_read_class_has_description(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_class_info("GSFont", sphinx_rst_path)
        assert result["description"]

    def test_read_nonexistent_class_returns_none(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_class_info("NonExistent", sphinx_rst_path)
        assert result is None

    def test_case_insensitive_lookup(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_class_info("gsfont", sphinx_rst_path)
        assert result is not None
        assert result["name"] == "GSFont"


class TestReadMember:
    """Test reading a specific member."""

    def test_read_property(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_member("GSFont", "masters", sphinx_rst_path)
        assert result is not None
        assert result["name"] == "masters"
        assert result["description"]

    def test_read_method(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_member("GSFont", "save", sphinx_rst_path)
        assert result is not None
        assert result["name"] == "save"

    def test_read_nonexistent_member(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_member("GSFont", "nonexistent", sphinx_rst_path)
        assert result is None


class TestReadSummary:
    """Test summary mode (names only)."""

    def test_summary_gsfont(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_class_summary("GSFont", sphinx_rst_path)
        assert "properties" in result
        assert "methods" in result
        assert isinstance(result["properties"], list)
        assert all(isinstance(p, str) for p in result["properties"])


class TestReadRelationships:
    """Test cross-reference relationships."""

    def test_gsfont_relationships(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_relationships("GSFont", sphinx_rst_path)
        assert "references" in result
        assert "referenced_by" in result
        assert "GSFontMaster" in result["references"]

    def test_referenced_by_includes_reverse(self, sphinx_rst_path, env_sdk_path):
        """GSFontMaster should be referenced_by GSFont."""
        result = read_class.read_relationships("GSFontMaster", sphinx_rst_path)
        assert "GSFont" in result["referenced_by"]


class TestReadFunction:
    """Test reading standalone function details."""

    def test_read_dividecurve(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_function("divideCurve", sphinx_rst_path)
        assert result is not None
        assert result["name"] == "divideCurve"
        assert result["params"]

    def test_read_nonexistent_function(self, sphinx_rst_path, env_sdk_path):
        result = read_class.read_function("nonexistent", sphinx_rst_path)
        assert result is None


class TestCLI:
    """Test CLI integration."""

    def test_read_class_cli(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_class.py"), "GSFont"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "GSFont"

    def test_member_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_class.py"), "GSFont", "--member", "masters"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "masters"

    def test_summary_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_class.py"), "GSFont", "--summary"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "properties" in data

    def test_relationships_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_class.py"), "GSFont", "--relationships"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "references" in data

    def test_function_flag(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_class.py"), "--function", "divideCurve"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "divideCurve"
