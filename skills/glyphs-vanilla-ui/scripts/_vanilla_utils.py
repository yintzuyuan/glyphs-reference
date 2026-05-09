"""Shared utilities for glyphs-vanilla-ui scripts.

Provides Vanilla path resolution, AST-based import parsing,
class source extraction, and JSON output helpers.
Not meant to be executed directly.
"""

import ast
import json
import os
import sys
from pathlib import Path

# Default Vanilla path inside Glyphs 3
_DEFAULT_VANILLA_PATH = (
    Path.home() / "Library/Application Support/Glyphs 3/Repositories/vanilla/Lib/vanilla"
)


def get_vanilla_path() -> Path:
    """Resolve Vanilla path: GLYPHS_VANILLA_PATH > GLYPHS_REPOSITORIES_PATH > default."""
    env_path = os.environ.get("GLYPHS_VANILLA_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Vanilla library not found at: {path}")
        return path

    repos_path = os.environ.get("GLYPHS_REPOSITORIES_PATH")
    if repos_path:
        path = Path(repos_path) / "vanilla" / "Lib" / "vanilla"
        if path.is_dir():
            return path

    if _DEFAULT_VANILLA_PATH.is_dir():
        return _DEFAULT_VANILLA_PATH

    raise FileNotFoundError(
        "Vanilla library not found. Set GLYPHS_VANILLA_PATH or ensure "
        "Glyphs 3 Repositories are available."
    )


def get_init_py_path() -> Path:
    """Return path to vanilla/__init__.py."""
    return get_vanilla_path() / "__init__.py"


def parse_init_imports(path: Path) -> dict[str, str]:
    """Parse vanilla/__init__.py to build class→module mapping using AST.

    Handles simple imports, multiline imports, and try/except blocks (GridView).
    Returns dict like {"Button": "vanillaButton", "Window": "vanillaWindows"}.
    """
    source = path.read_text()
    tree = ast.parse(source)
    mapping: dict[str, str] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if not node.module or not node.module.startswith("vanilla."):
            continue
        module = node.module.split(".", 1)[1]
        for alias in node.names:
            mapping[alias.name] = module

    return mapping


def extract_class_source(path: Path, class_name: str) -> dict | None:
    """Extract a single class from a source file using AST.

    Returns dict with class_name, bases, docstring, methods, source.
    Returns None if class not found.
    """
    source = path.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue

        bases = [_node_name(b) for b in node.bases]
        docstring = ast.get_docstring(node) or ""

        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                params = _extract_params(item)
                methods.append({"name": item.name, "params": params})

        class_source = _extract_node_source(source, node)

        return {
            "class_name": node.name,
            "bases": bases,
            "docstring": docstring,
            "methods": methods,
            "source": class_source,
        }

    return None


def _node_name(node: ast.expr) -> str:
    """Get the name string from an AST node (Name or Attribute)."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_node_name(node.value)}.{node.attr}"
    return str(node)


def _extract_params(func_node: ast.FunctionDef) -> str:
    """Extract parameter string from a function definition."""
    params = []
    args = func_node.args

    # Count defaults offset
    num_args = len(args.args)
    num_defaults = len(args.defaults)
    default_offset = num_args - num_defaults

    for i, arg in enumerate(args.args):
        if arg.arg == "self":
            continue
        param = arg.arg
        default_idx = i - default_offset
        if 0 <= default_idx < len(args.defaults):
            default_node = args.defaults[default_idx]
            try:
                # ast.literal_eval is safe — only evaluates constant literals
                default_val = ast.literal_eval(default_node)
                param += f"={default_val!r}"
            except (ValueError, TypeError):
                param += "=..."
        params.append(param)

    if args.vararg:
        params.append(f"*{args.vararg.arg}")
    for kwarg in args.kwonlyargs:
        params.append(kwarg.arg)
    if args.kwarg:
        params.append(f"**{args.kwarg.arg}")

    return ", ".join(params)


def _extract_node_source(source: str, node: ast.AST) -> str:
    """Extract source code for an AST node using line numbers."""
    lines = source.splitlines()
    start = node.lineno - 1
    end = node.end_lineno
    return "\n".join(lines[start:end])


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)
