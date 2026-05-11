# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-12

### Added

- `plugin.json` — `homepage` field pointing to `https://erikyin.net/glyphs-reference/`.
- `skills/glyphs-python-api/references/class-index.md` — index of 35 classes (grouped by domain), 16 standalone functions (5 categories), and 133 constants (12 categories).
- `skills/glyphs-sdk-reference/references/template-catalog.md` — catalog of 7 plugin base classes with method counts, 9 Python Templates, and 6+ Samples; includes method-type classification rules.
- `skills/glyphs-web-search/references/content-index.md` — domain map for the 4 official web sources, handbook chapter-area overview, custom-parameter groupings (~10 domains), and a query-intent → script routing table.

### Changed

- `agents/glyphs-meta-search.md` — restructured as a **meta-dispatcher**:
  - `model: sonnet` → `model: inherit`.
  - `description` expanded to 3 `<example>` blocks with `<commentary>` (including a counter-example showing when *not* to use the agent).
  - System prompt now leads with a routing matrix (query type → skills to consult) instead of duplicating skill-level search logic.
  - `$GLYPHS_SDK_PATH` resolution now documents a `${CLAUDE_PLUGIN_ROOT}/GlyphsSDK/` fallback.
- `skills/glyphs-file-format/SKILL.md` — expanded with worked workflow, v2/v3 migration table, edge cases, and cross-skill matrix (328 → 985 words).
- `skills/glyphs-light-table/SKILL.md` — added concept tables (`DocumentState` vs `ObjectStatus`, restoration vs version load), two worked workflows, edge cases, and cross-skill matrix (317 → 895 words).
- `skills/glyphs-objc-headers/SKILL.md` — added "this skill vs. Python skill" decision table, two worked workflows, selector ↔ Python mapping, edge cases, and cross-skill matrix (381 → 935 words).
- `skills/glyphs-remote-scripts/SKILL.md` — added "remote vs in-Glyphs" decision table, two worked workflows, Obj-C selector translation table, edge cases, and cross-skill matrix (436 → 925 words).
- `plugin.json` — removed redundant `"agents": "./agents"` (auto-discovery covers this).

## [1.0.1] - 2026-05-11

### Changed

- Translated remaining Chinese content to English for the public release:
  - `agents/glyphs-meta-search.md` — full agent system prompt translated.
  - `.claude-plugin/plugin.json` — `description` field translated.
  - `skills/glyphs-objc-headers/references/header-categories.md` — category guide translated.
  - `skills/glyphs-vanilla-ui/references/component-categories.md` — component guide translated.
  - `skills/glyphs-packages/references/repository-guide.md` — repository structure guide translated.
  - `skills/glyphs-localization/scripts/translate-term.sh` — usage comment translated.
- Preserved intentional Chinese: `README.zh-TW.md`, bilingual `docs/` landing page, Unicode test fixtures, native language names in `language-codes.md`, and the localization skill's own translation examples.

## [1.0.0] - 2026-05-09

### Added

- Initial public release of `glyphs-reference` plugin.
- 10 Skills covering Glyphs.app documentation:
  - `glyphs-python-api` — Python scripting API reference
  - `glyphs-objc-headers` — Objective-C plugin headers
  - `glyphs-sdk-reference` — Plugin SDK reference, templates, samples
  - `glyphs-vanilla-ui` — Vanilla UI library
  - `glyphs-file-format` — `.glyphs` / `.glyphspackage` format
  - `glyphs-light-table` — Light Table extension API
  - `glyphs-localization` — Glyphs localization data
  - `glyphs-packages` — Package management
  - `glyphs-remote-scripts` — Remote script API
  - `glyphs-web-search` — Glyphs handbook web search
- Meta-search agent at `agents/glyphs-meta-search.md`
- `GlyphsSDK` submodule for `glyphs-sdk-reference` skill

### Migration

- Public successor to legacy [`glyphs-info-mcp`](https://github.com/yintzuyuan/glyphs-info-mcp) MCP server.
- ~98% lower token usage via Skills progressive disclosure.
- Original MCP enters maintenance mode; new users should install this plugin instead.

### Infrastructure

- `tests/conftest.py` for `glyphs-sdk-reference` uses deployment-aware path resolution
  (supports both standalone repo layout and marketplace-embedded layout, with `GLYPHS_SDK_PATH` env var override).
