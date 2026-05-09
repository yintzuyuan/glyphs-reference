"""Tests for extract-nib-strings.sh."""

import subprocess

import pytest


class TestExtractNibStringsHelp:
    """Tests that don't require Glyphs installation."""

    def test_help_flag(self, extract_script):
        """--help should print usage and exit 0."""
        result = subprocess.run(
            [str(extract_script), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage" in result.stdout

    def test_unknown_option(self, extract_script):
        """Unknown option should print error and exit 1."""
        result = subprocess.run(
            [str(extract_script), "--nonexistent"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1


@pytest.mark.requires_glyphs
class TestExtractNibStringsWithGlyphs:
    """Tests that require Glyphs 3 installation."""

    def test_default_extraction(self, extract_script):
        """Default run should extract NIB strings."""
        result = subprocess.run(
            [str(extract_script)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Extraction Complete" in result.stdout

    def test_term_filter(self, extract_script):
        """--term should filter strings by keyword."""
        result = subprocess.run(
            [str(extract_script), "--term", "Font"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_csv_format(self, extract_script):
        """--format csv should output CSV header."""
        result = subprocess.run(
            [str(extract_script), "--term", "Font", "--format", "csv"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "NIB File" in result.stdout

    def test_json_format(self, extract_script):
        """--format json should output valid JSON structure."""
        result = subprocess.run(
            [str(extract_script), "--term", "Font", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert '"source"' in result.stdout
        assert '"strings"' in result.stdout

    def test_keys_only(self, extract_script):
        """--keys-only should output only keys."""
        result = subprocess.run(
            [str(extract_script), "--term", "Font", "--keys-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
