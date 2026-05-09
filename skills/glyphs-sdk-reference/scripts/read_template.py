"""Read GlyphsSDK template/sample source code with AST analysis.

Reads plugin.py source, extracts AST info (classes, methods, imports),
and attaches accompanying README if present.
"""

import argparse
import ast

import _sdk_utils
import list_templates


def _parse_ast_info(source: str) -> dict:
    """Extract classes, methods, and imports from Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"classes": [], "imports": []}

    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        "name": item.name,
                        "args": [a.arg for a in item.args.args if a.arg != "self"],
                        "line": item.lineno,
                    })
            classes.append({
                "name": node.name,
                "bases": [
                    b.id if isinstance(b, ast.Name) else ast.dump(b)
                    for b in node.bases
                ],
                "methods": methods,
                "line": node.lineno,
            })

    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    return {"classes": classes, "imports": imports}


def _find_readme(py_path) -> str | None:
    """Find README.md near the Python file (same dir or parent dirs)."""
    search_dirs = [py_path.parent]
    # Walk up to find README in parent directories (up to 4 levels)
    current = py_path.parent
    for _ in range(4):
        current = current.parent
        search_dirs.append(current)
        # Stop if we reach Templates/ or Samples/ root
        if current.name in ("Python Templates", "Python Samples"):
            break

    for d in search_dirs:
        for name in ("README.md", "readme.md", "Readme.md"):
            readme = d / name
            if readme.is_file():
                return readme.read_text(encoding="utf-8")
    return None


def _find_entry(name: str, variant: str | None = None) -> dict | None:
    """Find an entry by name, with optional variant filter."""
    all_entries = list_templates.list_all()
    name_lower = name.lower()

    for entry in all_entries:
        entry_name = entry["name"].lower()
        # Exact name match
        if entry_name == name_lower:
            if variant:
                if entry.get("variant") and variant.lower() in entry["variant"].lower():
                    return entry
            else:
                return entry
        # Partial match on plugin_type or name
        if name_lower in entry_name or name_lower == entry.get("plugin_type", "").lower():
            if variant:
                if entry.get("variant") and variant.lower() in entry["variant"].lower():
                    return entry
            elif not variant:
                return entry

    return None


def read_entry(name: str, variant: str | None = None) -> dict | None:
    """Read a template or sample by name.

    Returns dict with: source, classes, imports, readme, entry_info
    """
    entry = _find_entry(name, variant)
    if entry is None:
        return None

    # Resolve Python file path
    if entry["type"] == "template":
        base_dir = _sdk_utils.get_templates_path()
    else:
        base_dir = _sdk_utils.get_samples_path()

    py_path = base_dir / entry["path"]
    if not py_path.exists() or not py_path.suffix == ".py":
        # Entry might point to a readme instead of .py (e.g., Plugin Preferences)
        return {
            "entry": entry,
            "source": None,
            "classes": [],
            "imports": [],
            "readme": py_path.read_text(encoding="utf-8") if py_path.exists() else None,
        }

    source = py_path.read_text(encoding="utf-8")
    ast_info = _parse_ast_info(source)
    readme = _find_readme(py_path)

    return {
        "entry": entry,
        "source": source,
        **ast_info,
        "readme": readme,
    }


def read_drawing_tools() -> dict:
    """Read drawingTools.py with AST analysis."""
    path = _sdk_utils.get_drawing_tools_path()
    source = path.read_text(encoding="utf-8")
    ast_info = _parse_ast_info(source)

    return {
        "source": source,
        **ast_info,
    }


def main():
    parser = argparse.ArgumentParser(description="Read GlyphsSDK template or sample")
    parser.add_argument("name", nargs="?", help="Template or sample name")
    parser.add_argument("--variant", help="Template variant (e.g. 'without dialog')")
    parser.add_argument("--drawing-tools", action="store_true",
                        help="Read drawingTools.py instead")
    args = parser.parse_args()

    if args.drawing_tools:
        result = read_drawing_tools()
        _sdk_utils.output_json(result)
    elif args.name:
        result = read_entry(args.name, args.variant)
        if result is None:
            _sdk_utils.output_error(f"Not found: {args.name}")
        _sdk_utils.output_json(result)
    else:
        parser.print_help()
        _sdk_utils.output_error("Provide a name or use --drawing-tools")


if __name__ == "__main__":
    main()
