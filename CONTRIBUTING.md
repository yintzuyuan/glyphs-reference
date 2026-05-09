# Contributing to glyphs-reference

Thanks for your interest in contributing.

## Quick start

```bash
git clone --recurse-submodules https://github.com/yintzuyuan/glyphs-reference.git
cd glyphs-reference
```

The `GlyphsSDK` submodule is required for `glyphs-sdk-reference` skill tests.

## Reporting issues

For bugs / feature requests, please open a [GitHub Issue](https://github.com/yintzuyuan/glyphs-reference/issues) with:

- Which skill (or agent) is affected
- Expected vs actual behavior
- Reproducible example (if applicable)
- Claude Code version

## Pull requests

PRs welcome — small targeted improvements preferred over large refactors.

### Skill authoring

Each skill follows Anthropic's [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

- `SKILL.md` body < 500 lines (concise; only context Claude doesn't already have)
- `description` in frontmatter is third-person, includes both **what** and **when triggers**, max 1024 chars
- Progressive disclosure — references one level deep; scripts execute (only output consumes tokens)
- Scripts handle errors directly (solve, don't punt to Claude)
- Avoid hardcoding translations, API responses, or any data that may change over time

### Tests

Tests live alongside each skill:

```
skills/<skill-name>/tests/
  conftest.py
  test_*.py
```

Run with `pytest skills/<skill-name>/tests/` from repo root.

For `glyphs-sdk-reference` tests, ensure `GlyphsSDK` submodule is initialized.

## Maintainer SLA

This is a personal open-source project maintained by [TzuYuan Yin](mailto:yintzuyuan@erikyin.net) on best-effort basis. Critical bugs typically addressed within a few weeks; non-urgent improvements may take longer.

## Code of Conduct

Be kind, be specific, be patient.
