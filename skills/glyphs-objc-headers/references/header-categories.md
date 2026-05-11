# GlyphsCore Headers Category Guide

The 174 header files fall into the following broad categories. Each category lists discovery patterns and representative files rather than an exhaustive index.

## Core Data Model

Core classes for the font data structure.

**Discover**: `Grep "@interface GS(Font|Glyph|Layer|Path|Node|Component|Anchor)" path/to/Headers/`

| Header | Description |
|--------|-------------|
| `GSFont.h` | Font document (contains masters, instances, glyphs) |
| `GSFontMaster.h` | Font master (metrics, custom parameters) |
| `GSGlyph.h` | Glyph (layers, unicode) |
| `GSLayer.h` | Layer (paths, components, anchors) |
| `GSPath.h` / `GSNode.h` | Paths and nodes |
| `GSComponent.h` | Component reference |
| `GSAnchor.h` / `GSGuide.h` | Anchors and guides |
| `GSInstance.h` | Export instance |
| `GSShape.h` / `GSElement.h` | Shape/Element base classes |

**Note**: Core classes usually have multiple category extensions (e.g. `GSLayer+PathOperations.h`); find them with `Glob path/to/Headers/ClassName+*.h`.

## Plugin Protocols

Protocol definitions that plugin developers must implement.

**Discover**: `Glob path/to/Headers/*Protocol*.h`

| Header | Description |
|--------|-------------|
| `GlyphsPluginProtocol.h` | Base plugin protocol |
| `GlyphsReporterProtocol.h` | Reporter plugin (visual overlays) |
| `GlyphsFilterProtocol.h` | Filter plugin (path processing) |
| `GlyphsPaletteProtocol.h` | Palette plugin (side panels) |
| `GlyphsToolProtocol.h` | Tool plugin (drawing tools) |
| `GlyphsFileFormatProtocol.h` | File format plugin |
| `GlyphsToolDrawProtocol.h` | Tool drawing interface |
| `GlyphsToolEventProtocol.h` | Tool event handling interface |
| `GSAppDelegateProtocol.h` | App delegate access |

## OpenType & Typography

OpenType features, hinting, and metrics.

**Discover**: `Grep "Feature\|Hint\|Metric\|Kern" path/to/Headers/ --glob "*.h" --output_mode files_with_matches`

| Header | Description |
|--------|-------------|
| `GSFeature.h` / `GSFeaturePrefix.h` | OpenType feature definitions |
| `GSFeatureComposer.h` / `GSFeatureGenerator.h` | Feature auto-generation |
| `GSHint.h` / `GSTTStem.h` | Hinting data |
| `GSMetric.h` / `GSMetricValue.h` | Metrics definitions |
| `GSAlignmentZone.h` | Alignment zones |
| `GSCustomParameter.h` | Custom parameters |
| `GSFontInfoProperty.h` / `GSFontInfoValue*.h` | Font info fields |

## UI Controllers & Views

Inspectors, dialogs, panels, and other UI components.

**Discover**: `Glob path/to/Headers/InspectorView*.h` and `Grep "Controller\|View" path/to/Headers/ --glob "GS*Controller*.h"`

| Header | Description |
|--------|-------------|
| `InspectorView*Controller.h` | 12 inspector-panel controllers |
| `GSDialogController.h` / `GSDialogContentView.h` | Dialogs |
| `GSPanelViewController.h` / `GSPanelView.h` | Panels |
| `GSGlyphEditViewProtocol.h` | Edit view interface |
| `GSWindowControllerProtocol.h` | Window controller interface |
| `GSGlyphCell.h` / `GSGlyphCellView.h` | Glyph cell view |
| `GSProgressWindowController.h` | Progress window |

## Drawing & Geometry

Path drawing, geometry computation, and the Pen protocol.

**Discover**: `Grep "Pen\|Bezier\|Geometrie\|Path" path/to/Headers/ --glob "GS*.h" --output_mode files_with_matches`

| Header | Description |
|--------|-------------|
| `GSPenProtocol.h` | Pen protocol definition |
| `GSBasePen.h` / `GSSegmentPen.h` / `GSPathPen.h` | Pen implementations |
| `GSGeometrieHelper.h` | Geometry helpers |
| `GSPathOperator.h` / `GSPathSegment.h` | Path operations |
| `GSFlattenPen.h` / `GSSVGPen.h` / `GSBezStringPen.h` | Specialized Pens |
| `GSProxyShapes.h` | Proxy shapes |

## Foundation Categories

Extensions on Foundation classes such as NSObject, NSString, and NSBezierPath.

**Discover**: `Glob path/to/Headers/NS*.h`

| Header | Description |
|--------|-------------|
| `NSBezierPath+*.h` | BezierPath extensions (4 files) |
| `NSString*.h` | String utilities |
| `NSImage+*.h` | Image extensions |
| `NSArrayHelpers.h` / `NSDictionaryHelpers.h` | Collection helpers |

## Misc / Utilities

Utility classes that do not fit the categories above.

**Discover**: browse the remaining `GS*.h` files

| Header | Description |
|--------|-------------|
| `GSUndoManager.h` | Undo management |
| `GSCallbackHandler.h` | Callback handling |
| `GSClass.h` / `GSSubstitution.h` | OpenType class and substitution |
| `GSInterpolationFontProxy.h` | Interpolation proxy |
| `GSOutlineImporter.h` | Outline import |
| `GlyphsCore.h` | Framework umbrella header |

## Search strategy

| Query intent | Best approach |
|--------------|--------------|
| Full API of a specific class | `Read` the class `.h` plus `Glob` its `+*.h` extensions |
| What a protocol requires you to implement | `Read` the matching `*Protocol.h`, mind the `@optional` sections |
| Where a method is declared | `Grep "methodName"` across all headers |
| All classes related to a feature | `Grep` by feature keyword, then `Read` each hit |
| Enum values or constants | `Grep "typedef.*enum\|extern\|#define"` |
