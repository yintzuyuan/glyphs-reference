#!/usr/bin/env python3
"""Read Vanilla UI component details.

Usage:
    read_component.py Button                # Full: source + docstring + methods
    read_component.py Window --summary      # Summary: methods list (no source)
"""

import argparse
from pathlib import Path

import _vanilla_utils


def read_component(
    name: str,
    mapping: dict[str, str],
    vanilla_path: Path,
    *,
    summary: bool = False,
) -> dict | None:
    """Read a Vanilla component by name.

    Args:
        name: Class name (e.g., "Button", "Window").
        mapping: class→module mapping from parse_init_imports.
        vanilla_path: Path to vanilla/ directory.
        summary: If True, return methods list without source.

    Returns:
        Component info dict, or None if not found.
    """
    module = mapping.get(name)
    if module is None:
        return None

    source_file = vanilla_path / f"{module}.py"
    if not source_file.exists():
        return None

    result = _vanilla_utils.extract_class_source(source_file, name)
    if result is None:
        return None

    result["module"] = module
    result["file_path"] = str(source_file)

    if summary:
        result.pop("source", None)

    return result


def main():
    parser = argparse.ArgumentParser(description="Read Vanilla UI component details")
    parser.add_argument("component_name", help="Component class name (e.g., Button)")
    parser.add_argument(
        "--summary", "-s", action="store_true", help="Methods list only (no source)"
    )
    args = parser.parse_args()

    try:
        vanilla_path = _vanilla_utils.get_vanilla_path()
        init_path = vanilla_path / "__init__.py"
        mapping = _vanilla_utils.parse_init_imports(init_path)
    except FileNotFoundError as e:
        _vanilla_utils.output_error(str(e))

    result = read_component(
        args.component_name, mapping, vanilla_path, summary=args.summary
    )
    if result is None:
        _vanilla_utils.output_error(f"Component not found: {args.component_name}")

    _vanilla_utils.output_json(result)


if __name__ == "__main__":
    main()
