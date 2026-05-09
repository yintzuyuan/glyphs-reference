"""Tests for _registry_utils.py — registry parsing and search utilities."""

import _registry_utils


class TestParseRegistry:
    """Test parse_registry() — extract packages from JSON data."""

    def test_parses_all_three_categories(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        categories = {p["category"] for p in result}
        assert categories == {"plugins", "scripts", "modules"}

    def test_total_count_matches(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        assert len(result) == 8  # 5 plugins + 2 scripts + 1 module

    def test_entry_has_required_fields(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        for entry in result:
            assert "title" in entry
            assert "url" in entry
            assert "category" in entry
            assert "description" in entry

    def test_extracts_title_from_titles_dict(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        titles = [p["title"] for p in result]
        assert "Show Anchors" in titles
        assert "mekkablue scripts" in titles

    def test_plugins_have_path_field(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        plugins = [p for p in result if p["category"] == "plugins"]
        for plugin in plugins:
            assert "path" in plugin

    def test_plugins_have_type_field(self, sample_registry_json):
        result = _registry_utils.parse_registry(sample_registry_json)
        plugins = [p for p in result if p["category"] == "plugins"]
        types = {p["type"] for p in plugins}
        assert "Reporter" in types
        assert "Filter" in types


class TestSearchPackages:
    """Test search_packages() — keyword search across packages."""

    def test_search_by_title(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = _registry_utils.search_packages(packages, "anchor")
        titles = [r["title"] for r in results]
        assert "Show Anchors" in titles
        assert "Anchor Mover" in titles

    def test_search_by_description(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = _registry_utils.search_packages(packages, "curvature")
        assert any(r["title"] == "SpeedPunk" for r in results)

    def test_search_by_url(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = _registry_utils.search_packages(packages, "mekkablue")
        assert len(results) >= 2  # ShowAnchors + RoundCorner + mekkablue scripts

    def test_search_case_insensitive(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results_lower = _registry_utils.search_packages(packages, "redarrow")
        results_upper = _registry_utils.search_packages(packages, "REDARROW")
        assert len(results_lower) == len(results_upper)
        assert len(results_lower) > 0

    def test_search_empty_result(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = _registry_utils.search_packages(packages, "nonexistent_xyz_123")
        assert results == []

    def test_search_empty_query_returns_all(self, sample_registry_json):
        packages = _registry_utils.parse_registry(sample_registry_json)
        results = _registry_utils.search_packages(packages, "")
        assert len(results) == len(packages)


class TestClassifyPluginType:
    """Test classify_plugin_type() — infer type from bundle extension."""

    def test_reporter(self):
        assert _registry_utils.classify_plugin_type("ShowAnchors.glyphsReporter") == "Reporter"

    def test_filter(self):
        assert _registry_utils.classify_plugin_type("RoundCorner.glyphsFilter") == "Filter"

    def test_palette(self):
        assert _registry_utils.classify_plugin_type("PaletteTool.glyphsPalette") == "Palette"

    def test_tool(self):
        assert _registry_utils.classify_plugin_type("SpeedPunk.glyphsTool") == "Tool"

    def test_generic_plugin(self):
        assert _registry_utils.classify_plugin_type("MyPlugin.glyphsPlugin") == "Plugin"

    def test_no_extension(self):
        assert _registry_utils.classify_plugin_type("SomeScript") == "Unknown"

    def test_none_path(self):
        assert _registry_utils.classify_plugin_type(None) == "Unknown"

    def test_empty_string(self):
        assert _registry_utils.classify_plugin_type("") == "Unknown"

    def test_file_format(self):
        assert _registry_utils.classify_plugin_type("UFO.glyphsFileFormat") == "FileFormat"
