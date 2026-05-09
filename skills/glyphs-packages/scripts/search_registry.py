#!/usr/bin/env python3
"""Search the official Glyphs plugin/script/module registry.

Usage:
    search_registry.py --search "keyword"                    # Cross-category search
    search_registry.py --all                                 # List all packages
    search_registry.py --all --category plugins              # Only plugins
    search_registry.py --all --category scripts              # Only script collections
    search_registry.py --all --type Reporter                 # By plugin type
    search_registry.py --search "x" --category plugins       # Combined
"""

import argparse
import json
import os

import _registry_utils


def run_search(packages: list[dict], query: str) -> list[dict]:
    """Search packages by keyword."""
    return _registry_utils.search_packages(packages, query)


def filter_packages(
    packages: list[dict],
    category: str | None = None,
    plugin_type: str | None = None,
) -> list[dict]:
    """Filter packages by category and/or plugin type."""
    result = packages
    if category:
        result = [p for p in result if p["category"] == category]
    if plugin_type:
        t = plugin_type.lower()
        result = [p for p in result if p.get("type", "").lower() == t]
    return result


def _load_registry() -> dict:
    """Load registry data from test file or fetch from remote.

    Uses _REGISTRY_TEST_FILE env var for testing (JSON file path),
    otherwise fetches from GitHub.
    """
    test_file = os.environ.get("_REGISTRY_TEST_FILE")
    if test_file:
        with open(test_file) as f:
            return json.load(f)
    return _registry_utils.fetch_all_registries()


def main():
    parser = argparse.ArgumentParser(
        description="Search the official Glyphs package registry"
    )
    parser.add_argument("--search", "-s", help="Search keyword")
    parser.add_argument("--all", "-a", action="store_true", help="List all packages")
    parser.add_argument(
        "--category",
        "-c",
        choices=["plugins", "scripts", "modules"],
        help="Filter by category",
    )
    parser.add_argument("--type", "-t", dest="plugin_type", help="Filter by plugin type (Reporter, Filter, etc.)")
    args = parser.parse_args()

    if not args.search and not args.all:
        parser.error("Either --search or --all is required")

    try:
        registry_data = _load_registry()
    except Exception as e:
        _registry_utils.output_error(str(e))
        return

    packages = _registry_utils.parse_registry(registry_data)

    # Apply filters
    packages = filter_packages(packages, category=args.category, plugin_type=args.plugin_type)

    # Apply search
    if args.search:
        packages = run_search(packages, args.search)

    _registry_utils.output_json(packages)


if __name__ == "__main__":
    main()
