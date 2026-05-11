---
name: glyphs-file-format
description: "Queries GlyphsFileFormat specification (v2/v3) and JSON Schema definitions from GlyphsSDK. Use when looking up .glyphs file type definitions, comparing v2 vs v3 format changes, browsing format structure, or querying JSON Schema for validation."
---

# GlyphsFileFormat Spec & Schema Skill

Query the `.glyphs` file format specification (v2/v3) and JSON Schema definitions from GlyphsSDK. This skill answers two distinct kinds of questions: (1) "What does field X mean and what type is it?" using the human-readable spec, and (2) "How do I validate this file?" using the JSON Schema.

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

## Environment

```
${GLYPHS_SDK_PATH}  # Required: Path to GlyphsSDK directory
```

If the variable is not set, fall back to the plugin-relative submodule at `${CLAUDE_PLUGIN_ROOT}/GlyphsSDK/`.

## Two data sources — which to use

| Question | Use | Reason |
|---|---|---|
| What does this key mean? | `query_spec.py` | Spec includes prose descriptions |
| What type is allowed for this key? | `query_spec.py` | Spec shows type + default + range |
| Is this file structurally valid? | `query_schema.py` + the validator script | JSON Schema is machine-checkable |
| What changed from v2 to v3? | `query_spec.py` with `--version 2` then default v3 | Spec is per-version |

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

Returns `[{name, gs_class}]` for every type in the spec. Use this to discover what's available before drilling into a specific type.

## Quick Start: Query JSON Schema

```bash
python3 scripts/query_schema.py layer                         # glyphs-3 schema (default)
python3 scripts/query_schema.py layer --schema glyphs-1       # v2 schema
python3 scripts/query_schema.py --list                         # List all $defs
python3 scripts/query_schema.py --list --schema fontinfo-3     # List fontinfo $defs
```

Available schemas:

| Schema id | Scope |
|---|---|
| `glyphs-1` | v2 main file |
| `glyphs-3` | v3 main file |
| `glyphs-autosave-1` | v2 autosave variant |
| `glyphs-autosave-3` | v3 autosave variant |
| `fontinfo-3` | v3 `fontinfo.plist` style |
| `fontinfo-autosave-3` | v3 fontinfo autosave |

## Quick Start: Validate a .glyphs File

The GlyphsSDK includes a validator (requires `glyphsLib` and `openstep_plist`):

```bash
python3 ${GLYPHS_SDK_PATH}/GlyphsFileFormat/validate.py <file.glyphs>
```

The validator reports schema mismatches with field paths. For a typical font, expect 0–2 false positives on edge fields (custom parameters mostly); investigate any error on a structural field (`glyphs`, `layers`, `masters`, etc.).

## Worked workflow — "What does `kernTop` mean in v3 vs v2?"

```bash
# 1. Confirm the field exists in v3 spec
python3 scripts/query_spec.py glyph | grep -A2 kernTop

# 2. Pull the v2 spec for comparison
python3 scripts/query_spec.py glyph --version 2 | grep -A2 kernTop

# 3. If v2 has a different name, query the schema for the legal type
python3 scripts/query_schema.py glyph --schema glyphs-1

# 4. For prose context, fall back to the handbook (see glyphs-web-search skill)
```

This workflow is the canonical pattern for migration questions: spec for semantics, schema for typing, handbook for narrative.

## v2 vs v3 — common migration friction points

| Area | v2 → v3 change | Where to verify |
|---|---|---|
| Format version key | `.formatVersion = 2` → `3` | Spec top-level metadata |
| Master metrics | Flat keys (`ascender`, `capHeight`, …) | `master` definition |
| Metrics in v3 | Indexed `metricValues` array tied to font-level `metrics` definitions | `metric` + `metricValues` |
| Axes | Implicit weight/width | Explicit `axes` array with `name` + `tag` |
| Number values | Floats serialized as strings | Schema relaxes — both float and string accepted in v3 |
| Layers | `associatedMasterId` always required | Now optional for backup / virtual layers |
| Shape model | `paths` + `components` | Unified `shapes` array with `shape` discriminator |

When in doubt, run `query_spec.py` for both versions side-by-side and diff the output.

## Common edge cases

- **`$GLYPHS_SDK_PATH` not set** → both scripts exit with a clear error. Set the variable or fall back to `${CLAUDE_PLUGIN_ROOT}/GlyphsSDK/`.
- **Type not found in `query_spec.py`** → run `--list` to see canonical names; the spec uses lowerCamelCase (e.g. `fontInfoValueLocalized`, not `FontInfoValueLocalized`).
- **Schema lookup returns nothing for a known field** → JSON Schema uses `$defs` indirection; many fields live under a `$ref` rather than inline. Use `query_schema.py --list` to discover the actual `$def` name.
- **Spec says type is `string` but schema accepts `number`** → v3 is intentionally permissive on numeric fields; both serialise to the same in-memory value when loaded by Glyphs.

## Cross-skill collaboration

| Question | Use this skill | Use instead | Reason |
|---|---|---|---|
| "What field stores X in the file?" | ✅ | — | This is the spec's job |
| "How do I read field X from Python?" | — | `glyphs-python-api` | Python wrapper is the runtime API |
| "How do I write a custom file format that exports to `.glyphs`?" | — | `glyphs-sdk-reference` (FileFormatPlugin) | Plugin lifecycle is in the SDK skill |
| "Show me the chapter explaining glyph names" | — | `glyphs-web-search` | Handbook prose is the right surface |

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
