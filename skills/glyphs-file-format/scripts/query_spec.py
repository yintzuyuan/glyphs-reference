#!/usr/bin/env python3
"""Query GlyphsFileFormat spec definitions.

Usage:
    query_spec.py <name>                  # Query v3 definition (default)
    query_spec.py <name> --version 2      # Query v2 definition
    query_spec.py --list                  # List all definitions (v3)
    query_spec.py --list --version 2      # List all definitions (v2)
"""

import argparse

import _format_utils


def main():
    parser = argparse.ArgumentParser(
        description="Query GlyphsFileFormat spec definitions"
    )
    parser.add_argument("name", nargs="?", help="Definition name (e.g., glyph, layer)")
    parser.add_argument(
        "--version",
        type=int,
        default=3,
        choices=[2, 3],
        help="Format version (default: 3)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all definitions"
    )
    args = parser.parse_args()

    if not args.list and not args.name:
        parser.error("either provide a definition name or use --list")

    try:
        spec_path = _format_utils.get_spec_path(args.version)
        spec_text = spec_path.read_text()
    except FileNotFoundError as e:
        _format_utils.output_error(str(e))

    if args.list:
        definitions = _format_utils.list_definitions(spec_text, version=args.version)
        _format_utils.output_json({
            "version": args.version,
            "spec_file": spec_path.name,
            "count": len(definitions),
            "definitions": definitions,
        })
    else:
        definition = _format_utils.extract_definition(
            spec_text, args.name, version=args.version
        )
        if definition is None:
            _format_utils.output_error(
                f"Definition '{args.name}' not found in v{args.version} spec"
            )
        _format_utils.output_json({
            "name": args.name,
            "version": args.version,
            "spec_file": spec_path.name,
            "definition": definition,
        })


if __name__ == "__main__":
    main()
