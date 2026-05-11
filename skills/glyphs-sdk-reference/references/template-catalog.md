# GlyphsSDK — Plugin Template & Sample Catalog

Catalog of the 7 plugin base classes, 9 Python Templates, and 6 Python Samples shipped in `GlyphsSDK/`. Use this as an index before running `scripts/list_templates.py` or `scripts/read_template.py`.

## Plugin base classes (7)

| Base class | Methods | Use it when you want… |
|---|---:|---|
| `ReporterPlugin` | 24 | Draw on glyph layers (foreground / background / inactive layers, edit/preview, vertical metrics) |
| `SelectTool` | 20 | Build a custom selection / editing tool that lives in the toolbar |
| `FileFormatPlugin` | 17 | Read or write a custom font file format on import / export |
| `FilterWithDialog` | 16 | Apply a transformation with a UI dialog (vanilla or .xib) |
| `PalettePlugin` | 16 | Add a sidebar panel to the main window |
| `FilterWithoutDialog` | 13 | Apply a transformation without UI (one-shot menu item) |
| `GeneralPlugin` | 7 | Add menu commands, observers, or arbitrary functionality |

Method-type classification used by `scripts/search_methods.py`:

| Type | Rule | Meaning |
|---|---|---|
| `protocol` | Method name ends with `_` | ObjC protocol callback (e.g. `drawForegroundForLayer_options_`) |
| `python_helper` | Has `@objc.python_method` decorator | Python-only helper, not bridged to ObjC |
| `python_wrapped` | Other methods | Python method that wraps an ObjC selector |

## Python Templates (9 variants)

| Template | Base class | Variant | When to use |
|---|---|---|---|
| Reporter | `ReporterPlugin` | — | Visual annotations on glyphs |
| Palette | `PalettePlugin` | — | Sidebar panel widget |
| General Plugin | `GeneralPlugin` | — | Menu command / global behavior |
| SelectTool | `SelectTool` | — | Custom editing tool |
| TemplateBinarySource | mixed | — | Bundling Obj-C / Swift binaries with Python entry |
| Filter (without dialog) | `FilterWithoutDialog` | one-shot | No UI; instant transformation |
| Filter (dialog with xib) | `FilterWithDialog` | xib UI | Interface Builder UI |
| File Format (dialog with vanilla) | `FileFormatPlugin` | vanilla UI | Cross-platform Python UI |
| File Format (dialog with xib) | `FileFormatPlugin` | xib UI | Native macOS UI |

Locate template source via `python3 scripts/list_templates.py --type template`. Read source + README via `python3 scripts/read_template.py <name>` (use `--variant` for filters / file formats).

## Python Samples (6+ working examples)

| Sample | Type | Demonstrates |
|---|---|---|
| Callback for context menu | Standalone script | Hooking the context menu via Glyphs callbacks |
| Document exported | Standalone script | Responding to `DOCUMENTEXPORTED` notification |
| MultipleTools | `SelectTool` bundle | Bundling multiple tools in one plugin |
| Plugin Preferences | README only | UserDefaults integration pattern |
| Plugin With Window | `GeneralPlugin` bundle | Opening a custom window from a plugin |
| Smiley Panel Plugin | `PalettePlugin` bundle | A complete working palette sample |

Additional standalone samples shipped under `Python Samples/` but not listed by `list_templates.py`:

- `Draw In Font View Example` — drawing customization in the font view
- `Kern Table Subsetter` — operating on `font.kerning`
- `Update Feature.glyphsPlugin` — auto-update plugin pattern

## Recommended lookup workflow

1. Identify the plugin type you want to build (use the **base class** table above).
2. Run `scripts/search_methods.py --plugin <type>` to list available lifecycle methods.
3. Run `scripts/read_template.py <type>` to read the canonical template (source + README).
4. Pick a matching **sample** for a working real-world reference.
5. For drawing-specific work, run `scripts/read_template.py --drawing-tools` to inspect `drawingTools.py`.

## Cross-references to other skills

- **`glyphs-python-api`** — for the runtime API (`GSFont`, `GSGlyph`, etc.) you will call from inside your plugin's lifecycle methods.
- **`glyphs-objc-headers`** — for the Obj-C selector signatures that `protocol`-typed methods bridge to.
- **`glyphs-vanilla-ui`** — for the Vanilla components you will compose inside `FilterWithDialog (vanilla)` and `File Format (vanilla)` templates.
- **`glyphs-packages`** — to find third-party plugin examples published to the official registry.
