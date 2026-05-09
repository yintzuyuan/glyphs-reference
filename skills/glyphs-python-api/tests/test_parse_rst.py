"""Tests for _parse_rst.py — RST documentation parser."""

import pytest

import _parse_rst


# --- Phase 2a: Class headers ---


class TestParseClasses:
    """Test parsing of class definitions from RST."""

    def test_finds_all_35_classes(self, sphinx_rst_path):
        """RST contains exactly 35 class definitions."""
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        assert len(classes) == 35

    def test_class_has_required_fields(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        first = classes[0]
        assert "name" in first
        assert "description" in first
        assert "line" in first
        assert "properties" in first
        assert "methods" in first

    def test_first_class_is_gsapplication(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        assert classes[0]["name"] == "GSApplication"

    def test_class_description_not_empty(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        for cls in classes:
            assert cls["description"], f"{cls['name']} should have a description"

    def test_class_line_numbers_ascending(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        lines = [c["line"] for c in classes]
        assert lines == sorted(lines)

    def test_known_classes_present(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        names = [c["name"] for c in classes]
        for expected in ["GSFont", "GSLayer", "GSGlyph", "GSNode", "GSPath"]:
            assert expected in names

    def test_constructor_params_preserved(self, sphinx_rst_path):
        """Classes with constructor params should preserve them."""
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        by_name = {c["name"]: c for c in classes}
        # GSGlyph([name, autoName=True])
        assert "constructor_params" in by_name["GSGlyph"]


# --- Phase 2b: Autosummary (property/method names) ---


class TestAutosummary:
    """Test extraction of property and method name lists."""

    def test_gsfont_has_properties(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        assert len(gsfont["properties"]) > 20

    def test_gsfont_has_methods(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        assert len(gsfont["methods"]) > 5

    def test_property_has_name(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        prop = gsfont["properties"][0]
        assert "name" in prop

    def test_method_has_name(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        method = gsfont["methods"][0]
        assert "name" in method


# --- Phase 2c: Attribute details ---


class TestAttributeDetails:
    """Test detailed attribute parsing (description, type, examples)."""

    def test_attribute_has_description(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        masters = next(p for p in gsfont["properties"] if p["name"] == "masters")
        assert masters["description"]

    def test_attribute_has_type(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        masters = next(p for p in gsfont["properties"] if p["name"] == "masters")
        assert masters.get("type") == "list"

    def test_attribute_with_class_reference_in_type(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsapp = next(c for c in classes if c["name"] == "GSApplication")
        font = next(p for p in gsapp["properties"] if p["name"] == "font")
        # :type: :class:`GSFont`
        assert "GSFont" in font.get("type", "")

    def test_attribute_with_examples(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        glyphs = next(p for p in gsfont["properties"] if p["name"] == "glyphs")
        assert glyphs.get("examples")
        assert any("font.glyphs" in ex for ex in glyphs["examples"])


# --- Phase 2d: Function (method) details ---


class TestMethodDetails:
    """Test detailed method parsing (params, description, return type)."""

    def test_method_has_params(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        save = next(m for m in gsfont["methods"] if m["name"] == "save")
        assert save.get("params")

    def test_method_has_description(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        save = next(m for m in gsfont["methods"] if m["name"] == "save")
        assert save["description"]

    def test_method_with_return_type(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        kerning = next(
            m for m in gsfont["methods"] if m["name"] == "kerningForPair"
        )
        assert kerning.get("return_type") == "float"

    def test_method_with_examples(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        kerning = next(
            m for m in gsfont["methods"] if m["name"] == "kerningForPair"
        )
        assert kerning.get("examples")


# --- Phase 2e: Standalone functions and constants ---


class TestStandaloneFunctions:
    """Test parsing of standalone functions (zero-indent)."""

    def test_finds_16_functions(self, sphinx_rst_path):
        functions = _parse_rst.parse_standalone_functions(sphinx_rst_path)
        assert len(functions) == 16

    def test_function_has_required_fields(self, sphinx_rst_path):
        functions = _parse_rst.parse_standalone_functions(sphinx_rst_path)
        func = functions[0]
        assert "name" in func
        assert "params" in func
        assert "description" in func

    def test_dividecurve_present(self, sphinx_rst_path):
        functions = _parse_rst.parse_standalone_functions(sphinx_rst_path)
        names = [f["name"] for f in functions]
        assert "divideCurve" in names

    def test_function_with_return_type(self, sphinx_rst_path):
        functions = _parse_rst.parse_standalone_functions(sphinx_rst_path)
        divide = next(f for f in functions if f["name"] == "divideCurve")
        assert divide.get("return_type") == "list"


class TestParseConstants:
    """Test parsing of constants (RST + __init__.py values)."""

    def test_finds_constants(self, sphinx_rst_path, init_py_path):
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        assert len(constants) > 50

    def test_constant_has_required_fields(self, sphinx_rst_path, init_py_path):
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        const = constants[0]
        assert "name" in const
        assert "category" in const

    def test_constant_has_value_from_init_py(self, sphinx_rst_path, init_py_path):
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        line_const = next(c for c in constants if c["name"] == "LINE")
        assert line_const["value"] == '"line"'

    def test_constant_has_description(self, sphinx_rst_path, init_py_path):
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        line_const = next(c for c in constants if c["name"] == "LINE")
        assert line_const["description"]

    def test_constant_has_category(self, sphinx_rst_path, init_py_path):
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        line_const = next(c for c in constants if c["name"] == "LINE")
        assert line_const["category"] == "Node Types"

    def test_triple_has_rst_value(self, sphinx_rst_path, init_py_path):
        """TRIPLE = 128 is defined in RST with value."""
        constants = _parse_rst.parse_constants(sphinx_rst_path, init_py_path)
        triple = next(c for c in constants if c["name"] == "TRIPLE")
        assert triple["value"] == "128"


# --- Phase 2f: Cross-references ---


class TestCrossReferences:
    """Test extraction of :class: cross-references."""

    def test_gsfont_references_gsfontmaster(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        refs = gsfont.get("cross_references", [])
        assert "GSFontMaster" in refs

    def test_gsfont_references_gsglyph(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        gsfont = next(c for c in classes if c["name"] == "GSFont")
        refs = gsfont.get("cross_references", [])
        assert "GSGlyph" in refs

    def test_cross_references_deduplicated(self, sphinx_rst_path):
        classes = _parse_rst.parse_classes(sphinx_rst_path)
        for cls in classes:
            refs = cls.get("cross_references", [])
            assert len(refs) == len(set(refs)), f"{cls['name']} has duplicate refs"
