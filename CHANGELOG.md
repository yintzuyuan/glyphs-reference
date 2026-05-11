# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
