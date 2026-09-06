## 1. 前置與備份

- [x] 1.1 在擴充 repo（`D:\AI\SillyTavern\public\scripts\extensions\third-party\character-diary`）確認目前分支是 `running`（不是 `main`）、`git status` 乾淨、對方的 mood 歸一改動已 commit 到 `running`；記下 HEAD hash；`git switch -c diary-player-messages`
- [x] 1.2 備份 `index.js` 為 `index.js.bak_include_player_msgs_<YYYYMMDD_HHMM>`（CLAUDE.md 硬性要求，不進 commit）；確認 CRLF、後續編輯保留 CRLF
- [x] 1.3 用 python 從銀趴郵輪 Branch #7 聊天檔算出當下待處理批次的 AI 樓號與依 D2 規則預期的玩家樓號集合，存到 scratchpad 當 Instrument 校準答案

## 2. 設定與面板

- [x] 2.1 在 `cdGetSettings` 預設物件（約 216 行附近）加 `includeUserMessagesInDiary: true` 並附註解
- [x] 2.2 在設定面板日記區（約 9291 行 `cd-s-diarycharfilter` 那列附近）加一列 `cds-row` 開關，id `cd-s-includeusermsgs`，依現值勾選
- [x] 2.3 在保存區塊（約 9524 行）加 `includeUserMessagesInDiary: $('#cd-s-includeusermsgs').is(':checked')`
- [x] 2.4 觀察模式：在設定面板「处理频率」那列附近加一列 `cds-row` 開關，id `cd-s-autosummary`，依 `s.autoSummary !== false` 勾選；保存區塊加 `autoSummary: $('#cd-s-autosummary').is(':checked')`。**不新增旗標**（`autoSummary` 已存在於 `DEFAULT_SETTINGS:212`，兩個 gate 已尊重它），只接線
- [x] 2.5 確認關閉狀態下的可見回饋：`cdCheckAutoTrigger:3298` 現有的 `toastr.warning('自动总结已关闭')` 已滿足 spec 的狀態可見性需求，不必新增程式；若實測發現訊息不夠明確再調整文案

## 3. 日記 prompt 組裝

- [x] 3.1 在 `cdBuildDiaryPrompt` 內新增取玩家樓層的區塊：從聊天陣列以本批第一個 AI 樓號往前找最近一個 AI 樓層（找不到則 0），收集其後至本批最後一個 AI 樓號之間所有 `is_user` 樓層；開關關閉時為空陣列
- [x] 3.2 把 AI 樓層與玩家樓層合併後依樓號排序，場景行改為 `[#樓號 Player／名字]` 與 `[#樓號 Assistant／名字]`，兩者皆經 `cdFilterTags`
- [x] 3.3 在 `sys` 陣列加玩家角色名一行（`SillyTavern.getContext().name1`，try／catch，缺省「主角」，註明不為其寫日記）與中性資料說明一句
- [x] 3.4 `git diff running` 確認只落在 `cdBuildDiaryPrompt`、設定預設值、面板列、保存區塊、`cdTestDiary`；`cdNormalizeMood`、`CD_MOOD_T2S`、`cdGetData` 的 mood 歸一段與 system 內 mood 列舉值均未被觸碰

## 4. 測試路徑記錄

- [x] 4.1 在 `cdTestDiary` 日記分支加 `cdAddLog('info', '测试 [日记] 完整材料', { usr, response })` 與 `window.__cdLastDiaryTest = { scene, sys, usr, response, includeUser }`

## 5. 驗證

- [x] 5.1 `node --check index.js` 通過
- [x] 5.2 DevTools 勾停用快取後 F5，設定面板出現開關且預設開；關閉再開啟各存一次，重載後狀態保留
- [x] 5.3 Instrument 校準：開關開，跑測試路徑，`window.__cdLastDiaryTest.usr` 中的 `Player` 行樓號集合等於 1.2 的預期集合；開關關，`Player` 行為 0。不符則修程式、不改答案
- [x] 5.4 Occurrence：測試前後讀聊天檔 metadata，`processedFloors` 長度與各角色 `diaries` 篇數不變；console 有「测试 [日记] 完整材料」那筆
- [x] 5.5 檢查 ON 態回應的 `npcs` 不含玩家名；`diaryCharFilter` 捕獲 log 未為玩家取日記
- [x] 5.6 記錄第一組 OFF／ON 材料到 `RP記憶/實驗與驗證/` 下的觀測檔（標明批次樓號、兩態完整回應、尚未判讀）

## 6. 交接

- [x] 6.1 在分支上 `git commit`（英文訊息，說明開關、範圍規則、測試路徑記錄），`git push -u fork diary-player-messages`，記下 hash
- [x] 6.2 `文檔/專案/Diary-Quality/README.md` Changelog 加一行連到當日 handoff；handoff 記錄分支名、commit hash、備份檔名、diff 落點、校準結果、第一組材料位置
- [x] 6.3 第 1 組 OFF／ON 材料**降級為 pilot**：只證明 mechanism（玩家樓層正確進入材料）與 measurement（測試路徑不寫入），不列入驗收樣本。原「累積 5 組後盲讀判定」設計作廢，改走第 7 節

## 7. 驗收（ON 態單跑、5 個 branch）

判準與流程的權威在 `design.md` §驗收流程；本節只列可勾的執行步驟。

### 7.1 前置（一次）

- [x] 7.1.1 讀主線聊天檔第一行 metadata，確認 `lastFloor <= chat.length - 1` 且 `max(processedFloors) <= chat.length - 1`。不符即停手回報，不得逕自開 branch
- [x] 7.1.2 在設定面板關閉「自动总结」（全域設定，一次對主線與所有 branch 生效）；確認「玩家訊息」開關為開
- [x] 7.1.3 主線凍結：從此不在主線寫日記、不推進主線，直到第 7.4 節收尾
- [x] 7.1.4 從主線最新位置建立 5 個 branch，全部直接從主線開（**不得** A → B 再分支）。在觀測檔記錄每個 ST branch 名稱（`… - Branch #N`）對應哪一種情境類型

### 7.2 每個 branch（重複 5 次，各一種類型）

類型：承諾／拒絕／揭露／請託／具體行動。

- [x] 7.2.1 branch #1 承諾　→ 實際落在 Branch #9
- [x] 7.2.2 branch #2 拒絕　→ 實際落在 Branch #12（另含 OFF／ON 對照材料）
- [x] 7.2.3 branch #3 揭露　→ 實際落在 Branch #11（事件分量：重）
- [x] 7.2.4 branch #4 請託　→ 實際落在 Branch #8（類型不預先綁順序）
- [x] 7.2.5 branch #5 具體行動　→ 實際落在 Branch #10（刻意極端、未交代動機）

每個 branch 內固定四步（順序不可調換）：① 正常 RP 讓該事件自然發生 → ② 記下涵蓋該場景的樓號範圍 → ③ **先寫 ground truth**（玩家實際做了／說了什麼、角色實際如何回應；不提供給日記、必須早於讀日記）→ ④ 用「补写指定范围」對該範圍產生真實日記，並確認 `diaries` 真的多了一篇且 `topFloor` 落在指定範圍內。

### 7.3 判讀

- [x] 7.3.1 收滿 5 個情境後一次判讀：每組記必要能力三子項（玩家言行／角色回應／因果連結，各 yes/no + 理由）與否決條件（是否新增與玩家有關的無證據推論）
- [x] 7.3.2 檢查清單四項（事實正確性、事件完整度、角色內在變化、重複污染）只記錄與描述、不參與判定
- [x] 7.3.3 結論以工程證據措辭寫入觀測檔，**不得**宣稱統計證明；依結果決定是否接受 Step 1 並開 Step 2 的 change

### 7.4 收尾

- [x] 7.4.1 **把 `autoSummary` 開回來**（全域設定，忘了開主線會從此靜默停止寫日記）
- [x] 7.4.2 確認 5 個 branch 與判讀結果都已記入 `RP記憶/實驗與驗證/` 的觀測檔；主線後續如何續接由使用者決定

> 驗收期間**不使用**擴充的「管理 → 备份/恢复」（localStorage 備份池跨 branch 不記來源身分，見 design §Risks）；要保險走「導出 JSON」。
> 亦**不得**拿「检查自动触发」的計數當對帳依據（該計數與真實觸發邏輯不一致，已另案登記）。
