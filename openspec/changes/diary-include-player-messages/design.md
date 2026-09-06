## Context

`character-diary` v2.7.6（本地修補版，位於 `D:\AI\SillyTavern\public\scripts\extensions\third-party\character-diary\index.js`，CRLF；該目錄是獨立 git repo，見下）以獨立 API 生成日記。批次來源 `cdGetNewFloors` 只收 AI 樓層，`cdBuildDiaryPrompt` 把這些樓層拼成「本次剧情片段」。2026-09-06 對帳銀趴郵輪 Branch #7：每批恰 5 個 AI 樓層、已處理集合 381 個樓層中玩家樓層 0 個、玩家訊息中位長度 14 字、AI 訊息中位長度 644 字，AI 回覆開頭固定轉述玩家動作。日記因此只有二手詮釋、沒有一手原話。

本改動是「日記品質線 V1」（`task-20260906-diary-quality`）的 Step 1，設計討論記錄在 `文檔/專案/Diary-Quality/討論共識_2026-09-06.md`（含查證註記）。Step 2（前情語境 overlap 加職責說明）另開 change，等本步觀測結果。

**同檔並行改動（2026-09-06 12:24，另一 session）**：`index.js` 已被 mood 簡繁歸一改動過，現況 hash 前綴 `7d1d596f`、大小 695,843 bytes；對方備份為 `index.js.bak_mood_normalize_20260906_122359`（改前原版），**不得覆蓋、不得用它當本步的起點**。對方改動落在 `cdGetData`（約 1955-1965 行）、`CD_MOOD_T2S` 與 `cdNormalizeMood`（約 7206-7221 行）與三個 mood 寫入點；本步觸及的 `cdBuildDiaryPrompt`（746 行）、`cdTestDiary`（現為 3142 行）、面板列（9291 行）、保存區塊（9524 行）與之不重疊。本步不改 system 內的 mood 列舉值（813 行）。

**版控身分（2026-09-06 查證，推翻「版控外」前提）**：擴充目錄本身是 git repo，`git rev-parse --show-toplevel` 即該目錄。原本只有 `origin`（上游作者 `zhaoyichan/SillyTavern-Plugin-HCDiary`）、本地 `main` 領先上游 1 個未推 commit；上游自 8 月 23 日後又推了 45 個 commit、v2.7.7 到 v2.13.0、`index.js` 淨增約 8,700 行。使用者當日拍板建 fork 並整理成三線結構：

| 分支 | 追蹤 | 內容 | 用途 |
|---|---|---|---|
| `main` | `origin/main` | 純上游 v2.13.0 | 看作者做了什麼；**只看不 checkout**，checkout 會讓正在跑的 ST 載到新版 |
| `running` | `fork/running` | v2.7.6 加本地修補 `2e07c0e`、mood 歸一 `38dd3ec` | 電腦實際在跑的版本；所有自用開發的基底 |
| `running` 底下的 feature branch | `fork/<name>` | 單一開發項 | 本 change 用 `diary-player-messages` |

長期規則（使用者 2026-09-06 拍板）：自用功能從 `running` 開；要貢獻上游的功能從最新 `main` 另開 PR branch，把已驗證的 commit cherry-pick 或重新移植過去、在新版上重測、再從 fork 對上游開 PR。**不拿 `running` 直接對上游開 PR**。另一 session 的 mood 歸一改動已由本 session 依使用者指示 commit 為 `38dd3ec`（`running` HEAD，已推 `fork/running`），工作樹乾淨、可直接開分支。

約束：
- 保護與回退以 git 為主：從乾淨的 `running` 開分支 `diary-player-messages`，改動 commit 在分支上；回退為切回 `running`。分支要等對方的 mood commit 落地後再開，避免把兩個工作單位混在同一個 diff。
- CLAUDE.md 硬性要求：改 `index.js` 前備份、改後 `node --check`；`data.js` 等切片改了不生效；reload 需 DevTools 勾停用快取。
- 單變因：本步唯一改變的機制假設是「日記是否看到玩家原始訊息」。
- 凍結不動：`interval`、`maxWindowFloors`、日記 schema、模型、temperature、checkpoint 三欄位、關係與檔案 prompt。

## Goals / Non-Goals

**Goals:**
- 日記 prompt 的場景含玩家原話，且來源身分顯式化。
- 開關可退回，兩態差異只有玩家行。
- 測試路徑能對同批樓層產出未截斷的 OFF／ON 成對材料。
- 進度機制零改動、零副作用。

**Non-Goals:**
- 前情 overlap、資料塊職責標籤（Step 2）。
- 去重、發生次數約束、regex 禁詞。
- 把玩家樓層納入已處理集合或關係／檔案 prompt。
- 修改日記 schema、觸發節奏、視窗上限、模型參數。

## Decisions

**D1 玩家樓層在 prompt 組裝時從聊天陣列撈，不進 `windowFloors`。**
`windowFloors` 同時是已處理集合的批次 id 來源（`_batchIds`）、`mergeDiaries` 的 `topFloor` 來源、關係與檔案 prompt 的輸入。把玩家樓層塞進去會一次動到四個地方。替代方案「加進 `windowFloors` 再在下游各自濾掉」改動面更大、且違反「進度機制不動」。

**D2 範圍規則：前一個 AI 樓層之後、本批最後一個 AI 樓層之前。**
本批第一個 AI 回覆所回應的玩家輸入一定在此範圍內；積壓被截到 40 時以截後第一個 AI 樓層為準，不擴及被截掉的部分。替代方案「本批第一個 AI 樓層減一」在玩家連發或刪除回覆時會漏；「上次 `lastFloor` 之後」在截到上限時範圍會失控。實作上以聊天陣列從本批第一個 AI 樓號往前掃到第一個 `!is_user && !is_system` 為止，找不到則從 0 開始。

**D3 行格式 `[#樓號 Player／名字]`、`[#樓號 Assistant／名字]`，兩態皆用。**
來源與名字並列是讓資料身分顯式化的直接表達。格式在 OFF 態也生效，這樣 OFF 與 ON 的唯一差異就是玩家行，對照才乾淨。代價是 OFF 態與改動前的 prompt 不逐字相同；接受，因為對照對象是同版本的兩態、不是歷史版本。

**D4 system 加中性資料說明，不加去重規則。**
使用者 2026-09-06 拍板：先靠明確 speaker、時序與資訊角色觀察模型表現；「玩家說一次加 AI 轉述一次被當成兩次」若在 ON 組實測出現，再升級成規則，證據較乾淨。說明放 system 要求清單，不放資料塊標籤（標籤會被模型撿去當台詞，見 `LearnedSelf_MVP設計.md` §二）。

**D5 開關 `includeUserMessagesInDiary` 預設 `true`。**
依既有設定風格（`cdGetSettings` 的預設物件、`cds-row` 面板列、保存區塊的 `$('#…').is(':checked')`）加一項。

**D6 玩家名取自 `SillyTavern.getContext().name1`，取不到用「主角」。**
擴充已有同樣做法（`index.js` 約 7294 行的 `protName`），沿用其 try／catch 形狀。

**D7 測試路徑補「完整材料」記錄。**
`cdAddLog` 的 localStorage 副本把 detail 截到 500 字，但 console 輸出的是完整物件。在 `cdTestDiary` 的日記分支加一筆 `cdAddLog('info', '测试 [日记] 完整材料', { usr, response })` 並寫 `window.__cdLastDiaryTest = { scene, sys, usr, response, includeUser }`。替代方案「加匯出按鈕」改 UI、超出本步範圍。

## Risks / Trade-offs

- [`diaryCharFilter` 的登場捕獲把玩家名當成登場角色] → 玩家沒有日記，`if (!list.length) return` 自然略過；驗證時檢查捕獲 log 確認沒有為玩家生成日記。
- [模型為玩家寫日記] → system 已有「不要为用户/玩家角色写日记」，本改動再加玩家名明示；OFF／ON 對照時檢查 `npcs` 是否出現玩家名。
- [玩家訊息含 OOC 或指令語句被當劇情] → 本聊天玩家樓層無標籤、中位 14 字；套用 `filterTags` 後風險與 AI 樓層相同。若觀測到，屬 Step 2 以後的資料身分問題，不在本步加規則。
- [OFF 態與改動前 prompt 不逐字相同（D3）] → 明示於 spec；歷史日記不重跑、不當基線。
- [擴充 repo 的 `origin` 是上游作者、本地 commit 無處可推] → 已建 fork，`running` 已推上 `fork/running`；feature branch 完成後也推到 `fork`。rollback 為關開關（行為層）、切回 `running`（程式層）、還原 `.bak`（最後保險）。

## Migration Plan

1. 在擴充 repo 確認目前在 `running`、`git status` 乾淨（對方 mood commit 已落地、無未 commit 改動），記下 `running` 的 HEAD hash；`git switch -c diary-player-messages`；再備份為 `index.js.bak_include_player_msgs_<YYYYMMDD_HHMM>`（`.bak` 不加進 commit）。
2. 改設定預設值、`cdBuildDiaryPrompt`、設定面板、保存區塊、`cdTestDiary`。
3. `node --check index.js`。
4. ST 開著時 DevTools 勾停用快取後 F5；確認設定面板出現開關且預設開。
5. 對當下待處理批次跑測試路徑 OFF、ON 各一次，取材料。
6. 改完 `git commit`（英文訊息）。回退：關開關即回到只有 AI 行；程式層回退為 `git switch running`；`.bak` 為最後保險。

## 驗證設計（CLAUDE.md 驗證前置 Gate 五問）

本步的結果會用來決定 Step 2 是否繼續、以及日記是否能當 Learned Self 上游，屬 decision-bearing，適用五問。

- **Observation**：觀察點為測試路徑產出的完整 prompt 與回應（D7），以及 `processedFloors` 與 `data.diaries` 在測試前後的內容。三者皆可從 console、`window.__cdLastDiaryTest` 與聊天檔第一行 metadata 取得。
- **Discrimination**：判準為共識 §13 第 1、4、5 項的人工判讀（是否集中於新增經歷、是否無依據放大舊結論、無變化時是否自然延續），加一項機械項（`npcs` 不含玩家名）。人工判讀由使用者盲讀：兩份輸出去掉標記後隨機排序再判。**樣本量**：每批一組 OFF／ON，累積至少 5 組再下結論；n=5 只能判「方向」，不能判幅度。在 5 組前不得把觀察升格為結論。
- **Construct**：要驗的是「補上一手玩家資訊是否改善日記對事件、玩家意圖與角色心理的理解」；量的是同批同版本兩態的日記文本差異，不是重複率、不是字數。重複句只當觀察項。
- **Instrument**：D7 的記錄先用一批已知內容校準：ON 態的 usr 必須逐行含該批範圍內全部玩家樓層（用 python 從聊天檔算出預期樓號集合對帳），OFF 態必須零 `Player` 行。校準通過後不再改記錄程式；若之後要改，先記錄 hash 再改。
- **Occurrence**：每次測試前後讀聊天檔 metadata，確認 `processedFloors` 長度與 `diaries` 各角色篇數不變（測試路徑不寫入的證據）；確認 console 真的有「测试 [日记] 完整材料」那筆，沒有就是沒跑，不得讀空。

## Open Questions

- 盲讀的隨機化與去標記由誰執行：預設由我在交付材料時做（去掉 `Player` 行的存在提示不可能，因為判讀對象是日記輸出、不是 prompt；只需隱藏「哪份是 ON」）。
- 5 組樣本要多久：每批 5 個 AI 樓層，正常遊玩約 5 到 10 樓一組，視使用者遊玩節奏；不催。
