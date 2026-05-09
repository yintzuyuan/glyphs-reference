"""Shared fixtures for glyphs-packages tests."""

import plistlib
import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Default Repositories path
_DEFAULT_REPOS_PATH = Path.home() / "Library/Application Support/Glyphs 3/Repositories"


@pytest.fixture
def repositories_path():
    """Return the local Repositories path, skip if not present."""
    if not _DEFAULT_REPOS_PATH.exists():
        pytest.skip("Glyphs 3 Repositories not available")
    return _DEFAULT_REPOS_PATH


@pytest.fixture
def env_repos_path(repositories_path, monkeypatch):
    """Set GLYPHS_REPOSITORIES_PATH environment variable."""
    monkeypatch.setenv("GLYPHS_REPOSITORIES_PATH", str(repositories_path))
    return repositories_path


def _write_info_plist(bundle_path: Path, info: dict):
    """Write Info.plist inside a bundle's Contents/ directory."""
    contents = bundle_path / "Contents"
    contents.mkdir(parents=True, exist_ok=True)
    with open(contents / "Info.plist", "wb") as f:
        plistlib.dump(info, f)


@pytest.fixture
def mock_repos(tmp_path):
    """Create mock Repositories/ with various package types for testing.

    Structure:
    - ShowAnchors: Python plugin (Reporter, no dialog)
    - RoundCorner: Python plugin (Filter, with dialog xib)
    - ClosedFilter: ObjC plugin (closed source)
    - speedpunk: ObjC plugin (open source, with .xcodeproj)
    - mekkablue: Script collection (3 scripts in 2 subdirs)
    - fonttools: Python module (has pyproject.toml)
    """
    repos = tmp_path / "Repositories"
    repos.mkdir()

    # --- Python plugin (no dialog): ShowAnchors ---
    sa = repos / "ShowAnchors"
    sa.mkdir()
    bundle = sa / "ShowAnchors.glyphsReporter"
    bundle.mkdir()
    _write_info_plist(bundle, {
        "NSPrincipalClass": "ShowAnchors",
        "PyMainFileNames": ["plugin.py"],
        "CFBundleIdentifier": "com.mekkablue.ShowAnchors",
    })
    res = bundle / "Contents" / "Resources"
    res.mkdir(exist_ok=True)
    (res / "plugin.py").write_text("# ShowAnchors entry point\n")

    # --- Python plugin (with dialog): RoundCorner ---
    rc = repos / "RoundCorner"
    rc.mkdir()
    bundle = rc / "RoundCorner.glyphsFilter"
    bundle.mkdir()
    _write_info_plist(bundle, {
        "NSPrincipalClass": "RoundCorner",
        "PyMainFileNames": ["plugin.py"],
        "CFBundleIdentifier": "com.mekkablue.RoundCorner",
    })
    res = bundle / "Contents" / "Resources"
    res.mkdir(exist_ok=True)
    (res / "plugin.py").write_text("# RoundCorner entry point\n")
    (res / "IBdialog.xib").write_text("<xib/>\n")

    # --- ObjC plugin (closed source): ClosedFilter ---
    cf = repos / "ClosedFilter"
    cf.mkdir()
    bundle = cf / "ClosedFilter.glyphsFilter"
    bundle.mkdir()
    _write_info_plist(bundle, {
        "NSPrincipalClass": "ClosedFilter",
        "CFBundleIdentifier": "com.example.ClosedFilter",
    })
    macos = bundle / "Contents" / "MacOS"
    macos.mkdir(exist_ok=True)
    (macos / "ClosedFilter").write_bytes(b"\x00binary\x00")

    # --- ObjC plugin (open source): speedpunk ---
    sp = repos / "speedpunk"
    sp.mkdir()
    bundle = sp / "SpeedPunk.glyphsReporter"
    bundle.mkdir()
    _write_info_plist(bundle, {
        "NSPrincipalClass": "SpeedPunk",
        "CFBundleIdentifier": "com.yanone.SpeedPunk",
    })
    macos = bundle / "Contents" / "MacOS"
    macos.mkdir(exist_ok=True)
    (macos / "SpeedPunk").write_bytes(b"\x00binary\x00")
    src = sp / "GlyphsSource"
    src.mkdir()
    (src / "SpeedPunk.xcodeproj").mkdir()  # .xcodeproj is a directory
    sp_src = src / "SpeedPunk"
    sp_src.mkdir()
    (sp_src / "SpeedPunk.h").write_text("@interface SpeedPunk\n@end\n")
    (sp_src / "SpeedPunk.m").write_text("@implementation SpeedPunk\n@end\n")

    # --- Script collection: mekkablue ---
    mk = repos / "mekkablue"
    mk.mkdir()
    anchors = mk / "Anchors"
    anchors.mkdir()
    (anchors / "Anchor Mover.py").write_text(
        '# MenuTitle: Anchor Mover\n"""Move anchors across masters."""\n'
    )
    (anchors / "Batch Insert.py").write_text(
        "# MenuTitle: Batch Insert Anchors\n"
    )
    paths_dir = mk / "Paths"
    paths_dir.mkdir()
    (paths_dir / "Path Cleaner.py").write_text(
        "# MenuTitle: Path Cleaner\n"
    )

    # --- Python module: fonttools ---
    ft = repos / "fonttools"
    ft.mkdir()
    (ft / "pyproject.toml").write_text('[project]\nname = "fonttools"\n')

    return repos


@pytest.fixture
def sample_registry_json():
    """Return mock registry JSON data (avoids HTTP dependency).

    Structure matches the output of `plutil -convert json` on the
    official Glyphs plugin/script/module registry plist files.
    """
    return {
        "plugins": [
            {
                "titles": {"en": "Show Anchors"},
                "url": "https://github.com/mekkablue/ShowAnchors",
                "path": "ShowAnchors.glyphsReporter",
                "description": {"en": "Displays anchor names and positions in Edit view."},
            },
            {
                "titles": {"en": "Red Arrow"},
                "url": "https://github.com/jenskutilek/RedArrow-Glyphs",
                "path": "RedArrow.glyphsReporter",
                "description": {"en": "Shows red arrows for outline errors."},
            },
            {
                "titles": {"en": "RoundCorner"},
                "url": "https://github.com/mekkablue/RoundCorner",
                "path": "RoundCorner.glyphsFilter",
                "description": {"en": "Rounds corners of selected nodes."},
            },
            {
                "titles": {"en": "SpeedPunk"},
                "url": "https://github.com/yanone/SpeedPunk",
                "path": "SpeedPunk.glyphsTool",
                "description": {"en": "Visualizes curvature."},
            },
            {
                "titles": {"en": "Palette Tool"},
                "url": "https://github.com/example/PaletteTool",
                "path": "PaletteTool.glyphsPalette",
                "description": {"en": "Adds a palette panel."},
            },
        ],
        "scripts": [
            {
                "titles": {"en": "mekkablue scripts"},
                "url": "https://github.com/mekkablue/Glyphs-Scripts",
                "description": {"en": "Collection of 300+ scripts for Glyphs."},
            },
            {
                "titles": {"en": "Anchor Mover"},
                "url": "https://github.com/example/AnchorMover",
                "description": {"en": "Move anchors across all masters."},
            },
        ],
        "modules": [
            {
                "titles": {"en": "python-fonttools"},
                "url": "https://github.com/fonttools/fonttools",
                "description": {"en": "A library to manipulate font files from Python."},
            },
        ],
    }
