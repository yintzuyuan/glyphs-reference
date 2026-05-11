---
name: glyphs-objc-headers
description: "Searches GlyphsCore Objective-C header files (174 headers) for class APIs, protocol methods, properties, enums, and constants. Use when looking up GSFont/GSLayer/GSGlyph properties, finding GlyphsReporter or GlyphsFilter protocol methods, or searching Obj-C type definitions for plugin development."
---

# GlyphsCore Obj-C Headers Skill

Query 174 Objective-C header files from the GlyphsCore framework to find class APIs, protocol methods, properties, enums, and constants. This skill is the authoritative surface for the Objective-C side of the Glyphs API — Python wrappers ultimately bridge through these declarations.

## Headers Path

```
${GLYPHS_APP_HEADERS_PATH:-/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers}
```

If the env var is not set, use the default path above. The path resolves to the installed Glyphs 3 application bundle; the skill works without a separate GlyphsSDK checkout for this domain.

## When to use this skill versus the Python skill

| Question | Use |
|---|---|
| "What properties does GSFont expose in Python?" | `glyphs-python-api` |
| "What's the Obj-C selector for GSFont.familyName?" | This skill |
| "What protocol methods can a Filter plugin implement?" | This skill (`GlyphsFilterProtocol.h`) |
| "What does `_LightTableInterface` look like at runtime?" | This skill + `glyphs-light-table` (cross-ref) |
| "What enum cases exist for GSFontMaster axes?" | This skill (header `typedef enum`) |

## Quick Start Patterns

```bash
# Find a class definition
Grep "@interface GSFont" path/to/Headers/

# Find all properties of a class
Grep "@property" path/to/Headers/GSFont.h

# Find a protocol and its methods
Read path/to/Headers/GlyphsReporterProtocol.h

# Search for an enum or constant
Grep "typedef.*enum" path/to/Headers/ --glob "*.h"

# Find which header declares a method
Grep "drawForegroundForLayer" path/to/Headers/
```

## Protocol Files

Glyphs plugin protocols follow a consistent naming convention:

| Pattern | Example |
|---------|---------|
| `Glyphs*Protocol.h` | `GlyphsReporterProtocol.h`, `GlyphsFilterProtocol.h` |
| `GS*Protocol.h` | `GSAppDelegateProtocol.h`, `GSContentProtocol.h` |

To list all protocols:
```bash
Glob path/to/Headers/*Protocol*.h
```

## Advanced Search

```bash
# Find subclass relationships
Grep "@interface GS\\w+ : " path/to/Headers/

# Find all extern constants
Grep "^extern" path/to/Headers/

# Find category extensions for a class (e.g., GSLayer+*)
Glob path/to/Headers/GSLayer+*.h

# Find delegate/notification patterns
Grep "Notification\|Delegate" path/to/Headers/
```

## Worked workflow — "Find every protocol method a Reporter plugin can implement"

```bash
# 1. Locate the protocol file
Read path/to/Headers/GlyphsReporterProtocol.h

# 2. Filter for @optional vs @required sections
Grep -n "@optional\|@required\|^- " path/to/Headers/GlyphsReporterProtocol.h

# 3. Cross-check with the SDK skill's method classification
#    (glyphs-sdk-reference will categorize protocol/python_helper/python_wrapped)
```

This is the canonical pattern for plugin development: header for the contract, then SDK skill for the Python lifecycle wrapper.

## Worked workflow — "What's the Obj-C type behind GSLayer.paths?"

```bash
# 1. Find the @property declaration
Grep "@property.*paths" path/to/Headers/GSLayer.h

# 2. If the property type is NSArray<X>, find the element type
Grep "@interface GSPath" path/to/Headers/

# 3. Check category extensions for additional methods on the array
Glob path/to/Headers/GSLayer+Path*.h
```

The header tells you the actual class names and method signatures the Python wrapper hides.

## Glyphs-Specific Notes

### Conditional Compilation Guards

About 26 headers contain `#ifndef GLYPHS_LITE` or `#ifndef LIBCORE` guards. Code inside these guards is only available in the full Glyphs 3, not in Glyphs Mini or the core library.

```bash
# Find guarded sections in a header
Grep "GLYPHS_LITE\|LIBCORE" path/to/Headers/GSFont.h
```

When reading a header with these guards, note which APIs are full-version only. This is the most common source of "the Python wrapper has this attribute but I can't find it in the header" confusion.

### Class Categories (Extensions)

Many core classes have functionality split across multiple headers:
- `GSFont.h` + `GSFont+GenerateGlyphs.h` + `GSFont+SerialImport.h` + `GSFont+SerialSave.h`
- `GSLayer.h` + `GSLayer+PathOperations.h` + `GSLayer+Autohinting.h` + ...
- `GSGlyph.h` + `GSGlyph+MetricsKeys.h` + `GSGlyph+TrueTypeCurves.h`

Always check for `ClassName+*.h` extensions when querying a class API. A missing method in the main header is almost always in a category file.

### Selector ↔ Python method mapping

Glyphs' Python bridge follows PyObjC conventions:

| Obj-C selector | Python method |
|---|---|
| `nameForKey:` | `nameForKey_("X")` |
| `font:loadFromPath:options:` | `font_loadFromPath_options_(f, p, o)` |
| `setLayer:forKey:` | `setLayer_forKey_(layer, key)` |

Each `:` becomes `_`. Trailing colon stays. For zero-argument selectors (`init`, `mainFont`), no underscore is added.

## Third-party Plugin APIs (Runtime Only)

Some third-party plugins expose Objective-C classes accessible via runtime introspection (`NSClassFromString`, `objc_getClass`), even without header files.

- **Light Table** (Git version control): Exposes `LightTableInterface`, `LightTableSignature`, `LightTableCommit`, `LightTableRecord`, `LightTableVersion`, `LightTableRestorationInfo`. See the `glyphs-light-table` skill for selector mappings and usage.

## Common edge cases

- **Header path missing** → confirm Glyphs 3 is installed at `/Applications/Glyphs 3.app`; for a non-standard install set `GLYPHS_APP_HEADERS_PATH`.
- **Property appears in Python but not in `.h`** → check category headers (`ClassName+*.h`) and `GLYPHS_LITE` guards before concluding it's runtime-only.
- **Method has no matching protocol** → it may be on a private subclass (no `Protocol.h` declaration). Search the class header directly.
- **Multiple `@interface` blocks for one class** → categories add to the base class; merge all matches before answering.

## Cross-skill collaboration

| Question | Use this skill | Use instead | Reason |
|---|---|---|---|
| "What Obj-C properties does GSFont have?" | ✅ | — | This is the headers' job |
| "What Python attributes does GSFont have?" | — | `glyphs-python-api` | Wrapper surface differs |
| "What's the plugin lifecycle protocol signature?" | ✅ | — | Headers define the contract |
| "How do I implement a Reporter plugin?" | — | `glyphs-sdk-reference` | Lifecycle + template |
| "What's the runtime class of `_LightTableInterface`?" | partial | `glyphs-light-table` | Third-party plugin surface |
| "What's a `GSFormatVersion3` value?" | — | `glyphs-python-api` (constants) | Constant lookups are easier in Python skill |

## Reference

See [references/header-categories.md](references/header-categories.md) for a categorized guide to the 174 headers.
