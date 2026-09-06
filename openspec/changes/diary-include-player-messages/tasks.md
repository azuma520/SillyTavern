## 1. 前置與備份

- [ ] 1.1 在擴充 repo（`D:\AI\SillyTavern\public\scripts\extensions\third-party\character-diary`）確認目前分支是 `running`（不是 `main`）、`git status` 乾淨、對方的 mood 歸一改動已 commit 到 `running`；記下 HEAD hash；`git switch -c diary-player-messages`
- [ ] 1.2 備份 `index.js` 為 `index.js.bak_include_player_msgs_<YYYYMMDD_HHMM>`（CLAUDE.md 硬性要求，不進 commit）；確認 CRLF、後續編輯保留 CRLF
- [ ] 1.3 用 python 從銀趴郵輪 Branch #7 聊天檔算出當下待處理批次的 AI 樓號與依 D2 規則預期的玩家樓號集合，存到 scratchpad 當 Instrument 校準答案

## 2. 設定與面板

- [ ] 2.1 在 `cdGetSettings` 預設物件（約 216 行附近）加 `includeUserMessagesInDiary: true` 並附註解
- [ ] 2.2 在設定面板日記區（約 9291 行 `cd-s-diarycharfilter` 那列附近）加一列 `cds-row` 開關，id `cd-s-includeusermsgs`，依現值勾選
- [ ] 2.3 在保存區塊（約 9524 行）加 `includeUserMessagesInDiary: $('#cd-s-includeusermsgs').is(':checked')`

## 3. 日記 prompt 組裝

- [ ] 3.1 在 `cdBuildDiaryPrompt` 內新增取玩家樓層的區塊：從聊天陣列以本批第一個 AI 樓號往前找最近一個 AI 樓層（找不到則 0），收集其後至本批最後一個 AI 樓號之間所有 `is_user` 樓層；開關關閉時為空陣列
- [ ] 3.2 把 AI 樓層與玩家樓層合併後依樓號排序，場景行改為 `[#樓號 Player／名字]` 與 `[#樓號 Assistant／名字]`，兩者皆經 `cdFilterTags`
- [ ] 3.3 在 `sys` 陣列加玩家角色名一行（`SillyTavern.getContext().name1`，try／catch，缺省「主角」，註明不為其寫日記）與中性資料說明一句
- [ ] 3.4 `git diff running` 確認只落在 `cdBuildDiaryPrompt`、設定預設值、面板列、保存區塊、`cdTestDiary`；`cdNormalizeMood`、`CD_MOOD_T2S`、`cdGetData` 的 mood 歸一段與 system 內 mood 列舉值均未被觸碰

## 4. 測試路徑記錄

- [ ] 4.1 在 `cdTestDiary` 日記分支加 `cdAddLog('info', '测试 [日记] 完整材料', { usr, response })` 與 `window.__cdLastDiaryTest = { scene, sys, usr, response, includeUser }`

## 5. 驗證

- [ ] 5.1 `node --check index.js` 通過
- [ ] 5.2 DevTools 勾停用快取後 F5，設定面板出現開關且預設開；關閉再開啟各存一次，重載後狀態保留
- [ ] 5.3 Instrument 校準：開關開，跑測試路徑，`window.__cdLastDiaryTest.usr` 中的 `Player` 行樓號集合等於 1.2 的預期集合；開關關，`Player` 行為 0。不符則修程式、不改答案
- [ ] 5.4 Occurrence：測試前後讀聊天檔 metadata，`processedFloors` 長度與各角色 `diaries` 篇數不變；console 有「测试 [日记] 完整材料」那筆
- [ ] 5.5 檢查 ON 態回應的 `npcs` 不含玩家名；`diaryCharFilter` 捕獲 log 未為玩家取日記
- [ ] 5.6 記錄第一組 OFF／ON 材料到 `RP記憶/實驗與驗證/` 下的觀測檔（標明批次樓號、兩態完整回應、尚未判讀）

## 6. 交接

- [ ] 6.1 在分支上 `git commit`（英文訊息，說明開關、範圍規則、測試路徑記錄），`git push -u fork diary-player-messages`，記下 hash
- [ ] 6.2 `文檔/專案/Diary-Quality/README.md` Changelog 加一行連到當日 handoff；handoff 記錄分支名、commit hash、備份檔名、diff 落點、校準結果、第一組材料位置
- [ ] 6.3 觀測累積至 5 組前不下結論；5 組後以盲讀判定，結果決定 Step 2 是否開 change
