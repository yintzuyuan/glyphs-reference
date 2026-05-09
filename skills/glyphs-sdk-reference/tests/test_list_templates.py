"""Tests for list_templates.py — scan Templates + Samples directories."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import list_templates

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestListAllEntries:
    """Test listing all templates and samples."""

    def test_returns_list(self, env_sdk_path):
        result = list_templates.list_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_has_templates_and_samples(self, env_sdk_path):
        result = list_templates.list_all()
        types = {e["type"] for e in result}
        assert "template" in types
        assert "sample" in types

    def test_nine_templates(self, env_sdk_path):
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        assert len(templates) == 9

    def test_six_samples(self, env_sdk_path):
        result = list_templates.list_all()
        samples = [e for e in result if e["type"] == "sample"]
        assert len(samples) == 6


class TestEntryFields:
    """Test that each entry has required fields."""

    def test_template_required_fields(self, env_sdk_path):
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        for t in templates:
            assert "name" in t
            assert "type" in t
            assert "plugin_type" in t
            assert "path" in t

    def test_sample_required_fields(self, env_sdk_path):
        result = list_templates.list_all()
        samples = [e for e in result if e["type"] == "sample"]
        for s in samples:
            assert "name" in s
            assert "type" in s
            assert "path" in s


class TestTemplateDetails:
    """Test template-specific information."""

    def test_reporter_template(self, env_sdk_path):
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        reporter = [t for t in templates if "reporter" in t["plugin_type"].lower()]
        assert len(reporter) == 1
        assert reporter[0]["name"] == "Reporter"

    def test_filter_variants(self, env_sdk_path):
        """Filter has two variants: with xib dialog and without dialog."""
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        filters = [t for t in templates if "filter" in t["plugin_type"].lower()]
        assert len(filters) == 2

    def test_file_format_variants(self, env_sdk_path):
        """File Format has two variants: vanilla and xib dialog."""
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        file_formats = [t for t in templates if "fileformat" in t["plugin_type"].lower()]
        assert len(file_formats) == 2

    def test_template_has_variant_info(self, env_sdk_path):
        """Templates with variants include variant field."""
        result = list_templates.list_all()
        templates = [e for e in result if e["type"] == "template"]
        filters = [t for t in templates if "filter" in t["plugin_type"].lower()]
        variants = {t.get("variant", "") for t in filters}
        assert len(variants) == 2  # Two different variants


class TestSampleDetails:
    """Test sample-specific information."""

    def test_known_samples(self, env_sdk_path):
        result = list_templates.list_all()
        samples = [e for e in result if e["type"] == "sample"]
        names = {s["name"] for s in samples}
        assert "Smiley Panel Plugin" in names
        assert "MultipleTools" in names
        assert "Plugin With Window" in names
        assert "Callback for context menu" in names
        assert "Document exported" in names
        assert "Plugin Preferences" in names

    def test_bundle_samples_have_plugin_type(self, env_sdk_path):
        """Samples with plugin bundles should identify plugin type."""
        result = list_templates.list_all()
        samples = [e for e in result if e["type"] == "sample"]
        smiley = next(s for s in samples if s["name"] == "Smiley Panel Plugin")
        assert smiley.get("plugin_type")


class TestFilterByType:
    """Test filtering list by type."""

    def test_filter_templates_only(self, env_sdk_path):
        result = list_templates.list_by_type("template")
        assert all(e["type"] == "template" for e in result)
        assert len(result) == 9

    def test_filter_samples_only(self, env_sdk_path):
        result = list_templates.list_by_type("sample")
        assert all(e["type"] == "sample" for e in result)
        assert len(result) == 6


class TestCLI:
    """Test CLI integration."""

    def test_cli_list_all(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "list_templates.py")],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 15  # 9 templates + 6 samples

    def test_cli_type_template(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "list_templates.py"), "--type", "template"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 9

    def test_cli_type_sample(self, env_sdk_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "list_templates.py"), "--type", "sample"],
            capture_output=True, text=True,
            env={**dict(__import__("os").environ), "GLYPHS_SDK_PATH": str(env_sdk_path)},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 6
