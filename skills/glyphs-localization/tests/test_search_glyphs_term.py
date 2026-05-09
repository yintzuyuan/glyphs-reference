"""Tests for search-glyphs-term.sh."""

import subprocess

import pytest


class TestSearchGlyphsTermHelp:
    """Tests that don't require Glyphs installation."""

    def test_help_flag(self, search_script):
        """--help should print usage and exit 0."""
        result = subprocess.run(
            [str(search_script), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage" in result.stdout

    def test_no_args_prints_error(self, search_script):
        """No arguments should print error and exit 1."""
        result = subprocess.run(
            [str(search_script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()

    def test_term_without_lang_prints_error(self, search_script):
        """Term without language should print error (unless --all-langs)."""
        result = subprocess.run(
            [str(search_script), "Cancel"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "error" in result.stdout.lower() or "language" in result.stdout.lower()

    def test_unknown_option(self, search_script):
        """Unknown option should print error and exit 1."""
        result = subprocess.run(
            [str(search_script), "--nonexistent"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_invalid_format(self, search_script):
        """Invalid format should print error and exit 1."""
        result = subprocess.run(
            [str(search_script), "--format", "xml", "Cancel", "en"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "invalid" in result.stdout.lower() or "error" in result.stdout.lower()


@pytest.mark.requires_glyphs
class TestSearchGlyphsTermWithGlyphs:
    """Tests that require Glyphs 3 installation."""

    def test_search_text_format(self, search_script):
        """Search with text format should return results."""
        result = subprocess.run(
            [str(search_script), "Cancel", "zh-Hant"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Search Results" in result.stdout or "Search Complete" in result.stdout

    def test_search_json_format(self, search_script):
        """Search with JSON format should return valid structure."""
        result = subprocess.run(
            [str(search_script), "--format", "json", "Cancel", "zh-Hant"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert '"term"' in result.stdout
        assert '"results"' in result.stdout

    def test_search_csv_format(self, search_script):
        """Search with CSV format should return header row."""
        result = subprocess.run(
            [str(search_script), "--format", "csv", "Cancel", "zh-Hant"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Language" in result.stdout

    def test_strings_only_flag(self, search_script):
        """--strings-only should not search NIB files."""
        result = subprocess.run(
            [str(search_script), "--strings-only", "Cancel", "en"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
