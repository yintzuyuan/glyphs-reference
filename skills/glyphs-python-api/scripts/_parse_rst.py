"""RST documentation parser for Glyphs Python API.

Parses the Sphinx-generated index.rst to extract class definitions,
attributes, methods, standalone functions, and constants.

Not meant to be executed directly.
"""

import re
from pathlib import Path


def _read_lines(path: Path) -> list[str]:
    """Read file and return lines with trailing whitespace stripped."""
    return [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()]


def _extract_class_refs(text: str) -> list[str]:
    """Extract :class:`ClassName` references from text."""
    return re.findall(r":class:`(?:[^`]*<)?(\w+)>?`", text)


def _parse_constant_values(init_py_path: Path) -> dict[str, str]:
    """Parse NAME = value assignments from __init__.py constants section."""
    values = {}
    in_constants = False
    for line in _read_lines(init_py_path):
        # Start collecting after the constants marker
        if "def ____CONSTANTS____" in line:
            in_constants = True
            continue
        if not in_constants:
            continue
        # Stop at the end of constants section
        if line.startswith("'''"):
            break
        m = re.match(r"^([A-Z]\w*)\s*=\s*(.+)$", line)
        if m:
            name, val = m.group(1), m.group(2).strip()
            # Normalize: remove comments
            if "#" in val:
                val = val[: val.index("#")].strip()
            values[name] = val
    return values



def _indent_level(line: str) -> int:
    """Count leading tab characters."""
    count = 0
    for ch in line:
        if ch == "\t":
            count += 1
        else:
            break
    return count


def _parse_attribute_block(lines: list[str], start: int) -> dict:
    """Parse a .. attribute:: block starting at the given line.

    Expected format (tab-indented within class):
        .. attribute:: name
            Description text...
            :type: SomeType
            .. code-block:: python
                example code
    """
    line = lines[start]
    # Extract name from ".. attribute:: name" (with possible leading tabs)
    m = re.match(r"\s*\.\. attribute:: (\w+)", line)
    if not m:
        return {}
    name = m.group(1)
    attr_indent = _indent_level(line)
    content_indent = attr_indent + 1

    description_parts = []
    type_str = ""
    examples = []
    in_code_block = False
    code_lines = []
    code_indent = 0

    i = start + 1
    while i < len(lines):
        ln = lines[i]

        # End of attribute block: line at same or lesser indent (non-blank)
        if ln.strip() and _indent_level(ln) <= attr_indent:
            break

        if in_code_block:
            if not ln.strip():
                code_lines.append("")
                i += 1
                continue
            if _indent_level(ln) >= code_indent:
                code_lines.append(ln.strip())
                i += 1
                continue
            else:
                # End of code block
                if code_lines:
                    examples.append("\n".join(code_lines).strip())
                code_lines = []
                in_code_block = False
                continue

        stripped = ln.strip()

        if stripped.startswith(".. code-block::"):
            in_code_block = True
            code_indent = _indent_level(ln) + 1
            code_lines = []
            i += 1
            # Skip blank line after directive
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue

        if stripped.startswith(":type:"):
            type_str = stripped[len(":type:"):].strip()
            # Clean :class:`GSFont` -> GSFont
            type_str = re.sub(r":class:`([^`]*)`", r"\1", type_str)
            i += 1
            continue

        # Skip version directives
        if stripped.startswith(".. versionadded::") or stripped.startswith(".. deprecated::"):
            i += 1
            continue

        if stripped and _indent_level(ln) >= content_indent:
            description_parts.append(stripped)

        i += 1

    if in_code_block and code_lines:
        examples.append("\n".join(code_lines).strip())

    desc = " ".join(description_parts)
    # Clean RST markup from description
    desc = re.sub(r":class:`(?:[^`]*<)?(\w+)>?`", r"\1", desc)
    desc = re.sub(r":(?:attr|meth|func)`[^`]*`", "", desc)

    return {
        "name": name,
        "description": desc.strip(),
        "type": type_str,
        "examples": examples,
    }


def _parse_function_block(lines: list[str], start: int) -> dict:
    """Parse a .. function:: block starting at the given line.

    Works for both class methods (tab-indented) and standalone functions (zero-indent).
    """
    line = lines[start]
    m = re.match(r"\s*\.\. function:: (\w+)\s*(.*)", line)
    if not m:
        return {}
    name = m.group(1)
    raw_params = m.group(2).strip()
    # Clean params: remove outer parens
    if raw_params.startswith("(") and raw_params.endswith(")"):
        raw_params = raw_params[1:-1]
    # Handle trailing colon (e.g., "AskString(...):")
    if raw_params.endswith(":"):
        raw_params = raw_params[:-1]
    if raw_params.endswith(")"):
        # e.g. "AskString(message, value=None, title="Glyphs", OKButton=None, placeholder=None):"
        pass

    func_indent = _indent_level(line)
    content_indent = func_indent + 1

    description_parts = []
    params = []
    return_type = ""
    examples = []
    in_code_block = False
    code_lines = []
    code_indent = 0

    i = start + 1
    while i < len(lines):
        ln = lines[i]

        if ln.strip() and _indent_level(ln) <= func_indent:
            break

        if in_code_block:
            if not ln.strip():
                code_lines.append("")
                i += 1
                continue
            if _indent_level(ln) >= code_indent:
                code_lines.append(ln.strip())
                i += 1
                continue
            else:
                if code_lines:
                    examples.append("\n".join(code_lines).strip())
                code_lines = []
                in_code_block = False
                continue

        stripped = ln.strip()

        if stripped.startswith(".. code-block::"):
            in_code_block = True
            code_indent = _indent_level(ln) + 1
            code_lines = []
            i += 1
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue

        if stripped.startswith(":param "):
            # :param name: description
            pm = re.match(r":param (\w+):\s*(.*)", stripped)
            if pm:
                params.append({"name": pm.group(1), "description": pm.group(2)})
            i += 1
            continue

        if stripped.startswith(":type "):
            # :type name: type — skip (we get type from :param)
            i += 1
            continue

        if stripped.startswith(":return:") or stripped.startswith(":returns:"):
            i += 1
            continue

        if stripped.startswith(":rtype:"):
            return_type = stripped[len(":rtype:"):].strip()
            i += 1
            continue

        if stripped.startswith(".. versionadded::") or stripped.startswith(".. deprecated::"):
            i += 1
            continue

        if stripped and _indent_level(ln) >= content_indent:
            description_parts.append(stripped)

        i += 1

    if in_code_block and code_lines:
        examples.append("\n".join(code_lines).strip())

    desc = " ".join(description_parts)
    desc = re.sub(r":class:`(?:[^`]*<)?(\w+)>?`", r"\1", desc)
    desc = re.sub(r":(?:attr|meth|func)`[^`]*`", "", desc)

    return {
        "name": name,
        "params": raw_params,
        "description": desc.strip(),
        "return_type": return_type,
        "examples": examples,
    }


def parse_classes(rst_path: Path) -> list[dict]:
    """Parse all class definitions from the RST file.

    Returns a list of dicts, each with:
    - name: class name (e.g., "GSFont")
    - description: class description text
    - line: 1-based line number of `.. class::` directive
    - constructor_params: constructor parameters string
    - properties: list of property dicts
    - methods: list of method dicts
    - cross_references: list of referenced class names
    """
    lines = _read_lines(rst_path)
    classes = []

    # Find all .. class:: directives (at zero indent level = top-level RST, but actually tab-indented 0)
    # Classes are defined as ".. class:: ClassName(...)" at zero indent
    class_starts = []
    for i, line in enumerate(lines):
        m = re.match(r"^\.\. class:: (\w+)\s*(.*)", line)
        if m:
            class_starts.append((i, m.group(1), m.group(2).strip()))

    for idx, (class_line, class_name, raw_params) in enumerate(class_starts):
        # Determine the end of this class section
        if idx + 1 < len(class_starts):
            class_end = class_starts[idx + 1][0]
        else:
            # End at Methods section or Constants section or EOF
            class_end = len(lines)
            for j in range(class_line + 1, len(lines)):
                if re.match(r"^Methods\s*$", lines[j]) or re.match(r"^Constants\s*$", lines[j]):
                    class_end = j
                    break

        # Extract description: text between :mod: header and .. class:: directive
        # Look backwards from class_line for the :mod: line
        description_parts = []
        mod_line = None
        for j in range(class_line - 1, max(class_line - 30, 0), -1):
            if re.match(r"^:mod:`" + re.escape(class_name) + r"`", lines[j]):
                mod_line = j
                break

        if mod_line is not None:
            # Description is between the === underline and .. class::
            desc_start = mod_line + 2  # skip :mod: line and === underline
            for j in range(desc_start, class_line):
                stripped = lines[j].strip()
                if stripped and not stripped.startswith(".. "):
                    description_parts.append(stripped)

        # Clean constructor params
        params_str = raw_params
        if params_str.startswith("(") and params_str.endswith(")"):
            params_str = params_str[1:-1]

        # Parse contents within class (indented with tab)
        properties = []
        methods = []
        all_refs = []
        i = class_line + 1
        while i < class_end:
            ln = lines[i]
            stripped = ln.strip()

            # Collect cross-references from all text within class
            if stripped:
                all_refs.extend(_extract_class_refs(stripped))

            # .. attribute:: at indent level 1
            if re.match(r"^\t\.\. attribute:: \w+", ln):
                attr = _parse_attribute_block(lines, i)
                if attr:
                    # Collect refs from attribute description
                    all_refs.extend(_extract_class_refs(attr.get("description", "")))
                    all_refs.extend(_extract_class_refs(attr.get("type", "")))
                    properties.append(attr)
                # Skip past this block
                i += 1
                while i < class_end and (not lines[i].strip() or _indent_level(lines[i]) >= 2):
                    if lines[i].strip():
                        all_refs.extend(_extract_class_refs(lines[i].strip()))
                    i += 1
                continue

            # .. function:: at indent level 1
            if re.match(r"^\t\.\. function:: \w+", ln):
                func = _parse_function_block(lines, i)
                if func:
                    all_refs.extend(_extract_class_refs(func.get("description", "")))
                    methods.append(func)
                i += 1
                while i < class_end and (not lines[i].strip() or _indent_level(lines[i]) >= 2):
                    if lines[i].strip():
                        all_refs.extend(_extract_class_refs(lines[i].strip()))
                    i += 1
                continue

            i += 1

        # Deduplicate cross-references, exclude self
        unique_refs = sorted(set(r for r in all_refs if r != class_name))

        # Build description from parts and code blocks before .. class::
        desc_text = " ".join(description_parts)
        # Clean RST markup from description
        desc_text = re.sub(r":class:`(?:[^`]*<)?(\w+)>?`", r"\1", desc_text)
        desc_text = re.sub(r":attr:`[^`]*`", "", desc_text)
        desc_text = re.sub(r":meth:`[^`]*`", "", desc_text)

        classes.append({
            "name": class_name,
            "description": desc_text.strip(),
            "line": class_line + 1,  # 1-based
            "constructor_params": params_str,
            "properties": properties,
            "methods": methods,
            "cross_references": unique_refs,
        })

    return classes


def parse_standalone_functions(rst_path: Path) -> list[dict]:
    """Parse standalone functions (zero-indent .. function::) after the Methods section.

    Returns a list of dicts with: name, params, description, return_type, examples.
    """
    lines = _read_lines(rst_path)
    functions = []

    # Find the "Methods" section header
    methods_start = None
    for i, line in enumerate(lines):
        if re.match(r"^Methods\s*$", line):
            methods_start = i
            break

    if methods_start is None:
        return functions

    # Find all zero-indent .. function:: after Methods section
    i = methods_start
    while i < len(lines):
        if re.match(r"^\.\. function:: \w+", lines[i]):
            func = _parse_function_block(lines, i)
            if func:
                functions.append(func)
        i += 1

    return functions


def parse_constants(rst_path: Path, init_py_path: Path) -> list[dict]:
    """Parse constants from RST (descriptions/categories) and __init__.py (values).

    Returns a list of dicts with: name, value, description, category.
    """
    lines = _read_lines(rst_path)
    init_values = _parse_constant_values(init_py_path)

    # Find the "Constants" section
    constants_start = None
    for i, line in enumerate(lines):
        if re.match(r"^Constants\s*$", line):
            constants_start = i
            break

    if constants_start is None:
        return []

    constants = []
    current_category = ""

    i = constants_start + 2  # Skip "Constants" and "======="
    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        # Category header: line followed by ====== or ------
        if (
            stripped
            and not stripped.startswith("..")
            and i + 1 < len(lines)
            and re.match(r"^[=\-]+$", lines[i + 1].strip())
        ):
            current_category = stripped
            i += 2  # Skip header and underline
            continue

        # Also handle category as standalone text before == line
        # (some categories like "Path attributes" have blank line before ==)
        if (
            stripped
            and not stripped.startswith("..")
            and i + 2 < len(lines)
            and not lines[i + 1].strip()
            and re.match(r"^[=\-]+$", lines[i + 2].strip())
        ):
            current_category = stripped
            i += 3
            continue

        # .. data:: NAME [= VALUE]
        m = re.match(r"^\.\. data:: (\w+)(?:\s*=\s*(.+))?", ln)
        if m:
            name = m.group(1)
            rst_value = m.group(2).strip() if m.group(2) else None

            # Collect description (indented lines after .. data::)
            desc_parts = []
            j = i + 1
            while j < len(lines):
                dl = lines[j]
                if not dl.strip():
                    # Check if next non-blank line is still indented
                    k = j + 1
                    while k < len(lines) and not lines[k].strip():
                        k += 1
                    if k < len(lines) and lines[k].startswith("\t"):
                        j += 1
                        continue
                    break
                if not dl.startswith("\t"):
                    break
                ds = dl.strip()
                if ds.startswith(".. "):
                    break
                desc_parts.append(ds)
                j += 1

            # Determine value: RST value > __init__.py value
            if rst_value:
                value = rst_value
            elif name in init_values:
                raw = init_values[name]
                value = raw
            else:
                value = ""

            constants.append({
                "name": name,
                "value": value,
                "description": " ".join(desc_parts),
                "category": current_category,
            })

        i += 1

    return constants
