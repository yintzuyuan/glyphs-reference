"""Tests for translate-term.sh."""

import subprocess

import pytest


class TestTranslateTermHelp:
    """Tests that don't require Glyphs installation."""

    def test_help_flag(self, translate_script):
        """--help should print usage and exit 0."""
        result = subprocess.run(
            [str(translate_script), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage" in result.stdout or "translate" in result.stdout.lower()

    def test_no_args_prints_usage(self, translate_script):
        """No arguments should print usage to stderr and exit 1."""
        result = subprocess.run(
            [str(translate_script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Usage" in result.stderr


@pytest.mark.requires_glyphs
class TestTranslateTermWithGlyphs:
    """Tests that require Glyphs 3 installation."""

    def test_list_locales(self, translate_script):
        """--list-locales should return available locales."""
        result = subprocess.run(
            [str(translate_script), "--list-locales"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        locales = result.stdout.strip().split("\n")
        assert len(locales) > 0
        assert "en" in locales
        assert "zh-Hant" in locales

    def test_translate_english_term(self, translate_script):
        """Translating an English term to zh-Hant should return a result."""
        result = subprocess.run(
            [str(translate_script), "Cancel", "zh-Hant"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "key:" in result.stdout
        assert "translation:" in result.stdout

    def test_translate_auto_detect(self, translate_script):
        """Auto-translate should detect source language."""
        result = subprocess.run(
            [str(translate_script), "Cancel"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "key:" in result.stdout

    def test_translate_unknown_term(self, translate_script):
        """Unknown term should return exit code 1 with 'not found' note."""
        result = subprocess.run(
            [str(translate_script), "xyzzy_nonexistent_term_12345"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "not in" in result.stdout.lower()

    @pytest.mark.slow
    def test_rebuild_cache(self, translate_script):
        """--rebuild should rebuild cache and exit 0.

        Marked slow: rebuilds all locale caches (>3 min).
        Run with: pytest -m slow
        """
        result = subprocess.run(
            [str(translate_script), "--rebuild"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert result.returncode == 0
        assert "cache" in result.stderr.lower()
