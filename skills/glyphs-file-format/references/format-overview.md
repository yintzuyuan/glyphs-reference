# GlyphsFileFormat Overview

## File Format Flavors

| Flavor | Extension | Description |
|--------|-----------|-------------|
| Single File | `.glyphs` | All font data in one OpenStep plist file |
| Package | `.glyphspackage` | Bundle with `fontinfo.plist`, `order.plist`, `UIState.plist`, and individual `glyphs/*.glyph` files |

## Format Versions

| Version | Anchor Tag | Used By | Spec File |
|---------|-----------|---------|-----------|
| v2 (format 1) | `spec-glyphs-1-` | Glyphs 1 & 2 | `GlyphsFileFormatv2.md` |
| v3 (format 3) | `spec-glyphs-3-` | Glyphs 3 | `GlyphsFileFormatv3.md` |

## Document Top-Level Properties (v3)

Key required properties: `.appVersion`, `.formatVersion`, `fontMaster`, `glyphs`, `unitsPerEm`, `versionMajor`, `versionMinor`.

Notable v3 additions: `axes`, `kerningLTR`/`RTL`/`Vertical`, `metrics`, `numbers`, `properties`, `settings`, `stems`, `note`.

## Type Definitions Index

| Name | GS Class | Description |
|------|----------|-------------|
| anchor | GSAnchor | Anchor point on a glyph layer |
| annotation | GSAnnotation | Text/arrow/circle annotation |
| attr | - | Component/path attributes |
| attrShape | - | Shape-specific attributes |
| axis | GSAxis | Designspace variation axis |
| class | GSClass | OpenType layout class |
| color | - | RGB/Gray/CMYK color value |
| colorLabel | - | Color label (index or color) |
| component | GSComponent | Reference to another glyph |
| customParameter | GSCustomParameter | Custom parameter key-value |
| displayStrings | - | Edit View tab strings |
| feature | GSFeature | OpenType feature |
| featurePrefix | GSFeaturePrefix | Feature prefix code block |
| fontMaster | GSFontMaster | Master definition |
| glyph | GSGlyph | Glyph with layers |
| guide | GSGuide | Guide line |
| hint | GSHint | TrueType/PostScript hint |
| image | GSImage | Background image |
| indexPath | - | Node index path reference |
| infoProperty | GSInfoProperty | Font info property |
| infoValue | GSInfoValue | Localized info value |
| instance | GSInstance | Export instance |
| kerning | - | Kerning table structure |
| layer | GSLayer | Glyph layer with paths/components |
| metric | GSMetric | Font metric/stem/number |
| metricStore | GSMetricStore | Per-master metric values |
| node | GSNode | Path node (point) |
| orientation | GSElementOrientation | Left/center/right orientation |
| partProperty | GSPartProperty | Smart component property |
| path | GSPath | Bezier path |
| pos | - | Position tuple [x, y] |
| scale | - | Scale tuple [x, y] |
| shape | GSShape | Path or component union |
| size | - | Size tuple [width, height] |
| slant | - | Slant tuple |
| userData | - | Custom user data dictionary |

v2-only: `legacyPosition` (string format `"{x, y}"`).

## v2 vs v3 Key Differences

- **Format marker**: v3 has `formatVersion: 3`; v2 omits it (implies format 1)
- **Axes**: v3 has top-level `axes` array; v2 uses `customParameters`
- **Kerning**: v3 splits into `kerningLTR`/`kerningRTL`/`kerningVertical`; v2 uses `kerning`/`vertKerning`
- **Booleans**: v3 uses native `boolean`; v2 encodes as `0`/`"0"`/`1`/`"1"`
- **Positions**: v3 uses `pos: array [x, y]`; v2 uses `position: string "{x, y}"`
- **Components**: v3 has `ref` property; v2 uses `name`
- **Settings**: v3 groups grid/keyboard settings under `settings`; v2 has them at top level
- **Properties**: v3 uses structured `properties` array; v2 uses top-level keys (`designer`, `copyright`, etc.)

## JSON Schemas

| Schema | Purpose |
|--------|---------|
| `glyphs-3.schema.json` | v3 single file validation |
| `glyphs-1.schema.json` | v2 single file validation |
| `glyphs-autosave-3.schema.json` | v3 autosave validation |
| `glyphs-autosave-1.schema.json` | v2 autosave validation |
| `fontinfo-3.schema.json` | v3 package fontinfo.plist |
| `fontinfo-autosave-3.schema.json` | v3 package autosave fontinfo |

## Validation Tools

Located at `GlyphsSDK/GlyphsFileFormat/`:
- `validate.py` — Python validator (requires `glyphsLib`, `openstep_plist`)
- `validate.sh` — Shell wrapper for validation
- `Schemas/` — JSON Schema files for programmatic validation
