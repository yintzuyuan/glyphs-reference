---
name: glyphs-remote-scripts
description: "Controls Glyphs.app from external Python processes via NSConnection (Distributed Objects). Use when connecting to Glyphs from Terminal, executing macros remotely via RunScript, or creating GSFont/GSGlyph objects from an external script."
---

# Glyphs Remote Scripts Skill

Control Glyphs.app from an external Python process via NSConnection (Distributed Objects). This API provides a bridge to create objects, access documents, and execute Macro code without running inside Glyphs. Use it when you need to drive Glyphs from a system-level script (CI pipeline, terminal, automation runner) rather than from the Macro window or a plugin.

## Source Path

```
${GLYPHS_SDK_PATH}/Glyphs remote scripts/
```

Where `GLYPHS_SDK_PATH` is the local GlyphsSDK submodule root. Typically `GlyphsSDK/` relative to the plugin repository root. If unset, fall back to `${CLAUDE_PLUGIN_ROOT}/GlyphsSDK/`.

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
- **No Python wrapper available** — must use Obj-C method names (e.g., `font.familyName()`, `glyph.setName_(name)`) instead of Python-style property access (e.g., `font.familyName`, `glyph.name = name`)
- Objects returned are **proxy objects** communicating via inter-process messaging
- Method calls are synchronous and **block** until Glyphs responds; expect higher latency than in-process calls

## When to use remote scripts vs. inside-Glyphs scripts

| Goal | Use |
|---|---|
| One-off automation from terminal | Remote scripts (this skill) |
| CI / scheduled job that opens fonts, runs ops, exports | Remote scripts |
| Macro window interactive prototyping | Inside-Glyphs (`glyphs-python-api`) |
| Plugin (Reporter, Filter, etc.) | Inside-Glyphs (`glyphs-sdk-reference`) |
| Read `.glyphs` file without launching Glyphs | Neither — use `glyphsLib` Python package |

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

## Worked workflow — "Export every instance of a font from a terminal script"

```python
# external_export.py — run with /usr/bin/python3 external_export.py
import sys
sys.path.insert(0, "/path/to/Glyphs remote scripts")
from Glyphs import application, font

glyphs = application()
doc = glyphs.openDocumentWithContentsOfURL_(NSURL.fileURLWithPath_("/path/to/font.glyphs"))
f = doc.font()

for instance in f.instances():
    if not instance.active():
        continue
    instance.generate()    # equivalent of the Export menu
    print("Exported:", instance.name())
```

Run this from a regular terminal — Glyphs.app must be open. Each `.generate()` call returns when Glyphs finishes the export.

## Worked workflow — "Run an arbitrary Macro snippet inside Glyphs"

```python
from Glyphs import application, RunScript

glyphs = application()
result = RunScript("""
Glyphs.fonts[0].familyName = "Renamed"
Glyphs.fonts[0].save_(None)
""")
print(result)   # captured stdout from inside Glyphs
```

`RunScript()` requires Glyphs 3.1+. For older versions, use `GSMacroViewController.runMacroString_()` — see `testExternal.py` for the version-checking pattern.

## Obj-C method conventions

Since the Python wrapper is **not** available in the remote context, all method calls use Obj-C style:

| Inside Glyphs (Python wrapper) | Remote (Obj-C style) |
|---|---|
| `font.familyName` | `font.familyName()` |
| `glyph.name = "A"` | `glyph.setName_("A")` |
| `font.glyphForName("A")` | `font.glyphForName_("A")` |
| `font.glyphs["A"]` | `font.glyphForName_("A")` (no subscript syntax) |
| `font.masters` | `font.fontMasters()` |

Each `:` in the Obj-C selector becomes `_` in Python. Trailing colon stays.

## Default Connection Port

The default port is `com.GeorgSeifert.Glyphs3`. To connect to a specific build, pass a versioned port name like `com.GeorgSeifert.Glyphs3.3313` via `application(port=...)`.

## Common edge cases

- **`NSConnection` returns `None`** → Glyphs.app is not running. Launch it (`open -a "Glyphs 3"`) and retry.
- **Port name mismatch** → Glyphs beta builds may publish under different port names; check `accessSpecificVersion.py` for the pattern.
- **`AttributeError` on a Python-style call** → you forgot you're remote. Translate to Obj-C selector form.
- **Proxy object outlives connection** → if the script disconnects, the proxy raises `NSDistantObjectInvalid` on next call. Keep the connection alive for the script's lifetime.
- **`RunScript` returns empty string** → check the script for syntax errors; remote `RunScript` swallows traceback by default. Wrap the body in `try/except` and `print` to capture errors.
- **PyObjC not installed** → `pip3 install pyobjc-framework-Cocoa` is required for the bridge.

## Cross-skill collaboration

| Question | Use this skill | Use instead | Reason |
|---|---|---|---|
| "How do I drive Glyphs from CI?" | ✅ | — | This is remote-scripts' job |
| "How do I read a .glyphs file without launching Glyphs?" | — | (external `glyphsLib` package) | Not Glyphs-API at all |
| "What Python properties does GSFont have?" | partial | `glyphs-python-api` | Use the Python skill for property names, then translate to Obj-C selector here |
| "What's the Obj-C selector for setLayer_forKey_?" | — | `glyphs-objc-headers` | Headers are the canonical selector source |
| "How do I write a Filter plugin?" | — | `glyphs-sdk-reference` | Plugins run in-process, not remote |

## Reference

See [references/api-reference.md](references/api-reference.md) for a structured API summary of all functions and constants.
