#!/usr/bin/env python3
"""Search Custom Parameters from Glyphs Handbook.

This script handles the large custom-parameter-descriptions page (105K+ chars)
by parsing parameters into an index and supporting targeted searches.

Usage:
    python search_custom_parameters.py                  # List all parameter names
    python search_custom_parameters.py "blue"           # Search by keyword
    python search_custom_parameters.py "blue" --detail  # Include descriptions

Output:
    List of matching parameters with optional descriptions.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from _http_utils import fetch_html, html_to_text
except ImportError:
    # Standalone mode
    import httpx
    from html.parser import HTMLParser
    
    def fetch_html(url: str) -> str:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GlyphsSearch/1.0)"}
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
    
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
            self.skip_tags = {'script', 'style', 'nav', 'header', 'footer'}
            self.current_skip = False
        
        def handle_starttag(self, tag, attrs):
            if tag in self.skip_tags:
                self.current_skip = True
        
        def handle_endtag(self, tag):
            if tag in self.skip_tags:
                self.current_skip = False
        
        def handle_data(self, data):
            if not self.current_skip:
                self.text.append(data)
        
        def get_text(self):
            return ' '.join(self.text)
    
    def html_to_text(html: str) -> str:
        extractor = TextExtractor()
        extractor.feed(html)
        return extractor.get_text()


URL = "https://handbook.glyphsapp.com/custom-parameter-descriptions/document.md"


def parse_parameters(text: str) -> list[dict]:
    """Parse the custom parameters page into structured data."""
    parameters = []
    
    # Split by parameter headers (name on its own line, followed by type + description)
    # Pattern: Parameter Name\n\n type Description...
    lines = text.split('\n')
    
    current_param = None
    current_desc_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip header section
        if line.startswith('### Custom Parameters') or line.startswith('Custom parameters provide'):
            i += 1
            continue
        
        # Check if this line looks like a parameter name
        # Parameter names are typically on their own line, followed by empty line, then type + desc
        if line and i + 2 < len(lines):
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            next_next_line = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            # Pattern: Name\n\n type description
            # The type line usually starts with: string, integer, boolean, list, float
            type_keywords = ['string', 'integer', 'boolean', 'list', 'float']
            
            if not next_line and next_next_line:
                first_word = next_next_line.split()[0] if next_next_line.split() else ""
                if first_word.lower() in type_keywords:
                    # Save previous parameter
                    if current_param:
                        parameters.append({
                            'name': current_param,
                            'description': '\n'.join(current_desc_lines).strip()
                        })
                    
                    # Start new parameter
                    current_param = line
                    current_desc_lines = [next_next_line]
                    i += 3
                    continue
        
        # Continue collecting description lines
        if current_param and line:
            current_desc_lines.append(line)
        
        i += 1
    
    # Don't forget the last parameter
    if current_param:
        parameters.append({
            'name': current_param,
            'description': '\n'.join(current_desc_lines).strip()
        })
    
    return parameters


def search_parameters(
    query: str = "",
    show_detail: bool = False,
    limit: int = 20
) -> str:
    """Search custom parameters."""
    
    try:
        html = fetch_html(URL)
        text = html_to_text(html)
    except Exception as e:
        return f"❌ Error fetching page: {e}"
    
    parameters = parse_parameters(text)
    
    if not parameters:
        return "❌ No parameters found. Page structure may have changed."
    
    # Filter by query
    if query:
        query_lower = query.lower()
        matches = []
        for p in parameters:
            if query_lower in p['name'].lower() or query_lower in p['description'].lower():
                matches.append(p)
    else:
        matches = parameters
    
    total = len(parameters)
    found = len(matches)
    
    # Build output
    lines = [f"## Custom Parameters"]
    
    if query:
        lines.append(f"**Search**: `{query}` → {found} of {total} parameters\n")
    else:
        lines.append(f"**Total**: {total} parameters\n")
    
    if not matches:
        lines.append("No matching parameters found.")
        return '\n'.join(lines)
    
    # Limit results
    showing = matches[:limit]
    
    if show_detail:
        # Show with descriptions (truncated)
        for p in showing:
            desc = p['description']
            # Truncate long descriptions
            if len(desc) > 300:
                desc = desc[:300] + "..."
            lines.append(f"### {p['name']}\n{desc}\n")
    else:
        # Just list names
        for p in showing:
            # Extract type from description
            first_word = p['description'].split()[0] if p['description'] else ""
            type_str = f" ({first_word})" if first_word in ['string', 'integer', 'boolean', 'list', 'float'] else ""
            lines.append(f"- **{p['name']}**{type_str}")
    
    if len(matches) > limit:
        lines.append(f"\n---\n📖 Showing {limit} of {found} results. Use `--limit` for more.")
    
    # Usage hint
    lines.append(f"\n---\n💡 **Get full details**: `fetch_custom_parameter.py \"{matches[0]['name'] if matches else 'parameter name'}\"`")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search Glyphs Custom Parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # List all parameters
  %(prog)s "blue"                   # Search for 'blue'
  %(prog)s "hinting" --detail       # Show descriptions
  %(prog)s "color" --limit 50       # More results
        """
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search keyword (optional)"
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show parameter descriptions"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max results (default: 20)"
    )
    
    args = parser.parse_args()
    result = search_parameters(args.query, args.detail, args.limit)
    print(result)


if __name__ == "__main__":
    main()
