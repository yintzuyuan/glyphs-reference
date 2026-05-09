"""Tests for search_custom_parameters.py — offline parse_parameters logic."""

from search_custom_parameters import parse_parameters


class TestParseParameters:
    """Test parameter parsing from text content."""

    def test_parses_parameters(self, sample_custom_params_text):
        params = parse_parameters(sample_custom_params_text)
        names = [p["name"] for p in params]
        assert "postscriptSlantAngle" in names
        assert "glyphOrder" in names
        assert "postscriptIsFixedPitch" in names
        assert "blueValues" in names

    def test_parameter_count(self, sample_custom_params_text):
        params = parse_parameters(sample_custom_params_text)
        assert len(params) == 4

    def test_description_contains_type(self, sample_custom_params_text):
        params = parse_parameters(sample_custom_params_text)
        slant = next(p for p in params if p["name"] == "postscriptSlantAngle")
        assert "float" in slant["description"].lower()

    def test_multiline_description(self, sample_custom_params_text):
        params = parse_parameters(sample_custom_params_text)
        blue = next(p for p in params if p["name"] == "blueValues")
        assert "alignment zones" in blue["description"].lower()

    def test_empty_text(self):
        assert parse_parameters("") == []

    def test_no_parameters_in_text(self):
        assert parse_parameters("Just some random text without parameters.") == []

    def test_header_only(self):
        text = "### Custom Parameters\n\nCustom parameters provide extra settings.\n"
        assert parse_parameters(text) == []
