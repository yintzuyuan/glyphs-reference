---
name: glyphs-web-search
description: "Searches Glyphs official web resources including forum discussions, tutorials, handbook, and release news with progressive content loading. Use when searching the Glyphs forum, finding tutorials, looking up handbook entries, querying custom parameters, or fetching release notes from glyphsapp.com."
---

# Glyphs Web Search

Search Glyphs official resources with progressive content loading.

## Scripts

> Run all scripts from this skill's base directory. Prepend the base directory path to `scripts/` when executing.

| Script | Purpose | Output |
|--------|---------|--------|
| `search_forum.py` | Forum discussions | Title + URL + replies |
| `search_tutorials.py` | Official tutorials | Title + URL |
| `search_news.py` | Release news | Title + URL |
| `search_handbook_toc.py` | Handbook chapters | Title + URL (460 sections) |
| `search_handbook_fulltext.py` | Handbook content | Title + URL + context |
| `search_all.py` | All sources | Combined (concurrent) |
| `fetch_content.py` | Page content | Text chunks + pagination |
| `search_custom_parameters.py` | Custom Parameters index | 182 parameters searchable |
| `fetch_custom_parameter.py` | Parameter details | Full description by name |

## Usage

### Quick Search (All Sources)

```bash
python scripts/search_all.py "variable font"
```

### Individual Search

```bash
python scripts/search_forum.py "kerning"
python scripts/search_tutorials.py "opentype"
python scripts/search_news.py "released"
```

### Handbook Search

```bash
# Browse chapter structure (titles/paths)
python scripts/search_handbook_toc.py "kerning"

# Search page content (fulltext)
python scripts/search_handbook_fulltext.py "add component"
```

**When to use which:**

| Use Case | Script |
|----------|--------|
| Find a chapter by name | `search_handbook_toc.py` |
| Find how to do something | `search_handbook_fulltext.py` |
| Browse handbook structure | `search_handbook_toc.py` |
| Find specific instructions | `search_handbook_fulltext.py` |

### Custom Parameters (Special Handling)

The Custom Parameters page (105K chars, 182 parameters) requires special handling to avoid context overflow.

```bash
# List all parameters (names only)
python scripts/search_custom_parameters.py

# Search by keyword
python scripts/search_custom_parameters.py "blue"

# Search with descriptions (truncated)
python scripts/search_custom_parameters.py "hinting" --detail

# Get full details for specific parameter
python scripts/fetch_custom_parameter.py "blueScale"

# Fuzzy match multiple parameters
python scripts/fetch_custom_parameter.py "Color" --fuzzy
```

**Workflow for Custom Parameters:**

```
User: "What does blueScale do?"

1. Direct lookup:
   $ python scripts/fetch_custom_parameter.py "blueScale"
   → Full description

User: "What parameters are related to color?"

1. Search parameters:
   $ python scripts/search_custom_parameters.py "color" --detail
   → 11 matching parameters with descriptions
```

⚠️ **Never use `fetch_content.py --full` on Custom Parameters page** - it will overflow context.

### Fetch Content

```bash
# First 3000 chars
python scripts/fetch_content.py <url>

# Continue from offset
python scripts/fetch_content.py <url> --offset 3000

# Full content (use sparingly, NOT for Custom Parameters)
python scripts/fetch_content.py <url> --full
```

**Handbook tip:** Append `document.md` to URL for clean Markdown:
```
https://handbook.glyphsapp.com/kerning/document.md
```

## Large Page Handling Strategy

| Page Size | Strategy |
|-----------|----------|
| < 10K chars | `fetch_content.py --full` OK |
| 10K-30K chars | Use chunked loading with offset |
| > 30K chars | Use specialized scripts (e.g., `search_custom_parameters.py`) |

### Automatic Protection

`fetch_content.py` includes built-in protection:

1. **Known large pages** (e.g., Custom Parameters): Automatically blocked with redirect to specialized script
2. **Unknown large pages** (>30K chars): Warning when using `--full` flag
3. **Bypass**: Use `--force` flag (not recommended)

```bash
# This will show warning and suggest search_custom_parameters.py
python scripts/fetch_content.py "https://handbook.glyphsapp.com/custom-parameter-descriptions/"

# Force bypass (use with caution)
python scripts/fetch_content.py "..." --full --force
```

## Workflow Example

```
User: "How do I add components?"

1. Fulltext search (finds instructions):
   $ python scripts/search_handbook_fulltext.py "add component"
   → Building Composites, Batch Commands

2. Fetch content:
   $ python scripts/fetch_content.py "https://handbook.../components/document.md"
```

## Requirements

```bash
pip install httpx --break-system-packages
```

## Network Domains

- `forum.glyphsapp.com`
- `glyphsapp.com/learn`
- `glyphsapp.com/news`
- `handbook.glyphsapp.com`

## Additional Resources

- **`references/content-index.md`** — Domain map across the 4 web sources, handbook chapter-area overview (drives `search_handbook_toc.py` vs `search_handbook_fulltext.py` choice), custom-parameter groupings (~10 domains), page-size handling thresholds, and a query-intent → script routing table. Read this first to pick the right script for ambiguous queries.
