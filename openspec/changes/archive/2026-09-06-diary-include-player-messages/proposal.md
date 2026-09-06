## Why

`character-diary` 的日記生成只讀 AI 樓層（篩選條件 `!m.is_user && !m.is_system`），玩家的原始輸入從未進入日記 prompt。2026-09-06 對銀趴郵輪 Branch #7 對帳：已處理集合 381 個樓層中玩家樓層為 0。日記因此只看得到角色模型對玩家言行的二手轉述，看不到一手原話；「忠於本次劇情」在結構上無法查證，audit 記錄的 R-2 放大案例（玩家只說過兩次的稱謂指令被寫成「渴望被掌控」）也沒有原始依據可對照。這是「日記品質線 V1」（`task-20260906-diary-quality`）兩步中的第一步，唯一改變的變因是「日記是否看到玩家原始訊息」。

## What Changes

- 新增擴充設定 `includeUserMessagesInDiary`（預設 `true`），設定面板加開關。
- 日記 prompt 的「本次劇情片段」在開關開啟時納入玩家樓層：範圍為「本批第一個 AI 樓層之前最近一個 AI 樓層」之後、到本批最後一個 AI 樓層為止的所有玩家樓層，依原始樓號順序與 AI 樓層交錯排列。
- 場景行格式由 `[#樓號 名字]` 改為 `[#樓號 Player／名字]` 與 `[#樓號 Assistant／名字]`，讓來源身分顯式化。玩家樓層同樣套 `filterTags` 過濾。
- system 要求清單新增一句中性資料說明（依 speaker 與時序理解劇情；角色回覆可能包含對前一則玩家言行的描述）與一行玩家角色名（取自 ST context `name1`，不為其寫日記）。**不**加入去重或 occurrence counting 約束。
- 玩家樓層只在日記 prompt 組裝時從聊天陣列撈取，**不**進入 `windowFloors`、`processedFloors`、`lastFloor`、`_lastDiaryChatLength`，關係與劇情檔案兩路 prompt 不變。
- 把既有但未接線的設定 `autoSummary` 接到設定面板（觀察模式）。旗標本身早已存在於預設值並被兩個入口尊重（`cdOnMessageReceived`、`cdCheckAutoTrigger`），缺的只是可見的開關與保存。它是本步驗收的前置：驗收要在 branch 裡以指定樓層範圍寫日記，期間不能讓自動總結先把樓層吃掉。
- 驗收改為 **ON 態單跑的 solution acceptance**：不做 OFF／ON 對照、不做 A/B 盲化、不做顯著性檢定。從主線最新位置建立 5 個 branch，各演一種玩家事件類型，用既有「补写指定范围」產生真實日記，對照事前寫下的 ground truth 判讀。

## Capabilities

### New Capabilities
- `diary-scene-player-messages`: 日記生成場景納入玩家原始訊息的行為契約（開關、範圍規則、行格式、system 說明、進度機制不受影響）
- `diary-auto-summary-toggle`: 自動總結開關 `autoSummary` 的面板控制與狀態可見性（觀察模式）

### Modified Capabilities
<!-- openspec/specs/ 目前為空，無既有 capability 可修改 -->

## Impact

- **程式**：`D:\AI\SillyTavern\public\scripts\extensions\third-party\character-diary\index.js`（CRLF、約 11,600 行）。該目錄是**獨立 git repo**。2026-09-06 已整理成：`origin` 為上游作者 `zhaoyichan/SillyTavern-Plugin-HCDiary`、`fork` 為使用者的 `azuma520/SillyTavern-Plugin-HCDiary`；本地 `running`（追 `fork/running`）是實際執行的 v2.7.6 加本地修補，本地 `main`（追 `origin/main`）是純上游 v2.13.0、**只看不 checkout**。ST 主 repo 以 `.gitignore:53` 忽略整個 third-party 目錄，所以它不在 SillyTavern 的版控裡，但**在自己的版控裡**。觸及 `cdBuildDiaryPrompt`（746 行起）的 `scene` 組裝與 `sys` 陣列、設定預設值區（約 216 行附近）、設定面板 HTML 與存檔（約 9256 / 9491 行附近）。`data.js` / `engine.js` / `prompts.js` 是源碼切片、改了不生效。
- **保護與回退**：以 git 為主。在該 repo 從乾淨的 `running` 開分支 `diary-player-messages`，改動以 commit 保存，回退為切回 `running`；**絕不從 `main` 開**，那會把整個擴充升到 v2.13.0；CLAUDE.md 的備份硬性要求照做，`.bak` 當額外保險。改後 `node --check`；reload 需 DevTools 勾停用快取再 F5。
- **驗收資料**：會從主線最新位置建立 5 個 SillyTavern branch（各一種玩家事件類型），每個 branch 產生真實日記。主線在建立這 5 個 branch 期間必須凍結、不得寫日記，且所有 branch 直接從主線開、不得 A → B 再分支（理由見 design §Risks 的 branch 繼承條目）。
- **不受影響**：日記 schema、模型、temperature、`interval=5`、`maxWindowFloors=40`、checkpoint 三欄位、`diaryCharFilter` 的登場捕獲（scene 多了玩家名，捕獲到的玩家沒有日記、`if (!list.length) return` 自然略過）。
- **下游**：Learned Self 線的提煉層輸入是日記序列；本改動凍結並觀測完成前，Learned Self 不動（`task-20260906-learned-self` README 已註明）。
