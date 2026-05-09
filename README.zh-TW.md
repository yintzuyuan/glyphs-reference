[English](README.md) | **繁體中文**

# glyphs-reference

涵蓋 Glyphs.app 文件的 Claude Code plugin，內含 10 個 Skills：Python/Obj-C API、檔案格式、SDK 參考、Vanilla UI、套件管理、在地化、網頁搜尋。

> 取代舊版 [`glyphs-info-mcp`](https://github.com/yintzuyuan/glyphs-info-mcp) MCP server，透過 Claude Skills 的 progressive disclosure 設計，token 使用量降低約 98%。

## 內容速覽

| Skill | 涵蓋 |
|-------|------|
| `glyphs-python-api` | Python 腳本 API 參考 |
| `glyphs-objc-headers` | Objective-C 插件 headers |
| `glyphs-sdk-reference` | 插件 SDK 參考、Templates、Samples |
| `glyphs-vanilla-ui` | Vanilla UI 函式庫（Glyphs 插件 UI 用） |
| `glyphs-file-format` | `.glyphs` / `.glyphspackage` 檔案格式規格 |
| `glyphs-light-table` | Light Table 擴充 API |
| `glyphs-localization` | Glyphs 在地化資料與語言代碼 |
| `glyphs-packages` | 套件管理流程 |
| `glyphs-remote-scripts` | 遠端腳本 API 參考 |
| `glyphs-web-search` | Glyphs handbook 網頁搜尋 |

另外含一個 meta-search agent（`agents/glyphs-meta-search.md`）支援跨 skill 查詢。

## 環境需求

- 已安裝 [Claude Code](https://docs.claude.com/en/docs/claude-code)
- macOS（Glyphs.app 開發工作流需要）
- 選用：[`GlyphsSDK`](https://github.com/schriftgestalt/GlyphsSDK) — 作為 submodule 提供給 `glyphs-sdk-reference` 使用

## 安裝方式

### 直接從本 repo（個人使用推薦）

克隆時帶上 submodules（取得 GlyphsSDK）：

```bash
git clone --recurse-submodules https://github.com/yintzuyuan/glyphs-reference.git
```

如果已克隆但沒拉 submodules：

```bash
git submodule update --init --recursive
```

接著在 Claude Code 中將克隆的目錄指定為 local plugin source 即可使用。

### 透過自訂 marketplace

如果你維護自己的 Claude Code plugin marketplace，可在 marketplace 的 `plugins/` 目錄下用 submodule 引用本 repo，再透過你習慣的 marketplace 工作流使用。

目前尚未發布專屬公開 marketplace；若使用需求增加，未來可能建立。

## 從 glyphs-info-mcp 遷移

如果你之前使用 [`glyphs-info-mcp`](https://github.com/yintzuyuan/glyphs-info-mcp)（MCP server 版本）：

- 該 MCP 已進入**維護模式**，**推薦遷移到本 plugin**
- 相同資料，~98% 更低 token 用量（progressive disclosure 按需載入）
- 遷移步驟：
  1. 從 `claude_desktop_config.json` 中移除 `glyphs-info-mcp` 設定（或在你的環境中停用）
  2. 安裝本 plugin（見上方 Installation）
  3. Skills 會自動被發現，無需手動配置

## 為什麼用 Skills 不用 MCP

原 `glyphs-info-mcp` 是 stdio MCP server。每個 Claude Code 對話都會 eager-load 全部 150K+ tokens 的 API 文件，不管使用者有沒有實際查 Glyphs API。

Skills 的 progressive disclosure 只載入需要的部分：上前 ~2K tokens 是 skill 描述，完整內容按需 fetch。對一般對話來說，這節省約 98% token 預算。

這呼應 Anthropic 對 progressive disclosure 的論述：「loading all tool definitions upfront and passing intermediate results through the context window slows down agents and increases costs」（[Anthropic engineering blog: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)）。同篇舉例 token 從 150,000 降到 2,000，約節省 98.7%。

## 貢獻

歡迎 PR 與 Issue。參考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 授權

MIT — 詳見 [LICENSE](LICENSE)。

## 致謝

- Glyphs SDK 由 [Schriftgestaltung GbR](https://glyphsapp.com/) 維護
- 設計理念受 Anthropic [progressive disclosure 論述](https://www.anthropic.com/engineering/code-execution-with-mcp) 啟發
- 用 [Claude Code](https://docs.claude.com/en/docs/claude-code) 建構
