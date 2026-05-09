#!/usr/bin/env python3
"""Search and list Glyphs Python API classes, members, and constants.

Usage:
    search_api.py                     # List all 35 classes with counts
    search_api.py --search "layer"    # Cross-type search
    search_api.py --constants         # List all constants
    search_api.py --functions         # List standalone functions
"""

import argparse
from pathlib import Path

import _sdk_utils
import _parse_rst


def list_classes(rst_path: Path) -> list[dict]:
    """List all classes with property/method counts."""
    classes = _parse_rst.parse_classes(rst_path)
    return [
        {
            "name": cls["name"],
            "description": cls["description"][:120] + ("..." if len(cls["description"]) > 120 else ""),
            "property_count": len(cls["properties"]),
            "method_count": len(cls["methods"]),
        }
        for cls in classes
    ]


def list_constants(rst_path: Path, init_py_path: Path) -> list[dict]:
    """List all constants with values and categories."""
    return _parse_rst.parse_constants(rst_path, init_py_path)


def list_functions(rst_path: Path) -> list[dict]:
    """List all standalone functions."""
    functions = _parse_rst.parse_standalone_functions(rst_path)
    return [
        {
            "name": f["name"],
            "params": f["params"],
            "description": f["description"][:120] + ("..." if len(f["description"]) > 120 else ""),
            "return_type": f.get("return_type", ""),
        }
        for f in functions
    ]


def search(query: str, rst_path: Path, init_py_path: Path) -> list[dict]:
    """Search across classes, properties, methods, constants, and functions."""
    q = query.lower()
    results = []

    # Search classes
    classes = _parse_rst.parse_classes(rst_path)
    for cls in classes:
        if q in cls["name"].lower():
            results.append({"type": "class", "name": cls["name"], "description": cls["description"][:120]})

        # Search properties
        for prop in cls["properties"]:
            if q in prop["name"].lower():
                results.append({
                    "type": "property",
                    "name": prop["name"],
                    "class": cls["name"],
                    "property_type": prop.get("type", ""),
                })

        # Search methods
        for method in cls["methods"]:
            if q in method["name"].lower():
                results.append({
                    "type": "method",
                    "name": method["name"],
                    "class": cls["name"],
                    "params": method.get("params", ""),
                })

    # Search standalone functions
    functions = _parse_rst.parse_standalone_functions(rst_path)
    for func in functions:
        if q in func["name"].lower():
            results.append({
                "type": "function",
                "name": func["name"],
                "params": func["params"],
            })

    # Search constants
    constants = _parse_rst.parse_constants(rst_path, init_py_path)
    for const in constants:
        if q in const["name"].lower():
            results.append({
                "type": "constant",
                "name": const["name"],
                "value": const["value"],
                "category": const["category"],
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search Glyphs Python API")
    parser.add_argument("--search", "-s", help="Search query")
    parser.add_argument("--constants", "-c", action="store_true", help="List all constants")
    parser.add_argument("--functions", "-f", action="store_true", help="List standalone functions")
    args = parser.parse_args()

    try:
        rst_path = _sdk_utils.get_sphinx_rst_path()
        init_py_path = _sdk_utils.get_init_py_path()
    except FileNotFoundError as e:
        _sdk_utils.output_error(str(e))

    if args.search:
        _sdk_utils.output_json(search(args.search, rst_path, init_py_path))
    elif args.constants:
        _sdk_utils.output_json(list_constants(rst_path, init_py_path))
    elif args.functions:
        _sdk_utils.output_json(list_functions(rst_path))
    else:
        _sdk_utils.output_json(list_classes(rst_path))


if __name__ == "__main__":
    main()
