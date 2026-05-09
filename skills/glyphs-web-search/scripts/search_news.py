#!/usr/bin/env python3
"""Search Glyphs official news and release announcements.

Usage:
    python search_news.py <query> [--limit N]

Examples:
    python search_news.py "released"
    python search_news.py "glyphs 3.3"
    python search_news.py "plugin" --limit 10

Output:
    Lightweight list of news posts (~2KB) with title, URL, and type.
    Use fetch_content.py to get detailed content of specific posts.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_html, url_to_title

NEWS_URL = "https://glyphsapp.com/news"


def classify_post(url: str) -> str:
    """Classify post type based on URL."""
    url_lower = url.lower()
    
    if "glyphs-" in url_lower and "released" in url_lower:
        if "mini" in url_lower:
            return "Glyphs Mini release"
        return "Glyphs release"
    elif "released" in url_lower:
        return "Plugin/Tool release"
    elif "interview" in url_lower:
        return "Interview"
    elif "tutorial" in url_lower or "tip" in url_lower:
        return "Tutorial"
    else:
        return "News"


def search_news(query: str, limit: int = 20) -> str:
    """Search news and return formatted results list."""
    
    try:
        html = fetch_html(NEWS_URL)
    except Exception as e:
        return f"""## ❌ News Search Error

{e}

**Manual search**: {NEWS_URL}
"""

    # Parse news links from HTML
    results = []
    seen = set()
    query_lower = query.lower()
    
    # Find all news URLs
    pattern = r'href="(https://glyphsapp\.com/news/[^"]+)"'
    urls = re.findall(pattern, html)
    
    # Also check relative URLs
    pattern2 = r'href="(/news/[^"]+)"'
    for path in re.findall(pattern2, html):
        if not path.endswith("/feed"):
            urls.append(f"https://glyphsapp.com{path}")
    
    for url in urls:
        # Skip duplicates, feeds, and media files
        if url in seen:
            continue
        if url.endswith("/feed"):
            continue
        if any(ext in url.lower() for ext in [".png", ".jpg", ".gif", ".mp4", ".pdf"]):
            continue
        
        seen.add(url)
        title = url_to_title(url)
        
        # Filter by query (match in URL or generated title)
        if query_lower in url.lower() or query_lower in title.lower():
            results.append({
                "title": title,
                "url": url,
                "type": classify_post(url),
            })
    
    # Sort: releases first, then by URL (newer versions typically have higher numbers)
    def sort_key(r):
        is_release = "release" in r["type"].lower()
        # Extract version numbers for sorting
        version_match = re.search(r"(\d+)-(\d+)(?:-(\d+))?", r["url"])
        if version_match:
            major = int(version_match.group(1))
            minor = int(version_match.group(2))
            patch = int(version_match.group(3) or 0)
            return (not is_release, -major, -minor, -patch)
        return (not is_release, 0, 0, 0)
    
    results.sort(key=sort_key)
    results = results[:limit]
    
    # Format output
    if not results:
        return f"""## 📰 News Search: "{query}"

No news posts found matching "{query}".

**Suggestions**:
- Try "released" to find all release announcements
- Browse all news: {NEWS_URL}
- Search forum for community discussions: `search_forum.py "{query}"`
"""
    
    lines = [
        f'## 📰 News Search: "{query}"',
        f"Found {len(results)} posts (releases sorted by version)\n",
    ]
    
    for i, r in enumerate(results, 1):
        # Type icon
        if "Glyphs release" in r["type"]:
            icon = "🚀"
        elif "release" in r["type"].lower():
            icon = "📦"
        else:
            icon = "📄"
        
        lines.append(f"### {i}. {r['title']} {icon}")
        lines.append(f"**URL**: {r['url']}")
        lines.append(f"**Type**: {r['type']}")
        lines.append("")
    
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read specific post")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs news")
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    result = search_news(query, args.limit)
    print(result)


if __name__ == "__main__":
    main()
