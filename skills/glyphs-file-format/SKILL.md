---
name: glyphs-file-format
description: "Queries GlyphsFileFormat specification (v2/v3) and JSON Schema definitions from GlyphsSDK. Use when looking up .glyphs file type definitions, comparing v2 vs v3 format changes, browsing format structure, or querying JSON Schema for validation."
---

# GlyphsFileFormat Spec & Schema Skill

Query the `.glyphs` file format specification (v2/v3) and JSON Schema definitions from GlyphsSDK.

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

## Environment

```
${GLYPHS_SDK_PATH}  # Required: Path to GlyphsSDK directory
```

## Quick Start: Query a Type Definition

```bash
python3 scripts/query_spec.py glyph                # v3 definition (default)
python3 scripts/query_spec.py glyph --version 2    # v2 definition
```

Returns the complete definition from the spec including all properties, types, defaults, and descriptions.

## Quick Start: List All Types

```bash
python3 scripts/query_spec.py --list                # All v3 definitions
python3 scripts/query_spec.py --list --version 2    # All v2 definitions
```

Returns `[{name, gs_class}]` for every type in the spec.

## Quick Start: Query JSON Schema

```bash
python3 scripts/query_schema.py layer                         # glyphs-3 schema (default)
python3 scripts/query_schema.py layer --schema glyphs-1       # v2 schema
python3 scripts/query_schema.py --list                         # List all $defs
python3 scripts/query_schema.py --list --schema fontinfo-3     # List fontinfo $defs
```

Available schemas: `glyphs-1`, `glyphs-3`, `glyphs-autosave-1`, `glyphs-autosave-3`, `fontinfo-3`, `fontinfo-autosave-3`.

## Quick Start: Browse Format Overview

```bash
Read references/format-overview.md
```

Provides type index table, v2/v3 differences summary, and schema inventory.

## Quick Start: Validate a .glyphs File

The GlyphsSDK includes a validator (requires `glyphsLib` and `openstep_plist`):

```bash
python3 ${GLYPHS_SDK_PATH}/GlyphsFileFormat/validate.py <file.glyphs>
```

## Common Workflow

1. **Browse structure** → `Read references/format-overview.md` for type index and v2/v3 comparison
2. **Look up definition** → `python3 scripts/query_spec.py <type>` for human-readable spec
3. **Check schema** → `python3 scripts/query_schema.py <type>` for machine-readable JSON Schema
4. **Compare versions** → Query with `--version 2` and default v3 to see differences

## Reference

See [references/format-overview.md](references/format-overview.md) for the complete type index and format overview.

## Requirements

- Python 3.10+ (standard library only)
- GlyphsSDK submodule cloned
- `GLYPHS_SDK_PATH` environment variable pointing to GlyphsSDK directory
