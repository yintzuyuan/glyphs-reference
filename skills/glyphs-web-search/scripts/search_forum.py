#!/usr/bin/env python3
"""Search Glyphs forum discussions.

Usage:
    python search_forum.py <query> [--limit N]

Examples:
    python search_forum.py "variable font"
    python search_forum.py "kerning groups" --limit 10

Output:
    Lightweight list of discussions (~2KB) with title, URL, reply count.
    Use fetch_content.py to get detailed content of specific discussions.

Note:
    Responses from Georg Seifert, Florian Pircher, and Rainer Erich Scheichelbauer
    (mekkablue) carry official weight - pay attention to their replies.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import fetch_json

FORUM_API = "https://forum.glyphsapp.com/search.json"


def search_forum(query: str, limit: int = 20) -> str:
    """Search forum and return formatted results list."""
    
    # Build search URL with latest ordering
    search_query = query.replace(" ", "+") + "+order:latest"
    url = f"{FORUM_API}?q={search_query}"
    
    try:
        data = fetch_json(url)
    except Exception as e:
        return f"""## ❌ Forum Search Error

{e}

**Manual search**: https://forum.glyphsapp.com/search?q={query.replace(" ", "+")}
"""

    # Build topics lookup
    topics = {t["id"]: t for t in data.get("topics", [])}
    
    # Extract unique discussions from posts
    results = []
    seen = set()
    
    for post in data.get("posts", []):
        topic_id = post.get("topic_id")
        if topic_id in seen or topic_id not in topics:
            continue
        seen.add(topic_id)
        
        if len(results) >= limit:
            break
        
        topic = topics[topic_id]
        slug = topic.get("slug", "")
        replies = topic.get("posts_count", 1) - 1
        created = topic.get("created_at", "")[:10]
        last_reply = topic.get("last_posted_at", "")[:10]
        author = post.get("name", "Unknown")
        
        results.append({
            "title": topic.get("title", "Untitled"),
            "url": f"https://forum.glyphsapp.com/t/{slug}/{topic_id}",
            "author": author,
            "replies": replies,
            "created": created,
            "last_reply": last_reply,
        })
    
    # Format output
    if not results:
        return f"""## 💬 Forum Search: "{query}"

No discussions found.

**Suggestions**:
- Try different English keywords
- Manual search: https://forum.glyphsapp.com/search?q={query.replace(" ", "+")}
"""
    
    lines = [
        f'## 💬 Forum Search: "{query}"',
        f"Found {len(results)} discussions (sorted by latest activity)\n",
    ]
    
    for i, r in enumerate(results, 1):
        # Activity indicator
        if r["replies"] >= 10:
            icon = "🔥"
        elif r["replies"] >= 5:
            icon = "📈"
        elif r["replies"] == 0:
            icon = "❓"
        else:
            icon = "💬"
        
        lines.append(f"### {i}. {r['title']} {icon}")
        lines.append(f"**URL**: {r['url']}")
        lines.append(f"**Author**: {r['author']} | **Replies**: {r['replies']} | **Date**: {r['created']}")
        
        if r["last_reply"] != r["created"]:
            lines.append(f"**Last reply**: {r['last_reply']}")
        
        lines.append("")
    
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read specific discussion")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs forum discussions")
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    result = search_forum(query, args.limit)
    print(result)


if __name__ == "__main__":
    main()
