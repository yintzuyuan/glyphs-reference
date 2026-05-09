"""Tests for search_registry.py — CLI for searching the official Glyphs registry."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import search_registry
import _registry_utils

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestSearchRegistryFunctions:
    """Test search_registry functions with mock data (no HTTP)."""

    def test_search_returns_matching_packages(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.run_search(packages, query="anchor")
        assert len(results) >= 2
        titles = [r["title"] for r in results]
        assert "Show Anchors" in titles

    def test_filter_by_category(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages, category="plugins")
        assert all(r["category"] == "plugins" for r in results)
        assert len(results) == 5

    def test_filter_by_category_scripts(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages, category="scripts")
        assert all(r["category"] == "scripts" for r in results)
        assert len(results) == 2

    def test_filter_by_category_modules(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages, category="modules")
        assert len(results) == 1

    def test_filter_by_type(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages, plugin_type="Reporter")
        assert all(r.get("type") == "Reporter" for r in results)
        assert len(results) == 2

    def test_filter_by_type_case_insensitive(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages, plugin_type="reporter")
        assert len(results) == 2

    def test_combined_search_and_category(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        filtered = search_registry.filter_packages(packages, category="plugins")
        results = search_registry.run_search(filtered, query="anchor")
        assert len(results) == 1  # Only "Show Anchors" in plugins
        assert results[0]["title"] == "Show Anchors"

    def test_combined_category_and_type(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(
            packages, category="plugins", plugin_type="Filter"
        )
        assert len(results) == 1
        assert results[0]["title"] == "RoundCorner"

    def test_all_returns_everything(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.filter_packages(packages)
        assert len(results) == 8

    def test_search_empty_result(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = search_registry.run_search(packages, query="nonexistent_xyz")
        assert results == []


class TestCLI:
    """Test CLI via subprocess with mocked registry data."""

    def _run_cli(self, *args, registry_data=None):
        """Helper to run search_registry.py with mock data injected via env."""
        cmd = [sys.executable, str(SCRIPTS_DIR / "search_registry.py")]
        cmd.extend(args)

        env_patch = {}
        if registry_data is not None:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(registry_data, f)
                env_patch["_REGISTRY_TEST_FILE"] = f.name

            env = {**os.environ, **env_patch}
        else:
            env = None

        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        # Clean up temp file
        if "_REGISTRY_TEST_FILE" in env_patch:
            Path(env_patch["_REGISTRY_TEST_FILE"]).unlink(missing_ok=True)

        return result

    def test_no_args_shows_help(self):
        result = self._run_cli()
        assert result.returncode != 0

    def test_search_flag(self, sample_registry_json):
        result = self._run_cli(
            "--search", "anchor", registry_data=sample_registry_json
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) >= 2

    def test_all_flag(self, sample_registry_json):
        result = self._run_cli("--all", registry_data=sample_registry_json)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 8

    def test_category_filter(self, sample_registry_json):
        result = self._run_cli(
            "--all", "--category", "plugins", registry_data=sample_registry_json
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert all(d["category"] == "plugins" for d in data)

    def test_type_filter(self, sample_registry_json):
        result = self._run_cli(
            "--all", "--type", "Reporter", registry_data=sample_registry_json
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert all(d.get("type") == "Reporter" for d in data)

    def test_combined_search_and_filters(self, sample_registry_json):
        result = self._run_cli(
            "--search", "anchor",
            "--category", "plugins",
            registry_data=sample_registry_json,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["title"] == "Show Anchors"
