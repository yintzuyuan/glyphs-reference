"""List GlyphsSDK Python Templates and Samples.

Scans Python Templates/ and Python Samples/ directories to enumerate
all available plugin templates and sample implementations.
"""

import argparse
import re

import _sdk_utils

# Map bundle extensions to plugin types
_BUNDLE_EXT_MAP = {
    ".glyphsReporter": "Reporter",
    ".glyphsFilter": "Filter",
    ".glyphsPlugin": "General",
    ".glyphsPalette": "Palette",
    ".glyphsFileFormat": "FileFormat",
    ".glyphsTool": "SelectTool",
}


def _infer_plugin_type_from_bundle(path_str: str) -> str:
    """Infer plugin type from bundle extension in path."""
    for ext, ptype in _BUNDLE_EXT_MAP.items():
        if ext in path_str:
            return ptype
    return ""


def _scan_templates() -> list[dict]:
    """Scan Python Templates/ for plugin.py files."""
    templates_dir = _sdk_utils.get_templates_path()
    entries = []

    for plugin_py in sorted(templates_dir.rglob("plugin.py")):
        rel = plugin_py.relative_to(templates_dir)
        parts = rel.parts

        # Top-level category (File Format, Filter, Reporter, etc.)
        category = parts[0]

        # Variant: subdirectory name if exists (e.g., "dialog with vanilla")
        variant = None
        if len(parts) > 2:
            # Check if there's a variant directory between category and bundle
            candidate = parts[1]
            if not candidate.startswith("____"):
                variant = candidate

        plugin_type = _infer_plugin_type_from_bundle(str(rel))
        # Fallback: use category name mapping
        if not plugin_type:
            plugin_type = re.sub(r"\s+", "", category)

        name = category
        if variant:
            name = f"{category} ({variant})"

        entries.append({
            "name": name,
            "type": "template",
            "plugin_type": plugin_type,
            "variant": variant,
            "path": str(rel),
        })

    return entries


def _scan_samples() -> list[dict]:
    """Scan Python Samples/ for sample directories."""
    samples_dir = _sdk_utils.get_samples_path()
    entries = []

    for subdir in sorted(samples_dir.iterdir()):
        if not subdir.is_dir():
            continue

        name = subdir.name

        # Find the main Python file
        py_files = list(subdir.rglob("plugin.py"))
        if not py_files:
            # Look for standalone .py scripts
            py_files = list(subdir.rglob("*.py"))

        path = ""
        plugin_type = ""
        if py_files:
            main_py = py_files[0]
            path = str(main_py.relative_to(samples_dir))
            plugin_type = _infer_plugin_type_from_bundle(str(main_py))
        else:
            # Directory with only README (e.g., Plugin Preferences)
            readmes = list(subdir.glob("*.md")) + list(subdir.glob("readme.*"))
            if readmes:
                path = str(readmes[0].relative_to(samples_dir))

        entry = {
            "name": name,
            "type": "sample",
            "path": path,
        }
        if plugin_type:
            entry["plugin_type"] = plugin_type

        entries.append(entry)

    return entries


def list_all() -> list[dict]:
    """List all templates and samples."""
    return _scan_templates() + _scan_samples()


def list_by_type(entry_type: str) -> list[dict]:
    """Filter entries by type ('template' or 'sample')."""
    return [e for e in list_all() if e["type"] == entry_type]


def main():
    parser = argparse.ArgumentParser(description="List GlyphsSDK templates and samples")
    parser.add_argument("--type", choices=["template", "sample"],
                        help="Filter by type")
    args = parser.parse_args()

    if args.type:
        result = list_by_type(args.type)
    else:
        result = list_all()

    _sdk_utils.output_json(result)


if __name__ == "__main__":
    main()
