# Glyphs Web Search — Content Domain Index

Routing map for the 4 official Glyphs web domains, the 460-section handbook, and the 182 custom parameters. Use this to pick the right script before searching.

## Domain map

| Domain | What it covers | Best entry script |
|---|---|---|
| `forum.glyphsapp.com` | Community Q&A, edge-case discussions, workarounds | `search_forum.py` |
| `glyphsapp.com/learn` | Official tutorials and walkthroughs | `search_tutorials.py` |
| `glyphsapp.com/news` | Release notes, beta announcements, version history | `search_news.py` |
| `handbook.glyphsapp.com` | Authoritative user manual (460 sections) | `search_handbook_toc.py` or `search_handbook_fulltext.py` |

For a parallel sweep of all 4 domains in one call, use `search_all.py`.

## Handbook — top-level chapter areas

The handbook splits into roughly these top-level chapter areas (each contains multiple sub-sections; numbers below are illustrative aggregates):

| Chapter area | Topics |
|---|---|
| Getting Started | Installation, licensing, first-run, preferences |
| Font Info | Family / style names, axes, masters, instances, custom parameters |
| Glyph | Naming, Unicode, anchors, categories, smart components |
| Layer | Geometry, masters, brace / bracket layers, alternates |
| Spacing & Kerning | Sidebearings, kerning groups, classes, exceptions |
| Drawing | Path tools, segment editing, transforms |
| Hinting | PS hints, TrueType hints, autohinting |
| Color | Color layers, palettes, COLR / CPAL / SVG / sbix |
| Variable fonts | Axes, virtual masters, intermediate layers, STAT, exports |
| OpenType features | Class syntax, feature code, prefixes, lookups |
| Scripting | Macros, plugins, callbacks, Python API entry |
| Previewing & Testing | Preview window, text rendering, proofing |
| Exporting | OTF, TTF, Variable, UFO, WOFF, plist generation |

Always use `search_handbook_toc.py <keyword>` to discover the exact section paths before fetching.

### TOC vs. fulltext — which handbook script to use

| Goal | Use |
|---|---|
| Find a chapter by name (e.g. "Kerning Window") | `search_handbook_toc.py` |
| Browse what's in the manual | `search_handbook_toc.py` |
| Find instructions for a task (e.g. "how to add component") | `search_handbook_fulltext.py` |
| Find a specific UI element or keyword | `search_handbook_fulltext.py` |

After locating a section, fetch with `fetch_content.py <url>`. Append `document.md` to handbook URLs for clean Markdown:

```
https://handbook.glyphsapp.com/kerning/document.md
```

## Custom parameters — 182 parameters grouped by domain

The Custom Parameters page (105K chars) cannot be fetched directly via `fetch_content.py --full` — it will overflow context. Always use the specialized scripts.

Approximate distribution across parameter scopes (font / master / instance / glyph level):

| Domain | Sample parameters |
|---|---|
| Font naming & metadata | `Add Class`, `Add Feature`, `Add Prefix`, `vendorID`, family name keys |
| Master metrics | `ascender`, `capHeight`, `xHeight`, `descender`, `italicAngle` |
| Hinting (PostScript blue zones) | `blueFuzz`, `blueScale`, `blueShift`, `BlueValues`, `OtherBlues` |
| Hinting (TrueType) | `Autohint`, `Round Stems`, `TTFStub` |
| CJK / grid | `CJK Grid`, `CJK Grid Horizontal`, `CJK Grid Vertical`, `CJK Guide` |
| Color | `Color Layers to COLR`, `Color Layers to SVG`, `Color Palettes`, `Color Palette for CPAL` / `for SVG` |
| OpenType layout | `OS/2 codePageRanges`, `Axis Location`, `Variation Font Origin` |
| Export controls | `Don't use Production Names`, `Remove Glyphs`, `RemoveFeatures` |
| Filters / pipeline | `Filter`, `RemoveOverlap`, `Subroutine Family Identifier` |

Use `search_custom_parameters.py <keyword>` to find parameters by name and `fetch_custom_parameter.py <name>` for the full description of a single parameter.

## Page-size handling

| Page size | Script behavior | Action |
|---|---|---|
| < 10 KB | `fetch_content.py --full` safe | Direct fetch |
| 10–30 KB | Chunked recommended | Use `fetch_content.py` with `--offset` paging |
| > 30 KB | Specialized script needed | Custom Parameters → `search_custom_parameters.py`; handbook → `search_handbook_fulltext.py` |

`fetch_content.py` blocks known-large pages automatically and warns on unknown >30 KB pages. Use `--force` only when explicitly necessary.

## Query intent → script routing

| User intent | Script |
|---|---|
| "How do I do X in Glyphs?" | `search_handbook_fulltext.py` → `fetch_content.py` |
| "What does parameter X mean?" | `fetch_custom_parameter.py "X"` |
| "Is there a script that does X?" | `search_forum.py` + `search_tutorials.py` |
| "What changed in version X.Y?" | `search_news.py "<version>"` |
| "Cross-source overview of topic X" | `search_all.py "X"` |
| "Show the structure of the manual" | `search_handbook_toc.py` |
| "Find a chapter by title" | `search_handbook_toc.py "<title fragment>"` |

## Cross-references to other skills

- **`glyphs-python-api`** — for Python scripting questions, prefer the API skill before searching the forum.
- **`glyphs-sdk-reference`** — for plugin development questions, prefer the SDK skill before searching tutorials.
- **`glyphs-file-format`** — for `.glyphs` file format questions, prefer the file-format skill before searching the handbook.
