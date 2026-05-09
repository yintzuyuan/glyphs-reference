---
name: glyphs-packages
description: "Searches Glyphs plugins, scripts, and Python modules across local installations and the official registry. Inspects package internals (bundle structure, entry points, source files). Use when finding available scripts, checking installed plugins, browsing the Glyphs plugin registry, inspecting how a package works, or looking up package details for Glyphs development."
---

# Glyphs Packages Skill

Search and browse Glyphs plugins, scripts, and Python modules across local installations and the official registry.

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

## Path Resolution

```
SCRIPTS=${GLYPHS_SCRIPTS_PATH:-~/Library/Application Support/Glyphs 3/Scripts}
PLUGINS=${GLYPHS_PLUGINS_PATH:-~/Library/Application Support/Glyphs 3/Plugins}
REPOS=${GLYPHS_REPOSITORIES_PATH:-~/Library/Application Support/Glyphs 3/Repositories}
```

Three-layer architecture:
- **`Repositories/`** — All installed packages (git clones, plugins + scripts + modules mixed)
- **`Scripts/`** — Enabled script collections and Python modules (symlinks → Repositories/)
- **`Plugins/`** — Enabled plugin bundles (symlinks → Repositories/*.glyphsPlugin)

## Quick Start: Search Scripts (Scripts/)

```bash
# Search all enabled scripts by MenuTitle
Grep "# MenuTitle:" "$SCRIPTS/" -i

# Search for a specific function
Grep "# MenuTitle:.*anchor" "$SCRIPTS/" -i

# Browse a collection's directory structure
Bash: ls "$SCRIPTS/mekkablue/"

# Read a script for details (docstring = description)
Read "$SCRIPTS/mekkablue/Anchors/Anchor Mover.py"
```

Note: mekkablue is the official, largest script collection. When multiple scripts offer similar functionality, prefer mekkablue's version.

## Quick Start: Check Enabled Plugins (Plugins/)

```bash
# List enabled plugin bundles
Bash: ls "$PLUGINS/"

# Read plugin metadata
Bash: plutil -convert json -o - "$PLUGINS/Name.glyphsPlugin/Contents/Info.plist"

# Find all Reporter-type plugins
Glob "$REPOS/*/*.glyphsReporter"

# Find all Filter-type plugins
Glob "$REPOS/*/*.glyphsFilter"
```

## Quick Start: Explore All Installed Packages (Repositories/)

```bash
# List all installed packages
Bash: ls "$REPOS/"

# Read a package's README
Read "$REPOS/PackageName/README.md"

# Check a package's git remote
Bash: git -C "$REPOS/PackageName" remote -v
```

## Quick Start: Official Registry

Search the official Glyphs package registry (plugins, scripts, modules) hosted on GitHub:

```bash
# Search across all categories
Bash: python3 scripts/search_registry.py --search "anchor"

# List all packages
Bash: python3 scripts/search_registry.py --all

# Filter by category
Bash: python3 scripts/search_registry.py --all --category plugins
Bash: python3 scripts/search_registry.py --all --category scripts
Bash: python3 scripts/search_registry.py --all --category modules

# Filter by plugin type
Bash: python3 scripts/search_registry.py --all --type Reporter
Bash: python3 scripts/search_registry.py --all --type Filter

# Combined search
Bash: python3 scripts/search_registry.py --search "kerning" --category plugins --type Filter
```

Output is JSON array. Each entry: `{title, url, category, description, path?, type?}`

## Inspect Package Internals

Inspect installed packages to understand their structure, language, entry points, and source files:

```bash
# Inspect a specific package (auto-detects type)
Bash: python3 scripts/inspect_package.py "ShowAnchors"

# List all installed packages with their types
Bash: python3 scripts/inspect_package.py --list
```

Output is JSON. Key fields by package type:
- **Python plugin** → `language: "python"`, `entry_file` (path to plugin.py), `has_dialog`
- **ObjC plugin** → `language: "objc"`, `open_source`, `xcodeproj_path`, `source_files`
- **Script collection** → `scripts[]` (menu_title + path), `subdirectories`
- **Module** → `has_setup_py`, `has_pyproject_toml`
- **Any plugin** → `has_python_api` (bool), `python_api_path` — indicates a bundled Python scripting API (e.g., Light Table)

After inspecting, `Read` the entry_file or source_files to understand the implementation.

## Workflow

Choose based on intent:

**Finding a package:**
1. **Local search first** — `Grep "# MenuTitle:" "$SCRIPTS/"` for scripts, `ls "$PLUGINS/"` for plugins
2. **If not found locally** — Search the registry: `python3 scripts/search_registry.py --search "keyword"`
3. **Read details** — `Read` the script file or README for usage instructions

**Understanding how a package works:**
1. **Inspect** — `python3 scripts/inspect_package.py "PackageName"`
2. **Read entry point** — For Python plugins: `Read "$REPOS/Name/{entry_file}"`; for scripts: `Read "$REPOS/Name/{scripts[].path}"`
3. **Dive deeper** — For ObjC open-source: `Read` the `.h`/`.m` files listed in `source_files`

**Looking up plugin development APIs:**
→ Use the `glyphs-sdk-reference` or `glyphs-python-api` skills for API reference and development patterns.

## Reference

See [references/repository-guide.md](references/repository-guide.md) for package structure details, bundle internals, and search strategies.
