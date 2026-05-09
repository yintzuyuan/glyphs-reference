# Glyphs Packages 結構導覽

## 目錄

- [三層目錄架構](#三層目錄架構)
- [Plugin Bundle 內部結構](#plugin-bundle-內部結構)
- [Script Collections](#script-collections)
- [Python Modules](#python-modules)
- [官方 Registry](#官方-registry)
- [搜尋策略](#搜尋策略)

## 三層目錄架構

```
~/Library/Application Support/Glyphs 3/
├── Repositories/   ← 所有已安裝套件（git clone，plugins + scripts + modules 混合）
├── Scripts/        ← 啟用的腳本集合 + Python 模組（symlink → Repositories/）
└── Plugins/        ← 啟用的外掛 bundle（symlink → Repositories/*.glyphsPlugin）
```

- **Repositories/** 是完整安裝目錄，包含所有透過 Plugin Manager 安裝的套件
- **Scripts/** 和 **Plugins/** 是 Glyphs 實際載入的目錄，內容為指向 Repositories/ 的 symlinks
- 啟用/停用套件 = 建立/移除 symlink

## Plugin Bundle 內部結構

外掛是 macOS bundle 目錄，副檔名表示類型：

| 副檔名 | 類型 | 用途 |
|---------|------|------|
| `.glyphsReporter` | Reporter | 在編輯視圖疊加視覺化資訊 |
| `.glyphsFilter` | Filter | 批次處理路徑（圓角、偏移等） |
| `.glyphsPalette` | Palette | 側邊面板 UI |
| `.glyphsTool` | Tool | 自訂繪圖工具 |
| `.glyphsPlugin` | General | 通用外掛 |
| `.glyphsFileFormat` | FileFormat | 自訂檔案格式匯入/匯出 |

### Python 外掛（Info.plist 有 `PyMainFileNames`）

```
Name.glyphsReporter/
├── Contents/
│   ├── Info.plist          ← NSPrincipalClass + PyMainFileNames
│   ├── MacOS/plugin        ← 二進位 stub（載入 Python runtime）
│   └── Resources/
│       ├── plugin.py       ← Python 入口點 ✅ 可直接讀取
│       ├── IBdialog.xib    ← UI 定義（有 dialog 的外掛才有）
│       └── IBdialog.nib    ← 編譯後的 UI
```

### ObjC 外掛（Info.plist 無 `PyMainFileNames`）

```
Name.glyphsPlugin/
├── Contents/
│   ├── Info.plist          ← NSPrincipalClass（無 PyMainFileNames）
│   ├── MacOS/Name          ← 編譯後二進位 ❌ 不可讀
│   └── Resources/
│       ├── *.nib           ← 編譯後 UI
│       └── *.lproj/        ← 本地化資源
```

原始碼不在 bundle 中。需在 `Repositories/` 搜尋 `.xcodeproj` 定位：
- 有 `.xcodeproj` → 開源，`.h`/`.m` 在其附近
- 無 `.xcodeproj` → 閉源，僅有編譯後 bundle

### 語言判別方式

1. Info.plist 有 `PyMainFileNames` 欄位 → **Python**，入口在 `Contents/Resources/plugin.py`
2. Info.plist 無 `PyMainFileNames` 欄位 → **ObjC**，bundle 內為編譯後二進位

### ObjC 原始碼定位（`.xcodeproj` 錨點法）

三種已驗證的 repo 結構模式：

```
# 模式 A：source 在自訂子目錄
speedpunk/GlyphsSource/SpeedPunk.xcodeproj
speedpunk/GlyphsSource/SpeedPunk/{.h, .m}

# 模式 B：source 在 .xcodeproj 同層
GutenTag/Guten Tag.xcodeproj
GutenTag/Guten Tag/{.h, .m, ...}

# 模式 C：多層巢狀
ShowAngledHandles/ShowAngledHandles/ShowAngledHandles.xcodeproj
ShowAngledHandles/ShowAngledHandles/ShowAngledHandles/{.h, .m}
```

演算法：找到 `.xcodeproj` 後，以其父目錄為基準搜尋 `.h`/`.m` 檔案。

**讀取外掛 metadata**：
```bash
plutil -convert json -o - "Name.glyphsPlugin/Contents/Info.plist"
```

## Script Collections

腳本集合是包含多個 `.py` 檔案的目錄：

### 結構慣例

- 按功能分類在子目錄中（Anchors/、Components/、Paths/ 等）
- 子目錄命名使用英文功能名稱，首字大寫
- 每個 `.py` 檔案是一個獨立腳本

### 腳本格式

每個腳本有：
- `# MenuTitle:` 行 — Glyphs Script 選單中顯示的名稱（**必要**）
- `__doc__` 字串 — 腳本描述（可選，用於 Plugin Manager 顯示）
- 標準 Python 腳本結構，可存取 Glyphs Python API

**發現腳本**：
```bash
Grep "# MenuTitle:" "$SCRIPTS/"
```

## Python Modules

Python 模組套件（fonttools、vanilla 等），可透過 `setup.py` 或 `pyproject.toml` 辨識：
```bash
Glob "$REPOS/*/setup.py"
Glob "$REPOS/*/pyproject.toml"
```

## 官方 Registry

三個分類的 ASCII plist 檔案，託管在 GitHub：
- **plugins** — 外掛 bundle（Reporter、Filter、Palette、Tool 等）
- **scripts** — 腳本集合（mekkablue 為官方最大集合）
- **modules** — Python 模組（fonttools、vanilla、robofab 等）

使用 `search_registry.py` 腳本查詢（內部用 `plutil -convert json` 轉換 plist）。

## 搜尋策略

| 查詢意圖 | 最佳目錄 | 工具 |
|----------|----------|------|
| 找特定功能的腳本 | Scripts/ | `Grep "# MenuTitle:.*keyword"` |
| 查目前啟用的外掛 | Plugins/ | `ls` |
| 瀏覽所有已安裝套件 | Repositories/ | `ls` |
| 查外掛的詳細資訊 | Repositories/ | `inspect_package.py "Name"` |
| 深入檢視套件內部 | Repositories/ | `inspect_package.py "Name"` → 根據結果 `Read` 入口檔 |
| 找尚未安裝的套件 | Registry | `search_registry.py --search "keyword"` |
| 按外掛類型瀏覽 | Registry | `search_registry.py --all --type Reporter` |
