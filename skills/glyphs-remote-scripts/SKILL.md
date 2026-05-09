---
name: glyphs-remote-scripts
description: "Controls Glyphs.app from external Python processes via NSConnection (Distributed Objects). Use when connecting to Glyphs from Terminal, executing macros remotely via RunScript, or creating GSFont/GSGlyph objects from an external script."
---

# Glyphs Remote Scripts Skill

Control Glyphs.app from an external Python process via NSConnection (Distributed Objects). This API provides a bridge to create objects, access documents, and execute Macro code without running inside Glyphs.

## Source Path

```
${GLYPHS_SDK_PATH}/Glyphs remote scripts/
```

Where `GLYPHS_SDK_PATH` is the local GlyphsSDK submodule root. Typically `GlyphsSDK/` relative to the plugin repository root.

The entire API is contained in 4 files (~210 lines total):

| File | Lines | Content |
|------|-------|---------|
| `Glyphs.py` | 106 | Bridge module: connection, factory functions, RunScript, constants |
| `testExternal.py` | 103 | 6 usage examples (export, UFO, RunScript, layer access, etc.) |
| `accessSpecificVersion.py` | 5 | Connect to a specific Glyphs build version |
| `Readme.md` | 3 | Brief description |

## Key Concept: NSConnection Bridge

The bridge uses macOS Distributed Objects (`NSConnection`) to connect to a running Glyphs.app instance. This means:

- **Glyphs.app must be running** before executing any remote script
- **No Python wrapper available** — you must use Obj-C method names (e.g., `font.familyName()`, `glyph.setName_(name)`) instead of Python-style property access (e.g., `font.familyName`, `glyph.name = name`)
- Objects returned are **proxy objects** communicating via inter-process messaging

## Quick Start: Read the API

The full API is in a single 106-line file:

```bash
Read ${GLYPHS_SDK_PATH}/Glyphs remote scripts/Glyphs.py
```

This gives you: connection function, factory functions, RunScript, and all constants.

## Quick Start: View Usage Examples

6 practical examples covering common workflows:

```bash
Read ${GLYPHS_SDK_PATH}/Glyphs remote scripts/testExternal.py
```

Examples include: export instances, write UFO, run script inside Glyphs, access glyph info, and access layers.

## Quick Start: Connect to a Specific Version

```bash
Read ${GLYPHS_SDK_PATH}/Glyphs remote scripts/accessSpecificVersion.py
```

Uses the `application()` function with a version-specific port name.

## Important Notes

### Obj-C Method Names Required

Since the Python wrapper is not available in the remote context, all method calls use Obj-C style:

```python
# Remote script (Obj-C style)
font.familyName()           # getter
glyph.setName_(name)        # setter
font.glyphForName_("A")     # method with argument

# NOT the Python wrapper style used inside Glyphs:
# font.familyName            # won't work
# glyph.name = name          # won't work
```

### RunScript Version Difference

`RunScript()` requires Glyphs 3.1+. For older versions, use `GSMacroViewController.runMacroString_()` — see `testExternal.py` for the version-checking pattern.

### Default Connection Port

The default port is `com.GeorgSeifert.Glyphs3`. To connect to a specific build, pass a versioned port name like `com.GeorgSeifert.Glyphs3.3313`.

## Reference

See [references/api-reference.md](references/api-reference.md) for a structured API summary of all functions and constants.
