#!/usr/bin/env python3
"""Search Glyphs Handbook chapter structure (TOC navigation).

Usage:
    python search_handbook_toc.py <query> [--limit N]

Examples:
    python search_handbook_toc.py "kerning"
    python search_handbook_toc.py "variable font" --limit 10

Output:
    Matching chapter/section titles from the handbook navigation (460+ sections).
    Best for: browsing structure, finding specific chapters by name.

For content search, use: search_handbook_fulltext.py
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_html

HANDBOOK_URL = "https://handbook.glyphsapp.com"


def parse_toc_structure(html: str) -> list[dict]:
    """Parse the Table of Contents structure from handbook homepage."""
    sections = []
    
    # Pattern: <a class=toc-link href=/path/>Title</a>
    pattern = r'<a\s+class=["\']?toc-link["\']?\s+href=["\']?(/[^>"\']+)["\']?>([^<]+)</a>'
    
    for match in re.finditer(pattern, html):
        path = match.group(1).strip()
        title = match.group(2).strip()
        
        # Clean HTML entities
        title = title.replace('&nbsp;', ' ')
        title = re.sub(r'&[a-z]+;', '', title)
        title = title.strip()
        
        if not title:
            continue
        
        # Calculate depth
        path_without_anchor = path.split('#')[0]
        depth = len([s for s in path_without_anchor.split('/') if s]) - 1
        depth = max(0, depth)
        
        url = f"{HANDBOOK_URL}{path}"
        
        sections.append({
            'title': title,
            'url': url,
            'path': path,
            'depth': depth,
        })
    
    # Remove duplicates
    seen = set()
    unique = []
    for s in sections:
        key = s['url'].rstrip('/').lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    
    return unique


def search_handbook_toc(query: str, limit: int = 20) -> str:
    """Search handbook using TOC structure (title/path matching)."""
    
    try:
        html = fetch_html(HANDBOOK_URL)
    except Exception as e:
        return f"## ❌ Handbook TOC Error\n\n{e}\n\n**Manual search**: {HANDBOOK_URL}"

    sections = parse_toc_structure(html)
    
    if not sections:
        return f"## 📕 Handbook TOC: \"{query}\"\n\nUnable to parse structure.\n\n**Manual search**: {HANDBOOK_URL}"

    # Search in titles and paths
    query_lower = query.lower()
    query_words = query_lower.split()
    
    results = []
    for section in sections:
        title_lower = section['title'].lower()
        path_lower = section['path'].lower().replace('-', ' ').replace('/', ' ')
        
        score = 0
        
        # Exact phrase match in title
        if query_lower in title_lower:
            score += 100
        
        # All words match in title
        if all(word in title_lower for word in query_words):
            score += 50
        
        # Any word match
        word_matches = sum(1 for word in query_words if word in title_lower)
        score += word_matches * 10
        
        # Path matches
        if query_lower in path_lower:
            score += 20
        path_word_matches = sum(1 for word in query_words if word in path_lower)
        score += path_word_matches * 5
        
        if score > 0:
            section['score'] = score
            results.append(section)
    
    results.sort(key=lambda x: (-x['score'], x['depth']))
    results = results[:limit]
    
    if not results:
        return f"""## 📕 Handbook TOC: "{query}"

No matching sections found.

**Suggestions**:
- Try `search_handbook_fulltext.py` to search page content
- Browse: {HANDBOOK_URL}
"""
    
    lines = [
        f'## 📕 Handbook TOC: "{query}"',
        f"Found {len(results)} sections\n",
    ]
    
    for i, r in enumerate(results, 1):
        indent = "  " * min(r['depth'], 2)
        lines.append(f"{i}. {indent}**{r['title']}**")
        lines.append(f"   {r['url']}")
        lines.append("")
    
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read content")
    lines.append("🔍 Use `search_handbook_fulltext.py` to search page content")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs Handbook chapter structure")
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    print(search_handbook_toc(query, args.limit))


if __name__ == "__main__":
    main()
