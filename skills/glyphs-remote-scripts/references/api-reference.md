# Glyphs Remote Scripts API Reference

Structured summary of the API in `Glyphs.py`. For full source, `Read` the file directly.

## Connection

### `application(appName, port=None)`

Connects to a running Glyphs.app instance via `NSConnection`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `appName` | (required) | Application name (e.g., `"Glyphs"`) |
| `port` | `"com.GeorgSeifert.Glyphs3"` | Registered port name. Override for specific build versions |

Returns the application proxy object, or `None` after 10 failed attempts (1s interval).

### Module-Level Globals

On import, `Glyphs.py` automatically:
1. Calls `application("Glyphs")` → stored as `Glyphs` and `GSApplication`
2. Gets the first open document → stored as `currentDocument`

## Factory Functions

Create new Glyphs objects through the application proxy. All objects are created in the Glyphs.app process.

| Function | Parameters | Description |
|----------|------------|-------------|
| `GSGlyph(name=None)` | `name`: glyph name (str) | Create a new glyph, optionally named |
| `GSLayer()` | — | Create a new layer |
| `GSPath()` | — | Create a new path |
| `GSNode(pt=None, type=None)` | `pt`: position, `type`: node type constant | Create a new node |
| `GSAnchor(pt=None, name=None)` | `pt`: position, `name`: anchor name (str) | Create a new anchor |
| `GSComponent(glyph=None, pt=None, scale=None)` | `glyph`: name (str) or GSGlyph, `pt`: position, `scale`: scale factor | Create a new component |

## RunScript

### `RunScript(code)`

Execute Python code inside Glyphs.app's Macro environment. Output is captured and printed locally via `GSStdOut`.

**Requires Glyphs 3.1+.** For older versions, use:
```python
macroViewController = Glyphs.objectWithClassName_("GSMacroViewController")
macroViewController.runMacroString_(code)
```

## Constants

Node type and smoothness constants:

| Constant | Value | Description |
|----------|-------|-------------|
| `GSMOVE` | 17 | Move-to point |
| `GSLINE` | 1 | Line-to point |
| `GSCURVE` | 35 | Curve point (on-curve) |
| `GSOFFCURVE` | 65 | Off-curve control point |
| `GSSHARP` | 0 | Sharp node connection |
| `GSSMOOTH` | 4096 | Smooth node connection |

## Usage Examples Index

All examples are in `testExternal.py`. Read the file directly for implementation details.

| Function | What It Does |
|----------|-------------|
| `exportAllInstances()` | Open a .glyphs file, export all instances as TTF/WOFF |
| `writeInstanceAsUFO()` | Generate an instance and write it as .ufo |
| `classTeste()` | Create objects by class name via `objectWithClassName_` |
| `runScriptInsideGlyphs()` | Execute Macro code (version-aware) |
| `accessGlyphsInfo()` | Query glyph info database |
| `accessLayers()` | Navigate font → glyph → master → layer → shape |

### Export Options

The `exportAllInstances()` example shows `instance.generate_()` accepting a dictionary of export options. Read `testExternal.py` directly for the current supported keys and values — see the comment block inside that function.
