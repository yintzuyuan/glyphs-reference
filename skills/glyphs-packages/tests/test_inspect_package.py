"""Tests for inspect_package.py — package inspection utility."""

import json
import os
import subprocess
import sys
from pathlib import Path

import inspect_package

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestInspectPythonPlugin:
    """Test inspection of Python plugin bundles (has PyMainFileNames)."""

    def test_package_type_is_plugin(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["package_type"] == "plugin"

    def test_language_is_python(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["language"] == "python"

    def test_plugin_type_from_extension(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["plugin_type"] == "Reporter"

    def test_entry_file_found(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["entry_file"].endswith("plugin.py")
        assert "ShowAnchors.glyphsReporter" in result["entry_file"]

    def test_info_plist_has_principal_class(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["info_plist"]["NSPrincipalClass"] == "ShowAnchors"

    def test_info_plist_has_py_main(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert "PyMainFileNames" in result["info_plist"]

    def test_has_dialog_false_when_no_xib(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["has_dialog"] is False

    def test_has_dialog_true_when_xib_present(self, mock_repos):
        result = inspect_package.inspect("RoundCorner", mock_repos)
        assert result["has_dialog"] is True

    def test_files_list_not_empty(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert len(result["files"]) > 0

    def test_name_field(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["name"] == "ShowAnchors"

    def test_no_python_api(self, mock_repos):
        result = inspect_package.inspect("ShowAnchors", mock_repos)
        assert result["has_python_api"] is False


class TestInspectPythonApiPlugin:
    """Test detection of bundled Python API (e.g., Light Table)."""

    def test_has_python_api(self, mock_repos):
        # Create a plugin with Python API directory
        lt = mock_repos / "Light-Table"
        lt.mkdir()
        bundle = lt / "LightTable.glyphsPlugin"
        bundle.mkdir()
        contents = bundle / "Contents"
        contents.mkdir()
        import plistlib
        with open(contents / "Info.plist", "wb") as f:
            plistlib.dump({"NSPrincipalClass": "LightTable"}, f)
        api_dir = lt / "Python API" / "lighttable"
        api_dir.mkdir(parents=True)
        (api_dir / "__init__.py").write_text("# API")

        result = inspect_package.inspect("Light-Table", mock_repos)
        assert result["has_python_api"] is True
        assert result["python_api_path"] == "Python API"


class TestInspectObjcPlugin:
    """Test inspection of Objective-C plugin bundles (no PyMainFileNames)."""

    def test_closed_source_language_is_objc(self, mock_repos):
        result = inspect_package.inspect("ClosedFilter", mock_repos)
        assert result["language"] == "objc"

    def test_closed_source_not_open_source(self, mock_repos):
        result = inspect_package.inspect("ClosedFilter", mock_repos)
        assert result["open_source"] is False

    def test_closed_source_entry_file_is_none(self, mock_repos):
        result = inspect_package.inspect("ClosedFilter", mock_repos)
        assert result["entry_file"] is None

    def test_closed_source_no_xcodeproj(self, mock_repos):
        result = inspect_package.inspect("ClosedFilter", mock_repos)
        assert result["xcodeproj_path"] is None

    def test_closed_source_plugin_type(self, mock_repos):
        result = inspect_package.inspect("ClosedFilter", mock_repos)
        assert result["plugin_type"] == "Filter"

    def test_open_source_detected(self, mock_repos):
        result = inspect_package.inspect("speedpunk", mock_repos)
        assert result["open_source"] is True

    def test_open_source_xcodeproj_found(self, mock_repos):
        result = inspect_package.inspect("speedpunk", mock_repos)
        assert result["xcodeproj_path"] is not None
        assert result["xcodeproj_path"].endswith(".xcodeproj")

    def test_open_source_source_files_found(self, mock_repos):
        result = inspect_package.inspect("speedpunk", mock_repos)
        extensions = {Path(f).suffix for f in result["source_files"]}
        assert ".h" in extensions
        assert ".m" in extensions

    def test_open_source_language_is_objc(self, mock_repos):
        result = inspect_package.inspect("speedpunk", mock_repos)
        assert result["language"] == "objc"


class TestInspectScriptCollection:
    """Test inspection of script collections (dirs with MenuTitle .py files)."""

    def test_package_type_is_scripts(self, mock_repos):
        result = inspect_package.inspect("mekkablue", mock_repos)
        assert result["package_type"] == "scripts"

    def test_lists_scripts_with_menu_title(self, mock_repos):
        result = inspect_package.inspect("mekkablue", mock_repos)
        titles = [s["menu_title"] for s in result["scripts"]]
        assert "Anchor Mover" in titles
        assert "Path Cleaner" in titles
        assert "Batch Insert Anchors" in titles

    def test_scripts_have_relative_path(self, mock_repos):
        result = inspect_package.inspect("mekkablue", mock_repos)
        for script in result["scripts"]:
            assert "path" in script
            assert script["path"].endswith(".py")

    def test_subdirectories_listed(self, mock_repos):
        result = inspect_package.inspect("mekkablue", mock_repos)
        assert "Anchors" in result["subdirectories"]
        assert "Paths" in result["subdirectories"]


class TestInspectModule:
    """Test inspection of Python modules (has setup.py/pyproject.toml)."""

    def test_package_type_is_module(self, mock_repos):
        result = inspect_package.inspect("fonttools", mock_repos)
        assert result["package_type"] == "module"

    def test_has_name(self, mock_repos):
        result = inspect_package.inspect("fonttools", mock_repos)
        assert result["name"] == "fonttools"

    def test_detects_pyproject_toml(self, mock_repos):
        result = inspect_package.inspect("fonttools", mock_repos)
        assert result["has_pyproject_toml"] is True


class TestInspectNotFound:
    """Test error handling for missing packages."""

    def test_returns_error_dict(self, mock_repos):
        result = inspect_package.inspect("nonexistent_xyz", mock_repos)
        assert "error" in result

    def test_error_includes_name(self, mock_repos):
        result = inspect_package.inspect("nonexistent_xyz", mock_repos)
        assert "nonexistent_xyz" in result["error"]


class TestListPackages:
    """Test list_packages() — enumerate all installed packages."""

    def test_lists_all_packages(self, mock_repos):
        result = inspect_package.list_packages(mock_repos)
        names = [p["name"] for p in result]
        assert "ShowAnchors" in names
        assert "mekkablue" in names
        assert "fonttools" in names
        assert "speedpunk" in names

    def test_each_entry_has_package_type(self, mock_repos):
        result = inspect_package.list_packages(mock_repos)
        for pkg in result:
            assert "package_type" in pkg

    def test_plugins_have_plugin_type(self, mock_repos):
        result = inspect_package.list_packages(mock_repos)
        plugins = [p for p in result if p["package_type"] == "plugin"]
        for plugin in plugins:
            assert "plugin_type" in plugin

    def test_sorted_by_name(self, mock_repos):
        result = inspect_package.list_packages(mock_repos)
        names = [p["name"] for p in result]
        assert names == sorted(names, key=str.lower)

    def test_empty_repos(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = inspect_package.list_packages(empty)
        assert result == []

    def test_nonexistent_repos(self, tmp_path):
        result = inspect_package.list_packages(tmp_path / "nope")
        assert result == []


class TestCLI:
    """Test CLI via subprocess."""

    def _run_cli(self, *args, repos_path=None):
        """Run inspect_package.py as subprocess with optional repos override."""
        cmd = [sys.executable, str(SCRIPTS_DIR / "inspect_package.py")]
        cmd.extend(args)
        env = {**os.environ}
        if repos_path:
            env["GLYPHS_REPOSITORIES_PATH"] = str(repos_path)
        return subprocess.run(cmd, capture_output=True, text=True, env=env)

    def test_inspect_python_plugin(self, mock_repos):
        result = self._run_cli("ShowAnchors", repos_path=mock_repos)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["language"] == "python"
        assert data["package_type"] == "plugin"

    def test_inspect_script_collection(self, mock_repos):
        result = self._run_cli("mekkablue", repos_path=mock_repos)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["package_type"] == "scripts"

    def test_list_flag(self, mock_repos):
        result = self._run_cli("--list", repos_path=mock_repos)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_not_found_exits_with_error(self, mock_repos):
        result = self._run_cli("nonexistent_xyz", repos_path=mock_repos)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data

    def test_no_args_shows_error(self):
        result = self._run_cli()
        assert result.returncode != 0
