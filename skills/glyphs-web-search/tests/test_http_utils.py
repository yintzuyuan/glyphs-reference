"""Tests for _http_utils.py — offline-only tests."""

from _http_utils import chunk_content, html_to_text, url_to_title


class TestHtmlToText:
    """Test HTML to plain text conversion."""

    def test_removes_script_tags(self, sample_html):
        text = html_to_text(sample_html)
        assert "var x = 1" not in text

    def test_removes_style_tags(self, sample_html):
        text = html_to_text(sample_html)
        assert ".foo" not in text
        assert "color: red" not in text

    def test_removes_nav_tags(self, sample_html):
        text = html_to_text(sample_html)
        assert "Navigation" not in text

    def test_removes_footer_tags(self, sample_html):
        text = html_to_text(sample_html)
        assert "Footer content" not in text

    def test_preserves_heading(self, sample_html):
        text = html_to_text(sample_html)
        assert "Main Title" in text

    def test_preserves_paragraph_text(self, sample_html):
        text = html_to_text(sample_html)
        assert "First paragraph" in text
        assert "bold" in text

    def test_preserves_list_items(self, sample_html):
        text = html_to_text(sample_html)
        assert "Item one" in text
        assert "Item two" in text

    def test_empty_string(self):
        assert html_to_text("") == ""

    def test_plain_text_passthrough(self):
        assert html_to_text("Hello world") == "Hello world"


class TestChunkContent:
    """Test content chunking/pagination."""

    def test_basic_chunk(self):
        result = chunk_content("Hello world", offset=0, limit=5)
        assert result["content"] == "Hello"
        assert result["offset"] == 0
        assert result["limit"] == 5
        assert result["total"] == 11
        assert result["has_more"] is True
        assert result["next_offset"] == 5

    def test_full_content_fits(self):
        result = chunk_content("Hi", offset=0, limit=100)
        assert result["content"] == "Hi"
        assert result["has_more"] is False
        assert result["next_offset"] is None

    def test_offset_beyond_content(self):
        result = chunk_content("Hi", offset=100, limit=10)
        assert result["content"] == ""
        assert result["offset"] == 2  # Clamped to total
        assert result["has_more"] is False

    def test_negative_offset_clamped(self):
        result = chunk_content("Hello", offset=-5, limit=3)
        assert result["offset"] == 0
        assert result["content"] == "Hel"

    def test_second_chunk(self):
        result = chunk_content("Hello world", offset=5, limit=6)
        assert result["content"] == " world"
        assert result["has_more"] is False

    def test_empty_content(self):
        result = chunk_content("", offset=0, limit=100)
        assert result["content"] == ""
        assert result["total"] == 0
        assert result["has_more"] is False


class TestUrlToTitle:
    """Test URL to readable title conversion."""

    def test_basic_slug(self):
        assert url_to_title("/news/glyphs-3-3-released") == "Glyphs 3 3 Released"

    def test_underscore_slug(self):
        assert url_to_title("/docs/getting_started") == "Getting Started"

    def test_trailing_slash(self):
        assert url_to_title("/news/new-feature/") == "New Feature"

    def test_single_word(self):
        assert url_to_title("/about") == "About"

    def test_full_url(self):
        title = url_to_title("https://glyphsapp.com/news/variable-fonts")
        assert title == "Variable Fonts"
