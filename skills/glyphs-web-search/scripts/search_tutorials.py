#!/usr/bin/env python3
"""Search Glyphs official tutorials.

Usage:
    python search_tutorials.py <query> [--limit N]

Examples:
    python search_tutorials.py "kerning"
    python search_tutorials.py "variable font" --limit 10

Output:
    Lightweight list of tutorials (~2KB) with title and URL.
    Use fetch_content.py to get detailed content of specific tutorials.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_html

TUTORIALS_URL = "https://glyphsapp.com/learn"


def search_tutorials(query: str, limit: int = 20) -> str:
    """Search tutorials and return formatted results list."""
    
    search_url = f"{TUTORIALS_URL}?q={query.replace(' ', '+')}"
    
    try:
        html = fetch_html(search_url)
    except Exception as e:
        return f"""## ❌ Tutorial Search Error

{e}

**Manual search**: {search_url}
"""

    # Parse tutorial links from HTML
    results = []
    seen = set()
    
    # Pattern 1: Standard href links
    pattern1 = r'href="(https://glyphsapp\.com/learn/[^"]+)"[^>]*>([^<]+)</a>'
    for url, title in re.findall(pattern1, html):
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        if url not in seen and clean_title:
            seen.add(url)
            results.append({"title": clean_title, "url": url})
    
    # Pattern 2: Relative URLs
    pattern2 = r'href="(/learn/[^"]+)"[^>]*>([^<]+)</a>'
    for path, title in re.findall(pattern2, html):
        url = f"https://glyphsapp.com{path}"
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        if url not in seen and clean_title:
            seen.add(url)
            results.append({"title": clean_title, "url": url})
    
    # Filter and limit
    # Remove generic navigation links
    results = [
        r for r in results 
        if r["title"].lower() not in ("learn", "tutorials", "view all", "next", "previous")
        and len(r["title"]) > 2
    ][:limit]
    
    # Format output
    if not results:
        return f"""## 📖 Tutorial Search: "{query}"

No tutorials found.

**Suggestions**:
- Try different English keywords
- Browse all tutorials: {TUTORIALS_URL}
- Search forum: `search_forum.py "{query}"`
"""
    
    lines = [
        f'## 📖 Tutorial Search: "{query}"',
        f"Found {len(results)} tutorials\n",
    ]
    
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['title']}**")
        lines.append(f"   {r['url']}")
        lines.append("")
    
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read specific tutorial")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs tutorials")
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    result = search_tutorials(query, args.limit)
    print(result)


if __name__ == "__main__":
    main()
