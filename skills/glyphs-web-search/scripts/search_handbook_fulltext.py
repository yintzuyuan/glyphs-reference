#!/usr/bin/env python3
"""Search Glyphs Handbook page content (fulltext search).

Usage:
    python search_handbook_fulltext.py <query> [--limit N]

Examples:
    python search_handbook_fulltext.py "add component"
    python search_handbook_fulltext.py "how to create anchors" --limit 5

Output:
    Pages containing the search terms with context snippets.
    Best for: finding specific operations, instructions, or concepts.

For chapter browsing, use: search_handbook_toc.py
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_html

HANDBOOK_URL = "https://handbook.glyphsapp.com"
SEARCH_INDEX_URL = f"{HANDBOOK_URL}/en/search-index.json"


def load_search_index() -> list[dict]:
    """Load the official handbook search index."""
    data = fetch_html(SEARCH_INDEX_URL)
    return json.loads(data)


def search_handbook_fulltext(query: str, limit: int = 20) -> str:
    """Search handbook using fulltext search index."""
    
    try:
        index = load_search_index()
    except Exception as e:
        return f"## ❌ Handbook Fulltext Error\n\n{e}\n\n**Manual search**: {HANDBOOK_URL}"
    
    query_lower = query.lower()
    query_words = query_lower.split()
    
    results = []
    
    for item in index:
        title = item.get('title', '') or ''
        summary = item.get('summary', '') or ''
        text = item.get('text', '') or ''
        keywords = item.get('keywords', {}) or {}
        url = item.get('pageURL', '') or ''
        parents = item.get('parents', []) or []
        
        if not url:
            continue
        
        # Combined searchable text
        searchable = f"{title} {summary} {text}".lower()
        
        score = 0
        matched_context = ""
        
        # Keyword weight from index
        for kw, weight in keywords.items():
            if query_lower in kw.lower():
                score += weight * 2
        
        # Exact phrase match
        if query_lower in title.lower():
            score += 100
            matched_context = title
        elif query_lower in summary.lower():
            score += 80
            matched_context = summary
        elif query_lower in text.lower():
            score += 50
            # Extract context around match
            idx = text.lower().find(query_lower)
            start = max(0, idx - 40)
            end = min(len(text), idx + len(query) + 60)
            matched_context = "..." + text[start:end].strip() + "..."
        
        # All words match
        if all(word in searchable for word in query_words):
            score += 30
            if not matched_context:
                for word in query_words:
                    idx = text.lower().find(word)
                    if idx >= 0:
                        start = max(0, idx - 30)
                        end = min(len(text), idx + 80)
                        matched_context = "..." + text[start:end].strip() + "..."
                        break
        
        # Individual word matches
        word_matches = sum(1 for word in query_words if word in searchable)
        score += word_matches * 5
        
        if score > 0:
            breadcrumb = " › ".join(parents + [title]) if parents else title
            
            results.append({
                'title': title,
                'url': url,
                'summary': summary[:120] + "..." if len(summary) > 120 else summary,
                'context': matched_context[:150] if matched_context else "",
                'breadcrumb': breadcrumb,
                'score': score,
            })
    
    results.sort(key=lambda x: -x['score'])
    results = results[:limit]
    
    if not results:
        return f"""## 🔍 Handbook Fulltext: "{query}"

No matching content found.

**Suggestions**:
- Try different keywords
- Use `search_handbook_toc.py` to browse chapters
- Browse: {HANDBOOK_URL}
"""
    
    lines = [
        f'## 🔍 Handbook Fulltext: "{query}"',
        f"Found {len(results)} results\n",
    ]
    
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['title']}**")
        if r['context']:
            lines.append(f"   > {r['context']}")
        lines.append(f"   {r['url']}")
        lines.append("")
    
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read full content")
    lines.append("💡 Append `document.md` to URL for clean Markdown")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs Handbook page content")
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    print(search_handbook_fulltext(query, args.limit))


if __name__ == "__main__":
    main()
