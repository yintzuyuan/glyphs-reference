---
name: glyphs-python-api
description: "Queries Glyphs Python Scripting API reference (35 classes, 16 functions, 133 constants) parsed from Sphinx RST documentation. Use when looking up GSFont/GSLayer/GSGlyph Python API properties, searching for scripting methods, reading class documentation, or finding code examples for Glyphs Python scripting."
---

# Glyphs Python API Reference

Python Scripting API reference extracted from GlyphsSDK Sphinx documentation. Covers all 35 wrapper classes, standalone helper functions, and constants with their actual values.

## Scripts

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

| Script | Purpose | Output |
|--------|---------|--------|
| `search_api.py` | Search/list classes, members, constants, functions | Classes with counts, or search results |
| `read_class.py` | Read class/member/function details | Full properties, methods, types, examples |

## Usage

### Browse Classes

```bash
# List all 35 classes with property/method counts
python scripts/search_api.py

# Search across classes, properties, methods, constants
python scripts/search_api.py --search "layer"

# List all constants with values
python scripts/search_api.py --constants

# List standalone functions
python scripts/search_api.py --functions
```

### Read Details

```bash
# Full class details (properties + methods + descriptions)
python scripts/read_class.py GSFont

# Specific member (type, description, examples)
python scripts/read_class.py GSFont --member masters

# Summary (property/method names only)
python scripts/read_class.py GSFont --summary

# Cross-reference relationships
python scripts/read_class.py GSFont --relationships

# Standalone function details
python scripts/read_class.py --function divideCurve
```

## Workflow Example

```
User: "How do I access font masters in Python?"

1. Search for relevant classes:
   $ python scripts/search_api.py --search "master"
   → GSFontMaster class + related properties

2. Read the class overview:
   $ python scripts/read_class.py GSFontMaster --summary
   → All property/method names

3. Get specific member details:
   $ python scripts/read_class.py GSFontMaster --member customParameters
   → Description, type, code examples

4. Check relationships:
   $ python scripts/read_class.py GSFontMaster --relationships
   → Referenced by GSFont, GSLayer, etc.
```

## Data Sources

| Source | Content |
|--------|---------|
| Sphinx `index.rst` | Class descriptions, property types, method params, examples, cross-references |
| `__init__.py` | Constant actual values (e.g., `LINE = "line"`, `STEM = 0`) |

## Third-party Plugin APIs

- **Light Table** (Git version control): See the `glyphs-light-table` skill for `lt_*` extensions on GSFont/GSGlyph/GSLayer

## Requirements

- Python 3.10+ (standard library only)
- GlyphsSDK submodule cloned
- `GLYPHS_SDK_PATH` environment variable pointing to GlyphsSDK directory
