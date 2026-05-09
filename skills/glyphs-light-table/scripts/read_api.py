#!/usr/bin/env python3
"""Read and search Light Table Python API.

Usage:
    read_api.py                    # List all types and extensions
    read_api.py DocumentState      # Detail for a specific type
    read_api.py GSFont             # GSFont lt_* extensions
    read_api.py --search "restore" # Cross-type search
"""

import argparse
import re
import sys
from pathlib import Path

import _lighttable_utils

# Known GS classes that Light Table extends
_GS_CLASSES = {"GSFont", "GSGlyph", "GSLayer"}


def parse_api(source: str) -> dict:
    """Parse Light Table API source into structured data.

    Returns dict with: enums, objc_classes, gs_extensions,
    objc_class_extensions, dataclasses.
    """
    return {
        "enums": _parse_enums(source),
        "objc_classes": _parse_objc_classes(source),
        "gs_extensions": _parse_extensions(source, gs_only=True),
        "objc_class_extensions": _parse_extensions(source, gs_only=False),
        "dataclasses": _parse_dataclasses(source),
    }


def _parse_enums(source: str) -> list[dict]:
    """Extract Enum definitions with members."""
    enums = []
    for match in re.finditer(
        r"^class (\w+)\((?:Int)?Enum\):\s*\n((?:[ \t]+\w+[ \t]*=[ \t]*\d+[ \t]*\n?)+)",
        source,
        re.MULTILINE,
    ):
        name = match.group(1)
        members = []
        for member_match in re.finditer(
            r"(\w+)\s*=\s*(\d+)", match.group(2)
        ):
            members.append({
                "name": member_match.group(1),
                "value": int(member_match.group(2)),
            })
        enums.append({"name": name, "members": members})
    return enums


def _parse_objc_classes(source: str) -> list[dict]:
    """Extract objc.lookUpClass() bindings (public only)."""
    classes = []
    for match in re.finditer(
        r'^(\w+)\s*=\s*objc\.lookUpClass\("(\w+)"\)',
        source,
        re.MULTILINE,
    ):
        python_name = match.group(1)
        if python_name.startswith("_"):
            continue
        classes.append({
            "python_name": python_name,
            "objc_class": match.group(2),
        })
    return classes


def _parse_extensions(source: str, *, gs_only: bool) -> dict[str, list[dict]]:
    """Extract property/method extensions on classes.

    If gs_only=True, returns only GS* class extensions.
    If gs_only=False, returns only non-GS class extensions.
    """
    extensions: dict[str, list[dict]] = {}
    for match in re.finditer(
        r"^(\w+)\.(\w+)\s*=\s*(property|objc\.python_method|staticmethod)\(",
        source,
        re.MULTILINE,
    ):
        cls_name = match.group(1)
        ext_name = match.group(2)
        ext_type = match.group(3)

        is_gs = cls_name in _GS_CLASSES
        if gs_only != is_gs:
            continue

        kind = "property" if ext_type == "property" else "method"

        # Look ahead in source for ObjC selector or pyobjc accessor
        block = source[match.end():match.end() + 400]

        entry: dict = {"name": ext_name, "kind": kind}

        lti_match = re.search(r"_LightTableInterface\.(\w+)\(", block)
        pyobjc_match = re.search(
            r"self\.pyobjc_instanceMethods\.(\w+)\(", block
        )

        if lti_match:
            entry["objc_selector"] = lti_match.group(1)
        elif pyobjc_match:
            entry["objc_accessor"] = pyobjc_match.group(1)

        extensions.setdefault(cls_name, []).append(entry)

    return extensions


def _parse_dataclasses(source: str) -> list[dict]:
    """Extract @dataclass definitions with field names."""
    dataclasses = []
    for match in re.finditer(
        r"@dataclass\s*\nclass (\w+):\s*\n((?:\s+\w+:.*\n?)+)",
        source,
        re.MULTILINE,
    ):
        name = match.group(1)
        fields = []
        for field_match in re.finditer(r"(\w+)\s*:", match.group(2)):
            fields.append(field_match.group(1))
        dataclasses.append({"name": name, "fields": fields})
    return dataclasses


def detail(parsed: dict, name: str):
    """Return detail for a specific type, or None if not found."""
    # Check enums
    for enum in parsed["enums"]:
        if enum["name"] == name:
            return {"type": "enum", **enum}

    # Check GS extensions
    if name in parsed["gs_extensions"]:
        return {
            "type": "gs_extensions",
            "class": name,
            "extensions": parsed["gs_extensions"][name],
        }

    # Check ObjC classes (combine binding + extensions)
    for cls in parsed["objc_classes"]:
        if cls["python_name"] == name:
            result = {
                "type": "objc_class",
                **cls,
                "extensions": parsed["objc_class_extensions"].get(name, []),
            }
            return result

    # Check ObjC class extensions (class name not in objc_classes)
    if name in parsed["objc_class_extensions"]:
        return {
            "type": "objc_class_extensions",
            "class": name,
            "extensions": parsed["objc_class_extensions"][name],
        }

    # Check dataclasses
    for dc in parsed["dataclasses"]:
        if dc["name"] == name:
            return {"type": "dataclass", **dc}

    return None


def search(parsed: dict, query: str) -> dict:
    """Search across all parsed types (case-insensitive)."""
    results = []
    q = query.lower()

    for enum in parsed["enums"]:
        if q in enum["name"].lower():
            results.append({"type": "enum", "name": enum["name"]})
        for member in enum["members"]:
            if q in member["name"].lower():
                results.append({
                    "type": "enum_member",
                    "enum": enum["name"],
                    "name": member["name"],
                })

    for cls in parsed["objc_classes"]:
        if q in cls["python_name"].lower() or q in cls["objc_class"].lower():
            results.append({
                "type": "objc_class",
                "name": cls["python_name"],
                "objc_class": cls["objc_class"],
            })

    for cls_name, exts in parsed["gs_extensions"].items():
        for ext in exts:
            if q in ext["name"].lower() or q in cls_name.lower():
                results.append({
                    "type": "gs_extension",
                    "class": cls_name,
                    "name": ext["name"],
                })

    for cls_name, exts in parsed["objc_class_extensions"].items():
        for ext in exts:
            if q in ext["name"].lower() or q in cls_name.lower():
                results.append({
                    "type": "objc_class_extension",
                    "class": cls_name,
                    "name": ext["name"],
                })

    for dc in parsed["dataclasses"]:
        if q in dc["name"].lower():
            results.append({"type": "dataclass", "name": dc["name"]})

    return {"query": query, "results": results}


def main():
    parser = argparse.ArgumentParser(
        description="Read and search Light Table Python API"
    )
    parser.add_argument("name", nargs="?", help="Type name to look up")
    parser.add_argument(
        "--search", "-s", dest="query", help="Search across all types"
    )
    args = parser.parse_args()

    try:
        source_path = _lighttable_utils.get_api_source_path()
        source = source_path.read_text()
    except FileNotFoundError as e:
        _lighttable_utils.output_error(str(e))
        return  # output_error exits, but helps type checker

    parsed = parse_api(source)

    if args.query:
        _lighttable_utils.output_json(search(parsed, args.query))
    elif args.name:
        result = detail(parsed, args.name)
        if result is None:
            _lighttable_utils.output_error(
                f"Type '{args.name}' not found in Light Table API"
            )
        else:
            _lighttable_utils.output_json(result)
    else:
        _lighttable_utils.output_json(parsed)


if __name__ == "__main__":
    main()
