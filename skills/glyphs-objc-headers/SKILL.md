---
name: glyphs-objc-headers
description: "Searches GlyphsCore Objective-C header files (174 headers) for class APIs, protocol methods, properties, enums, and constants. Use when looking up GSFont/GSLayer/GSGlyph properties, finding GlyphsReporter or GlyphsFilter protocol methods, or searching Obj-C type definitions for plugin development."
---

# GlyphsCore Obj-C Headers Skill

Query 174 Objective-C header files from the GlyphsCore framework to find class APIs, protocol methods, properties, enums, and constants.

## Headers Path

```
${GLYPHS_APP_HEADERS_PATH:-/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers}
```

If the env var is not set, use the default path above.

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

## Glyphs-Specific Notes

### Conditional Compilation Guards

About 26 headers contain `#ifndef GLYPHS_LITE` or `#ifndef LIBCORE` guards. Code inside these guards is only available in the full Glyphs 3, not in Glyphs Mini or the core library.

```bash
# Find guarded sections in a header
Grep "GLYPHS_LITE\|LIBCORE" path/to/Headers/GSFont.h
```

When reading a header with these guards, note which APIs are full-version only.

### Class Categories (Extensions)

Many core classes have functionality split across multiple headers:
- `GSFont.h` + `GSFont+GenerateGlyphs.h` + `GSFont+SerialImport.h` + `GSFont+SerialSave.h`
- `GSLayer.h` + `GSLayer+PathOperations.h` + `GSLayer+Autohinting.h` + ...
- `GSGlyph.h` + `GSGlyph+MetricsKeys.h` + `GSGlyph+TrueTypeCurves.h`

Always check for `ClassName+*.h` extensions when querying a class API.

## Third-party Plugin APIs (Runtime Only)

Some third-party plugins expose Objective-C classes accessible via runtime introspection (`NSClassFromString`, `objc_getClass`), even without header files.

- **Light Table** (Git version control): Exposes `LightTableInterface`, `LightTableSignature`, `LightTableCommit`, `LightTableRecord`, `LightTableVersion`, `LightTableRestorationInfo`. See the `glyphs-light-table` skill for selector mappings and usage.

## Reference

See [references/header-categories.md](references/header-categories.md) for a categorized guide to the 174 headers.
