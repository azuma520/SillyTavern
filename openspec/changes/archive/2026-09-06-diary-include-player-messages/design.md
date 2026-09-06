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
- 開關可退回：關閉時場景回到只有 AI 行，其餘行為不變。
- 觀察模式可從面板控制：`autoSummary` 有可見開關，關閉時使用者看得出目前是關的。
- 進度機制零改動、零副作用。

**Non-Goals:**
- 前情 overlap、資料塊職責標籤（Step 2）。
- 去重、發生次數約束、regex 禁詞。
- 把玩家樓層納入已處理集合或關係／檔案 prompt。
- 修改日記 schema、觸發節奏、視窗上限、模型參數。
- **採樣器**（一鍵 OFF／ON 雙跑、機械 request diff、隨機執行順序、A/B 盲化與 blind key、每情境重複生成）。2026-09-06 驗收改為 ON 態單跑後全部不做；既有 UI（觀察模式 + `补写指定范围`）已足夠。
- 修 `cdCheckAutoTrigger` 的計數不一致，與 branch 繼承幽靈 `processedFloors`（兩者皆已登記為獨立 backlog `[bug]`，不在本 change 修）。

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

**D8 觀察模式沿用既有 `autoSummary`，不新增旗標。**
2026-09-06 查證：`autoSummary` 已在 `DEFAULT_SETTINGS`（`index.js:212`，預設 `true`），且 `cdOnMessageReceived`（`:4879`）與 `cdCheckAutoTrigger`（`:3298`）兩個入口都已尊重它；`cdSaveSettings` 是 `Object.assign(cdGetSettings(), patch)` 的 merge（`:1855`），保存區塊沒有這個欄位所以按「应用设置」不會洗掉它。缺的只有面板控制與狀態可見性。替代方案「新增一個 `observationMode` 旗標」會製造兩個語意重疊的開關，且要在兩個 gate 各加一次判斷。

**注意：`autoSummary` 與 `includeUserMessagesInDiary` 都是全域設定**（`extension_settings['character-diary']`，非 chat metadata），一次設定對主線與所有 branch 同時生效。因此驗收期間只需關閉一次；相對地，**實驗結束後必須明確開回來**，否則主線會從此靜默停止寫日記。這是操作面的單向風險，收尾步驟必須包含它。

**D7 測試路徑補「完整材料」記錄。**
`cdAddLog` 的 localStorage 副本把 detail 截到 500 字，但 console 輸出的是完整物件。在 `cdTestDiary` 的日記分支加一筆 `cdAddLog('info', '测试 [日记] 完整材料', { usr, response })` 並寫 `window.__cdLastDiaryTest = { scene, sys, usr, response, includeUser }`。替代方案「加匯出按鈕」改 UI、超出本步範圍。

## Risks / Trade-offs

- [`diaryCharFilter` 的登場捕獲把玩家名當成登場角色] → 玩家沒有日記，`if (!list.length) return` 自然略過；驗證時檢查捕獲 log 確認沒有為玩家生成日記。
- [模型為玩家寫日記] → system 已有「不要为用户/玩家角色写日记」，本改動再加玩家名明示；OFF／ON 對照時檢查 `npcs` 是否出現玩家名。
- [玩家訊息含 OOC 或指令語句被當劇情] → 本聊天玩家樓層無標籤、中位 14 字；套用 `filterTags` 後風險與 AI 樓層相同。若觀測到，屬 Step 2 以後的資料身分問題，不在本步加規則。
- [OFF 態與改動前 prompt 不逐字相同（D3）] → 明示於 spec；歷史日記不重跑、不當基線。
- [注入的記憶段隨場景內容而變，5 個 branch 之間不會相同] → `s.diaryCharFilter` 為 true（使用者現值）時，`cdCaptureCast(scene, data)` 以整段 scene 全文比對角色名決定注入誰的近期日記。ON 態多出的玩家原話會讓捕獲名單可能改變；不同 branch 的劇情不同，捕獲名單也會不同。**這是已知的變異來源，ON 態單跑無法消除**。因為驗收改為 solution acceptance（不做兩態因果歸因），可以接受；但判讀時仍須連同 `usr` 全文一起看，不得只看日記輸出就推論成因。行首格式改動本身不影響捕獲（比對不依賴行首）。原文寫的是 OFF／ON 對照下的歸因風險（2026-09-06 實作時揭露），改為 ON-only 後歸因問題消失、變異來源仍在，故保留為註記。
- [從歷史 checkpoint 建 branch 會繼承幽靈 `processedFloors` 與未來日記] → `createBranch`（`bookmarks.js:186`）只傳 `{main_chat}`，`saveChat`（`script.js:7347`）做 `{...chat_metadata, ...withMetadata}`，chat 內容被截到 `mesId` 但 metadata 沒有。`lastFloor` 會被 `cdOnMessageReceived:4893` 自癒，`processedFloors` 不會，後續樓層被 `cdGetNewFloors:2165` 與 `:4911` 靜默跳過。**規避方式（本 change 採用）**：branch 一律從主線最新位置建立、且建立前確認 `max(processedFloors) <= chat.length - 1` 與 `lastFloor <= chat.length - 1`；建立期間主線凍結不寫日記；所有 branch 直接從主線開、不得 A → B 再分支。另 `补写指定范围` 走 `extraFloors`（`index.js:4405`）繞過 `cdGetNewFloors`，本身不受此坑影響。缺陷本體已登記為獨立 backlog `[bug] [P2]`，不在本 change 修。
- [localStorage 備份池跨 branch 不記來源身分] → `cd-data-backups`（`index.js:1926`）條目只有 `{time, label, diaryCount}`，恢復（`:10570`）會整組覆蓋當前聊天。驗收期間**不使用「管理 → 备份/恢复」**，要保險走「導出 JSON」。已登記為獨立 backlog `[bug] [P3]`。
- [擴充 repo 的 `origin` 是上游作者、本地 commit 無處可推] → 已建 fork，`running` 已推上 `fork/running`；feature branch 完成後也推到 `fork`。rollback 為關開關（行為層）、切回 `running`（程式層）、還原 `.bak`（最後保險）。

## Migration Plan

1. 在擴充 repo 確認目前在 `running`、`git status` 乾淨（對方 mood commit 已落地、無未 commit 改動），記下 `running` 的 HEAD hash；`git switch -c diary-player-messages`；再備份為 `index.js.bak_include_player_msgs_<YYYYMMDD_HHMM>`（`.bak` 不加進 commit）。
2. 改設定預設值、`cdBuildDiaryPrompt`、設定面板、保存區塊、`cdTestDiary`。
3. `node --check index.js`。
4. ST 開著時 DevTools 勾停用快取後 F5；確認設定面板出現兩個開關（玩家訊息、自動總結）且狀態正確。
5. 走 §驗收流程（ON 態、5 個 branch）。
6. 改完 `git commit`（英文訊息）。回退：關開關即回到只有 AI 行；程式層回退為 `git switch running`；`.bak` 為最後保險。

## 驗收流程（ON 態單跑、5 個 branch）

2026-09-06 使用者拍板：本步驗收改為 **solution acceptance**，只驗 ON 態，不做 OFF／ON 對照、不做 A/B 盲化、不做顯著性檢定。理由：OFF 是既有原態、其結構性缺陷已由 Diary Audit 記錄；`includeUserMessagesInDiary` 的機制已由 pilot 驗證（ON 態玩家樓層正確進入材料、OFF 為 0、其他材料可維持一致、測試路徑不寫入）。**原第 1 組材料降級為 pilot**，只證明 mechanism／measurement，不列入驗收樣本。

### 前置（一次）

1. 讀主線聊天檔第一行 metadata，確認 `lastFloor <= chat.length - 1` 且 `max(processedFloors) <= chat.length - 1`。不符即停手——代表 metadata 已領先 chat，開 branch 會踩幽靈 `processedFloors`。
2. 關閉 `autoSummary`（全域設定，關一次對主線與所有 branch 同時生效）；確認 `includeUserMessagesInDiary` 為 ON。
3. 主線凍結：從此不在主線寫日記、不推進主線。
4. 從主線最新位置建立 5 個 branch，**全部直接從主線開，不得 A → B 再分支**。記錄每個 branch 的 ST 名稱（`… - Branch #N`）對應哪一種情境類型。

### 情境類型（一 branch 一種）

| 類型 | 玩家事件 |
|---|---|
| 承諾 | 玩家明確承諾未來會做／不做某件事 |
| 拒絕 | 玩家明確拒絕角色的要求或提議 |
| 揭露 | 玩家告訴角色一件角色原本不知道的重要資訊 |
| 請託 | 玩家提出具體要求，角色自由接受／拒絕／附條件 |
| 具體行動 | 玩家做出具關係意義的行為，而非只是說話 |

不寫逐字腳本——只預先指定「必須發生且可驗證的玩家事件」，由使用者在正常 RP 中自然說出／做出，角色自由回應。

### 每個 branch 的步驟

1. 正常 RP，讓該類型事件自然發生。
2. 事件與角色回應完成後，記下涵蓋該場景的樓號範圍。
3. **先寫 ground truth**——一段散文記「玩家實際做了／說了什麼、角色實際如何回應」。ground truth 不提供給日記，且**必須在讀日記之前寫**。這是取代盲讀的防污染機制：順序不用花錢，但寫在後面就沒有價值。
4. 用「补写指定范围」對該範圍產生真實日記（走 `extraFloors`、`index.js:4405`，繞過 `cdGetNewFloors`，不受 `processedFloors` 影響）。
5. 依下節判準記錄結果。

### 判準（收第一份材料前凍結）

**必要能力**（主問）——當該玩家事件對劇情具記憶價值時，日記是否正確保留三項：

- 玩家做了／說了什麼
- 角色如何回應
- 玩家事件與角色反應／認知／關係變化之間的因果連結

不要求每篇都寫玩家內容；玩家資訊不重要時，**正確忽略也算通過**。

**否決條件**——日記是否新增**與玩家有關**、且原始 RP 無證據支持的推論：玩家的動機、心理、秘密、情感、對玩家的關係狀態。

> **為什麼收窄到「與玩家有關」**：ON-only 沒有同批對照，看到幻覺無法歸因給本改動；而「日記本身會編造」是**既有基線行為**（Diary Audit 記錄的 `secret` 會編造）。只有與玩家有關的編造，才是「多給了玩家材料」能解釋的。NPC 自身的編造記入檢查清單、不參與否決。
>
> **基線不必另跑**：范婼慧現有 50 篇歷史日記全部產生於 OFF 態，Diary Audit 已對其做過欄位覆蓋率分析，可直接當幻覺基線（n=50，比重跑幾次 OFF 強）。

**檢查清單**（記錄與描述，不參與判定）：事實正確性、重要事件完整度、角色內在變化、重複污染。

### 結論措辭

以工程證據描述，例如「5 個情境中 X 個成功保留重要的玩家→角色因果；出現 Y 個與玩家有關的無證據推論；依此決定是否接受 Step 1 並進入 Step 2」。**不得**宣稱「Step 1 經統計證明有效」。

## 驗證設計（CLAUDE.md 驗證前置 Gate 五問）

本步的結果會用來決定 Step 2 是否繼續、以及日記是否能當 Learned Self 上游，屬 decision-bearing，適用五問。

- **Observation**：觀察點為各 branch 內以「补写指定范围」產生的真實日記（存於該 branch 的 `chatMetadata.extensions['character-diary'].diaries`，可由日記面板或聊天檔第一行讀取），以及事前寫下的 ground truth。兩者皆已確認存在且可取得。
- **Discrimination**：判準為上節的必要能力三子項（各 yes/no + 理由）與否決條件，收材料前凍結。**這不是統計檢定**——5 個情境給的是跨情境的穩定度描述，不是 p 值；不得因 5 中有 4 通過就宣稱「證明有效」，也不得因 1 個不通過就宣稱失敗。防地板／天花板效應的機制是 ground truth：它獨立於日記產生，判讀時可逐項對照，不是純主觀印象。
  **已知的鑑別力限制**：沒有 OFF 同批對照，所以「必要能力通過」只能說「ON 態做得到」，不能說「OFF 態做不到」（OFF 態在結構上看不見玩家發言是設計事實，非本次觀察所得）。
- **Construct**：要驗的是「補上一手玩家資訊之後，日記能否保留玩家→角色的因果，且不因此編造與玩家有關的內容」。量的是日記文本相對 ground truth 的保留與新增，不是重複率、不是字數、不是與 OFF 的文本差異。
- **Instrument**：本步的量測工具是**人的判讀 + ground truth**。凍結方式：判準與情境類型在收第一份材料前寫定於本文件，收材料期間不得修改；若中途發現判準有缺陷，**作廢已收材料重來**，不得改判準後沿用舊材料。pilot 階段的 `calc_expected_floors.py`（Instrument 校準腳本）已完成任務，驗收階段不再逐組執行。
- **Occurrence**：兩層。
  ① **建 branch 前**確認 `lastFloor` 與 `max(processedFloors)` 未超過 chat 末端——不做這步的話，後續 log 上的「沒有新樓層」是無意義的（可能是幽靈 `processedFloors` 靜默跳過，不是真的沒有）。
  ② **寫日記後**確認該 branch 的 `diaries` 真的多了一篇、且 `topFloor` 落在指定範圍內——`补写指定范围` 失敗時只在面板顯示文字，不對帳就分不出「沒跑」與「跑了沒結果」。
  另注意：`cdCheckAutoTrigger`（「检查自动触发」按鈕）的計數與真實觸發邏輯不一致（用 `_baselineChatLength` 且不跳過 `processedFloors`，`cdOnMessageReceived` 已改用 `lastFloor` 且跳過），**不得拿它當對帳依據**。本流程不依賴它。

## Open Questions

- 5 個 branch 演完之後，哪一個（若有）成為正史？影響投入程度與實驗後主線如何續接，不影響本 change 的實作。使用者未定。
- 收滿 5 個情境需要多久，視遊玩節奏；不催。若某一類型（例如「拒絕」）在自然 RP 中遲遲不出現，可刻意安排該場景，並在觀測檔記錄「此組為刻意安排」。
