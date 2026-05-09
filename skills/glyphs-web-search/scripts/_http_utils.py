"""Shared HTTP utilities for Glyphs web search scripts.

This module provides synchronous HTTP utilities with connection pooling.
Not meant to be executed directly.
"""

import re
from typing import Any

import httpx

USER_AGENT = "GlyphsWebSearch/1.0"
TIMEOUT = 30

# Shared client with connection pooling
_client: httpx.Client | None = None


def get_client() -> httpx.Client:
    """Get or create shared HTTP client with connection pooling."""
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
    return _client


def fetch_json(url: str) -> Any:
    """Fetch URL and return parsed JSON."""
    resp = get_client().get(url)
    resp.raise_for_status()
    return resp.json()


def fetch_html(url: str) -> str:
    """Fetch URL and return raw HTML content."""
    resp = get_client().get(url)
    resp.raise_for_status()
    return resp.text


def html_to_text(html: str) -> str:
    """Convert HTML to plain text, removing scripts, styles, and tags."""
    # Remove script and style blocks
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<nav[^>]*>.*?</nav>", "", text, flags=re.S | re.I)
    text = re.sub(r"<footer[^>]*>.*?</footer>", "", text, flags=re.S | re.I)
    text = re.sub(r"<header[^>]*>.*?</header>", "", text, flags=re.S | re.I)
    
    # Convert common elements to readable format
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<p[^>]*>", "\n\n", text, flags=re.I)
    text = re.sub(r"</p>", "", text, flags=re.I)
    text = re.sub(r"<h[1-6][^>]*>", "\n\n## ", text, flags=re.I)
    text = re.sub(r"</h[1-6]>", "\n", text, flags=re.I)
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.I)
    
    # Remove remaining tags
    text = re.sub(r"<[^>]+>", " ", text)
    
    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    
    return text


def chunk_content(content: str, offset: int = 0, limit: int = 3000) -> dict:
    """Split content into chunks with pagination info.
    
    Returns:
        dict with keys: content, offset, limit, total, has_more, next_offset
    """
    total = len(content)
    offset = max(0, min(offset, total))
    chunk = content[offset : offset + limit]
    
    return {
        "content": chunk,
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": offset + limit < total,
        "next_offset": offset + limit if offset + limit < total else None,
    }


def url_to_title(url: str) -> str:
    """Convert URL path to readable title.
    
    Example: /news/glyphs-3-3-released -> Glyphs 3 3 Released
    """
    # Extract path segment
    path = url.rstrip("/").split("/")[-1]
    
    # Convert to title
    words = path.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)
