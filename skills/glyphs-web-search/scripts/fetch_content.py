#!/usr/bin/env python3
"""Fetch URL content with chunked loading support.

Usage:
    python fetch_content.py <url>                     # First 3000 chars
    python fetch_content.py <url> --offset 3000      # Continue from offset
    python fetch_content.py <url> --limit 5000       # Custom chunk size
    python fetch_content.py <url> --full             # Full content (use sparingly)

Examples:
    python fetch_content.py "https://forum.glyphsapp.com/t/topic/12345"
    python fetch_content.py "https://glyphsapp.com/learn/kerning"
    python fetch_content.py "https://glyphsapp.com/news/glyphs-3-3-released" --full

Output:
    Content chunk with pagination info.
    Shows remaining chars and command to continue reading.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_html, html_to_text, chunk_content

DEFAULT_LIMIT = 3000

# Large pages with specialized scripts
# Format: { url_pattern: (page_name, script_name, description) }
LARGE_PAGE_HANDLERS = {
    "custom-parameter-descriptions": (
        "Custom Parameters",
        "search_custom_parameters.py",
        "182 parameters, 105K+ chars"
    ),
}

# Threshold for warning about large pages (chars)
LARGE_PAGE_THRESHOLD = 30000


def check_large_page(url: str) -> tuple[str, str, str] | None:
    """Check if URL matches a known large page with specialized handler."""
    for pattern, handler_info in LARGE_PAGE_HANDLERS.items():
        if pattern in url:
            return handler_info
    return None


def fetch_content(
    url: str, 
    offset: int = 0, 
    limit: int = DEFAULT_LIMIT, 
    full: bool = False,
    force: bool = False
) -> str:
    """Fetch URL content with optional chunking."""
    
    # Validate URL
    if not url.startswith(("http://", "https://")):
        return "❌ Error: Please provide a complete URL (including https://)"
    
    # Check for known large pages with specialized handlers
    handler = check_large_page(url)
    if handler and not force:
        page_name, script_name, description = handler
        return f"""## ⚠️ Large Page Detected: {page_name}

**URL**: {url}
**Size**: {description}

This page has a specialized search script for efficient querying.

### Recommended Usage

```bash
# Search parameters by keyword
python scripts/{script_name} "keyword"

# Search with descriptions
python scripts/{script_name} "keyword" --detail

# Get specific parameter details
python scripts/fetch_custom_parameter.py "parameterName"
```

### Why?

Loading this entire page ({description}) would overflow the context window.
The specialized script parses the page and returns only relevant results.

---
💡 Use `--force` flag to bypass this warning (not recommended).
"""
    
    try:
        html = fetch_html(url)
        text = html_to_text(html)
    except Exception as e:
        return f"""## ❌ Fetch Error

{e}

**Try visiting directly**: {url}
"""

    total_chars = len(text)
    
    # Warning for unknown large pages
    if total_chars > LARGE_PAGE_THRESHOLD and full and not force:
        return f"""## ⚠️ Large Page Warning

**URL**: {url}
**Size**: {total_chars:,} chars (>{LARGE_PAGE_THRESHOLD:,} threshold)

Using `--full` on this page may overflow context.

### Recommended Actions

1. **Use chunked loading** (default behavior):
   ```bash
   python scripts/fetch_content.py "{url}"
   python scripts/fetch_content.py "{url}" --offset 3000
   ```

2. **Or force full load** (use with caution):
   ```bash
   python scripts/fetch_content.py "{url}" --full --force
   ```

---
📖 First {DEFAULT_LIMIT:,} chars preview available without --full flag.
"""
    
    # Full content mode
    if full:
        return f"""## 📄 Content ({total_chars:,} chars)
**Source**: {url}

{text}

---
✅ Full content displayed
"""
    
    # Chunked mode
    result = chunk_content(text, offset, limit)
    
    # Build output
    start = result["offset"] + 1
    end = result["offset"] + len(result["content"])
    
    lines = [
        f"## 📄 Content (chars {start:,}-{end:,} of {total_chars:,})",
        f"**Source**: {url}\n",
        result["content"],
    ]
    
    # Pagination info
    lines.append("\n---")
    
    if result["has_more"]:
        remaining = total_chars - result["next_offset"]
        lines.append(f"📖 **{remaining:,} chars remaining**")
        lines.append(f"➡️ Continue: `fetch_content.py \"{url}\" --offset {result['next_offset']}`")
        
        # Add warning for very large pages
        if total_chars > LARGE_PAGE_THRESHOLD:
            lines.append(f"\n⚠️ Large page ({total_chars:,} chars). Consider if full content is needed.")
    else:
        lines.append("✅ **Content complete**")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch URL content with chunked loading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://forum.glyphsapp.com/t/topic/12345"
  %(prog)s "https://glyphsapp.com/learn/kerning" --offset 3000
  %(prog)s "https://glyphsapp.com/news/glyphs-3-3-released" --full
        """
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--offset", 
        type=int, 
        default=0, 
        help=f"Start position in chars (default: 0)"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=DEFAULT_LIMIT, 
        help=f"Max chars per chunk (default: {DEFAULT_LIMIT})"
    )
    parser.add_argument(
        "--full", 
        action="store_true", 
        help="Fetch full content (use sparingly for large pages)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass large page warnings (use with caution)"
    )
    
    args = parser.parse_args()
    
    result = fetch_content(
        args.url, 
        offset=args.offset, 
        limit=args.limit, 
        full=args.full,
        force=args.force
    )
    print(result)


if __name__ == "__main__":
    main()
