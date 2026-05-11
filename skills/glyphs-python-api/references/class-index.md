# Glyphs Python API — Class / Function / Constant Index

Quick navigation index for the 35 classes, 16 standalone functions, and 133 constants exposed by the Glyphs.app Python Scripting API. Use this as a map before running `scripts/search_api.py` or `scripts/read_class.py`.

## Class index (35 classes by domain)

### Application

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSApplication` | 20 | 16 | Top-level `Glyphs` object — windows, fonts, callbacks |
| `GSDocument` | 2 | 0 | Document container for a font |

### Font · Master · Instance

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSFont` | 66 | 12 | The font object (most-used entry point) |
| `GSAxis` | 5 | 0 | Variable font axis |
| `GSMetric` | 7 | 0 | Linked metrics & stems |
| `GSFontMaster` | 22 | 0 | Master in the "Masters" pane |
| `GSAlignmentZone` | 2 | 0 | Master blue / other zones |
| `GSInstance` | 62 | 2 | Instance in the "Exports" pane |
| `GSCustomParameter` | 4 | 0 | Custom parameter name/value pair |

### OpenType definitions

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSClass` | 5 | 0 | OT class definition |
| `GSFeaturePrefix` | 4 | 0 | Standalone lookup / pre-feature code |
| `GSFeature` | 7 | 1 | OT feature definition |

### Glyph

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSGlyph` | 45 | 4 | Glyph in the font |
| `GSGlyphInfo` | 17 | 0 | Glyph metadata (Unicode, category, script) |

### Layer & geometry

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSLayer` | 45 | 22 | Layer of a glyph (the geometry container) |
| `GSAnchor` | 5 | 0 | Anchor point |
| `GSComponent` | 20 | 2 | Component reference |
| `GSGlyphReference` | 1 | 0 | Lightweight reference |
| `GSSmartComponentAxis` | 4 | 0 | Smart-component axis |
| `GSShape` | 2 | 0 | Base shape class |
| `GSPath` | 10 | 3 | Closed/open path |
| `GSNode` | 11 | 2 | Node on a path |
| `GSPathSegment` | 2 | 11 | Bezier segment between two nodes |
| `GSGuide` | 8 | 0 | Guide line |
| `GSAnnotation` | 5 | 0 | Annotation marker |
| `GSHint` | 19 | 0 | Hint (PostScript / TrueType / corner) |
| `GSBackgroundImage` | 9 | 3 | Layer background image |
| `GSGradient` | 6 | 0 | Gradient fill |

### View / UI

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSEditViewController` | 19 | 3 | Edit tab view controller |
| `PreviewTextWindow` | 4 | 2 | Preview text window |

### Font Info value types

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `GSFontInfoValueLocalized` | 3 | 0 | Localized info value (per language) |
| `GSFontInfoValueSingle` | 2 | 0 | Single-value info |
| `GSFontInfoValue` | 3 | 0 | Generic info value |
| `GSMetricValue` | 5 | 0 | Metric value with type tag |

### Utility

| Class | Props | Methods | Purpose |
|---|---:|---:|---|
| `NSAffineTransform` | 5 | 0 | Affine transform (Apple) |

## Standalone function index (16 functions, 5 categories)

| Category | Functions |
|---|---|
| Bezier geometry | `divideCurve`, `distance`, `addPoints`, `subtractPoints`, `scalePoint` |
| Path ops | `removeOverlap`, `subtractPaths`, `intersectPaths` |
| File dialogs | `GetSaveFile`, `GetOpenFile`, `GetFolder` |
| UI dialogs | `Message`, `AskString`, `PickGlyphs` |
| Logging | `LogToConsole`, `LogError` |

## Constants index (133 constants, 12 categories)

| Category | Count | Examples |
|---|---:|---|
| Node types | 4 | `LINE`, `CURVE`, `QCURVE`, `OFFCURVE` |
| Shape attributes (fill / stroke / gradient / shadow / mask) | 18 | `FILL`, `FILLCOLOR`, `STROKEWIDTH`, `GRADIENT`, `SHADOW`, `INNERSHADOW`, `MASK` |
| File format versions | 3 | `GSFormatVersion1`, `GSFormatVersion3`, `GSFormatVersionCurrent` |
| Export formats | 7 | `OTF`, `TTF`, `VARIABLE`, `UFO`, `WOFF`, `WOFF2`, `PLAIN`, `EOT` |
| OT property name keys (Font Info) | 27 | `GSPropertyNameFamilyNamesKey`, `GSPropertyNameVendorIDKey`, … |
| Instance types | 2 | `INSTANCETYPESINGLE`, `INSTANCETYPEVARIABLE` |
| Hint types (PS / TT / corner / brush) | 17 | `TOPGHOST`, `STEM`, `BOTTOMGHOST`, `CORNER`, `CAP`, `BRUSH`, `TTSNAP`, `TTSTEM`, … |
| Menu identifiers | 10 | `APP_MENU`, `FILE_MENU`, `EDIT_MENU`, … `HELP_MENU` |
| NSMenuItem state | 3 | `ONSTATE`, `OFFSTATE`, `MIXEDSTATE` |
| Drawing & notifications | 17 | `DRAWFOREGROUND`, `DRAWBACKGROUND`, `MOUSEMOVED`, `UPDATEINTERFACE`, `DOCUMENTOPENED`, `TABDIDOPEN`, … |
| Writing direction & shape types | 8 | `GSBIDI`, `GSLTR`, `GSRTL`, `GSVertical`, `GSShapeTypePath`, `GSShapeTypeComponent` |
| Annotation, inspector size, metrics type | 17 | `TEXT`, `ARROW`, `CIRCLE`, `GSInspectorSizeSmall`, `GSMetricsTypeAscender`, `GSMetricsTypeCapHeight`, … |

For exact values, run `python3 scripts/search_api.py --constants` and filter by name.

## Cross-references to other skills

- **Third-party plugin APIs** — Light Table adds `lt_*` properties to `GSFont`, `GSGlyph`, `GSLayer`. See `glyphs-light-table` skill for the full surface.
- **Objective-C surface** — Every Python class wraps an Obj-C counterpart. See `glyphs-objc-headers` for the underlying selectors and properties.
- **Plugin scaffolding** — For plugin entry-point classes (Reporter, Filter, Palette, Tool, File Format), see `glyphs-sdk-reference`.
- **Remote-process control** — For driving Glyphs from an external Python process, see `glyphs-remote-scripts`.

## Recommended lookup workflow

1. Identify the class domain from the **Class index** above.
2. Run `scripts/search_api.py --search <keyword>` for fuzzy match.
3. Run `scripts/read_class.py <ClassName> --summary` to list members.
4. Run `scripts/read_class.py <ClassName> --member <name>` for full details (description, type, examples).
5. Run `scripts/read_class.py <ClassName> --relationships` to discover what links to it.
