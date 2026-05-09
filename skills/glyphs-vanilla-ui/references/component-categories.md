# Vanilla 元件分類導覽

Vanilla 元件大致分為 6 個類別（依官方 index.rst 分類）。每個類別提供代表性元件和發現模式，而非完整列表。

## Windows

視窗容器，是大多數 UI 的最外層。

**發現**：`Grep "^class.*Window\|^class.*Sheet" $VANILLA/vanillaWindows.py`

| 代表元件 | 說明 |
|----------|------|
| `Window` | 標準視窗 |
| `FloatingWindow` | 浮動工具視窗 |
| `Sheet` | 附加在視窗上的表單 |

**Palette 注意**：Palette 外掛不使用 Window，而是用 `Group` 作為容器。

## Layout Views

佈局容器，用來組織子元件的排列方式。

**發現**：`Grep "^class.*(Stack\|Split\|Group\|Box\|Tab\|Scroll)" $VANILLA/`

| 代表元件 | 說明 |
|----------|------|
| `Group` | 通用容器（也是 Palette 的根容器） |
| `Box` | 帶框線的分組容器 |
| `VerticalStackView` / `HorizontalStackView` | Auto Layout 堆疊 |
| `SplitView` / `SplitView2` | 可拖曳分割面板 |
| `Tabs` | 分頁容器 |
| `ScrollView` | 可捲動區域 |

## Data Views

資料顯示元件，用於列表、表格等。

**發現**：`Grep "^class.*(List\|Browser)" $VANILLA/`

| 代表元件 | 說明 |
|----------|------|
| `List` | 傳統列表（含排序、拖曳） |
| `List2` | 新版列表（支援 group rows） |
| `ObjectBrowser` | 物件瀏覽器 |

**提示**：`List2` 相關的 12 個 Cell 類別都在 `vanillaList2.py`（1500+ 行），用 `read_component.py` 精確提取。

## Buttons

按鈕和可點擊控制元件。

**發現**：`Grep "^class.*(Button\|CheckBox\|Radio\|Segmented)" $VANILLA/`

| 代表元件 | 說明 |
|----------|------|
| `Button` | 標準按鈕 |
| `SquareButton` / `ImageButton` / `HelpButton` | 特殊按鈕 |
| `CheckBox` | 核取方塊 |
| `RadioGroup` | 單選按鈕群組 |
| `SegmentedButton` | 分段按鈕 |
| `PopUpButton` / `ActionButton` | 下拉選單 |
| `GradientButton` | 漸層按鈕 |

## Inputs

文字輸入和數值選取。

**發現**：`Grep "^class.*(Edit\|Text\|Combo\|Slider\|Search\|Stepper\|Color\|Date\|Path)" $VANILLA/`

| 代表元件 | 說明 |
|----------|------|
| `EditText` / `SecureEditText` | 文字輸入欄位 |
| `TextBox` | 靜態文字標籤 |
| `TextEditor` | 多行文字編輯器 |
| `ComboBox` | 可輸入的下拉選單 |
| `SearchBox` | 搜尋欄位 |
| `Slider` | 滑桿 |
| `Stepper` | 數值微調器 |
| `ColorWell` | 色彩選取器 |
| `DatePicker` | 日期選取器 |
| `PathControl` | 路徑選取器 |
| `ImageView` | 圖片顯示 |

## Progress Indicators

進度指示元件。

**發現**：`Grep "^class.*(Progress\|Level)" $VANILLA/`

| 代表元件 | 說明 |
|----------|------|
| `ProgressBar` | 水平進度條 |
| `ProgressSpinner` | 旋轉進度指示器 |
| `LevelIndicator` | 等級指示器 |

## 搜尋策略建議

| 查詢意圖 | 最佳方式 |
|----------|----------|
| 查全部元件列表 | `Read $VANILLA/__init__.py` |
| 查特定元件 API | `python3 scripts/read_component.py ComponentName` |
| 查某個方法在哪裡 | `Grep "def methodName" $VANILLA/` |
| 查特定功能的元件 | 用功能關鍵字 `Grep` 搜尋 |
| 查官方文件 | `WebFetch https://vanilla.robotools.dev/en/latest/objects/Name.html` |
| 查元件類別階層 | `Grep "^class.*ClassName" $VANILLA/` 看 bases |
