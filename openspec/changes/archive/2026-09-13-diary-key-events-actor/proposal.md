## Why

`character-diary` 日記的 `key_events` 欄位是六個輸出欄位裡唯一屬於 Experience 核心、且最接近結構化資料的一格，Learned Self 未來讀的就是它。2026-09-06 的機制與 prompt audit（`RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md` §3.2）對 Branch #12 的 248 條 `key_events` 逐條分類：**124 條（50.0%）完全沒有主詞**，例如「高潮后主动索吻」「介绍今晚压轴剧目」。成因是結構性的：prompt 對這個欄位的全部指示只有 JSON 範本裡的「关键事件」四個字（audit §2.3），沒有任何「寫出誰做的」的要求。角色自己做的事省略主詞沒問題；玩家做的事一旦省略主詞，讀的人會自動補成「角色做的」，Step 1 驗收時觀察到的主詞錯置就是這個欄位一半時間都處在的狀態。「誰做了什麼」錯掉，Learned Self 整條推論都偏。這是「日記品質線 V1」（`task-20260906-diary-quality`）的 Step 2，audit §七 的候選 A。

## What Changes

- `cdBuildDiaryPrompt` 的 system 要求清單新增一條 `key_events` 的 actor 契約：每條關鍵事件必須以行為主體開頭，格式「主体：事件」；主體是「已知角色名单」中的主名或玩家角色名（沿用 Step 1 已注入的 `玩家角色名：${_protNameDiary}`）；日記主人自己做的事也寫主名、不寫「我」；多人共同行為寫主要發起者。
- JSON 範本裡 `key_events` 的 placeholder 由 `["关键事件"]` 改為 `["主体：事件"]`，讓範本與要求一致。
- **不改 schema**：`key_events` 維持字串陣列。actor 以字串前綴表達，既有 13 個讀取點（面板、時間軸、搜尋、編輯器、匯出、收藏、重寫合併）零改動，既有 314 條（Branch #12 現值）舊格式資料不遷移、照常顯示。
- 新增量測工具 `文檔/專案/Diary-Quality/tools/classify_key_events.py`：重現 audit §3.2 的五類主詞形態分類器，先以 audit 的 248 條子集（52／5／19／48／124）當凍結基線校準（證明分類器重現了 audit 的量法，不是人工 ground truth），校準通過即 commit 凍結，之後不得再改；**分類器的 commit 必須早於 prompt 的 commit**。
- 驗收：在 Step 1 的四個測試 branch（#8–#11）對同一段樓層範圍用「补写指定范围」重跑日記，以凍結的分類器數新產出 `key_events` 的「完全無主詞」比例，並用 Step 1 已寫好的 ground truth 由使用者判定「玩家行為被歸給角色」的條數。成功標準在動手前定死（見 design.md）。

## Capabilities

### New Capabilities
- `diary-key-events-actor`: `key_events` 每條必須帶行為主體的 prompt 契約（格式、主體詞彙、日記主人不用「我」、schema 不變、舊資料相容）

### Modified Capabilities
<!-- `diary-scene-player-messages` 的「system 提示的資料說明」要求不變：本 change 只在同一個 sys 清單再加一條，不改該 spec 既有 requirement 的行為 -->

## Impact

- **程式**：`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary/index.js`（CRLF、11,651 行、獨立 git repo）。只觸及 `cdBuildDiaryPrompt`（747 行起）的 `sys` 陣列（約 809–846 行）。`cdBuildCombinedPrompt`（876 行）的同款範本**不動**：2026-09-13 查證它沒有任何呼叫點，是死碼。`cdBuildDiaryPrompt` 有三個呼叫點（測試路徑 3192、正式生成 4430、單篇重寫 8674），三者自動同時吃到新 prompt。
- **分支**：擴充 repo 目前 checkout 在 `diary-player-messages`（Step 1 的分支，領先 `running` 兩個 commit `63a6537`／`8d19c7f`，皆已推 `fork`，Step 1 change 已歸檔）。本 change 先把 `running` fast-forward 到 `diary-player-messages`（推 `fork/running`），再依規則從 `running` 開 `diary-key-events-actor`。
- **下游讀取點**（改中間產物前先列消費者）：`index.js` 1893（收藏）、2246（合併寫入）、2331（`formatEntryForWb`，世界書同步死碼）、6748（搜尋）、6932（面板）、7148／7176（編輯器，逗號分隔）、7214（編輯後渲染）、8699（單篇重寫合併）、8791（時間軸）、9058／9234（匯出）、9768（彩蛋收藏）。全部以字串處理、以 `,，、` 或 `;`／`·` 連接，冒號前綴不觸發任何分隔。`diaryMemory` 注入（788–858 行）只注入 `entry`、不注入 `key_events`，新格式不會經由記憶注入回饋給下一批。
- **資料**：驗收會在 Branch #8–#11 各追加一組同樓層的新日記（`mergeDiaries` 以 `message_id + entry` 去重，新 entry 必然不同、會 append）。重跑前逐檔備份。Branch #12 是使用者現行遊玩線，**不重跑**。
- **不受影響**：`interval=5`、`maxWindowFloors=40`、日記 schema 的鍵集合、模型、temperature、checkpoint 三欄位、關係與劇情檔案 prompt、`secret`／`mood`／`relationship_with_others` 的規格（audit P3／P5 另案）。
- **下游線**：Learned Self 讀 `key_events` 時要能同時接受「有前綴」與「無前綴」兩種格式（前綴以第一個全形冒號切分）；LS 尚未動工，此為其輸入契約的註記。
