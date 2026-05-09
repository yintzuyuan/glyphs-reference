"""AST-based analysis of GlyphsSDK plugins.py.

Extracts plugin base classes and their methods with type classification:
- protocol: ObjC selector methods (name ends with _), no @objc.python_method
- python_helper: has @objc.python_method decorator
- python_wrapped: regular Python method overrides
"""

import argparse
import ast

import _sdk_utils


def _has_python_method_decorator(node: ast.FunctionDef) -> bool:
    """Check if a function has @objc.python_method decorator."""
    for dec in node.decorator_list:
        # @objc.python_method
        if isinstance(dec, ast.Attribute) and dec.attr == "python_method":
            if isinstance(dec.value, ast.Name) and dec.value.id == "objc":
                return True
    return False


def _classify_method(node: ast.FunctionDef) -> str:
    """Classify a method as protocol, python_helper, or python_wrapped."""
    if _has_python_method_decorator(node):
        return "python_helper"
    if node.name.endswith("_"):
        return "protocol"
    return "python_wrapped"


def _extract_args(node: ast.FunctionDef) -> list[str]:
    """Extract argument names excluding 'self'."""
    return [arg.arg for arg in node.args.args if arg.arg != "self"]


def _extract_method_info(node: ast.FunctionDef) -> dict:
    """Extract method information from a FunctionDef node."""
    info = {
        "name": node.name,
        "type": _classify_method(node),
        "line": node.lineno,
        "args": _extract_args(node),
    }
    docstring = ast.get_docstring(node)
    if docstring:
        info["docstring"] = docstring
    return info


def _find_injected_methods(tree: ast.Module) -> dict[str, list[dict]]:
    """Find methods injected after class definition.

    Pattern: ClassName.method = python_method(func)
    Returns: {class_name: [method_info, ...]}
    """
    injected: dict[str, list[dict]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Attribute):
            continue
        if not isinstance(target.value, ast.Name):
            continue

        # Check if value is python_method(func)
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "python_method":
                class_name = target.value.id
                method_name = target.attr
                if class_name not in injected:
                    injected[class_name] = []
                injected[class_name].append({
                    "name": method_name,
                    "type": "python_helper",
                    "line": node.lineno,
                    "args": [],
                })
    return injected


def parse_plugin_classes() -> list[dict]:
    """Parse plugins.py and extract all plugin base classes with methods."""
    source = _sdk_utils.get_plugins_py_path().read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Known plugin classes (defined in __all__)
    plugin_class_names = {
        "FileFormatPlugin",
        "FilterWithDialog",
        "FilterWithoutDialog",
        "GeneralPlugin",
        "PalettePlugin",
        "ReporterPlugin",
        "SelectTool",
    }

    injected = _find_injected_methods(tree)
    classes = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name not in plugin_class_names:
            continue

        base_class = node.bases[0].id if node.bases and isinstance(node.bases[0], ast.Name) else ""
        methods = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(_extract_method_info(item))

        # Add injected methods
        if node.name in injected:
            methods.extend(injected[node.name])

        classes.append({
            "name": node.name,
            "base_class": base_class,
            "line": node.lineno,
            "methods": methods,
        })

    # Sort by line number
    classes.sort(key=lambda c: c["line"])
    return classes


def search_methods(query: str) -> list[dict]:
    """Search methods across all plugin classes by name substring."""
    query_lower = query.lower()
    results = []
    for cls in parse_plugin_classes():
        for method in cls["methods"]:
            if query_lower in method["name"].lower():
                results.append({
                    "class": cls["name"],
                    **method,
                })
    return results


def identify_method(method_name: str) -> dict | None:
    """Identify a specific method by exact name, return first match."""
    for cls in parse_plugin_classes():
        for method in cls["methods"]:
            if method["name"] == method_name:
                return {"class": cls["name"], **method}
    return None


def get_plugin_methods(plugin_type: str) -> dict | None:
    """Get methods for a specific plugin type (case-insensitive partial match)."""
    plugin_lower = plugin_type.lower()
    for cls in parse_plugin_classes():
        if plugin_lower in cls["name"].lower():
            return cls
    return None


def main():
    parser = argparse.ArgumentParser(description="Search GlyphsSDK plugin methods")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--plugin", help="List methods for a plugin type (e.g. reporter)")
    group.add_argument("--search", help="Search methods by name substring")
    group.add_argument("--method", help="Identify a specific method by exact name")
    args = parser.parse_args()

    if args.plugin:
        result = get_plugin_methods(args.plugin)
        if result is None:
            _sdk_utils.output_error(f"Plugin type not found: {args.plugin}")
        _sdk_utils.output_json(result)
    elif args.search:
        results = search_methods(args.search)
        _sdk_utils.output_json(results)
    elif args.method:
        result = identify_method(args.method)
        if result is None:
            _sdk_utils.output_error(f"Method not found: {args.method}")
        _sdk_utils.output_json(result)
    else:
        # List all classes (summary)
        _sdk_utils.output_json(parse_plugin_classes())


if __name__ == "__main__":
    main()
