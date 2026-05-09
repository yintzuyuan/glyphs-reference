#!/usr/bin/env python3
"""Read Glyphs Python API class/member/function details.

Usage:
    read_class.py GSFont                   # Full class details
    read_class.py GSFont --member masters  # Specific member
    read_class.py GSFont --summary         # Names only
    read_class.py GSFont --relationships   # Cross-references
    read_class.py --function divideCurve   # Standalone function
"""

import argparse
from pathlib import Path

import _sdk_utils
import _parse_rst


def _find_class(name: str, classes: list[dict]) -> dict | None:
    """Find a class by name (case-insensitive)."""
    name_lower = name.lower()
    for cls in classes:
        if cls["name"].lower() == name_lower:
            return cls
    return None


def read_class_info(name: str, rst_path: Path) -> dict | None:
    """Read full class details including all properties and methods."""
    classes = _parse_rst.parse_classes(rst_path)
    return _find_class(name, classes)


def read_member(class_name: str, member_name: str, rst_path: Path) -> dict | None:
    """Read a specific property or method from a class."""
    classes = _parse_rst.parse_classes(rst_path)
    cls = _find_class(class_name, classes)
    if cls is None:
        return None

    member_lower = member_name.lower()
    for prop in cls["properties"]:
        if prop["name"].lower() == member_lower:
            return {**prop, "member_type": "property", "class": cls["name"]}
    for method in cls["methods"]:
        if method["name"].lower() == member_lower:
            return {**method, "member_type": "method", "class": cls["name"]}
    return None


def read_class_summary(name: str, rst_path: Path) -> dict | None:
    """Read class summary (property/method names only)."""
    classes = _parse_rst.parse_classes(rst_path)
    cls = _find_class(name, classes)
    if cls is None:
        return None
    return {
        "name": cls["name"],
        "description": cls["description"],
        "properties": [p["name"] for p in cls["properties"]],
        "methods": [m["name"] for m in cls["methods"]],
    }


def read_relationships(name: str, rst_path: Path) -> dict | None:
    """Read cross-reference relationships for a class."""
    classes = _parse_rst.parse_classes(rst_path)
    cls = _find_class(name, classes)
    if cls is None:
        return None

    # Forward references (classes this class mentions)
    references = cls.get("cross_references", [])

    # Reverse references (classes that mention this class)
    referenced_by = []
    for other in classes:
        if other["name"] == cls["name"]:
            continue
        if cls["name"] in other.get("cross_references", []):
            referenced_by.append(other["name"])

    return {
        "name": cls["name"],
        "references": references,
        "referenced_by": sorted(referenced_by),
    }


def read_function(name: str, rst_path: Path) -> dict | None:
    """Read a standalone function by name."""
    functions = _parse_rst.parse_standalone_functions(rst_path)
    name_lower = name.lower()
    for func in functions:
        if func["name"].lower() == name_lower:
            return func
    return None


def main():
    parser = argparse.ArgumentParser(description="Read Glyphs Python API details")
    parser.add_argument("class_name", nargs="?", help="Class name (e.g., GSFont)")
    parser.add_argument("--member", "-m", help="Specific member name")
    parser.add_argument("--summary", "-s", action="store_true", help="Names only")
    parser.add_argument("--relationships", "-r", action="store_true", help="Cross-references")
    parser.add_argument("--function", "-f", dest="func_name", help="Standalone function name")
    args = parser.parse_args()

    try:
        rst_path = _sdk_utils.get_sphinx_rst_path()
    except FileNotFoundError as e:
        _sdk_utils.output_error(str(e))

    if args.func_name:
        result = read_function(args.func_name, rst_path)
        if result is None:
            _sdk_utils.output_error(f"Function not found: {args.func_name}")
        _sdk_utils.output_json(result)
        return

    if not args.class_name:
        _sdk_utils.output_error("Provide a class name or --function")

    if args.member:
        result = read_member(args.class_name, args.member, rst_path)
        if result is None:
            _sdk_utils.output_error(f"Member not found: {args.class_name}.{args.member}")
        _sdk_utils.output_json(result)
    elif args.summary:
        result = read_class_summary(args.class_name, rst_path)
        if result is None:
            _sdk_utils.output_error(f"Class not found: {args.class_name}")
        _sdk_utils.output_json(result)
    elif args.relationships:
        result = read_relationships(args.class_name, rst_path)
        if result is None:
            _sdk_utils.output_error(f"Class not found: {args.class_name}")
        _sdk_utils.output_json(result)
    else:
        result = read_class_info(args.class_name, rst_path)
        if result is None:
            _sdk_utils.output_error(f"Class not found: {args.class_name}")
        _sdk_utils.output_json(result)


if __name__ == "__main__":
    main()
