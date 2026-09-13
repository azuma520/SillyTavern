## 1. 分支與備份

- [x] 1.1 擴充 repo（`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary`）確認 `git status` 乾淨、目前在 `diary-player-messages`；`git switch running && git merge --ff-only diary-player-messages && git push fork running`；記錄 `running` 新 HEAD
- [x] 1.2 `git switch -c diary-key-events-actor`；備份 `index.js` 為 `index.js.bak_key_events_actor_<YYYYMMDD_HHMM>`（不進 commit）；確認 CRLF

## 2. 前置驗證（凍結前必須完成）

- [x] 2.1 ST 開著、DevTools 勾停用快取後，跑日記測試路徑，讀 `window.__cdLastDiaryTest.sys`，記錄「玩家角色名：」後的執行期值（預期「宇璽」）；此值即分類器的玩家主體詞
- [x] 2.2 對 Step 1 驗收檔（`RP記憶/實驗與驗證/Diary_玩家樓層_ON態驗收_2026-09-06.md`）抄出 Branch #8–#11 各自的樓層範圍與 ground truth 段落位置，寫入本步驗收檔的骨架 `RP記憶/實驗與驗證/Diary_KeyEvents_Actor_驗收_<日期>.md`
- [x] 2.3 讀 #8–#11 聊天檔第一行，記錄每角色 `diaries` 陣列長度與最後一篇的 `message_id`，當 Occurrence 對帳基準

## 3. 量測工具（Instrument 校準與凍結；本節 commit 必須早於第 4 節的 prompt commit）

- [x] 3.1 寫 `文檔/專案/Diary-Quality/tools/classify_key_events.py`：讀指定聊天檔的 `diaries`，對每條 `key_events` 依 audit §3.2 規則分五類（①前 6 字內有名單內名字／②起首為代名詞／③名字在句中非開頭／④代名詞在句中非開頭／⑤皆無），另輸出子計數 ①-strict（以名單內名字 + 全形冒號開頭，名字不限日記主人）；輸出各類條數、佔比、對帳合計；支援 `--subset 范婼慧:60,蘇芮萱:13,徐婷婷:3` 取每角色陣列前 N 篇；名單為程式內常數
- [x] 3.2 凍結基線校準：對 Branch #12 的 248 條子集跑，須得 52／5／19／48／124、合計 248（這證明分類器重現了 audit 的量法，不是人工 ground truth）。名單只在「范婼慧、蘇芮萱、徐婷婷、小秘書、<2.1 的玩家名>」封閉集合內取子集嘗試，記錄每次嘗試的名單與結果；重現的那組寫死。封閉集合內無解則停手回報
- [x] 3.3 合成樣本測試：腳本內附 10 條手寫樣本（5 條「主体：事件」新格式須判①且計入 ①-strict，含玩家名與非日記主人的角色名各至少一條；5 條舊格式對應①③④⑤各至少一條、皆不計入 ①-strict），以 `--selftest` 執行全部通過
- [x] 3.4 在 elephantfish repo commit 分類器（英文訊息），記錄 commit hash 到 design.md「驗證設計・Instrument」與驗收檔；此後腳本不得修改

## 4. Prompt 改動

- [x] 4.1 在 `cdBuildDiaryPrompt` 的 `sys` 陣列、Step 1 加的資料說明那行之後，新增 key_events 契約一行（措辭依 design D3；玩家名用 `${_protNameDiary}`）
- [x] 4.2 同函數 JSON 範本的 `"key_events":["关键事件"]` 改為 `"key_events":["主体：事件"]`；`cdBuildCombinedPrompt` 的範本不動
- [x] 4.3 `node --check index.js` 通過；`git diff running` 只落在 `cdBuildDiaryPrompt` 的 sys 陣列與範本兩處
- [x] 4.4 commit（英文訊息）、`git push -u fork diary-key-events-actor`，記錄 hash

## 5. 靜態驗證與 smoke test

- [x] 5.1 DevTools 勾停用快取後 F5；跑測試路徑，`window.__cdLastDiaryTest.sys` 含新要求行與玩家名；`response` 中的 `key_events` 目視有「主体：」前綴（smoke test，不記入驗收）
- [x] 5.2 測試前後讀當前聊天檔 metadata，`diaries` 篇數不變（測試路徑不寫入）

## 6. 驗收（Branch #8–#11 配對重跑）

- [x] 6.1 （聊天檔備份已於 2026-09-13 14:2x 完成，`.bak_before_step2_rerun_*`）設定面板關閉「自动总结」；確認「玩家訊息」開關為開；逐檔備份 #8–#11 聊天檔為 `.bak_before_step2_rerun_<ts>`
- [x] 6.2 Branch #8（請託）：載入該 branch，對 Step 1 的同一樓層範圍執行「补写指定范围」；讀聊天檔對帳該角色 `diaries` 長度 +1、新篇 `message_id` = 範圍頂樓；把新篇完整 JSON 抄進驗收檔
- [x] 6.3 Branch #9（承諾）：同 6.2
- [x] 6.4 Branch #10（具體行動）：同 6.2
- [x] 6.5 Branch #11（揭露）：同 6.2
- [x] 6.6 四個 branch 對帳全過後，用凍結的分類器對四篇新日記的 `key_events` 跑分類，記錄五類條數與比例；標準 1（⑤ ≤ 10%）與標準 2（①-strict ≥ 80%，實際行為者明確、不限日記主人）判定
- [x] 6.7 使用者逐條對照 Step 1 ground truth 判「玩家行為被歸給角色」條數（標準 3，須 = 0）；agent 只列表、不代判
- [x] 6.8 標準 4：新篇鍵集合與舊篇相同；標準 5：面板／時間軸／搜尋／編輯器對 #8 的新舊兩篇皆正常
- [x] 6.9 結論以工程措辭寫入驗收檔（「4 個情境共 N 條，⑤ 佔 x%、① 佔 y%、歸屬錯誤 z 條；依此接受／不接受」），不得寫「經統計證明」
- [x] 6.10 設定面板開回「自动总结」，讀 `settings.json` 確認值與 mtime

## 7. 交接

- [x] 7.1 `文檔/專案/Diary-Quality/README.md` Changelog 加一行連到當日 handoff；handoff 記錄分支、兩個 commit hash（分類器／prompt）、備份檔名、校準記錄、驗收結果
- [x] 7.2 驗收節點 2026-09-20 Instrument 那條：若 3.2／3.4 有落檔的校準記錄與凍結 hash，填 result 並勾選
- [x] 7.3 （不適用：首輪五項標準全達標）未達標時：agent 提兩個措辭版本讓使用者選、不自行擴 scope；下一輪登記為本 change 的新 tasks 段，不重判舊資料
