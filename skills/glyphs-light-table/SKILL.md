---
name: glyphs-light-table
description: "Queries Light Table plugin's Python and Objective-C API for Git version control in Glyphs. Use when scripting with Light Table version history, checking glyph/layer modification status (lt_status), loading previous font versions (lt_load_version), restoring glyphs from Git history, or mapping Python API calls to Objective-C selectors (LightTableInterface)."
---

# Light Table API

Git version control for Glyphs via the Light Table plugin (com.formkunft.LightTable). Provides `lt_*` extensions on GSFont/GSGlyph/GSLayer and ObjC bridge classes for version history access.

## Path Resolution

```
${GLYPHS_LIGHT_TABLE_PATH:-~/Library/Application Support/Glyphs 3/Repositories/Light-Table}
```

API source: `{path}/Python API/lighttable/__init__.py`

## Scripts

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

| Script | Purpose | Output |
|--------|---------|--------|
| `read_api.py` | Parse/search Light Table Python API | JSON: types, extensions, ObjC selectors |

## Usage

```bash
# List all types and extensions
python3 scripts/read_api.py

# Detail for a specific type (enum, GS class, ObjC class, dataclass)
python3 scripts/read_api.py DocumentState
python3 scripts/read_api.py GSFont
python3 scripts/read_api.py RestorationInfo

# Search across all types
python3 scripts/read_api.py --search "restore"
python3 scripts/read_api.py --search "version"
```

## Quick Reference

### Key Concepts

- `import lighttable` monkey-patches GSFont/GSGlyph/GSLayer with `lt_*` attributes
- All `lt_*` calls route through the private `_LightTableInterface` ObjC singleton
- Enum states: `DocumentState` (font repo status), `ObjectStatus` (glyph/layer modification)

### Typical Workflow

```
1. font.lt_document_state == DocumentState.OPERATIONAL  (check repo)
2. records = font.lt_available_records                   (get history)
3. font.lt_load_version(record, callback)                (load version)
4. glyph.lt_status                                       (check changes)
5. info = glyph.lt_restoration_info()                    (get restore handle)
6. info.restore_glyph_as_replacement()                   (restore)
```

### ObjC Selector Mapping

Python bridge `_` maps to ObjC `:`. Example:
- `documentStateOfFont_` → `documentStateOfFont:`
- `font_loadVersionForRecord_completionHandler_` → `font:loadVersionForRecord:completionHandler:`

Run `read_api.py` to see all `objc_selector` fields.

## Prerequisites

- Light Table installed in Glyphs 3
- Font in a Git repository
- Script runs in Glyphs context (`import lighttable`)

## Reference

See [references/api-overview.md](references/api-overview.md) for architecture details, full Python↔ObjC mapping patterns, and ObjC runtime class list.
