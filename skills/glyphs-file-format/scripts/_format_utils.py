"""Shared utilities for GlyphsFileFormat query scripts.

Provides SDK path resolution, spec definition extraction, and JSON Schema
querying. Not meant to be executed directly.
"""

import json
import os
import re
import sys
from pathlib import Path

# Relative path from scripts/ to GlyphsSDK
_RELATIVE_SDK_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "GlyphsSDK"

# Version tag mapping: format version -> anchor tag version
_VERSION_TAG = {2: "1", 3: "3"}


def get_sdk_path() -> Path:
    """Resolve GlyphsSDK path: GLYPHS_SDK_PATH env var > relative path."""
    env_path = os.environ.get("GLYPHS_SDK_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_dir():
            raise FileNotFoundError(f"GlyphsSDK not found at: {path}")
        return path

    if _RELATIVE_SDK_PATH.is_dir():
        return _RELATIVE_SDK_PATH

    raise FileNotFoundError(
        "GlyphsSDK not found. Set GLYPHS_SDK_PATH or ensure the submodule is cloned."
    )


def get_file_format_path() -> Path:
    """Return path to GlyphsSDK/GlyphsFileFormat/."""
    return get_sdk_path() / "GlyphsFileFormat"


def get_spec_path(version: int) -> Path:
    """Return path to GlyphsFileFormatv{version}.md."""
    return get_file_format_path() / f"GlyphsFileFormatv{version}.md"


def get_schema_path(schema_name: str) -> Path:
    """Return path to Schemas/{schema_name}.schema.json."""
    return get_file_format_path() / "Schemas" / f"{schema_name}.schema.json"


def extract_definition(spec_text: str, name: str, *, version: int) -> str | None:
    """Extract a single definition from spec markdown by name.

    Finds the anchor `<a name="spec-glyphs-{tag}-{name}">` and returns
    all text from that line up to (but not including) the next top-level
    definition anchor or `## ` heading.
    """
    tag = _VERSION_TAG.get(version, str(version))
    anchor = f'<a name="spec-glyphs-{tag}-{name}">'

    lines = spec_text.splitlines()
    start_idx = None

    for i, line in enumerate(lines):
        if anchor in line:
            start_idx = i
            break

    if start_idx is None:
        return None

    end_idx = len(lines)
    anchor_prefix = f'<a name="spec-glyphs-{tag}-'

    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        # Next top-level definition (starts with "- <a name=")
        if line.startswith("- ") and anchor_prefix in line:
            end_idx = i
            break
        # Next heading
        if line.startswith("## "):
            end_idx = i
            break

    return "\n".join(lines[start_idx:end_idx]).rstrip()


def list_definitions(spec_text: str, *, version: int) -> list[dict]:
    """List all definitions in the spec, returning [{name, gs_class}]."""
    tag = _VERSION_TAG.get(version, str(version))
    pattern = re.compile(
        rf'<a name="spec-glyphs-{tag}-([^"]+)">'
        r"</a>.*?<strong>([^<]+)</strong>"
    )
    gs_class_pattern = re.compile(r"\(`(GS\w+)`\)")

    results = []
    for line in spec_text.splitlines():
        if not line.startswith("- "):
            continue
        match = pattern.search(line)
        if not match:
            continue
        name = match.group(1)
        gs_match = gs_class_pattern.search(line)
        gs_class = gs_match.group(1) if gs_match else None
        results.append({"name": name, "gs_class": gs_class})

    return results


def extract_schema_def(schema_data: dict, name: str) -> dict | None:
    """Extract a single definition from JSON Schema $defs."""
    defs = schema_data.get("$defs", {})
    return defs.get(name)


def list_schema_defs(schema_data: dict) -> list[str]:
    """List all $defs keys from a JSON Schema."""
    return sorted(schema_data.get("$defs", {}).keys())


def output_json(data):
    """Print data as indented JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_error(message: str):
    """Print error as JSON and exit with code 1."""
    print(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    sys.exit(1)
