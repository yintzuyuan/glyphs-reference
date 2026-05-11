---
name: glyphs-sdk-reference
description: "Queries GlyphsSDK plugin development reference with AST-based analysis of 7 plugin base classes. Use when looking up plugin lifecycle methods, browsing Python Templates (9) and Samples (6), or understanding GlyphsReporter/GlyphsFilter/GlyphsPalette base class APIs for plugin development."
---

# GlyphsSDK Reference

Plugin development reference extracted from GlyphsSDK. Covers plugin base class methods, templates, and sample implementations.

## Scripts

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

| Script | Purpose | Output |
|--------|---------|--------|
| `search_methods.py` | AST analysis of plugins.py — 7 plugin base classes and their methods | Classes + methods with type classification |
| `list_templates.py` | List all Python Templates (9) and Samples (6) | Name + type + plugin_type + path |
| `read_template.py` | Read template/sample source code + README + AST info | Source + classes + imports + readme |

## Usage

### Plugin Methods

```bash
# List all 7 plugin base classes with methods
python scripts/search_methods.py

# Methods for a specific plugin type
python scripts/search_methods.py --plugin reporter

# Search methods across all classes
python scripts/search_methods.py --search foreground

# Identify a specific method
python scripts/search_methods.py --method drawForegroundForLayer_options_
```

**Method type classification:**

| Type | Meaning | AST rule |
|------|---------|----------|
| `protocol` | ObjC protocol method | Name ends with `_` |
| `python_helper` | Python convenience method | Has `@objc.python_method` decorator |
| `python_wrapped` | Python method override | Other methods |

### Templates & Samples

```bash
# List all templates + samples
python scripts/list_templates.py

# Only templates
python scripts/list_templates.py --type template

# Only samples
python scripts/list_templates.py --type sample
```

### Read Source Code

```bash
# Read a template (with README)
python scripts/read_template.py reporter

# Filter with specific variant
python scripts/read_template.py filter --variant "without dialog"

# Read a sample by name
python scripts/read_template.py "Smiley Panel Plugin"

# Read drawingTools.py
python scripts/read_template.py --drawing-tools
```

## Workflow Example

```
User: "How do I implement a Reporter plugin?"

1. Check available methods:
   $ python scripts/search_methods.py --plugin reporter
   → All methods with types and docstrings

2. Get the template:
   $ python scripts/read_template.py reporter
   → Source code + README guide

3. Check a sample for real-world patterns:
   $ python scripts/read_template.py "Smiley Panel Plugin"
   → Working example with AST analysis
```

## Templates Available

| Name | Plugin Type | Variant |
|------|-------------|---------|
| Reporter | Reporter | — |
| Palette | Palette | — |
| General Plugin | General | — |
| SelectTool | SelectTool | — |
| TemplateBinarySource | TemplateBinarySource | — |
| Filter (without dialog) | Filter | without dialog |
| Filter (dialog with xib) | Filter | dialog with xib |
| File Format (dialog with vanilla) | FileFormat | dialog with vanilla |
| File Format (dialog with xib) | FileFormat | dialog with xib |

## Samples Available

| Name | Type |
|------|------|
| Callback for context menu | Standalone script |
| Document exported | Standalone script |
| MultipleTools | SelectTool bundle |
| Plugin Preferences | README only |
| Plugin With Window | General bundle |
| Smiley Panel Plugin | Palette bundle |

## Additional Resources

- **`references/template-catalog.md`** — Catalog of the 7 plugin base classes (with method counts), 9 Python Templates with variants, and the 6+ working samples. Includes method-type classification rules (`protocol` / `python_helper` / `python_wrapped`) and cross-references to companion skills. Read this first to pick the right base class.

## Requirements

- Python 3.10+ (standard library only)
- GlyphsSDK submodule cloned
- `GLYPHS_SDK_PATH` environment variable pointing to GlyphsSDK directory
