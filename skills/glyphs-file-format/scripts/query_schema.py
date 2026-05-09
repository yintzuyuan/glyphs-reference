#!/usr/bin/env python3
"""Query GlyphsFileFormat JSON Schema definitions.

Usage:
    query_schema.py <name>                        # Query glyphs-3 schema
    query_schema.py <name> --schema glyphs-1      # Query v2 schema
    query_schema.py --list                         # List all $defs
    query_schema.py --list --schema fontinfo-3     # List fontinfo $defs
"""

import argparse
import json

import _format_utils

AVAILABLE_SCHEMAS = [
    "glyphs-1",
    "glyphs-3",
    "glyphs-autosave-1",
    "glyphs-autosave-3",
    "fontinfo-3",
    "fontinfo-autosave-3",
]


def main():
    parser = argparse.ArgumentParser(
        description="Query GlyphsFileFormat JSON Schema definitions"
    )
    parser.add_argument("name", nargs="?", help="Definition name (e.g., anchor, glyph)")
    parser.add_argument(
        "--schema",
        default="glyphs-3",
        help=f"Schema name (default: glyphs-3). Available: {', '.join(AVAILABLE_SCHEMAS)}",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all $defs keys"
    )
    args = parser.parse_args()

    if not args.list and not args.name:
        parser.error("either provide a definition name or use --list")

    try:
        schema_path = _format_utils.get_schema_path(args.schema)
        if not schema_path.exists():
            _format_utils.output_error(
                f"Schema not found: {args.schema}. "
                f"Available: {', '.join(AVAILABLE_SCHEMAS)}"
            )
        schema_data = json.loads(schema_path.read_text())
    except FileNotFoundError as e:
        _format_utils.output_error(str(e))

    if args.list:
        defs = _format_utils.list_schema_defs(schema_data)
        _format_utils.output_json({
            "schema": args.schema,
            "schema_file": schema_path.name,
            "count": len(defs),
            "definitions": defs,
        })
    else:
        definition = _format_utils.extract_schema_def(schema_data, args.name)
        if definition is None:
            _format_utils.output_error(
                f"Definition '{args.name}' not found in {args.schema} schema"
            )
        _format_utils.output_json({
            "name": args.name,
            "schema": args.schema,
            "schema_file": schema_path.name,
            "definition": definition,
        })


if __name__ == "__main__":
    main()
