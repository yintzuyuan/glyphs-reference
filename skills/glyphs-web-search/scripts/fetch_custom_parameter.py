#!/usr/bin/env python3
"""Fetch specific Custom Parameter details from Glyphs Handbook.

Usage:
    python fetch_custom_parameter.py "blueScale"
    python fetch_custom_parameter.py "Color" --fuzzy

Output:
    Full description of the specified parameter(s).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from _http_utils import fetch_html, html_to_text
except ImportError:
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
        
        if line and i + 2 < len(lines):
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            next_next_line = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            type_keywords = ['string', 'integer', 'boolean', 'list', 'float']
            
            if not next_line and next_next_line:
                first_word = next_next_line.split()[0] if next_next_line.split() else ""
                if first_word.lower() in type_keywords:
                    if current_param:
                        parameters.append({
                            'name': current_param,
                            'description': '\n'.join(current_desc_lines).strip()
                        })
                    
                    current_param = line
                    current_desc_lines = [next_next_line]
                    i += 3
                    continue
        
        if current_param and line:
            current_desc_lines.append(line)
        
        i += 1
    
    if current_param:
        parameters.append({
            'name': current_param,
            'description': '\n'.join(current_desc_lines).strip()
        })
    
    return parameters


def fetch_parameter(name: str, fuzzy: bool = False) -> str:
    """Fetch details for a specific parameter."""
    
    try:
        html = fetch_html(URL)
        text = html_to_text(html)
    except Exception as e:
        return f"❌ Error fetching page: {e}"
    
    parameters = parse_parameters(text)
    
    if not parameters:
        return "❌ No parameters found. Page structure may have changed."
    
    # Find matching parameters
    name_lower = name.lower()
    
    if fuzzy:
        # Fuzzy match: contains
        matches = [p for p in parameters if name_lower in p['name'].lower()]
    else:
        # Exact match first
        exact = [p for p in parameters if p['name'].lower() == name_lower]
        if exact:
            matches = exact
        else:
            # Fall back to contains
            matches = [p for p in parameters if name_lower in p['name'].lower()]
    
    if not matches:
        # Suggest similar
        suggestions = []
        for p in parameters:
            # Simple similarity check
            if any(word in p['name'].lower() for word in name_lower.split()):
                suggestions.append(p['name'])
        
        lines = [f"## ❌ Parameter Not Found: `{name}`\n"]
        if suggestions[:5]:
            lines.append("**Did you mean:**")
            for s in suggestions[:5]:
                lines.append(f"- {s}")
        lines.append(f"\n💡 Use `search_custom_parameters.py \"{name}\"` to search.")
        return '\n'.join(lines)
    
    # Build output
    lines = [f"## Custom Parameter Details\n"]
    
    for p in matches:
        # Extract type
        desc_parts = p['description'].split(None, 1)
        param_type = desc_parts[0] if desc_parts else "unknown"
        param_desc = desc_parts[1] if len(desc_parts) > 1 else p['description']
        
        lines.append(f"### {p['name']}")
        lines.append(f"**Type**: `{param_type}`\n")
        lines.append(param_desc)
        lines.append("")
    
    lines.append(f"---\n**Source**: [Custom Parameters]({URL.replace('/document.md', '')})")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch specific Custom Parameter details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "blueScale"              # Exact match
  %(prog)s "Color" --fuzzy          # All params containing 'Color'
  %(prog)s "Decompose"              # Partial match fallback
        """
    )
    parser.add_argument(
        "name",
        help="Parameter name to look up"
    )
    parser.add_argument(
        "--fuzzy",
        action="store_true",
        help="Match all parameters containing the name"
    )
    
    args = parser.parse_args()
    result = fetch_parameter(args.name, args.fuzzy)
    print(result)


if __name__ == "__main__":
    main()
