# Light Table Python API Overview

Light Table (com.formkunft.LightTable) by Florian Pircher — Git version control for Glyphs. The `lighttable` Python package provides scripting access to version history, modification status, and glyph/layer restoration.

## Architecture

`import lighttable` does two things at import time:

1. **Binds ObjC classes** via `objc.lookUpClass()` — exposes `Signature`, `Commit`, `Record`, `Version`, `RestorationInfo` as Python-accessible ObjC bridge objects
2. **Monkey-patches GS classes** — adds `lt_*` properties and methods to `GSFont`, `GSGlyph`, `GSLayer`

All operations go through the private `_LightTableInterface` ObjC singleton (not directly accessible from Python).

## API Categories

Use `read_api.py` to query live API details:

```bash
# Full API overview (all types, extensions, selectors)
python3 scripts/read_api.py

# Specific type detail
python3 scripts/read_api.py DocumentState
python3 scripts/read_api.py GSFont
python3 scripts/read_api.py RestorationInfo

# Search across types
python3 scripts/read_api.py --search "restore"
python3 scripts/read_api.py --search "version"
```

### Enums

State constants: `DocumentState` (font repository status), `ObjectStatus` (glyph/layer modification status), `ComponentIntegrationStrategy` (restoration behavior).

### GS Class Extensions (lt_*)

Properties and methods added to GSFont, GSGlyph, GSLayer at runtime:
- **GSFont**: repository state, version selection, record loading, changesets
- **GSGlyph/GSLayer**: modification status (`lt_status`), restoration info

### ObjC Bridge Classes

Objects returned by the API: `Signature` (git author), `Commit` (git commit), `Record` (file+commit pair), `Version` (loaded font version), `RestorationInfo` (glyph/layer restoration handle).

### Dataclass

`ComponentIntegrationPlan` — controls how components are handled during glyph restoration.

## Python ↔ ObjC Mapping

All Light Table functionality is implemented in ObjC. The Python API is a thin bridge:

### Mapping Patterns

| Python Pattern | ObjC Equivalent |
|---|---|
| `font.lt_document_state` | `[LightTableInterface documentStateOfFont:font]` |
| `font.lt_load_version(record, cb)` | `[LightTableInterface font:font loadVersionForRecord:record completionHandler:cb]` |
| `glyph.lt_status` | `[glyph lightTableStatus]` (instance method) |
| `sig.name` | `[sig name]` (pyobjc bridge) |

### Selector Naming Convention

Python bridge method names use `_` where ObjC uses `:`:
- `documentStateOfFont_` → `documentStateOfFont:`
- `font_loadVersionForRecord_completionHandler_` → `font:loadVersionForRecord:completionHandler:`

The `read_api.py` output includes `objc_selector` fields showing the exact Python bridge method name. Convert `_` to `:` for the ObjC selector.

### ObjC Runtime Access

For ObjC plugin developers, Light Table exposes these classes at runtime (no header files):
- `LightTableInterface` (main singleton)
- `LightTableSignature`, `LightTableCommit`, `LightTableRecord`
- `LightTableVersion`, `LightTableRestorationInfo`
- `LightTableComponentIntegrationPlan`

Access via `NSClassFromString()` / `objc_getClass()` in ObjC, or `objc.lookUpClass()` in Python.

## Common Workflow

```
1. Check state:     font.lt_document_state == DocumentState.OPERATIONAL
2. Get records:     records = font.lt_available_records
3. Load version:    font.lt_load_version(record, callback)
4. Check status:    glyph.lt_status  (UNMODIFIED / ADDED / MODIFIED)
5. Get restore info: info = glyph.lt_restoration_info()
6. Restore:         info.restore_glyph_as_replacement()
```

## Prerequisites

- Light Table plugin installed in Glyphs 3
- Font must be in a Git repository
- `import lighttable` must be called in script context (Glyphs macro panel or plugin)

## Official Documentation

https://formkunft.com/light-table/python-api/
