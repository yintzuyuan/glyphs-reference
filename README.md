**English** | [繁體中文](README.zh-TW.md)

# glyphs-reference

A Claude Code plugin providing 10 Skills covering Glyphs.app documentation: Python/Obj-C API, file format, SDK reference, Vanilla UI, packages, localization, and web search.

> Replaces the legacy [`glyphs-info-mcp`](https://github.com/yintzuyuan/glyphs-info-mcp) MCP server with ~98% lower token usage via Claude's Skills progressive disclosure.

## What's inside

| Skill | Covers |
|-------|--------|
| `glyphs-python-api` | Python scripting API reference |
| `glyphs-objc-headers` | Objective-C plugin headers |
| `glyphs-sdk-reference` | Plugin SDK reference, templates, and samples |
| `glyphs-vanilla-ui` | Vanilla UI library (used in Glyphs plugin UI) |
| `glyphs-file-format` | `.glyphs` / `.glyphspackage` format spec |
| `glyphs-light-table` | Light Table extension API |
| `glyphs-localization` | Glyphs localization data and language codes |
| `glyphs-packages` | Package management workflows |
| `glyphs-remote-scripts` | Remote script API reference |
| `glyphs-web-search` | Glyphs handbook web search |

Plus a meta-search agent (`agents/glyphs-meta-search.md`) for cross-skill queries.

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed
- macOS (for Glyphs.app development workflows)
- Optional: [`GlyphsSDK`](https://github.com/schriftgestalt/GlyphsSDK) — included as a submodule for `glyphs-sdk-reference`

## Installation

### Direct from this repo (recommended for individual use)

Clone with submodules to get GlyphsSDK:

```bash
git clone --recurse-submodules https://github.com/yintzuyuan/glyphs-reference.git
```

Or if already cloned without submodules:

```bash
git submodule update --init --recursive
```

Then point Claude Code at the cloned directory as a local plugin source.

### Via custom marketplace

If you maintain your own Claude Code plugin marketplace, you can reference this repo as a submodule under your marketplace's `plugins/` directory and consume it through your usual marketplace workflow.

A dedicated public marketplace for this plugin is not yet published; if usage warrants, one may be added later.

## Migration from glyphs-info-mcp

If you previously used [`glyphs-info-mcp`](https://github.com/yintzuyuan/glyphs-info-mcp) (the MCP server):

- The MCP is in **maintenance mode**; this plugin is the recommended path forward
- Same data, ~98% lower token usage via Skills progressive disclosure
- Migration steps:
  1. Remove `glyphs-info-mcp` entry from your `claude_desktop_config.json` (or unset its activation in your environment)
  2. Install this plugin (see Installation above)
  3. The skills are auto-discovered; no manual configuration needed

## Why Skills over MCP?

The original `glyphs-info-mcp` was a stdio MCP server. Every Claude Code session would eager-load all 150K+ tokens of API documentation, regardless of whether the user actually queried Glyphs APIs.

Skills with progressive disclosure load only what's needed: ~2K tokens of skill descriptions upfront, full content fetched on demand. For typical sessions, this saves about 98% of token budget.

This mirrors Anthropic's published rationale for progressive disclosure: "loading all tool definitions upfront and passing intermediate results through the context window slows down agents and increases costs" ([Anthropic engineering blog: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)). Their reference example reports a reduction from 150,000 to 2,000 tokens — about 98.7%.

## Contributing

PRs and issues welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- Glyphs SDK by [Schriftgestaltung GbR](https://glyphsapp.com/)
- Inspired by Anthropic's [progressive disclosure design](https://www.anthropic.com/engineering/code-execution-with-mcp)
- Built with [Claude Code](https://docs.claude.com/en/docs/claude-code)
