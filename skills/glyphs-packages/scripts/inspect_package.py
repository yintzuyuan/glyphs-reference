#!/usr/bin/env python3
"""Inspect installed Glyphs packages — plugins, scripts, and modules.

Usage:
    inspect_package.py "PackageName"    # Inspect a specific package
    inspect_package.py --list           # List all installed packages
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

import _registry_utils


def _default_repos_path() -> Path:
    """Resolve the Repositories path from env or default location."""
    env = os.environ.get("GLYPHS_REPOSITORIES_PATH")
    if env:
        return Path(env)
    return Path.home() / "Library/Application Support/Glyphs 3/Repositories"


def read_info_plist(plist_path: Path) -> dict:
    """Read an Info.plist file and return its contents as a dict.

    Uses macOS `plutil` to convert binary/XML plist to JSON.
    Returns empty dict if file doesn't exist or conversion fails.
    """
    if not plist_path.exists():
        return {}
    result = subprocess.run(
        ["plutil", "-convert", "json", "-o", "-", str(plist_path)],
        capture_output=True,
    )
    if result.returncode != 0:
        return {}
    return json.loads(result.stdout)


def _find_bundles(pkg_dir: Path) -> list[Path]:
    """Find all Glyphs plugin bundles in a package directory.

    Uses classify_plugin_type() to identify valid bundle extensions.
    """
    return [
        p for p in pkg_dir.iterdir()
        if p.is_dir() and _registry_utils.classify_plugin_type(p.name) != "Unknown"
    ]


def _classify_package(pkg_dir: Path) -> str:
    """Classify a package directory as plugin, module, or scripts.

    Priority: plugin > module > scripts (some plugin repos also have setup.py).
    """
    if _find_bundles(pkg_dir):
        return "plugin"
    if (pkg_dir / "setup.py").exists() or (pkg_dir / "pyproject.toml").exists():
        return "module"
    # Check for .py files with MenuTitle (script collection)
    for py_file in pkg_dir.rglob("*.py"):
        try:
            head = py_file.read_text(errors="ignore")[:500]
            if "# MenuTitle:" in head:
                return "scripts"
        except OSError:
            continue
    return "unknown"


def _find_xcode_source(pkg_dir: Path) -> dict:
    """Find .xcodeproj and related source files for ObjC plugins.

    Strategy: locate .xcodeproj (max depth 3), then search its parent
    directory for .h/.m files.

    Returns:
        Dict with open_source, xcodeproj_path, source_files keys.
    """
    result = {"open_source": False, "xcodeproj_path": None, "source_files": []}

    for xcodeproj in pkg_dir.rglob("*.xcodeproj"):
        relative = xcodeproj.relative_to(pkg_dir)
        if len(relative.parts) > 3:
            continue
        result["open_source"] = True
        result["xcodeproj_path"] = str(relative)
        # Search .h/.m near xcodeproj
        for src_file in xcodeproj.parent.rglob("*.[hm]"):
            result["source_files"].append(str(src_file.relative_to(pkg_dir)))
        result["source_files"].sort()
        break  # Use first match

    return result


def _inspect_plugin(name: str, pkg_dir: Path, bundle: Path) -> dict:
    """Inspect a plugin bundle and return structured metadata."""
    plist_path = bundle / "Contents" / "Info.plist"
    info = read_info_plist(plist_path)

    plugin_type = _registry_utils.classify_plugin_type(bundle.name)
    is_python = "PyMainFileNames" in info
    language = "python" if is_python else "objc"

    # Find entry file for Python plugins
    entry_file = None
    if is_python:
        main_files = info.get("PyMainFileNames", [])
        if main_files:
            candidate = bundle / "Contents" / "Resources" / main_files[0]
            if candidate.exists():
                entry_file = str(candidate.relative_to(pkg_dir))

    # Check for dialog UI
    resources = bundle / "Contents" / "Resources"
    has_dialog = False
    if resources.exists():
        has_dialog = any(
            f.suffix in (".xib", ".nib")
            for f in resources.iterdir()
            if f.is_file()
        )

    # List all files in bundle
    files = sorted(
        str(f.relative_to(pkg_dir))
        for f in bundle.rglob("*")
        if f.is_file()
    )

    result = {
        "name": name,
        "package_type": "plugin",
        "plugin_type": plugin_type,
        "language": language,
        "info_plist": info,
        "entry_file": entry_file,
        "has_dialog": has_dialog,
        "files": files,
    }

    # ObjC plugins: find source code via .xcodeproj
    if language == "objc":
        result.update(_find_xcode_source(pkg_dir))

    # Detect bundled Python API (e.g., Light Table)
    python_api_dir = pkg_dir / "Python API"
    if python_api_dir.is_dir():
        result["has_python_api"] = True
        result["python_api_path"] = str(python_api_dir.relative_to(pkg_dir))
    else:
        result["has_python_api"] = False

    return result


def _inspect_scripts(name: str, pkg_dir: Path) -> dict:
    """Inspect a script collection directory."""
    scripts = []
    for py_file in sorted(pkg_dir.rglob("*.py")):
        try:
            head = py_file.read_text(errors="ignore")[:500]
        except OSError:
            continue
        for line in head.splitlines():
            if line.startswith("# MenuTitle:"):
                title = line.split(":", 1)[1].strip()
                scripts.append({
                    "menu_title": title,
                    "path": str(py_file.relative_to(pkg_dir)),
                })
                break

    subdirectories = sorted(
        d.name for d in pkg_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    return {
        "name": name,
        "package_type": "scripts",
        "scripts": scripts,
        "subdirectories": subdirectories,
    }


def _inspect_module(name: str, pkg_dir: Path) -> dict:
    """Inspect a Python module package."""
    return {
        "name": name,
        "package_type": "module",
        "has_setup_py": (pkg_dir / "setup.py").exists(),
        "has_pyproject_toml": (pkg_dir / "pyproject.toml").exists(),
    }


def inspect(name: str, repos_path: Path) -> dict:
    """Inspect a named package in the Repositories directory.

    Args:
        name: Package directory name (e.g. "ShowAnchors", "mekkablue")
        repos_path: Path to the Repositories directory

    Returns:
        Dict with package metadata, or {"error": "..."} if not found.
    """
    pkg_dir = repos_path / name
    if not pkg_dir.is_dir():
        return {"error": f"Package '{name}' not found in {repos_path}"}

    pkg_type = _classify_package(pkg_dir)

    if pkg_type == "plugin":
        bundles = _find_bundles(pkg_dir)
        return _inspect_plugin(name, pkg_dir, bundles[0])
    elif pkg_type == "scripts":
        return _inspect_scripts(name, pkg_dir)
    elif pkg_type == "module":
        return _inspect_module(name, pkg_dir)
    else:
        return {"name": name, "package_type": "unknown"}


def list_packages(repos_path: Path) -> list[dict]:
    """List all packages in the Repositories directory.

    Returns:
        Sorted list of dicts with name, package_type, and (for plugins) plugin_type.
    """
    if not repos_path.is_dir():
        return []

    packages = []
    for item in sorted(repos_path.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        pkg_type = _classify_package(item)
        entry = {"name": item.name, "package_type": pkg_type}
        if pkg_type == "plugin":
            bundles = _find_bundles(item)
            if bundles:
                entry["plugin_type"] = _registry_utils.classify_plugin_type(
                    bundles[0].name
                )
        packages.append(entry)

    return packages


def main():
    parser = argparse.ArgumentParser(
        description="Inspect installed Glyphs packages"
    )
    parser.add_argument("name", nargs="?", help="Package name to inspect")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all installed packages"
    )
    args = parser.parse_args()

    if not args.name and not args.list:
        parser.error("Either a package name or --list is required")

    repos = _default_repos_path()

    if args.list:
        _registry_utils.output_json(list_packages(repos))
    else:
        result = inspect(args.name, repos)
        if "error" in result:
            _registry_utils.output_error(result["error"])
        else:
            _registry_utils.output_json(result)


if __name__ == "__main__":
    main()
