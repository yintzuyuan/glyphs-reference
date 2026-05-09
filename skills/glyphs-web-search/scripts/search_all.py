#!/usr/bin/env python3
"""Search all Glyphs resources concurrently.

Usage:
    python search_all.py <query> [--limit N]

Examples:
    python search_all.py "variable font"
    python search_all.py "kerning" --limit 5

Output:
    Combined results from forum, tutorials, and news.
    Searches run concurrently for faster results.

Note:
    This script uses async/await for true concurrent requests.
    Individual search scripts use synchronous requests for simplicity.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))

from _http_utils import url_to_title

# URLs
FORUM_API = "https://forum.glyphsapp.com/search.json"
TUTORIALS_URL = "https://glyphsapp.com/learn"
NEWS_URL = "https://glyphsapp.com/news"

USER_AGENT = "GlyphsWebSearch/1.0"
TIMEOUT = 30


async def search_forum_async(client: httpx.AsyncClient, query: str, limit: int) -> dict:
    """Search forum asynchronously."""
    search_query = query.replace(" ", "+") + "+order:latest"
    url = f"{FORUM_API}?q={search_query}"
    
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"source": "forum", "error": str(e), "results": []}
    
    topics = {t["id"]: t for t in data.get("topics", [])}
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
        
        results.append({
            "title": topic.get("title", "Untitled"),
            "url": f"https://forum.glyphsapp.com/t/{slug}/{topic_id}",
            "replies": replies,
        })
    
    return {"source": "forum", "results": results, "error": None}


async def search_tutorials_async(client: httpx.AsyncClient, query: str, limit: int) -> dict:
    """Search tutorials asynchronously."""
    search_url = f"{TUTORIALS_URL}?q={query.replace(' ', '+')}"
    
    try:
        resp = await client.get(search_url)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        return {"source": "tutorials", "error": str(e), "results": []}
    
    results = []
    seen = set()
    
    # Pattern 1: Full URLs
    for url, title in re.findall(r'href="(https://glyphsapp\.com/learn/[^"]+)"[^>]*>([^<]+)</a>', html):
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        if url not in seen and clean_title and len(clean_title) > 2:
            if clean_title.lower() not in ("learn", "tutorials", "view all", "next", "previous"):
                seen.add(url)
                results.append({"title": clean_title, "url": url})
    
    # Pattern 2: Relative URLs
    for path, title in re.findall(r'href="(/learn/[^"]+)"[^>]*>([^<]+)</a>', html):
        url = f"https://glyphsapp.com{path}"
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        if url not in seen and clean_title and len(clean_title) > 2:
            if clean_title.lower() not in ("learn", "tutorials", "view all", "next", "previous"):
                seen.add(url)
                results.append({"title": clean_title, "url": url})
    
    return {"source": "tutorials", "results": results[:limit], "error": None}


async def search_news_async(client: httpx.AsyncClient, query: str, limit: int) -> dict:
    """Search news asynchronously."""
    try:
        resp = await client.get(NEWS_URL)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        return {"source": "news", "error": str(e), "results": []}
    
    results = []
    seen = set()
    query_lower = query.lower()
    
    # Find all news URLs
    urls = re.findall(r'href="(https://glyphsapp\.com/news/[^"]+)"', html)
    for path in re.findall(r'href="(/news/[^"]+)"', html):
        if not path.endswith("/feed"):
            urls.append(f"https://glyphsapp.com{path}")
    
    for url in urls:
        if url in seen or url.endswith("/feed"):
            continue
        if any(ext in url.lower() for ext in [".png", ".jpg", ".gif", ".mp4", ".pdf"]):
            continue
        
        seen.add(url)
        title = url_to_title(url)
        
        if query_lower in url.lower() or query_lower in title.lower():
            results.append({"title": title, "url": url})
    
    return {"source": "news", "results": results[:limit], "error": None}


async def search_all(query: str, limit: int = 10) -> dict:
    """Search all sources concurrently."""
    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        results = await asyncio.gather(
            search_forum_async(client, query, limit),
            search_tutorials_async(client, query, limit),
            search_news_async(client, query, limit),
            return_exceptions=True,
        )
    
    return {
        "query": query,
        "forum": results[0] if not isinstance(results[0], Exception) else {"source": "forum", "error": str(results[0]), "results": []},
        "tutorials": results[1] if not isinstance(results[1], Exception) else {"source": "tutorials", "error": str(results[1]), "results": []},
        "news": results[2] if not isinstance(results[2], Exception) else {"source": "news", "error": str(results[2]), "results": []},
    }


def format_results(data: dict) -> str:
    """Format combined results for display."""
    lines = [
        f'## 🔍 Combined Search: "{data["query"]}"',
        "",
    ]
    
    # Forum results
    forum = data["forum"]
    if forum.get("error"):
        lines.append(f"### 💬 Forum: ❌ {forum['error']}")
    elif forum["results"]:
        lines.append(f"### 💬 Forum ({len(forum['results'])} results)")
        for r in forum["results"][:5]:
            icon = "🔥" if r.get("replies", 0) >= 10 else "💬"
            lines.append(f"- [{r['title']}]({r['url']}) {icon}")
    else:
        lines.append("### 💬 Forum: No results")
    lines.append("")
    
    # Tutorial results
    tutorials = data["tutorials"]
    if tutorials.get("error"):
        lines.append(f"### 📖 Tutorials: ❌ {tutorials['error']}")
    elif tutorials["results"]:
        lines.append(f"### 📖 Tutorials ({len(tutorials['results'])} results)")
        for r in tutorials["results"][:5]:
            lines.append(f"- [{r['title']}]({r['url']})")
    else:
        lines.append("### 📖 Tutorials: No results")
    lines.append("")
    
    # News results
    news = data["news"]
    if news.get("error"):
        lines.append(f"### 📰 News: ❌ {news['error']}")
    elif news["results"]:
        lines.append(f"### 📰 News ({len(news['results'])} results)")
        for r in news["results"][:5]:
            lines.append(f"- [{r['title']}]({r['url']})")
    else:
        lines.append("### 📰 News: No results")
    
    lines.append("")
    lines.append("---")
    lines.append("➡️ Use `fetch_content.py <url>` to read specific content")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search all Glyphs resources concurrently",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "variable font"
  %(prog)s "kerning" --limit 5

This searches forum, tutorials, and news simultaneously.
        """
    )
    parser.add_argument("query", nargs="+", help="Search keywords")
    parser.add_argument("--limit", type=int, default=10, help="Max results per source (default: 10)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    data = asyncio.run(search_all(query, args.limit))
    print(format_results(data))


if __name__ == "__main__":
    main()
