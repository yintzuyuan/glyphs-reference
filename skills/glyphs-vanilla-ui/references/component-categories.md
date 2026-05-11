# Vanilla Component Category Guide

Vanilla components fall into 6 categories (following the official `index.rst`). Each category lists representative components and a discovery pattern rather than an exhaustive list.

## Windows

Top-level window containers — the outermost layer of most UIs.

**Discover**: `Grep "^class.*Window\|^class.*Sheet" $VANILLA/vanillaWindows.py`

| Component | Description |
|-----------|-------------|
| `Window` | Standard window |
| `FloatingWindow` | Floating tool window |
| `Sheet` | Sheet attached to a window |

**Palette note**: Palette plugins do not use `Window`; they use `Group` as the root container.

## Layout Views

Layout containers used to arrange child components.

**Discover**: `Grep "^class.*(Stack\|Split\|Group\|Box\|Tab\|Scroll)" $VANILLA/`

| Component | Description |
|-----------|-------------|
| `Group` | Generic container (also the root container for Palettes) |
| `Box` | Bordered grouping container |
| `VerticalStackView` / `HorizontalStackView` | Auto Layout stacks |
| `SplitView` / `SplitView2` | Draggable split panes |
| `Tabs` | Tab container |
| `ScrollView` | Scrollable region |

## Data Views

Components for displaying lists, tables, and similar data.

**Discover**: `Grep "^class.*(List\|Browser)" $VANILLA/`

| Component | Description |
|-----------|-------------|
| `List` | Classic list (sorting, drag-and-drop) |
| `List2` | New-style list (supports group rows) |
| `ObjectBrowser` | Object browser |

**Hint**: The 12 cell classes related to `List2` all live in `vanillaList2.py` (1500+ lines). Use `read_component.py` to extract them precisely.

## Buttons

Buttons and clickable controls.

**Discover**: `Grep "^class.*(Button\|CheckBox\|Radio\|Segmented)" $VANILLA/`

| Component | Description |
|-----------|-------------|
| `Button` | Standard button |
| `SquareButton` / `ImageButton` / `HelpButton` | Specialized buttons |
| `CheckBox` | Checkbox |
| `RadioGroup` | Radio button group |
| `SegmentedButton` | Segmented button |
| `PopUpButton` / `ActionButton` | Pop-up / action menus |
| `GradientButton` | Gradient button |

## Inputs

Text input and value selection.

**Discover**: `Grep "^class.*(Edit\|Text\|Combo\|Slider\|Search\|Stepper\|Color\|Date\|Path)" $VANILLA/`

| Component | Description |
|-----------|-------------|
| `EditText` / `SecureEditText` | Text input fields |
| `TextBox` | Static text label |
| `TextEditor` | Multi-line text editor |
| `ComboBox` | Editable drop-down |
| `SearchBox` | Search field |
| `Slider` | Slider |
| `Stepper` | Stepper for numeric values |
| `ColorWell` | Color picker |
| `DatePicker` | Date picker |
| `PathControl` | Path picker |
| `ImageView` | Image display |

## Progress Indicators

Progress indication components.

**Discover**: `Grep "^class.*(Progress\|Level)" $VANILLA/`

| Component | Description |
|-----------|-------------|
| `ProgressBar` | Horizontal progress bar |
| `ProgressSpinner` | Spinning progress indicator |
| `LevelIndicator` | Level indicator |

## Search strategy

| Query intent | Best approach |
|--------------|--------------|
| List every component | `Read $VANILLA/__init__.py` |
| API of a specific component | `python3 scripts/read_component.py ComponentName` |
| Find where a method lives | `Grep "def methodName" $VANILLA/` |
| Components for a specific feature | `Grep` with the feature keyword |
| Official docs | `WebFetch https://vanilla.robotools.dev/en/latest/objects/Name.html` |
| Component class hierarchy | `Grep "^class.*ClassName" $VANILLA/` and read the base list |
