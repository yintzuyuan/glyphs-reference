# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-XX

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
