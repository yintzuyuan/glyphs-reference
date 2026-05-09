# GlyphsCore Headers 分類導覽

174 個 header 檔案可大致分為以下類別。每個分類提供發現模式和代表性檔案，而非完整列表。

## Core Data Model

字型資料結構的核心類別。

**發現**：`Grep "@interface GS(Font|Glyph|Layer|Path|Node|Component|Anchor)" path/to/Headers/`

| 代表檔案 | 說明 |
|----------|------|
| `GSFont.h` | 字型文件（含 masters、instances、glyphs） |
| `GSFontMaster.h` | 字型 master（含 metrics、custom parameters） |
| `GSGlyph.h` | 字符（含 layers、unicode） |
| `GSLayer.h` | 圖層（含 paths、components、anchors） |
| `GSPath.h` / `GSNode.h` | 路徑和節點 |
| `GSComponent.h` | 組件參照 |
| `GSAnchor.h` / `GSGuide.h` | 定位標記和參考線 |
| `GSInstance.h` | 匯出實例 |
| `GSShape.h` / `GSElement.h` | Shape/Element 基礎類別 |

**注意**：核心類別通常有多個 category 擴展（`GSLayer+PathOperations.h` 等），用 `Glob path/to/Headers/ClassName+*.h` 查找。

## Plugin Protocols

外掛開發必須實作的 protocol 定義。

**發現**：`Glob path/to/Headers/*Protocol*.h`

| 代表檔案 | 說明 |
|----------|------|
| `GlyphsPluginProtocol.h` | 基礎外掛 protocol |
| `GlyphsReporterProtocol.h` | Reporter 外掛（視覺化覆蓋） |
| `GlyphsFilterProtocol.h` | Filter 外掛（路徑處理） |
| `GlyphsPaletteProtocol.h` | Palette 外掛（側邊面板） |
| `GlyphsToolProtocol.h` | Tool 外掛（繪圖工具） |
| `GlyphsFileFormatProtocol.h` | 檔案格式外掛 |
| `GlyphsToolDrawProtocol.h` | Tool 繪製介面 |
| `GlyphsToolEventProtocol.h` | Tool 事件處理介面 |
| `GSAppDelegateProtocol.h` | App delegate 存取介面 |

## OpenType & Typography

OpenType feature、hinting、metrics 相關。

**發現**：`Grep "Feature\|Hint\|Metric\|Kern" path/to/Headers/ --glob "*.h" --output_mode files_with_matches`

| 代表檔案 | 說明 |
|----------|------|
| `GSFeature.h` / `GSFeaturePrefix.h` | OpenType feature 定義 |
| `GSFeatureComposer.h` / `GSFeatureGenerator.h` | Feature 自動產生 |
| `GSHint.h` / `GSTTStem.h` | Hinting 資訊 |
| `GSMetric.h` / `GSMetricValue.h` | Metrics 定義 |
| `GSAlignmentZone.h` | 對齊區域 |
| `GSCustomParameter.h` | 自訂參數 |
| `GSFontInfoProperty.h` / `GSFontInfoValue*.h` | 字型資訊欄位 |

## UI Controllers & Views

Inspector、dialog、panel 等 UI 元件。

**發現**：`Glob path/to/Headers/InspectorView*.h` 和 `Grep "Controller\|View" path/to/Headers/ --glob "GS*Controller*.h"`

| 代表檔案 | 說明 |
|----------|------|
| `InspectorView*Controller.h` | 12 個 Inspector 面板控制器 |
| `GSDialogController.h` / `GSDialogContentView.h` | 對話框 |
| `GSPanelViewController.h` / `GSPanelView.h` | 面板 |
| `GSGlyphEditViewProtocol.h` | 編輯視圖介面 |
| `GSWindowControllerProtocol.h` | 視窗控制器介面 |
| `GSGlyphCell.h` / `GSGlyphCellView.h` | 字符格視圖 |
| `GSProgressWindowController.h` | 進度視窗 |

## Drawing & Geometry

路徑繪製、幾何運算、Pen protocol。

**發現**：`Grep "Pen\|Bezier\|Geometrie\|Path" path/to/Headers/ --glob "GS*.h" --output_mode files_with_matches`

| 代表檔案 | 說明 |
|----------|------|
| `GSPenProtocol.h` | Pen protocol 定義 |
| `GSBasePen.h` / `GSSegmentPen.h` / `GSPathPen.h` | Pen 實作 |
| `GSGeometrieHelper.h` | 幾何運算工具 |
| `GSPathOperator.h` / `GSPathSegment.h` | 路徑運算 |
| `GSFlattenPen.h` / `GSSVGPen.h` / `GSBezStringPen.h` | 特殊用途 Pen |
| `GSProxyShapes.h` | 代理形狀 |

## Foundation Categories

NSObject/NSString/NSBezierPath 等 Foundation 類別的擴展。

**發現**：`Glob path/to/Headers/NS*.h`

| 代表檔案 | 說明 |
|----------|------|
| `NSBezierPath+*.h` | BezierPath 擴展（4 個） |
| `NSString*.h` | 字串工具 |
| `NSImage+*.h` | 圖片擴展 |
| `NSArrayHelpers.h` / `NSDictionaryHelpers.h` | 集合工具 |

## Misc / Utilities

不屬於上述分類的工具類別。

**發現**：瀏覽剩餘的 `GS*.h` 檔案

| 代表檔案 | 說明 |
|----------|------|
| `GSUndoManager.h` | Undo 管理 |
| `GSCallbackHandler.h` | 回調處理 |
| `GSClass.h` / `GSSubstitution.h` | OpenType class 和替換 |
| `GSInterpolationFontProxy.h` | 內插代理 |
| `GSOutlineImporter.h` | 輪廓匯入 |
| `GlyphsCore.h` | Framework 主要 header |

## 搜尋策略建議

| 查詢意圖 | 最佳方式 |
|----------|----------|
| 查特定類別的完整 API | `Read` 該類別的 `.h` 檔 + `Glob` 其 `+*.h` 擴展 |
| 查 protocol 需要實作什麼 | `Read` 對應的 `*Protocol.h` 檔，注意 `@optional` 區隔 |
| 查某個方法在哪裡宣告 | `Grep "methodName"` 搜尋所有 headers |
| 查特定功能相關的所有類別 | 用功能關鍵字 `Grep` 搜尋，再逐一 `Read` |
| 查列舉值或常數 | `Grep "typedef.*enum\|extern\|#define"` |
