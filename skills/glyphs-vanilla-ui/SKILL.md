---
name: glyphs-vanilla-ui
description: "Queries Vanilla GUI library (schriftgestalt/vanilla fork) for Glyphs 3 plugin UI development. Use when building plugin UIs with windows, buttons, text fields, or lists, finding available Vanilla components, or looking up component APIs like Window, List2, or PopUpButton parameters."
---

# Vanilla GUI Library Skill

Query the Vanilla GUI library (schriftgestalt/vanilla fork) used by Glyphs 3 for building plugin UIs — windows, buttons, text fields, lists, and more.

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

## Vanilla Path

```
${GLYPHS_VANILLA_PATH:-~/Library/Application Support/Glyphs 3/Repositories/vanilla/Lib/vanilla}
```

If `GLYPHS_VANILLA_PATH` is not set, try `GLYPHS_REPOSITORIES_PATH/vanilla/Lib/vanilla`, then the default path above.

## Quick Start: Browse All Components

Read `__init__.py` (≈107 lines) to see every exported class and which module it comes from:

```bash
Read $VANILLA/__init__.py
```

This shows all `from vanilla.moduleName import ClassName` lines — the complete component inventory.

## Quick Start: Read a Component

For multi-class files (vanillaWindows.py, vanillaList2.py, etc.), use the script to extract a single class:

```bash
python3 scripts/read_component.py Button                # Full: source + docstring + methods
python3 scripts/read_component.py Window --summary      # Summary: methods list (no source)
```

For single-class files (vanillaCheckBox.py, vanillaSlider.py, etc.), just Read directly:

```bash
Read $VANILLA/vanillaCheckBox.py
```

## Quick Start: Search Components

```bash
# Find a component by keyword
Grep "class.*Button" $VANILLA/

# Find all classes in a module
Grep "^class " $VANILLA/vanillaWindows.py

# Find usage of a specific method
Grep "def setTitle" $VANILLA/
```

## Quick Start: Official Documentation

Fetch component docs from the vanilla website:

```
WebFetch https://vanilla.robotools.dev/en/latest/objects/{ComponentName}.html
```

Replace `{ComponentName}` with the actual class name (e.g., `Button`, `Window`, `List2`).

## Glyphs-Specific Notes

### Palette Plugins Use Group, Not Window

Palette plugins receive a `Group` as their container — never create a `Window` inside a palette. Use `Group` with embedded controls.

### posSize Convention

All Vanilla components use `posSize = (left, top, width, height)`:
- Use `"auto"` for Auto Layout managed dimensions
- Negative values for `width`/`height` mean "from right/bottom edge"

### Auto Layout

Use `VerticalStackView` and `HorizontalStackView` for modern Auto Layout UIs instead of manual `posSize` positioning.

### GridView

`GridView` is conditionally imported (requires macOS 10.12+). It appears in a try/except block at the bottom of `__init__.py`.

## Common Workflow

1. **Find component** → `Read $VANILLA/__init__.py` to browse all exports
2. **Read API** → `python3 scripts/read_component.py ComponentName` for details
3. **Check docs** → `WebFetch https://vanilla.robotools.dev/en/latest/objects/ComponentName.html`
4. **Search patterns** → `Grep "pattern" $VANILLA/` for usage examples

## Reference

See [references/component-categories.md](references/component-categories.md) for categorized component guide.
