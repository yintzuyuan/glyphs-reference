# Glyphs Packages Structure Guide

## Table of Contents

- [Three-Tier Directory Layout](#three-tier-directory-layout)
- [Plugin Bundle Internals](#plugin-bundle-internals)
- [Script Collections](#script-collections)
- [Python Modules](#python-modules)
- [Official Registry](#official-registry)
- [Search Strategy](#search-strategy)

## Three-Tier Directory Layout

```
~/Library/Application Support/Glyphs 3/
├── Repositories/   ← every installed package (git clone, plugins + scripts + modules mixed)
├── Scripts/        ← enabled script collections + Python modules (symlinks → Repositories/)
└── Plugins/        ← enabled plugin bundles (symlinks → Repositories/*.glyphsPlugin)
```

- **Repositories/** is the full install directory containing every package installed via Plugin Manager
- **Scripts/** and **Plugins/** are the directories Glyphs actually loads from; their contents are symlinks pointing into Repositories/
- Enabling / disabling a package = creating / removing a symlink

## Plugin Bundle Internals

Plugins are macOS bundle directories. The extension indicates the type:

| Extension | Type | Purpose |
|-----------|------|---------|
| `.glyphsReporter` | Reporter | Overlay visual information in the edit view |
| `.glyphsFilter` | Filter | Batch path operations (round corners, offset, etc.) |
| `.glyphsPalette` | Palette | Side-panel UI |
| `.glyphsTool` | Tool | Custom drawing tools |
| `.glyphsPlugin` | General | General-purpose plugin |
| `.glyphsFileFormat` | FileFormat | Custom file format import / export |

### Python plugins (Info.plist has `PyMainFileNames`)

```
Name.glyphsReporter/
├── Contents/
│   ├── Info.plist          ← NSPrincipalClass + PyMainFileNames
│   ├── MacOS/plugin        ← binary stub (loads Python runtime)
│   └── Resources/
│       ├── plugin.py       ← Python entry point ✅ directly readable
│       ├── IBdialog.xib    ← UI definition (only when the plugin has a dialog)
│       └── IBdialog.nib    ← compiled UI
```

### Obj-C plugins (Info.plist has no `PyMainFileNames`)

```
Name.glyphsPlugin/
├── Contents/
│   ├── Info.plist          ← NSPrincipalClass (no PyMainFileNames)
│   ├── MacOS/Name          ← compiled binary ❌ not readable
│   └── Resources/
│       ├── *.nib           ← compiled UI
│       └── *.lproj/        ← localized resources
```

Source code is not inside the bundle. Search `Repositories/` for an `.xcodeproj` instead:
- `.xcodeproj` present → open source; `.h` / `.m` files live nearby
- `.xcodeproj` absent → closed source; only the compiled bundle is available

### Detecting the language

1. Info.plist has a `PyMainFileNames` key → **Python**, entry point at `Contents/Resources/plugin.py`
2. Info.plist has no `PyMainFileNames` key → **Obj-C**, bundle contents are compiled binaries

### Locating Obj-C source (`.xcodeproj` anchor method)

Three repository layout patterns observed in the wild:

```
# Pattern A: sources in a custom subdirectory
speedpunk/GlyphsSource/SpeedPunk.xcodeproj
speedpunk/GlyphsSource/SpeedPunk/{.h, .m}

# Pattern B: sources next to the .xcodeproj
GutenTag/Guten Tag.xcodeproj
GutenTag/Guten Tag/{.h, .m, ...}

# Pattern C: deeply nested
ShowAngledHandles/ShowAngledHandles/ShowAngledHandles.xcodeproj
ShowAngledHandles/ShowAngledHandles/ShowAngledHandles/{.h, .m}
```

Algorithm: locate the `.xcodeproj`, then search its parent directory for `.h` / `.m` files.

**Read plugin metadata**:
```bash
plutil -convert json -o - "Name.glyphsPlugin/Contents/Info.plist"
```

## Script Collections

A script collection is a directory of `.py` files:

### Convention

- Grouped into subdirectories by purpose (Anchors/, Components/, Paths/, etc.)
- Subdirectory names use capitalized English feature names
- Each `.py` file is a standalone script

### Script format

Every script has:
- A `# MenuTitle:` line — the name shown in the Glyphs Script menu (**required**)
- A `__doc__` string — script description (optional, used by Plugin Manager)
- Standard Python script structure with access to the Glyphs Python API

**Discover scripts**:
```bash
Grep "# MenuTitle:" "$SCRIPTS/"
```

## Python Modules

Python module packages (fonttools, vanilla, etc.). Identified by `setup.py` or `pyproject.toml`:
```bash
Glob "$REPOS/*/setup.py"
Glob "$REPOS/*/pyproject.toml"
```

## Official Registry

Three category-specific ASCII plist files hosted on GitHub:
- **plugins** — plugin bundles (Reporter, Filter, Palette, Tool, etc.)
- **scripts** — script collections (mekkablue is the largest official collection)
- **modules** — Python modules (fonttools, vanilla, robofab, etc.)

Query with the `search_registry.py` script (which uses `plutil -convert json` under the hood).

## Search Strategy

| Query intent | Best directory | Tool |
|--------------|---------------|------|
| Find a script for a specific feature | Scripts/ | `Grep "# MenuTitle:.*keyword"` |
| List currently enabled plugins | Plugins/ | `ls` |
| Browse every installed package | Repositories/ | `ls` |
| Inspect a plugin in detail | Repositories/ | `inspect_package.py "Name"` |
| Deep dive into a package | Repositories/ | `inspect_package.py "Name"` → `Read` the entry file based on the result |
| Find packages not yet installed | Registry | `search_registry.py --search "keyword"` |
| Browse by plugin type | Registry | `search_registry.py --all --type Reporter` |
