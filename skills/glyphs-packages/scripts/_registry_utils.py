"""Shared utilities for glyphs-packages scripts.

Provides registry parsing, search, and JSON output helpers.
Not meant to be executed directly.
"""

import json
import subprocess
import sys
import urllib.request

# Registry URLs (GitHub raw ASCII plist files)
_REGISTRY_BASE = "https://raw.githubusercontent.com/schriftgestalt/glyphs-packages/refs/heads/glyphs3"
REGISTRY_URLS = {
    "plugins": f"{_REGISTRY_BASE}/packages.plist",
    "scripts": f"{_REGISTRY_BASE}/scripts.plist",
    "modules": f"{_REGISTRY_BASE}/modules.plist",
}

# Bundle extension → plugin type mapping
_TYPE_MAP = {
    ".glyphsReporter": "Reporter",
    ".glyphsFilter": "Filter",
    ".glyphsPalette": "Palette",
    ".glyphsTool": "Tool",
    ".glyphsPlugin": "Plugin",
    ".glyphsFileFormat": "FileFormat",
}


def classify_plugin_type(path: str | None) -> str:
    """Infer plugin type from bundle file extension.

    Args:
        path: Bundle filename like "ShowAnchors.glyphsReporter"

    Returns:
        Plugin type string (Reporter, Filter, etc.) or "Unknown"
    """
    if not path:
        return "Unknown"
    for ext, plugin_type in _TYPE_MAP.items():
        if path.endswith(ext):
            return plugin_type
    return "Unknown"


def parse_registry(data: dict) -> list[dict]:
    """Parse registry JSON data into a flat list of packages.

    Args:
        data: Dict with keys "plugins", "scripts", "modules",
              each containing a list of package dicts.

    Returns:
        List of normalized package dicts with fields:
        title, url, category, description, path (plugins only), type (plugins only)
    """
    results = []
    for category, packages in data.items():
        for pkg in packages:
            entry = {
                "title": _extract_title(pkg),
                "url": pkg.get("url", ""),
                "category": category,
                "description": _extract_description(pkg),
            }
            path = pkg.get("path", "")
            if category == "plugins":
                entry["path"] = path
                entry["type"] = classify_plugin_type(path)
            results.append(entry)
    return results


def search_packages(packages: list[dict], query: str) -> list[dict]:
    """Search packages by keyword across title, description, and URL.

    Args:
        packages: Flat list from parse_registry()
        query: Search string (case-insensitive)

    Returns:
        Filtered list of matching packages
    """
    if not query:
        return list(packages)
    q = query.lower()
    return [
        p for p in packages
        if q in p["title"].lower()
        or q in p["description"].lower()
        or q in p["url"].lower()
    ]


def fetch_and_convert(url: str) -> dict:
    """Fetch an ASCII plist from URL and convert to JSON via plutil.

    Args:
        url: URL to a .plist file

    Returns:
        Parsed JSON dict

    Raises:
        RuntimeError: If fetch or conversion fails
    """
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            plist_data = resp.read()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    result = subprocess.run(
        ["plutil", "-convert", "json", "-o", "-", "-"],
        input=plist_data,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"plutil conversion failed: {result.stderr.decode()}")

    return json.loads(result.stdout)


def fetch_all_registries() -> dict:
    """Fetch and merge all three registry categories.

    Returns:
        Dict with keys "plugins", "scripts", "modules"
    """
    merged = {}
    for category, url in REGISTRY_URLS.items():
        data = fetch_and_convert(url)
        # The plist contains a top-level array of packages
        if isinstance(data, list):
            merged[category] = data
        elif isinstance(data, dict) and "packages" in data:
            merged[category] = data["packages"]
        else:
            merged[category] = data if isinstance(data, list) else []
    return merged


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)


def _extract_title(pkg: dict) -> str:
    """Extract English title from a package dict."""
    titles = pkg.get("titles", {})
    if isinstance(titles, dict):
        return titles.get("en", "")
    return str(titles)


def _extract_description(pkg: dict) -> str:
    """Extract English description from a package dict."""
    desc = pkg.get("description", "")
    if isinstance(desc, dict):
        return desc.get("en", "")
    return str(desc)
