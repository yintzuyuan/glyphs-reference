---
name: glyphs-light-table
description: "Queries Light Table plugin's Python and Objective-C API for Git version control in Glyphs. Use when scripting with Light Table version history, checking glyph/layer modification status (lt_status), loading previous font versions (lt_load_version), restoring glyphs from Git history, or mapping Python API calls to Objective-C selectors (LightTableInterface)."
---

# Light Table API

Git version control for Glyphs via the Light Table plugin (`com.formkunft.LightTable`). The plugin extends `GSFont`, `GSGlyph`, and `GSLayer` with `lt_*` attributes that bridge through a private `_LightTableInterface` Obj-C singleton.

Use this skill whenever the question involves the plugin's version-history surface — checking modification state, listing past commits, loading an older font snapshot, or restoring a single glyph from history.

## Path Resolution

```
${GLYPHS_LIGHT_TABLE_PATH:-~/Library/Application Support/Glyphs 3/Repositories/Light-Table}
```

API source: `{path}/Python API/lighttable/__init__.py`

If `GLYPHS_LIGHT_TABLE_PATH` is unset, the default Glyphs 3 install location is used. The skill exits with a clear error if neither location holds the plugin.

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

## Core concepts

### Two state enums

| Enum | Scope | Values | Used by |
|---|---|---|---|
| `DocumentState` | Font-level repo status | `OPERATIONAL`, `UNINITIALIZED`, `UNAVAILABLE`, … | `font.lt_document_state` |
| `ObjectStatus` | Per-glyph / per-layer modification | `UNCHANGED`, `MODIFIED`, `ADDED`, `REMOVED` | `glyph.lt_status`, `layer.lt_status` |

A font must reach `DocumentState.OPERATIONAL` before any other `lt_*` call returns meaningful data.

### Bridge architecture

- `import lighttable` monkey-patches `GSFont`, `GSGlyph`, and `GSLayer` with `lt_*` attributes
- All `lt_*` properties and methods route through the private `_LightTableInterface` Obj-C singleton
- Python's `_` separator maps to Obj-C `:` (see selector mapping below)

### Restoration vs. version loading

| Goal | Call | Scope |
|---|---|---|
| Load entire font at a past commit | `font.lt_load_version(record, callback)` | Whole document, replaces current view |
| Get a handle to restore a single glyph | `glyph.lt_restoration_info()` → `RestorationInfo` | Glyph-level, surgical |
| Restore one glyph from history | `info.restore_glyph_as_replacement()` | Single glyph, keeps rest of font intact |

Use `lt_load_version` for browsing; use `RestorationInfo` for cherry-picking changes.

## Worked workflow — "Show me what's modified in this glyph since the last commit"

```python
import lighttable
from lighttable import DocumentState, ObjectStatus

font = Glyphs.font

# 1. Guard: is the font actually under Light Table control?
if font.lt_document_state != DocumentState.OPERATIONAL:
    print("Font not in an operational Light Table repo.")
    return

# 2. Iterate glyphs and surface modifications
modified = [g for g in font.glyphs if g.lt_status == ObjectStatus.MODIFIED]
print(f"{len(modified)} modified glyphs:")
for g in modified:
    print(f"  {g.name}")

# 3. To roll back one glyph
target = font.glyphs["A"]
info = target.lt_restoration_info()
if info:
    info.restore_glyph_as_replacement()
```

This is the canonical pattern: check `DocumentState` first, then filter on `ObjectStatus`, then act with `RestorationInfo` for fine-grained restores.

## Worked workflow — "List the last N commits and load one"

```python
import lighttable

font = Glyphs.font
records = font.lt_available_records   # list[VersionRecord]

# Show last 5
for r in records[:5]:
    print(r.commit_summary, r.date)

# Load the second-most-recent
def on_loaded(success):
    print("Loaded:", success)

font.lt_load_version(records[1], on_loaded)
```

The callback runs asynchronously after Light Table finishes the load.

## ObjC selector mapping

Python's `_` maps to Obj-C `:`. Trailing `_` keeps the trailing colon. Examples:

| Python | Obj-C selector |
|---|---|
| `documentStateOfFont_` | `documentStateOfFont:` |
| `font_loadVersionForRecord_completionHandler_` | `font:loadVersionForRecord:completionHandler:` |
| `lt_restoration_info` | (Python helper; no direct selector) |

Run `python3 scripts/read_api.py <TypeName>` and look at the `objc_selector` fields to see all bridges.

## Common edge cases

- **Light Table not installed** → `import lighttable` raises `ModuleNotFoundError`. Catch and degrade gracefully.
- **Font not in a Git repo** → `font.lt_document_state` returns `DocumentState.UNAVAILABLE` or similar; do not proceed with history calls.
- **Uninitialized state right after opening** → some calls return `None` until the first index pass completes. Re-query after a short delay or wait for the relevant Light Table notification.
- **`lt_restoration_info()` returns `None`** → the glyph is unchanged or has no recoverable history; this is expected, not an error.
- **`lt_load_version` callback never fires** → ensure the script holds a strong reference to the callback; weak references get collected before Light Table's async load completes.

## Cross-skill collaboration

| Question | Use this skill | Use instead | Reason |
|---|---|---|---|
| "What `lt_*` properties does GSGlyph have?" | ✅ | — | Light Table-specific surface |
| "What does `glyph.layers` do (no `lt_` prefix)?" | — | `glyphs-python-api` | Core Python API |
| "What's the Obj-C selector for `lt_load_version`?" | ✅ | — | This skill exposes selector mapping |
| "What's the Obj-C protocol of `_LightTableInterface`?" | partial | `glyphs-objc-headers` | Header search for the underlying protocol declarations |
| "Where do I install Light Table?" | — | `glyphs-packages` | Plugin discovery + install |

## Prerequisites

- Light Table installed in Glyphs 3 (`com.formkunft.LightTable`)
- Font in a Git repository
- Script runs in Glyphs context (`import lighttable`)

## Reference

See [references/api-overview.md](references/api-overview.md) for architecture details, full Python↔ObjC mapping patterns, and ObjC runtime class list.
