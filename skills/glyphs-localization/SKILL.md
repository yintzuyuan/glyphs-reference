---
name: glyphs-localization
description: "Translates Glyphs 3 UI terms between 14 languages using Hub-and-Spoke architecture via English. Use when translating Glyphs menu items, finding localized UI strings for plugin development, or looking up how a feature is named in another language."
---

# Glyphs UI Localization Skill

Translate Glyphs 3 UI terms between 14 languages using Hub-and-Spoke architecture.

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

## Quick Start

```bash
# Auto-translate to English (from any language)
./scripts/translate-term.sh "取消"

# Translate to specific locale
./scripts/translate-term.sh "Cancel" "zh-Hant"

# Cross-language (goes through English hub)
./scripts/translate-term.sh "移除重疊" "ja"

# Rebuild cache after Glyphs update
./scripts/translate-term.sh --rebuild

# List available locales
./scripts/translate-term.sh --list-locales
```

## Output Format

```
key: Remove Overlap
source: en
target: zh-Hant
translation: 移除重疊
```

Simple key-value format for easy parsing.

## Supported Languages

See [references/language-codes.md](references/language-codes.md) for complete list.

Common locales: `en`, `zh-Hant`, `zh-Hans`, `ja`, `ko`, `de`, `fr`, `es`

## Architecture

**Hub-and-Spoke**: All translations go through English as the hub language.

```
zh-Hant → en → ja
         ↑
       (hub)
```

**Three-tier search**:
1. Main App: `/Applications/Glyphs 3.app/Contents/Resources/{lang}.lproj/`
2. Framework: `.../Frameworks/GlyphsCore.framework/.../Resources/{lang}.lproj/`
3. Plugins: `.../PlugIns/*/.../Resources/{lang}.lproj/`

**NIB integration**: English vocabulary includes terms from Base.lproj NIB files.

## Cache

Cache stored at `/tmp/glyphs-vocab-cache/`. Auto-builds on first use.

Rebuild after Glyphs update:
```bash
./scripts/translate-term.sh --rebuild
```

## Other Tools

### search-glyphs-term.sh

Raw grep search for debugging:

```bash
./scripts/search-glyphs-term.sh "Remove Overlap" "zh-Hant"
./scripts/search-glyphs-term.sh --all-langs "Remove Overlap"
./scripts/search-glyphs-term.sh --format json "Filter" "ja"
```

### extract-nib-strings.sh

Extract strings from NIB files:

```bash
./scripts/extract-nib-strings.sh --term "Remove Overlap"
./scripts/extract-nib-strings.sh --lang zh-Hant --format csv
```
